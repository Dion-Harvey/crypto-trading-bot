#!/usr/bin/env python3
import json

# Load config
with open('enhanced_config.json', 'r') as f:
    config = json.load(f)

# Apply optimizations
config['strategy_parameters']['confidence_threshold'] = 0.45
config['trading']['trade_cooldown_seconds'] = 90

# Save config  
with open('enhanced_config.json', 'w') as f:
    json.dump(config, f, indent=2)

print("✅ Configuration optimized:")
print(f"   - Confidence threshold: 0.55 → 0.45")
print(f"   - Trade cooldown: 180s → 90s")
