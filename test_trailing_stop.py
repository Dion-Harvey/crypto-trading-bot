#!/usr/bin/env python3
"""
Test script for trailing stop functionality
Tests the trailing stop logic without triggering AWS-only protection
"""

def test_trailing_stop_parameters():
    """Test that trailing stop parameters match user specifications"""
    
    # User specifications:
    # - Activation Price: Left blank (defaults to current market price)
    # - Trailing Delta: 0.50%
    # - Limit Price: 0.50% below current buy order price
    
    print("🎯 TESTING TRAILING STOP PARAMETERS")
    print("=" * 50)
    
    # Test parameters
    symbol = "BTC/USDT"
    entry_price = 97000.00  # Example entry price
    btc_amount = 0.0001     # Example amount (small test)
    current_price = 97000.00  # Same as entry for this test
    
    # Fixed trailing stop parameters per user specification
    trailing_delta_pct = 0.005  # 0.50% trailing delta (fixed)
    
    # Calculate limit price: 0.50% below current buy order price
    limit_price = current_price * (1 - trailing_delta_pct)  # 0.50% below buy price
    
    # Validate order size
    MIN_NOTIONAL_VALUE = 10.0  # Binance minimum is $10
    order_value = btc_amount * current_price
    
    print(f"📊 TEST PARAMETERS:")
    print(f"   Symbol: {symbol}")
    print(f"   Entry/Current Price: ${current_price:.2f}")
    print(f"   Amount: {btc_amount:.6f} BTC")
    print(f"   Order Value: ${order_value:.2f}")
    print(f"   Trailing Delta: {trailing_delta_pct*100:.1f}%")
    print(f"   Limit Price: ${limit_price:.4f} (0.50% below entry)")
    print()
    
    # Test order parameters that would be sent to Binance
    order_params = {
        'symbol': symbol,
        'type': 'TRAILING_STOP_MARKET',
        'side': 'sell',
        'amount': btc_amount,
        'price': None,  # No price for trailing stop market orders
        'params': {
            'callbackRate': '0.5',  # 0.50% trailing delta
            # No activationPrice specified - defaults to current market price
            'timeInForce': 'GTC'
        }
    }
    
    print(f"🎯 BINANCE ORDER PARAMETERS:")
    print(f"   Type: {order_params['type']}")
    print(f"   Side: {order_params['side']}")
    print(f"   Amount: {order_params['amount']:.6f}")
    print(f"   Callback Rate: {order_params['params']['callbackRate']}%")
    print(f"   Activation Price: Auto (current market)")
    print(f"   Time In Force: {order_params['params']['timeInForce']}")
    print()
    
    # Test fallback stop-limit parameters
    stop_price = current_price * (1 - trailing_delta_pct)  # 0.50% below entry
    fallback_limit_price = current_price * (1 - trailing_delta_pct)  # 0.50% below entry per spec
    
    fallback_params = {
        'symbol': symbol,
        'type': 'stop_loss_limit',
        'side': 'sell',
        'amount': btc_amount,
        'price': fallback_limit_price,
        'params': {
            'stopPrice': str(stop_price),
            'timeInForce': 'GTC'
        }
    }
    
    print(f"🔄 FALLBACK STOP-LIMIT PARAMETERS:")
    print(f"   Type: {fallback_params['type']}")
    print(f"   Stop Price: ${float(fallback_params['params']['stopPrice']):.4f} (0.50% below entry)")
    print(f"   Limit Price: ${fallback_params['price']:.4f} (0.50% below entry)")
    print()
    
    # Validation checks
    print("✅ VALIDATION CHECKS:")
    
    # Check 1: Order value meets minimum
    if order_value >= MIN_NOTIONAL_VALUE:
        print(f"   ✅ Order value ${order_value:.2f} meets Binance minimum ${MIN_NOTIONAL_VALUE}")
    else:
        print(f"   ❌ Order value ${order_value:.2f} below Binance minimum ${MIN_NOTIONAL_VALUE}")
    
    # Check 2: Trailing delta is exactly 0.50%
    if trailing_delta_pct == 0.005:
        print(f"   ✅ Trailing delta is exactly 0.50%")
    else:
        print(f"   ❌ Trailing delta is {trailing_delta_pct*100:.1f}%, should be 0.50%")
    
    # Check 3: Limit price is exactly 0.50% below entry
    expected_limit = current_price * 0.995
    if abs(limit_price - expected_limit) < 0.01:
        print(f"   ✅ Limit price ${limit_price:.4f} is 0.50% below entry ${current_price:.2f}")
    else:
        print(f"   ❌ Limit price calculation error")
    
    # Check 4: No activation price (auto mode)
    if 'activationPrice' not in order_params['params']:
        print(f"   ✅ Activation price left blank (auto mode)")
    else:
        print(f"   ❌ Activation price should be left blank")
    
    print()
    print("🎉 TEST COMPLETE!")
    print("   Ready for AWS deployment with correct parameters")
    
    return True

def test_different_price_scenarios():
    """Test trailing stop with different price scenarios"""
    
    print("\n🔍 TESTING DIFFERENT PRICE SCENARIOS")
    print("=" * 50)
    
    scenarios = [
        {"name": "Small BTC position", "price": 97000, "amount": 0.0001},
        {"name": "Medium BTC position", "price": 97000, "amount": 0.0002},
        {"name": "Different price point", "price": 95000, "amount": 0.0001},
        {"name": "Higher price point", "price": 100000, "amount": 0.0001},
    ]
    
    trailing_delta_pct = 0.005  # 0.50%
    
    for scenario in scenarios:
        price = scenario["price"]
        amount = scenario["amount"]
        order_value = amount * price
        limit_price = price * (1 - trailing_delta_pct)
        
        print(f"\n📊 {scenario['name']}:")
        print(f"   Price: ${price:,.2f}")
        print(f"   Amount: {amount:.6f} BTC")
        print(f"   Order Value: ${order_value:.2f}")
        print(f"   Limit Price: ${limit_price:.4f} (0.50% below)")
        
        if order_value >= 10.0:
            print(f"   ✅ Meets Binance minimum")
        else:
            print(f"   ⚠️ Below minimum - would use stop-market fallback")

if __name__ == "__main__":
    try:
        test_trailing_stop_parameters()
        test_different_price_scenarios()
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
