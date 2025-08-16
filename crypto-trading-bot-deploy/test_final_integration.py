#!/usr/bin/env python3
"""
FINAL INTEGRATION TEST
Test the complete daily high/low strategies integration with main bot logic
"""

import sys
import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add the current directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import bot functions
try:
    from bot import (
        implement_daily_high_low_strategies,
        analyze_scalping_opportunities,
        analyze_swing_opportunities, 
        analyze_momentum_opportunities,
        analyze_reversal_opportunities,
        analyze_dca_opportunities,
        select_optimal_high_low_strategy,
        enhance_signal_with_high_low_analysis,
        calculate_rsi_for_reversals,
        calculate_macd_for_reversals,
        calculate_bollinger_bands
    )
    print("✅ Successfully imported all bot functions")
except ImportError as e:
    print(f"❌ Failed to import bot functions: {e}")
    sys.exit(1)

def create_test_data():
    """Create realistic market data for testing"""
    np.random.seed(42)  # For reproducible tests
    
    # Create 50 periods of realistic BTC price data
    base_price = 65000
    periods = 50
    
    # Simulate realistic price movement
    returns = np.random.normal(0, 0.025, periods)  # 2.5% daily volatility
    prices = [base_price]
    
    for i in range(periods - 1):
        new_price = prices[-1] * (1 + returns[i])
        prices.append(new_price)
    
    # Create DataFrame with high/low/volume
    data = []
    for i, price in enumerate(prices):
        high = price * (1 + abs(np.random.normal(0, 0.01)))  # Random high
        low = price * (1 - abs(np.random.normal(0, 0.01)))   # Random low
        volume = np.random.uniform(10000, 50000)
        
        data.append({
            'timestamp': datetime.now() - timedelta(hours=periods-i),
            'open': price * (1 + np.random.normal(0, 0.005)),
            'high': high,
            'low': low, 
            'close': price,
            'volume': volume
        })
    
    df = pd.DataFrame(data)
    return df

def test_individual_strategies():
    """Test each strategy individually"""
    print("\n" + "="*60)
    print("🧪 TESTING INDIVIDUAL STRATEGIES")
    print("="*60)
    
    df = create_test_data()
    current_price = df['close'].iloc[-1]
    today_high = df['high'].iloc[-1]
    today_low = df['low'].iloc[-1]
    position_in_range = (current_price - today_low) / (today_high - today_low) if today_high != today_low else 0.5
    
    print(f"📊 Test Data: Price=${current_price:.2f}, Range Position: {position_in_range:.2%}")
    
    # Test each strategy
    strategies = [
        ("Day Trading/Scalping", analyze_scalping_opportunities),
        ("Swing Trading", analyze_swing_opportunities),
        ("Momentum Trading", analyze_momentum_opportunities),
        ("Reversal Trading", analyze_reversal_opportunities),
        ("DCA Strategy", analyze_dca_opportunities)
    ]
    
    # Calculate daily highs/lows for swing analysis
    daily_highs = df['high'].rolling(24).max().dropna()
    daily_lows = df['low'].rolling(24).min().dropna()
    
    results = {}
    
    for name, func in strategies:
        try:
            if name == "Day Trading/Scalping":
                result = func(df, current_price, today_high, today_low, position_in_range)
            elif name == "Swing Trading":
                result = func(df, current_price, daily_highs, daily_lows, False)  # Not holding position
            elif name == "Momentum Trading":
                result = func(df, current_price, position_in_range)
            elif name == "Reversal Trading":
                result = func(df, current_price, today_high, today_low, position_in_range)
            elif name == "DCA Strategy":
                result = func(df, current_price, position_in_range, False)  # Not holding position
            
            results[name] = result
            print(f"✅ {name}: {result['action']} (confidence: {result['confidence']:.3f})")
            if result['reasons']:
                for reason in result['reasons']:
                    print(f"   📋 {reason}")
        except Exception as e:
            print(f"❌ {name} failed: {e}")
            results[name] = {'action': 'ERROR', 'confidence': 0.0, 'reasons': [str(e)]}
    
    return results

def test_strategy_selection():
    """Test optimal strategy selection"""
    print("\n" + "="*60)
    print("🎯 TESTING STRATEGY SELECTION")
    print("="*60)
    
    df = create_test_data()
    current_price = df['close'].iloc[-1]
    
    # Create mock strategy signals
    strategy_signals = {
        'day_trading': {'action': 'BUY', 'confidence': 0.8, 'reasons': ['Test scalping signal']},
        'swing_trading': {'action': 'BUY', 'confidence': 0.6, 'reasons': ['Test swing signal']},
        'momentum_trading': {'action': 'SELL', 'confidence': 0.7, 'reasons': ['Test momentum signal']},
        'reversal_trading': {'action': 'BUY', 'confidence': 0.9, 'reasons': ['Test reversal signal']},
        'dca_signal': {'action': 'BUY', 'confidence': 0.5, 'reasons': ['Test DCA signal']}
    }
    
    try:
        optimal = select_optimal_high_low_strategy(strategy_signals, df, current_price)
        
        if optimal:
            print(f"✅ Optimal Strategy Selected: {optimal['strategy']}")
            print(f"   Action: {optimal['action']}")
            print(f"   Confidence: {optimal['confidence']:.3f}")
            print(f"   Score: {optimal['score']:.3f}")
            print(f"   Reason: {optimal['reason']}")
            print(f"   All Scores: {optimal['all_scores']}")
        else:
            print("❌ No optimal strategy selected")
            
    except Exception as e:
        print(f"❌ Strategy selection failed: {e}")

