#!/usr/bin/env python3
"""
Comprehensive Bot Status and Opportunity Scanner
Checks current positions, recent trades, and identifies new opportunities after LINK sale
"""

import ccxt
import json
import time
from datetime import datetime, timedelta
import pandas as pd

def load_config():
    """Load trading configuration"""
    try:
        with open('enhanced_config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ enhanced_config.json not found")
        return None

def check_comprehensive_status():
    """Check comprehensive bot status and opportunities"""
    
    print("🤖 COMPREHENSIVE BOT STATUS CHECK")
    print("=" * 60)
    print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    config = load_config()
    if not config:
        return
    
    # Initialize exchange
    try:
        exchange_config = config['exchange']
        exchange = ccxt.binanceus({
            'apiKey': exchange_config['api_key'],
            'secret': exchange_config['secret'],
            'sandbox': exchange_config.get('testnet', False),
            'enableRateLimit': True,
            'options': {'defaultType': 'spot'}
        })
        
        print("✅ Exchange connection established")
        
    except Exception as e:
        print(f"❌ Exchange connection failed: {e}")
        return
    
    # Check current balance for all assets
    print("\n💰 CURRENT PORTFOLIO STATUS:")
    try:
        balance = exchange.fetch_balance()
        
        # Key assets to check
        key_assets = ['USDT', 'BTC', 'ETH', 'LINK', 'QTUM', 'ADA', 'DOT', 'MATIC']
        total_portfolio_value = 0
        positions = []
        
        for asset in key_assets:
            if asset in balance and balance[asset]['total'] > 0.001:
                free = balance[asset]['free']
                used = balance[asset]['used'] 
                total = balance[asset]['total']
                
                if asset == 'USDT':
                    value = total
                else:
                    try:
                        ticker = exchange.fetch_ticker(f'{asset}/USDT')
                        price = ticker['last']
                        value = total * price
                    except:
                        price = 0
                        value = 0
                
                total_portfolio_value += value
                
                if total >= 0.001:  # Only show significant amounts
                    positions.append({
                        'asset': asset,
                        'free': free,
                        'used': used,
                        'total': total,
                        'price': price if asset != 'USDT' else 1.0,
                        'value': value
                    })
                    
                    status = "🟢 ACTIVE" if (price > 0 and total >= 10/price) else "💨 DUST"
                    print(f"   {asset:>6}: {total:>12.8f} (Free: {free:>10.6f}, Used: {used:>10.6f}) = ${value:>8.2f} {status}")
        
        print(f"\n   📊 TOTAL PORTFOLIO VALUE: ${total_portfolio_value:.2f}")
        
    except Exception as e:
        print(f"   ❌ Balance check failed: {e}")
    
    # Check specific positions mentioned
    print("\n🎯 SPECIFIC POSITION ANALYSIS:")
    
    # LINK Analysis
    print("   📊 LINK/USDT Status:")
    try:
        link_balance = balance['LINK']
        ticker = exchange.fetch_ticker('LINK/USDT')
        price = ticker['last']
        
        if link_balance['total'] <= 0.001:
            print("   ✅ CONFIRMED: LINK position is CLOSED/SOLD")
            print("   📈 Ready for new opportunities")
        else:
            print(f"   ⚠️  LINK still held: {link_balance['total']:.6f} LINK (${link_balance['total'] * price:.2f})")
            
    except Exception as e:
        print(f"   ❌ LINK check failed: {e}")
    
    # QTUM Analysis  
    print("\n   📊 QTUM/USDT Status:")
    try:
        qtum_balance = balance['QTUM']
        ticker = exchange.fetch_ticker('QTUM/USDT')
        price = ticker['last']
        value = qtum_balance['total'] * price
        
        if qtum_balance['total'] >= 0.01:
            print(f"   🟢 QTUM POSITION ACTIVE: {qtum_balance['total']:.6f} QTUM")
            print(f"   💰 Current Value: ${value:.2f}")
            print(f"   📊 Price: ${price:.4f}")
            print(f"   🔓 Free: {qtum_balance['free']:.6f}")
            print(f"   🔒 Used: {qtum_balance['used']:.6f}")
            
            # Get recent price performance
            try:
                ohlcv = exchange.fetch_ohlcv('QTUM/USDT', '1h', limit=24)
                if ohlcv:
                    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                    price_24h_ago = df['close'].iloc[0]
                    price_change = ((price - price_24h_ago) / price_24h_ago) * 100
                    print(f"   📈 24h Performance: {price_change:+.2f}%")
            except:
                pass
                
        else:
            print("   📭 No significant QTUM position")
            
    except Exception as e:
        print(f"   ❌ QTUM check failed: {e}")
    
    # Check recent trading activity
    print("\n📈 RECENT TRADING ACTIVITY (Last 24h):")
    try:
        since = int((datetime.now() - timedelta(hours=24)).timestamp() * 1000)
        
        # Check multiple pairs for recent activity
        trading_pairs = ['LINK/USDT', 'QTUM/USDT', 'BTC/USDT']
        total_trades = 0
        
        for pair in trading_pairs:
            try:
                trades = exchange.fetch_my_trades(pair, since=since, limit=50)
                if trades:
                    print(f"   📊 {pair}: {len(trades)} trades")
                    total_trades += len(trades)
                    
                    # Show recent trades
                    for trade in trades[-3:]:  # Last 3 trades
                        timestamp = datetime.fromtimestamp(trade['timestamp'] / 1000)
                        side = "🟢 BUY " if trade['side'] == 'buy' else "🔴 SELL"
                        print(f"      {timestamp.strftime('%H:%M:%S')} {side} {trade['amount']:.6f} @ ${trade['price']:.4f}")
            except:
                continue
        
        if total_trades == 0:
            print("   📭 No trades in last 24 hours")
            
    except Exception as e:
        print(f"   ❌ Trading activity check failed: {e}")
    
    # Market opportunity analysis
    print("\n🎯 NEW TRADING OPPORTUNITIES:")
    try:
        # Check top volume pairs for opportunities
        markets = exchange.fetch_tickers()
        
        # Filter for USDT pairs with good volume
        usdt_pairs = {k: v for k, v in markets.items() 
                     if k.endswith('/USDT') and v['quoteVolume'] and v['quoteVolume'] > 1000000}
        
        # Sort by volume
        top_pairs = sorted(usdt_pairs.items(), key=lambda x: x[1]['quoteVolume'], reverse=True)[:10]
        
        print("   📊 TOP VOLUME OPPORTUNITIES (24h volume > $1M):")
        for pair, ticker in top_pairs[:5]:
            symbol = pair.replace('/USDT', '')
            price = ticker['last']
            change = ticker['percentage']
            volume = ticker['quoteVolume']
            
            # Opportunity scoring
            opportunity_score = 0
            signals = []
            
            # Volume-based scoring
            if volume > 10000000:  # >$10M
                opportunity_score += 2
                signals.append("High Volume")
            elif volume > 5000000:  # >$5M  
                opportunity_score += 1
                signals.append("Good Volume")
            
            # Price movement scoring
            if abs(change) > 5:
                if change > 0:
                    signals.append("Strong Up Momentum")
                    opportunity_score += 1
                else:
                    signals.append("Oversold Potential")
                    opportunity_score += 1
            elif abs(change) > 2:
                signals.append("Active Movement")
                opportunity_score += 0.5
            
            # Exclude current holdings
            if symbol not in ['QTUM', 'LINK']:
                score_emoji = "🔥" if opportunity_score >= 2 else "⭐" if opportunity_score >= 1 else "📊"
                print(f"      {score_emoji} {symbol:>6}: ${price:>8.4f} ({change:+6.2f}%) Vol: ${volume/1e6:>5.1f}M {' | '.join(signals)}")
        
    except Exception as e:
        print(f"   ❌ Opportunity analysis failed: {e}")
    
    # Bot operational status
    print("\n🤖 BOT OPERATIONAL STATUS:")
    
    # Check if bot processes are running
    import psutil
    python_processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] and 'python' in proc.info['name'].lower():
                cmdline = proc.info['cmdline']
                if cmdline and any('bot.py' in arg for arg in cmdline):
                    python_processes.append({
                        'pid': proc.info['pid'],
                        'cmdline': ' '.join(cmdline[-2:])  # Last 2 args
                    })
        except:
            continue
    
    if python_processes:
        print("   ✅ Bot processes detected:")
        for proc in python_processes:
            print(f"      PID {proc['pid']}: {proc['cmdline']}")
    else:
        print("   ⚠️  No bot processes detected - bot may not be running")
    
    # Summary and recommendations
    print("\n📋 SUMMARY & RECOMMENDATIONS:")
    
    # Position summary
    active_positions = [p for p in positions if p['value'] >= 10]
    if active_positions:
        print("   🎯 Active Positions:")
        for pos in active_positions:
            if pos['asset'] != 'USDT':
                print(f"      {pos['asset']}: {pos['total']:.6f} = ${pos['value']:.2f}")
    
    # Cash available
    usdt_balance = next((p['total'] for p in positions if p['asset'] == 'USDT'), 0)
    print(f"   💰 Available Cash: ${usdt_balance:.2f}")
    
    # Recommendations
    if usdt_balance >= 20:
        print("   ✅ Sufficient cash for new opportunities")
    else:
        print("   ⚠️  Limited cash - consider taking profits on existing positions")
    
    print("\n" + "=" * 60)
    print("🔄 STATUS CHECK COMPLETE")

if __name__ == "__main__":
    check_comprehensive_status()
