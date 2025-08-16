#!/bin/bash
echo "🔍 AWS Bot Status Check"
echo "======================="

echo "📊 Checking for bot processes..."
ps aux | grep -E "(bot\.py|python.*bot)" | grep -v grep

echo ""
echo "📝 Latest log entries..."
if [ -f crypto-trading-bot/bot_log.txt ]; then
    tail -10 crypto-trading-bot/bot_log.txt
else
    echo "❌ Bot log file not found"
fi

echo ""
echo "🕒 System uptime..."
uptime

echo ""
echo "💾 Available disk space..."
df -h | head -2

echo ""
echo "🧠 Memory usage..."
free -h
