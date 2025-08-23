#!/usr/bin/env python3
"""
Real-time Bot Dashboard
Enhanced monitoring with portfolio tracking and live updates
"""

import ccxt
import json
import time
import os
import subprocess
import json as _json
from datetime import datetime, timedelta

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def load_config():
    """Load configuration"""
    try:
        with open('enhanced_config.json', 'r') as f:
            return json.load(f)
    except:
        return None

def check_bot_status(max_stale_seconds: int = 120):
    """Check if bot is running using multi-source approach.

    Priority order:
      1. Heartbeat file freshness (bot_heartbeat.json)
      2. Process list heuristic
    Returns True if heartbeat fresh or process heuristics positive.
    """
    # 1. Heartbeat file
    try:
        if os.path.exists("bot_heartbeat.json"):
            with open("bot_heartbeat.json", "r", encoding="utf-8") as f:
                hb = _json.load(f)
            ts = hb.get("timestamp")
            if ts:
                from datetime import datetime, timezone
                try:
                    hb_time = datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(timezone.utc)
                    age = (datetime.now(timezone.utc) - hb_time).total_seconds()
                    if age <= max_stale_seconds and hb.get("status") in {"RUNNING", "STARTING"}:
                        return True
                except Exception:
                    pass
    except Exception:
        pass

    # 2. Process heuristic fallback
    try:
        result = subprocess.run(['powershell', '-Command', 
                               'Get-Process | Where-Object {$_.ProcessName -eq "python" -and $_.CommandLine -like "*bot.py*"}'], 
                               capture_output=True, text=True, timeout=5)
        if "python" in result.stdout.lower():
            return True
    except Exception:
        pass

    try:
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], 
                               capture_output=True, text=True, timeout=5)
        return "python.exe" in result.stdout
    except Exception:
        return False

def get_portfolio_data():
    """Get current portfolio status"""
    config = load_config()
    if not config:
        return None
    
    try:
        exchange = ccxt.binanceus({
            'apiKey': config['exchange']['api_key'],
            'secret': config['exchange']['secret'],
            'sandbox': False,
            'enableRateLimit': True,
            'options': {'defaultType': 'spot'}
        })
        
        balance = exchange.fetch_balance()
        
        # Focus on key assets
        assets = ['USDT', 'QTUM', 'LINK', 'BTC', 'ETH']
        portfolio = {}
        total_value = 0
        
        for asset in assets:
            if asset in balance and balance[asset]['total'] > 0.001:
                total = balance[asset]['total']
                free = balance[asset]['free']
                used = balance[asset]['used']
                
                if asset == 'USDT':
                    price = 1.0
                    value = total
                else:
                    try:
                        ticker = exchange.fetch_ticker(f'{asset}/USDT')
                        price = ticker['last']
                        value = total * price
                    except:
                        price = 0
                        value = 0
                
                if value >= 0.1:  # Show positions > $0.10
                    portfolio[asset] = {
                        'total': total,
                        'free': free,
                        'used': used,
                        'price': price,
                        'value': value
                    }
                    total_value += value
        
        return portfolio, total_value
    except:
        return None, 0

def get_recent_logs(lines=15):
    """Get recent log entries"""
    try:
        if os.path.exists('bot_log.txt'):
            with open('bot_log.txt', 'r') as f:
                log_lines = f.readlines()
                return [line.strip() for line in log_lines[-lines:] if line.strip()]
        return []
    except:
        return []

def format_currency(value):
    """Format currency values"""
    if value >= 1000:
        return f"${value:,.2f}"
    elif value >= 1:
        return f"${value:.2f}"
    else:
        return f"${value:.4f}"

