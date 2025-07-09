#!/usr/bin/env python3
"""
Quick Import Test
Tests that bot can import all new modules
"""

def test_imports():
    try:
        # Test config loading
        from enhanced_config import get_bot_config
        config = get_bot_config()
        print(f"✅ Config loaded: {config.config['system']['loop_interval_seconds']}s intervals")
        
        # Test price jump detector
        from price_jump_detector import detect_price_jump, get_price_jump_detector
        print("✅ Price jump detector imported")
        
        # Test multi-timeframe MA
        from multi_timeframe_ma import detect_multi_timeframe_ma_signals
        print("✅ Multi-timeframe MA imported")
        
        # Test that detector can be created
        detector = get_price_jump_detector(config.config)
        print("✅ Price jump detector created")
        
        print("\n🎉 All imports successful! Bot is ready.")
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

if __name__ == "__main__":
    test_imports()
