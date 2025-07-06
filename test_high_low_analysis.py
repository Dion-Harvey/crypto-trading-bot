#!/usr/bin/env python3
"""
High/Low Price Analysis Test
Tests the new high/low analysis functions for profit maximization
"""

import sys
import os
import pandas as pd
import numpy as np

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

def create_test_data():
    """Create test OHLCV data with clear high/low patterns"""
    dates = pd.date_range(start='2025-01-01', periods=100, freq='1H')
    
    # Create realistic BTC price data with highs and lows
    base_price = 60000
    price_trend = np.linspace(0, 5000, 100)  # Upward trend
    volatility = np.random.normal(0, 500, 100)  # Random volatility
    
    # Add some clear support and resistance levels
    closes = base_price + price_trend + volatility
    
    # Create highs and lows with realistic spreads
    highs = closes + np.random.uniform(50, 300, 100)
    lows = closes - np.random.uniform(50, 300, 100)
    opens = closes + np.random.uniform(-100, 100, 100)
    volumes = np.random.uniform(1000, 5000, 100)
    
    # Add clear support at 62000 and resistance at 67000
    for i in range(len(closes)):
        if closes[i] < 62000:
            closes[i] = 62000 + np.random.uniform(0, 200)  # Bounce off support
        if closes[i] > 67000:
            closes[i] = 67000 - np.random.uniform(0, 200)  # Reject at resistance
    
    df = pd.DataFrame({
        'timestamp': dates,
        'open': opens,
        'high': highs,
        'low': lows,
        'close': closes,
        'volume': volumes
    })
    
    return df

def test_high_low_analysis():
    """Test the high/low analysis functions"""
    print("🧪 Testing High/Low Price Analysis Functions")
    print("=" * 50)
    
    # Create test data
    df = create_test_data()
    current_price = df['close'].iloc[-1]
    
    print(f"📊 Test Data Created: {len(df)} periods")
    print(f"💰 Current Price: ${current_price:.2f}")
    print(f"📈 Price Range: ${df['low'].min():.2f} - ${df['high'].max():.2f}")
    
    try:
        # Import the functions from bot.py
        from bot import analyze_high_low_opportunities, enhance_signal_with_high_low_analysis
        
        # Test high/low opportunities analysis
        print("\n🎯 Testing High/Low Opportunities Analysis...")
        opportunities = analyze_high_low_opportunities(df, current_price)
        
        print(f"✅ Analysis completed successfully!")
        print(f"📊 Price Position Analysis:")
        for period, pos_data in opportunities['price_position'].items():
            print(f"   {period}: {pos_data['position_pct']:.1f}% of range")
            print(f"      Range: ${pos_data['low']:.2f} - ${pos_data['high']:.2f}")
            print(f"      Near Low: {pos_data['near_low']}, Near High: {pos_data['near_high']}")
        
        print(f"\n🎯 Buy Opportunities Found: {len(opportunities['buy_opportunities'])}")
        for i, opp in enumerate(opportunities['buy_opportunities'][:3]):
            print(f"   {i+1}. {opp['type']}: {opp['reason']} (confidence: {opp['confidence']:.2f})")
        
        print(f"\n🎯 Sell Opportunities Found: {len(opportunities['sell_opportunities'])}")
        for i, opp in enumerate(opportunities['sell_opportunities'][:3]):
            print(f"   {i+1}. {opp['type']}: {opp['reason']} (confidence: {opp['confidence']:.2f})")
        
        print(f"\n🛡️ Support Levels Found: {len(opportunities['support_levels'])}")
        for i, support in enumerate(opportunities['support_levels'][:3]):
            print(f"   {i+1}. ${support['price']:.2f} (distance: {support['distance_pct']:.1f}%)")
        
        print(f"\n⚡ Resistance Levels Found: {len(opportunities['resistance_levels'])}")
        for i, resistance in enumerate(opportunities['resistance_levels'][:3]):
            print(f"   {i+1}. ${resistance['price']:.2f} (distance: {resistance['distance_pct']:.1f}%)")
        
        # Test signal enhancement
        print("\n🚀 Testing Signal Enhancement...")
        
        # Create a test BUY signal
        test_buy_signal = {
            'action': 'BUY',
            'confidence': 0.6,
            'reason': 'Test buy signal'
        }
        
        enhanced_buy_signal = enhance_signal_with_high_low_analysis(test_buy_signal, df, current_price)
        
        print(f"📈 BUY Signal Enhancement:")
        print(f"   Original Confidence: {test_buy_signal['confidence']:.3f}")
        print(f"   Enhanced Confidence: {enhanced_buy_signal.get('confidence', 0):.3f}")
        if 'high_low_boost' in enhanced_buy_signal:
            print(f"   High/Low Boost: +{enhanced_buy_signal['high_low_boost']:.3f}")
            print(f"   Boost Reasons: {enhanced_buy_signal.get('high_low_reasons', [])}")
        
        # Create a test SELL signal
        test_sell_signal = {
            'action': 'SELL',
            'confidence': 0.6,
            'reason': 'Test sell signal'
        }
        
        enhanced_sell_signal = enhance_signal_with_high_low_analysis(test_sell_signal, df, current_price)
        
        print(f"\n📉 SELL Signal Enhancement:")
        print(f"   Original Confidence: {test_sell_signal['confidence']:.3f}")
        print(f"   Enhanced Confidence: {enhanced_sell_signal.get('confidence', 0):.3f}")
        if 'high_low_boost' in enhanced_sell_signal:
            print(f"   High/Low Boost: +{enhanced_sell_signal['high_low_boost']:.3f}")
            print(f"   Boost Reasons: {enhanced_sell_signal.get('high_low_reasons', [])}")
        
        print(f"\n✅ HIGH/LOW ANALYSIS TEST COMPLETED SUCCESSFULLY!")
        print(f"🎯 The bot can now better identify optimal entry/exit points!")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("💡 Make sure bot.py contains the new high/low analysis functions")
        return False
    except Exception as e:
        print(f"❌ Test Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_high_low_analysis()
    if success:
        print("\n🚀 Ready to maximize profits with high/low price analysis!")
    else:
        print("\n⚠️ Tests failed - check the implementation")
