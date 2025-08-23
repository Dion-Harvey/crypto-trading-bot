#!/usr/bin/env python3

"""
Balance Investigation Script - Check LINK position discrepancy
"""

import ccxt
import json
import time
from config import load_config

def investigate_link_balance():
    """Investigate the LINK balance discrepancy"""
    
    print("🔍 LINK Balance Investigation")
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
        
        symbol = 'LINK/USDT'
        
        print(f"📊 Detailed Balance Analysis for LINK:")
        
        # Get comprehensive balance information
        balance = exchange.fetch_balance()
        
        if 'LINK' in balance:
            link_info = balance['LINK']
            print(f"   Total LINK: {link_info.get('total', 0):.8f}")
            print(f"   Free LINK: {link_info.get('free', 0):.8f}")
            print(f"   Used LINK: {link_info.get('used', 0):.8f}")
        else:
            print(f"   ❌ No LINK found in balance")
        
        # Get current LINK price
        try:
            ticker = exchange.fetch_ticker(symbol)
            current_price = ticker['last']
            print(f"\n💰 Current LINK Price: ${current_price:.4f}")
            
            if 'LINK' in balance:
                free_value = balance['LINK']['free'] * current_price
                total_value = balance['LINK']['total'] * current_price
                used_value = balance['LINK']['used'] * current_price
                
                print(f"   Free Value: ${free_value:.2f}")
                print(f"   Total Value: ${total_value:.2f}")
                print(f"   Used Value: ${used_value:.2f}")
        except Exception as e:
            print(f"   ⚠️ Could not get LINK price: {e}")
        
        # Check for open orders that might be tying up LINK
        print(f"\n📋 Checking Open Orders for {symbol}:")
        try:
            open_orders = exchange.fetch_open_orders(symbol)
            
            if open_orders:
                total_link_in_orders = 0
                for order in open_orders:
                    print(f"   🆔 Order {order['id'][:8]}...:")
                    print(f"      Type: {order['type']} {order['side']}")
                    print(f"      Amount: {order['amount']:.8f} LINK")
                    print(f"      Status: {order['status']}")
                    print(f"      Created: {order['datetime']}")
                    
                    if order['side'] == 'sell':
                        total_link_in_orders += order['amount']
                    
                    if 'stopPrice' in order.get('info', {}):
                        print(f"      Stop Price: ${float(order['info']['stopPrice']):.4f}")
                    if order.get('price'):
                        print(f"      Limit Price: ${order['price']:.4f}")
                    print()
                
                print(f"   📊 Total LINK in sell orders: {total_link_in_orders:.8f}")
                
                if 'LINK' in balance:
                    expected_free = balance['LINK']['total'] - total_link_in_orders
                    actual_free = balance['LINK']['free']
                    print(f"   🔍 Expected free LINK: {expected_free:.8f}")
                    print(f"   🔍 Actual free LINK: {actual_free:.8f}")
                    
                    if abs(expected_free - actual_free) > 0.00001:
                        print(f"   🚨 DISCREPANCY DETECTED!")
                        print(f"   💡 Difference: {abs(expected_free - actual_free):.8f} LINK")
            else:
                print(f"   ✅ No open orders found")
                
        except Exception as e:
            print(f"   ❌ Error checking open orders: {e}")
        
        # Check account status
        print(f"\n🔐 Account Information:")
        try:
            account = exchange.fetch_account_status()
            print(f"   Status: {account}")
        except Exception as e:
            print(f"   ⚠️ Could not get account status: {e}")
        
        # Check trading permissions for LINK/USDT
        print(f"\n🎯 Market Information for {symbol}:")
        try:
            markets = exchange.load_markets()
            if symbol in markets:
                market_info = markets[symbol]
                print(f"   Active: {market_info.get('active', 'Unknown')}")
                print(f"   Min Amount: {market_info.get('limits', {}).get('amount', {}).get('min', 'Unknown')}")
                print(f"   Min Cost: {market_info.get('limits', {}).get('cost', {}).get('min', 'Unknown')}")
                print(f"   Precision: {market_info.get('precision', {})}")
                
                # Check if we meet minimum requirements
                if 'LINK' in balance and balance['LINK']['free'] > 0:
                    free_link = balance['LINK']['free']
                    min_amount = market_info.get('limits', {}).get('amount', {}).get('min', 0)
                    
                    print(f"\n✅ Trading Requirements Check:")
                    print(f"   Available: {free_link:.8f} LINK")
                    print(f"   Minimum: {min_amount} LINK")
                    
                    if free_link >= min_amount:
                        print(f"   ✅ MEETS minimum amount requirement")
                    else:
                        print(f"   ❌ BELOW minimum amount requirement")
                        print(f"   📊 Need: {min_amount - free_link:.8f} more LINK")
        
        except Exception as e:
            print(f"   ❌ Error getting market info: {e}")
        
        print(f"\n📝 Summary:")
        if 'LINK' in balance:
            free_link = balance['LINK']['free']
            total_link = balance['LINK']['total']
            
            if free_link >= 0.01:  # Binance US minimum
                print(f"   ✅ You have {free_link:.8f} LINK available for trading")
                print(f"   💰 This should be sufficient for stop-loss orders")
            elif total_link >= 0.01:
                print(f"   ⚠️ You have {total_link:.8f} LINK total, but only {free_link:.8f} free")
                print(f"   💡 Some LINK may be tied up in open orders")
            else:
                print(f"   ❌ LINK position is below minimum trading amount (0.01 LINK)")
                print(f"   📊 Consider consolidating or manually managing this position")
        else:
            print(f"   ❌ No LINK position found")
            
    except Exception as e:
        print(f"❌ Investigation failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    investigate_link_balance()
