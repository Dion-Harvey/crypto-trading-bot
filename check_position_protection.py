#!/usr/bin/env python3
"""
🔍 POSITION & TRAILING STOP STATUS CHECK

Check current positions and their trailing stop protection status.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import ccxt
import time
from config import optimized_config
from state_manager import StateManager

def check_positions_and_trailing_stops():
    """Check current positions and their trailing stop protection"""
    
    print("="*70)
    print("🔍 POSITION & TRAILING STOP STATUS")
    print("="*70)
    
    try:
        # Initialize exchange
        exchange = ccxt.binanceus({
            'apiKey': optimized_config['binance_us']['api_key'],
            'secret': optimized_config['binance_us']['secret'],
            'sandbox': optimized_config['binance_us'].get('sandbox', False),
            'enableRateLimit': True,
        })
        
        print("✅ Connected to Binance US")
        
        # Get balance and positions
        balance = exchange.fetch_balance()
        
        print(f"\n💰 CURRENT POSITIONS:")
        positions = []
        for asset, info in balance.items():
            if asset not in ['USD', 'USDT', 'free', 'used', 'total', 'info'] and info['total'] > 0:
                if info['total'] > 0.001:  # Minimum threshold
                    symbol = f"{asset}/USDT"
                    try:
                        ticker = exchange.fetch_ticker(symbol)
                        current_price = ticker['last']
                        position_value = info['total'] * current_price
                        
                        positions.append({
                            'symbol': symbol,
                            'asset': asset,
                            'amount': info['total'],
                            'free': info['free'],
                            'used': info['used'],
                            'current_price': current_price,
                            'value_usd': position_value
                        })
                        
                        print(f"   📊 {symbol}: {info['total']:.6f} @ ${current_price:.6f} = ${position_value:.2f}")
                        print(f"      Free: {info['free']:.6f} | Used: {info['used']:.6f}")
                        
                    except Exception as e:
                        print(f"   ⚠️ {symbol}: {info['total']:.6f} (price fetch failed)")
        
        # Check for open orders (trailing stops)
        print(f"\n🛡️ ACTIVE PROTECTION ORDERS:")
        protection_found = False
        
        for pos in positions:
            try:
                open_orders = exchange.fetch_open_orders(pos['symbol'])
                if open_orders:
                    protection_found = True
                    for order in open_orders:
                        order_type = order.get('type', 'Unknown')
                        side = order.get('side', 'Unknown')
                        amount = order.get('amount', 0)
                        price = order.get('price') or order.get('stopPrice', 'N/A')
                        
                        print(f"   🔒 {pos['symbol']}: {order_type} {side}")
                        print(f"      Order ID: {order['id']}")
                        print(f"      Amount: {amount:.6f}")
                        print(f"      Price/Stop: ${price}")
                        print(f"      Status: {order.get('status', 'Unknown')}")
                else:
                    print(f"   ❌ {pos['symbol']}: NO PROTECTION ORDERS")
            except Exception as e:
                print(f"   ⚠️ {pos['symbol']}: Error checking orders - {e}")
        
        if not protection_found and positions:
            print(f"   ❌ NO ACTIVE PROTECTION FOUND FOR ANY POSITIONS")
        
        # Check bot state for trailing stop data
        print(f"\n🔄 BOT TRAILING STOP STATE:")
        try:
            state_manager = StateManager()
            current_state = state_manager.get_current_state()
            trailing_data = current_state.get('trading_state', {}).get('trailing_stop_data')
            
            if trailing_data and trailing_data.get('active'):
                print(f"   ✅ ACTIVE MANUAL TRAILING STOP:")
                print(f"      Symbol: {trailing_data['symbol']}")
                print(f"      Order ID: {trailing_data['order_id']}")
                print(f"      Amount: {trailing_data['amount']:.6f}")
                print(f"      Entry Price: ${trailing_data['entry_price']:.6f}")
                print(f"      Highest Price: ${trailing_data['highest_price']:.6f}")
                print(f"      Current Stop: ${trailing_data['current_stop_price']:.6f}")
                print(f"      Trail %: {trailing_data['trailing_percent']:.1%}")
                print(f"      Last Updated: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(trailing_data['last_updated']))}")
            else:
                print(f"   ❌ NO ACTIVE TRAILING STOP DATA IN BOT STATE")
                
        except Exception as e:
            print(f"   ⚠️ Error reading bot state: {e}")
        
        # Analysis based on your trade data
        print(f"\n📈 TRADE ANALYSIS:")
        print(f"   EGLD Position: 0.74 coins @ entry ~$15.05")
        print(f"   ENJ Position: 129.9 coins @ entry ~$0.0973")
        
        # Find matching positions
        for pos in positions:
            if pos['asset'] == 'EGLD':
                entry_price = 15.05
                current_pnl_pct = ((pos['current_price'] - entry_price) / entry_price) * 100
                expected_stop = entry_price * 0.995  # 0.5% below entry
                print(f"   📊 EGLD: Current ${pos['current_price']:.4f} vs Entry ${entry_price:.4f}")
                print(f"      P&L: {current_pnl_pct:+.2f}% | Expected Stop: ${expected_stop:.4f}")
                
            elif pos['asset'] == 'ENJ':
                entry_price = 0.0973
                current_pnl_pct = ((pos['current_price'] - entry_price) / entry_price) * 100
                expected_stop = entry_price * 0.995  # 0.5% below entry
                print(f"   📊 ENJ: Current ${pos['current_price']:.6f} vs Entry ${entry_price:.6f}")
                print(f"      P&L: {current_pnl_pct:+.2f}% | Expected Stop: ${expected_stop:.6f}")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        if not protection_found and positions:
            print(f"   🚨 URGENT: No trailing stops found - positions are UNPROTECTED")
            print(f"   🔄 Restart bot to activate manual trailing stop system")
            print(f"   📈 New system will automatically trail stops 0.50% behind rising prices")
        elif protection_found:
            print(f"   ✅ Positions have some protection orders")
            print(f"   🔄 Verify these are updating properly as prices rise")
            
    except Exception as e:
        print(f"❌ Error checking positions: {e}")

if __name__ == "__main__":
    check_positions_and_trailing_stops()
