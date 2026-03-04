"""
AI-Powered Trading Bot - Terminal Version
Terminal tabanlı kripto trading botu
"""
import os
from dotenv import load_dotenv
from Patterns.Observer import LoggingObserver
from Patterns.Observer.telegram_observer import TelegramAlertObserver
from Bot import TradingBot
from Patterns.Observer import LoggingObserver

# Load environment variables
load_dotenv()


def print_banner():
    """Print welcome banner"""
    print("\n" + "="*70)
    print("🤖  AI-POWERED CRYPTO TRADING BOT")
    print("="*70)
    print("Pattern Kullanımı:")
    print("  ✅ Observer Pattern (Logging)")
    print("  ✅ Strategy Pattern (RSI, MACD, ADX, Default)")
    print("  ✅ Template Method Pattern (Strategy Template)")
    print("  ✅ Singleton Pattern (LoggingObserver)")
    print("="*70 + "\n")


def get_user_input():
    """Get trading parameters from user"""
    print("📝 Lütfen trading parametrelerini girin:\n")
    
    # Cryptocurrency symbol
    print("Mevcut coin'ler: BTCUSDT, ETHUSDT, BNBUSDT")
    symbol = input("Coin sembolü (varsayılan: BTCUSDT): ").strip().upper() or "BTCUSDT"
    
    # Trading mode
    print("\nTrading Modları:")
    print("  1. Live Trading (Gerçek zamanlı)")
    print("  2. Backtest (Geçmiş veri)")
    mode = input("Mod seçin (1 veya 2, varsayılan: 2): ").strip() or "2"
    
    # Stop loss
    stop_loss_pct = input("Stop loss % (varsayılan: 2): ").strip() or "2"
    stop_loss = float(stop_loss_pct) / 100
    
    # Initial balance
    balance = input("Başlangıç bakiyesi $ (varsayılan: 10000): ").strip() or "10000"
    initial_balance = float(balance)
    
    # Position size percentage
    position_size_pct_str = input("Her işlemde bakiyenin % kaçı kullanılsın? (varsayılan: 50): ").strip() or "50"
    position_size_pct = float(position_size_pct_str) / 100
    
    # Mode-specific parameters
    if mode == "1":
        interval_mins = input("Trading aralığı (dakika, varsayılan: 5): ").strip() or "5"
        interval = int(interval_mins) * 60  # Convert to seconds
        check_date = None
        candle_interval = None
    else:
        print("\nKandle aralıkları: 1m, 5m, 30m, 1h, 1d, 1w, 1M")
        candle_interval = input("Kandle aralığı (varsayılan: 1m): ").strip() or "1m"
        
        print("\nTarih aralıkları: 1 hour ago UTC, 1 day ago UTC, 1 month ago UTC")
        check_date = input("Tarih aralığı (varsayılan: 1 hour ago UTC): ").strip() or "1 hour ago UTC"
        interval = None
    
    return {
        'symbol': symbol,
        'mode': mode,
        'stop_loss': stop_loss,
        'initial_balance': initial_balance,
        'position_size_pct': position_size_pct,
        'interval': interval,
        'candle_interval': candle_interval,
        'check_date': check_date
    }


def main():
    """Main function"""
    print_banner()
    
    # Check API keys
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")
    
    if not api_key or not api_secret:
        print("⚠️  UYARI: .env dosyasında API key'leri bulunamadı!")
        print("   Lütfen .env dosyasını oluşturun ve API key'lerinizi ekleyin.\n")
        use_mock = input("Test verisi ile devam edilsin mi? (y/n): ").strip().lower()
        if use_mock != 'y':
            print("❌ Program sonlandırıldı.")
            return
    
    # Get user input
    params = get_user_input()
    
    print("\n" + "="*70)
    print("🚀 Trading Bot Başlatılıyor...")
    print("="*70)
    print(f"Coin: {params['symbol']}")
    print(f"Mod: {'Live Trading' if params['mode'] == '1' else 'Backtest'}")
    print(f"Stop Loss: {params['stop_loss']*100}%")
    print(f"Başlangıç Bakiyesi: ${params['initial_balance']:.2f}")
    print("="*70)
    
    # Create trading bot
    bot = TradingBot(coin_symbol=params['symbol'])
    
    # Setup Telegram Observer if credentials are available
    telegram_bot_token = os.getenv("TELEGRAM_TOKEN")
    telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    # Register observers (possible telegram user as well)
    logger = LoggingObserver(log_file="trade_log.txt")
    bot.register_observer(logger)
    if telegram_bot_token and telegram_chat_id:
        telegram_alerter = TelegramAlertObserver(token=telegram_bot_token, chat_id=telegram_chat_id)
        bot.register_observer(telegram_alerter)
    
    
    # Run trading
    try:
        if params['mode'] == "1":
            # Live trading
            final_balance = bot.simulate_trading(
                initial_balance=params['initial_balance'],
                stop_loss=params['stop_loss'],
                interval=params['interval'],
                position_size_pct=params['position_size_pct']
            )
        else:
            # Backtest
            final_balance = bot.backtest_trading(
                initial_balance=params['initial_balance'],
                stop_loss=params['stop_loss'],
                interval=params['candle_interval'],
                check_date=params['check_date'],
                position_size_pct=params['position_size_pct']
            )
        
        print(f"\n✅ Trading tamamlandı!")
        print(f"   Son bakiye: ${final_balance:.2f}")
        print(f"   Kar/Zarar: ${final_balance - params['initial_balance']:.2f}")
        print(f"\n📝 Loglar: trade_log.txt dosyasında kaydedildi.\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Trading kullanıcı tarafından durduruldu.")
    except Exception as e:
        print(f"\n❌ Hata oluştu: {e}")


if __name__ == "__main__":
    main()