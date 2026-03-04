from Patterns.Template.strategy_template import TradingStrategyTemplate
import pandas as pd


class DefaultStrategy(TradingStrategyTemplate):
    """
    CONCRETE STRATEGY: Default moving average stratejisi
    """
    
    def __init__(self, stop_loss: float = 0.02):
        super().__init__(stop_loss)
        print(f"🎯 Default Strategy initialized with stop_loss: {stop_loss}")

    def label_logic(self, row: pd.Series) -> str:
        """Moving average tabanlı etiketleme mantığı"""
        short_term_ma = row.get('short_term_ma', 0)
        long_term_ma = row.get('long_term_ma', 0)
        rsi = row.get('rsi', 50)

        # Determine trend
        if short_term_ma > long_term_ma:
            trend = 'uptrend'
        elif short_term_ma < long_term_ma:
            trend = 'downtrend'
        else:
            trend = 'sideways'

        # Decide action
        if trend == 'uptrend' and rsi < 70:
            return "Buy"
        elif trend == 'downtrend' and rsi > 30:
            return "Sell"
        
        return "Hold"

    def feature_columns(self) -> list:
        """Default stratejisi için gerekli feature'lar"""
        return ['Close', 'rsi', 'Volume']