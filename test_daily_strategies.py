#!/usr/bin/env python3
"""
Daily High/Low Strategy Test
Tests the new comprehensive high/low profit maximization strategies
"""

import sys
import os
import pandas as pd
import numpy as np

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

def create_realistic_btc_data():
    """Create realistic BTC price data with clear daily patterns"""
    dates = pd.date_range(start='2025-01-01', periods=168, freq='h')  # 1 week of hourly data
    
    # Create realistic BTC price patterns
    base_price = 65000
    
    # Daily patterns (higher volatility during certain hours)
    daily_pattern = np.sin(np.arange(168) * 2 * np.pi / 24) * 500  # Daily cycle
    
    # Weekly trend
    weekly_trend = np.linspace(-2000, 3000, 168)  # Upward trend over the week
    
    # Random volatility with higher volatility during "trading hours"
    volatility = []
    for i in range(168):
        hour = i % 24
        if 8 <= hour <= 22:  # Higher volatility during "active hours"
            vol = np.random.normal(0, 800)
        else:  # Lower volatility during "quiet hours"
            vol = np.random.normal(0, 300)
        volatility.append(vol)
    
    closes = base_price + daily_pattern + weekly_trend + volatility
    
    # Create realistic OHLC from closes
    highs = []
    lows = []
    opens = []
    
    for i, close in enumerate(closes):
        if i == 0:
            open_price = close
        else:
            open_price = closes[i-1] + np.random.normal(0, 50)
        
        # High and low based on volatility
        hour = i % 24
        if 8 <= hour <= 22:  # Active hours - wider ranges
            high = close + np.random.uniform(100, 400)
            low = close - np.random.uniform(100, 400)
        else:  # Quiet hours - narrower ranges
            high = close + np.random.uniform(50, 150)
            low = close - np.random.uniform(50, 150)
        
        # Ensure high >= close >= low and high >= open >= low
        high = max(high, close, open_price)
        low = min(low, close, open_price)
        
        opens.append(open_price)
        highs.append(high)
        lows.append(low)
    
    volumes = np.random.uniform(1000, 5000, 168)
    
    df = pd.DataFrame({
        'timestamp': dates,
        'open': opens,
        'high': highs,
        'low': lows,
        'close': closes,
        'volume': volumes
    })
    
    return df

