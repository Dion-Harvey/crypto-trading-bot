#!/bin/bash
# 🎯 Bot Monitoring Script - Quick Status Check

echo "🤖 CRYPTO BOT STATUS CHECK"
echo "=========================="

# Check if bot is running
echo "🔍 Bot Process Status:"
BOT_PID=$(ps aux | grep '[b]ot.py' | grep crypto-trading-bot | awk '{print $2}')
if [ -n "$BOT_PID" ]; then
    echo "✅ Bot is RUNNING (PID: $BOT_PID)"
    echo "   Started: $(ps -o lstart= -p $BOT_PID 2>/dev/null || echo 'Unknown')"
else
    echo "❌ Bot is NOT RUNNING"
fi

echo ""
echo "⚙️ Configuration Summary:"
echo "   Confidence Threshold: $(grep 'confidence_threshold' enhanced_config.json | head -1 | cut -d':' -f2 | tr -d ' ,')"
echo "   Position Size: $(grep 'base_position_pct' enhanced_config.json | cut -d':' -f2 | tr -d ' ,')"
echo "   Trade Cooldown: $(grep 'trade_cooldown_seconds' enhanced_config.json | cut -d':' -f2 | tr -d ' ,')"

echo ""
echo "📊 Recent Activity (Last 10 lines):"
tail -10 bot_output.log

echo ""
echo "📈 Monitoring Commands:"
echo "   tail -f bot_output.log     # Watch live activity"
echo "   tail -f trade_log.csv      # Watch trades"
echo "   ps aux | grep bot.py       # Check bot status"
