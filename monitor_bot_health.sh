#!/bin/bash
"""
🔍 CRYPTO BOT HEALTH MONITOR
============================
Comprehensive health monitoring for the crypto trading bot
"""

echo "🔍 Crypto Bot Health Monitor"
echo "============================"
echo ""

# Check system services
echo "📊 Service Status:"
systemctl is-active crypto-trading-bot 2>/dev/null && echo "✅ Trading Bot: ACTIVE" || echo "❌ Trading Bot: INACTIVE"
systemctl is-active crypto-bot-watchdog 2>/dev/null && echo "✅ Watchdog: ACTIVE" || echo "❌ Watchdog: INACTIVE"
echo ""

# Check processes
echo "🔄 Process Status:"
if pgrep -f "bot.py" > /dev/null; then
    echo "✅ Bot process: RUNNING"
    echo "   PID: $(pgrep -f 'bot.py')"
    echo "   Memory: $(ps -o pid,rss,pmem,comm -p $(pgrep -f 'bot.py') | tail -1 | awk '{print $2/1024 " MB (" $3 "%)"}')"
else
    echo "❌ Bot process: NOT RUNNING"
fi

if pgrep -f "crypto-bot-watchdog.py" > /dev/null; then
    echo "✅ Watchdog process: RUNNING"
    echo "   PID: $(pgrep -f 'crypto-bot-watchdog.py')"
else
    echo "❌ Watchdog process: NOT RUNNING"
fi
echo ""

# Check recent activity
echo "📈 Recent Activity:"
if [ -f "bot_log.txt" ]; then
    last_log=$(stat -c %Y bot_log.txt)
    current_time=$(date +%s)
    time_diff=$((current_time - last_log))
    
    if [ $time_diff -lt 300 ]; then
        echo "✅ Bot log activity: RECENT (${time_diff}s ago)"
    elif [ $time_diff -lt 900 ]; then
        echo "⚠️ Bot log activity: OLD (${time_diff}s ago)"
    else
        echo "❌ Bot log activity: STALE (${time_diff}s ago)"
    fi
    
    echo "   Last log entry:"
    tail -1 bot_log.txt | sed 's/^/   /'
else
    echo "❌ No bot log file found"
fi
echo ""

# Check disk space
echo "💾 Disk Space:"
df -h . | awk 'NR==2 {print "   Used: " $3 "/" $2 " (" $5 ")"}'
echo ""

# Check network connectivity
echo "🌐 Network Status:"
if ping -c 1 api.binance.com > /dev/null 2>&1; then
    echo "✅ Binance API: REACHABLE"
else
    echo "❌ Binance API: UNREACHABLE"
fi

# Show system uptime
echo ""
echo "⏰ System Uptime:"
uptime | sed 's/^/   /'
