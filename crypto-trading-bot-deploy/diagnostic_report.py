#!/usr/bin/env python3
"""
Comprehensive Diagnostic Report for Crypto Trading Bot
Checks configuration, dependencies, connections, and recent performance
"""

import os
import sys
import json
import datetime
import traceback
from pathlib import Path

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print('='*60)

def check_file_exists(filepath, description):
    """Check if a file exists and print status"""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: MISSING - {filepath}")
        return False

def check_config_files():
    """Check all configuration files"""
    print_section("CONFIGURATION FILES")
    
    config_files = {
        'enhanced_config.json': 'Main configuration file',
        'config.json': 'Legacy configuration file',
        'bot_state.json': 'Bot state file',
        'dynamic_config.json': 'Dynamic configuration'
    }
    
    missing_files = []
    for filename, description in config_files.items():
        if not check_file_exists(filename, description):
            missing_files.append(filename)
    
    return missing_files

def analyze_config_content():
    """Analyze configuration file content"""
    print_section("CONFIGURATION ANALYSIS")
    
    try:
        # Check enhanced_config.json
        if os.path.exists('enhanced_config.json'):
            with open('enhanced_config.json', 'r') as f:
                config = json.load(f)
            
            print("📋 Enhanced Config Structure:")
            for section in config.keys():
                print(f"   - {section}")
            
            # Check critical settings
            if 'system' in config:
                loop_interval = config['system'].get('loop_interval_seconds', 'NOT SET')
                print(f"   ⏰ Loop Interval: {loop_interval}s")
            
            if 'trading' in config:
                trading = config['trading']
                position_mode = trading.get('position_sizing_mode', 'NOT SET')
                print(f"   💰 Position Sizing Mode: {position_mode}")
                
                if position_mode == 'percentage':
                    base_pct = trading.get('base_position_pct', 'NOT SET')
                    print(f"   📊 Base Position %: {base_pct}")
                else:
                    base_amount = trading.get('base_amount_usd', 'NOT SET')
                    print(f"   💵 Base Amount: ${base_amount}")
            
            if 'api_keys' in config:
                api_keys = config['api_keys']
                print(f"   🔑 API Keys Present: {len(api_keys.get('binance', {}))} Binance keys")
                
                # Check if keys are set (but don't print them)
                binance_keys = api_keys.get('binance', {})
                api_key_set = bool(binance_keys.get('api_key'))
                secret_key_set = bool(binance_keys.get('secret'))
                print(f"   🔐 API Key Set: {api_key_set}")
                print(f"   🔐 Secret Key Set: {secret_key_set}")
            
            if 'strategy_parameters' in config:
                strategy = config['strategy_parameters']
                confidence_threshold = strategy.get('confidence_threshold', 'NOT SET')
                print(f"   🎯 Confidence Threshold: {confidence_threshold}")
        
        else:
            print("❌ enhanced_config.json not found")
    
    except Exception as e:
        print(f"❌ Error analyzing config: {e}")
        traceback.print_exc()

def check_dependencies():
    """Check if required Python packages are installed"""
    print_section("PYTHON DEPENDENCIES")
    
    required_packages = [
        'ccxt',
        'pandas', 
        'numpy',
        'requests',
        'python-dotenv'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}: Installed")
        except ImportError:
            print(f"❌ {package}: NOT INSTALLED")
            missing_packages.append(package)
    
    return missing_packages

def check_log_files():
    """Check recent log files and activity"""
    print_section("LOG FILES & RECENT ACTIVITY")
    
    log_files = [
        'bot_log.txt',
        'daily_sync_task.log',
        'daily_sync.log'
    ]
    
    for log_file in log_files:
        if os.path.exists(log_file):
            try:
                stat = os.stat(log_file)
                size_kb = stat.st_size / 1024
                modified = datetime.datetime.fromtimestamp(stat.st_mtime)
                print(f"✅ {log_file}: {size_kb:.1f}KB, last modified: {modified}")
                
                # Check recent activity (last 10 lines)
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    if lines:
                        print(f"   📝 Last entry: {lines[-1].strip()}")
            except Exception as e:
                print(f"⚠️ {log_file}: Error reading - {e}")
        else:
            print(f"❌ {log_file}: NOT FOUND")

def check_state_files():
    """Check bot state and backup files"""
    print_section("BOT STATE & BACKUPS")
    
    state_files = [
        'bot_state.json',
        'bot_state_ec2_backup.json'
    ]
    
    for state_file in state_files:
        if os.path.exists(state_file):
            try:
                with open(state_file, 'r') as f:
                    state = json.load(f)
                print(f"✅ {state_file}: Found")
                
                # Check key state information
                if 'holding_position' in state:
                    holding = state['holding_position']
                    print(f"   📊 Holding Position: {holding}")
                
                if 'entry_price' in state:
                    entry = state['entry_price']
                    print(f"   💰 Entry Price: ${entry}")
                
                if 'last_trade_time' in state:
                    last_trade = state['last_trade_time']
                    if last_trade:
                        trade_time = datetime.datetime.fromtimestamp(last_trade)
                        print(f"   🕐 Last Trade: {trade_time}")
                    else:
                        print(f"   🕐 Last Trade: None")
                
            except Exception as e:
                print(f"⚠️ {state_file}: Error reading - {e}")
        else:
            print(f"❌ {state_file}: NOT FOUND")

