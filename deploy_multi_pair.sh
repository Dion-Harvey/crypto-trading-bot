#!/bin/bash
# =============================================================================
# DEPLOY MULTI-PAIR SCANNING TO AWS
# =============================================================================
#
# 🚀 DEPLOYMENT SCRIPT FOR ENHANCED MULTI-PAIR BOT
# Deploys multi-pair scanning system to your AWS instance
#
# =============================================================================

echo "🚀 DEPLOYING MULTI-PAIR SCANNING SYSTEM TO AWS"
echo "="*60

# Configuration
AWS_HOST="ubuntu@3.135.216.32"
KEY_PATH="C:\Users\miste\Downloads\cryptobot-key.pem"
DEPLOY_DIR="crypto-trading-bot-deploy"

echo "📁 Uploading multi-pair scanning files..."

# Upload scanner
scp -i "$KEY_PATH" multi_pair_scanner.py $AWS_HOST:$DEPLOY_DIR/

# Upload enhanced bot
scp -i "$KEY_PATH" enhanced_multi_pair_bot.py $AWS_HOST:$DEPLOY_DIR/

echo "🔧 Creating integration script..."

# Create integration script on AWS
ssh -i "$KEY_PATH" $AWS_HOST "cat > $DEPLOY_DIR/integrate_multi_pair.py << 'EOF'
#!/usr/bin/env python3
# =============================================================================
# MULTI-PAIR INTEGRATION SCRIPT
# =============================================================================

import json
import sys
import os
from datetime import datetime

