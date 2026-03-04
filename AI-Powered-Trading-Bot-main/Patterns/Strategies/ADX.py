from Patterns.Template.strategy_template import TradingStrategyTemplate
import pandas as pd


class ADXStrategy(TradingStrategyTemplate):
    """
    CONCRETE STRATEGY: ADX tabanlı trading stratejisi
    """
    
    def __init__(self, stop_loss: float = 0.02):
        super().__init__(stop_loss)
        print(f"🎯 ADX Strategy initialized with stop_loss: {stop_loss}")

    def label_logic(self, row: pd.Series) -> str:
        """ADX tabanlı etiketleme mantığı"""
        adx = row.get('adx', 0)
        rsi = row.get('rsi', 50)
        di_plus = row.get('di_plus', 0)
        di_minus = row.get('di_minus', 0)

        # Buy Signal
        if adx > 25 and di_plus > di_minus and rsi > 60:
            return "Buy"

        # Sell Signal
        elif adx > 25 and di_minus > di_plus and rsi < 40:
            return "Sell"

        return "Hold"

    def feature_columns(self) -> list:
        """ADX stratejisi için gerekli feature'lar"""
        return ['rsi', 'adx', 'di_plus', 'di_minus', 'macd', 'Close', 'Volume']