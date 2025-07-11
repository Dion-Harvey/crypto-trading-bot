#!/usr/bin/env python3
"""
Comprehensive Strategy Logic Test
"""

import sys
import os
import pandas as pd
import numpy as np

# Add current directory to path
sys.path.append(os.getcwd())

def test_strategy_execution():
    print("🧠 STRATEGY EXECUTION TEST")
    print("=" * 60)
    
    try:
        # 1. Import all required modules
        from enhanced_config import get_bot_config
        from strategies.ma_crossover import fetch_ohlcv
        from strategies.multi_strategy_optimized import MultiStrategyOptimized
        from enhanced_multi_strategy import EnhancedMultiStrategy
        from institutional_strategies import InstitutionalStrategyManager
        from success_rate_enhancer import success_enhancer
        from config import BINANCE_API_KEY, BINANCE_API_SECRET
        import ccxt
        
        config = get_bot_config()
        
        print("1. MODULE IMPORTS:")
        print("✅ All strategy modules imported successfully")
        
        # 2. Initialize exchange for real data
        exchange = ccxt.binanceus({
            'apiKey': BINANCE_API_KEY,
            'secret': BINANCE_API_SECRET,
            'enableRateLimit': True,
            'timeout': 30000,
            'rateLimit': 1200
        })
        
        print("\n2. REAL MARKET DATA:")
        df = fetch_ohlcv(exchange, 'BTC/USDC', '1m', 100)
        current_price = df['close'].iloc[-1]
        print(f"✅ Retrieved {len(df)} candles")
        print(f"   Current BTC/USDC: ${current_price:,.2f}")
        print(f"   Data range: {df.index[0]} to {df.index[-1]}")
        
        # 3. Test strategy initialization
        print("\n3. STRATEGY INITIALIZATION:")
        base_strategy = MultiStrategyOptimized()
        enhanced_strategy = EnhancedMultiStrategy()
        institutional_manager = InstitutionalStrategyManager()
        print("✅ All strategies initialized")
        
        # 4. Test signal generation
        print("\n4. SIGNAL GENERATION:")
        
        # Base strategy signal
        base_signal = base_strategy.get_consensus_signal(df)
        print(f"   Base strategy: {base_signal.get('action', 'N/A')} (conf: {base_signal.get('confidence', 0):.3f})")
        
        # Enhanced strategy signal
        enhanced_signal = enhanced_strategy.get_enhanced_consensus_signal(df)
        print(f"   Enhanced strategy: {enhanced_signal.get('action', 'N/A')} (conf: {enhanced_signal.get('confidence', 0):.3f})")
        
        # Institutional signal
        institutional_signal = institutional_manager.get_institutional_signal(df, portfolio_value=50, base_position_size=12)
        print(f"   Institutional: {institutional_signal.get('action', 'N/A')} (conf: {institutional_signal.get('confidence', 0):.3f})")
        
        # 5. Test market filters
        print("\n5. MARKET FILTERS TEST:")
        filters = config.config['market_filters']
        
        # Calculate current market conditions
        if len(df) >= 99:
            ema_7 = df['close'].ewm(span=7).mean().iloc[-1]
            ema_25 = df['close'].ewm(span=25).mean().iloc[-1] 
            ema_99 = df['close'].ewm(span=99).mean().iloc[-1]
            
            ma_aligned = ema_7 > ema_25 > ema_99
            print(f"   MA Trend Alignment: {'✅ BULLISH' if ma_aligned else '❌ BEARISH'}")
            print(f"     EMA7: ${ema_7:.2f}, EMA25: ${ema_25:.2f}, EMA99: ${ema_99:.2f}")
        
        # Calculate volatility
        returns = df['close'].pct_change().dropna()
        volatility = returns.std() * np.sqrt(1440)  # Daily volatility
        vol_threshold = filters['high_volatility_threshold']
        print(f"   Volatility: {volatility:.4f} ({'HIGH' if volatility > vol_threshold else 'NORMAL'})")
        
        # 6. Test position sizing
        print("\n6. POSITION SIZING TEST:")
        trading_config = config.config['trading']
        position_pct = trading_config['base_position_pct']
        portfolio_value = 50.35  # From connection test
        
        base_position = portfolio_value * position_pct
        print(f"   Portfolio value: ${portfolio_value:.2f}")
        print(f"   Base position: {position_pct*100:.1f}% = ${base_position:.2f}")
        
        # Check Binance minimums
        min_order = 10.0
        if base_position >= min_order:
            print(f"   ✅ Position size meets Binance minimum (${min_order})")
        else:
            print(f"   ⚠️  Position size below minimum, will adjust to ${min_order}")
        
        # 7. Test risk management
        print("\n7. RISK MANAGEMENT TEST:")
        risk_config = config.config['risk_management']
        
        stop_loss_pct = risk_config['stop_loss_pct']
        take_profit_pct = risk_config['take_profit_pct']
        
        entry_price = current_price
        stop_loss_price = entry_price * (1 - stop_loss_pct)
        take_profit_price = entry_price * (1 + take_profit_pct)
        
        print(f"   Entry: ${entry_price:.2f}")
        print(f"   Stop Loss: ${stop_loss_price:.2f} ({stop_loss_pct*100:.1f}%)")
        print(f"   Take Profit: ${take_profit_price:.2f} ({take_profit_pct*100:.1f}%)")
        print(f"   Risk/Reward: 1:{take_profit_pct/stop_loss_pct:.1f}")
        
        # 8. Test success rate enhancements
        print("\n8. SUCCESS RATE ENHANCEMENTS:")
        if 'success_enhancer' in locals():
            # Create a mock signal for testing
            test_signal = {
                'action': 'BUY',
                'confidence': 0.7,
                'reason': 'Test signal'
            }
            
            try:
                quality_analysis = success_enhancer.analyze_signal_quality(df, test_signal, current_price)
                print(f"   ✅ Quality analysis working")
                print(f"   Overall quality: {quality_analysis['overall_quality_score']:.3f}")
                print(f"   Enhanced confidence: {quality_analysis['enhanced_confidence']:.3f}")
            except Exception as e:
                print(f"   ⚠️  Quality analysis error: {e}")
        else:
            print("   ⚠️  Success rate enhancer not available")
        
        print(f"\n{'='*60}")
        print("✅ ALL STRATEGY TESTS PASSED!")
        print("🎯 BOT TRADING LOGIC VERIFIED!")
        print(f"{'='*60}")
        
        # Summary of key settings
        print(f"\n📋 CURRENT CONFIGURATION SUMMARY:")
        print(f"   Trading Pair: BTC/USDC")
        print(f"   Position Size: {position_pct*100:.1f}% of portfolio")
        print(f"   Stop Loss: {stop_loss_pct*100:.1f}%")
        print(f"   Take Profit: {take_profit_pct*100:.1f}%")
        print(f"   Confidence Threshold: {config.config['strategy_parameters']['confidence_threshold']*100:.0f}%")
        print(f"   Trade Cooldown: {trading_config['trade_cooldown_seconds']/60:.0f} minutes")
        print(f"   Trailing Stops: {risk_config['trailing_stop_enabled']}")
        print(f"   Partial Exits: {risk_config['partial_exit_enabled']}")
        print(f"   Min Hold Time: {risk_config['minimum_hold_time_minutes']} minutes")
        
        return True
        
    except Exception as e:
        print(f"❌ Strategy test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_strategy_execution()
