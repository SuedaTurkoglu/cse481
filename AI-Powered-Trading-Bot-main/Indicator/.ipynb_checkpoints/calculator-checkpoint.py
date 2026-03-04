import pandas_ta as ta
import pandas as pd


class IndicatorCalculator:
    """
    Technical Indicator Calculator
    RSI, MACD, ADX ve diğer teknik göstergeleri hesaplar.
    """
    
    def __init__(self, rsi_length=14, macd_fast=12, macd_slow=26, macd_signal=9, adx_length=14):
        """
        Initialize indicator calculator with customizable parameters.
        
        Args:
            rsi_length (int): RSI period (default: 14)
            macd_fast (int): MACD fast period (default: 12)
            macd_slow (int): MACD slow period (default: 26)
            macd_signal (int): MACD signal period (default: 9)
            adx_length (int): ADX period (default: 14)
        """
        self.rsi_length = rsi_length
        self.macd_fast = macd_fast
        self.macd_slow = macd_slow
        self.macd_signal = macd_signal
        self.adx_length = adx_length

    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate all technical indicators for the given DataFrame.
        """
        # Make a copy to avoid modifying the original
        df = df.copy()
        
        # Validate required columns
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        missing_cols = set(required_columns) - set(df.columns)
        if missing_cols:
            raise ValueError(f"❌ Missing required columns: {missing_cols}")
        
        min_periods = max(self.rsi_length, self.macd_slow, self.adx_length, 2 * self.rsi_length)
        if len(df) < min_periods:
            print(f"⚠️  Yetersiz veri: {len(df)} mum bulundu, {min_periods} gerekiyor. İndikatörler hesaplanamadı.")
            return pd.DataFrame(columns=df.columns.tolist() + ['rsi', 'short_term_ma', 'long_term_ma', 'macd', 'adx', 'di_plus', 'di_minus'])

        # Calculate RSI
        df['rsi'] = ta.rsi(df['Close'], length=self.rsi_length)
        
        # Calculate Moving Averages
        df['short_term_ma'] = df['Close'].rolling(window=self.rsi_length).mean()
        df['long_term_ma'] = df['Close'].rolling(window=2 * self.rsi_length).mean()

        # Calculate MACD Histogram
        macd = ta.macd(df['Close'], fast=self.macd_fast, slow=self.macd_slow, signal=self.macd_signal)
        
        if macd is not None and not macd.empty:
            df['macd'] = macd[f'MACDh_{self.macd_fast}_{self.macd_slow}_{self.macd_signal}']
        else:
            print("⚠️  MACD hesaplanamadı (yetersiz veri).")
            df['macd'] = float('nan') # NaN (Not a Number) olarak ayarla

        # Calculate ADX and its components
        adx = ta.adx(df['High'], df['Low'], df['Close'], length=self.adx_length)
        
        if adx is not None and not adx.empty:
            df['adx'] = adx[f'ADX_{self.adx_length}']  # Average Directional Index
            df['di_plus'] = adx[f'DMP_{self.adx_length}']  # Positive Directional Indicator
            df['di_minus'] = adx[f'DMN_{self.adx_length}']  # Negative Directional Indicator
        else:
            print("⚠️  ADX hesaplanamadı (yetersiz veri).")
            df['adx'] = float('nan')
            df['di_plus'] = float('nan')
            df['di_minus'] = float('nan')

        # Calculate Bollinger Bands (BBands)
        # Default parameters: length=20, std=2.0
        bbands = ta.bbands(df['Close'], length=20, std=2.0)

        if bbands is not None and not bbands.empty:
            # Orta Bant (Basit Hareketli Ortalama)
            df['BB_middle'] = bbands[f'BBM_20_2.0_2.0']
            # Üst Bant
            df['BB_upper'] = bbands[f'BBU_20_2.0_2.0']
            # Alt Bant
            df['BB_lower'] = bbands[f'BBL_20_2.0_2.0']
        else:
            print("⚠️ Bollinger Bands hesaplanamadı.")
            df['BB_middle'], df['BB_upper'], df['BB_lower'] = float('nan'), float('nan'), float('nan')

        # Calculate KAMA (Kaufman's Adaptive Moving Average)
        # Default length=10, fast_length=2, slow_length=30
        df['KAMA'] = ta.kama(df['Close'])
        
        if df['KAMA'].isnull().all():
            print("⚠️ KAMA hesaplanamadı.")
            df['KAMA'] = float('nan')

        # Calculate SuperTrend (ST)
        # Default parameters: length=10, multiplier=3.0
        st = ta.supertrend(df['High'], df['Low'], df['Close'], length=10, multiplier=3.0)
        
        if st is not None and not st.empty:
            # SuperTrend Direction: 1 (BUY) veya -1 (SELL)
            df['ST_DIR'] = st[f'SUPERTd_10_3.0'] 
        else:
            print("⚠️ SuperTrend hesaplanamadı.")
            df['ST_DIR'] = float('nan')

        # Calculate Ichimoku Kinko Hyo
        # Default: t(9), k(26), b(52)
        ichimoku = ta.ichimoku(df['High'], df['Low'], df['Close'], tenkan=9, kijun=26, senkou=52, offset=26)

        if ichimoku is not None and len(ichimoku) == 2 and not ichimoku[0].empty:
            # ichimoku[0] -> Tenkan, Kijun, Senkou Span A, Senkou Span B
            # ichimoku[0] -> Chikou Span (geriye kaydırılmış)
            
            # 1. Tenkan-sen (Dönüş Çizgisi)
            df['Tenkan-sen'] = ichimoku[0][f'ITS_9']
            
            # 2. Kijun-sen (Standart Çizgi)
            df['Kijun-sen'] = ichimoku[0][f'IKS_26']
            
            # 3. Senkou Span A (Öncü Açıklık A)
            df['Senkou Span A'] = ichimoku[0][f'ISA_9']
            
            # 4. Senkou Span B (Öncü Açıklık B)
            df['Senkou Span B'] = ichimoku[0][f'ISB_26']
            
            # 5. Chikou Span (Gecikmeli Açıklık)
            # öngörülen ofsetle geriye kaydırır
            df['Chikou Span'] = ichimoku[0][f'ICS_26'] 
        else:
            print("⚠️ Ichimoku hesaplanamadı (yetersiz veri veya hata).")
            # Gerekli tüm Ichimoku sütunlarını NaN olarak atayın (stratejiye hata vermemek için)
            ichimoku_cols = ['Tenkan-sen', 'Kijun-sen', 'Senkou Span A', 'Senkou Span B', 'Chikou Span']
            for col in ichimoku_cols:
                df[col] = float('nan')

        # Basitleştirilmiş Market Yapısı Sinyali (HH/HL için proxy)
        # Kapanış fiyatı, uzun vadeli hareketli ortalamanın (2*RSI length) üzerinde mi?
        df['TREND_UP'] = df['Close'] > df['long_term_ma']
        df['TREND_DOWN'] = df['Close'] < df['long_term_ma']
        
        # HH/HL dizisi yerine kullanılabilecek basit bir Trend Direction kolonu oluştururuz.
        # True: Uptrend (HH/HL'ye benzer), False: Downtrend (LH/LL'ye benzer)
        df['MARKET_STRUCTURE_TREND'] = df['TREND_UP'].apply(lambda x: "UPTREND" if x else "DOWNTREND")

        # Remove rows with NaN values
        df.dropna(inplace=True)
        
        if len(df) == 0:
            print("⚠️  Tüm veriler 'dropna' sonrası kaldırıldı (muhtemelen tüm indikatörler NaN idi).")
        else:
            print(f"✅ Indicators calculated successfully. {len(df)} rows available.")
        
        return df
    
    def calculate_single_indicator(self, df: pd.DataFrame, indicator_name: str) -> pd.DataFrame:
        """
        Calculate a single indicator (opsiyonel - gelecek için).
        
        Args:
            df (pd.DataFrame): DataFrame with OHLCV data
            indicator_name (str): Name of indicator ('rsi', 'macd', 'adx')
            
        Returns:
            pd.DataFrame: DataFrame with the specified indicator
        """
        df = df.copy()
        
        if indicator_name == 'rsi':
            df['rsi'] = ta.rsi(df['Close'], length=self.rsi_length)
        elif indicator_name == 'macd':
            macd = ta.macd(df['Close'], fast=self.macd_fast, slow=self.macd_slow, signal=self.macd_signal)
            df['macd'] = macd[f'MACDh_{self.macd_fast}_{self.macd_slow}_{self.macd_signal}']
        elif indicator_name == 'adx':
            adx = ta.adx(df['High'], df['Low'], df['Close'], length=self.adx_length)
            df['adx'] = adx[f'ADX_{self.adx_length}']
        else:
            raise ValueError(f"❌ Unknown indicator: {indicator_name}")
        
        df.dropna(inplace=True)
        return df