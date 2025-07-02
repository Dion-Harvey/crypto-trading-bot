#!/usr/bin/env python3
"""
Test for KeyError: 'recommendation' debugging
"""

import sys
import pandas as pd
from institutional_strategies import InstitutionalStrategyManager

def test_regime_detection():
    """Test regime detection to ensure recommendation key is present"""
    print("Testing institutional regime detection...")
    
    try:
        # Create dummy data for testing
        df = pd.DataFrame({
            'timestamp': pd.date_range('2024-01-01', periods=100, freq='1H'),
            'close': [50000 + i*10 for i in range(100)],
            'volume': [1000 + i*5 for i in range(100)],
            'high': [50010 + i*10 for i in range(100)],
            'low': [49990 + i*10 for i in range(100)],
            'open': [50000 + i*10 for i in range(100)]
        })
        
        # Test regime detection
        manager = InstitutionalStrategyManager()
        regime_detector = manager.regime_detector
        result = regime_detector.detect_regime(df)
        
        print(f"Regime detection result: {result}")
        print(f"Keys in result: {list(result.keys())}")
        print(f"Has recommendation: {'recommendation' in result}")
        
        if 'recommendation' in result:
            print(f"Recommendation value: {result['recommendation']}")
            print("✅ PASS: Recommendation key is present")
        else:
            print("❌ FAIL: Missing recommendation key!")
        
        # Test with insufficient data (early return path)
        short_df = df.head(10)  # Less than lookback_period
        result2 = regime_detector.detect_regime(short_df)
        
        print(f"\nShort data result: {result2}")
        print(f"Keys in short result: {list(result2.keys())}")
        print(f"Has recommendation (short): {'recommendation' in result2}")
        
        if 'recommendation' in result2:
            print(f"Short recommendation: {result2['recommendation']}")
            print("✅ PASS: Early return has recommendation key")
        else:
            print("❌ FAIL: Early return missing recommendation key!")
            
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    return True

if __name__ == "__main__":
    success = test_regime_detection()
    sys.exit(0 if success else 1)
