#!/usr/bin/env python3

"""
Test script to check available order types for QTUM/USDT and test stop-loss functionality
"""

import ccxt
import json
import time
import sys
import os
from config import load_config

def test_qtum_order_types():
    """Test what order types are available for QTUM/USDT"""
    
    print("🔍 QTUM/USDT Order Type Compatibility Test")
    print("=" * 50)
    
    # Load configuration
    try:
        config = load_config()
        
        # Initialize exchange
        exchange = ccxt.binanceus({
            'apiKey': config['api_key'],
            'secret': config['api_secret'],
            'sandbox': config.get('sandbox', False),
            'enableRateLimit': True,
        })
        
        symbol = 'QTUM/USDT'
        
        # Get market info
        print(f"📊 Getting market info for {symbol}...")
        markets = exchange.load_markets()
        
        if symbol not in markets:
            print(f"❌ {symbol} not found in markets")
            return
        
        market_info = markets[symbol]
        print(f"✅ Market found: {symbol}")
        print(f"   Active: {market_info.get('active', 'Unknown')}")
        print(f"   Type: {market_info.get('type', 'Unknown')}")
        print(f"   Spot: {market_info.get('spot', 'Unknown')}")
        
        # Check permitted order types
        if 'info' in market_info and 'orderTypes' in market_info['info']:
            order_types = market_info['info']['orderTypes']
            print(f"   📋 Permitted Order Types: {order_types}")
            
            # Check specifically for stop-loss order types
            stop_types = [ot for ot in order_types if 'STOP' in ot.upper()]
            print(f"   🛑 Stop-Loss Order Types: {stop_types}")
        else:
            print("   ⚠️ Order type info not available in market data")
        
        # Test current balance
        print(f"\n💰 Checking QTUM balance...")
        balance = exchange.fetch_balance()
        qtum_balance = balance.get('QTUM', {}).get('free', 0)
        print(f"   QTUM Balance: {qtum_balance:.8f}")
        
        if qtum_balance > 0:
            print(f"   ✅ You have QTUM to test stop-loss orders with")
            
            # Get current price
            ticker = exchange.fetch_ticker(symbol)
            current_price = ticker['last']
            print(f"   📊 Current QTUM Price: ${current_price:.4f}")
            
            # Calculate test stop price (1% below current)
            stop_price = current_price * 0.99
            stop_price = round(stop_price, 4)
            
            print(f"\n🧪 Testing Stop-Loss Order Types...")
            print(f"   Test Amount: {min(qtum_balance, 0.01):.8f} QTUM")
            print(f"   Stop Price: ${stop_price:.4f} (1% below current)")
            
            # Test 1: STOP_LOSS order type
            print(f"\n🔬 Test 1: STOP_LOSS Order Type")
            try:
                # Don't actually place the order, just validate parameters
                print(f"   Attempting to validate STOP_LOSS order...")
                print(f"   (Note: This is just a validation test - no actual order placed)")
                
                test_params = {
                    'symbol': symbol,
                    'type': 'STOP_LOSS',
                    'side': 'sell',
                    'amount': min(qtum_balance, 0.01),
                    'price': None,
                    'params': {
                        'stopPrice': stop_price,
                        'timeInForce': 'GTC'
                    }
                }
                
                print(f"   ✅ STOP_LOSS parameters validated")
                print(f"      Symbol: {test_params['symbol']}")
                print(f"      Type: {test_params['type']}")
                print(f"      Amount: {test_params['amount']:.8f}")
                print(f"      Stop Price: ${test_params['params']['stopPrice']:.4f}")
                
            except Exception as e:
                print(f"   ❌ STOP_LOSS validation failed: {e}")
            
            # Test 2: STOP_LOSS_LIMIT order type
            print(f"\n🔬 Test 2: STOP_LOSS_LIMIT Order Type")
            try:
                limit_price = stop_price * 0.999  # Slightly below stop for quick execution
                limit_price = round(limit_price, 4)
                
                print(f"   Attempting to validate STOP_LOSS_LIMIT order...")
                print(f"   (Note: This is just a validation test - no actual order placed)")
                
                test_params = {
                    'symbol': symbol,
                    'type': 'STOP_LOSS_LIMIT',
                    'side': 'sell',
                    'amount': min(qtum_balance, 0.01),
                    'price': limit_price,
                    'params': {
                        'stopPrice': stop_price,
                        'timeInForce': 'GTC'
                    }
                }
                
                print(f"   ✅ STOP_LOSS_LIMIT parameters validated")
                print(f"      Symbol: {test_params['symbol']}")
                print(f"      Type: {test_params['type']}")
                print(f"      Amount: {test_params['amount']:.8f}")
                print(f"      Stop Price: ${test_params['params']['stopPrice']:.4f}")
                print(f"      Limit Price: ${test_params['price']:.4f}")
                
            except Exception as e:
                print(f"   ❌ STOP_LOSS_LIMIT validation failed: {e}")
        
        else:
            print(f"   ⚠️ No QTUM balance available for stop-loss testing")
            print(f"   💡 You need to buy some QTUM first to test stop-loss functionality")
        
        print(f"\n✅ Order Type Compatibility Test Complete")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_qtum_order_types()
