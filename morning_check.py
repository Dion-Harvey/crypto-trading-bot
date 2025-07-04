import ccxt
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import BINANCE_API_KEY, BINANCE_API_SECRET

print("🌅 GOOD MORNING! Bot Status Check")
print("=" * 40)

try:
    exchange = ccxt.binanceus({
        'apiKey': BINANCE_API_KEY,
        'secret': BINANCE_API_SECRET,
        'enableRateLimit': True,
        'timeout': 30000,
        'options': {'timeDifference': 1000}
    })
    
    ticker = exchange.fetch_ticker('BTC/USDC')
    balance = exchange.fetch_balance()
    
    print(f"✅ Binance US: CONNECTED")
    print(f"📈 BTC/USDC: ${ticker['last']:,.2f} ({ticker['percentage']:+.2f}%)")
    print(f"💰 Your USDC: ${balance['total'].get('USDC', 0):.2f}")
    print(f"₿ Your BTC: {balance['total'].get('BTC', 0):.6f}")
    
    total_value = balance['total'].get('USDC', 0) + (balance['total'].get('BTC', 0) * ticker['last'])
    print(f"📊 Total Portfolio: ${total_value:.2f}")
    
    print(f"\n🤖 BOT STATUS: OFFLINE (not running)")
    print(f"🚀 Ready to start with: python bot.py")
    
except Exception as e:
    print(f"❌ Connection issue: {e}")
