"""
AI-Powered Trading Bot - FastAPI API Sunucusu
Bu dosya, botu bir web arayüzü üzerinden kontrol etmek için API ve WebSocket sağlar.
'uvicorn main:app --reload' komutu ile çalıştırılmalıdır.
"""
import asyncio
import os
import threading
import uuid
from typing import Any, Dict, Optional

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from Bot import TradingBot
from Patterns.Observer import LoggingObserver
from Patterns.Observer.websocket_observer import WebSocketObserver
from Patterns.Observer.telegram_observer import TelegramAlertObserver

# Environment değişkenlerini yükle
load_dotenv()

def run_trading_bot(
    params: Dict[str, Any],
    *,
    enable_console: bool = True,
    ws_observer: Optional[WebSocketObserver] = None,
) -> float:
    """Execute trading session with shared logic for CLI and API."""

    def console_print(message: str):
        if enable_console:
            print(message)

    # API modunda (enable_console=False) bu print'ler görünmez.
    console_print("\n" + "="*70)
    console_print("🚀 Trading Bot Başlatılıyor...")
    console_print("="*70)
    console_print(f"Coin: {params['symbol']}")
    console_print(f"Mod: {'Live Trading' if params['mode'] == '1' else 'Backtest'}")
    console_print(f"Stop Loss: {params['stop_loss']*100}%")
    console_print(f"Başlangıç Bakiyesi: ${params['initial_balance']:.2f}")
    console_print("="*70)

    bot = TradingBot(coin_symbol=params["symbol"])

    # Dosya loglayıcı (her zaman aktif)
    logger = LoggingObserver(log_file="trade_log.txt")
    bot.register_observer(logger)

    # WebSocket loglayıcı (sadece UI'dan istek gelirse)
    if ws_observer:
        bot.register_observer(ws_observer)

    # Telegram loglayıcı (opsiyonel)
    telegram_bot_token = os.getenv("TELEGRAM_TOKEN")
    telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if telegram_bot_token and telegram_chat_id:
        bot.register_observer(TelegramAlertObserver(token=telegram_bot_token, chat_id=telegram_chat_id))

    try:
        if params["mode"] == "1":
            final_balance = bot.simulate_trading(
                initial_balance=params["initial_balance"],
                stop_loss=params["stop_loss"],
                interval=params["interval"],
                position_size_pct=params["position_size_pct"],
            )
        else:
            final_balance = bot.backtest_trading(
                initial_balance=params["initial_balance"],
                stop_loss=params["stop_loss"],
                interval=params["candle_interval"],
                check_date=params["check_date"],
                position_size_pct=params["position_size_pct"],
            )

        console_print("\n✅ Trading tamamlandı!")
        console_print(f"   Son bakiye: ${final_balance:.2f}")
        console_print(f"   Kar/Zarar: ${final_balance - params['initial_balance']:.2f}")
        console_print("\n📝 Loglar: trade_log.txt dosyasında kaydedildi.\n")

        # Sonucu WebSocket'e gönder
        if ws_observer:
            ws_observer.send_result(final_balance, params["initial_balance"])

        return final_balance
    
    except KeyboardInterrupt as exc:
        console_print("\n\n⚠️  Trading kullanıcı tarafından durduruldu.")
        if ws_observer:
            ws_observer.send_error("Trading kullanıcı tarafından durduruldu.")
        raise exc
    except Exception as exc:
        console_print(f"\n❌ Hata oluştu: {exc}")
        if ws_observer:
            ws_observer.send_error(str(exc))
        raise

# --- 2. FastAPI Sunucu Tanımları ---

# UI'ın dropdown'larını doldurmak için sabit veriler
CONFIG_RESPONSE = {
    "available_symbols": ["BTCUSDT", "ETHUSDT", "BNBUSDT"],
    "available_intervals": ["1m", "5m", "30m", "1h", "1d", "1w", "1M"],
    "available_date_ranges": ["1 hour ago UTC", "1 day ago UTC", "1 month ago UTC"],
}

# Aktif bot oturumlarını (session) ve thread'leri yönetmek için
sessions: Dict[str, Dict[str, Any]] = {}
sessions_lock = threading.Lock()

# FastAPI uygulamasını oluştur
app = FastAPI(title="AI Trading Bot API", version="1.0.0")

# CORS (Cross-Origin Resource Sharing) ayarları - UI'ın bağlanabilmesi için
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Veya UI adresiniz: ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API Modelleri (Pydantic) ---
# API'ye gelecek verinin nasıl görünmesi gerektiğini tanımlar

class TradeStartRequest(BaseModel):
    symbol: str = Field(..., examples=["BTCUSDT"])
    mode: str = Field(..., pattern="^(1|2)$", description="1=Live, 2=Backtest")
    stop_loss_pct: float = Field(..., gt=0)
    initial_balance: float = Field(..., gt=0)
    position_size_pct: float = Field(50.0, gt=0, le=100)
    interval_mins: Optional[int] = Field(None, gt=0, description="Live interval (minutes)")
    candle_interval: Optional[str] = Field(None, description="Backtest candle interval")
    check_date: Optional[str] = Field(None, description="Backtest tarih aralığı")

class TradeStartResponse(BaseModel):
    status: str
    session_id: str
    message: str

# --- Yardımcı Fonksiyonlar (Session Yönetimi) ---

