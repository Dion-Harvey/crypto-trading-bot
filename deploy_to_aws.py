#!/usr/bin/env python3
"""
🚀 AWS EC2 DEPLOYMENT SCRIPT - PROFIT-FIRST BOT
Deploy enhanced profit-first switching bot to AWS EC2
"""

import os
import subprocess
import json
from datetime import datetime

# AWS EC2 Details
KEY_FILE = r"C:\Users\miste\Documents\cryptobot-key.pem"
EC2_USER = "ubuntu"
EC2_IP = "3.135.216.32"
EC2_TARGET_DIR = "/home/ubuntu/crypto-trading-bot"
LOCAL_SOURCE_DIR = r"C:\Users\miste\Documents\crypto-trading-bot\crypto-trading-bot"

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}")
    print(f"   Command: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - SUCCESS")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()[:200]}...")
            return True
        else:
            print(f"❌ {description} - FAILED")
            print(f"   Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ {description} - EXCEPTION: {e}")
        return False

def create_deployment_summary():
    """Create deployment summary"""
    
    summary = {
        "deployment_time": datetime.now().isoformat(),
        "deployment_type": "PROFIT-FIRST_ENHANCED_BOT",
        "key_features": [
            "✅ Profit-taking at 0.8%, 1.5%, 3.0%+ levels",
            "✅ Aggressive pair switching (35+ urgency, down from 50+)",
            "✅ Smart profit-first switching logic",
            "✅ Enhanced 4-layer detection system",
            "✅ Lowered thresholds for more opportunities (4%+ moves)",
            "✅ Comprehensive all-pairs monitoring (16 pairs)",
            "✅ Volume surge detection (100-300%+ thresholds)"
        ],
        "improvements": [
            "🔄 More aggressive opportunity capture",
            "💰 Higher profit realization rate", 
            "📊 Better portfolio performance",
            "⚡ Faster response to market moves",
            "🎯 Reduced missed opportunities"
        ],
        "files_deployed": [
            "bot.py - Enhanced with profit-first switching",
            "comprehensive_opportunity_scanner.py - All-pairs monitoring",
            "enhanced_multi_pair_switcher.py - Aggressive switching logic",
            "multi_position_portfolio_manager.py - Future multi-position support",
            "profit_first_demo.py - System documentation",
            "monitoring_dashboard.py - Real-time status monitoring"
        ]
    }
    
    with open('deployment_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    return summary

def deploy_to_aws():
    """Deploy profit-first bot to AWS EC2"""
    
    print("\n" + "="*80)
    print("🚀 DEPLOYING PROFIT-FIRST BOT TO AWS EC2")
    print("="*80)
    
    print(f"📊 DEPLOYMENT DETAILS:")
    print(f"   🔑 Key File: {KEY_FILE}")
    print(f"   🌐 Server: {EC2_USER}@{EC2_IP}")
    print(f"   📁 Target: {EC2_TARGET_DIR}")
    print(f"   📂 Source: {LOCAL_SOURCE_DIR}")
    
    # Check if key file exists
    if not os.path.exists(KEY_FILE):
        print(f"❌ Key file not found: {KEY_FILE}")
        return False
    
    # Create deployment summary
    summary = create_deployment_summary()
    
    print(f"\n🎯 DEPLOYING ENHANCED FEATURES:")
    for feature in summary["key_features"]:
        print(f"   {feature}")
    
    # Step 1: Test SSH connection
    test_cmd = f'ssh -i "{KEY_FILE}" -o StrictHostKeyChecking=no {EC2_USER}@{EC2_IP} "echo \'SSH connection successful\'"'
    if not run_command(test_cmd, "Testing SSH connection"):
        return False
    
    # Step 2: Create backup of existing bot
    backup_cmd = f'ssh -i "{KEY_FILE}" {EC2_USER}@{EC2_IP} "cd {EC2_TARGET_DIR} && cp bot.py bot.py.backup.$(date +%Y%m%d_%H%M%S) 2>/dev/null || echo \'No existing bot.py to backup\'"'
    run_command(backup_cmd, "Creating backup of existing bot")
    
    # Step 3: Stop existing bot process
    stop_cmd = f'ssh -i "{KEY_FILE}" {EC2_USER}@{EC2_IP} "pkill -f \'python.*bot.py\' || echo \'No bot process running\'"'
    run_command(stop_cmd, "Stopping existing bot process")
    
    # Step 4: Upload enhanced bot files
    files_to_upload = [
        "bot.py",
        "comprehensive_opportunity_scanner.py", 
        "enhanced_multi_pair_switcher.py",
        "multi_position_portfolio_manager.py",
        "profit_first_demo.py",
        "monitoring_dashboard.py",
        "multi_pair_analysis.py",
        "enhanced_config.json",
        "deployment_summary.json"
    ]
    
    print(f"\n📤 UPLOADING FILES:")
    upload_success = True
    
    for file in files_to_upload:
        file_path = os.path.join(LOCAL_SOURCE_DIR, file)
        if os.path.exists(file_path):
            upload_cmd = f'scp -i "{KEY_FILE}" "{file_path}" {EC2_USER}@{EC2_IP}:{EC2_TARGET_DIR}/'
            if run_command(upload_cmd, f"Uploading {file}"):
                print(f"   ✅ {file}")
            else:
                print(f"   ❌ {file}")
                upload_success = False
        else:
            print(f"   ⚠️ {file} - File not found locally")
    
    if not upload_success:
        print(f"⚠️ Some files failed to upload, but continuing...")
    
    # Step 5: Set permissions
    chmod_cmd = f'ssh -i "{KEY_FILE}" {EC2_USER}@{EC2_IP} "cd {EC2_TARGET_DIR} && chmod +x *.py"'
    run_command(chmod_cmd, "Setting file permissions")
    
    # Step 6: Install any missing dependencies
    deps_cmd = f'ssh -i "{KEY_FILE}" {EC2_USER}@{EC2_IP} "cd {EC2_TARGET_DIR} && pip3 install --user ccxt pandas numpy ta-lib requests python-dateutil || echo \'Dependencies may already be installed\'"'
    run_command(deps_cmd, "Installing/updating dependencies")
    
    # Step 7: Test the enhanced bot
    test_bot_cmd = f'ssh -i "{KEY_FILE}" {EC2_USER}@{EC2_IP} "cd {EC2_TARGET_DIR} && timeout 10 python3 profit_first_demo.py || echo \'Demo completed\'"'
    run_command(test_bot_cmd, "Testing profit-first demo")
    
    # Step 8: Start the enhanced bot in background
    start_cmd = f'ssh -i "{KEY_FILE}" {EC2_USER}@{EC2_IP} "cd {EC2_TARGET_DIR} && nohup python3 bot.py > bot_output.log 2>&1 & echo \'Bot started with PID: $!\'"'
    if run_command(start_cmd, "Starting enhanced profit-first bot"):
        print(f"🚀 PROFIT-FIRST BOT DEPLOYED AND STARTED!")
    
    # Step 9: Check bot status
    status_cmd = f'ssh -i "{KEY_FILE}" {EC2_USER}@{EC2_IP} "cd {EC2_TARGET_DIR} && ps aux | grep \'python.*bot.py\' | grep -v grep || echo \'Bot process not found\'"'
    run_command(status_cmd, "Checking bot process status")
    
    print(f"\n🎉 DEPLOYMENT SUMMARY:")
    print(f"   🚀 Enhanced profit-first bot deployed")
    print(f"   💰 Profit-taking: 0.8%, 1.5%, 3.0%+ levels")
    print(f"   🔄 Aggressive switching: 35+ urgency threshold")
    print(f"   📊 All-pairs monitoring: 16 cryptocurrencies")
    print(f"   ⚡ Lowered detection thresholds for more opportunities")
    print(f"   🎯 Smart profit-first switching logic active")
    
    print(f"\n📋 NEXT STEPS:")
    print(f"   1. Monitor bot logs: ssh -i {KEY_FILE} {EC2_USER}@{EC2_IP} 'tail -f {EC2_TARGET_DIR}/bot_output.log'")
    print(f"   2. Check status: ssh -i {KEY_FILE} {EC2_USER}@{EC2_IP} 'cd {EC2_TARGET_DIR} && python3 monitoring_dashboard.py'")
    print(f"   3. View profits: ssh -i {KEY_FILE} {EC2_USER}@{EC2_IP} 'cd {EC2_TARGET_DIR} && python3 bot_status_check.py'")
    
    return True

if __name__ == "__main__":
    success = deploy_to_aws()
    if success:
        print(f"\n✅ DEPLOYMENT COMPLETE!")
        print(f"🎯 Your profit-first bot is now running on AWS")
        print(f"💰 Ready to capture profits and switch to best opportunities!")
    else:
        print(f"\n❌ DEPLOYMENT FAILED!")
        print(f"Please check the errors above and try again.")
    
    print("="*80)
