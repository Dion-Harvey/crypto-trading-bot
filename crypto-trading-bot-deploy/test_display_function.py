#!/usr/bin/env python3
"""
Test the exact institutional analysis display that's causing the KeyError
"""

import sys
sys.path.append('.')
from bot import display_institutional_analysis_safe

def test_display_function():
    """Test the display function with various data structures"""
    print("Testing display_institutional_analysis_safe function...")
    
    # Test 1: Normal complete data
    normal_data = {
        'market_regime': {
            'regime': 'stable',
            'confidence': 0.50,
            'recommendation': 'Wait for more data'
        },
        'correlation_analysis': {
            'regime': 'moderate_correlation'
        },
        'ml_signal': {
            'action': 'HOLD',
            'confidence': 0.30
        },
        'risk_analysis': {
            'risk_score': 'LOW',
            'var_daily': 0.02
        },
        'kelly_position_size': 7.50
    }
    
    print("\n--- Test 1: Normal complete data ---")
    try:
        display_institutional_analysis_safe(normal_data)
        print("✅ PASS: Normal data displayed successfully")
    except Exception as e:
        print(f"❌ FAIL: Normal data failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: Missing recommendation key
    broken_data = {
        'market_regime': {
            'regime': 'stable',
            'confidence': 0.50
            # Missing 'recommendation' key
        },
        'correlation_analysis': {
            'regime': 'moderate_correlation'
        }
    }
    
    print("\n--- Test 2: Missing recommendation key ---")
    try:
        display_institutional_analysis_safe(broken_data)
        print("✅ PASS: Missing key handled gracefully")
    except Exception as e:
        print(f"❌ FAIL: Missing key caused error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: Empty/None data
    print("\n--- Test 3: Empty data ---")
    try:
        display_institutional_analysis_safe({})
        display_institutional_analysis_safe(None)
        print("✅ PASS: Empty data handled gracefully")
    except Exception as e:
        print(f"❌ FAIL: Empty data caused error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 4: Test actual user's data structure from the error
    user_data = {
        'market_regime': {
            'regime': 'stable',
            'confidence': 0.50
        },
        'correlation_analysis': {
            'regime': 'moderate_correlation'
        },
        'ml_signal': {
            'action': 'HOLD',
            'confidence': 0.30
        },
        'risk_analysis': {
            'risk_score': 'LOW'
        },
        'kelly_position_size': 7.50
    }
    
    print("\n--- Test 4: User's actual data structure ---")
    try:
        display_institutional_analysis_safe(user_data)
        print("✅ PASS: User data displayed successfully")
    except Exception as e:
        print(f"❌ FAIL: User data failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_display_function()
