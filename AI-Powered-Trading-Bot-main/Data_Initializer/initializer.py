from binance.client import Client
import websockets
import json
import pandas as pd


class DataLoader:
    """
    Binance API ve WebSocket kullanarak kripto verilerini çeken sınıf.
    """
    
    def __init__(self):
        """Initialize DataLoader with WebSocket URL"""
        self.BINANCE_WS_URL = "wss://stream.binance.com:9443/ws/{symbol}@kline_1s"

    async def download_crypto_data(self, symbol: str) -> pd.DataFrame:
        """
        WebSocket kullanarak real-time veri çeker (1 saniye kline).
        
        Args:
            symbol (str): Kripto sembolü (örn: 'btcusdt')
            
        Returns:
            pd.DataFrame: OHLCV verisi
        """
        url = self.BINANCE_WS_URL.format(symbol=symbol.lower())
        df = []
        
        try:
            async with websockets.connect(url) as websocket:
                # Receive only one message
                msg = await websocket.recv()
                data = json.loads(msg)

                # Extract kline data
                kline = data['k']
                timestamp = pd.to_datetime(kline['t'], unit='ms')
                timestamp = timestamp.tz_localize("UTC").tz_convert("Europe/Istanbul")
                timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                
                df.append({
                    "Timestamp": timestamp,
                    "Open": float(kline['o']),
                    "High": float(kline['h']),
                    "Low": float(kline['l']),
                    "Close": float(kline['c']),
                    "Volume": float(kline['v'])
                })

                df = pd.DataFrame(df)
                print(f"✅ WebSocket data received for {symbol.upper()}")
                            
        except Exception as e:
            print(f"❌ Error in WebSocket connection: {e}")
            df = pd.DataFrame()

        return df

    def download_crypto_data_interval(self, api_key: str, api_secret: str, 
                                     symbol: str, interval: str = "1m", 
                                     limit: int = 100) -> pd.DataFrame:
        """
        REST API kullanarak historical veri çeker.
        
        Args:
            api_key (str): Binance API key
            api_secret (str): Binance API secret
            symbol (str): Kripto sembolü (örn: 'BTCUSDT')
            interval (str): Zaman aralığı (örn: '1m', '5m', '1h')
            limit (int): Kaç adet kline çekilecek
            
        Returns:
            pd.DataFrame: OHLCV verisi
        """
        try:
            client = Client(api_key, api_secret)
            klines = client.get_historical_klines(symbol, interval, limit=limit)
            
            data = []
            for kline in klines:
                timestamp = pd.to_datetime(kline[0], unit='ms')
                timestamp = timestamp.tz_localize("UTC").tz_convert("Europe/Istanbul")
                timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                
                data.append({
                    "Timestamp": timestamp,
                    "Open": float(kline[1]),
                    "High": float(kline[2]),
                    "Low": float(kline[3]),
                    "Close": float(kline[4]),
                    "Volume": float(kline[5])
                })
            
            df = pd.DataFrame(data)
            print(f"✅ Historical data loaded: {len(df)} rows for {symbol}")
            return df
            
        except Exception as e:
            print(f"❌ Error loading historical data: {e}")
            return pd.DataFrame()
    
    def download_crypto_data_interval_backtest(self, api_key: str, api_secret: str,
                                               symbol: str, interval: str, 
                                               check_date: str) -> pd.DataFrame:
        """
        Backtest için belirli tarih aralığında veri çeker.
        """
        try:
            client = Client(api_key, api_secret)
            klines = client.get_historical_klines(symbol, interval, check_date)
            
            # Eğer klines None ise veya boşsa, hatayı burada yakala
            if not klines:
                print(f"❌ Error loading backtest data: No data received from Binance. Check API keys or date range.")
                return pd.DataFrame()
            
            data = []
            for kline in klines:
                # kline'ın da None olmadığını kontrol et
                if kline is None:
                    continue 

                timestamp = pd.to_datetime(kline[0], unit='ms')
                timestamp = timestamp.tz_localize("UTC").tz_convert("Europe/Istanbul")
                timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                
                data.append({
                    "Timestamp": timestamp,
                    "Open": float(kline[1]),
                    "High": float(kline[2]),
                    "Low": float(kline[3]),
                    "Close": float(kline[4]),
                    "Volume": float(kline[5])
                })
            
            df = pd.DataFrame(data)
            print(f"✅ Backtest data loaded: {len(df)} rows from {check_date}")
            return df
            
        except Exception as e:
            # Hata (örn. 'NoneType' object is not subscriptable) burada yakalanacak
            print(f"❌ Error in download_crypto_data_interval_backtest: {e}")
            return pd.DataFrame() # Hata durumunda her zaman boş DataFrame döndür