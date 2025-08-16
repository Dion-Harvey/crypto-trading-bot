#!/usr/bin/env python3
"""
🌐 AWS SYNC VERIFICATION TOOL
============================
Check if recent bot updates have been uploaded to AWS
"""

import subprocess
import os
import time
import hashlib
from datetime import datetime

# AWS connection details
AWS_KEY_FILE = r"C:\Users\miste\Documents\cryptobot-key.pem"
AWS_USER = "ubuntu"
AWS_IP = "3.135.216.32"
AWS_BOT_DIR = "/home/ubuntu/crypto-trading-bot"

def run_ssh_command(command, timeout=30):
    """Execute SSH command on AWS instance"""
    try:
        ssh_cmd = [
            "ssh", 
            "-i", AWS_KEY_FILE,
            "-o", "StrictHostKeyChecking=no",
            "-o", "ConnectTimeout=10",
            f"{AWS_USER}@{AWS_IP}",
            command
        ]
        
        result = subprocess.run(ssh_cmd, capture_output=True, text=True, timeout=timeout)
        
        if result.returncode == 0:
            return {"success": True, "output": result.stdout.strip(), "error": None}
        else:
            return {"success": False, "output": result.stdout.strip(), "error": result.stderr.strip()}
            
    except subprocess.TimeoutExpired:
        return {"success": False, "output": "", "error": f"Command timed out after {timeout}s"}
    except Exception as e:
        return {"success": False, "output": "", "error": str(e)}