def test_daily_high_low_strategies():
    """Test all daily high/low profit maximization strategies"""
    print("🧪 Testing Daily High/Low Profit Maximization Strategies")
    print("=" * 60)
    
    # Create realistic test data
    df = create_realistic_btc_data()
    current_price = df['close'].iloc[-1]
    
    print(f"📊 Test Data: {len(df)} hours of BTC data")
    print(f"💰 Current Price: ${current_price:.2f}")
    print(f"📈 Price Range: ${df['low'].min():.2f} - ${df['high'].max():.2f}")
    print(f"📊 Daily Volatility: {df['close'].pct_change().std()*100:.2f}%")
    
    try:
        # Import the functions from bot.py
        from bot import (implement_daily_high_low_strategies, 
                        analyze_scalping_opportunities,
                        analyze_swing_opportunities,
                        analyze_momentum_opportunities, 
                        analyze_reversal_opportunities,
                        analyze_dca_opportunities)
        
        # Test the comprehensive strategy implementation
        print("\n🎯 Testing Comprehensive Daily Strategy Implementation...")
        
        # Test both holding and not holding positions
        for holding_position in [False, True]:
            print(f"\n📊 Testing with holding_position = {holding_position}")
            
            # Create a mock signal
            mock_signal = {
                'action': 'BUY' if not holding_position else 'SELL',
                'confidence': 0.6,
                'reason': 'Test signal'
            }
            
            # Test comprehensive strategy
            strategies = implement_daily_high_low_strategies(df, current_price, mock_signal, holding_position)
            
            print(f"✅ Daily Strategy Analysis completed!")
            
            # Show results for each strategy
            strategy_names = {
                'day_trading': '📈 Day Trading/Scalping',
                'swing_trading': '🔄 Swing Trading', 
                'momentum_trading': '🚀 Momentum Trading',
                'reversal_trading': '🔄 Reversal Trading',
                'dca_signal': '💰 Dollar-Cost Averaging'
            }
            
            for strategy_key, strategy_name in strategy_names.items():
                strategy_data = strategies[strategy_key]
                action = strategy_data['action']
                confidence = strategy_data['confidence']
                reasons = strategy_data['reasons']
                
                if confidence > 0.5:
                    print(f"   {strategy_name}: {action} (conf: {confidence:.2f})")
                    for reason in reasons[:2]:  # Top 2 reasons
                        print(f"      • {reason}")
                else:
                    print(f"   {strategy_name}: {action} (conf: {confidence:.2f}) - No strong signal")
            
            # Show optimal strategy selection
            optimal = strategies.get('optimal_strategy')
            if optimal:
                print(f"\n🎯 OPTIMAL STRATEGY SELECTED:")
                print(f"   Strategy: {optimal['strategy']}")
                print(f"   Action: {optimal['action']} (confidence: {optimal['confidence']:.2f})")
                print(f"   Score: {optimal['score']:.3f}")
                print(f"   Reason: {optimal['reason']}")
                
                if 'all_scores' in optimal:
                    print(f"   All Scores: {optimal['all_scores']}")
            else:
                print(f"\n⚠️ No optimal strategy selected (no high-confidence signals)")
        
        # Test individual strategy components
        print(f"\n🔍 Testing Individual Strategy Components...")
        
        # Calculate daily position for component tests
        daily_highs = df['high'].rolling(24).max().dropna()
        daily_lows = df['low'].rolling(24).min().dropna()
        
        if len(daily_highs) > 0 and len(daily_lows) > 0:
            today_high = daily_highs.iloc[-1]
            today_low = daily_lows.iloc[-1]
            daily_range = today_high - today_low
            position_in_range = (current_price - today_low) / daily_range if daily_range > 0 else 0.5
            
            print(f"📊 Daily Analysis: Range ${today_low:.2f} - ${today_high:.2f}")
            print(f"   Current Position: {position_in_range*100:.1f}% of daily range")
            
            # Test scalping
            scalping_result = analyze_scalping_opportunities(df, current_price, today_high, today_low, position_in_range)
            print(f"   📈 Scalping: {scalping_result['action']} ({scalping_result['confidence']:.2f})")
            
            # Test swing trading
            swing_result = analyze_swing_opportunities(df, current_price, daily_highs, daily_lows, False)
            print(f"   🔄 Swing: {swing_result['action']} ({swing_result['confidence']:.2f})")
            
            # Test momentum
            momentum_result = analyze_momentum_opportunities(df, current_price, position_in_range)
            print(f"   🚀 Momentum: {momentum_result['action']} ({momentum_result['confidence']:.2f})")
            
            # Test reversal
            reversal_result = analyze_reversal_opportunities(df, current_price, today_high, today_low, position_in_range)
            print(f"   🔄 Reversal: {reversal_result['action']} ({reversal_result['confidence']:.2f})")
            
            # Test DCA
            dca_result = analyze_dca_opportunities(df, current_price, position_in_range, False)
            print(f"   💰 DCA: {dca_result['action']} ({dca_result['confidence']:.2f})")
        
        print(f"\n✅ ALL DAILY HIGH/LOW STRATEGY TESTS COMPLETED SUCCESSFULLY!")
        print(f"🎯 Your bot can now implement 6 different profit maximization strategies!")
        print(f"💡 Each strategy targets different market conditions and timeframes")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("💡 Make sure bot.py contains the new daily high/low strategy functions")
        return False
    except Exception as e:
        print(f"❌ Test Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_daily_high_low_strategies()
    if success:
        print("\n🚀 Ready to maximize profits with comprehensive daily high/low strategies!")
        print("\n📋 STRATEGIES IMPLEMENTED:")
        print("   1. 📈 Day Trading/Scalping - Quick profits from minor moves")
        print("   2. 🔄 Swing Trading - Multi-day price swings")
        print("   3. 🚀 Momentum Trading - Ride strong trends")
        print("   4. 🔄 Reversal Trading - Capitalize on trend changes")
        print("   5. 💰 Dollar-Cost Averaging - Systematic accumulation")
        print("   6. 🎯 Optimal Strategy Selection - AI chooses best approach")
    else:
        print("\n⚠️ Tests failed - check the implementation")
