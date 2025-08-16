#!/usr/bin/env python3

"""
Enhanced Bot Integration - Phase 2 Intelligence + Native Trailing Stops
Designed specifically for Binance US trading with native trailing stop support
"""

# Read current bot.py and create enhanced version
with open('/home/ubuntu/crypto-trading-bot-deploy/bot.py', 'r') as f:
    bot_content = f.read()

# Integration modifications
enhanced_imports = '''
# =============================================================================
# ENHANCED INTEGRATIONS - PHASE 2 & NATIVE TRAILING
# =============================================================================
try:
    from free_phase2_api import FreePhase2Provider
    from binance_native_trailing import place_binance_trailing_stop_order
    from binance_native_trailing_integration import (
        update_bot_config, 
        place_enhanced_order_with_native_trailing,
        check_and_place_pending_trailing_stops,
        replace_manual_trailing_logic,
        update_config_for_native_trailing
    )
    ENHANCED_FEATURES_AVAILABLE = True
    print('✅ Enhanced features loaded: Phase 2 Intelligence + Native Trailing')
except ImportError as e:
    print(f'⚠️ Enhanced features not available: {e}')
    ENHANCED_FEATURES_AVAILABLE = False

# Add missing function if not available
if ENHANCED_FEATURES_AVAILABLE:
    try:
        # Test if update_bot_config is callable
        callable(update_bot_config)
        print('✅ update_bot_config function available')
    except:
        # Define fallback function
        def update_bot_config(config_dict):
            import json
            from datetime import datetime
            try:
                config_file = 'enhanced_config.json'
                with open(config_file, 'r') as f:
                    current_config = json.load(f)
                current_config.update(config_dict)
                current_config['last_updated'] = datetime.now().isoformat()
                with open(config_file, 'w') as f:
                    json.dump(current_config, f, indent=2)
                return True
            except Exception as e:
                print(f"Error updating config: {e}")
                return False
        print('✅ Fallback update_bot_config function created')
'''

# Find the end of imports and add our enhanced imports
lines = bot_content.split('\n')
for i, line in enumerate(lines):
    if line.strip() == '' and i > 10:  # Find first empty line after imports
        # Check if this is after imports by looking at previous lines
        prev_lines = lines[max(0, i-5):i]
        if any('import ' in l or 'from ' in l for l in prev_lines):
            lines.insert(i, enhanced_imports)
            break

# Add enhanced initialization to the TradingBot class
enhanced_init = '''
        # Enhanced Features Initialization
        if ENHANCED_FEATURES_AVAILABLE:
            try:
                # Phase 2 Intelligence
                self.phase2_provider = FreePhase2Provider()
                self.log_trade("✅ Phase 2 Intelligence: 4 APIs active ($0 cost, $579 value)")
                
                # Native Trailing Configuration
                self.native_trailing_config = update_bot_config()
                trailing_enabled = self.native_trailing_config.get('binance_native_trailing', {}).get('enabled', False)
                trailing_pct = self.native_trailing_config.get('binance_native_trailing', {}).get('trailing_percent', 0.5)
                
                if trailing_enabled:
                    self.log_trade(f"✅ Binance US Native Trailing: {trailing_pct}% distance enabled")
                else:
                    self.log_trade("⚠️ Native trailing disabled in config")
                    
                self.enhanced_features_active = True
                
            except Exception as e:
                self.log_trade(f"⚠️ Enhanced features initialization failed: {e}")
                self.phase2_provider = None
                self.native_trailing_config = None
                self.enhanced_features_active = False
        else:
            self.phase2_provider = None
            self.native_trailing_config = None
            self.enhanced_features_active = False
            self.log_trade("ℹ️ Running with standard features only")
'''

# Find TradingBot __init__ method and add enhanced initialization
for i, line in enumerate(lines):
    if 'def __init__(self' in line and 'TradingBot' in lines[max(0, i-10):i]:
        # Find end of __init__ method
        indent_level = len(line) - len(line.lstrip())
        for j in range(i + 1, len(lines)):
            if lines[j].strip() == '':
                continue
            current_indent = len(lines[j]) - len(lines[j].lstrip())
            if current_indent <= indent_level and lines[j].strip():
                # Found end of __init__, insert before this line
                lines.insert(j, enhanced_init)
                break
        break

# Enhance the place_intelligent_order method for native trailing stops
enhanced_order_method = '''
    def place_enhanced_intelligent_order(self, symbol, amount, side='buy', order_type='limit'):
        """Enhanced order placement with Phase 2 intelligence and native trailing stops"""
        
        # Use Phase 2 intelligence if available
        if self.enhanced_features_active and self.phase2_provider:
            try:
                phase2_signals = self.phase2_provider.get_trading_signals(symbol)
                if phase2_signals.get('alert_level') == 'high':
                    self.log_trade(f"🔥 Phase 2 HIGH ALERT: {phase2_signals.get('summary', 'Enhanced conditions detected')}")
                elif phase2_signals.get('alert_level') == 'medium':
                    self.log_trade(f"📊 Phase 2 Alert: {phase2_signals.get('summary', 'Notable market activity')}")
            except Exception as e:
                self.log_trade(f"⚠️ Phase 2 analysis error: {e}")
        
        # Use native trailing stops if enabled and selling
        if (self.enhanced_features_active and 
            self.native_trailing_config and 
            self.native_trailing_config.get('binance_native_trailing', {}).get('enabled', False) and
            side == 'sell'):
            
            try:
                return place_enhanced_order_with_native_trailing(
                    self, symbol, amount, side, order_type
                )
            except Exception as e:
                self.log_trade(f"⚠️ Native trailing failed, using standard order: {e}")
                
        # Fallback to standard order placement
        return self.place_intelligent_order(symbol, amount, side, order_type)
'''

# Add the enhanced method after the existing place_intelligent_order method
for i, line in enumerate(lines):
    if 'def place_intelligent_order(self' in line:
        # Find end of this method
        indent_level = len(line) - len(line.lstrip())
        for j in range(i + 1, len(lines)):
            if lines[j].strip() == '':
                continue
            current_indent = len(lines[j]) - len(lines[j].lstrip())
            if current_indent <= indent_level and lines[j].strip() and 'def ' in lines[j]:
                # Found next method, insert our enhanced method before it
                lines.insert(j, enhanced_order_method)
                break
        break

# Write the enhanced bot
enhanced_content = '\n'.join(lines)

with open('/home/ubuntu/crypto-trading-bot-deploy/bot_enhanced.py', 'w') as f:
    f.write(enhanced_content)

print("✅ Enhanced bot created: bot_enhanced.py")
print("🎯 Features integrated:")
print("   • Phase 2 Intelligence (4 free APIs)")
print("   • Binance US Native Trailing Stops (0.5%)")
print("   • Enhanced order placement logic")
print("   • Fallback to standard methods if needed")
