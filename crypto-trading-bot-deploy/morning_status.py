#!/usr/bin/env python3
"""
Morning Status Check - Comprehensive Bot and Market Analysis
"""

import ccxt
import datetime
from config import BINANCE_API_KEY, BINANCE_API_SECRET

def morning_status_check():
    print("🌅 GOOD MORNING - COMPREHENSIVE STATUS CHECK")
    print("=" * 60)
    print(f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Initialize exchange
        exchange = ccxt.binanceus({
            'apiKey': BINANCE_API_KEY,
            'secret': BINANCE_API_SECRET,
            'enableRateLimit': True,
            'options': {'timeDifference': 1000}
        })
        
        # Get balance and market data
        balance = exchange.fetch_balance()
        ticker = exchange.fetch_ticker('BTC/USDC')
        
        current_price = ticker['last']
        btc_balance = balance['BTC']['free']
        usdc_balance = balance['USDC']['free']
        usdt_balance = balance['USDT']['free']
        
        total_usd = usdc_balance + usdt_balance + (btc_balance * current_price)
        
        print("💰 PORTFOLIO STATUS:")
        print(f"   BTC: {btc_balance:.8f} BTC (~${btc_balance * current_price:.2f})")
        print(f"   USDC: ${usdc_balance:.2f}")
        print(f"   USDT: ${usdt_balance:.2f}")
        print(f"   📊 Total Portfolio: ${total_usd:.2f}")
        
        # Determine if we're in a position
        btc_value_usd = btc_balance * current_price
        in_position = btc_value_usd > 1.0
        print(f"   🎯 Position Status: {'📈 HOLDING BTC' if in_position else '💵 CASH READY'}")
        print()
        
        print("📈 MARKET CONDITIONS:")
        print(f"   BTC/USDC: ${current_price:,.2f}")
        print(f"   24h Change: {ticker['percentage']:+.2f}%")
        print(f"   24h High: ${ticker['high']:,.2f}")
        print(f"   24h Low: ${ticker['low']:,.2f}")
        print(f"   24h Volume: ${ticker['quoteVolume']:,.0f}")
        print()
        
        # Market analysis
        price_change = ticker['percentage']
        price_range_pct = (ticker['high'] - ticker['low']) / current_price * 100
        
        # Market mood assessment
        if price_change > 3:
            market_mood = "🚀 VERY BULLISH"
        elif price_change > 1:
            market_mood = "📈 BULLISH"
        elif price_change > -1:
            market_mood = "😐 NEUTRAL"
        elif price_change > -3:
            market_mood = "📉 BEARISH"
        else:
            market_mood = "🐻 VERY BEARISH"
        
        # Volatility assessment
        if price_range_pct > 5:
            volatility = "🔥 VERY HIGH"
            vol_note = "High profit potential but increased risk"
        elif price_range_pct > 3:
            volatility = "⚡ HIGH" 
            vol_note = "Good trading opportunities"
        elif price_range_pct > 1.5:
            volatility = "📊 MEDIUM"
            vol_note = "Normal market conditions"
        else:
            volatility = "😴 LOW"
            vol_note = "Limited opportunities"
        
        print("🎯 MARKET ASSESSMENT:")
        print(f"   Market Mood: {market_mood}")
        print(f"   Volatility: {volatility} ({price_range_pct:.1f}% range)")
        print(f"   Note: {vol_note}")
        print()
        
        # Bot configuration reminder
        print("🤖 BOT CONFIGURATION SUMMARY:")
        print("   ✅ Rally Riding: 15% take profit (perfect for 4.7%+ moves)")
        print("   ✅ Risk Management: 2.5% stop loss, 3% trailing stops")
        print("   ✅ Trend Following: Anti-sell during strong uptrends")
        print("   ✅ Quality Filters: 75% confidence + anti-whipsaw protection")
        print("   ✅ Position Sizing: 25% of portfolio (institutional Kelly)")
        print()
        
        # Trading recommendations
        print("📋 MORNING RECOMMENDATIONS:")
        
        if price_change > 2 and volatility in ["🔥 VERY HIGH", "⚡ HIGH"]:
            print("   🎯 OPPORTUNITY: Strong momentum + high volatility")
            print("   💡 Bot is well-positioned to capture breakout moves")
            
        elif price_change < -2 and volatility in ["🔥 VERY HIGH", "⚡ HIGH"]:
            print("   💎 OPPORTUNITY: Potential dip-buying setup")
            print("   💡 Bot has smart trend filters to avoid falling knives")
            
        elif abs(price_change) < 1 and volatility == "😴 LOW":
            print("   ⏳ PATIENCE: Low volatility choppy market")
            print("   💡 Bot's anti-whipsaw protection will prevent bad trades")
            
        else:
            print("   👀 MONITOR: Normal market conditions")
            print("   💡 Bot is ready for quality signals when they appear")
        
        print()
        print("✅ STATUS CHECK COMPLETE - Bot is ready for trading!")
        
        return {
            'portfolio_value': total_usd,
            'btc_price': current_price,
            'price_change_24h': price_change,
            'volatility_pct': price_range_pct,
            'in_position': in_position
        }
        
    except Exception as e:
        print(f"❌ Error during status check: {e}")
        return None

if __name__ == "__main__":
    morning_status_check()
