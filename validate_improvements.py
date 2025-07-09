#!/usr/bin/env python3
"""
Price Jump Improvements Validation Script
Tests the new price jump detection and multi-timeframe features
"""

import sys
import json
from pathlib import Path

# Add the project directory to Python path
sys.path.append(str(Path(__file__).parent))

def validate_config():
    """Validate the enhanced configuration"""
    print("🔧 Validating Enhanced Configuration...")
    
    try:
        with open('enhanced_config.json', 'r') as f:
            config = json.load(f)
        
        # Check key improvements
        improvements = {
            'faster_loop': config['system']['loop_interval_seconds'] == 30,
            'shorter_cooldown': config['trading']['trade_cooldown_seconds'] == 900,
            'price_jump_detection': config['system'].get('price_jump_detection', {}).get('enabled', False),
            'jump_threshold': config['system'].get('price_jump_detection', {}).get('threshold_pct', 0) == 0.5,
            'jump_override': config['system'].get('price_jump_detection', {}).get('override_cooldown', False)
        }
        
        print("✅ Configuration Validation:")
        for improvement, status in improvements.items():
            status_icon = "✅" if status else "❌"
            print(f"   {status_icon} {improvement}: {status}")
        
        return all(improvements.values())
        
    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")
        return False

def test_price_jump_detector():
    """Test price jump detection functionality"""
    print("\n🚀 Testing Price Jump Detection...")
    
    try:
        from price_jump_detector import PriceJumpDetector
        
        # Mock config
        config = {
            'system': {
                'price_jump_detection': {
                    'enabled': True,
                    'threshold_pct': 0.5,
                    'detection_window_seconds': 60,
                    'override_cooldown': True
                }
            }
        }
        
        detector = PriceJumpDetector(config)
        
        # Test normal price movement (no jump)
        detector.add_price_point(100.0)
        detector.add_price_point(100.2)  # 0.2% change
        jump1 = detector.add_price_point(100.3)  # 0.3% total change
        
        # Test price jump
        jump2 = detector.add_price_point(100.8)  # 0.8% total change - should trigger
        
        print("✅ Price Jump Detection Tests:")
        print(f"   Normal movement (0.3%): {'No jump' if jump1 is None else 'Jump detected'}")
        print(f"   Price jump (0.8%): {'Jump detected' if jump2 is not None else 'No jump'}")
        
        if jump2:
            analysis = detector.get_jump_analysis(jump2)
            print(f"   Jump analysis: {analysis['direction']} {analysis['magnitude']:.2f}% - {analysis['urgency']}")
        
        return jump1 is None and jump2 is not None
        
    except Exception as e:
        print(f"❌ Price jump detection test failed: {e}")
        return False

def test_multi_timeframe_analysis():
    """Test multi-timeframe MA analysis"""
    print("\n📊 Testing Multi-Timeframe Analysis...")
    
    try:
        from multi_timeframe_ma import _analyze_timeframe_ma, _combine_timeframe_signals
        import pandas as pd
        
        # Create mock data
        data = {
            'close': [100 + i * 0.5 for i in range(50)],  # Upward trend
            'volume': [1000 + i * 10 for i in range(50)]
        }
        df = pd.DataFrame(data)
        
        # Test 1-minute timeframe analysis
        signal_1m = _analyze_timeframe_ma(df, 125.0, '1m')
        
        # Test 5-minute timeframe analysis  
        signal_5m = _analyze_timeframe_ma(df, 125.0, '5m')
        
        # Test signal combination
        combined = _combine_timeframe_signals(signal_1m, signal_5m)
        
        print("✅ Multi-Timeframe Analysis Tests:")
        print(f"   1m signal: {signal_1m['action']} ({signal_1m['confidence']:.3f})")
        print(f"   5m signal: {signal_5m['action']} ({signal_5m['confidence']:.3f})")
        print(f"   Combined: {combined['action']} ({combined['confidence']:.3f})")
        print(f"   Agreement: {combined.get('agreement', False)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Multi-timeframe analysis test failed: {e}")
        return False

def validate_bot_integration():
    """Validate that the bot can import new modules"""
    print("\n🤖 Validating Bot Integration...")
    
    try:
        # Test imports
        from price_jump_detector import detect_price_jump, get_price_jump_detector
        from multi_timeframe_ma import detect_multi_timeframe_ma_signals
        
        print("✅ Bot Integration Tests:")
        print("   ✅ Price jump detector import successful")
        print("   ✅ Multi-timeframe MA import successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Bot integration validation failed: {e}")
        return False

def main():
    """Main validation function"""
    print("🔍 PRICE JUMP IMPROVEMENTS VALIDATION")
    print("=" * 60)
    
    tests = [
        ("Configuration", validate_config),
        ("Price Jump Detection", test_price_jump_detector),
        ("Multi-Timeframe Analysis", test_multi_timeframe_analysis),
        ("Bot Integration", validate_bot_integration)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ {test_name} test failed with error: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("📊 VALIDATION SUMMARY")
    print("=" * 60)
    
    all_passed = all(results)
    status_icon = "✅" if all_passed else "❌"
    
    for i, (test_name, _) in enumerate(tests):
        result_icon = "✅" if results[i] else "❌"
        print(f"{result_icon} {test_name}: {'PASSED' if results[i] else 'FAILED'}")
    
    print("\n" + "=" * 60)
    print(f"{status_icon} OVERALL STATUS: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")
    
    if all_passed:
        print("🎉 All improvements successfully implemented and validated!")
        print("🚀 Bot is ready for enhanced price jump detection!")
    else:
        print("⚠️ Some issues found - please review the test results above.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
