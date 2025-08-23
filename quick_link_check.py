#!/usr/bin/env python3
"""
Quick LINK status verification script
"""

import ccxt
import json
from datetime import datetime

def quick_link_check():
    print(f"🔍 LINK STATUS CHECK - {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 40)
    
    try:
        # Load config
        with open('enhanced_config.json', 'r') as f:
            config = json.load(f)
        
        # Setup exchange  
        exchange_config = config['exchange']
        exchange = ccxt.binanceus({
            'apiKey': exchange_config['api_key'],
            'secret': exchange_config['secret'],
            'sandbox': exchange_config.get('testnet', False),
            'enableRateLimit': True
        })
        
        # Check balance
        balance = exchange.fetch_balance()
        link_total = balance['LINK']['total']
        link_free = balance['LINK']['free'] 
        link_used = balance['LINK']['used']
        
        # Get price
        ticker = exchange.fetch_ticker('LINK/USDT')
        price = ticker['last']
        value = link_total * price
        
        print(f"💰 LINK Balance:")
        print(f"   Total: {link_total:.8f} LINK")
        print(f"   Free:  {link_free:.8f} LINK")  
        print(f"   Used:  {link_used:.8f} LINK")
        print(f"   Price: ${price:.4f}")
        print(f"   Value: ${value:.2f}")
        
        if link_total <= 0.001:
            print("✅ CONFIRMED: LINK position is SOLD/CLOSED")
            print("🎉 Mission accomplished!")
        elif link_total >= 0.01:
            print(f"⚠️ WARNING: Significant LINK still held ({link_total:.6f})")
        else:
            print(f"💨 DUST: Small amount remaining ({link_total:.8f})")
            
    except Exception as e:
        print(f"❌ Check failed: {e}")

if __name__ == "__main__":
    quick_link_check()
