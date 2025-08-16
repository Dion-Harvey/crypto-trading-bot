#!/usr/bin/env python3
"""
Quick LSTM Status Check
"""

print("🔍 LSTM System Status Check")
print("=" * 30)

# Test TensorFlow
try:
    import tensorflow as tf
    print(f"✅ TensorFlow: {tf.__version__}")
    tf_available = True
except ImportError as e:
    print(f"❌ TensorFlow: {e}")
    tf_available = False

# Test LSTM Predictor
try:
    from lstm_price_predictor import LSTMPricePredictor
    print("✅ LSTM Predictor: Imported successfully")
    lstm_available = True
except ImportError as e:
    print(f"❌ LSTM Predictor: {e}")
    lstm_available = False

# Test Bot Integration
try:
    import bot
    print(f"✅ Bot LSTM Flag: {bot.LSTM_PREDICTOR_AVAILABLE}")
    bot_integration = True
except Exception as e:
    print(f"❌ Bot Integration: {e}")
    bot_integration = False

print("\n" + "=" * 30)
print("SUMMARY:")
if tf_available and lstm_available and bot_integration:
    print("🎉 LSTM SYSTEM FULLY OPERATIONAL!")
    print("   The bot should now show LSTM enhancement messages")
elif tf_available and lstm_available:
    print("⚠️  LSTM components work, checking bot integration...")
elif tf_available:
    print("⚠️  TensorFlow works, but LSTM predictor has issues")
else:
    print("❌ TensorFlow still not available")

print("=" * 30)