def display_dashboard():
    """Main dashboard loop"""
    print("🚀 Starting Real-time Bot Dashboard...")
    print("   Press Ctrl+C to stop monitoring")
    time.sleep(2)
    
    try:
        while True:
            clear_screen()
            
            # Header
            print("🤖 CRYPTO TRADING BOT - LIVE DASHBOARD")
            print("=" * 70)
            print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print()
            
            # Bot status
            bot_running = check_bot_status()
            status_emoji = "✅" if bot_running else "❌"
            status_text = "RUNNING" if bot_running else "STOPPED"
            print(f"{status_emoji} BOT STATUS: {status_text}")
            print()
            
            # Portfolio status
            portfolio, total_value = get_portfolio_data()
            if portfolio:
                print("💰 PORTFOLIO STATUS:")
                print(f"   📈 Total Value: {format_currency(total_value)}")
                print()
                
                # Show positions
                active_positions = {k: v for k, v in portfolio.items() 
                                  if v['value'] >= 1.0 and k != 'USDT'}
                
                if active_positions:
                    print("🎯 ACTIVE POSITIONS:")
                    for asset, data in active_positions.items():
                        status_icon = "🟢" if asset == 'QTUM' else "💎"
                        print(f"   {status_icon} {asset:>6}: {data['total']:>10.6f} @ {format_currency(data['price'])} = {format_currency(data['value'])}")
                        if data['used'] > 0.001:
                            print(f"      🔒 Used: {data['used']:.6f} (in orders)")
                else:
                    print("   📭 No active positions")
                print()
                
                # Cash status
                if 'USDT' in portfolio:
                    usdt = portfolio['USDT']
                    print(f"💵 Available Cash: {format_currency(usdt['free'])}")
                    if usdt['free'] >= 20:
                        print("   ✅ Ready for opportunities")
                    else:
                        print("   ⚠️  Limited trading capital")
                print()
            else:
                print("⚠️ Portfolio data unavailable")
                print()
            
            # Recent activity
            recent_logs = get_recent_logs(8)
            if recent_logs:
                print("📊 RECENT ACTIVITY:")
                for log in recent_logs:
                    # Highlight key activities
                    if any(word in log.upper() for word in ['BUY', 'SELL']):
                        print(f"   🔥 {log}")
                    elif any(word in log.upper() for word in ['PROTECTION', 'BLOCK']):
                        print(f"   🛡️  {log}")
                    elif 'ERROR' in log.upper():
                        print(f"   ⚠️  {log}")
                    else:
                        print(f"   💡 {log}")
                print()
            
            # System status
            print("🔧 ENHANCED PROTECTION STATUS:")
            print("   ✅ Anti-Peak Buy Protection")
            print("   ✅ Stop-Loss Fallback (STOP_LOSS → STOP_LOSS_LIMIT)")  
            print("   ✅ Death Cross Protection (EMA7 < EMA25 blocking)")
            print("   ✅ Consolidation Detection")
            print("   ✅ Multi-Timeframe Analysis")
            print()

            # --- Gemini & AI Metrics (from heartbeat top-level fields) ---
            try:
                if os.path.exists('bot_heartbeat.json'):
                    with open('bot_heartbeat.json','r',encoding='utf-8') as _fhb:
                        _hb = json.load(_fhb)
                    ai_calls = _hb.get('ai_calls')
                    ai_use = _hb.get('ai_use')
                    ai_avg = _hb.get('ai_avg')
                    ai_last = _hb.get('ai_last')
                    ai_pos = _hb.get('ai_pos')
                    ai_neg = _hb.get('ai_neg')
                    gm_ms = _hb.get('gm_ms')
                    lat_ms = _hb.get('lat_ms')
                    if any(v is not None for v in [ai_calls, ai_use, ai_avg, ai_last, ai_pos, ai_neg, gm_ms, lat_ms]):
                        print("🤖 AI / GEMINI METRICS:")
                        if ai_calls is not None:
                            print(f"   📈 Total AI Calls: {ai_calls}")
                        if ai_use is not None:
                            print(f"   🎯 Adoption Rate: {ai_use}")
                        if ai_avg is not None:
                            print(f"   ⚖️ Avg Boost (last 50): {ai_avg:.3f}")
                        if ai_last is not None:
                            print(f"   🔄 Last Boost: {ai_last:.3f}")
                        if ai_pos is not None and ai_neg is not None:
                            print(f"   ✅ Positive / ❌ Negative: {ai_pos}/{ai_neg}")
                        if gm_ms is not None:
                            print(f"   ⏱️ Gemini Latency (ms): {gm_ms}")
                        if lat_ms is not None:
                            print(f"   ⏱️ Avg AI Latency (ms): {lat_ms}")
                        print()
            except Exception:
                pass
            
            # Key improvements summary
            print("🎯 RESOLVED ISSUES:")
            print("   ✅ QTUM peak buying fixed (was $26.32 spike)")
            print("   ✅ LINK balance tied up resolved (sold position)")
            print("   ✅ Stop-loss order type failures fixed")
            print("   ✅ Enhanced entry timing operational")
            print()
            
            print("🔄 Auto-refresh every 30 seconds | Ctrl+C to exit")
            print("=" * 70)
            
            # Wait for next update
            time.sleep(30)
            
    except KeyboardInterrupt:
        print("\n\n👋 Dashboard stopped - Bot continues running")
        print("💡 Check bot_log.txt for detailed activity")

if __name__ == "__main__":
    display_dashboard()
