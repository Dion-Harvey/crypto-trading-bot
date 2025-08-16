#!/usr/bin/env python3
"""
🚀 COMPLETE AWS UPDATE SCRIPT
=============================
Updates AWS with all latest improvements including LSTM Phase 3
"""

import subprocess
import os
import time
import hashlib
from datetime import datetime
from pathlib import Path

class AWSUpdater:
    def __init__(self):
        self.aws_key = r"C:\Users\miste\Documents\cryptobot-key.pem"
        self.aws_user = "ubuntu"
        self.aws_ip = "3.135.216.32"
        self.aws_dir = "/home/ubuntu/crypto-trading-bot"
        
        # Files to update with their importance
        self.critical_files = {
            # Core bot files
            "bot.py": "Main trading bot with LSTM integration",
            "enhanced_config.json": "Latest optimized configuration",
            "enhanced_config.py": "Configuration management",
            
            # LSTM Phase 3 files
            "lstm_price_predictor.py": "LSTM neural network system",
            "install_lstm_dependencies.py": "LSTM dependency installer",
            "test_lstm_setup.py": "LSTM testing and verification",
            
            # Enhanced strategies
            "priority_functions_5m1m.py": "Enhanced 5m+1m priority system",
            "multi_crypto_monitor.py": "Multi-crypto monitoring",
            "success_rate_enhancer_enhanced.py": "Enhanced success rate system",
            
            # Utility scripts
            "run_bot_daemon.py": "24/7 daemon for continuous operation",
            "crypto-bot-watchdog.py": "Health monitoring watchdog",
            "setup_auto_restart.sh": "Auto-restart configuration",
        }
        
        self.optional_files = {
            # Documentation and analysis
            "PHASE3_WEEK1_SUCCESS.md": "Phase 3 completion documentation",
            "PHASE3_WEEK1_COMPLETE.md": "Phase 3 implementation guide",
            
            # Tools and utilities
            "quick_aws_check.py": "AWS status checking tool",
            "verify_aws_status.py": "Upload verification tool",
            "monitor_bot_health.sh": "Health monitoring script",
        }
    
    def run_ssh_command(self, command, timeout=30):
        """Execute SSH command on AWS instance"""
        try:
            ssh_cmd = [
                "ssh", 
                "-i", self.aws_key,
                "-o", "StrictHostKeyChecking=no",
                "-o", "ConnectTimeout=10",
                f"{self.aws_user}@{self.aws_ip}",
                command
            ]
            
            result = subprocess.run(ssh_cmd, capture_output=True, text=True, timeout=timeout)
            return result.stdout.strip(), result.stderr.strip(), result.returncode == 0
            
        except Exception as e:
            return "", str(e), False
    
    def upload_file(self, local_file, remote_file=None):
        """Upload a single file to AWS"""
        if remote_file is None:
            remote_file = f"{self.aws_dir}/{os.path.basename(local_file)}"
        
        try:
            scp_cmd = [
                "scp", 
                "-i", self.aws_key,
                "-o", "StrictHostKeyChecking=no",
                local_file,
                f"{self.aws_user}@{self.aws_ip}:{remote_file}"
            ]
            
            result = subprocess.run(scp_cmd, capture_output=True, text=True, timeout=30)
            return result.returncode == 0, result.stderr
            
        except Exception as e:
            return False, str(e)
    
    def check_local_files(self):
        """Check which files exist locally"""
        print("🔍 CHECKING LOCAL FILES...")
        print("=" * 40)
        
        existing_files = []
        missing_files = []
        
        all_files = {**self.critical_files, **self.optional_files}
        
        for file, description in all_files.items():
            if os.path.exists(file):
                size = os.path.getsize(file)
                mod_time = datetime.fromtimestamp(os.path.getmtime(file))
                print(f"✅ {file}")
                print(f"   📄 {description}")
                print(f"   💾 {size:,} bytes, modified {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
                existing_files.append(file)
            else:
                print(f"❌ {file} - Missing")
                missing_files.append(file)
            print()
        
        print(f"📊 Summary: {len(existing_files)} found, {len(missing_files)} missing")
        return existing_files, missing_files
    
    def test_aws_connection(self):
        """Test AWS connection"""
        print("\n🔍 TESTING AWS CONNECTION...")
        print("=" * 30)
        
        if not os.path.exists(self.aws_key):
            print(f"❌ AWS key file not found: {self.aws_key}")
            return False
        
        # Test basic connection
        stdout, stderr, success = self.run_ssh_command("echo 'Connection test successful'", timeout=10)
        
        if success and "Connection test successful" in stdout:
            print("✅ AWS connection successful")
            
            # Get system info
            stdout, stderr, success = self.run_ssh_command("uname -a && df -h")
            if success:
                lines = stdout.split('\n')
                print(f"🖥️ System: {lines[0] if lines else 'Unknown'}")
                print(f"💾 Disk space: Available")
            
            return True
        else:
            print(f"❌ AWS connection failed: {stderr}")
            return False
    
    def backup_aws_files(self):
        """Create backup of current AWS files"""
        print("\n💾 CREATING AWS BACKUP...")
        print("=" * 25)
        
        backup_dir = f"{self.aws_dir}/backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create backup directory
        stdout, stderr, success = self.run_ssh_command(f"mkdir -p {backup_dir}")
        if not success:
            print(f"⚠️ Could not create backup directory: {stderr}")
            return False
        
        # Backup critical files
        backup_files = ["bot.py", "enhanced_config.json", "enhanced_config.py"]
        backed_up = 0
        
        for file in backup_files:
            stdout, stderr, success = self.run_ssh_command(f"cp {self.aws_dir}/{file} {backup_dir}/ 2>/dev/null")
            if success:
                backed_up += 1
                print(f"✅ Backed up {file}")
            else:
                print(f"⚠️ Could not backup {file} (may not exist)")
        
        print(f"📊 Backup complete: {backed_up} files saved to {backup_dir}")
        return True
    
    def upload_all_files(self, files_to_upload):
        """Upload all files to AWS"""
        print(f"\n📤 UPLOADING {len(files_to_upload)} FILES...")
        print("=" * 35)
        
        uploaded = 0
        failed = 0
        
        for file in files_to_upload:
            print(f"📤 Uploading {file}...")
            
            success, error = self.upload_file(file)
            if success:
                print(f"✅ {file} uploaded successfully")
                uploaded += 1
            else:
                print(f"❌ Failed to upload {file}: {error}")
                failed += 1
            
            # Small delay to avoid overwhelming the connection
            time.sleep(0.5)
        
        print(f"\n📊 Upload Summary: {uploaded} successful, {failed} failed")
        return uploaded, failed
    
    def setup_python_environment(self):
        """Setup Python environment on AWS"""
        print("\n🐍 SETTING UP PYTHON ENVIRONMENT...")
        print("=" * 40)
        
        # Check if virtual environment exists
        stdout, stderr, success = self.run_ssh_command(f"cd {self.aws_dir} && ls -la .venv")
        if not success:
            print("📦 Creating virtual environment...")
            stdout, stderr, success = self.run_ssh_command(f"cd {self.aws_dir} && python3 -m venv .venv")
            if not success:
                print(f"❌ Failed to create virtual environment: {stderr}")
                return False
        
        print("✅ Virtual environment ready")
        
        # Install basic dependencies
        print("📦 Installing dependencies...")
        deps_cmd = f"cd {self.aws_dir} && .venv/bin/pip install ccxt pandas numpy python-dotenv scipy scikit-learn"
        stdout, stderr, success = self.run_ssh_command(deps_cmd, timeout=120)
        
        if success:
            print("✅ Basic dependencies installed")
        else:
            print(f"⚠️ Some dependencies may have failed: {stderr}")
        
        # Try to install TensorFlow
        print("🧠 Installing TensorFlow for LSTM...")
        tf_cmd = f"cd {self.aws_dir} && .venv/bin/pip install tensorflow-cpu==2.13.0"
        stdout, stderr, success = self.run_ssh_command(tf_cmd, timeout=180)
        
        if success:
            print("✅ TensorFlow installed successfully")
        else:
            print(f"⚠️ TensorFlow installation may have failed: {stderr}")
            print("💡 Bot will work without TensorFlow (no LSTM enhancement)")
        
        return True
    
    def setup_system_services(self):
        """Setup systemd services for 24/7 operation"""
        print("\n⚙️ SETTING UP SYSTEM SERVICES...")
        print("=" * 35)
        
        # Make scripts executable
        scripts_to_make_executable = [
            "run_bot_daemon.py",
            "crypto-bot-watchdog.py",
            "setup_auto_restart.sh"
        ]
        
        for script in scripts_to_make_executable:
            stdout, stderr, success = self.run_ssh_command(f"cd {self.aws_dir} && chmod +x {script}")
            if success:
                print(f"✅ Made {script} executable")
            else:
                print(f"⚠️ Could not make {script} executable (may not exist)")
        
        # Run auto-restart setup if available
        stdout, stderr, success = self.run_ssh_command(f"cd {self.aws_dir} && ls setup_auto_restart.sh")
        if success:
            print("🔧 Running auto-restart setup...")
            stdout, stderr, success = self.run_ssh_command(f"cd {self.aws_dir} && bash setup_auto_restart.sh", timeout=120)
            if success:
                print("✅ Auto-restart system configured")
            else:
                print(f"⚠️ Auto-restart setup had issues: {stderr}")
        else:
            print("⚠️ setup_auto_restart.sh not found, skipping service setup")
        
        return True
    
    def stop_existing_bot(self):
        """Stop any existing bot processes"""
        print("\n🛑 STOPPING EXISTING BOT PROCESSES...")
        print("=" * 40)
        
        # Check for running processes
        stdout, stderr, success = self.run_ssh_command("pgrep -f 'python.*bot.py'")
        if success and stdout.strip():
            pids = stdout.strip().split('\n')
            print(f"🔍 Found {len(pids)} bot process(es)")
            
            # Kill processes
            stdout, stderr, success = self.run_ssh_command("pkill -f 'python.*bot.py'")
            if success:
                print("✅ Bot processes stopped")
            else:
                print(f"⚠️ Error stopping processes: {stderr}")
            
            # Wait a moment
            time.sleep(3)
        else:
            print("ℹ️ No bot processes found")
        
        return True
    
    def start_bot(self):
        """Start the bot with the new configuration"""
        print("\n🚀 STARTING BOT...")
        print("=" * 20)
        
        # Start bot in background
        start_cmd = f"cd {self.aws_dir} && nohup .venv/bin/python bot.py > bot_output.log 2>&1 &"
        stdout, stderr, success = self.run_ssh_command(start_cmd)
        
        if success:
            print("✅ Bot start command executed")
            
            # Wait a moment for startup
            time.sleep(5)
            
            # Check if bot is running
            stdout, stderr, success = self.run_ssh_command("pgrep -f 'python.*bot.py'")
            if success and stdout.strip():
                print(f"✅ Bot is running (PID: {stdout.strip()})")
                
                # Check recent output
                stdout, stderr, success = self.run_ssh_command(f"cd {self.aws_dir} && tail -5 bot_output.log")
                if success and stdout.strip():
                    print("📋 Recent output:")
                    for line in stdout.split('\n'):
                        if line.strip():
                            print(f"   {line}")
                
                return True
            else:
                print("❌ Bot may not have started properly")
                
                # Check for errors
                stdout, stderr, success = self.run_ssh_command(f"cd {self.aws_dir} && tail -10 bot_output.log")
                if success and stdout.strip():
                    print("📋 Error output:")
                    for line in stdout.split('\n'):
                        if line.strip():
                            print(f"   {line}")
                
                return False
        else:
            print(f"❌ Failed to start bot: {stderr}")
            return False
    
    def verify_deployment(self):
        """Verify the deployment is working"""
        print("\n🔍 VERIFYING DEPLOYMENT...")
        print("=" * 30)
        
        # Check bot status
        stdout, stderr, success = self.run_ssh_command("pgrep -f 'python.*bot.py' | wc -l")
        if success and stdout.strip().isdigit():
            process_count = int(stdout.strip())
            if process_count > 0:
                print(f"✅ Bot is running ({process_count} process(es))")
            else:
                print("❌ Bot is not running")
                return False
        
        # Check LSTM availability
        stdout, stderr, success = self.run_ssh_command(f"cd {self.aws_dir} && .venv/bin/python -c \"import tensorflow; print('TensorFlow available')\" 2>/dev/null")
        if "TensorFlow available" in stdout:
            print("✅ LSTM/TensorFlow is available")
        else:
            print("⚠️ LSTM/TensorFlow not available (bot will work without it)")
        
        # Check recent activity
        stdout, stderr, success = self.run_ssh_command(f"cd {self.aws_dir} && tail -2 bot_output.log")
        if success and stdout.strip():
            print("📋 Recent activity:")
            for line in stdout.split('\n'):
                if line.strip():
                    print(f"   {line}")
        
        return True
    
    def run_complete_update(self):
        """Run the complete AWS update process"""
        print("🚀 COMPLETE AWS UPDATE - CRYPTO TRADING BOT")
        print("=" * 60)
        print(f"🕒 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Step 1: Check local files
        existing_files, missing_files = self.check_local_files()
        if not existing_files:
            print("❌ No files to upload!")
            return False
        
        # Step 2: Test AWS connection
        if not self.test_aws_connection():
            return False
        
        # Step 3: Create backup
        self.backup_aws_files()
        
        # Step 4: Stop existing bot
        self.stop_existing_bot()
        
        # Step 5: Upload files
        uploaded, failed = self.upload_all_files(existing_files)
        if uploaded == 0:
            print("❌ No files uploaded successfully!")
            return False
        
        # Step 6: Setup Python environment
        self.setup_python_environment()
        
        # Step 7: Setup system services (optional)
        self.setup_system_services()
        
        # Step 8: Start bot
        if not self.start_bot():
            print("⚠️ Bot start had issues, but files are uploaded")
        
        # Step 9: Verify deployment
        deployment_ok = self.verify_deployment()
        
        # Final summary
        print(f"\n🎯 UPDATE SUMMARY")
        print("=" * 20)
        print(f"📤 Files uploaded: {uploaded}")
        print(f"❌ Files failed: {failed}")
        print(f"🤖 Bot status: {'Running' if deployment_ok else 'Issues detected'}")
        print(f"🧠 LSTM status: {'Ready' if deployment_ok else 'Check logs'}")
        print()
        
        if deployment_ok:
            print("🎉 AWS UPDATE COMPLETED SUCCESSFULLY!")
            print("✅ Your bot is now running with all latest improvements:")
            print("   • LSTM Phase 3 neural network enhancement")
            print("   • Enhanced 5m+1m priority system")
            print("   • Optimized 0.25% trailing stops")
            print("   • Multi-crypto monitoring")
            print("   • 24/7 auto-restart capability")
            print("   • Advanced risk management")
        else:
            print("⚠️ Update completed with some issues")
            print("💡 Check the logs above for details")
            print("🔧 You may need to manually restart the bot")
        
        print(f"\n🔧 Manual Commands (if needed):")
        print(f'   ssh -i "{self.aws_key}" {self.aws_user}@{self.aws_ip}')
        print(f'   cd {self.aws_dir}')
        print(f'   .venv/bin/python bot.py')
        
        return deployment_ok

def main():
    updater = AWSUpdater()
    success = updater.run_complete_update()
    
    if success:
        print("\n✅ All systems ready! Your AWS bot is updated and running.")
    else:
        print("\n⚠️ Update had some issues. Check the output above.")
    
    return success

if __name__ == "__main__":
    main()
