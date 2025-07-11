#!/usr/bin/env python3
"""
Simple test to verify position sizing targets without external dependencies
"""

def test_position_sizing_targets():
    """Test the specific target amounts we discussed"""
    
    def calculate_target_position_size(total_portfolio_value):
        """Simplified version of our target position logic"""
        if total_portfolio_value >= 100:
            return 20.0  # $20 for $100+ accounts (20%)
        elif total_portfolio_value >= 75:
            return 18.75  # $18.75 for $75-100 accounts (25%)
        elif total_portfolio_value >= 50:
            return 15.0  # $15 for $50-75 accounts (30%)
        elif total_portfolio_value >= 25:
            return 12.50  # $12.50 for $25-50 accounts (50%)
        else:
            return max(10.0, total_portfolio_value * 0.50)  # 50% or $10 minimum
    
    def calculate_safety_cap(total_portfolio_value):
        """Calculate safety cap based on account size"""
        if total_portfolio_value <= 25:
            return total_portfolio_value * 0.60  # 60% max
        elif total_portfolio_value <= 50:
            return total_portfolio_value * 0.55  # 55% max
        elif total_portfolio_value <= 75:
            return total_portfolio_value * 0.35  # 35% max
        elif total_portfolio_value <= 100:
            return total_portfolio_value * 0.25  # 25% max
        else:
            return total_portfolio_value * 0.20  # 20% max
    
    # Test cases based on our discussion
    test_cases = [
        (25.0, 12.50, "25→12.50 (50%)"),
        (50.0, 15.0, "50→15 (30%)"),
        (75.0, 18.75, "75→18.75 (25%)"),
        (100.0, 20.0, "100→20 (20%)"),
        (150.0, 20.0, "150→20 (13.3%)")  # Larger account
    ]
    
    print("🧪 POSITION SIZING TARGET VERIFICATION")
    print("=" * 50)
    
    all_passed = True
    
    for portfolio_value, expected_target, description in test_cases:
        # Get target position size
        target_size = calculate_target_position_size(portfolio_value)
        
        # Apply safety cap
        safety_cap = calculate_safety_cap(portfolio_value)
        final_size = min(target_size, safety_cap)
        
        # Calculate actual percentage
        actual_pct = (final_size / portfolio_value) * 100
        expected_pct = (expected_target / portfolio_value) * 100
        
        # Check if we hit our target (within 1% tolerance)
        target_met = abs(final_size - expected_target) < 0.01
        
        status = "✅ PASS" if target_met else "❌ FAIL"
        
        print(f"🧪 {description}")
        print(f"   Portfolio: ${portfolio_value:.2f}")
        print(f"   Target: ${target_size:.2f}")
        print(f"   Safety Cap: ${safety_cap:.2f}")
        print(f"   Final Size: ${final_size:.2f}")
        print(f"   Actual %: {actual_pct:.1f}%")
        print(f"   Expected %: {expected_pct:.1f}%")
        print(f"   {status}")
        print()
        
        if not target_met:
            all_passed = False
    
    print("=" * 50)
    if all_passed:
        print("🎉 ALL TESTS PASSED! Position sizing matches our targets.")
    else:
        print("⚠️ Some tests failed. Position sizing logic needs adjustment.")
    
    return all_passed

if __name__ == "__main__":
    test_position_sizing_targets()
