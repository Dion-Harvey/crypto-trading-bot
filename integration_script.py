#!/usr/bin/env python3

"""
Integration script to add Phase 2 Intelligence and Native Trailing Stops to the main bot
This script will modify the existing bot.py to include both systems
"""

import re
import os
from datetime import datetime

def integrate_phase2_and_trailing():
    """Integrate Phase 2 APIs and Native Trailing Stops into bot.py"""
    
    # Read the current bot.py
    with open('/home/ubuntu/crypto-trading-bot-deploy/bot.py', 'r') as f:
        bot_content = f.read()
    
    # Check if already integrated
    if 'free_phase2_api' in bot_content:
        print("✅ Phase 2 already integrated")
        return False
        
    if 'binance_native_trailing' in bot_content:
        print("✅ Native trailing already integrated")
        return False
    
    # Find import section
    import_section = []
    lines = bot_content.split('\n')
    
    # Add new imports after existing imports
    for i, line in enumerate(lines):
        if line.startswith('import ') or line.startswith('from '):
            continue
        else:
            # Found end of imports, insert our imports
            integration_imports = [
                "",
                "# =============================================================================",
                "# PHASE 2 & NATIVE TRAILING INTEGRATION",
                "# =============================================================================",
                "try:",
                "    from free_phase2_api import FreePhase2Provider",
                "    from binance_native_trailing import place_binance_trailing_stop_order",
                "    from binance_native_trailing_integration import update_bot_config, place_enhanced_order_with_native_trailing",
                "    PHASE2_AVAILABLE = True",
                "    NATIVE_TRAILING_AVAILABLE = True",
                "    print('✅ Phase 2 Intelligence & Native Trailing Stops loaded')",
                "except ImportError as e:",
                "    print(f'⚠️ Integration modules not available: {e}')",
                "    PHASE2_AVAILABLE = False",
                "    NATIVE_TRAILING_AVAILABLE = False",
                ""
            ]
            
            # Insert the imports
            for j, import_line in enumerate(integration_imports):
                lines.insert(i + j, import_line)
            break
    
    # Join lines back
    integrated_content = '\n'.join(lines)
    
    # Add initialization after main bot initialization
    init_code = '''
    # Initialize Phase 2 Intelligence
    if PHASE2_AVAILABLE:
        try:
            self.phase2_provider = FreePhase2Provider()
            self.log_trade("✅ Phase 2 Intelligence initialized (4 APIs, $0 cost)")
        except Exception as e:
            self.log_trade(f"⚠️ Phase 2 initialization failed: {e}")
            self.phase2_provider = None
    else:
        self.phase2_provider = None
        
    # Initialize Native Trailing Configuration
    if NATIVE_TRAILING_AVAILABLE:
        try:
            self.native_trailing_config = update_bot_config()
            if self.native_trailing_config.get('binance_native_trailing', {}).get('enabled', False):
                self.log_trade("✅ Native Trailing Stops enabled (0.5% distance)")
            else:
                self.log_trade("⚠️ Native Trailing Stops disabled in config")
        except Exception as e:
            self.log_trade(f"⚠️ Native trailing config failed: {e}")
            self.native_trailing_config = None
    else:
        self.native_trailing_config = None
'''
    
    # Find the __init__ method and add our initialization
    init_pattern = r'(def __init__\(self[^)]*\):.*?)(def|\Z)'
    
    def add_init_code(match):
        init_method = match.group(1)
        next_def = match.group(2) if match.group(2) else ''
        
        # Add our initialization before the next method
        return init_method + init_code + '\n    ' + next_def
    
    integrated_content = re.sub(init_pattern, add_init_code, integrated_content, flags=re.DOTALL)
    
    # Write the integrated bot
    with open('/home/ubuntu/crypto-trading-bot-deploy/bot_integrated.py', 'w') as f:
        f.write(integrated_content)
    
    print("✅ Integration complete - created bot_integrated.py")
    return True

if __name__ == "__main__":
    print("🔧 Starting Phase 2 & Native Trailing Integration...")
    success = integrate_phase2_and_trailing()
    if success:
        print("🎉 Integration ready for testing!")
    else:
        print("ℹ️ Integration already exists or skipped")