def _store_session(session_id: str, data: Dict[str, Any]) -> None:
    with sessions_lock:
        sessions[session_id] = data

def _get_session(session_id: str) -> Optional[Dict[str, Any]]:
    with sessions_lock:
        return sessions.get(session_id)

def _remove_session(session_id: str) -> None:
    with sessions_lock:
        sessions.pop(session_id, None)

def _build_params_from_request(request: TradeStartRequest) -> Dict[str, Any]:
    """API'den gelen isteği, botun anladığı 'params' dict'ine çevirir."""
    interval_seconds = int(request.interval_mins) * 60 if request.mode == "1" and request.interval_mins else None
    candle_interval = request.candle_interval if request.mode == "2" else None
    check_date = request.check_date if request.mode == "2" else None

    return {
        "symbol": request.symbol,
        "mode": request.mode,
        "stop_loss": request.stop_loss_pct / 100,
        "initial_balance": request.initial_balance,
        "position_size_pct": request.position_size_pct / 100,
        "interval": interval_seconds,
        "candle_interval": candle_interval,
        "check_date": check_date,
    }

def _run_bot_session(session_id: str, payload: Dict[str, Any]) -> None:
    """
    Bu fonksiyon YENİ BİR THREAD'de çalışır.
    Botun çalışmasını (uzun süren işlemi) yönetir.
    """
    session = _get_session(session_id)
    if not session:
        return

    request_model = TradeStartRequest(**payload)
    params = _build_params_from_request(request_model)

    # Bu session için WebSocketObserver'ı oluştur
    ws_observer = WebSocketObserver(
        session_id=session_id,
        queue=session["queue"],
        loop=session["loop"],
        fallback_to_console=False,
    )

    try:
        # Botu API modunda çalıştır (enable_console=False)
        run_trading_bot(params, enable_console=False, ws_observer=ws_observer)
    except Exception:
        # Hata olursa (run_trading_bot zaten logladı)
        pass
    finally:
        # Bot bittiğinde veya hata verdiğinde session'ı işaretle
        session["completed"] = True

# --- 3. API Endpoint'leri ---

@app.get("/api/config")
def get_config() -> Dict[str, Any]:
    """UI'daki (React, Vue vb.) dropdown'ları doldurmak için konfigürasyon verisi sağlar."""
    return CONFIG_RESPONSE

@app.post("/api/trade/start", response_model=TradeStartResponse)
async def start_trade(request: TradeStartRequest) -> TradeStartResponse:
    """Yeni bir trade botu oturumu başlatan ana endpoint."""
    
    # Gelen veriyi doğrula
    if request.mode == "1" and request.interval_mins is None:
        raise HTTPException(status_code=400, detail="Live mod için 'interval_mins' gereklidir")
    if request.mode == "2" and (not request.candle_interval or not request.check_date):
        raise HTTPException(status_code=400, detail="Backtest modu için 'candle_interval' ve 'check_date' gereklidir")

    loop = asyncio.get_running_loop() # FastAPI'nin ana event loop'u
    queue: asyncio.Queue = asyncio.Queue() # Bu session için mesaj kuyruğu
    session_id = str(uuid.uuid4()) # Benzersiz ID oluştur

    # Session'ı kaydet
    _store_session(
        session_id,
        {
            "queue": queue,
            "loop": loop,
            "completed": False,
        },
    )

    # Botu çalıştırmak için yeni bir thread başlat
    # Bu, botun API'yi (UI'ı) kilitlemesini engeller
    thread = threading.Thread(
        target=_run_bot_session,
        args=(session_id, request.model_dump()),
        daemon=True,
        name=f"bot-session-{session_id}",
    )
    thread.start()

    mode_label = "Backtest" if request.mode == "2" else "Live trading"
    message = f"{mode_label} {request.symbol} için başlatıldı."
    return TradeStartResponse(status="started", session_id=session_id, message=message)

@app.websocket("/ws/updates/{session_id}")
async def websocket_updates(websocket: WebSocket, session_id: str):
    """
    WebSocket bağlantısı. Bot loglarını ve sonuçlarını UI'a canlı olarak
    akıtır (stream).
    """
    session = _get_session(session_id)
    if not session:
        await websocket.close(code=4404, reason="Unknown session")
        return

    await websocket.accept()
    queue: asyncio.Queue = session["queue"]

    try:
        # Kuyrukta mesaj oldukça UI'a gönder
        while True:
            payload = await queue.get()
            await websocket.send_json(payload)
            # Bot bittiğinde (result) veya hata verdiğinde (error)
            # bağlantıyı kapat
            if payload.get("type") in {"result", "error"}:
                break
    except WebSocketDisconnect:
        pass
    finally:
        # UI bağlantıyı kapattığında veya bot bittiğinde session'ı temizle
        _remove_session(session_id)

# --- 4. Sunucuyu Çalıştırma ---

if __name__ == "__main__":
    print("🚀 AI Trading Bot API Sunucusu Başlatılıyor...")
    print("   Lütfen 'uvicorn main:app --reload' komutunu kullanarak başlatın.")
    print("   Test için: http://127.0.0.1:8000/docs")
    
    # Bu, 'python main.py' komutuyla Geliştirme modu için hızlı bir başlatma sağlar
    uvicorn.run(app, host="127.0.0.1", port=8000)