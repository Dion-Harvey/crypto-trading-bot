#!/usr/bin/env python3
"""
Persistent State Manager for Crypto Trading Bot
Handles bot state persistence across restarts and crashes
"""

import json
import os
from datetime import datetime
import threading

class StateManager:
    def __init__(self, state_file="bot_state.json"):
        self.state_file = state_file
        self.state_lock = threading.Lock()
        self.default_state = {
            "bot_info": {
                "last_updated": None,
                "version": "1.0",
                "bot_id": "btc_optimized_bot"
            },
            "trading_state": {
                "holding_position": False,
                "entry_price": None,
                "stop_loss_price": None,
                "take_profit_price": None,
                "trade_id": None,
                "entry_timestamp": None,
                "consecutive_losses": 0,
                "last_trade_time": 0,
                "active_trade_index": None
            },
            "risk_management": {
                "account_peak_value": 20.0,
                "max_drawdown_from_peak": 0.0,
                "daily_pnl_start_balance": None,
                "daily_pnl_date": None
            },
            "performance": {
                "session_start_time": None,
                "total_trades_session": 0,
                "profitable_trades_session": 0
            }
        }
        self.load_state()
    
    def load_state(self):
        """Load state from file or create default"""
        try:
            with open(self.state_file, 'r') as f:
                self.state = json.load(f)
            print(f"✅ Loaded bot state from {self.state_file}")
            
            # Validate and merge with default structure
            merged_state = self._merge_with_default(self.state)
            if merged_state != self.state:
                self.state = merged_state
                self.save_state()
                print("🔄 Updated state structure")
                
        except FileNotFoundError:
            self.state = self.default_state.copy()
            self.save_state()
            print(f"🆕 Created new bot state: {self.state_file}")
        except json.JSONDecodeError:
            print(f"⚠️ Corrupted state file - creating backup and using defaults")
            if os.path.exists(self.state_file):
                backup_name = f"{self.state_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                os.rename(self.state_file, backup_name)
            self.state = self.default_state.copy()
            self.save_state()
    
    def _merge_with_default(self, loaded_state):
        """Merge loaded state with default structure to handle version upgrades"""
        merged = self.default_state.copy()
        
        for section, defaults in merged.items():
            if section in loaded_state:
                if isinstance(defaults, dict):
                    for key, default_value in defaults.items():
                        if key in loaded_state[section]:
                            merged[section][key] = loaded_state[section][key]
                else:
                    merged[section] = loaded_state[section]
        
        return merged
    
    def save_state(self):
        """Save current state to file"""
        with self.state_lock:
            self.state["bot_info"]["last_updated"] = datetime.now().isoformat()
            try:
                with open(self.state_file, 'w') as f:
                    json.dump(self.state, f, indent=2, default=str)
            except Exception as e:
                print(f"⚠️ Failed to save state: {e}")
    
    def get_trading_state(self):
        """Get current trading state"""
        return self.state["trading_state"].copy()
    
    def update_trading_state(self, **kwargs):
        """Update trading state with new values"""
        with self.state_lock:
            for key, value in kwargs.items():
                if key in self.state["trading_state"]:
                    self.state["trading_state"][key] = value
            self.save_state()
    
    def enter_trade(self, entry_price, stop_loss_price, take_profit_price, trade_id=None, active_trade_index=None):
        """Record entering a trade"""
        with self.state_lock:
            self.state["trading_state"].update({
                "holding_position": True,
                "entry_price": entry_price,
                "stop_loss_price": stop_loss_price,
                "take_profit_price": take_profit_price,
                "trade_id": trade_id,
                "entry_timestamp": datetime.now().isoformat(),
                "active_trade_index": active_trade_index
            })
            self.save_state()
        print(f"💾 Trade entry saved to state: ${entry_price:.2f}")
    
    def exit_trade(self, exit_reason="MANUAL"):
        """Record exiting a trade"""
        with self.state_lock:
            # Preserve some stats before clearing
            was_profitable = False
            if self.state["trading_state"]["entry_price"]:
                # We can't determine profitability without exit price, but we can track attempts
                pass
                
            self.state["trading_state"].update({
                "holding_position": False,
                "entry_price": None,
                "stop_loss_price": None,
                "take_profit_price": None,
                "trade_id": None,
                "entry_timestamp": None,
                "active_trade_index": None
            })
            self.save_state()
        print(f"💾 Trade exit saved to state: {exit_reason}")
    
    def update_consecutive_losses(self, count):
        """Update consecutive losses count"""
        self.update_trading_state(consecutive_losses=count)
    
    def update_last_trade_time(self, timestamp):
        """Update last trade timestamp"""
        self.update_trading_state(last_trade_time=timestamp)
    
    def get_risk_state(self):
        """Get current risk management state"""
        return self.state["risk_management"].copy()
    
    def update_risk_state(self, **kwargs):
        """Update risk management state"""
        with self.state_lock:
            for key, value in kwargs.items():
                if key in self.state["risk_management"]:
                    self.state["risk_management"][key] = value
            self.save_state()
    
    def is_in_trade(self):
        """Check if bot is currently in a trade"""
        return self.state["trading_state"]["holding_position"]
    
    def get_current_trade_info(self):
        """Get current trade information if in trade"""
        if self.is_in_trade():
            return {
                "entry_price": self.state["trading_state"]["entry_price"],
                "stop_loss_price": self.state["trading_state"]["stop_loss_price"],
                "take_profit_price": self.state["trading_state"]["take_profit_price"],
                "entry_timestamp": self.state["trading_state"]["entry_timestamp"],
                "trade_id": self.state["trading_state"]["trade_id"],
                "active_trade_index": self.state["trading_state"]["active_trade_index"]
            }
        return None
    
    def print_current_state(self):
        """Print current state summary"""
        ts = self.state["trading_state"]
        rs = self.state["risk_management"]
        
        print("\n📊 CURRENT BOT STATE:")
        print(f"   In Trade: {'✅ YES' if ts['holding_position'] else '❌ NO'}")
        
        if ts['holding_position']:
            print(f"   Entry Price: ${ts['entry_price']:.2f}")
            print(f"   Stop Loss: ${ts['stop_loss_price']:.2f}")
            print(f"   Take Profit: ${ts['take_profit_price']:.2f}")
            print(f"   Entry Time: {ts['entry_timestamp']}")
            
        print(f"   Consecutive Losses: {ts['consecutive_losses']}")
        print(f"   Account Peak: ${rs['account_peak_value']:.2f}")
        print(f"   Max Drawdown: {rs['max_drawdown_from_peak']:.3f}")

# Global state manager instance
state_manager = StateManager()

def get_state_manager():
    """Get the global state manager instance"""
    return state_manager
