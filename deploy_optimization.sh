#!/bin/bash
# 🚀 Quick Bot Optimization Deployment Script

echo "🎯 CRYPTO BOT OPTIMIZATION DEPLOYMENT"
echo "======================================"

# Backup current config
echo "📁 Creating backup..."
cp enhanced_config.json enhanced_config.json.backup_$(date +%Y%m%d_%H%M%S)

# Apply optimizations directly via sed commands
echo "⚙️ Applying optimizations..."

# 1. Reduce confidence threshold from 0.7 to 0.55
sed -i 's/"confidence_threshold": 0.7/"confidence_threshold": 0.55/' enhanced_config.json

# 2. Reduce consensus requirements
sed -i 's/"min_consensus_votes": 5/"min_consensus_votes": 3/' enhanced_config.json
sed -i 's/"strong_consensus_votes": 6/"strong_consensus_votes": 4/' enhanced_config.json

# 3. Disable confirmation requirements
sed -i 's/"volume_confirmation_required": true/"volume_confirmation_required": false/' enhanced_config.json
sed -i 's/"trend_confirmation_required": true/"trend_confirmation_required": false/' enhanced_config.json

# 4. Increase position sizing
sed -i 's/"base_position_pct": 0.35/"base_position_pct": 0.45/' enhanced_config.json
sed -i 's/"min_position_pct": 0.25/"min_position_pct": 0.30/' enhanced_config.json
sed -i 's/"max_position_pct": 0.5/"max_position_pct": 0.65/' enhanced_config.json

# 5. Reduce trade cooldown
sed -i 's/"trade_cooldown_seconds": 300/"trade_cooldown_seconds": 180/' enhanced_config.json

# 6. Reduce minimum hold time
sed -i 's/"minimum_hold_time_minutes": 30/"minimum_hold_time_minutes": 15/' enhanced_config.json

# 7. Adjust RSI levels
sed -i 's/"rsi_oversold": 25/"rsi_oversold": 30/' enhanced_config.json
sed -i 's/"rsi_overbought": 75/"rsi_overbought": 70/' enhanced_config.json

# 8. Disable multi-timeframe requirement
sed -i 's/"multi_timeframe_required": true/"multi_timeframe_required": false/' enhanced_config.json

# 9. Reduce trend strength requirement
sed -i 's/"minimum_trend_strength": 0.02/"minimum_trend_strength": 0.015/' enhanced_config.json

# 10. Adjust confidence scaling
sed -i 's/"high_confidence_threshold": 0.65/"high_confidence_threshold": 0.55/' enhanced_config.json
sed -i 's/"exceptional_confidence_threshold": 0.75/"exceptional_confidence_threshold": 0.65/' enhanced_config.json

echo "✅ Configuration optimized!"

# Restart bot
echo "🔄 Restarting bot..."
pkill -f bot.py
sleep 2

echo "🚀 Starting optimized bot..."
nohup python3 bot.py > bot_output.log 2>&1 &

sleep 3

# Check if bot started
if ps aux | grep -q "[b]ot.py"; then
    echo "✅ Bot restarted successfully!"
    echo "📊 Bot PID: $(ps aux | grep '[b]ot.py' | awk '{print $2}')"
    echo ""
    echo "📋 MONITORING COMMANDS:"
    echo "   tail -f bot_output.log    # Watch bot activity"
    echo "   tail -f trade_log.csv     # Watch trades"
    echo "   ps aux | grep bot.py      # Check bot status"
    echo ""
    echo "🎯 EXPECTED CHANGES:"
    echo "   • 2-3x more trade signals"
    echo "   • 45% position sizes (vs 35%)"
    echo "   • 3min cooldowns (vs 5min)"
    echo "   • 55% confidence threshold (vs 70%)"
else
    echo "❌ Bot failed to start. Check bot_output.log for errors."
fi
