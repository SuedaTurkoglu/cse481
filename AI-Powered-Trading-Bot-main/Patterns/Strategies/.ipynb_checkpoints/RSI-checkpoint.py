from Patterns.Template.strategy_template import TradingStrategyTemplate
import pandas as pd


class RSIStrategy(TradingStrategyTemplate):
    """
    CONCRETE STRATEGY: RSI tabanlı trading stratejisi
    
    Mantık:
    - RSI < 30 ve ADX > 25: Buy (oversold + trend var)
    - RSI > 70 ve ADX > 25: Sell (overbought + trend var)
    - Diğer durumlar: Hold
    """
    
    def __init__(self, stop_loss: float = 0.02):
        super().__init__(stop_loss)
        print(f"🎯 RSI Strategy initialized with stop_loss: {stop_loss}")

    def label_logic(self, row: pd.Series) -> str:
        """RSI tabanlı etiketleme mantığı"""
        rsi = row.get('rsi', 50)
        adx = row.get('adx', 0)
        volume = row.get('Volume', 0)
        
        if adx > 25:  # Strong trend
            if rsi < 30:  # Oversold
                return "Buy"
            elif rsi > 70:  # Overbought
                return "Sell"
        
        elif adx < 20:  # Weak trend
            if rsi < 35:
                return "Buy"
            elif rsi > 65:
                return "Sell"
        
        if volume < 10:  # Low volume
            return "Hold"
        
        return "Hold"

    def feature_columns(self) -> list:
        """RSI stratejisi için gerekli feature'lar"""
        return ['rsi', 'adx', 'macd', 'Close', 'Volume']