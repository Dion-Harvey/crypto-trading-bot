#!/usr/bin/env python3
"""
Comprehensive Bot Diagnostic Test
"""

import json
import os
import sys

def run_diagnostic():
    print("🔧 CRYPTO TRADING BOT DIAGNOSTIC")
    print("=" * 60)
    
    # 1. Configuration Analysis
    print("\n📋 1. CONFIGURATION ANALYSIS:")
    try:
        with open('enhanced_config.json', 'r') as f:
            config = json.load(f)
        
        print("✅ Enhanced config loaded successfully")
        
        # Key trading parameters
        trading = config['trading']
        print(f"   Trading pair: {trading['symbol']}")
        print(f"   Position sizing mode: {trading['position_sizing_mode']}")
        print(f"   Base position: {trading['base_position_pct']*100:.1f}%")
        print(f"   Trade cooldown: {trading['trade_cooldown_seconds']/60:.1f} minutes")
        
        # Risk management
        risk = config['risk_management']
        print(f"   Stop Loss: {risk['stop_loss_pct']*100:.1f}%")
        print(f"   Take Profit: {risk['take_profit_pct']*100:.1f}%")
        print(f"   Trailing Stops: {risk['trailing_stop_enabled']}")
        print(f"   Partial Exits: {risk['partial_exit_enabled']}")
        print(f"   Min Hold Time: {risk['minimum_hold_time_minutes']} minutes")
        
        # Strategy parameters
        strategy = config['strategy_parameters']
        print(f"   Confidence threshold: {strategy['confidence_threshold']*100:.0f}%")
        print(f"   Min consensus votes: {strategy['min_consensus_votes']}")
        
        # Market filters
        filters = config['market_filters']
        print(f"   MA trend filter: {filters['ma_trend_filter_enabled']}")
        print(f"   RSI range filter: {filters['rsi_range_filter']['enabled']}")
        print(f"   Multi-timeframe required: {filters['multi_timeframe_required']}")
        
        # Position sizing features
        pos_sizing = config['position_sizing']
        print(f"   Confidence scaling: {pos_sizing['confidence_scaling']['enabled']}")
        print(f"   Risk-based sizing: {pos_sizing['risk_based_sizing']['enabled']}")
        print(f"   Compounding: {pos_sizing['risk_based_sizing']['compounding_enabled']}")
        
    except Exception as e:
        print(f"❌ Config error: {e}")
        return False

    # 2. Check bot state
    print("\n💾 2. BOT STATE ANALYSIS:")
    if os.path.exists('bot_state.json'):
        try:
            with open('bot_state.json', 'r') as f:
                state = json.load(f)
            print("✅ Bot state file found")
            print(f"   Currently holding: {state['trading_state']['holding_position']}")
            print(f"   Consecutive losses: {state['trading_state']['consecutive_losses']}")
            print(f"   Peak account value: ${state['risk_management']['account_peak_value']}")
            print(f"   Last updated: {state['bot_info']['last_updated']}")
        except Exception as e:
            print(f"❌ Bot state error: {e}")
    else:
        print("⚠️  No bot state file found (new bot)")

    # 3. Check trade log
    print("\n📊 3. TRADE LOG ANALYSIS:")
    if os.path.exists('trade_log.csv'):
        try:
            with open('trade_log.csv', 'r') as f:
                lines = f.readlines()
            print("✅ Trade log found")
            print(f"   Total trades logged: {len(lines)-1}")  # -1 for header
        except Exception as e:
            print(f"❌ Trade log error: {e}")
    else:
        print("⚠️  No trade log found")

    # 4. Check API config
    print("\n🔑 4. API CONFIGURATION:")
    if os.path.exists('config.json'):
        try:
            with open('config.json', 'r') as f:
                api_config = json.load(f)
            if api_config.get('binance_api_key') and api_config.get('binance_api_secret'):
                print("✅ API credentials configured")
            else:
                print("❌ API credentials missing")
        except Exception as e:
            print(f"❌ API config error: {e}")
    else:
        print("❌ config.json not found")

    # 5. Success Rate Enhancement Check
    print("\n🎯 5. SUCCESS RATE ENHANCEMENTS:")
    if os.path.exists('success_rate_enhancer.py'):
        print("✅ Success rate enhancer module found")
    else:
        print("❌ Success rate enhancer module missing")
    
    # 6. Strategy Module Check
    print("\n🧠 6. STRATEGY MODULES:")
    modules = ['enhanced_multi_strategy.py', 'momentum_enhancer.py', 'institutional_strategies.py']
    for module in modules:
        if os.path.exists(module):
            print(f"✅ {module} found")
        else:
            print(f"❌ {module} missing")

    print("\n" + "="*60)
    print("🚀 DIAGNOSTIC COMPLETE")
    print("="*60)
    
    return True

if __name__ == "__main__":
    run_diagnostic()
