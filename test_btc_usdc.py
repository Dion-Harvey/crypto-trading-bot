#!/usr/bin/env python3
"""
Test BTC/USDC connection and verify the switch was successful
"""

import ccxt
import sys
import os

# Add the current directory to the path so we can import config
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import BINANCE_API_KEY, BINANCE_API_SECRET

def test_btc_usdc_connection():
    """Test BTC/USDC trading pair connectivity"""
    
    print("🔄 TESTING BTC/USDC CONNECTION")
    print("=" * 50)
    
    try:
        # Initialize exchange
        exchange = ccxt.binanceus({
            'apiKey': BINANCE_API_KEY,
            'secret': BINANCE_API_SECRET,
            'enableRateLimit': True,
            'timeout': 30000,
            'options': {
                'timeDifference': 1000,
                'adjustForTimeDifference': True
            }
        })
        
        # Test BTC/USDC ticker
        ticker = exchange.fetch_ticker('BTC/USDC')
        print(f"✅ BTC/USDC Price: ${ticker['last']:,.2f}")
        print(f"   24h Volume: {ticker['baseVolume']:,.2f} BTC")
        print(f"   24h Change: {ticker['percentage']:+.2f}%")
        
        # Test order book
        orderbook = exchange.fetch_order_book('BTC/USDC', 5)
        best_bid = orderbook['bids'][0][0] if orderbook['bids'] else 0
        best_ask = orderbook['asks'][0][0] if orderbook['asks'] else 0
        spread = best_ask - best_bid
        spread_pct = (spread / best_ask) * 100 if best_ask > 0 else 0
        
        print(f"\n📊 ORDER BOOK:")
        print(f"   Best Bid: ${best_bid:,.2f}")
        print(f"   Best Ask: ${best_ask:,.2f}")
        print(f"   Spread: ${spread:.2f} ({spread_pct:.3f}%)")
        
        # Check account balances
        balance = exchange.fetch_balance()
        
        print(f"\n💰 ACCOUNT BALANCES:")
        relevant_coins = ['BTC', 'USDC', 'USDT']
        for coin in relevant_coins:
            if coin in balance['total']:
                total_amount = balance['total'][coin]
                free_amount = balance['free'][coin]
                if total_amount > 0:
                    print(f"   {coin}: {total_amount:.6f} (Free: {free_amount:.6f})")
        
        # Calculate portfolio value in USDC
        btc_balance = balance['total'].get('BTC', 0)
        usdc_balance = balance['total'].get('USDC', 0)
        total_value_usdc = usdc_balance + (btc_balance * ticker['last'])
        
        print(f"\n📈 PORTFOLIO VALUE:")
        print(f"   Total Value: ${total_value_usdc:.2f} USDC")
        print(f"   BTC Holdings: {btc_balance:.6f} BTC (${btc_balance * ticker['last']:.2f})")
        print(f"   USDC Holdings: ${usdc_balance:.2f} USDC")
        
        # Validate trading requirements
        print(f"\n✅ BTC/USDC TRADING VALIDATION:")
        
        # Check minimum trade amount
        min_btc = 0.00001  # Minimum BTC amount
        min_notional = 10.0  # Minimum $10 USD equivalent
        
        current_price = ticker['last']
        min_usdc_for_min_btc = min_btc * current_price
        
        print(f"   Minimum BTC trade: {min_btc:.6f} BTC")
        print(f"   Minimum notional: ${min_notional:.2f}")
        print(f"   Min USDC needed: ${min_usdc_for_min_btc:.2f}")
        
        can_trade = usdc_balance >= max(min_notional, min_usdc_for_min_btc)
        trade_status = "✅ Ready to trade" if can_trade else "⚠️ Need more USDC"
        
        print(f"   Trading Status: {trade_status}")
        
        if not can_trade:
            needed = max(min_notional, min_usdc_for_min_btc) - usdc_balance
            print(f"   💡 Transfer at least ${needed:.2f} more USDC to start trading")
        
        print(f"\n🎯 RECOMMENDATION:")
        if usdc_balance > 0:
            print(f"   ✅ Switch to BTC/USDC completed successfully!")
            print(f"   🚀 Bot is ready to trade with ${usdc_balance:.2f} USDC")
        else:
            print(f"   📝 Transfer your USDT to USDC to complete the switch")
            print(f"   💡 Go to Binance US > Convert > USDT to USDC")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_btc_usdc_connection()
