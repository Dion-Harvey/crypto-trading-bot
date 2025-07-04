#!/usr/bin/env python3
"""
Check available trading pairs and fee structures on Binance US
Focus on zero-fee pairs for optimal trading
"""

import ccxt
import json
from config import BINANCE_API_KEY, BINANCE_API_SECRET

def check_binance_us_pairs():
    """Check available pairs and fee structures"""
    
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
    
    print("🔍 CHECKING BINANCE US TRADING PAIRS AND FEES")
    print("=" * 60)
    
    try:
        # Get all available markets
        markets = exchange.load_markets()
        
        # Get trading fees
        try:
            trading_fees = exchange.fetch_trading_fees()
            print(f"✅ Trading fees structure loaded")
        except Exception as fee_error:
            print(f"⚠️ Could not fetch trading fees: {fee_error}")
            trading_fees = None
        
        # Focus on BTC pairs
        btc_pairs = []
        zero_fee_pairs = []
        
        print(f"\n📊 AVAILABLE BTC TRADING PAIRS:")
        print("-" * 40)
        
        for symbol, market in markets.items():
            if symbol.startswith('BTC/') and market['active']:
                btc_pairs.append(symbol)
                
                # Check fees if available
                maker_fee = 0
                taker_fee = 0
                
                if trading_fees and 'trading' in trading_fees:
                    if symbol in trading_fees['trading']:
                        maker_fee = trading_fees['trading'][symbol]['maker']
                        taker_fee = trading_fees['trading'][symbol]['taker']
                    else:
                        # Use default fees
                        maker_fee = trading_fees['trading'].get('maker', 0.001)  # 0.1% default
                        taker_fee = trading_fees['trading'].get('taker', 0.001)  # 0.1% default
                
                # Check if it's zero fee
                is_zero_fee = (maker_fee == 0 and taker_fee == 0)
                if is_zero_fee:
                    zero_fee_pairs.append(symbol)
                
                fee_status = "🆓 ZERO FEES" if is_zero_fee else f"💰 {maker_fee:.3%}/{taker_fee:.3%}"
                
                print(f"   {symbol:<12} - {fee_status}")
        
        print(f"\n🎯 ZERO-FEE BTC PAIRS FOUND:")
        print("-" * 30)
        if zero_fee_pairs:
            for pair in zero_fee_pairs:
                print(f"   ✅ {pair}")
        else:
            print("   ❌ No zero-fee BTC pairs detected")
            print("   💡 Note: Some pairs may have promotional zero fees not reflected in API")
        
        # Test specific pairs we're interested in
        test_pairs = ['BTC/USDT', 'BTC/USDC', 'BTC/USD']
        
        print(f"\n🧪 TESTING SPECIFIC PAIRS:")
        print("-" * 30)
        
        for pair in test_pairs:
            if pair in markets:
                market_info = markets[pair]
                
                # Get current ticker
                try:
                    ticker = exchange.fetch_ticker(pair)
                    price = ticker['last']
                    volume = ticker['baseVolume']
                    
                    # Check fees
                    maker_fee = 0
                    taker_fee = 0
                    
                    if trading_fees and 'trading' in trading_fees:
                        if pair in trading_fees['trading']:
                            maker_fee = trading_fees['trading'][pair]['maker']
                            taker_fee = trading_fees['trading'][pair]['taker']
                        else:
                            maker_fee = trading_fees['trading'].get('maker', 0.001)
                            taker_fee = trading_fees['trading'].get('taker', 0.001)
                    
                    is_zero_fee = (maker_fee == 0 and taker_fee == 0)
                    fee_status = "🆓 ZERO FEES" if is_zero_fee else f"💰 {maker_fee:.3%}/{taker_fee:.3%}"
                    
                    print(f"   {pair}:")
                    print(f"      Price: ${price:,.2f}")
                    print(f"      24h Volume: {volume:,.2f} BTC")
                    print(f"      Fees: {fee_status}")
                    print(f"      Status: {'✅ ACTIVE' if market_info['active'] else '❌ INACTIVE'}")
                    print()
                    
                except Exception as ticker_error:
                    print(f"   {pair}: ❌ Error fetching data - {ticker_error}")
            else:
                print(f"   {pair}: ❌ Not available")
        
        # Account balance check
        print(f"\n💰 CURRENT ACCOUNT BALANCES:")
        print("-" * 30)
        
        try:
            balance = exchange.fetch_balance()
            
            relevant_coins = ['BTC', 'USDT', 'USDC', 'USD']
            for coin in relevant_coins:
                if coin in balance['total'] and balance['total'][coin] > 0:
                    free_amount = balance['free'][coin]
                    total_amount = balance['total'][coin]
                    print(f"   {coin}: {total_amount:.6f} (Free: {free_amount:.6f})")
        
        except Exception as balance_error:
            print(f"   ❌ Could not fetch balance: {balance_error}")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        print("-" * 20)
        
        if 'BTC/USDC' in markets and markets['BTC/USDC']['active']:
            print("   ✅ BTC/USDC is available - try this pair!")
        
        if 'BTC/USDT' in markets and markets['BTC/USDT']['active']:
            print("   ✅ BTC/USDT is available - currently used by bot")
        
        print("\n   📝 Note: Binance US may have promotional zero fees on certain pairs")
        print("   📝 that aren't reflected in the API fee structure.")
        print("   📝 Check the Binance US website for current promotions.")
        
    except Exception as e:
        print(f"❌ Error checking pairs: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_binance_us_pairs()
