#!/usr/bin/env python3
import ccxt
import json
from datetime import datetime

with open('enhanced_config.json', 'r') as f:
    config = json.load(f)

api_key = config['api_keys']['binance']['api_key']
api_secret = config['api_keys']['binance']['api_secret']

exchange = ccxt.binanceus({
    'apiKey': api_key, 
    'secret': api_secret, 
    'sandbox': False
})

balance = exchange.fetch_balance()
print('=== ACCOUNT BALANCE ===')
for currency, amount in balance['total'].items():
    if amount > 0:
        print(f'{currency}: {amount:.6f}')

print('\n=== RECENT FARTCOIN TRADES ===')
try:
    orders = exchange.fetch_orders('FARTCOIN/USDT', limit=10)
    for order in orders[-5:]:
        print(f'{order["datetime"]} - {order["side"].upper()} {order["amount"]} FARTCOIN at ${order["price"]} - Status: {order["status"]}')
except Exception as e:
    print(f'Error fetching FARTCOIN trades: {e}')

print('\n=== OPEN ORDERS ===')
try:
    open_orders = exchange.fetch_open_orders('FARTCOIN/USDT')
    if open_orders:
        for order in open_orders:
            print(f'{order["side"].upper()} {order["amount"]} FARTCOIN at ${order["price"]} - Type: {order["type"]} - Status: {order["status"]}')
    else:
        print('No open orders for FARTCOIN')
except Exception as e:
    print(f'Error fetching open orders: {e}')
