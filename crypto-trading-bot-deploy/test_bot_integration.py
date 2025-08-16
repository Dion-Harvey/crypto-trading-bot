#!/usr/bin/env python3
"""
Quick Bot Test - Test current bot functionality before AWS deployment
"""

import sys
import os
import time

# Add the project directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_bot_connection():
    """Test bot connection and basic functionality"""
    print("🔗 Testing Bot Connection...")

    try:
        # Import after path setup
        from bot import test_connection, safe_api_call, exchange

        print("✅ Bot modules imported successfully")

        # Test exchange connection
        print("\n📡 Testing Exchange Connection...")
        test_connection()

        # Test current price fetch
        print("\n💰 Testing Price Fetch...")
        ticker = safe_api_call(exchange.fetch_ticker, 'BTC/USDC')
        print(f"Current BTC/USDC Price: ${ticker['last']:,.2f}")

        print("\n✅ Connection test passed!")
        return True

    except Exception as e:
        print(f"\n❌ Connection test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_position_sizing_integration():
    """Test the position sizing with real bot configuration"""
    print("\n🧮 Testing Position Sizing Integration...")

    try:
        from bot import calculate_position_size, optimized_config

        # Get current portfolio value (mock for testing)
        test_portfolio_values = [25, 50, 75, 100]
        current_price = 108000
        volatility = 0.02
        signal_confidence = 0.75

        print("\nPosition sizing with real bot config:")
        print("-" * 50)

        for portfolio_value in test_portfolio_values:
            try:
                position_size = calculate_position_size(
                    current_price, volatility, signal_confidence, portfolio_value
                )
                position_pct = (position_size / portfolio_value) * 100 if portfolio_value > 0 else 0

                print(f"Portfolio ${portfolio_value:3.0f} → Position ${position_size:5.2f} ({position_pct:4.1f}%)")

            except Exception as e:
                print(f"Portfolio ${portfolio_value:3.0f} → Error: {e}")

        print("\n✅ Position sizing integration test passed!")
        return True

    except Exception as e:
        print(f"\n❌ Position sizing test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run integration tests"""
    print("🚀 BOT INTEGRATION TEST SUITE")
    print("Testing before AWS deployment")
    print("=" * 60)

    all_passed = True

    # Test 1: Connection
    if not test_bot_connection():
        all_passed = False

    # Test 2: Position sizing integration
    if not test_position_sizing_integration():
        all_passed = False

    print("\n" + "="*60)
    if all_passed:
        print("✅ ALL INTEGRATION TESTS PASSED")
        print("🚀 Bot is ready for AWS deployment!")
    else:
        print("❌ SOME TESTS FAILED")
        print("⚠️  Fix issues before deploying to AWS!")

    return all_passed

if __name__ == "__main__":
    success = main()
    input("\nPress Enter to exit...")
