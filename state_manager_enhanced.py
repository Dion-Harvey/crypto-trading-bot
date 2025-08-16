#!/usr/bin/env python3
"""
Enhanced state manager module for crypto trading bot
"""
import json
import os
import datetime
import shutil

class StateManager:
    def __init__(self):
        self.state_file = 'bot_state.json'
        self.state = self.load_state()
        
    def load_state(self):
        """Load bot state from file"""
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading state: {e}")
        
        # Return default state
        return {
            'holding_position': False,
            'entry_price': None,
            'stop_loss_price': None,
            'take_profit_price': None,
            'trade_id': None,
            'active_trade_index': None,
            'consecutive_losses': 0,
            'last_trade_time': 0,
            'total_trades': 0,
            'winning_trades': 0
        }
    
    def save_state(self):
        """Save current state to file"""
        try:
            # Create backup
            if os.path.exists(self.state_file):
                backup_name = f"{self.state_file}_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                shutil.copy2(self.state_file, backup_name)
            
            # Save current state
            with open(self.state_file, 'w') as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            print(f"Error saving state: {e}")
    
    def is_in_trade(self):
        """Check if currently in a trade"""
        return self.state.get('holding_position', False)
    
    def enter_trade(self, entry_price, stop_loss_price=None, take_profit_price=None, trade_id=None, active_trade_index=None):
        """Record entering a trade"""
        self.state.update({
            'holding_position': True,
            'entry_price': entry_price,
            'stop_loss_price': stop_loss_price,
            'take_profit_price': take_profit_price,
            'trade_id': trade_id,
            'active_trade_index': active_trade_index
        })
        self.save_state()
    
    def exit_trade(self, exit_reason=''):
        """Record exiting a trade"""
        self.state.update({
            'holding_position': False,
            'entry_price': None,
            'stop_loss_price': None,
            'take_profit_price': None,
            'trade_id': None,
            'active_trade_index': None
        })
        self.state['total_trades'] = self.state.get('total_trades', 0) + 1
        self.save_state()
    
    def update_trading_state(self, **kwargs):
        """Update trading state with provided parameters"""
        self.state.update(kwargs)
        self.save_state()
    
    def update_consecutive_losses(self, count):
        """Update consecutive losses count"""
        self.state['consecutive_losses'] = count
        self.save_state()
    
    def get_consecutive_losses(self):
        """Get current consecutive losses count"""
        return self.state.get('consecutive_losses', 0)
    
    def get_trading_state(self):
        """Get current trading state"""
        return self.state
    
    def get_risk_state(self):
        """Get current risk state for backwards compatibility"""
        return {
            'account_peak_value': 20.0,
            'max_drawdown_from_peak': 0.0,
            'daily_pnl_start_balance': None,
            'daily_pnl_date': None
        }
    
    def print_current_state(self):
        """Print current state for debugging"""
        print(f"Current State:")
        print(f"  In Trade: {self.state.get('holding_position', False)}")
        print(f"  Entry Price: {self.state.get('entry_price')}")
        print(f"  Stop Loss: {self.state.get('stop_loss_price')}")
        print(f"  Take Profit: {self.state.get('take_profit_price')}")
        print(f"  Consecutive Losses: {self.state.get('consecutive_losses', 0)}")

# Global instance
_state_manager = None

def get_state_manager():
    """Get or create global state manager instance"""
    global _state_manager
    if _state_manager is None:
        _state_manager = StateManager()
    return _state_manager

# For backward compatibility
state_manager = get_state_manager()
