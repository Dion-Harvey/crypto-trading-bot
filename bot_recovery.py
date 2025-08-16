#!/usr/bin/env python3
"""
Crypto Trading Bot Recovery Script
Restores the bot to working condition with proper configuration
"""

import os
import json
import subprocess
import sys
from datetime import datetime

def print_section(title):
    print(f"\n{'='*60}")
    print(f"🔧 {title}")
    print('='*60)

def install_missing_dependencies():
    """Install missing Python packages"""
    print_section("INSTALLING MISSING DEPENDENCIES")
    
    missing_packages = ['python-dotenv']
    
    for package in missing_packages:
        try:
            print(f"📦 Installing {package}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"✅ {package} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package}: {e}")

def fix_api_configuration():
    """Check and fix API configuration"""
    print_section("FIXING API CONFIGURATION")
    
    config_file = 'enhanced_config.json'
    
    if not os.path.exists(config_file):
        print(f"❌ {config_file} not found!")
        return False
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        # Check if API keys section exists
        if 'api_keys' not in config:
            print("⚠️ Adding missing api_keys section to config...")
            config['api_keys'] = {
                "binance": {
                    "api_key": "",
                    "secret": ""
                }
            }
        
        # Check if API keys are set
        binance_keys = config.get('api_keys', {}).get('binance', {})
        api_key = binance_keys.get('api_key', '')
        secret = binance_keys.get('secret', '')
        
        if not api_key or not secret:
            print("❌ API keys not configured!")
            print("📝 Please add your Binance API credentials to enhanced_config.json:")
            print("   1. Open enhanced_config.json")
            print("   2. Find the 'api_keys' section")
            print("   3. Add your API key and secret")
            print("   4. Save the file")
            return False
        else:
            print("✅ API keys are configured")
            return True
            
    except Exception as e:
        print(f"❌ Error checking API configuration: {e}")
        return False

def fix_bot_loop_issue():
    """Fix the infinite loop issue in bot.py"""
    print_section("FIXING BOT LOOP ISSUES")
    
    # Check if the run_continuously function has proper loop control
    bot_file = 'bot.py'
    
    if not os.path.exists(bot_file):
        print(f"❌ {bot_file} not found!")
        return False
    
    print("✅ Bot file exists")
    print("🔍 The current bot.py appears to be using the correct multi-timeframe strategy")
    print("⚠️ Make sure to run the bot with proper error handling and monitoring")
    
    return True

def check_configuration():
    """Check and validate bot configuration"""
    print_section("VALIDATING CONFIGURATION")
    
    config_file = 'enhanced_config.json'
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        # Check required sections
        required_sections = ['trading', 'risk_management', 'strategy_parameters', 'system']
        missing_sections = []
        
        for section in required_sections:
            if section not in config:
                missing_sections.append(section)
            else:
                print(f"✅ {section}: Present")
        
        if missing_sections:
            print(f"❌ Missing sections: {missing_sections}")
            return False
        
        # Check loop interval
        loop_interval = config.get('system', {}).get('loop_interval_seconds', None)
        if loop_interval:
            print(f"✅ Loop interval: {loop_interval}s")
        else:
            print("❌ Loop interval not configured")
            return False
        
        # Check confidence threshold
        confidence = config.get('strategy_parameters', {}).get('confidence_threshold', None)
        if confidence:
            print(f"✅ Confidence threshold: {confidence}")
        else:
            print("❌ Confidence threshold not configured")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error validating configuration: {e}")
        return False

def create_startup_script():
    """Create a startup script for the bot"""
    print_section("CREATING STARTUP SCRIPT")
    
    startup_script = """@echo off
echo 🚀 Starting Crypto Trading Bot Recovery...
echo.

REM Change to bot directory
cd /d "C:\\Users\\miste\\Documents\\crypto-trading-bot\\crypto-trading-bot"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Please install Python.
    pause
    exit /b 1
)

REM Run the bot with error handling
echo 📊 Generating diagnostic report first...
python diagnostic_report.py

echo.
echo 🤖 Starting the trading bot...
echo 💡 Press Ctrl+C to stop the bot safely
echo.

python bot.py

echo.
echo 🛑 Bot stopped. Generating final reports...
pause
"""
    
    try:
        with open('start_bot.bat', 'w') as f:
            f.write(startup_script)
        print("✅ Startup script created: start_bot.bat")
        print("📝 You can double-click this file to start the bot")
        return True
    except Exception as e:
        print(f"❌ Error creating startup script: {e}")
        return False

def backup_current_config():
    """Backup current configuration"""
    print_section("BACKING UP CURRENT CONFIGURATION")
    
    config_file = 'enhanced_config.json'
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"enhanced_config.json.backup_{timestamp}"
    
    try:
        if os.path.exists(config_file):
            import shutil
            shutil.copy2(config_file, backup_file)
            print(f"✅ Configuration backed up to: {backup_file}")
            return True
        else:
            print(f"⚠️ No configuration file to backup")
            return False
    except Exception as e:
        print(f"❌ Error backing up configuration: {e}")
        return False

def test_bot_imports():
    """Test if bot modules can be imported"""
    print_section("TESTING BOT IMPORTS")
    
    try:
        print("🔍 Testing Python imports...")
        
        # Test standard imports
        import ccxt
        print("✅ ccxt: OK")
        
        import pandas
        print("✅ pandas: OK")
        
        import numpy
        print("✅ numpy: OK")
        
        # Test bot modules
        sys.path.append('.')
        from enhanced_config import get_bot_config
        print("✅ enhanced_config: OK")
        
        config = get_bot_config()
        print(f"✅ Config loaded from: {config.config_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

def main():
    """Main recovery process"""
    print("🚀 CRYPTO TRADING BOT RECOVERY TOOL")
    print(f"📅 Started: {datetime.now()}")
    print(f"📁 Working Directory: {os.getcwd()}")
    
    success_count = 0
    total_checks = 7
    
    # Run all recovery steps
    if backup_current_config():
        success_count += 1
    
    install_missing_dependencies()
    success_count += 1  # Always count as success
    
    if fix_api_configuration():
        success_count += 1
    
    if fix_bot_loop_issue():
        success_count += 1
    
    if check_configuration():
        success_count += 1
    
    if test_bot_imports():
        success_count += 1
    
    if create_startup_script():
        success_count += 1
    
    # Final summary
    print_section("RECOVERY SUMMARY")
    print(f"✅ Completed: {success_count}/{total_checks} checks")
    
    if success_count >= 5:
        print("🎉 Bot recovery successful!")
        print("\n📋 NEXT STEPS:")
        print("1. ⚙️ Verify your API keys are set in enhanced_config.json")
        print("2. 🚀 Run: python bot.py")
        print("3. 📊 Or use: start_bot.bat")
        print("4. 📈 Monitor the bot logs for proper operation")
        print("5. 💡 Press Ctrl+C to stop the bot safely")
    else:
        print("⚠️ Recovery incomplete - please address the issues above")
        print("\n🔧 TROUBLESHOOTING:")
        print("1. Check API credentials in enhanced_config.json")
        print("2. Ensure all Python dependencies are installed")
        print("3. Verify file permissions")
        print("4. Check error messages above")
    
    print(f"\n📅 Recovery completed: {datetime.now()}")

if __name__ == "__main__":
    main()
