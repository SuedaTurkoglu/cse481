from Patterns.Strategies.base_strategy import BaseStrategy
import pandas as pd
from typing import final

class IchimokuCustomStrategy(BaseStrategy):
    """
    Test Case 2 için Ichimoku, Piyasa Yapısı ve Hibrit Çıkışları birleştiren strateji.
    """
    
    def __init__(self, stop_loss: float):
        super().__init__(stop_loss)
        self.strategy_name = "IchimokuCustomStrategy"
        
        # SuperTrend Direction sinyalleri
        self.ST_BUY_SIGNAL = 1

    def _get_market_structure(self, df: pd.DataFrame) -> str:
        """
        Piyasa yapısını (Trend Filter) belirler. 
        (Basit bir yaklaşım, Swing noktaları tanımlanmalıdır.)
        
        NOT: Gerçek uygulamada, bu metodun HH/HL/LH/LL dizilerini analiz eden
        karmaşık bir sinyalden dönmesi gerekir. Şimdilik son Close/MA ilişkisine dayalı basitleştirilmiş bir trend kontrolü kullanalım.
        """
        if len(df) < 5:
            return "UNKNOWN"
        
        # Basit trend filtresi: Fiyat Tenkan ve Kijun'un üzerinde mi? (HH/HL yerine geçici)
        if (df['Close'].iloc[-1] > df['Tenkan-sen'].iloc[-1] and 
            df['Tenkan-sen'].iloc[-1] > df['Kijun-sen'].iloc[-1]):
            # HH + HL dizisini simüle eder (Güçlü Yükseliş)
            return "UPTREND" 
        
        # LH + LL dizisini simüle eder (Güçlü Düşüş)
        if (df['Close'].iloc[-1] < df['Kijun-sen'].iloc[-1] and
            df['Tenkan-sen'].iloc[-1] < df['Kijun-sen'].iloc[-1]):
            return "DOWNTREND"
            
        return "SIDEWAYS"

    def _check_entry_conditions(self, row: pd.Series, df: pd.DataFrame) -> bool:
        """
        Ichimoku ve Piyasa Yapısı Giriş Kurallarını Kontrol Eder.
        """
        # Ichimoku Kuralları
        tenkan_kijun_buy = row['Tenkan-sen'] > row['Kijun-sen']
        price_above_cloud = row['Close'] > row['Senkou Span A'] and row['Close'] > row['Senkou Span B']
        market_uptrend = self._get_market_structure(df) == "UPTREND"
        chikou_above_price = row['Chikou Span'] > row['Close']

        base_entry = (tenkan_kijun_buy and 
                      price_above_cloud and 
                      market_uptrend)
                  
        # 4h ve 1d gibi stabil grafiklerde ek onay (Chikou) şart
        if base_entry and chikou_above_price:
            return True
    
        # 1h gibi gürültülü grafiklerde Chikou'yu zorunlu kılmayarak giriş yap
        if base_entry:
            pass # Şu anki durumda bu koşulun da zorlanması gerekiyor.
            
        return False
    
    def _check_exit_conditions(self, row: pd.Series, entry_price: float, position: float) -> bool:
        """
        Hibrit Çıkış Kurallarını Kontrol Eder.
        """
        
        # Fiyat Hareketi/Trend Kaybı Çıkışları
        price_below_cloud = row['Close'] < row['Senkou Span A'] and row['Close'] < row['Senkou Span B'] #her iki bulutun da altı
        
        # Aşırı Alım Çıkışları (Hybrid)
        rsi_overbought = row['rsi'] > 70 
        close_above_bb_upper = row['Close'] > row['BB_upper'] 
        
        # Stop Loss Kontrolü (BaseStrategy'den gelir)
        if self.check_stop_loss(row['Close'], entry_price):
            return True # Zarar kesmeyi tetikle

        # YENİ HIZLI KAR ALMA KURALI (Örn: Sabit %3 Kâr Alma)
        profit_pct = (row['Close'] / entry_price - 1)
        if profit_pct >= 0.03: # Eğer kâr %3 veya daha fazlaysa sat
             return True
        
        # YENİ: Kijun-sen altında kapanış (Basit Trend Değişimi)
        kijun_cross_down = row['Close'] < row['Kijun-sen']
    
        if (price_below_cloud or 
            rsi_overbought or 
            close_above_bb_upper or
            kijun_cross_down):
            return True
            
        return False
        
    def execute_strategy(self, row: pd.Series, df: pd.DataFrame, position: float, entry_price: float) -> tuple[str, str | None]:
        """Stratejiyi yürütür ve eylem ve tetikleyici kuralı döndürür."""
        
        # Çıkış Kontrolü (Pozisyon açıksa)
        if position > 0:
            # Stop Loss (En Yüksek Öncelik)
            if self.check_stop_loss(row['Close'], entry_price):
                return "Sell", "StopLoss"
                
            # Hibrit Çıkış Kuralları
            if self._check_exit_conditions(row, entry_price, position):
                # Çıkış sinyalini basitleştirilmiş olarak 'CustomExit' döndür
                return "Sell", "CustomExit"

            # Piyasa yapısı tersine döndüğünde çıkış (Opsiyonel)
            market_shift = self._get_market_structure(df) == "DOWNTREND"
            if market_shift:
                # return "Sell", "MarketShift" # Opsiyonel: Loss of Uptrend
                pass
                
            return "Hold", None

        # Giriş Kontrolü (Pozisyon kapalıysa)
        if position == 0:
            if self._check_entry_conditions(row, df):
                # Giriş kuralını basitleştirilmiş olarak 'IchimokuEntry' döndür
                return "Buy", "IchimokuEntry" 
                
            return "Hold", None
            
        return "Hold", None