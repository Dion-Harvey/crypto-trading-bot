#!/usr/bin/env python3
import ccxt
import json

with open('enhanced_config.json', 'r') as f:
    config = json.load(f)

api_key = config['api_keys']['binance']['api_key']  
api_secret = config['api_keys']['binance']['api_secret']

exchange = ccxt.binanceus({
    'apiKey': api_key,
    'secret': api_secret, 
    'sandbox': False,
    'enableRateLimit': True
})

print('=== QUICK BALANCE CHECK ===')
balance = exchange.fetch_balance()
usdt_balance = balance.get('USDT', {}).get('total', 0)
fartcoin_balance = balance.get('FARTCOIN', {}).get('total', 0)

print(f'USDT: {usdt_balance:.2f}')
print(f'FARTCOIN: {fartcoin_balance:.6f}')

print('\n=== FARTCOIN PRICE ===')
try:
    ticker = exchange.fetch_ticker('FARTCOIN/USDT')
    current_price = ticker['last']
    change_24h = ticker['percentage']
    print(f'Current Price: ${current_price:.4f}')
    print(f'24h Change: {change_24h:.2f}%')
    
    if fartcoin_balance > 0:
        position_value = fartcoin_balance * current_price
        print(f'\n=== POSITION STATUS ===')
        print(f'FARTCOIN Holdings: {fartcoin_balance:.6f}')
        print(f'Position Value: ${position_value:.2f}')
        print(f'Entry Price: $1.02 (from logs)')
        pnl_percent = ((current_price - 1.02) / 1.02) * 100
        pnl_dollar = (current_price - 1.02) * fartcoin_balance
        print(f'P&L: {pnl_percent:+.2f}% (${pnl_dollar:+.2f})')
        
        if pnl_percent < -2:
            print('⚠️ WARNING: Position down more than 2%!')
            print('🚨 CRITICAL: No stop-loss protection in place!')
            
except Exception as e:
    print(f'Error getting price: {e}')
