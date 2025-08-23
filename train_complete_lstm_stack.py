#!/usr/bin/env python3
"""
🧠 COMPLETE LSTM MODEL TRAINING SCRIPT
=====================================

Trains all 4 LSTM timeframe models for the complete stack:
- 1m model: Ultra-short-term predictions for scalping
- 5m model: Short-term trend confirmation  
- 15m model: Medium-term signal enhancement
- 1h model: Long-term trend validation

This script fetches appropriate data for each timeframe and trains
models with enhanced feature engineering for maximum accuracy.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bot import exchange, optimized_config, LSTM_PREDICTOR_AVAILABLE
from log_utils import log_message
import json
import time
from datetime import datetime

def fetch_training_data_for_timeframe(timeframe):
    """Fetch appropriate amount of data for each timeframe"""
    try:
        # Determine optimal data amounts for each timeframe
        data_amounts = {
            '1m': 1000,   # ~16.7 hours of 1m data
            '5m': 800,    # ~2.8 days of 5m data  
            '15m': 672,   # ~1 week of 15m data
            '1h': 500     # ~3 weeks of 1h data
        }
        
        amount = data_amounts.get(timeframe, 500)
        print(f"📊 Fetching {amount} periods of {timeframe} data...")
        
        # Fetch data from exchange
        from bot import fetch_ohlcv
        data = fetch_ohlcv(exchange, 'BTC/USDT', timeframe, amount)
        
        if data is not None and len(data) >= 200:
            print(f"✅ Successfully fetched {len(data)} periods of {timeframe} data")
            return data
        else:
            print(f"⚠️ Insufficient {timeframe} data: {len(data) if data is not None else 0} periods")
            return None
            
    except Exception as e:
        print(f"❌ Error fetching {timeframe} data: {e}")
        return None

def train_complete_lstm_stack():
    """Train all 4 LSTM models with optimized data for each timeframe"""
    
    if not LSTM_PREDICTOR_AVAILABLE:
        print("❌ LSTM system not available - install TensorFlow first")
        return False
    
    print("🧠 COMPLETE LSTM STACK TRAINING")
    print("=" * 50)
    print("Training models for: 1m, 5m, 15m, 1h timeframes")
    print("This will take approximately 10-15 minutes...")
    print("=" * 50)
    
    try:
        from src.lstm_price_predictor import get_lstm_predictor, train_lstm_models
        
        # Get LSTM predictor instance
        lstm_predictor = get_lstm_predictor(optimized_config)
        
        # Define all timeframes for complete stack
        timeframes = ['1m', '5m', '15m', '1h']
        training_results = {}
        training_stats = {}
        
        # Train each timeframe with appropriate data
        for timeframe in timeframes:
            print(f"\n🎯 Training {timeframe} LSTM model...")
            print(f"⏱️ Started at: {datetime.now().strftime('%H:%M:%S')}")
            
            start_time = time.time()
            
            # Fetch timeframe-specific data
            training_data = fetch_training_data_for_timeframe(timeframe)
            
            if training_data is None:
                print(f"❌ Skipping {timeframe} model - insufficient data")
                training_results[timeframe] = False
                continue
            
            try:
                # Train the model for this specific timeframe
                result = train_lstm_models(training_data, optimized_config, [timeframe])
                success = result.get(timeframe, False)
                training_results[timeframe] = success
                
                # Track training time
                training_time = time.time() - start_time
                training_stats[timeframe] = {
                    'success': success,
                    'training_time': training_time,
                    'data_points': len(training_data)
                }
                
                if success:
                    print(f"✅ {timeframe} model trained successfully in {training_time:.1f}s")
                    
                    # Try to get model accuracy if available
                    try:
                        model_path = f'models/lstm/lstm_{timeframe}.h5'
                        if os.path.exists(model_path):
                            print(f"   📁 Model saved: {model_path}")
                    except:
                        pass
                        
                else:
                    print(f"❌ {timeframe} model training failed")
                    
            except Exception as e:
                print(f"❌ Error training {timeframe} model: {e}")
                training_results[timeframe] = False
                training_stats[timeframe] = {
                    'success': False,
                    'error': str(e),
                    'training_time': time.time() - start_time
                }
        
        # Display final results
        print("\n" + "=" * 50)
        print("🎯 LSTM TRAINING COMPLETE")
        print("=" * 50)
        
        successful_models = sum(1 for success in training_results.values() if success)
        total_models = len(training_results)
        
        print(f"📊 Overall Success: {successful_models}/{total_models} models trained")
        print("\n📋 Detailed Results:")
        
        for timeframe in timeframes:
            success = training_results.get(timeframe, False)
            stats = training_stats.get(timeframe, {})
            
            status = "✅ SUCCESS" if success else "❌ FAILED"
            print(f"   {timeframe:>3s} model: {status}")
            
            if success and 'training_time' in stats:
                print(f"        Training time: {stats['training_time']:.1f}s")
                print(f"        Data points: {stats.get('data_points', 'N/A')}")
            elif 'error' in stats:
                print(f"        Error: {stats['error']}")
        
        # Check for model files
        print(f"\n📁 Model Files Status:")
        model_files = ['lstm_1m.h5', 'lstm_5m.h5', 'lstm_15m.h5', 'lstm_1h.h5']
        existing_models = 0
        
        for model_file in model_files:
            model_path = f'models/lstm/{model_file}'
            if os.path.exists(model_path):
                file_size = os.path.getsize(model_path) / 1024  # KB
                print(f"   ✅ {model_file}: {file_size:.1f} KB")
                existing_models += 1
            else:
                print(f"   ❌ {model_file}: Not found")
        
        # Save training summary
        summary = {
            'training_date': datetime.now().isoformat(),
            'total_models': total_models,
            'successful_models': successful_models,
            'existing_model_files': existing_models,
            'results': training_results,
            'stats': training_stats
        }
        
        with open('lstm_training_summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n📄 Training summary saved to: lstm_training_summary.json")
        
        if successful_models == total_models:
            print(f"\n🎉 COMPLETE SUCCESS! All {total_models} LSTM models ready for trading!")
            log_message(f"🧠 LSTM COMPLETE STACK: All {total_models} models trained successfully")
        elif successful_models > 0:
            print(f"\n⚠️ PARTIAL SUCCESS: {successful_models}/{total_models} models trained")
            log_message(f"🧠 LSTM PARTIAL STACK: {successful_models}/{total_models} models trained")
        else:
            print(f"\n❌ TRAINING FAILED: No models were successfully trained")
            log_message(f"🧠 LSTM TRAINING FAILED: 0/{total_models} models trained")
        
        return successful_models == total_models
        
    except Exception as e:
        print(f"\n❌ Critical error in LSTM training: {e}")
        log_message(f"❌ LSTM training critical error: {e}")
        return False

def verify_lstm_models():
    """Verify all LSTM models are properly trained and accessible"""
    print("\n🔍 VERIFYING LSTM MODEL STACK...")
    
    try:
        from src.lstm_price_predictor import get_lstm_predictor
        
        # Get predictor instance
        predictor = get_lstm_predictor(optimized_config)
        
        # Test each timeframe
        timeframes = ['1m', '5m', '15m', '1h']
        working_models = []
        
        for timeframe in timeframes:
            try:
                # Try to load/access the model
                model_key = f'lstm_{timeframe}'
                if hasattr(predictor, 'models') and model_key in predictor.models:
                    working_models.append(timeframe)
                    print(f"   ✅ {timeframe} model: Loaded and ready")
                else:
                    # Check if model file exists
                    model_path = f'models/lstm/lstm_{timeframe}.h5'
                    if os.path.exists(model_path):
                        print(f"   ⚠️ {timeframe} model: File exists but not loaded")
                    else:
                        print(f"   ❌ {timeframe} model: Missing")
            except Exception as e:
                print(f"   ❌ {timeframe} model: Error - {e}")
        
        print(f"\n📊 Model Verification: {len(working_models)}/{len(timeframes)} models working")
        
        if len(working_models) == len(timeframes):
            print("🎉 Complete LSTM stack verified and ready!")
            return True
        else:
            print("⚠️ LSTM stack incomplete - some models need attention")
            return False
            
    except Exception as e:
        print(f"❌ Verification error: {e}")
        return False

if __name__ == "__main__":
    print("🧠 LSTM Complete Stack Training Script")
    print("=" * 40)
    
    # Run the complete training
    success = train_complete_lstm_stack()
    
    if success:
        # Verify the models
        verify_lstm_models()
        print("\n🚀 Ready to restart bot with complete LSTM stack!")
    else:
        print("\n⚠️ Please check errors above and retry if needed")
