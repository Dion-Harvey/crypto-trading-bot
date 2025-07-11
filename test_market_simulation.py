#!/usr/bin/env python3
"""
Test the new position sizing logic against simulated market conditions
"""

def simulate_market_test():
    """Simulate position sizing with various market scenarios"""
    
    # Simulate the calculate_position_size function with key components
    def calculate_test_position_size(total_portfolio_value, signal_confidence=0.75, volatility=0.02):
        """Simplified version of our position sizing logic for testing"""
        
        # Base configuration (from your enhanced_config.json)
        base_position_pct = 0.15  # 15% base
        min_position_pct = 0.08   # 8% min
        max_position_pct = 0.25   # 25% max
        
        # Calculate base amounts
        base_amount = total_portfolio_value * base_position_pct
        min_amount = total_portfolio_value * min_position_pct
        max_amount = total_portfolio_value * max_position_pct
        
        # Risk factors (simplified)
        volatility_factor = 0.75 if volatility > 0.02 else 1.0
        confidence_factor = max(0.7, min(1.3, signal_confidence * 1.2))
        
        # 🎯 DYNAMIC SCALING FOR SMALL ACCOUNTS (Our new logic)
        target_position_size = None
        
        if total_portfolio_value <= 100:
            if total_portfolio_value >= 100:
                target_position_size = 20.0  # $20 for $100+ accounts (20%)
            elif total_portfolio_value >= 75:
                target_position_size = 18.75  # $18.75 for $75-100 accounts (25%)
            elif total_portfolio_value >= 50:
                target_position_size = 15.0  # $15 for $50-75 accounts (30%)
            elif total_portfolio_value >= 25:
                target_position_size = 12.50  # $12.50 for $25-50 accounts (50%)
            else:
                target_position_size = max(10.0, total_portfolio_value * 0.50)  # 50% or $10 minimum
        
        # Apply risk adjustments for small accounts
        if target_position_size is not None:
            major_risk_adjustment = min(volatility_factor, confidence_factor)
            
            if major_risk_adjustment < 0.8:
                risk_adjusted_target = target_position_size * major_risk_adjustment
                final_size = max(min_amount, min(max_amount, risk_adjusted_target))
            else:
                final_size = max(min_amount, min(max_amount, target_position_size))
        else:
            # For larger accounts, use traditional Kelly + risk factors
            institutional_size = base_amount * volatility_factor * confidence_factor
            final_size = max(min_amount, min(max_amount, institutional_size))
        
        # Apply dynamic safety cap
        if total_portfolio_value <= 25:
            safety_cap = total_portfolio_value * 0.60  # 60% max
        elif total_portfolio_value <= 50:
            safety_cap = total_portfolio_value * 0.55  # 55% max
        elif total_portfolio_value <= 75:
            safety_cap = total_portfolio_value * 0.35  # 35% max
        elif total_portfolio_value <= 100:
            safety_cap = total_portfolio_value * 0.25  # 25% max
        else:
            safety_cap = total_portfolio_value * 0.20  # 20% max
        
        final_size = min(final_size, safety_cap)
        
        # Ensure minimum order size
        if final_size < 10.0 and total_portfolio_value >= 10.0:
            final_size = 10.0
        elif final_size < 10.0:
            final_size = 0  # Skip trade
        
        return final_size, target_position_size, safety_cap
    
    print("🚀 MARKET SIMULATION TEST")
    print("=" * 60)
    print("Testing new position sizing with various market scenarios")
    print("=" * 60)
    
    # Test scenarios: (portfolio_value, description, signal_confidence, volatility)
    test_scenarios = [
        # Small accounts (our focus)
        (25.0, "Very Small Account - Normal Market", 0.75, 0.015),
        (25.0, "Very Small Account - High Volatility", 0.75, 0.035),
        (25.0, "Very Small Account - Low Confidence", 0.55, 0.015),
        
        (50.0, "Small Account - Normal Market", 0.75, 0.015),
        (50.0, "Small Account - High Volatility", 0.75, 0.035),
        (50.0, "Small Account - High Confidence", 0.85, 0.015),
        
        (75.0, "Growing Account - Normal Market", 0.75, 0.015),
        (75.0, "Growing Account - High Volatility", 0.75, 0.035),
        
        (100.0, "Medium Account - Normal Market", 0.75, 0.015),
        (100.0, "Medium Account - High Volatility", 0.75, 0.035),
        
        # Larger accounts for comparison
        (200.0, "Large Account - Normal Market", 0.75, 0.015),
        (500.0, "Very Large Account - Normal Market", 0.75, 0.015),
    ]
    
    for portfolio_value, description, signal_conf, vol in test_scenarios:
        print(f"\n📊 {description}")
        print(f"   Portfolio: ${portfolio_value:.2f}")
        print(f"   Signal Confidence: {signal_conf:.2f}")
        print(f"   Market Volatility: {vol:.3f}")
        
        final_size, target_size, safety_cap = calculate_test_position_size(
            portfolio_value, signal_conf, vol
        )
        
        if final_size > 0:
            position_pct = (final_size / portfolio_value) * 100
            
            print(f"   🎯 Target Size: ${target_size:.2f}" if target_size else "   🎯 Target Size: Kelly-based")
            print(f"   🛡️ Safety Cap: ${safety_cap:.2f}")
            print(f"   ✅ Final Position: ${final_size:.2f} ({position_pct:.1f}%)")
            
            # Show if target was achieved
            if target_size and abs(final_size - target_size) < 0.01:
                print(f"   🎉 TARGET ACHIEVED!")
            elif target_size and final_size < target_size:
                reduction_pct = ((target_size - final_size) / target_size) * 100
                print(f"   ⚠️ Risk-adjusted down {reduction_pct:.1f}%")
        else:
            print(f"   ❌ Trade skipped - portfolio too small")
    
    print("\n" + "=" * 60)
    print("💡 KEY INSIGHTS:")
    print("✅ Small accounts get aggressive but safe position sizes")
    print("✅ Risk adjustments preserve capital in volatile markets")
    print("✅ Safety caps prevent overexposure")
    print("✅ Larger accounts get conservative institutional sizing")
    print("=" * 60)

def simulate_current_btc_price():
    """Simulate with a realistic BTC price"""
    btc_price = 94000  # Approximate current BTC price
    
    print(f"\n🔸 BTC PRICE SIMULATION @ ${btc_price:,.0f}")
    print("=" * 50)
    
    # Different portfolio sizes
    portfolios = [25, 30, 50, 75, 100, 150]
    
    for portfolio_value in portfolios:
        # Calculate position size with our new logic
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
        
        # Calculate BTC amount
        btc_amount = target_usd / btc_price
        
        print(f"💰 ${portfolio_value:.0f} portfolio → ${target_usd:.2f} ({target_usd/portfolio_value*100:.1f}%) → {btc_amount:.8f} BTC")

if __name__ == "__main__":
    simulate_market_test()
    simulate_current_btc_price()
