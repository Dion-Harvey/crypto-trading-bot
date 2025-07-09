#!/usr/bin/env python3
"""
Quick Bot Diagnostic Script
Tests all major bot components and provides status report
"""

import sys
import os
import datetime
from log_utils import log_message

def run_diagnostic():
    print("🔍 CRYPTO TRADING BOT DIAGNOSTIC")
    print("=" * 60)
    print(f"📅 Diagnostic Date: {datetime.datetime.now()}")
    print()
    
    log_message("🔧 DIAGNOSTIC: Starting comprehensive bot health check")
    
    # Test 1: Configuration
    try:
        from enhanced_config import get_bot_config
        config = get_bot_config()
        trading_config = config.config['trading']
        risk_config = config.config['risk_management']
        
        print("✅ Test 1: Configuration")
        print(f"   Trading Symbol: {trading_config['symbol']}")
        print(f"   Confidence Threshold: {config.config['strategy_parameters']['confidence_threshold']}")
        print(f"   Trade Cooldown: {trading_config['trade_cooldown_seconds']} seconds")
        print(f"   Position Mode: {trading_config.get('position_sizing_mode', 'N/A')}")
        
        log_message(f"🔧 DIAGNOSTIC: Config OK - Confidence threshold: {config.config['strategy_parameters']['confidence_threshold']}")
        
    except Exception as e:
        print(f"❌ Test 1: Configuration FAILED - {e}")
        log_message(f"🔧 DIAGNOSTIC: Config FAILED - {e}")
        return
    
    # Test 2: API Connection
    try:
        import ccxt
        from config import BINANCE_API_KEY, BINANCE_API_SECRET
        
        exchange = ccxt.binanceus({
            'apiKey': BINANCE_API_KEY,
            'secret': BINANCE_API_SECRET,
            'enableRateLimit': True,
            'options': {'timeDifference': 1000}
        })
        
        # Test connection
        ticker = exchange.fetch_ticker('BTC/USDC')
        balance = exchange.fetch_balance()
        
        print("✅ Test 2: API Connection")
        print(f"   Current BTC Price: ${ticker['last']:,.2f}")
        print(f"   Portfolio USDC: ${balance['USDC']['free']:.2f}")
        print(f"   Portfolio BTC: {balance['BTC']['free']:.6f} BTC")
        
        total_portfolio = balance['USDC']['free'] + (balance['BTC']['free'] * ticker['last'])
        print(f"   Total Portfolio: ${total_portfolio:.2f}")
        
        log_message(f"🔧 DIAGNOSTIC: API OK - Portfolio: ${total_portfolio:.2f}, BTC: ${ticker['last']:,.2f}")
        
    except Exception as e:
        print(f"❌ Test 2: API Connection FAILED - {e}")
        log_message(f"🔧 DIAGNOSTIC: API FAILED - {e}")
        return
    
    # Test 3: MA7/MA25 Strategy
    try:
        from strategies.ma_crossover import fetch_ohlcv
        
        df = fetch_ohlcv(exchange, 'BTC/USDC', '1h', 50)
        current_price = df['close'].iloc[-1]
        
        # Calculate MAs
        ma_7 = df['close'].rolling(7).mean()
        ma_25 = df['close'].rolling(25).mean()
        
        ma7_current = ma_7.iloc[-1]
        ma25_current = ma_25.iloc[-1]
        ma7_previous = ma_7.iloc[-2]
        ma25_previous = ma_25.iloc[-2]
        
        # Check crossovers
        golden_cross = (ma7_previous <= ma25_previous) and (ma7_current > ma25_current)
        death_cross = (ma7_previous >= ma25_previous) and (ma7_current < ma25_current)
        
        ma_spread = abs(ma7_current - ma25_current) / ma25_current * 100
        
        print("✅ Test 3: MA7/MA25 Strategy")
        print(f"   MA7: ${ma7_current:.2f}")
        print(f"   MA25: ${ma25_current:.2f}")
        print(f"   Spread: {ma_spread:.3f}%")
        print(f"   Golden Cross: {golden_cross}")
        print(f"   Death Cross: {death_cross}")
        print(f"   Trend: {'Bullish' if ma7_current > ma25_current else 'Bearish'}")
        
        # Test signal generation
        if golden_cross:
            signal_strength = "STRONG BUY"
        elif death_cross:
            signal_strength = "STRONG SELL"
        elif ma_spread > 1.0:
            signal_strength = "TREND CONTINUATION"
        else:
            signal_strength = "NO CLEAR SIGNAL"
        
        print(f"   Current Signal: {signal_strength}")
        
        log_message(f"🔧 DIAGNOSTIC: MA Strategy OK - Signal: {signal_strength}, Spread: {ma_spread:.3f}%")
        
    except Exception as e:
        print(f"❌ Test 3: MA7/MA25 Strategy FAILED - {e}")
        log_message(f"🔧 DIAGNOSTIC: MA Strategy FAILED - {e}")
        return
    
    # Test 4: State Manager
    try:
        from state_manager import get_state_manager
        state_mgr = get_state_manager()
        
        trading_state = state_mgr.get_trading_state()
        
        print("✅ Test 4: State Manager")
        print(f"   Holding Position: {trading_state['holding_position']}")
        print(f"   Last Trade Time: {trading_state['last_trade_time']}")
        print(f"   Consecutive Losses: {trading_state['consecutive_losses']}")
        
        # Check last trade timing
        if trading_state['last_trade_time']:
            import time
            time_since_last = time.time() - trading_state['last_trade_time']
            print(f"   Time Since Last Trade: {time_since_last/3600:.1f} hours")
            
            # Check cooldown
            cooldown_remaining = max(0, trading_config['trade_cooldown_seconds'] - time_since_last)
            if cooldown_remaining > 0:
                print(f"   ⏳ Trade Cooldown: {cooldown_remaining/60:.1f} minutes remaining")
            else:
                print(f"   ✅ Trade Cooldown: Ready to trade")
        
        log_message(f"🔧 DIAGNOSTIC: State Manager OK - Position: {trading_state['holding_position']}")
        
    except Exception as e:
        print(f"❌ Test 4: State Manager FAILED - {e}")
        log_message(f"🔧 DIAGNOSTIC: State Manager FAILED - {e}")
        return
    
    # Test 5: Check Trade History
    try:
        import csv
        if os.path.exists('trade_log.csv'):
            with open('trade_log.csv', 'r') as f:
                reader = csv.DictReader(f)
                trades = list(reader)
                
            print("✅ Test 5: Trade History")
            print(f"   Total Trades: {len(trades)}")
            
            if trades:
                last_trade = trades[-1]
                print(f"   Last Trade: {last_trade['action']} on {last_trade['timestamp']}")
                print(f"   Last Price: ${float(last_trade['price']):.2f}")
                
                # Calculate days since last trade
                from datetime import datetime
                last_date = datetime.fromisoformat(last_trade['timestamp'].replace('Z', '').split('+')[0])
                days_since = (datetime.now() - last_date).days
                print(f"   Days Since Last Trade: {days_since}")
                
                if days_since > 3:
                    print("   ⚠️ WARNING: No trades in over 3 days!")
            else:
                print("   ⚠️ No trades found in log")
        else:
            print("❌ Test 5: Trade History - No trade log file found")
            
        log_message(f"🔧 DIAGNOSTIC: Trade history checked")
        
    except Exception as e:
        print(f"❌ Test 5: Trade History FAILED - {e}")
        log_message(f"🔧 DIAGNOSTIC: Trade history FAILED - {e}")
    
    print()
    print("🔧 DIAGNOSTIC COMPLETE")
    print("=" * 60)
    print("📋 SUMMARY:")
    print("✅ All major components are functional")
    print("⚠️ Bot appears to be configured but may not be actively running")
    print("💡 Check if bot is running in a loop or scheduled process")
    print()
    
    log_message("🔧 DIAGNOSTIC: Complete - All components functional")

if __name__ == "__main__":
    run_diagnostic()
