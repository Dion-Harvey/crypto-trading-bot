#!/usr/bin/env python3
"""
EMERGENCY FARTCOIN POSITION MANAGER
Use this script to either:
1. Place a manual stop-loss 
2. Sell the FARTCOIN position
3. Check current status
"""

import ccxt
import json

def main():
    with open('enhanced_config.json', 'r') as f:
        config = json.load(f)
    
    exchange = ccxt.binanceus({
        'apiKey': config['api_keys']['binance']['api_key'],
        'secret': config['api_keys']['binance']['api_secret'], 
        'sandbox': False,
        'enableRateLimit': True
    })
    
    print("🚨 FARTCOIN EMERGENCY MANAGER 🚨\n")
    
    try:
        # Get current position
        balance = exchange.fetch_balance()
        fartcoin_qty = balance.get('FARTCOIN', {}).get('total', 0)
        usdt_balance = balance.get('USDT', {}).get('total', 0)
        
        if fartcoin_qty == 0:
            print("✅ No FARTCOIN position found - you're safe!")
            return
            
        # Get current price
        ticker = exchange.fetch_ticker('FARTCOIN/USDT')
        current_price = ticker['last']
        
        print(f"📊 CURRENT POSITION:")
        print(f"   FARTCOIN: {fartcoin_qty:.6f}")
        print(f"   Current Price: ${current_price:.4f}")
        print(f"   Entry Price: $1.02 (from logs)")
        
        position_value = fartcoin_qty * current_price
        pnl_percent = ((current_price - 1.02) / 1.02) * 100
        pnl_dollar = (current_price - 1.02) * fartcoin_qty
        
        print(f"   Position Value: ${position_value:.2f}")
        print(f"   P&L: {pnl_percent:+.2f}% (${pnl_dollar:+.2f})")
        print(f"   USDT Balance: ${usdt_balance:.2f}")
        
        if pnl_percent > 10:
            print("\n🎉 GREAT NEWS: Position is up 10%+ - consider taking profit!")
        elif pnl_percent < -5:
            print("\n⚠️ WARNING: Position down 5%+ - consider cutting losses!")
        
        print(f"\n🛠️ RECOMMENDED ACTIONS:")
        print(f"1. EMERGENCY SELL: Sell all {fartcoin_qty:.6f} FARTCOIN at market price")
        print(f"2. STOP-LOSS: Place stop at ${current_price * 0.98:.4f} (2% below current)")
        print(f"3. TAKE PROFIT: Place sell at ${current_price * 1.05:.4f} (5% above current)")
        
        action = input("\nChoose action (1=Sell All, 2=Stop-Loss, 3=Take Profit, 0=Exit): ")
        
        if action == "1":
            print(f"\n🚨 EMERGENCY SELL: Selling {fartcoin_qty:.6f} FARTCOIN...")
            order = exchange.create_market_sell_order('FARTCOIN/USDT', fartcoin_qty)
            print(f"✅ SOLD: {order}")
            
        elif action == "2":
            stop_price = current_price * 0.98
            print(f"\n🛡️ PLACING STOP-LOSS at ${stop_price:.4f}...")
            order = exchange.create_order('FARTCOIN/USDT', 'stop_market', 'sell', fartcoin_qty, None, None, {'stopPrice': stop_price})
            print(f"✅ STOP-LOSS PLACED: {order}")
            
        elif action == "3":
            take_profit_price = current_price * 1.05
            print(f"\n🎯 PLACING TAKE PROFIT at ${take_profit_price:.4f}...")
            order = exchange.create_limit_sell_order('FARTCOIN/USDT', fartcoin_qty, take_profit_price)
            print(f"✅ TAKE PROFIT PLACED: {order}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n📱 MANUAL ACTION REQUIRED:")
        print("1. Login to Binance manually")
        print("2. Check FARTCOIN/USDT position") 
        print("3. Place stop-loss or sell order")

if __name__ == "__main__":
    main()
