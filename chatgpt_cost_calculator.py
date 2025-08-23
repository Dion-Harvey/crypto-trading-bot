#!/usr/bin/env python3
"""
CHATGPT API COST CALCULATOR
Accurate cost estimation for crypto trading bot integration
"""

import json
from datetime import datetime, timedelta

# Current ChatGPT API pricing (as of 2024-2025)
CHATGPT_PRICING = {
    'gpt-4o': {
        'input_per_1m_tokens': 2.50,   # $2.50 per 1M input tokens
        'output_per_1m_tokens': 10.00  # $10.00 per 1M output tokens
    },
    'gpt-4o-mini': {
        'input_per_1m_tokens': 0.15,   # $0.15 per 1M input tokens  
        'output_per_1m_tokens': 0.60   # $0.60 per 1M output tokens
    },
    'gpt-3.5-turbo': {
        'input_per_1m_tokens': 0.50,   # $0.50 per 1M input tokens
        'output_per_1m_tokens': 1.50   # $1.50 per 1M output tokens
    }
}

def load_bot_config():
    """Load bot configuration to understand usage patterns"""
    try:
        with open('enhanced_config.json', 'r') as f:
            return json.load(f)
    except:
        return {}

def calculate_trading_frequency(config):
    """Estimate how often the bot makes trading decisions"""
    # Bot runs every 15 seconds in HFT mode
    cycles_per_hour = 60 * 60 / 15  # 240 cycles per hour
    cycles_per_day = cycles_per_hour * 24  # 5,760 cycles per day
    
    # Not every cycle triggers ChatGPT - only when making trading decisions
    # Based on logs, bot makes 1-5 trades per day typically
    chatgpt_calls_per_day = 50  # Conservative estimate including analysis calls
    
    return {
        'cycles_per_day': cycles_per_day,
        'chatgpt_calls_per_day': chatgpt_calls_per_day,
        'chatgpt_calls_per_month': chatgpt_calls_per_day * 30
    }

def estimate_token_usage():
    """Estimate token usage per ChatGPT call"""
    
    # Input tokens per call (context we send to ChatGPT)
    input_tokens_per_call = {
        'market_data': 500,      # Price data, indicators, volume
        'technical_analysis': 300, # RSI, MACD, MA crossovers
        'portfolio_context': 200,  # Current positions, P&L
        'risk_parameters': 100,   # Stop-loss, take-profit settings
        'prompt_instructions': 400, # Trading strategy instructions
        'total_per_call': 1500    # Total input tokens per call
    }
    
    # Output tokens per call (ChatGPT's response)
    output_tokens_per_call = {
        'analysis': 300,         # Technical analysis explanation
        'recommendation': 100,   # BUY/SELL/HOLD recommendation
        'reasoning': 200,        # Why this decision was made
        'risk_assessment': 100,  # Risk level and concerns
        'key_levels': 100,       # Support/resistance levels
        'total_per_call': 800    # Total output tokens per call
    }
    
    return input_tokens_per_call, output_tokens_per_call

def calculate_monthly_costs():
    """Calculate accurate monthly costs for different ChatGPT models"""
    
    config = load_bot_config()
    frequency = calculate_trading_frequency(config)
    input_tokens, output_tokens = estimate_token_usage()
    
    monthly_calls = frequency['chatgpt_calls_per_month']
    monthly_input_tokens = monthly_calls * input_tokens['total_per_call']
    monthly_output_tokens = monthly_calls * output_tokens['total_per_call']
    
    print("=" * 70)
    print("🤖 CHATGPT API COST ANALYSIS FOR CRYPTO TRADING BOT")
    print("=" * 70)
    
    print(f"\n📊 USAGE ESTIMATES:")
    print(f"   🔄 API Calls per Day: {frequency['chatgpt_calls_per_day']}")
    print(f"   📅 API Calls per Month: {monthly_calls:,}")
    print(f"   📝 Input Tokens per Month: {monthly_input_tokens:,}")
    print(f"   💬 Output Tokens per Month: {monthly_output_tokens:,}")
    
    print(f"\n💰 MONTHLY COST BREAKDOWN:")
    print("-" * 50)
    
    for model_name, pricing in CHATGPT_PRICING.items():
        input_cost = (monthly_input_tokens / 1_000_000) * pricing['input_per_1m_tokens']
        output_cost = (monthly_output_tokens / 1_000_000) * pricing['output_per_1m_tokens']
        total_cost = input_cost + output_cost
        
        print(f"\n🧠 {model_name.upper()}:")
        print(f"   📥 Input Cost: ${input_cost:.2f}")
        print(f"   📤 Output Cost: ${output_cost:.2f}")
        print(f"   💵 Total Monthly: ${total_cost:.2f}")
        
        # Annual cost
        annual_cost = total_cost * 12
        print(f"   📅 Annual Cost: ${annual_cost:.2f}")
        
        # Cost per trade (assuming 50 trades/month)
        cost_per_trade = total_cost / 50
        print(f"   📊 Cost per Trade: ${cost_per_trade:.3f}")
    
    print(f"\n🔍 COMPARISON WITH CURRENT SETUP:")
    print(f"   🚀 Gemini AI Current: $0.18/month")
    print(f"   💎 ChatGPT 4o-mini: ${(monthly_input_tokens / 1_000_000) * 0.15 + (monthly_output_tokens / 1_000_000) * 0.60:.2f}/month")
    print(f"   📈 Cost Increase: {((monthly_input_tokens / 1_000_000) * 0.15 + (monthly_output_tokens / 1_000_000) * 0.60) / 0.18:.1f}x")
    
    print(f"\n🎯 RECOMMENDATIONS:")
    gpt4o_mini_cost = (monthly_input_tokens / 1_000_000) * 0.15 + (monthly_output_tokens / 1_000_000) * 0.60
    
    if gpt4o_mini_cost < 10:
        print("   ✅ GPT-4o-mini: RECOMMENDED - Good balance of cost/performance")
    if gpt4o_mini_cost > 25:
        print("   ⚠️ Consider reducing API calls or using Gemini AI primarily")
    
    print(f"\n💡 COST OPTIMIZATION STRATEGIES:")
    print("   1. Use ChatGPT only for complex decisions (>$50 trades)")
    print("   2. Cache responses for similar market conditions")
    print("   3. Combine with Gemini AI (use ChatGPT for critical decisions)")
    print("   4. Implement daily spend limits")
    
    return {
        'monthly_calls': monthly_calls,
        'gpt4o_mini_monthly': gpt4o_mini_cost,
        'gpt4o_monthly': (monthly_input_tokens / 1_000_000) * 2.50 + (monthly_output_tokens / 1_000_000) * 10.00,
        'current_gemini': 0.18
    }

if __name__ == "__main__":
    costs = calculate_monthly_costs()
    
    print(f"\n" + "=" * 70)
    print("📋 EXECUTIVE SUMMARY")
    print("=" * 70)
    print(f"🏆 BEST OPTION: GPT-4o-mini at ${costs['gpt4o_mini_monthly']:.2f}/month")
    print(f"💎 PREMIUM OPTION: GPT-4o at ${costs['gpt4o_monthly']:.2f}/month") 
    print(f"🔄 CURRENT: Gemini AI at ${costs['current_gemini']:.2f}/month")
    
    roi_needed = costs['gpt4o_mini_monthly'] / costs['current_gemini']
    print(f"\n📈 ROI NEEDED: {roi_needed:.1f}x improvement to justify ChatGPT upgrade")
    print("💡 RECOMMENDATION: Start with Gemini AI, upgrade if profit > $50/month")