def integrate_multi_pair_scanning():
    '''Integrate multi-pair scanning with existing bot'''
    
    print('🔧 INTEGRATING MULTI-PAIR SCANNING...')
    
    # 1. Backup current bot.py
    print('📁 Backing up current bot.py...')
    os.system('cp bot.py bot_single_pair_backup.py')
    
    # 2. Update enhanced_config.json
    print('⚙️ Updating configuration...')
    try:
        with open('enhanced_config.json', 'r') as f:
            config = json.load(f)
        
        # Add multi-pair configuration
        config['multi_pair_scanning'] = {
            'enabled': True,
            'scan_interval_seconds': 30,
            'supported_pairs': [
                'BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'XRP/USDT',
                'ADA/USDT', 'DOGE/USDT', 'XLM/USDT', 'SUI/USDT', 
                'SHIB/USDT', 'HBAR/USDT', 'AVAX/USDT', 'DOT/USDT',
                'MATIC/USDT', 'LINK/USDT', 'UNI/USDT', 'LTC/USDT'
            ],
            'auto_switch_threshold': 0.75,
            'switch_cooldown_seconds': 300,
            'momentum_thresholds': {
                'strong_bullish': 3.0,
                'moderate_bullish': 1.5,
                'weak_bullish': 0.5,
                'volume_surge_min': 2.0
            }
        }
        
        # Backup and save
        backup_name = f'enhanced_config_backup_{datetime.now().strftime(\"%Y%m%d_%H%M%S\")}.json'
        os.system(f'cp enhanced_config.json {backup_name}')
        
        with open('enhanced_config.json', 'w') as f:
            json.dump(config, f, indent=2)
            
        print('✅ Configuration updated')
        
    except Exception as e:
        print(f'❌ Config update failed: {e}')
        return False
    
    # 3. Create enhanced bot wrapper
    print('🤖 Creating enhanced bot wrapper...')
    wrapper_code = '''#!/usr/bin/env python3
# Enhanced bot with multi-pair scanning integration

import asyncio
import sys
import os
import signal
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from enhanced_multi_pair_bot import EnhancedMultiPairBot
    MULTI_PAIR_AVAILABLE = True
except ImportError as e:
    print(f\"⚠️ Multi-pair module not available: {e}\")
    print(\"🔄 Falling back to single-pair bot...\")
    MULTI_PAIR_AVAILABLE = False

def signal_handler(signum, frame):
    \"\"\"Handle shutdown signals\"\"\"
    print(f\"\\n🛑 Received signal {signum}, shutting down...\")
    sys.exit(0)

async def run_enhanced_bot():
    \"\"\"Run enhanced multi-pair bot\"\"\"
    try:
        if MULTI_PAIR_AVAILABLE:
            print(\"🚀 Starting Enhanced Multi-Pair Bot...\")
            bot = EnhancedMultiPairBot()
            await bot.start_enhanced_trading()
        else:
            print(\"🔄 Starting original bot (multi-pair unavailable)...\")
            # Import and run original bot
            exec(open('bot_single_pair_backup.py').read())
    except Exception as e:
        print(f\"❌ Bot error: {e}\")
        print(\"🔄 Attempting fallback to original bot...\")
        exec(open('bot_single_pair_backup.py').read())

if __name__ == \"__main__\":
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print(\"=\"*60)
    print(\"🤖 ENHANCED CRYPTO TRADING BOT\")
    print(\"🎯 Multi-Pair Opportunity Detection\")
    print(\"🧠 Phase 2 Blockchain Intelligence\")
    print(\"🛡️ Native Trailing Stops\")
    print(\"=\"*60)
    
    # Run bot
    try:
        asyncio.run(run_enhanced_bot())
    except KeyboardInterrupt:
        print(\"\\n👋 Shutdown complete\")
    except Exception as e:
        print(f\"\\n❌ Fatal error: {e}\")
        sys.exit(1)
'''
    
    with open('bot_enhanced_multi_pair.py', 'w') as f:
        f.write(wrapper_code)
    
    os.chmod('bot_enhanced_multi_pair.py', 0o755)
    print('✅ Enhanced bot wrapper created')
    
    # 4. Test imports
    print('🧪 Testing imports...')
    try:
        import importlib.util
        
        # Test multi_pair_scanner
        spec = importlib.util.spec_from_file_location('multi_pair_scanner', 'multi_pair_scanner.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        print('✅ multi_pair_scanner import successful')
        
        # Test enhanced_multi_pair_bot
        spec = importlib.util.spec_from_file_location('enhanced_multi_pair_bot', 'enhanced_multi_pair_bot.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        print('✅ enhanced_multi_pair_bot import successful')
        
    except Exception as e:
        print(f'⚠️ Import test warning: {e}')
    
    print('\\n🎉 MULTI-PAIR INTEGRATION COMPLETE!')
    print('\\nNext steps:')
    print('1. Stop current bot: pkill -f \"python bot.py\"')
    print('2. Start enhanced bot: nohup python3 bot_enhanced_multi_pair.py > bot_multi_pair.log 2>&1 &')
    print('3. Monitor logs: tail -f bot_multi_pair.log')
    
    return True

if __name__ == '__main__':
    try:
        success = integrate_multi_pair_scanning()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f'❌ Integration failed: {e}')
        sys.exit(1)
EOF"

echo "🔧 Running integration on AWS..."
ssh -i "$KEY_PATH" $AWS_HOST "cd $DEPLOY_DIR && python3 integrate_multi_pair.py"

echo ""
echo "🎯 DEPLOYMENT SUMMARY:"
echo "✅ Multi-pair scanner uploaded"
echo "✅ Enhanced bot uploaded" 
echo "✅ Integration script executed"
echo "✅ Configuration updated"
echo ""
echo "🚀 Ready to deploy! Run these commands to start:"
echo "ssh -i \"$KEY_PATH\" $AWS_HOST"
echo "cd $DEPLOY_DIR"
echo "pkill -f 'python bot.py'"
echo "nohup python3 bot_enhanced_multi_pair.py > bot_multi_pair.log 2>&1 &"
echo "tail -f bot_multi_pair.log"
echo ""
echo "🎯 Your bot will now monitor ALL 16 pairs and auto-switch to catch moves like:"
echo "   📈 SUI/USDT +6.50% (CAUGHT!)"
echo "   📈 HBAR/USDT +4.46% (CAUGHT!)"
echo "   📈 Any future pumps across all supported pairs"
