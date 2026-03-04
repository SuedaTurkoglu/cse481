"""
Strategy pattern testleri
"""
from Patterns.Strategies import RSIStrategy, MACDStrategy, ADXStrategy, DefaultStrategy
import pandas as pd
import numpy as np

# Test verisi oluştur
np.random.seed(42)
test_data = pd.DataFrame({
    'Close': np.random.uniform(40000, 50000, 100),
    'Volume': np.random.uniform(1000, 5000, 100),
    'rsi': np.random.uniform(20, 80, 100),
    'adx': np.random.uniform(15, 35, 100),
    'macd': np.random.uniform(-100, 100, 100),
    'di_plus': np.random.uniform(10, 30, 100),
    'di_minus': np.random.uniform(10, 30, 100),
    'short_term_ma': np.random.uniform(40000, 50000, 100),
    'long_term_ma': np.random.uniform(40000, 50000, 100)
})

def test_strategy(strategy_class, strategy_name):
    print(f"\n{'='*50}")
    print(f"Testing {strategy_name}")
    print(f"{'='*50}")
    
    strategy = strategy_class(stop_loss=0.02)
    row = test_data.iloc[-1]
    
    try:
        action = strategy.execute_strategy(row, test_data)
        print(f"✅ {strategy_name} Action: {action}")
        print(f"   RSI: {row['rsi']:.2f}")
        print(f"   ADX: {row['adx']:.2f}")
        print(f"   MACD: {row['macd']:.2f}")
    except Exception as e:
        print(f"❌ Error: {e}")

# Test all strategies
if __name__ == "__main__":
    print("🚀 Starting Strategy Tests...")
    
    test_strategy(RSIStrategy, "RSI Strategy")
    test_strategy(MACDStrategy, "MACD Strategy")
    test_strategy(ADXStrategy, "ADX Strategy")
    test_strategy(DefaultStrategy, "Default Strategy")
    
    print(f"\n{'='*50}")
    print("✅ All tests completed!")
    print(f"{'='*50}\n")