def get_file_hash(filepath):
    """Get MD5 hash of a local file"""
    try:
        with open(filepath, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except Exception as e:
        return f"Error: {e}"

def check_aws_file_hash(remote_path):
    """Get MD5 hash of a remote file on AWS"""
    command = f"md5sum {remote_path} 2>/dev/null || echo 'File not found'"
    result = run_ssh_command(command)
    
    if result["success"] and "File not found" not in result["output"]:
        # Extract just the hash (first part before space)
        hash_output = result["output"].split()[0] if result["output"] else "Error"
        return hash_output
    else:
        return "File not found"

def check_file_sync_status():
    """Check if critical files are synced between local and AWS"""
    print("🔍 CHECKING FILE SYNC STATUS")
    print("=" * 50)
    
    # Critical files to check
    critical_files = [
        "bot.py",
        "enhanced_config.json", 
        "enhanced_config.py",
        "config.py",
        "state_manager.py",
        "multi_crypto_monitor.py",
        "price_jump_detector.py",
        "institutional_strategies.py",
        "enhanced_multi_strategy.py"
    ]
    
    sync_status = {}
    
    for file in critical_files:
        print(f"\n📁 Checking {file}...")
        
        # Get local file info
        if os.path.exists(file):
            local_hash = get_file_hash(file)
            local_size = os.path.getsize(file)
            local_modified = datetime.fromtimestamp(os.path.getmtime(file))
            
            print(f"   💻 Local: {local_hash[:8]}... ({local_size} bytes, {local_modified.strftime('%Y-%m-%d %H:%M')})")
            
            # Get AWS file info
            aws_hash = check_aws_file_hash(f"{AWS_BOT_DIR}/{file}")
            
            if aws_hash != "File not found" and "Error" not in aws_hash:
                print(f"   ☁️ AWS:   {aws_hash[:8]}...")
                
                if local_hash == aws_hash:
                    print(f"   ✅ Status: SYNCED")
                    sync_status[file] = "synced"
                else:
                    print(f"   ❌ Status: OUT OF SYNC")
                    sync_status[file] = "out_of_sync"
            else:
                print(f"   ⚠️ AWS:   {aws_hash}")
                print(f"   ❌ Status: MISSING FROM AWS")
                sync_status[file] = "missing"
        else:
            print(f"   ⚠️ Local file not found")
            sync_status[file] = "local_missing"
    
    return sync_status

def check_recent_updates():
    """Check what files have been recently modified"""
    print("\n🕒 RECENT LOCAL MODIFICATIONS")
    print("=" * 40)
    
    # Check files modified in last 24 hours
    current_time = time.time()
    recent_files = []
    
    for file in os.listdir('.'):
        if file.endswith(('.py', '.json')):
            try:
                mod_time = os.path.getmtime(file)
                hours_ago = (current_time - mod_time) / 3600
                
                if hours_ago < 24:  # Modified in last 24 hours
                    recent_files.append({
                        'file': file,
                        'hours_ago': hours_ago,
                        'mod_time': datetime.fromtimestamp(mod_time)
                    })
            except:
                pass
    
    if recent_files:
        # Sort by most recent first
        recent_files.sort(key=lambda x: x['hours_ago'])
        
        print("📝 Files modified in last 24 hours:")
        for file_info in recent_files:
            hours = file_info['hours_ago']
            if hours < 1:
                time_str = f"{hours*60:.0f} minutes ago"
            else:
                time_str = f"{hours:.1f} hours ago"
            
            print(f"   🔸 {file_info['file']:25} - {time_str}")
    else:
        print("📝 No files modified in last 24 hours")
    
    return recent_files

def check_aws_bot_status():
    """Check if bot is running on AWS with current code"""
    print("\n🤖 AWS BOT STATUS")
    print("=" * 30)
    
    # Check if bot process is running
    result = run_ssh_command("pgrep -f 'python.*bot.py' || echo 'No bot running'")
    
    if result["success"]:
        if "No bot running" in result["output"]:
            print("❌ Bot is NOT running on AWS")
            bot_running = False
        else:
            pids = result["output"].strip().split('\n') if result["output"].strip() else []
            print(f"✅ Bot is running on AWS (PIDs: {', '.join(pids)})")
            bot_running = True
    else:
        print(f"⚠️ Error checking bot status: {result['error']}")
        bot_running = False
    
    # Check bot log for recent activity
    log_result = run_ssh_command(f"cd {AWS_BOT_DIR} && tail -3 bot_log.txt 2>/dev/null || echo 'No log file'")
    
    if log_result["success"] and "No log file" not in log_result["output"]:
        print("📋 Recent AWS bot activity:")
        for line in log_result["output"].split('\n'):
            if line.strip():
                print(f"   {line}")
    else:
        print("⚠️ No recent bot log activity found")
    
    return bot_running

def provide_sync_recommendations(sync_status, recent_files):
    """Provide recommendations based on sync status"""
    print("\n💡 SYNC RECOMMENDATIONS")
    print("=" * 40)
    
    out_of_sync = [f for f, status in sync_status.items() if status in ['out_of_sync', 'missing']]
    
    if out_of_sync:
        print("🚨 FILES NEEDING UPLOAD TO AWS:")
        for file in out_of_sync:
            status = sync_status[file]
            if status == 'out_of_sync':
                print(f"   🔸 {file} - Updated locally but not on AWS")
            else:
                print(f"   🔸 {file} - Missing from AWS")
        
        print("\n🔧 UPLOAD COMMANDS:")
        print(f'   scp -i "{AWS_KEY_FILE}" {{filename}} {AWS_USER}@{AWS_IP}:{AWS_BOT_DIR}/{{filename}}')
        print("\n📦 Upload all at once:")
        files_to_upload = ' '.join(out_of_sync)
        print(f'   scp -i "{AWS_KEY_FILE}" {files_to_upload} {AWS_USER}@{AWS_IP}:{AWS_BOT_DIR}/')
    
    if recent_files:
        print(f"\n⚡ RECENTLY MODIFIED FILES:")
        for file_info in recent_files[:5]:  # Show top 5 most recent
            file = file_info['file']
            status = sync_status.get(file, 'unknown')
            
            if status == 'synced':
                print(f"   ✅ {file} - Already synced")
            elif status in ['out_of_sync', 'missing']:
                print(f"   ❌ {file} - Needs upload")
            else:
                print(f"   ⚠️ {file} - Status unknown")
    
    synced_count = len([f for f, status in sync_status.items() if status == 'synced'])
    total_count = len(sync_status)
    sync_percentage = (synced_count / total_count) * 100 if total_count > 0 else 0
    
    print(f"\n📊 SYNC SUMMARY:")
    print(f"   ✅ Synced: {synced_count}/{total_count} files ({sync_percentage:.1f}%)")
    print(f"   ❌ Need upload: {len(out_of_sync)} files")
    
    if sync_percentage >= 90:
        print(f"   🟢 Status: EXCELLENT SYNC")
    elif sync_percentage >= 70:
        print(f"   🟡 Status: GOOD SYNC (minor updates needed)")
    else:
        print(f"   🔴 Status: POOR SYNC (major updates needed)")

def main():
    """Main sync verification function"""
    print("🌐 AWS SYNC VERIFICATION")
    print("=" * 60)
    print(f"🕒 Check Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔗 Target: {AWS_USER}@{AWS_IP}")
    print(f"📁 AWS Directory: {AWS_BOT_DIR}")
    print()
    
    # Test AWS connection
    print("🔌 Testing AWS connection...")
    test_result = run_ssh_command("echo 'Connection successful'", timeout=10)
    
    if not test_result["success"]:
        print(f"❌ Cannot connect to AWS: {test_result['error']}")
        print("\n💡 Troubleshooting:")
        print("   - Check if AWS instance is running")
        print("   - Verify key file permissions")
        print("   - Test network connectivity")
        return False
    
    print(f"✅ AWS connection successful")
    
    # Check recent local modifications
    recent_files = check_recent_updates()
    
    # Check file sync status
    sync_status = check_file_sync_status()
    
    # Check AWS bot status
    bot_running = check_aws_bot_status()
    
    # Provide recommendations
    provide_sync_recommendations(sync_status, recent_files)
    
    # Final status
    print(f"\n🎯 FINAL STATUS:")
    out_of_sync_count = len([f for f, status in sync_status.items() if status in ['out_of_sync', 'missing']])
    
    if out_of_sync_count == 0:
        print(f"✅ ALL FILES ARE SYNCED WITH AWS")
        if bot_running:
            print(f"✅ Bot is running with latest code")
        else:
            print(f"⚠️ Bot is not running (needs restart)")
    else:
        print(f"❌ {out_of_sync_count} FILES NEED TO BE UPLOADED")
        print(f"🔧 Upload required before AWS bot reflects latest changes")
    
    return True

if __name__ == "__main__":
    main()
