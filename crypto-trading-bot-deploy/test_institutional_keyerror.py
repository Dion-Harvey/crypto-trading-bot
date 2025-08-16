#!/usr/bin/env python3
"""
Quick test for institutional analysis KeyError issue
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from institutional_strategies import InstitutionalStrategyManager
from strategies.ma_crossover import fetch_ohlcv
import ccxt
import pandas as pd

def test_institutional_analysis():
    """Test institutional analysis to check for KeyError issues"""
    print("🔍 TESTING INSTITUTIONAL ANALYSIS FOR KeyError ISSUES")
    print("="*60)
    
    try:
        # Create minimal test data
        test_data = {
            'timestamp': pd.date_range('2025-01-01', periods=100, freq='1min'),
            'open': [100 + i for i in range(100)],
            'high': [101 + i for i in range(100)],
            'low': [99 + i for i in range(100)],
            'close': [100.5 + i for i in range(100)],
            'volume': [1000 for _ in range(100)]
        }
        df = pd.DataFrame(test_data)
        
        # Initialize institutional manager
        institutional_manager = InstitutionalStrategyManager()
        
        # Test 1: Normal operation with sufficient data
        print("\n📋 Test 1: Normal operation (100 data points)")
        try:
            signal = institutional_manager.get_institutional_signal(
                df, portfolio_value=100, base_position_size=10
            )
            print(f"✅ Signal generated: {signal['action']} (conf: {signal['confidence']:.2f})")
            
            # Check institutional analysis structure
            if 'institutional_analysis' in signal:
                inst = signal['institutional_analysis']
                print(f"✅ Institutional analysis present")
                print(f"   Market regime keys: {list(inst['market_regime'].keys())}")
                print(f"   Recommendation present: {'recommendation' in inst['market_regime']}")
                print(f"   Recommendation value: {inst['market_regime'].get('recommendation', 'MISSING')}")
            else:
                print("❌ No institutional analysis in signal")
                
        except Exception as e:
            print(f"❌ Test 1 failed: {e}")
        
        # Test 2: Insufficient data (should trigger early return)
        print("\n📋 Test 2: Insufficient data (10 data points)")
        small_df = df.head(10)
        try:
            signal = institutional_manager.get_institutional_signal(
                small_df, portfolio_value=100, base_position_size=10
            )
            print(f"✅ Signal generated: {signal['action']} (conf: {signal['confidence']:.2f})")
            
            # Check institutional analysis structure
            if 'institutional_analysis' in signal:
                inst = signal['institutional_analysis']
                print(f"✅ Institutional analysis present")
                print(f"   Market regime keys: {list(inst['market_regime'].keys())}")
                print(f"   Recommendation present: {'recommendation' in inst['market_regime']}")
                print(f"   Recommendation value: {inst['market_regime'].get('recommendation', 'MISSING')}")
            else:
                print("❌ No institutional analysis in signal")
                
        except Exception as e:
            print(f"❌ Test 2 failed: {e}")
        
        # Test 3: Direct regime detection test
        print("\n📋 Test 3: Direct regime detection")
        try:
            regime = institutional_manager.regime_detector.detect_regime(small_df)
            print(f"✅ Regime detected: {regime}")
            print(f"   Keys present: {list(regime.keys())}")
            print(f"   Recommendation: {regime.get('recommendation', 'MISSING')}")
        except Exception as e:
            print(f"❌ Test 3 failed: {e}")
            
        print("\n" + "="*60)
        print("✅ INSTITUTIONAL ANALYSIS TEST COMPLETE")
        
    except Exception as e:
        print(f"❌ Overall test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_institutional_analysis()
