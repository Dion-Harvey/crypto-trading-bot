#!/usr/bin/env python3
import json

print("Testing configuration load...")

try:
    with open('enhanced_config.json', 'r') as f:
        config = json.load(f)
    print("✅ Configuration is valid JSON")
    
    # Test new emergency protection settings
    emergency_protection = config.get('emergency_protection', {})
    print(f"🛡️ Spike protection: {emergency_protection.get('spike_chasing_protection', False)}")
    print(f"📊 Max spike threshold: {emergency_protection.get('max_spike_threshold_pct', 0)}%")
    
    # Test stop-loss reserve settings
    stop_loss_reserve = config.get('stop_loss_reserve', {})
    print(f"💰 Stop-loss reserve: {stop_loss_reserve.get('enabled', False)}")
    print(f"📈 Reserve percentage: {stop_loss_reserve.get('reserve_percentage', 0):.1%}")
    
    print("\n🎯 Configuration test completed successfully!")
    
except json.JSONDecodeError as e:
    print(f"❌ JSON error: {e}")
except Exception as e:
    print(f"❌ Configuration error: {e}")
