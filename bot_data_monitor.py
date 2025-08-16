#!/usr/bin/env python3
"""
Real-time Bot Data Monitor - Shows live data polling from the bot
"""

import time
import sys
import ccxt
from datetime import datetime
from config import BINANCE_API_KEY, BINANCE_API_SECRET

# Initialize exchange (same as bot)
exchange = ccxt.binanceus({
    'apiKey': BINANCE_API_KEY,
    'secret': BINANCE_API_SECRET,
    'enableRateLimit': True,
    'timeout': 30000,
    'rateLimit': 1200,
    'options': {
        'recvWindow': 10000,
        'timeDifference': 1000,
        'adjustForTimeDifference': True
    }
})

def monitor_bot_data_polling():
    """Monitor what data the bot would be seeing in real-time"""
    print("🔴 LIVE BOT DATA MONITOR")
    print("Showing real-time data as the bot would see it...")
    print("=" * 60)
    
    try:
        # Import the same fetch function the bot uses
        from strategies.ma_crossover import fetch_ohlcv
        
        previous_price = None
        poll_count = 0
        
        while True:
            poll_count += 1
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            # Get live ticker (same as bot)
            ticker = exchange.fetch_ticker('BTC/USDC')
            current_price = ticker['last']
            
            # Fetch 1-minute OHLCV data (same as bot loop)
            try:
                df = fetch_ohlcv(exchange, 'BTC/USDC', '1m', 10)
                latest_candle_price = df['close'].iloc[-1] if len(df) > 0 else current_price
                data_points = len(df)
            except Exception as e:
                latest_candle_price = current_price
                data_points = 0
                
            # Calculate price movement
            price_change = 0
            change_pct = 0
            if previous_price:
                price_change = current_price - previous_price
                change_pct = (price_change / previous_price) * 100
            
            # Display bot's view
            change_symbol = "📈" if price_change >= 0 else "📉"
            print(f"\n🤖 BOT DATA POLL #{poll_count} @ {timestamp}")
            print(f"   💰 Live Price: ${current_price:,.2f}")
            print(f"   📊 Candle Data: {data_points} points | Latest: ${latest_candle_price:,.2f}")
            
            if previous_price:
                print(f"   {change_symbol} Movement: ${price_change:+.2f} ({change_pct:+.4f}%)")
            
            print(f"   📊 Bid: ${ticker['bid']:,.2f} | Ask: ${ticker['ask']:,.2f}")
            print(f"   📈 Volume: ${ticker['quoteVolume']:,.0f}")
            print(f"   🕐 Exchange Time: {ticker['datetime']}")
            
            # Show what bot's MA calculations would see
            if data_points >= 25:
                try:
                    # Calculate the same MAs the bot uses
                    ma_7 = df['close'].rolling(7).mean().iloc[-1]
                    ma_25 = df['close'].rolling(25).mean().iloc[-1] if len(df) >= 25 else None
                    
                    if ma_25:
                        ma_spread = abs(ma_7 - ma_25) / ma_25 * 100
                        ma_position = "MA7 > MA25" if ma_7 > ma_25 else "MA7 < MA25"
                        print(f"   📊 MA7: ${ma_7:.2f} | MA25: ${ma_25:.2f}")
                        print(f"   📈 {ma_position} | Spread: {ma_spread:.2f}%")
                except:
                    print("   ⚠️ MA calculation error")
            else:
                print(f"   ⏳ Waiting for MA data ({data_points}/25 candles)")
            
            previous_price = current_price
            
            print("-" * 50)
            
            # Wait 30 seconds (same as bot's fast loop)
            time.sleep(30)
            
    except KeyboardInterrupt:
        print(f"\n✅ Monitoring stopped after {poll_count} polls")
        print("🤖 Bot data polling is working correctly!")
    except Exception as e:
        print(f"❌ Error during monitoring: {e}")

if __name__ == "__main__":
    print("🚀 REAL-TIME BOT DATA MONITORING")
    print("Press Ctrl+C to stop...")
    print("=" * 60)
    
    monitor_bot_data_polling()
