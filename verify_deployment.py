import subprocess
import os
from datetime import datetime

def check_deployment():
    print("🔍 AWS DEPLOYMENT VERIFICATION")
    print("=" * 35)
    print(f"⏰ Check time: {datetime.now().strftime('%H:%M:%S')}")
    print()
    
    key_path = r"C:\Users\miste\Documents\cryptobot-key.pem"
    
    if not os.path.exists(key_path):
        print("❌ Key file not found at expected location")
        return False
    
    print("✅ Key file found")
    
    # Check AWS files
    try:
        cmd = [
            'ssh', '-i', key_path,
            '-o', 'StrictHostKeyChecking=no',
            'ubuntu@3.135.216.32',
            'ls -la bot.py enhanced_config.json'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("📁 AWS Files Status:")
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    print(f"   {line}")
        else:
            print(f"⚠️ File check failed: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False
    
    # Check if bot is running
    try:
        cmd = [
            'ssh', '-i', key_path,
            '-o', 'StrictHostKeyChecking=no',
            'ubuntu@3.135.216.32',
            'ps aux | grep bot.py | grep -v grep'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0 and result.stdout.strip():
            print("✅ Bot is running:")
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    print(f"   {line}")
        else:
            print("⚠️ Bot may not be running")
            
    except Exception as e:
        print(f"❌ Process check error: {e}")
    
    return True

if __name__ == "__main__":
    check_deployment()
