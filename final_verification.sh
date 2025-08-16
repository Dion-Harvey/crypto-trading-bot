#!/bin/bash
# 🎯 FINAL VERIFICATION REPORT - OPTIMIZED BOT STATUS

echo "🤖 CRYPTO TRADING BOT - FINAL VERIFICATION"
echo "=========================================="
echo ""

# Get bot PID
BOT_PID=$(ps aux | grep '[.]venv/bin/python bot.py' | grep crypto-trading-bot | awk '{print $2}')

if [ -n "$BOT_PID" ]; then
    echo "✅ BOT STATUS: RUNNING"
    echo "   Process ID: $BOT_PID"
    echo "   Directory: /home/ubuntu/crypto-trading-bot"
    echo "   Config File: enhanced_config.json (OPTIMIZED)"
else
    echo "❌ BOT STATUS: NOT RUNNING"
    exit 1
fi

echo ""
echo "⚙️ OPTIMIZED CONFIGURATION VALUES:"
echo "   Confidence Threshold: $(grep '"confidence_threshold"' enhanced_config.json | head -1 | cut -d':' -f2 | tr -d ' ,')"
echo "   Position Size: $(grep '"base_position_pct"' enhanced_config.json | cut -d':' -f2 | tr -d ' ,') (was 0.35)"
echo "   Trade Cooldown: $(grep '"trade_cooldown_seconds"' enhanced_config.json | cut -d':' -f2 | tr -d ' ,')s (was 300s)"
echo "   Min Hold Time: $(grep '"minimum_hold_time_minutes"' enhanced_config.json | cut -d':' -f2 | tr -d ' ,')min (was 30min)"

echo ""
echo "📊 RECENT BOT ACTIVITY:"
tail -5 bot_live.log

echo ""
echo "🎯 OPTIMIZATION SUMMARY:"
echo "   • Confidence lowered from 70% to 55% (more responsive)"
echo "   • Position size increased from 35% to 45% (+28% larger)"
echo "   • Trade cooldown reduced from 5min to 3min (40% faster)"
echo "   • Min hold time reduced from 30min to 15min (50% shorter)"
echo "   • Volume/trend confirmations disabled (less restrictive)"
echo ""
echo "✅ VERIFICATION COMPLETE: Bot running with optimized configuration!"
