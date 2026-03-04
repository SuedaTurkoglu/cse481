from Patterns.Template.strategy_template import TradingStrategyTemplate
import pandas as pd


class MACDStrategy(TradingStrategyTemplate):
    """
    CONCRETE STRATEGY: MACD tabanlı trading stratejisi
    """
    
    def __init__(self, stop_loss: float = 0.02):
        super().__init__(stop_loss)
        print(f"🎯 MACD Strategy initialized with stop_loss: {stop_loss}")

    def label_logic(self, row: pd.Series) -> str:
        """MACD tabanlı etiketleme mantığı"""
        macd = row.get('macd', 0)
        adx = row.get('adx', 0)
        rsi = row.get('rsi', 50)

        # Buy Signal
        if macd > 0 and rsi > 60 and adx > 25:
            return "Buy"

        # Sell Signal
        elif macd < 0 and rsi < 40 and adx > 25:
            return "Sell"

        return "Hold"

    def feature_columns(self) -> list:
        """MACD stratejisi için gerekli feature'lar"""
        return ['macd', 'rsi', 'adx', 'Close', 'Volume']