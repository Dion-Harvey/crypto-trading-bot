#!/usr/bin/env python3

"""
Emergency script to place a stop-loss order for the existing QTUM position
"""

import ccxt
import json
import time
import sys
import os
from config import load_config

def place_emergency_qtum_stop_loss():
    """Place emergency stop-loss for QTUM position"""
    
    print("🚨 Emergency QTUM Stop-Loss Placement")
    print("=" * 40)
    
    try:
        # Load configuration
        config = load_config()
        
        # Initialize exchange
        exchange = ccxt.binanceus({
            'apiKey': config['api_key'],
            'secret': config['api_secret'],
            'sandbox': config.get('sandbox', False),
            'enableRateLimit': True,
        })
        
        symbol = 'QTUM/USDT'
        
        # Check current QTUM balance
        print(f"💰 Checking current QTUM balance...")
        balance = exchange.fetch_balance()
        qtum_balance = balance.get('QTUM', {}).get('free', 0)
        
        print(f"   QTUM Balance: {qtum_balance:.8f}")
        
        if qtum_balance < 0.0001:  # Less than minimum trade amount
            print(f"❌ No significant QTUM position found")
            print(f"   Current balance: {qtum_balance:.8f} QTUM")
            return
        
        # Get current price
        ticker = exchange.fetch_ticker(symbol)
        current_price = ticker['last']
        print(f"📊 Current QTUM Price: ${current_price:.4f}")
        
        # Calculate stop-loss price (0.8% below current price, same as bot)
        stop_percentage = 0.008  # 0.8% trailing stop
        stop_price = current_price * (1 - stop_percentage)
        stop_price = round(stop_price, 4)
        
        print(f"🛑 Calculated Stop Price: ${stop_price:.4f} (0.8% below current)")
        
        # Try STOP_LOSS first, then STOP_LOSS_LIMIT as fallback
        order = None
        order_type_used = None
        
        print(f"\n🎯 Attempting to place stop-loss order...")
        
        # Method 1: Try STOP_LOSS
        try:
            print(f"   Trying STOP_LOSS order type...")
            order = exchange.create_order(
                symbol,
                'STOP_LOSS',
                'sell',
                qtum_balance,
                None,
                {
                    'stopPrice': stop_price,
                    'timeInForce': 'GTC'
                }
            )
            
            if order:
                order_type_used = 'STOP_LOSS'
                print(f"   ✅ STOP_LOSS order placed successfully!")
        
        except Exception as e:
            error_msg = str(e).lower()
            if "is not a valid order type" in error_msg or "invalid order type" in error_msg:
                print(f"   ⚠️ STOP_LOSS not supported, trying STOP_LOSS_LIMIT...")
                
                # Method 2: Try STOP_LOSS_LIMIT
                try:
                    limit_price = stop_price * 0.999  # 0.1% below stop for execution
                    limit_price = round(limit_price, 4)
                    
                    print(f"   Trying STOP_LOSS_LIMIT order type...")
                    print(f"      Stop Price: ${stop_price:.4f}")
                    print(f"      Limit Price: ${limit_price:.4f}")
                    
                    order = exchange.create_order(
                        symbol,
                        'STOP_LOSS_LIMIT',
                        'sell',
                        qtum_balance,
                        limit_price,
                        {
                            'stopPrice': stop_price,
                            'timeInForce': 'GTC'
                        }
                    )
                    
                    if order:
                        order_type_used = 'STOP_LOSS_LIMIT'
                        print(f"   ✅ STOP_LOSS_LIMIT order placed successfully!")
                
                except Exception as limit_error:
                    print(f"   ❌ STOP_LOSS_LIMIT also failed: {limit_error}")
                    return
            
            else:
                print(f"   ❌ STOP_LOSS failed: {e}")
                return
        
        if order:
            print(f"\n✅ Emergency stop-loss order placed successfully!")
            print(f"   🆔 Order ID: {order['id']}")
            print(f"   💰 Amount: {qtum_balance:.8f} QTUM")
            print(f"   🛑 Stop Price: ${stop_price:.4f}")
            print(f"   📊 Order Type: {order_type_used}")
            print(f"   💡 Current Price: ${current_price:.4f}")
            
            if order_type_used == 'STOP_LOSS':
                print(f"   🎯 Will execute at MARKET PRICE when stop triggered")
            else:
                print(f"   ⚠️ Will execute at LIMIT PRICE ${limit_price:.4f} when stop triggered")
            
            # Calculate potential loss
            position_value = qtum_balance * current_price
            max_loss = position_value * stop_percentage
            print(f"\n💡 Position Protection Summary:")
            print(f"   📦 Position Size: {qtum_balance:.8f} QTUM (${position_value:.2f})")
            print(f"   🛡️ Maximum Loss: ${max_loss:.2f} (0.8%)")
            print(f"   🎯 Your position is now PROTECTED!")
            
            return order
        
        else:
            print(f"❌ Failed to place stop-loss order")
            print(f"💡 MANUAL ACTION REQUIRED:")
            print(f"   - Monitor your QTUM position manually")
            print(f"   - Consider placing a manual stop-loss at ${stop_price:.4f}")
            return None
            
    except Exception as e:
        print(f"❌ Emergency stop-loss placement failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    place_emergency_qtum_stop_loss()
