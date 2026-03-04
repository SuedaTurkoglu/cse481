# Patterns/Strategies/GridSearchStrategy.py

from Patterns.Strategies.base_strategy import BaseStrategy # BaseStrategy kullandığınızı varsayıyoruz
from typing import Dict, Any, List
import pandas as pd

class GridSearchStrategy(BaseStrategy):
    """
    Test Case 1 için Grid-Search kurallarını uygulayan strateji.
    """
    
    def __init__(self, entry_rule_id: str, exit_rule_id: str, stop_loss: float):
        super().__init__(stop_loss)
        self.entry_rule_id = entry_rule_id
        self.exit_rule_id = exit_rule_id
        
        # SuperTrend için -1 (SELL) kuralını temsil etmek için sabit tanımlayalım
        self.ST_SELL_SIGNAL = -1
        self.ST_BUY_SIGNAL = 1

    def _check_entry_conditions(self, row: pd.Series, df: pd.DataFrame) -> bool:
        """
        Giriş kurallarını kontrol eder.
        """
        # --- A. RSI Girişleri ---
        if self.entry_rule_id == "RSI_20":
            return row['rsi'] < 20
        if self.entry_rule_id == "RSI_25":
            return row['rsi'] < 25
        if self.entry_rule_id == "RSI_30":
            return row['rsi'] < 30
        if self.entry_rule_id == "RSI_40":
            return row['rsi'] < 40
            
        # --- B. Bollinger Band Reversal Girişi ---
        if self.entry_rule_id == "BB_Reversal":
            # close[t-1] < BB_lower[t-1], close[t] > BB_lower[t]
            if len(df) < 2: return False # Yeterli veri yok
            prev_row = df.iloc[-2]
            return (prev_row['Close'] < prev_row['BB_lower']) and (row['Close'] > row['BB_lower'])
        
        # --- C. KAMA/SuperTrend Girişi ---
        if self.entry_rule_id == "KAMA_ST":
            # close[t] < KAMA[t], ST_DIR[t] == SELL
            return (row['Close'] < row['KAMA']) and (row['ST_DIR'] == self.ST_SELL_SIGNAL)
            
        return False # Tanımsız Giriş ID'si
    
    def _check_exit_conditions(self, row: pd.Series, df: pd.DataFrame, entry_price: float) -> bool:
        """
        Çıkış kurallarını kontrol eder. SADECE kârlı olduğunda tetiklenmelidir.
        """
        current_profit = (row['Close'] - entry_price) / entry_price
        
        # 1. Kârlılık Kontrolü (Zorunlu Kural)
        if current_profit <= 0:
            return False 

        # --- A. RSI Çıkışları ---
        if self.exit_rule_id == "RSI_60": return row['rsi'] > 60
        if self.exit_rule_id == "RSI_50": return row['rsi'] > 50
        if self.exit_rule_id == "RSI_45": return row['rsi'] > 45
        if self.exit_rule_id == "RSI_40": return row['rsi'] > 40
        
        # --- B. SuperTrend Çıkışı ---
        if self.exit_rule_id == "ST_BUY": 
            return row['ST_DIR'] == self.ST_BUY_SIGNAL

        # --- C. Bollinger Band Çıkışları ---
        # BB_Exit (A): BB_middle < close < BB_upper
        if self.exit_rule_id == "BB_A":
            return (row['BB_middle'] < row['Close']) and (row['Close'] < row['BB_upper'])
            
        # BB_Exit (B): BB_lower < close < BB_middle (near_ratio'ya göre 7 konfigürasyon)
        if self.exit_rule_id.startswith("BB_B"):
            # Örn: BB_B_0.25 -> near_ratio = 0.25
            ratio = float(self.exit_rule_id.split('_')[-1])
            
            # near_ratio kontrolü: Fiyatın, BB_lower'dan BB_middle'a olan mesafesi
            # BB_middle - BB_lower = toplam mesafe
            # close - BB_lower = kat edilen mesafe
            distance_ratio = (row['Close'] - row['BB_lower']) / (row['BB_middle'] - row['BB_lower'])
            
            return (row['BB_lower'] < row['Close']) and (row['Close'] < row['BB_middle']) and (distance_ratio >= ratio)

        return False # Tanımsız Çıkış ID'si
        
    def execute_strategy(self, row: pd.Series, df: pd.DataFrame, position: float, entry_price: float) -> str:
        """Stratejiyi yürütür ve eylem döndürür."""
        # Not: Stop-Loss mantığı genellikle TradingBot'un ana döngüsünde (burada yoksa) veya 
        # BaseStrategy'de kontrol edilmelidir. Grid-Search'te kayıp beklenmediği için (Exit sadece kârlı iken)
        # burada Stop-Loss'u zorunlu kılmıyoruz, ancak risk yönetimi için eklenmesi gerekir.
        
        # 1. Çıkış Kontrolü (Pozisyon açıksa)
        if position > 0:
            if self._check_exit_conditions(row, df, entry_price):
                return "Sell", self.exit_rule_id 
            return "Hold", None

        # 2. Giriş Kontrolü (Pozisyon kapalıysa)
        if position == 0:
            if self._check_entry_conditions(row, df):
                return "Buy", self.entry_rule_id
            return "Hold", None
            
        return "Hold", None