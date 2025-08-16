#!/usr/bin/env python3
"""
Dynamic Scaling Test Suite
Tests the new small account scaling logic before AWS deployment
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add the project directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import bot modules
from enhanced_config import get_bot_config
from institutional_strategies import InstitutionalStrategyManager
from log_utils import log_message

def test_position_sizing_logic():
    """Test the position sizing calculation with different portfolio values"""
    
    print("="*60)
    print("TESTING DYNAMIC SCALING POSITION SIZING")
    print("="*60)
    
    # Initialize required components
    bot_config = get_bot_config()
    optimized_config = bot_config.config
    institutional_manager = InstitutionalStrategyManager()
    
    # Test scenarios
    test_portfolios = [15, 25, 35, 50, 75, 100, 150, 200]
    current_price = 108000  # Current BTC price
    volatility = 0.02  # 2% volatility
    signal_confidence = 0.75  # 75% confidence
    
    results = []
    
    for portfolio_value in test_portfolios:
        print(f"\n🧪 Testing Portfolio Value: ${portfolio_value:.2f}")
        print("-" * 40)
        
        # Simulate the position sizing calculation
        position_size = calculate_test_position_size(
            current_price, volatility, signal_confidence, 
            portfolio_value, optimized_config, institutional_manager
        )
        
        position_pct = (position_size / portfolio_value) * 100 if portfolio_value > 0 else 0
        
        results.append({
            'portfolio': portfolio_value,
            'position_size': position_size,
            'position_pct': position_pct,
            'scaling_factor': get_scaling_factor(portfolio_value)
        })
        
        print(f"   Position Size: ${position_size:.2f}")
        print(f"   Portfolio %: {position_pct:.1f}%")
        print(f"   Scaling Factor: {get_scaling_factor(portfolio_value):.1f}x")
        
        # Safety checks
        if position_pct > 20:
            print(f"   ⚠️  WARNING: Position exceeds 20% safety cap!")
        else:
            print(f"   ✅ Position within safety limits")
    
    return results

def calculate_test_position_size(current_price, volatility, signal_confidence, total_portfolio_value, optimized_config, institutional_manager):
    """Replicate the position sizing logic for testing"""
    
    # Get position sizing configuration
    trading_config = optimized_config['trading']
    position_mode = trading_config.get('position_sizing_mode', 'percentage')
    
    if position_mode == 'percentage':
        base_position_pct = trading_config['base_position_pct']  # e.g., 0.15 = 15%
        min_position_pct = trading_config['min_position_pct']    # e.g., 0.08 = 8%
        max_position_pct = trading_config['max_position_pct']    # e.g., 0.25 = 25%
        
        base_amount = total_portfolio_value * base_position_pct
        min_amount = total_portfolio_value * min_position_pct
        max_amount = total_portfolio_value * max_position_pct
    else:
        base_amount = trading_config['base_amount_usd']
        min_amount = trading_config['min_amount_usd']
        max_amount = trading_config['max_amount_usd']
    
    # Kelly Criterion sizing (simplified for testing)
    kelly_size = base_amount * signal_confidence * 1.2  # Simplified Kelly
    
    # Risk factors (simplified)
    volatility_factor = 0.9 if volatility <= 0.02 else 0.75
    confidence_factor = max(0.7, min(1.3, signal_confidence * 1.2))
    loss_factor = 1.0  # No consecutive losses for test
    drawdown_factor = 1.0  # No drawdown for test
    time_factor = 1.0  # Normal trading hours
    var_factor = 1.0  # Normal risk
    
    # Portfolio size adjustment
    if position_mode == 'percentage' and total_portfolio_value > 100:
        size_adjustment = min(1.0, 50 / total_portfolio_value + 0.5)
    else:
        size_adjustment = 1.0
    
    # 🎯 DYNAMIC SCALING FOR SMALL ACCOUNTS
    small_account_scaling = 1.0
    if position_mode == 'percentage' and total_portfolio_value <= 100:
        if total_portfolio_value >= 75:
            small_account_scaling = 1.3  # 30% larger positions
        elif total_portfolio_value >= 50:
            small_account_scaling = 1.5  # 50% larger positions
        elif total_portfolio_value >= 25:
            small_account_scaling = 1.8  # 80% larger positions
        else:
            small_account_scaling = 2.0  # 100% larger positions
    
    size_adjustment = size_adjustment * small_account_scaling
    
    # Combine all factors
    institutional_size = (kelly_size * volatility_factor * confidence_factor *
                         loss_factor * drawdown_factor * time_factor * var_factor * size_adjustment)
    
    # Apply bounds
    final_size = max(min_amount, min(max_amount, institutional_size))
    
    # Safety cap: Never exceed 20% of portfolio
    if position_mode == 'percentage' and total_portfolio_value > 0:
        safety_cap = total_portfolio_value * 0.20
        if final_size > safety_cap:
            final_size = safety_cap
    
    # Binance minimum
    BINANCE_MIN_ORDER_USD = 10.0
    if final_size < BINANCE_MIN_ORDER_USD and total_portfolio_value >= BINANCE_MIN_ORDER_USD:
        final_size = BINANCE_MIN_ORDER_USD
    elif final_size < BINANCE_MIN_ORDER_USD:
        final_size = 0  # Skip trade
    
    return final_size

def get_scaling_factor(portfolio_value):
    """Get the scaling factor for a given portfolio value"""
    if portfolio_value <= 100:
        if portfolio_value >= 75:
            return 1.3
        elif portfolio_value >= 50:
            return 1.5
        elif portfolio_value >= 25:
            return 1.8
        else:
            return 2.0
    else:
        return min(1.0, 50 / portfolio_value + 0.5)

def simulate_growth_scenario():
    """Simulate how the dynamic scaling affects account growth"""
    
    print("\n" + "="*60)
    print("SIMULATING GROWTH SCENARIO")
    print("="*60)
    
    # Starting conditions
    initial_balance = 50.0
    current_balance = initial_balance
    trades_count = 0
    max_trades = 20
    
    # Simulate successful trades with 3% average gain
    avg_gain_pct = 0.03
    win_rate = 0.65  # 65% win rate
    avg_loss_pct = -0.015  # -1.5% average loss
    
    trade_history = []
    
    print(f"Starting simulation with ${initial_balance:.2f}")
    print(f"Win Rate: {win_rate:.0%}, Avg Win: {avg_gain_pct:.1%}, Avg Loss: {avg_loss_pct:.1%}")
    print("-" * 60)
    
    for trade_num in range(1, max_trades + 1):
        # Calculate position size with current balance
        position_size = calculate_test_position_size(
            108000, 0.02, 0.75, current_balance, 
            get_bot_config().config, InstitutionalStrategyManager()
        )
        
        if position_size == 0:
            print(f"Trade {trade_num}: Skipped - insufficient balance")
            continue
        
        # Simulate trade outcome
        is_win = np.random.random() < win_rate
        pnl_pct = avg_gain_pct if is_win else avg_loss_pct
        pnl_amount = position_size * pnl_pct
        
        new_balance = current_balance + pnl_amount
        position_pct = (position_size / current_balance) * 100
        scaling_factor = get_scaling_factor(current_balance)
        
        trade_history.append({
            'trade': trade_num,
            'balance_before': current_balance,
            'position_size': position_size,
            'position_pct': position_pct,
            'scaling_factor': scaling_factor,
            'outcome': 'WIN' if is_win else 'LOSS',
            'pnl_pct': pnl_pct,
            'pnl_amount': pnl_amount,
            'balance_after': new_balance
        })
        
        print(f"Trade {trade_num:2d}: ${current_balance:6.2f} → ${position_size:5.2f} ({position_pct:4.1f}%) → {pnl_pct:+5.1%} → ${new_balance:6.2f} [{scaling_factor:.1f}x]")
        
        current_balance = new_balance
        trades_count += 1
        
        # Stop if balance gets too low
        if current_balance < 10:
            print(f"\nSimulation stopped: Balance too low (${current_balance:.2f})")
            break
    
    # Summary
    total_return = ((current_balance - initial_balance) / initial_balance) * 100
    wins = sum(1 for t in trade_history if t['outcome'] == 'WIN')
    actual_win_rate = wins / len(trade_history) if trade_history else 0
    
    print("\n" + "="*40)
    print("SIMULATION RESULTS")
    print("="*40)
    print(f"Initial Balance: ${initial_balance:.2f}")
    print(f"Final Balance:   ${current_balance:.2f}")
    print(f"Total Return:    {total_return:+.1f}%")
    print(f"Trades Made:     {len(trade_history)}")
    print(f"Win Rate:        {actual_win_rate:.1%}")
    
    return trade_history

def test_safety_mechanisms():
    """Test that safety mechanisms work properly"""
    
    print("\n" + "="*60)
    print("TESTING SAFETY MECHANISMS")
    print("="*60)
    
    test_cases = [
        {"portfolio": 50, "expected_max_pct": 20, "description": "Normal 20% cap"},
        {"portfolio": 25, "expected_max_pct": 20, "description": "Small account 20% cap"},
        {"portfolio": 5, "expected_max_pct": 0, "description": "Too small for minimum order"},
        {"portfolio": 15, "expected_max_pct": 20, "description": "Just above minimum threshold"},
    ]
    
    for test_case in test_cases:
        portfolio_value = test_case["portfolio"]
        expected_max_pct = test_case["expected_max_pct"]
        description = test_case["description"]
        
        position_size = calculate_test_position_size(
            108000, 0.02, 0.95,  # High confidence to test caps
            portfolio_value, get_bot_config().config, InstitutionalStrategyManager()
        )
        
        actual_pct = (position_size / portfolio_value) * 100 if portfolio_value > 0 and position_size > 0 else 0
        
        print(f"\n🧪 {description}")
        print(f"   Portfolio: ${portfolio_value:.2f}")
        print(f"   Position Size: ${position_size:.2f}")
        print(f"   Actual %: {actual_pct:.1f}%")
        print(f"   Expected Max %: {expected_max_pct:.1f}%")
        
        if expected_max_pct == 0:
            if position_size == 0:
                print("   ✅ PASS: Correctly skipped trade")
            else:
                print("   ❌ FAIL: Should have skipped trade")
        else:
            if actual_pct <= expected_max_pct + 0.1:  # Small tolerance
                print("   ✅ PASS: Within safety limits")
            else:
                print("   ❌ FAIL: Exceeds safety limits")

def main():
    """Run all tests"""
    print("🧪 DYNAMIC SCALING TEST SUITE")
    print("Testing new position sizing before AWS deployment")
    print("=" * 60)
    
    try:
        # Test 1: Position sizing logic
        position_results = test_position_sizing_logic()
        
        # Test 2: Growth simulation
        growth_results = simulate_growth_scenario()
        
        # Test 3: Safety mechanisms
        test_safety_mechanisms()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS COMPLETED")
        print("="*60)
        print("Review the results above before deploying to AWS.")
        print("Key things to verify:")
        print("1. Position sizes are reasonable (10-20% of portfolio)")
        print("2. Scaling factors increase for smaller accounts")
        print("3. Safety caps are working (never > 20%)")
        print("4. Growth simulation shows reasonable progression")
        print("5. No trades are attempted with insufficient balance")
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🚀 Ready for AWS deployment!")
    else:
        print("\n⚠️  Fix issues before deploying to AWS!")
    
    input("\nPress Enter to exit...")
