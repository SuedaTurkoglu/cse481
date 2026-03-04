"""
Data Loader ve Indicator Calculator testleri
"""
import pandas as pd
import numpy as np
from Indicator import IndicatorCalculator
from Data_Initializer import DataLoader
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_indicator_calculator():
    """Test indicator calculator with sample data"""
    print("\n" + "="*50)
    print("Testing Indicator Calculator")
    print("="*50)
    
    # Create sample OHLCV data
    np.random.seed(42)
    sample_data = pd.DataFrame({
        'Open': np.random.uniform(40000, 50000, 100),
        'High': np.random.uniform(40000, 50000, 100),
        'Low': np.random.uniform(40000, 50000, 100),
        'Close': np.random.uniform(40000, 50000, 100),
        'Volume': np.random.uniform(1000, 5000, 100)
    })
    
    # Initialize calculator
    calculator = IndicatorCalculator()
    
    # Calculate indicators
    df_with_indicators = calculator.calculate_indicators(sample_data)
    
    print(f"\n📊 Sample data with indicators:")
    print(df_with_indicators[['Close', 'rsi', 'macd', 'adx']].tail())
    print(f"\n✅ Indicator Calculator test passed!")
    

def test_data_loader():
    """Test data loader with Binance API (requires API keys)"""
    print("\n" + "="*50)
    print("Testing Data Loader")
    print("="*50)
    
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")
    
    if not api_key or not api_secret:
        print("⚠️  API keys not found in .env file. Skipping Data Loader test.")
        return
    
    loader = DataLoader()
    
    # Test historical data loading
    print("\n📥 Fetching historical data...")
    df = loader.download_crypto_data_interval(
        api_key=api_key,
        api_secret=api_secret,
        symbol="BTCUSDT",
        interval="1m",
        limit=10
    )
    
    if not df.empty:
        print(f"\n📊 Sample historical data:")
        print(df.tail())
        print(f"\n✅ Data Loader test passed!")
    else:
        print("❌ Data Loader test failed - no data received")


if __name__ == "__main__":
    print("🚀 Starting Data and Indicator Tests...")
    
    test_indicator_calculator()
    test_data_loader()
    
    print("\n" + "="*50)
    print("✅ All tests completed!")
    print("="*50 + "\n")