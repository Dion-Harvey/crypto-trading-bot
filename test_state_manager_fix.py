#!/usr/bin/env python3
"""
Quick test to verify the state manager fix
"""

import sys
import os

# Add the current directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_state_manager_fix():
    """Test that state manager calls work correctly"""
    try:
        from state_manager import get_state_manager
        
        state_manager = get_state_manager()
        
        # Test the update_trading_state method with keyword arguments
        print("Testing state_manager.update_trading_state() with keyword arguments...")
        
        # This should work now
        state_manager.update_trading_state(
            holding_position=True,
            entry_price=65000.0,
            stop_loss_price=63700.0,
            take_profit_price=66950.0
        )
        
        print("✅ First update_trading_state call successful")
        
        # Test second call
        state_manager.update_trading_state(
            holding_position=False,
            entry_price=None,
            stop_loss_price=None,
            take_profit_price=None
        )
        
        print("✅ Second update_trading_state call successful")
        print("✅ State manager fix verified!")
        
    except Exception as e:
        print(f"❌ State manager test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_state_manager_fix()
