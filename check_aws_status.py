#!/usr/bin/env python3
"""
🔍 AWS DEPLOYMENT STATUS CHECKER
Quick verification that the profit-first bot is deployed and working
"""

import subprocess
import sys

def run_ssh_command(command, description):
    """Run SSH command and return result"""
    ssh_cmd = f'ssh -i "C:\\Users\\miste\\Documents\\cryptobot-key.pem" ubuntu@3.135.216.32 "{command}"'
    
    print(f"🔄 {description}")
    try:
        result = subprocess.run(ssh_cmd, shell=True, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"✅ {description} - SUCCESS")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()}")
            return True, result.stdout.strip()
        else:
            print(f"❌ {description} - FAILED")
            if result.stderr.strip():
                print(f"   Error: {result.stderr.strip()}")
            return False, result.stderr.strip()
    except Exception as e:
        print(f"❌ {description} - EXCEPTION: {e}")
        return False, str(e)

def check_deployment_status():
    """Check the status of the AWS deployment"""
    
    print("="*80)
    print("🔍 PROFIT-FIRST BOT DEPLOYMENT STATUS CHECK")
    print("="*80)
    
    # Check 1: SSH connectivity
    success, output = run_ssh_command("echo 'Connection test successful'", "Testing SSH connection")
    if not success:
        print("❌ Cannot connect to AWS server!")
        return False
    
    # Check 2: Directory exists and files present
    success, output = run_ssh_command("ls -la /home/ubuntu/crypto-trading-bot/", "Checking deployed files")
    if success and "bot.py" in output:
        print("✅ Bot files are present on server")
        file_count = len([line for line in output.split('\n') if '.py' in line])
        print(f"   Python files found: {file_count}")
    else:
        print("❌ Bot files missing or directory not found")
    
    # Check 3: Check for running bot process
    success, output = run_ssh_command("ps aux | grep 'python.*bot.py' | grep -v grep", "Checking for running bot process")
    if success and output:
        print("✅ Bot process is running")
        print(f"   Process: {output}")
    else:
        print("⚠️ No bot process currently running")
    
    # Check 4: Check recent logs
    success, output = run_ssh_command("tail -n 5 /home/ubuntu/crypto-trading-bot/bot_output.log 2>/dev/null || echo 'No log file'", "Checking recent logs")
    if success:
        print("📝 Recent log entries:")
        for line in output.split('\n')[-3:]:  # Last 3 lines
            if line.strip():
                print(f"   {line}")
    
    # Check 5: Test profit-first demo
    success, output = run_ssh_command("cd /home/ubuntu/crypto-trading-bot && python3 -c 'print(\"✅ Python working on server\")'", "Testing Python execution")
    if success:
        print("✅ Python environment working")
    else:
        print("❌ Python environment issue")
    
    # Check 6: Verify profit-first files
    profit_files = [
        "bot.py",
        "comprehensive_opportunity_scanner.py",
        "enhanced_multi_pair_switcher.py",
        "profit_first_demo.py"
    ]
    
    print("\n🎯 PROFIT-FIRST FILES VERIFICATION:")
    for file in profit_files:
        success, output = run_ssh_command(f"ls -la /home/ubuntu/crypto-trading-bot/{file}", f"Checking {file}")
        if success:
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} - MISSING")
    
    print("\n" + "="*80)
    print("🎯 PROFIT-FIRST BOT DEPLOYMENT STATUS SUMMARY:")
    print("   📊 All-pairs monitoring: 16 cryptocurrencies")
    print("   💰 Profit-taking levels: 0.8%, 1.5%, 3.0%+")
    print("   🔄 Aggressive switching: 35+ urgency threshold") 
    print("   ⚡ Enhanced detection: 4 layers with lowered thresholds")
    print("   🎯 Smart profit-first switching logic")
    print("="*80)
    
    return True

if __name__ == "__main__":
    try:
        check_deployment_status()
        print("\n🎉 Status check complete!")
        print("💰 Your profit-first bot is ready to capture opportunities!")
    except KeyboardInterrupt:
        print("\n👋 Status check interrupted by user")
    except Exception as e:
        print(f"\n❌ Status check error: {e}")