def check_backup_files():
    """Check for recent backup files"""
    print_section("BACKUP FILES")
    
    # Look for backup files with timestamps
    backup_patterns = [
        'enhanced_config.json.backup_*',
        'config.json.backup_*'
    ]
    
    backup_files = []
    for pattern in backup_patterns:
        import glob
        matches = glob.glob(pattern)
        backup_files.extend(matches)
    
    if backup_files:
        print(f"✅ Found {len(backup_files)} backup files:")
        # Sort by modification time (most recent first)
        backup_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        for backup in backup_files[:5]:  # Show only the 5 most recent
            modified = datetime.datetime.fromtimestamp(os.path.getmtime(backup))
            print(f"   📄 {backup} (modified: {modified})")
    else:
        print("❌ No backup files found")

def test_basic_imports():
    """Test if bot modules can be imported"""
    print_section("MODULE IMPORT TEST")
    
    try:
        # Test if we can import the config module
        sys.path.append('.')
        
        print("🔍 Testing module imports...")
        
        # Test config loading
        try:
            from enhanced_config import get_bot_config
            config = get_bot_config()
            print("✅ enhanced_config: Import successful")
            print(f"   📝 Config file used: {config.config_file}")
        except Exception as e:
            print(f"❌ enhanced_config: Import failed - {e}")
        
        # Test other critical imports
        try:
            import ccxt
            print("✅ ccxt: Import successful")
        except Exception as e:
            print(f"❌ ccxt: Import failed - {e}")
        
        try:
            import pandas
            print("✅ pandas: Import successful")
        except Exception as e:
            print(f"❌ pandas: Import failed - {e}")
    
    except Exception as e:
        print(f"❌ Module import test failed: {e}")

def check_recent_changes():
    """Check for recent file modifications"""
    print_section("RECENT FILE CHANGES")
    
    # Get all Python files and config files
    files_to_check = []
    for ext in ['*.py', '*.json']:
        import glob
        files_to_check.extend(glob.glob(ext))
    
    # Sort by modification time
    recent_files = []
    cutoff_time = datetime.datetime.now() - datetime.timedelta(days=3)
    
    for file in files_to_check:
        try:
            modified = datetime.datetime.fromtimestamp(os.path.getmtime(file))
            if modified > cutoff_time:
                recent_files.append((file, modified))
        except:
            continue
    
    recent_files.sort(key=lambda x: x[1], reverse=True)
    
    if recent_files:
        print(f"✅ Files modified in last 3 days:")
        for file, modified in recent_files[:10]:  # Show top 10
            print(f"   📝 {file}: {modified}")
    else:
        print("❌ No recent file modifications found")

def run_connection_test():
    """Test exchange connection"""
    print_section("EXCHANGE CONNECTION TEST")
    
    try:
        # Try to load config and test connection
        from enhanced_config import get_bot_config
        config = get_bot_config()
        optimized_config = config.get_optimized_config()
        
        import ccxt
        
        # Get API credentials
        api_keys = optimized_config.get('api_keys', {}).get('binance', {})
        api_key = api_keys.get('api_key')
        secret = api_keys.get('secret')
        
        if not api_key or not secret:
            print("❌ API credentials not found in config")
            return False
        
        # Create exchange instance
        exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': secret,
            'sandbox': False,
            'enableRateLimit': True,
        })
        
        print("🔍 Testing exchange connection...")
        
        # Test basic connection
        try:
            balance = exchange.fetch_balance()
            print("✅ Exchange connection: SUCCESS")
            
            # Show basic balance info
            usdc_balance = balance.get('USDC', {}).get('free', 0)
            btc_balance = balance.get('BTC', {}).get('free', 0)
            print(f"   💰 USDC Balance: {usdc_balance:.2f}")
            print(f"   ₿ BTC Balance: {btc_balance:.6f}")
            
            return True
            
        except Exception as e:
            print(f"❌ Exchange connection failed: {e}")
            return False
    
    except Exception as e:
        print(f"❌ Connection test setup failed: {e}")
        return False

def generate_diagnostic_summary():
    """Generate a summary of findings and recommendations"""
    print_section("DIAGNOSTIC SUMMARY & RECOMMENDATIONS")
    
    print("🔍 DIAGNOSTIC COMPLETE")
    print("\n📊 ANALYSIS:")
    
    # Check critical files
    critical_files = ['enhanced_config.json', 'bot.py']
    missing_critical = []
    for file in critical_files:
        if not os.path.exists(file):
            missing_critical.append(file)
    
    if missing_critical:
        print(f"🚨 CRITICAL: Missing files: {missing_critical}")
    else:
        print("✅ All critical files present")
    
    print("\n🔧 RECOMMENDATIONS:")
    print("1. Check the above sections for any ❌ errors")
    print("2. If API connection failed, verify API keys in enhanced_config.json")
    print("3. If dependencies are missing, run: pip install -r requirements.txt")
    print("4. Check recent log files for error messages")
    print("5. Compare current config with recent backups if needed")
    
    print(f"\n📅 Diagnostic completed at: {datetime.datetime.now()}")

def main():
    """Run complete diagnostic"""
    print("🚀 CRYPTO TRADING BOT - COMPREHENSIVE DIAGNOSTIC")
    print(f"📅 Date: {datetime.datetime.now()}")
    print(f"📁 Working Directory: {os.getcwd()}")
    
    try:
        # Run all diagnostic checks
        check_config_files()
        analyze_config_content()
        check_dependencies()
        check_log_files()
        check_state_files()
        check_backup_files()
        test_basic_imports()
        check_recent_changes()
        run_connection_test()
        generate_diagnostic_summary()
        
    except Exception as e:
        print(f"\n❌ Diagnostic failed with error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
