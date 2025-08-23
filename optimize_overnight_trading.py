#!/usr/bin/env python3
"""
Overnight Trading Optimization
Configure bot for maximum overnight spike detection and profit capture
"""

import json
import os
from datetime import datetime

def optimize_for_overnight_trading():
    """Optimize bot configuration for overnight trading"""
    
    print("🌙 OVERNIGHT TRADING OPTIMIZATION")
    print("=" * 50)
    
    # Read current enhanced config
    with open('enhanced_config.json', 'r') as f:
        config = json.load(f)
    
    # 🚀 OVERNIGHT OPTIMIZATIONS
    
    # 1. Enhanced Spike Detection - More aggressive for overnight moves
    if 'price_jump_detection' not in config:
        config['price_jump_detection'] = {}
    
    spike_config = config['price_jump_detection']
    spike_config.update({
        # Lower thresholds to catch smaller moves
        'spike_threshold': 0.008,  # 0.8% (was likely higher)
        'short_trend_threshold': 0.015,  # 1.5%
        'medium_trend_threshold': 0.025,  # 2.5%
        'long_trend_threshold': 0.04,   # 4.0%
        
        # Faster detection for overnight volatility
        'spike_window_seconds': 300,     # 5 minutes
        'short_trend_window_seconds': 900,   # 15 minutes
        'medium_trend_window_seconds': 1800,  # 30 minutes
        
        # Enhanced urgency scoring
        'urgency_multiplier': 1.3,  # 30% more urgent
        'cooldown_override_threshold': 6.0  # Lower threshold for overrides
    })
    
    # 2. LSTM Enhanced for overnight
    if 'lstm_predictor' in config:
        config['lstm_predictor']['confidence_threshold'] = 0.65  # Lower threshold
        config['lstm_predictor']['enabled'] = True
    
    # 3. More aggressive position sizing for overnight opportunities
    if 'trading' not in config:
        config['trading'] = {}
        
    config['trading'].update({
        'base_amount_usd': 30,  # Slightly higher base
        'min_amount_usd': 25,   # Higher minimum
        'max_amount_usd': 50,   # Higher maximum for big moves
    })
    
    # 4. Reduced confidence thresholds for overnight
    if 'strategy_parameters' not in config:
        config['strategy_parameters'] = {}
        
    config['strategy_parameters'].update({
        'confidence_threshold': 0.40,  # Lower from 0.45
        'dip_confidence_reduction': 0.20,  # More aggressive dip buying
        'spike_confidence_boost': 0.25,    # Higher boost for spikes
    })
    
    # 5. Risk management optimized for overnight
    if 'risk_management' not in config:
        config['risk_management'] = {}
        
    config['risk_management'].update({
        'stop_loss_percentage': 0.025,  # 2.5% stop loss
        'take_profit_percentage': 0.015, # 1.5% take profit (quick)
        'trailing_stop_percentage': 0.003, # 0.3% trailing
        'minimum_hold_time_minutes': 10,  # Reduced hold time
        'max_position_time_hours': 8,     # Max 8 hours overnight
    })
    
    # 6. Enhanced multi-timeframe for overnight
    if 'multi_timeframe' not in config:
        config['multi_timeframe'] = {}
        
    config['multi_timeframe'].update({
        'priority_boost': 0.20,           # 20% boost for multi-timeframe
        'agreement_threshold': 0.70,      # Lower agreement needed
        'timeframe_weights': {
            '1m': 0.35,   # Higher weight on short-term
            '5m': 0.30,   # Balanced
            '15m': 0.25,  # Medium term
            '1h': 0.10    # Lower weight for overnight
        }
    })
    
    # Backup current config
    backup_filename = f"enhanced_config_backup_overnight_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(backup_filename, 'w') as f:
        json.dump(config, f, indent=2)
    
    # Save optimized config
    with open('enhanced_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✅ OVERNIGHT OPTIMIZATIONS APPLIED:")
    print(f"   🚀 Spike Detection: More sensitive (0.8% threshold)")
    print(f"   🧠 LSTM: Enabled with 65% confidence threshold")
    print(f"   💰 Position Size: $25-50 range")
    print(f"   🎯 Confidence: Lowered to 40% for more opportunities")
    print(f"   🛡️ Risk: 2.5% stop, 1.5% profit, 10min hold time")
    print(f"   📊 Multi-timeframe: Enhanced short-term focus")
    print(f"   💾 Backup saved: {backup_filename}")
    print()
    
    return True

if __name__ == "__main__":
    optimize_for_overnight_trading()
    print("🌙 Ready for overnight trading! Sleep well! 😴")
