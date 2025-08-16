#!/usr/bin/env python3
"""
Market Diagnostic Tool
Analyzes why the bot missed BTC movement and provides optimization recommendations
"""
import ccxt
import pandas as pd
import json
from datetime import datetime, timedelta
import sys
import os

def load_config():
    """Load the bot configuration"""
    try:
        with open('enhanced_config.json', 'r') as f:
            return json.load(f)
    except:
        return None

def analyze_recent_market_movement():
    """Analyze BTC movement in the last 24 hours"""
    print("🔍 ANALYZING RECENT BTC/USDC MARKET MOVEMENT")
    print("=" * 60)
    
    try:
        exchange = ccxt.binanceus({'sandbox': False, 'enableRateLimit': True})
        
        # Get 24h ticker data
        ticker = exchange.fetch_ticker('BTC/USDC')
        print(f"📊 Current Price: ${ticker['last']:.2f}")
        print(f"📊 24h Change: {ticker['percentage']:+.2f}%")
        print(f"📊 24h High: ${ticker['high']:.2f}")
        print(f"📊 24h Low: ${ticker['low']:.2f}")
        print(f"📊 24h Range: {((ticker['high'] - ticker['low']) / ticker['low'] * 100):.2f}%")
        
        # Get hourly data for detailed analysis
        ohlcv = exchange.fetch_ohlcv('BTC/USDC', '1h', limit=24)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
        df['hourly_change'] = (df['close'] - df['open']) / df['open'] * 100
        df['hourly_range'] = (df['high'] - df['low']) / df['low'] * 100
        
        # Find significant movements
        significant_moves = df[
            (abs(df['hourly_change']) > 1.0) | (df['hourly_range'] > 2.0)
        ].copy()
        
        if len(significant_moves) > 0:
            print(f"\n🎯 SIGNIFICANT MOVEMENTS (Last 24h):")
            for _, row in significant_moves.iterrows():
                direction = "🟢 UP" if row['hourly_change'] > 0 else "🔴 DOWN"
                timestamp = row['datetime'].strftime('%m-%d %H:%M UTC')
                print(f"   {timestamp}: {direction} {row['hourly_change']:+.2f}% | Range: {row['hourly_range']:.2f}% | ${row['open']:.0f}→${row['close']:.0f}")
            
            # Calculate total movement in last 3 hours
            last_3h = df.tail(3)
            total_3h_change = (last_3h['close'].iloc[-1] - last_3h['open'].iloc[0]) / last_3h['open'].iloc[0] * 100
            max_3h_high = last_3h['high'].max()
            min_3h_low = last_3h['low'].min()
            range_3h = (max_3h_high - min_3h_low) / min_3h_low * 100
            
            print(f"\n📈 LAST 3 HOURS SUMMARY:")
            print(f"   Total Change: {total_3h_change:+.2f}%")
            print(f"   Price Range: ${min_3h_low:.2f} - ${max_3h_high:.2f} ({range_3h:.2f}% range)")
            
            return {
                'has_movement': True,
                'significant_moves': len(significant_moves),
                'last_3h_change': total_3h_change,
                'last_3h_range': range_3h,
                'current_price': ticker['last']
            }
        else:
            print(f"\nℹ️  No major movements detected (>1% hourly change)")
            return {
                'has_movement': False,
                'current_price': ticker['last']
            }
            
    except Exception as e:
        print(f"❌ Error analyzing market: {e}")
        return None

def test_ma_signals():
    """Test current MA signals across timeframes"""
    print(f"\n🎯 TESTING MULTI-TIMEFRAME MA SIGNALS")
    print("=" * 50)
    
    try:
        exchange = ccxt.binanceus({'sandbox': False, 'enableRateLimit': True})
        current_price = exchange.fetch_ticker('BTC/USDC')['last']
        
        timeframes = ['1m', '5m', '15m', '30m', '1h', '2h']
        
        for tf in timeframes:
            try:
                ohlcv = exchange.fetch_ohlcv('BTC/USDC', tf, limit=50)
                df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                
                if len(df) >= 25:
                    ma7 = df['close'].rolling(7).mean().iloc[-1]
                    ma25 = df['close'].rolling(25).mean().iloc[-1]
                    ma7_prev = df['close'].rolling(7).mean().iloc[-2]
                    ma25_prev = df['close'].rolling(25).mean().iloc[-2]
                    
                    spread = abs(ma7 - ma25) / ma25 * 100
                    direction = "🟢 BULLISH" if ma7 > ma25 else "🔴 BEARISH"
                    
                    # Check for crossovers
                    golden_cross = (ma7_prev <= ma25_prev) and (ma7 > ma25)
                    death_cross = (ma7_prev >= ma25_prev) and (ma7 < ma25)
                    
                    crossover = ""
                    if golden_cross:
                        crossover = " 🚀 GOLDEN CROSS!"
                    elif death_cross:
                        crossover = " 💥 DEATH CROSS!"
                    
                    print(f"   {tf:>3}: {direction} | Spread: {spread:.3f}% | MA7: {ma7:.2f} | MA25: {ma25:.2f}{crossover}")
                else:
                    print(f"   {tf:>3}: Insufficient data")
            except Exception as e:
                print(f"   {tf:>3}: Error - {e}")
        
        return current_price
        
    except Exception as e:
        print(f"❌ Error testing MA signals: {e}")
        return None

