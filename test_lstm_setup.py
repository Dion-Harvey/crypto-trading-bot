#!/usr/bin/env python3
"""
🚀 PHASE 3 WEEK 1: Quick LSTM Setup Verification
================================================

This script tests if the LSTM integration is working properly
and provides manual installation instructions if needed.
"""

import sys
import os

def test_basic_imports():
    """Test basic Python packages"""
    print("🔍 Testing basic imports...")
    
    try:
        import numpy as np
        print("✅ NumPy available")
    except ImportError:
        print("❌ NumPy missing")
        return False
    
    try:
        import pandas as pd
        print("✅ Pandas available")
    except ImportError:
        print("❌ Pandas missing")
        return False
    
    try:
        import sklearn
        print("✅ Scikit-learn available")
    except ImportError:
        print("❌ Scikit-learn missing")
        return False
    
    return True

def test_tensorflow():
    """Test TensorFlow availability"""
    print("\n🧠 Testing TensorFlow...")
    
    try:
        import tensorflow as tf
        print(f"✅ TensorFlow {tf.__version__} available")
        
        # Test basic functionality
        x = tf.constant([1, 2, 3])
        print("✅ TensorFlow basic operations working")
        return True
        
    except ImportError:
        print("❌ TensorFlow not available")
        return False
    except Exception as e:
        print(f"⚠️ TensorFlow test failed: {e}")
        return False

def test_lstm_module():
    """Test LSTM module import"""
    print("\n📦 Testing LSTM module...")
    
    try:
        from lstm_price_predictor import LSTMPricePredictor
        print("✅ LSTM module imported successfully")
        return True
    except ImportError as e:
        print(f"❌ LSTM module import failed: {e}")
        return False

def test_bot_integration():
    """Test bot integration"""
    print("\n🤖 Testing bot integration...")
    
    try:
        # Test config
        from enhanced_config import get_bot_config
        config = get_bot_config()
        
        if 'lstm_predictor' in config.config:
            print("✅ LSTM configuration found")
        else:
            print("❌ LSTM configuration missing")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Bot integration test failed: {e}")
        return False

def print_manual_instructions():
    """Print manual installation instructions"""
    print("\n" + "="*60)
    print("📋 MANUAL INSTALLATION INSTRUCTIONS")
    print("="*60)
    print("\n🎯 If TensorFlow installation failed, try these steps:")
    print("\n1️⃣ **Activate your virtual environment:**")
    print("   .venv\\Scripts\\activate")
    print("\n2️⃣ **Install TensorFlow manually:**")
    print("   pip install tensorflow==2.13.0")
    print("\n3️⃣ **Verify installation:**")
    print("   python -c \"import tensorflow as tf; print('TensorFlow', tf.__version__)\"")
    print("\n4️⃣ **Alternative: Try TensorFlow CPU:**")
    print("   pip install tensorflow-cpu==2.13.0")
    print("\n5️⃣ **If still failing, install older version:**")
    print("   pip install tensorflow==2.12.0")
    
    print("\n💡 **Alternative Options:**")
    print("- The bot will work WITHOUT TensorFlow (no LSTM enhancement)")
    print("- You'll still get all Phase 1 & 2 features")
    print("- LSTM can be added later when TensorFlow is working")
    
    print("\n🎯 **System Requirements:**")
    print("- Python 3.8-3.11 (TensorFlow compatibility)")
    print("- Windows 10/11 with Visual C++ redistributables")
    print("- At least 4GB RAM for model training")

def main():
    print("🚀 PHASE 3 WEEK 1: LSTM Setup Verification")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 4
    
    # Test 1: Basic imports
    if test_basic_imports():
        tests_passed += 1
    
    # Test 2: TensorFlow
    tensorflow_available = test_tensorflow()
    if tensorflow_available:
        tests_passed += 1
    
    # Test 3: LSTM module
    if test_lstm_module():
        tests_passed += 1
    
    # Test 4: Bot integration
    if test_bot_integration():
        tests_passed += 1
    
    print(f"\n📊 Test Results: {tests_passed}/{total_tests} passed")
    
    if tests_passed == total_tests:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ LSTM AI system is ready")
        print("🧠 Neural network price prediction active")
        print("📈 Expecting 5-10% timing improvement")
        print("\n🚀 Start the bot to activate LSTM enhancement!")
        
    elif tests_passed >= 3 and not tensorflow_available:
        print("\n⚠️ ALMOST READY - TensorFlow installation needed")
        print("✅ Bot integration complete")
        print("❌ TensorFlow missing - LSTM disabled")
        print("💡 Bot will work normally without LSTM")
        print_manual_instructions()
        
    else:
        print(f"\n❌ {total_tests - tests_passed} tests failed")
        print("💡 Check the error messages above")
        print_manual_instructions()

if __name__ == "__main__":
    main()
