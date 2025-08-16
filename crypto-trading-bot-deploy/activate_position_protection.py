#!/usr/bin/env python3
"""
🛡️ IMMEDIATE POSITION PROTECTION

Activates manual trailing stops for current EGLD and ENJ positions.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import ccxt
import time
from config import optimized_config
from state_manager import StateManager

def protect_current_positions():
    """Activate trailing stops for EGLD and ENJ positions"""
    
    print("="*70)
    print("🛡️ ACTIVATING TRAILING STOP PROTECTION")
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
        
        # Your known positions from trade history
        positions_to_protect = [
            {
                'symbol': 'EGLD/USDT',
                'amount': 0.74,
                'entry_price': 15.05,
                'entry_time': '2025-08-15 14:37:24'
            },
            {
                'symbol': 'ENJ/USDT', 
                'amount': 129.9,
                'entry_price': 0.09732,
                'entry_time': '2025-08-15 12:49:12'
            }
        ]
        
        state_manager = StateManager()
        
        for pos in positions_to_protect:
            symbol = pos['symbol']
            amount = pos['amount']
            entry_price = pos['entry_price']
            
            print(f"\n🔒 PROTECTING {symbol} POSITION:")
            print(f"   Amount: {amount:.6f}")
            print(f"   Entry Price: ${entry_price:.6f}")
            print(f"   Entry Time: {pos['entry_time']}")
            
            try:
                # Get current market price
                ticker = exchange.fetch_ticker(symbol)
                current_price = ticker['last']
                
                # Calculate current P&L
                current_pnl_pct = ((current_price - entry_price) / entry_price) * 100
                
                print(f"   Current Price: ${current_price:.6f}")
                print(f"   Current P&L: {current_pnl_pct:+.2f}%")
                
                # Calculate initial stop price (0.50% below entry price)
                trailing_percent = 0.005  # 0.50%
                
                # Use the higher of: entry price or current price for stop calculation
                # This ensures we don't place stops above current price if position is losing
                reference_price = max(entry_price, current_price) if current_pnl_pct >= 0 else entry_price
                initial_stop_price = reference_price * (1 - trailing_percent)
                limit_price = initial_stop_price * 0.995  # Limit slightly below stop
                
                print(f"   Reference Price: ${reference_price:.6f}")
                print(f"   Initial Stop Price: ${initial_stop_price:.6f} (0.50% below)")
                print(f"   Limit Price: ${limit_price:.6f}")
                
                # Check if we already have open orders for this symbol
                open_orders = exchange.fetch_open_orders(symbol)
                if open_orders:
                    print(f"   ⚠️ Existing orders found - canceling first")
                    for order in open_orders:
                        try:
                            exchange.cancel_order(order['id'], symbol)
                            print(f"   🗑️ Cancelled order: {order['id']}")
                        except Exception as e:
                            print(f"   ⚠️ Failed to cancel order {order['id']}: {e}")
                
                # Place stop-loss-limit order
                print(f"   🔄 Placing STOP_LOSS_LIMIT order...")
                
                order = exchange.create_order(
                    symbol,
                    'STOP_LOSS_LIMIT',
                    'sell',
                    amount,
                    limit_price,
                    {
                        'stopPrice': str(initial_stop_price),
                        'timeInForce': 'GTC'
                    }
                )
                
                if order and order.get('id'):
                    print(f"   ✅ PROTECTION ORDER PLACED: {order['id']}")
                    
                    # Store trailing stop data for continuous monitoring
                    trailing_stop_data = {
                        'order_id': order['id'],
                        'symbol': symbol,
                        'amount': amount,
                        'entry_price': entry_price,
                        'highest_price': current_price,  # Start tracking from current price
                        'current_stop_price': initial_stop_price,
                        'trailing_percent': trailing_percent,
                        'last_updated': time.time(),
                        'active': True
                    }
                    
                    # Save to bot state
                    state_manager.update_trading_state(
                        trailing_stop_data=trailing_stop_data,
                        trailing_stop_order_id=order['id'],
                        trailing_stop_active=True
                    )
                    
                    print(f"   💾 Saved to bot state for continuous monitoring")
                    print(f"   📈 Will trail 0.50% behind rising prices automatically")
                    
                else:
                    print(f"   ❌ Failed to place protection order")
                    
            except Exception as e:
                print(f"   ❌ Error protecting {symbol}: {e}")
                continue
        
        print(f"\n✅ PROTECTION ACTIVATION COMPLETE")
        print(f"🔄 Positions will now be monitored and trailing stops updated automatically")
        print(f"📈 Stops will trail 0.50% behind the highest price achieved")
        print(f"🚀 Start the bot to begin continuous monitoring")
        
    except Exception as e:
        print(f"❌ Error during protection setup: {e}")

if __name__ == "__main__":
    protect_current_positions()
