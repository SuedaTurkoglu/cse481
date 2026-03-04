"""
Observer Pattern testleri
"""
from Patterns.Observer import LoggingObserver


def test_singleton_pattern():
    """Test Singleton pattern - aynı instance'ı döndürmeli"""
    print("\n" + "="*60)
    print("Testing Singleton Pattern")
    print("="*60)
    
    # LoggingObserver singleton test
    logger1 = LoggingObserver()
    logger2 = LoggingObserver()
    
    print(f"Logger1 ID: {id(logger1)}")
    print(f"Logger2 ID: {id(logger2)}")
    assert logger1 is logger2, "❌ LoggingObserver is not singleton!"
    print("✅ LoggingObserver Singleton test passed")
    

def test_observer_updates():
    """Test observer update metodları"""
    print("\n" + "="*60)
    print("Testing Observer Updates")
    print("="*60)
    
    logger = LoggingObserver(log_file="test_trade_log.txt")
    
    # Test mesajları gönder
    test_messages = [
        "Bought BTCUSDT, Current balance is: 10000, Current Strategy: RSIStrategy",
        "Sold BTCUSDT, Current balance is: 10500, Current Strategy: MACDStrategy",
        "Bought BTCUSDT, Current balance is: 10500, Current Strategy: ADXStrategy",
        "Sold BTCUSDT, Current balance is: 11000, Current Strategy: DefaultStrategy",
        "Simulation complete"
    ]
    
    for message in test_messages:
        logger.update(message)
    
    print("\n✅ Observer updates test passed")


if __name__ == "__main__":
    print("🚀 Starting Observer Pattern Tests...")
    
    test_singleton_pattern()
    test_observer_updates()
    
    print("\n" + "="*60)
    print("✅ All Observer tests completed!")
    print("="*60 + "\n")