#!/usr/bin/env python3
"""
Simple Bot Status Verification
"""

import ccxt
import json

def main():
    print("🔍 BOT STATUS VERIFICATION")
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
            'enableRateLimit': True,
            'options': {'defaultType': 'spot'}
        })
        
        # Check key balances
        balance = exchange.fetch_balance()
        
        # LINK Status
        link_balance = balance['LINK']['total']
        link_value = 0
        if link_balance > 0.001:
            ticker = exchange.fetch_ticker('LINK/USDT')
            link_value = link_balance * ticker['last']
        
        print(f"📊 LINK: {link_balance:.6f} LINK = ${link_value:.2f}")
        if link_balance <= 0.001:
            print("✅ LINK CONFIRMED SOLD")
        
        # QTUM Status 
        qtum_balance = balance['QTUM']['total']
        qtum_value = 0
        if qtum_balance > 0.001:
            ticker = exchange.fetch_ticker('QTUM/USDT')
            qtum_value = qtum_balance * ticker['last']
            
        print(f"📊 QTUM: {qtum_balance:.6f} QTUM = ${qtum_value:.2f}")
        if qtum_balance >= 0.01:
            print("🟢 QTUM POSITION ACTIVE")
        
        # USDT Available
        usdt_balance = balance['USDT']['free']
        print(f"💰 USDT: ${usdt_balance:.2f} available")
        
        # Total portfolio value
        total_value = link_value + qtum_value + usdt_balance
        print(f"📈 TOTAL: ${total_value:.2f}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
