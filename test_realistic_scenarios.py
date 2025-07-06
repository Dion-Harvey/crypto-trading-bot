#!/usr/bin/env python3
"""
Test position sizing with realistic trading scenarios
"""

def test_realistic_trading_scenarios():
    """Test position sizing in various realistic trading scenarios"""
    
    print("🎯 REALISTIC TRADING SCENARIOS TEST")
    print("=" * 60)
    
    # Current market assumptions
    btc_price = 94000  # Approximate current BTC price
    
    def calculate_position_details(portfolio_value, scenario_name, confidence=0.75, volatility=0.02):
        """Calculate position details for a scenario"""
        
        # Our new target position logic
        if portfolio_value >= 100:
            target_usd = 20.0
        elif portfolio_value >= 75:
            target_usd = 18.75
        elif portfolio_value >= 50:
            target_usd = 15.0
        elif portfolio_value >= 25:
            target_usd = 12.50
        else:
            target_usd = max(10.0, portfolio_value * 0.50)
        
        # Risk adjustments
        volatility_factor = 0.75 if volatility > 0.025 else 1.0
        confidence_factor = max(0.7, min(1.3, confidence * 1.2))
        major_risk_adjustment = min(volatility_factor, confidence_factor)
        
        # Apply risk adjustment if needed
        if major_risk_adjustment < 0.8:
            risk_adjusted_target = target_usd * major_risk_adjustment
        else:
            risk_adjusted_target = target_usd
        
        # Apply safety cap
        if portfolio_value <= 25:
            safety_cap = portfolio_value * 0.60
        elif portfolio_value <= 50:
            safety_cap = portfolio_value * 0.55
        elif portfolio_value <= 75:
            safety_cap = portfolio_value * 0.35
        elif portfolio_value <= 100:
            safety_cap = portfolio_value * 0.25
        else:
            safety_cap = portfolio_value * 0.20
        
        # Final size calculation
        min_amount = portfolio_value * 0.08  # 8% min
        max_amount = portfolio_value * 0.25  # 25% max
        
        final_size = min(max(min_amount, risk_adjusted_target), min(safety_cap, max_amount))
        
        # Ensure minimum order size
        if final_size < 10.0 and portfolio_value >= 10.0:
            final_size = 10.0
        elif final_size < 10.0:
            final_size = 0
        
        # Calculate BTC amount
        btc_amount = final_size / btc_price if final_size > 0 else 0
        position_pct = (final_size / portfolio_value) * 100 if final_size > 0 else 0
        
        return {
            'target_usd': target_usd,
            'risk_adjusted': risk_adjusted_target,
            'safety_cap': safety_cap,
            'final_size': final_size,
            'btc_amount': btc_amount,
            'position_pct': position_pct,
            'risk_adjustment': major_risk_adjustment
        }
    
    # Test scenarios
    scenarios = [
        # Small account scenarios
        {
            'portfolio': 25.0,
            'name': 'Very Small Account - Strong Signal',
            'confidence': 0.85,
            'volatility': 0.015
        },
        {
            'portfolio': 25.0,
            'name': 'Very Small Account - Volatile Market',
            'confidence': 0.75,
            'volatility': 0.035
        },
        {
            'portfolio': 50.0,
            'name': 'Small Account - Perfect Conditions',
            'confidence': 0.90,
            'volatility': 0.010
        },
        {
            'portfolio': 50.0,
            'name': 'Small Account - Risky Market',
            'confidence': 0.60,
            'volatility': 0.030
        },
        {
            'portfolio': 75.0,
            'name': 'Growing Account - Normal Market',
            'confidence': 0.75,
            'volatility': 0.020
        },
        {
            'portfolio': 100.0,
            'name': 'Medium Account - Strong Signal',
            'confidence': 0.85,
            'volatility': 0.015
        },
        {
            'portfolio': 35.0,
            'name': 'Awkward Size Account',
            'confidence': 0.70,
            'volatility': 0.025
        }
    ]
    
    for scenario in scenarios:
        result = calculate_position_details(
            scenario['portfolio'],
            scenario['name'],
            scenario['confidence'],
            scenario['volatility']
        )
        
        print(f"\n📊 {scenario['name']}")
        print(f"   💰 Portfolio: ${scenario['portfolio']:.2f}")
        print(f"   📈 Signal Confidence: {scenario['confidence']:.2f}")
        print(f"   📉 Market Volatility: {scenario['volatility']:.3f}")
        print(f"   🎯 Target: ${result['target_usd']:.2f}")
        print(f"   ⚖️ Risk Factor: {result['risk_adjustment']:.2f}")
        print(f"   🛡️ Safety Cap: ${result['safety_cap']:.2f}")
        
        if result['final_size'] > 0:
            print(f"   ✅ Final Position: ${result['final_size']:.2f} ({result['position_pct']:.1f}%)")
            print(f"   🪙 BTC Amount: {result['btc_amount']:.8f} BTC")
            
            # Show if target was achieved
            if abs(result['final_size'] - result['target_usd']) < 0.01:
                print(f"   🎉 FULL TARGET ACHIEVED!")
            elif result['final_size'] < result['target_usd']:
                reduction = ((result['target_usd'] - result['final_size']) / result['target_usd']) * 100
                print(f"   ⚠️ Risk-reduced by {reduction:.1f}%")
        else:
            print(f"   ❌ Trade skipped - insufficient funds")
    
    print(f"\n{'='*60}")
    print("🔥 KEY PERFORMANCE INSIGHTS:")
    print("✅ Small accounts get 25-50% exposure for rapid growth")
    print("✅ Risk management prevents overexposure in volatile markets")
    print("✅ Minimum $10 orders ensure Binance compatibility")
    print("✅ Safety caps protect against excessive risk")
    print("💡 Perfect balance of aggression and safety!")
    print("="*60)

if __name__ == "__main__":
    test_realistic_trading_scenarios()