def check_bot_sensitivity():
    """Check current bot sensitivity settings"""
    print(f"\n⚙️  CURRENT BOT SENSITIVITY ANALYSIS")
    print("=" * 50)
    
    config = load_config()
    if not config:
        print("❌ Could not load bot configuration")
        return
    
    strategy_params = config.get('strategy_parameters', {})
    trading_params = config.get('trading', {})
    
    print(f"📊 Current Settings:")
    print(f"   Confidence Threshold: {strategy_params.get('confidence_threshold', 'N/A'):.3f}")
    print(f"   Base Position %: {trading_params.get('base_position_pct', 'N/A'):.1%}")
    print(f"   Trade Cooldown: {trading_params.get('trade_cooldown_seconds', 'N/A')}s")
    print(f"   Min Hold Time: {config.get('risk_management', {}).get('minimum_hold_time_minutes', 'N/A')} min")
    
    # Sensitivity analysis
    current_threshold = strategy_params.get('confidence_threshold', 0.55)
    
    print(f"\n🎯 SENSITIVITY RECOMMENDATIONS:")
    if current_threshold > 0.5:
        print(f"   🔧 Current threshold ({current_threshold:.3f}) may be too conservative")
        print(f"   💡 Suggest lowering to 0.45-0.50 for more signals")
    
    if trading_params.get('trade_cooldown_seconds', 180) > 120:
        print(f"   ⏰ Trade cooldown may be too long for volatile markets")
        print(f"   💡 Suggest reducing to 60-120s during high volatility")
    
    return config

def generate_optimization_recommendations(market_analysis, current_price, config):
    """Generate specific optimization recommendations"""
    print(f"\n🎯 OPTIMIZATION RECOMMENDATIONS")
    print("=" * 50)
    
    if not market_analysis or not config:
        print("❌ Insufficient data for recommendations")
        return
    
    recommendations = []
    
    # 1. Movement-based recommendations
    if market_analysis.get('has_movement'):
        print(f"✅ MARKET ACTIVITY DETECTED:")
        print(f"   - {market_analysis['significant_moves']} significant hourly moves")
        print(f"   - Last 3h change: {market_analysis.get('last_3h_change', 0):+.2f}%")
        
        if abs(market_analysis.get('last_3h_change', 0)) > 2.0:
            recommendations.append("LOWER_CONFIDENCE_THRESHOLD")
            recommendations.append("REDUCE_COOLDOWN")
            print(f"   💡 High volatility detected - bot should be more aggressive")
    
    # 2. Configuration-based recommendations
    current_threshold = config.get('strategy_parameters', {}).get('confidence_threshold', 0.55)
    if current_threshold > 0.50:
        recommendations.append("LOWER_CONFIDENCE_THRESHOLD")
    
    # 3. Generate specific changes
    print(f"\n📝 SPECIFIC OPTIMIZATIONS TO IMPLEMENT:")
    
    if "LOWER_CONFIDENCE_THRESHOLD" in recommendations:
        new_threshold = max(0.35, current_threshold - 0.10)
        print(f"   1. Lower confidence threshold: {current_threshold:.3f} → {new_threshold:.3f}")
    
    if "REDUCE_COOLDOWN" in recommendations:
        current_cooldown = config.get('trading', {}).get('trade_cooldown_seconds', 180)
        new_cooldown = max(60, current_cooldown - 60)
        print(f"   2. Reduce trade cooldown: {current_cooldown}s → {new_cooldown}s")
    
    # 4. Immediate action items
    print(f"\n🚀 IMMEDIATE ACTIONS:")
    print(f"   ✅ Bot is now running and monitoring every 30s")
    print(f"   🔧 Consider temporary sensitivity boost for current volatility")
    print(f"   📊 Monitor next 2-3 hours for signal generation")
    
    return recommendations

def main():
    """Main diagnostic function"""
    print("🤖 CRYPTO TRADING BOT - MARKET DIAGNOSTIC TOOL")
    print("=" * 60)
    print(f"🕐 Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. Analyze recent market movement
    market_analysis = analyze_recent_market_movement()
    
    # 2. Test current MA signals
    current_price = test_ma_signals()
    
    # 3. Check bot sensitivity
    config = check_bot_sensitivity()
    
    # 4. Generate recommendations
    recommendations = generate_optimization_recommendations(market_analysis, current_price, config)
    
    print(f"\n✅ DIAGNOSTIC COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()
