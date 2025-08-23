#!/usr/bin/env python3
"""
Live Bot Monitor - Continuous monitoring of bot status
Runs as background process to monitor trading bot activity
"""

import os
import time
import json
from datetime import datetime
import threading

class LiveBotMonitor:
    def __init__(self):
        self.running = True
        self.monitor_interval = 30  # Check every 30 seconds
        
    def get_bot_state(self):
        """Read current bot state"""
        try:
            with open('bot_state.json', 'r') as f:
                return json.load(f)
        except Exception as e:
            return {"error": str(e)}
    
    def get_enhanced_config(self):
        """Read enhanced configuration"""
        try:
            with open('enhanced_config.json', 'r') as f:
                return json.load(f)
        except Exception as e:
            return {"error": str(e)}
    
    def check_lstm_models(self):
        """Check if LSTM models exist"""
        model_path = "models/lstm"
        models = {
            "1m": os.path.exists(f"{model_path}/lstm_1m.h5"),
            "5m": os.path.exists(f"{model_path}/lstm_5m.h5"), 
            "15m": os.path.exists(f"{model_path}/lstm_15m.h5"),
            "1h": os.path.exists(f"{model_path}/lstm_1h.h5")
        }
        return models
    
    def get_log_tail(self, lines=5):
        """Get last few lines from bot log"""
        try:
            if os.path.exists('bot_log.txt'):
                with open('bot_log.txt', 'r', encoding='utf-8', errors='ignore') as f:
                    all_lines = f.readlines()
                return all_lines[-lines:] if len(all_lines) > lines else all_lines
        except Exception as e:
            return [f"Log read error: {e}"]
        return ["No log file found"]
    
    def monitor_cycle(self):
        """Single monitoring cycle"""
        print(f"\n{'='*60}")
        print(f"🤖 CRYPTO TRADING BOT MONITOR - {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'='*60}")
        
        # Bot State
        state = self.get_bot_state()
        if "error" not in state:
            print(f"📊 BOT STATUS:")
            print(f"   💱 Current Pair: {state.get('current_pair', 'N/A')}")
            print(f"   💰 Balance USD: ${state.get('balance_usd', 0)}")
            print(f"   📈 Daily Profit: ${state.get('daily_profit', 0):.2f}")
            print(f"   🎯 Success Rate: {state.get('success_rate', 0):.1f}%")
            print(f"   🔄 Total Trades: {state.get('total_trades', 0)}")
        else:
            print(f"❌ Bot State Error: {state['error']}")
        
        # Configuration
        config = self.get_enhanced_config()
        if "error" not in config:
            # Check LSTM configuration properly
            lstm_enabled = False
            if config.get('lstm_predictor', {}).get('enabled', False):
                lstm_enabled = True
            elif config.get('use_lstm_prediction', False):
                lstm_enabled = True
                
            print(f"\n⚙️ CONFIGURATION:")
            print(f"   💱 Trading Pair: {config.get('current_pair', 'Unknown')}")
            print(f"   💰 Balance: ${config.get('balance_usd', 'Unknown')}")
            print(f"   🎯 Daily Target: ${config.get('daily_target_profit', 'Unknown')}")
            print(f"   🧠 LSTM AI: {'✅ Enabled' if lstm_enabled else '❌ Disabled'}")
        
        # LSTM Models Status
        models = self.check_lstm_models()
        model_count = sum(models.values())
        print(f"\n🧠 LSTM MODELS: {model_count}/4 available")
        for timeframe, exists in models.items():
            status = "✅" if exists else "❌"
            print(f"   {status} {timeframe} model")
        
        # Recent Activity
        logs = self.get_log_tail(3)
        print(f"\n📝 RECENT ACTIVITY:")
        for log in logs:
            if log.strip():
                print(f"   {log.strip()}")
        
        print(f"\n💓 Monitor running... (next check in {self.monitor_interval}s)")
    
    def run_monitor(self):
        """Main monitoring loop"""
        print("🚀 Starting Live Bot Monitor...")
        print(f"📊 Monitoring interval: {self.monitor_interval} seconds")
        print("🛑 Press Ctrl+C to stop")
        
        try:
            while self.running:
                self.monitor_cycle()
                time.sleep(self.monitor_interval)
        except KeyboardInterrupt:
            print("\n🛑 Monitor stopped by user")
        except Exception as e:
            print(f"\n❌ Monitor error: {e}")
        finally:
            self.running = False

if __name__ == "__main__":
    monitor = LiveBotMonitor()
    monitor.run_monitor()
