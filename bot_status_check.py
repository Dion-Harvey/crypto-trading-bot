#!/usr/bin/env python3
"""
Bot Status Diagnostic Tool
Checks current bot state, position, and signal conditions
"""

import ccxt
import pandas as pd
from config import BINANCE_API_KEY, BINANCE_API_SECRET
from enhanced_config import get_bot_config
from state_manager import get_state_manager
from strategies.ma_crossover import fetch_ohlcv

def check_bot_status():
    """Comprehensive bot status check"""
    
    print("="*60)
    print("🔍 BOT STATUS DIAGNOSTIC REPORT")
    print("="*60)
    
    # Initialize exchange
    exchange = ccxt.binanceus({
        'apiKey': BINANCE_API_KEY,
        'secret': BINANCE_API_SECRET,
        'enableRateLimit': True,
        'timeout': 30000,
        'options': {
            'timeDifference': 1000,
            'adjustForTimeDifference': True
        }
    })
    
    try:
        # 1. Check current balance and position
        print("\n📊 CURRENT BALANCE & POSITION:")
        balance = exchange.fetch_balance()
        ticker = exchange.fetch_ticker('BTC/USDC')
        current_price = ticker['last']
        
        btc_balance = balance['BTC']['free']
        usdc_balance = balance['USDC']['free']
        btc_value = btc_balance * current_price
        total_portfolio = usdc_balance + btc_value
        
        print(f"   BTC Balance: {btc_balance:.6f} BTC (${btc_value:.2f})")
        print(f"   USDC Balance: ${usdc_balance:.2f}")
        print(f"   Total Portfolio: ${total_portfolio:.2f}")
        print(f"   Current BTC Price: ${current_price:.2f}")
        
        # 2. Check bot state
        print("\n🤖 BOT STATE:")
        state_manager = get_state_manager()
        bot_config = get_bot_config()
        
        trading_state = state_manager.get_trading_state()
        holding_position = trading_state['holding_position']
        entry_price = trading_state.get('entry_price')
        
        print(f"   Holding Position: {holding_position}")
        print(f"   Entry Price: ${entry_price:.2f}" if entry_price else "   Entry Price: None")
        
        if btc_value > 1.0:
            print(f"   ✅ Bot should detect BTC position (${btc_value:.2f} > $1.00 threshold)")
            if entry_price:
                pnl_pct = (current_price - entry_price) / entry_price
                print(f"   Current P&L: {pnl_pct:+.2%}")
        else:
            print(f"   ⚠️ BTC position below detection threshold (${btc_value:.2f} <= $1.00)")
        
        # 3. Check configuration
        print("\n⚙️ CONFIGURATION:")
        config = bot_config.config
        confidence_threshold = config['strategy_parameters']['confidence_threshold']
        print(f"   Confidence Threshold: {confidence_threshold:.3f}")
        print(f"   Position Sizing Mode: {config['trading']['position_sizing_mode']}")
        print(f"   Stop Loss: {config['risk_management']['stop_loss_pct']:.1%}")
        print(f"   Take Profit: {config['risk_management']['take_profit_pct']:.1%}")
        
        # 4. Check recent market data and potential signals
        print("\n📈 MARKET CONDITIONS:")
        df = fetch_ohlcv(exchange, 'BTC/USDC', '1m', 50)
        
        # Calculate basic indicators
        if len(df) >= 14:
            # RSI
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            current_rsi = rsi.iloc[-1]
            
            # Moving averages
            ma_7 = df['close'].rolling(7).mean().iloc[-1]
            ma_25 = df['close'].rolling(25).mean().iloc[-1]
            
            # Recent price movement
            price_change_1h = (df['close'].iloc[-1] - df['close'].iloc[-60]) / df['close'].iloc[-60] if len(df) >= 60 else 0
            price_change_24h = (current_price - df['close'].iloc[0]) / df['close'].iloc[0]
            
            print(f"   RSI (14): {current_rsi:.1f}")
            print(f"   MA7: ${ma_7:.2f}")
            print(f"   MA25: ${ma_25:.2f}")
            print(f"   1H Change: {price_change_1h:+.2%}")
            print(f"   24H Change: {price_change_24h:+.2%}")
            
            # Market sentiment
            if current_rsi > 70:
                print("   📊 Market: Overbought (RSI > 70) - SELL signals more likely")
            elif current_rsi < 30:
                print("   📊 Market: Oversold (RSI < 30) - BUY signals more likely")
            else:
                print("   📊 Market: Neutral (RSI 30-70) - Mixed signals")
        
        # 5. Trading recommendations
        print("\n💡 ANALYSIS & RECOMMENDATIONS:")
        
        if btc_value > 1.0:
            print("   🎯 Bot is currently HOLDING BTC")
            print("   📤 Waiting for SELL signal or risk management trigger")
            print("   🔍 Monitor for:")
            print("      - Strong SELL signals with high confidence")
            print("      - Take profit triggers")
            print("      - Stop loss conditions")
            print("      - Trailing stop activation")
            
            if entry_price and entry_price > 0:
                pnl_pct = (current_price - entry_price) / entry_price
                if pnl_pct > 0.05:
                    print(f"   💰 Currently profitable ({pnl_pct:+.2%}) - consider partial profit taking")
                elif pnl_pct < -0.03:
                    print(f"   ⚠️ Currently at loss ({pnl_pct:+.2%}) - monitoring stop loss")
        else:
            print("   📥 Bot is ready for BUY signals")
            print("   🔍 Monitor for:")
            print("      - Strong BUY signals with high confidence")
            print("      - Oversold conditions (RSI < 30)")
            print("      - Support level bounces")
        
        # 6. Check if there are any obvious issues
        print("\n🔧 POTENTIAL ISSUES:")
        issues_found = False
        
        if confidence_threshold > 0.8:
            print(f"   ⚠️ Confidence threshold very high ({confidence_threshold:.3f}) - may filter out valid signals")
            issues_found = True
            
        if total_portfolio < 20:
            print(f"   ⚠️ Portfolio size small (${total_portfolio:.2f}) - limited position sizes")
            issues_found = True
        
        if not issues_found:
            print("   ✅ No obvious configuration issues detected")
        
        print(f"\n📝 SUMMARY:")
        print(f"   Status: {'HOLDING BTC' if btc_value > 1.0 else 'READY TO BUY'}")
        print(f"   Portfolio: ${total_portfolio:.2f}")
        print(f"   Next Action: {'Wait for SELL signal' if btc_value > 1.0 else 'Wait for BUY signal'}")
        
    except Exception as e:
        print(f"❌ Error during status check: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_bot_status()
