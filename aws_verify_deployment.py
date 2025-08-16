#!/usr/bin/env python3
"""
AWS Deployment Verification Script
Tests all modules required for live data access
"""

import sys
import importlib
import traceback
from datetime import datetime

def test_module_import(module_name, description=""):
    """Test if a module can be imported successfully"""
    try:
        importlib.import_module(module_name)
        print(f"✅ {module_name} - {description}")
        return True
    except ImportError as e:
        print(f"❌ {module_name} - FAILED: {e}")
        return False
    except Exception as e:
        print(f"⚠️ {module_name} - ERROR: {e}")
        return False

def main():
    print("🔍 AWS DEPLOYMENT VERIFICATION")
    print("=" * 50)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("")
    
    # Track results
    total_tests = 0
    passed_tests = 0
    
    # Core dependencies
    print("📦 TESTING CORE DEPENDENCIES:")
    dependencies = [
        ('ccxt', 'Binance US API connection'),
        ('pandas', 'Data manipulation'),
        ('numpy', 'Numerical computing'),
        ('scipy', 'Scientific computing'),
        ('requests', 'HTTP requests'),
        ('json', 'JSON handling'),
        ('time', 'Time functions'),
        ('datetime', 'Date/time handling')
    ]
    
    for module, desc in dependencies:
        total_tests += 1
        if test_module_import(module, desc):
            passed_tests += 1
    
    print("")
    print("🎯 TESTING CORE BOT MODULES:")
    
    # Core bot modules
    bot_modules = [
        ('config', 'Configuration and API keys'),
        ('enhanced_config', 'Enhanced configuration management'),
        ('state_manager', 'Trading state persistence'),
        ('log_utils', 'Logging and performance tracking'),
        ('performance_tracker', 'Trade performance analysis'),
        ('success_rate_enhancer', 'Success rate optimization')
    ]
    
    for module, desc in bot_modules:
        total_tests += 1
        if test_module_import(module, desc):
            passed_tests += 1
    
    print("")
    print("📊 TESTING LIVE DATA MODULES:")
    
    # Live data modules
    live_data_modules = [
        ('price_jump_detector', 'Real-time price movement detection'),
        ('multi_timeframe_ma', 'Multi-timeframe MA analysis'),
        ('enhanced_multi_timeframe_ma', 'Enhanced timeframe analysis'),
        ('priority_functions_5m1m', 'Priority signal management')
    ]
    
    for module, desc in live_data_modules:
        total_tests += 1
        if test_module_import(module, desc):
            passed_tests += 1
    
    print("")
    print("📈 TESTING TRADING STRATEGIES:")
    
    # Strategy modules
    strategy_modules = [
        ('strategies.ma_crossover', 'MA crossover strategy'),
        ('strategies.multi_strategy_optimized', 'Multi-strategy optimization'),
        ('strategies.hybrid_strategy', 'Hybrid trading approach'),
        ('enhanced_multi_strategy', 'Enhanced strategy coordination'),
        ('institutional_strategies', 'Institutional-grade algorithms')
    ]
    
    for module, desc in strategy_modules:
        total_tests += 1
        if test_module_import(module, desc):
            passed_tests += 1
    
    print("")
    print("🔧 TESTING BOT FUNCTIONALITY:")
    
    # Test bot import and key functions
    try:
        print("Testing main bot import...")
        import bot
        print("✅ bot.py - Main application imported")
        passed_tests += 1
        
        # Test connection function
        print("Testing connection function...")
        if hasattr(bot, 'test_connection'):
            print("✅ test_connection - Connection test function available")
            passed_tests += 1
        else:
            print("❌ test_connection - Function not found")
        
        # Test MA crossover detection
        print("Testing MA crossover detection...")
        if hasattr(bot, 'detect_ma_crossover_signals'):
            print("✅ detect_ma_crossover_signals - MA crossover detection available")
            passed_tests += 1
        else:
            print("❌ detect_ma_crossover_signals - Function not found")
        
        # Test multi-layer coordination
        print("Testing multi-layer strategy coordination...")
        if hasattr(bot, 'coordinate_multi_layer_strategy'):
            print("✅ coordinate_multi_layer_strategy - Multi-layer coordination available")
            passed_tests += 1
        else:
            print("❌ coordinate_multi_layer_strategy - Function not found")
            
        total_tests += 4
        
    except Exception as e:
        print(f"❌ bot.py - FAILED: {e}")
        print("Traceback:")
        traceback.print_exc()
        total_tests += 4
    
    # Final results
    print("")
    print("📋 VERIFICATION RESULTS:")
    print("=" * 30)
    print(f"Total tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("")
        print("🎉 ALL TESTS PASSED!")
        print("✅ AWS deployment is ready for live data trading")
        print("")
        print("🚀 TO START TRADING:")
        print("   python3 bot.py")
        return True
    else:
        print("")
        print("⚠️ SOME TESTS FAILED")
        print("❌ Please fix the issues before starting live trading")
        print("")
        print("🔧 COMMON FIXES:")
        print("   • Install missing dependencies: pip install -r requirements.txt")
        print("   • Check file permissions: chmod +x *.py")
        print("   • Verify all files are uploaded")
        print("   • Check API keys in config.py")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