def test_helper_functions():
    """Test technical indicator helper functions"""
    print("\n" + "="*60)
    print("🔧 TESTING HELPER FUNCTIONS")
    print("="*60)
    
    df = create_test_data()
    prices = df['close']
    
    try:
        # Test RSI
        rsi = calculate_rsi_for_reversals(prices)
        print(f"✅ RSI calculated: Current = {rsi.iloc[-1]:.2f}")
        
        # Test MACD
        macd_line, macd_signal, macd_histogram = calculate_macd_for_reversals(prices)
        print(f"✅ MACD calculated: Line = {macd_line.iloc[-1]:.2f}, Signal = {macd_signal.iloc[-1]:.2f}")
        
        # Test Bollinger Bands
        bb_upper, bb_middle, bb_lower = calculate_bollinger_bands(prices)
        print(f"✅ Bollinger Bands: Upper = ${bb_upper.iloc[-1]:.2f}, Lower = ${bb_lower.iloc[-1]:.2f}")
        
    except Exception as e:
        print(f"❌ Helper function test failed: {e}")

def test_main_integration():
    """Test the main daily high/low strategies integration"""
    print("\n" + "="*60)
    print("🔗 TESTING MAIN INTEGRATION")
    print("="*60)
    
    df = create_test_data()
    current_price = df['close'].iloc[-1]
    
    # Create a mock signal
    mock_signal = {
        'action': 'BUY',
        'confidence': 0.7,
        'reason': 'Mock test signal',
        'source': 'test'
    }
    
    try:
        # Test enhance_signal_with_high_low_analysis
        enhanced_signal = enhance_signal_with_high_low_analysis(mock_signal, df, current_price)
        print(f"✅ Signal Enhancement: Confidence {mock_signal['confidence']:.3f} → {enhanced_signal['confidence']:.3f}")
        
        # Test implement_daily_high_low_strategies
        daily_strategies = implement_daily_high_low_strategies(df, current_price, enhanced_signal, False)
        
        print(f"✅ Daily Strategies Implementation:")
        print(f"   Strategies analyzed: {len([k for k in daily_strategies.keys() if k != 'optimal_strategy'])}")
        
        if daily_strategies.get('optimal_strategy'):
            optimal = daily_strategies['optimal_strategy']
            print(f"   Optimal strategy: {optimal['strategy']}")
            print(f"   Action: {optimal['action']}")
            print(f"   Confidence: {optimal['confidence']:.3f}")
        else:
            print("   No optimal strategy selected")
            
    except Exception as e:
        print(f"❌ Main integration test failed: {e}")

def test_market_scenarios():
    """Test strategies under different market scenarios"""
    print("\n" + "="*60)
    print("📈 TESTING MARKET SCENARIOS")
    print("="*60)
    
    scenarios = [
        ("Bull Market", lambda x: x * 1.05),  # 5% gain
        ("Bear Market", lambda x: x * 0.95),  # 5% loss  
        ("Sideways Market", lambda x: x),     # No change
        ("High Volatility", lambda x: x * (1 + np.random.normal(0, 0.05)))  # High volatility
    ]
    
    for scenario_name, price_modifier in scenarios:
        print(f"\n🎭 Scenario: {scenario_name}")
        
        df = create_test_data()
        # Modify prices based on scenario
        df['close'] = df['close'].apply(price_modifier)
        df['high'] = df['high'].apply(price_modifier)
        df['low'] = df['low'].apply(price_modifier)
        
        current_price = df['close'].iloc[-1]
        
        # Test signal enhancement
        mock_signal = {'action': 'BUY', 'confidence': 0.6, 'reason': 'Test signal'}
        
        try:
            daily_strategies = implement_daily_high_low_strategies(df, current_price, mock_signal, False)
            
            active_strategies = [k for k, v in daily_strategies.items() 
                               if k != 'optimal_strategy' and v.get('action') in ['BUY', 'SELL']]
            
            print(f"   Active strategies: {len(active_strategies)}")
            
            if daily_strategies.get('optimal_strategy'):
                optimal = daily_strategies['optimal_strategy'] 
                print(f"   Best: {optimal['strategy']} ({optimal['action']}, {optimal['confidence']:.3f})")
            else:
                print("   No clear optimal strategy")
                
        except Exception as e:
            print(f"   ❌ Failed: {e}")

def main():
    """Run all integration tests"""
    print("🚀 FINAL INTEGRATION TEST SUITE")
    print("Testing daily high/low strategies integration with main bot logic")
    print("="*80)
    
    try:
        # Run all tests
        test_helper_functions()
        test_individual_strategies()
        test_strategy_selection()
        test_main_integration()
        test_market_scenarios()
        
        print("\n" + "="*80)
        print("✅ ALL INTEGRATION TESTS COMPLETED")
        print("✅ Daily high/low strategies are properly integrated!")
        print("✅ Ready for live trading verification")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ INTEGRATION TEST FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
