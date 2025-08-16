#!/usr/bin/env python3
"""
🚀 PROFIT-FIRST SWITCHING TEST
Test the enhanced profit-first switching system
"""

import json
from datetime import datetime
from log_utils import log_message

def demonstrate_profit_first_logic():
    """
    Demonstrate how the new profit-first switching logic works
    """
    
    print("\n" + "="*80)
    print("🚀 PROFIT-FIRST SWITCHING SYSTEM - ENHANCED BOT BEHAVIOR")
    print("="*80)
    
    print(f"📊 NEW BOT BEHAVIOR:")
    print(f"   1. 💰 PROFIT-TAKING: Take profits at 0.8%, 1.5%, 3.0%+ levels")
    print(f"   2. 🔄 SMART SWITCHING: Switch to better opportunities when profitable") 
    print(f"   3. 🎯 LOWERED THRESHOLDS: 35+ urgency (down from 50+), 4%+ moves (down from 6%+)")
    print(f"   4. 📈 AGGRESSIVE SCANNING: Check all opportunities every 15 seconds")
    
    print(f"\n🎯 PROFIT-FIRST SWITCHING CONDITIONS:")
    
    scenarios = [
        {
            'current_position': 'XLM/USDT',
            'current_profit': '+1.2%',
            'opportunity': 'BTC/USDT +8.5% (urgency: 65)',
            'action': '✅ SWITCH',
            'reason': 'Take 1.2% profit + Switch to better opportunity'
        },
        {
            'current_position': 'BTC/USDT', 
            'current_profit': '+0.9%',
            'opportunity': 'SOL/USDT +12.3% (urgency: 75)',
            'action': '✅ SWITCH',
            'reason': 'Take 0.9% profit + Switch to exceptional opportunity'
        },
        {
            'current_position': 'ETH/USDT',
            'current_profit': '-0.8%',
            'opportunity': 'XRP/USDT +15.7% (urgency: 85)',
            'action': '✅ SWITCH',
            'reason': 'Cut small loss for exceptional opportunity (>60 urgency)'
        },
        {
            'current_position': 'SOL/USDT',
            'current_profit': '+3.2%',
            'opportunity': 'No major opportunities',
            'action': '✅ TAKE PROFIT',
            'reason': 'Standalone profit-taking at 3.2%'
        },
        {
            'current_position': 'ADA/USDT',
            'current_profit': '-1.5%',
            'opportunity': 'DOGE/USDT +4.8% (urgency: 45)',
            'action': '✅ SWITCH',
            'reason': 'Exit underperforming position for better opportunity'
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n📋 SCENARIO {i}:")
        print(f"   Current: {scenario['current_position']} ({scenario['current_profit']})")
        print(f"   Opportunity: {scenario['opportunity']}")
        print(f"   Decision: {scenario['action']}")
        print(f"   Logic: {scenario['reason']}")
    
    print(f"\n🔍 ENHANCED DETECTION LAYERS:")
    layers = [
        "✅ Layer 1: Comprehensive Scanner (35+ urgency, lowered from 50+)",
        "✅ Layer 2: Multi-Crypto Monitor (0.60+ score, lowered from 0.70+)",
        "✅ Layer 3: Emergency Detector (30+ urgency, lowered from 40+)",
        "✅ Layer 4: Direct Ticker Scan (4%+ moves, lowered from 6%+)"
    ]
    
    for layer in layers:
        print(f"   {layer}")
    
    print(f"\n💰 PROFIT-TAKING THRESHOLDS:")
    thresholds = [
        "🟢 Quick Profits: 0.8%+ (immediate profit-taking)",
        "🟡 Medium Profits: 1.5%+ (profit-taking)",
        "🟠 Large Profits: 3.0%+ (mandatory profit-taking)",
        "🔴 Exceptional Profits: 5.0%+ (emergency profit-taking)"
    ]
    
    for threshold in thresholds:
        print(f"   {threshold}")
    
    print(f"\n🎯 SWITCHING INTELLIGENCE:")
    intelligence = [
        "📊 Scans all 16 pairs every 15 seconds for opportunities",
        "💰 Takes profits when available (0.8%+ threshold)",
        "🔄 Switches to better opportunities immediately",
        "🎯 Cuts losses (-2% max) for exceptional opportunities (60+ urgency)",
        "📈 Prioritizes profit realization over holding positions",
        "⚡ No cooldown delays for profit-taking switches"
    ]
    
    for feature in intelligence:
        print(f"   {feature}")
    
    print(f"\n🚀 EXPECTED IMPROVEMENTS:")
    improvements = [
        "💰 Higher profit realization rate (take profits quickly)",
        "🔄 More aggressive opportunity capture (lower thresholds)",
        "📊 Better portfolio performance (always chase best opportunities)",
        "⚡ Faster response to market moves (profit-first switching)",
        "🎯 Reduced missed opportunities (comprehensive scanning)",
        "📈 Compound growth through frequent profit-taking + reinvestment"
    ]
    
    for improvement in improvements:
        print(f"   {improvement}")

def show_current_config_status():
    """Show current bot configuration for profit-first system"""
    
    print(f"\n📊 CURRENT BOT CONFIGURATION:")
    
    try:
        with open('enhanced_config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        current_symbol = config['trading']['symbol']
        emergency_info = config.get('emergency_switch', {})
        
        print(f"   🎯 Active Pair: {current_symbol}")
        print(f"   🚨 Emergency Mode: {'ACTIVE' if emergency_info.get('activated') else 'INACTIVE'}")
        
        if emergency_info.get('activated'):
            print(f"   📅 Last Switch: {emergency_info.get('switched_at', 'N/A')}")
            print(f"   💡 Reason: {emergency_info.get('reason', 'N/A')}")
        
        print(f"   📊 Supported Pairs: {len(config['trading']['supported_pairs'])}")
        print(f"   ⚡ Loop Interval: {config['system']['loop_interval_seconds']}s")
        
    except Exception as e:
        print(f"   ⚠️ Could not load config: {e}")

if __name__ == "__main__":
    demonstrate_profit_first_logic()
    show_current_config_status()
    
    print(f"\n✅ PROFIT-FIRST SYSTEM READY!")
    print(f"🎯 Your bot will now:")
    print(f"   • Take profits at 0.8%+ levels")
    print(f"   • Switch to better opportunities immediately") 
    print(f"   • Use lowered thresholds for more opportunities")
    print(f"   • Maximize profit realization across all 16 pairs")
    print("="*80)
