#!/bin/bash
# 📊 Quick Daily Health Check for Phase 3 Week 1

echo "🤖 CRYPTO BOT DAILY HEALTH CHECK"
echo "================================="
echo "📅 $(date)"
echo

# Bot Status
if pgrep -f "python.*bot.py" > /dev/null; then
    BOT_PID=$(pgrep -f "python.*bot.py")
    BOT_UPTIME=$(ps -o etime= -p $BOT_PID | tr -d ' ')
    echo "✅ Bot Status: RUNNING (PID: $BOT_PID, Uptime: $BOT_UPTIME)"
else
    echo "❌ Bot Status: NOT RUNNING"
fi

# System Resources
echo
echo "💾 System Health:"
echo "   Disk: $(df -h / | tail -1 | awk '{print $3 "/" $2 " (" $5 " used)"}')"
echo "   Memory: $(free -h | grep Mem | awk '{print $3 "/" $2}')"
echo "   Load: $(uptime | awk -F'load average:' '{print $2}')"

# Recent Activity
echo
echo "📈 Recent Trading Activity (last 5 lines):"
tail -5 bot_output.log 2>/dev/null | head -5 || echo "   No recent activity logged"

# Quick Performance Check
echo
echo "🧠 AI Status:"
if python3 -c "import tensorflow" 2>/dev/null; then
    echo "   ✅ TensorFlow: Working"
else
    echo "   ❌ TensorFlow: Issue detected"
fi

# Quick Summary
echo
echo "📊 Quick Summary:"
echo "   - Phase 3 Week 1: Day $(( ($(date +%s) - $(date -d '2025-08-01' +%s)) / 86400 + 1 ))"
echo "   - AI Learning: In progress"
echo "   - Next Check: Tomorrow same time"
echo "   - Goal: Watch for improvement trends"

echo
echo "💡 Reminder: Day 1-2 losses are normal as AI learns!"
echo "🎯 Expected improvement by Day 3-4"
echo "🚀 Full optimization by Day 5-7"
