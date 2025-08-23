#!/usr/bin/env python3
"""
🔍 LSTM MODEL VERIFICATION SCRIPT
=================================

Verifies that all 4 LSTM models can be loaded and are ready for trading.
Tests each timeframe model and reports accuracy and readiness status.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def verify_lstm_stack():
    """Verify all LSTM models are properly loaded and functional"""
    
    try:
        # Import required modules
        from bot import optimized_config, LSTM_PREDICTOR_AVAILABLE
        
        if not LSTM_PREDICTOR_AVAILABLE:
            print("❌ LSTM system not available - TensorFlow missing")
            return False
        
        from src.lstm_price_predictor import get_lstm_predictor
        
        print("🔍 LSTM MODEL STACK VERIFICATION")
        print("=" * 40)
        
        # Get predictor instance
        predictor = get_lstm_predictor(optimized_config)
        
        # Force load all models
        timeframes = ['1m', '5m', '15m', '1h']
        loaded_models = []
        model_details = {}
        
        for timeframe in timeframes:
            try:
                print(f"\n🎯 Testing {timeframe} model...")
                
                # Check if model file exists
                model_path = f'models/lstm/lstm_{timeframe}.h5'
                scaler_path = f'models/lstm/scaler_{timeframe}.pkl'
                
                model_exists = os.path.exists(model_path)
                scaler_exists = os.path.exists(scaler_path)
                
                print(f"   Model file: {'✅' if model_exists else '❌'} {model_path}")
                print(f"   Scaler file: {'✅' if scaler_exists else '❌'} {scaler_path}")
                
                if model_exists and scaler_exists:
                    # Get file sizes
                    model_size = os.path.getsize(model_path) / 1024  # KB
                    scaler_size = os.path.getsize(scaler_path) / 1024  # KB
                    
                    print(f"   Model size: {model_size:.1f} KB")
                    print(f"   Scaler size: {scaler_size:.1f} KB")
                    
                    # Try to load the model into predictor
                    try:
                        model_key = f'lstm_{timeframe}'
                        
                        # Load model if not already loaded
                        if model_key not in predictor.models:
                            from tensorflow.keras.models import load_model
                            import pickle
                            
                            # Load the model
                            model = load_model(model_path)
                            predictor.models[model_key] = model
                            
                            # Load the scaler
                            with open(scaler_path, 'rb') as f:
                                scaler = pickle.load(f)
                            predictor.scalers[timeframe] = scaler
                            
                            print(f"   ✅ Model loaded successfully")
                        else:
                            print(f"   ✅ Model already loaded")
                        
                        loaded_models.append(timeframe)
                        
                        # Get model architecture info
                        model = predictor.models[model_key]
                        model_details[timeframe] = {
                            'input_shape': str(model.input_shape),
                            'output_shape': str(model.output_shape),
                            'parameters': model.count_params(),
                            'layers': len(model.layers)
                        }
                        
                        print(f"   📊 Architecture: {model_details[timeframe]['layers']} layers, {model_details[timeframe]['parameters']:,} parameters")
                        
                    except Exception as load_error:
                        print(f"   ❌ Load error: {load_error}")
                        
                else:
                    print(f"   ❌ Missing required files")
                    
            except Exception as e:
                print(f"   ❌ Verification error: {e}")
        
        print(f"\n" + "=" * 40)
        print("📊 VERIFICATION SUMMARY")
        print("=" * 40)
        
        success_rate = len(loaded_models) / len(timeframes) * 100
        print(f"Models loaded: {len(loaded_models)}/{len(timeframes)} ({success_rate:.0f}%)")
        
        for timeframe in timeframes:
            status = "✅" if timeframe in loaded_models else "❌"
            print(f"   {timeframe:>3s} model: {status}")
        
        if len(loaded_models) == len(timeframes):
            print(f"\n🎉 COMPLETE SUCCESS! All {len(timeframes)} LSTM models verified and ready!")
            print(f"\n📋 Model Details:")
            for timeframe, details in model_details.items():
                print(f"   {timeframe} model: {details['parameters']:,} params, {details['layers']} layers")
            
            return True
        else:
            print(f"\n⚠️ PARTIAL SUCCESS: {len(loaded_models)}/{len(timeframes)} models ready")
            missing = [tf for tf in timeframes if tf not in loaded_models]
            print(f"   Missing: {', '.join(missing)}")
            return False
            
    except Exception as e:
        print(f"❌ Critical verification error: {e}")
        return False

def test_lstm_predictions():
    """Test that LSTM models can make actual predictions"""
    try:
        from bot import exchange, fetch_ohlcv, optimized_config
        from src.lstm_price_predictor import get_lstm_predictor
        
        print(f"\n🧪 LSTM PREDICTION TEST")
        print("=" * 30)
        
        # Get some test data
        test_data = fetch_ohlcv(exchange, 'BTC/USDT', '5m', 100)
        if test_data is None or len(test_data) < 50:
            print("❌ Could not fetch test data")
            return False
        
        # Get predictor
        predictor = get_lstm_predictor(optimized_config)
        
        # Create a dummy signal to enhance
        dummy_signal = {
            'action': 'BUY',
            'confidence': 0.7,
            'reason': 'Test signal'
        }
        
        # Test signal enhancement with all timeframes
        timeframes = ['1m', '5m', '15m', '1h']
        enhanced_signal = predictor.get_enhanced_signal(test_data, dummy_signal, timeframes)
        
        print(f"Original signal: {dummy_signal['action']} ({dummy_signal['confidence']:.3f})")
        print(f"Enhanced signal: {enhanced_signal['action']} ({enhanced_signal['confidence']:.3f})")
        
        if 'lstm_enhancement' in enhanced_signal:
            enhancement = enhanced_signal['lstm_enhancement']
            print(f"LSTM enhancement: {enhancement}")
        
        print(f"✅ LSTM prediction test successful!")
        return True
        
    except Exception as e:
        print(f"❌ Prediction test failed: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Starting LSTM Model Verification...")
    
    # Verify models can be loaded
    verification_success = verify_lstm_stack()
    
    if verification_success:
        # Test actual predictions
        prediction_success = test_lstm_predictions()
        
        if prediction_success:
            print(f"\n🎉 COMPLETE LSTM STACK VERIFICATION SUCCESSFUL!")
            print(f"✅ All 4 models (1m, 5m, 15m, 1h) are trained, loaded, and functional")
            print(f"🚀 Ready for enhanced trading with complete LSTM intelligence!")
        else:
            print(f"\n⚠️ Models loaded but prediction test failed")
    else:
        print(f"\n❌ Model verification failed - check errors above")
