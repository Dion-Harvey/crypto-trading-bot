#!/usr/bin/env python3
"""
🚀 ENHANCED MULTI-PAIR TRADING BOT LAUNCHER
Complete system with real-time communication between processes
"""

import asyncio
import subprocess
import time
import json
import signal
import sys
from datetime import datetime
from pathlib import Path

class EnhancedMultiPairSystem:
    def __init__(self):
        self.scanner_process = None
        self.main_bot_process = None
        self.running = False
        
        # Process configuration
        self.scanner_script = "multi_pair_scanner.py"
        self.main_bot_script = "bot.py"
        self.config_file = "enhanced_config.json"
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        print(f"\n🛑 Received signal {signum}, shutting down system...")
        self.running = False
        self.stop_all_processes()
        sys.exit(0)
    
    def ensure_config_has_all_pairs(self):
        """Ensure configuration includes all 16 trading pairs"""
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            
            # All 16 pairs that should be monitored
            all_pairs = [
                "BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT",
                "ADA/USDT", "DOGE/USDT", "XLM/USDT", "SUI/USDT", 
                "SHIB/USDT", "HBAR/USDT", "AVAX/USDT", "DOT/USDT",
                "MATIC/USDT", "LINK/USDT", "UNI/USDT", "LTC/USDT"
            ]
            
            # Update supported pairs if needed
            current_pairs = config.get('trading', {}).get('supported_pairs', [])
            if len(current_pairs) < 16:
                config['trading']['supported_pairs'] = all_pairs
                
                # Save updated config
                with open(self.config_file, 'w') as f:
                    json.dump(config, f, indent=2)
                
                print(f"✅ Updated config with all {len(all_pairs)} trading pairs")
            else:
                print(f"✅ Config already has {len(current_pairs)} trading pairs")
                
        except Exception as e:
            print(f"⚠️ Error updating config: {e}")
    
    def start_multi_pair_scanner(self):
        """Start the multi-pair opportunity scanner"""
        try:
            print("🚀 Starting multi-pair opportunity scanner...")
            
            # Check if scanner script exists
            if not Path(self.scanner_script).exists():
                print(f"⚠️ Scanner script not found: {self.scanner_script}")
                print("📝 Using enhanced_bot_quick_deploy.py as fallback...")
                self.scanner_script = "enhanced_bot_quick_deploy.py"
            
            if Path(self.scanner_script).exists():
                self.scanner_process = subprocess.Popen(
                    [sys.executable, self.scanner_script],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    bufsize=1
                )
                print(f"✅ Multi-pair scanner started (PID: {self.scanner_process.pid})")
                return True
            else:
                print(f"❌ Scanner script not found: {self.scanner_script}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to start scanner: {e}")
            return False
    
    def start_main_bot(self):
        """Start the main trading bot with runtime config reload"""
        try:
            print("🤖 Starting main trading bot...")
            
            if not Path(self.main_bot_script).exists():
                print(f"❌ Main bot script not found: {self.main_bot_script}")
                return False
            
            self.main_bot_process = subprocess.Popen(
                [sys.executable, self.main_bot_script],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            print(f"✅ Main trading bot started (PID: {self.main_bot_process.pid})")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start main bot: {e}")
            return False
    
    def check_process_health(self):
        """Check if processes are still running"""
        scanner_alive = self.scanner_process and self.scanner_process.poll() is None
        bot_alive = self.main_bot_process and self.main_bot_process.poll() is None
        
        return scanner_alive, bot_alive
    
    def stop_all_processes(self):
        """Stop all running processes gracefully"""
        if self.scanner_process:
            try:
                print("🛑 Stopping multi-pair scanner...")
                self.scanner_process.terminate()
                self.scanner_process.wait(timeout=10)
                print("✅ Scanner stopped")
            except subprocess.TimeoutExpired:
                print("⚠️ Force killing scanner...")
                self.scanner_process.kill()
            except Exception as e:
                print(f"⚠️ Error stopping scanner: {e}")
        
        if self.main_bot_process:
            try:
                print("🛑 Stopping main bot...")
                self.main_bot_process.terminate()
                self.main_bot_process.wait(timeout=10)
                print("✅ Main bot stopped")
            except subprocess.TimeoutExpired:
                print("⚠️ Force killing main bot...")
                self.main_bot_process.kill()
            except Exception as e:
                print(f"⚠️ Error stopping main bot: {e}")
    
    def monitor_communication(self):
        """Monitor communication between processes via config file"""
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            
            current_symbol = config.get('trading', {}).get('symbol', 'Unknown')
            last_switch = config.get('trading', {}).get('last_pair_switch', 'Never')
            switch_reason = config.get('trading', {}).get('switch_reason', 'None')
            
            print(f"📊 Communication Status:")
            print(f"   Active Symbol: {current_symbol}")
            print(f"   Last Switch: {last_switch}")
            print(f"   Switch Reason: {switch_reason}")
            
        except Exception as e:
            print(f"⚠️ Communication monitoring error: {e}")
    
    async def run_system(self):
        """Run the complete enhanced multi-pair system"""
        self.running = True
        
        print("🚀 ENHANCED MULTI-PAIR TRADING SYSTEM")
        print("="*60)
        print("🎯 Features:")
        print("   ✅ Real-time multi-pair opportunity scanning")
        print("   ✅ Automatic pair switching with communication")
        print("   ✅ Runtime configuration reload") 
        print("   ✅ 16-pair simultaneous monitoring")
        print("   ✅ Phase 1 & Phase 2 intelligence integration")
        print("   ✅ 0.25% optimized trailing stops")
        print("="*60)
        
        # Ensure config has all pairs
        self.ensure_config_has_all_pairs()
        
        # Start both processes
        scanner_started = self.start_multi_pair_scanner()
        await asyncio.sleep(2)  # Give scanner time to start
        
        bot_started = self.start_main_bot()
        
        if not scanner_started or not bot_started:
            print("❌ Failed to start all processes")
            self.stop_all_processes()
            return
        
        print("\n🎉 SYSTEM STARTUP COMPLETE!")
        print("📊 Both processes running with real-time communication")
        print("🔄 Main bot now reloads config changes from scanner")
        print("-"*60)
        
        # Monitor system
        monitor_count = 0
        while self.running:
            monitor_count += 1
            
            # Check process health
            scanner_alive, bot_alive = self.check_process_health()
            
            current_time = datetime.now().strftime("%H:%M:%S")
            print(f"\n🔍 System Monitor #{monitor_count} - {current_time}")
            print(f"   📡 Scanner: {'✅ Running' if scanner_alive else '❌ Stopped'}")
            print(f"   🤖 Main Bot: {'✅ Running' if bot_alive else '❌ Stopped'}")
            
            # Monitor communication
            self.monitor_communication()
            
            # Restart failed processes
            if not scanner_alive and self.running:
                print("🔄 Restarting scanner...")
                self.start_multi_pair_scanner()
            
            if not bot_alive and self.running:
                print("🔄 Restarting main bot...")
                self.start_main_bot()
            
            # Wait before next check
            await asyncio.sleep(30)  # Check every 30 seconds
        
        print("\n🏁 System monitoring ended")

async def main():
    """Main function"""
    system = EnhancedMultiPairSystem()
    
    try:
        await system.run_system()
    except KeyboardInterrupt:
        print("\n👋 System stopped by user")
    except Exception as e:
        print(f"\n❌ System error: {e}")
    finally:
        system.stop_all_processes()

if __name__ == "__main__":
    print("🚀 LAUNCHING ENHANCED MULTI-PAIR TRADING SYSTEM...")
    asyncio.run(main())
