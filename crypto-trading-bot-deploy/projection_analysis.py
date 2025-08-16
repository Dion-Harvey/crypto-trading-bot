#!/usr/bin/env python3
"""
Crypto Bot Daily Gain Projections Analysis
Based on current configuration and market conditions
"""

print("📊 CRYPTO BOT DAILY GAIN PROJECTIONS")
print("="*60)
print()

# Bot Configuration Analysis from enhanced_config.json
position_size = 25  # USD per trade
portfolio_value = 51.14  # Current portfolio value 
stop_loss = 0.03  # 3%
take_profit = 0.08  # 8%
daily_limit = 5.0  # USD
trade_cooldown = 15  # minutes
confidence_threshold = 0.70  # 70%

print("🤖 Current Bot Configuration:")
print(f"• Portfolio Value: ${portfolio_value:.2f}")
print(f"• Position Size: ${position_size} per trade ({position_size/portfolio_value*100:.1f}% of portfolio)")
print(f"• Stop Loss: {stop_loss*100:.1f}%")
print(f"• Take Profit: {take_profit*100:.1f}%")
print(f"• Risk/Reward Ratio: 1:{take_profit/stop_loss:.1f}")
print(f"• Daily Loss Limit: ${daily_limit}")
print(f"• Confidence Threshold: {confidence_threshold*100:.0f}%")
print()

print("📈 DAILY GAIN PROJECTIONS:")
print()

# Scenario 1: Conservative (Current bot behavior)
print("🔹 CONSERVATIVE Scenario (Current behavior):")
conservative_trades = 1.5  # Based on current cautious behavior
conservative_win_rate = 0.65
conservative_gain = conservative_trades * (conservative_win_rate * take_profit - (1-conservative_win_rate) * stop_loss) * position_size
conservative_pct = (conservative_gain / portfolio_value) * 100
print(f"   • Trades per day: {conservative_trades:.1f}")
print(f"   • Win rate: {conservative_win_rate*100:.0f}%")
print(f"   • Expected daily gain: ${conservative_gain:.2f}")
print(f"   • Daily return: {conservative_pct:+.2f}%")
print()

# Scenario 2: Moderate Volatility
print("🔸 MODERATE Scenario (Normal volatility):")
moderate_trades = 3
moderate_win_rate = 0.60
moderate_gain = moderate_trades * (moderate_win_rate * take_profit - (1-moderate_win_rate) * stop_loss) * position_size
moderate_pct = (moderate_gain / portfolio_value) * 100
print(f"   • Trades per day: {moderate_trades}")
print(f"   • Win rate: {moderate_win_rate*100:.0f}%")
print(f"   • Expected daily gain: ${moderate_gain:.2f}")
print(f"   • Daily return: {moderate_pct:+.2f}%")
print()

# Scenario 3: High Volatility
print("🔶 AGGRESSIVE Scenario (High volatility days):")
aggressive_trades = 5
aggressive_win_rate = 0.55
aggressive_gain = aggressive_trades * (aggressive_win_rate * take_profit - (1-aggressive_win_rate) * stop_loss) * position_size
aggressive_pct = (aggressive_gain / portfolio_value) * 100
print(f"   • Trades per day: {aggressive_trades}")
print(f"   • Win rate: {aggressive_win_rate*100:.0f}%")
print(f"   • Expected daily gain: ${aggressive_gain:.2f}")
print(f"   • Daily return: {aggressive_pct:+.2f}%")
print()

print("📊 RANGE OF EXPECTED DAILY RETURNS:")
print(f"• Conservative: {conservative_pct:+.2f}% per day")
print(f"• Moderate: {moderate_pct:+.2f}% per day") 
print(f"• Aggressive: {aggressive_pct:+.2f}% per day")
print()

print("⚠️ RISK FACTORS:")
print(f"• Daily loss cap: ${daily_limit} ({daily_limit/portfolio_value*100:.1f}% of portfolio)")
print(f"• Max single trade loss: ${position_size * stop_loss:.2f}")
print(f"• Bot is currently very conservative (waiting for high-confidence signals)")
print()

print("🎯 REALISTIC EXPECTATIONS:")
print("Based on current market conditions and bot behavior:")
print(f"• Most likely daily return: {conservative_pct:+.1f}% to {moderate_pct:+.1f}%")
print(f"• Range: ${conservative_gain:.2f} to ${moderate_gain:.2f} per day")
print("• Bot prioritizes capital preservation over aggressive gains")
print("• Performance will vary significantly based on market volatility")
