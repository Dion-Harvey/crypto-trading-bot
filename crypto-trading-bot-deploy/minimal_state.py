#!/usr/bin/env python3
"""
Minimal state manager module
"""
import json
import os

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
        except:
            pass
        return {
            'holding_position': False,
            'entry_price': None,
            'consecutive_losses': 0
        }
    
    def save_state(self):
        """Save state to file"""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            print(f"Error saving state: {e}")
    
    def is_in_trade(self):
        """Check if currently in a trade"""
        return self.state.get('holding_position', False)
    
    def print_current_state(self):
        """Print current bot state"""
        in_trade = "✅ YES" if self.state.get('holding_position', False) else "❌ NO"
        consecutive_losses = self.state.get('consecutive_losses', 0)
        account_peak = self.state.get('account_peak_value', 20.0)
        max_drawdown = self.state.get('max_drawdown', 0.0)
        
        print(f"📊 CURRENT BOT STATE:")
        print(f"   In Trade: {in_trade}")
        print(f"   Consecutive Losses: {consecutive_losses}")
        print(f"   Account Peak: ${account_peak:.2f}")
        print(f"   Max Drawdown: {max_drawdown:.3f}")
    
    def enter_trade(self, entry_price, stop_loss_price, take_profit_price, trade_id=None, active_trade_index=None):
        """Enter a trade"""
        self.state.update({
            'holding_position': True,
            'entry_price': entry_price,
            'stop_loss_price': stop_loss_price,
            'take_profit_price': take_profit_price,
            'trade_id': trade_id,
            'active_trade_index': active_trade_index
        })
        self.save_state()
    
    def exit_trade(self, reason=""):
        """Exit a trade"""
        self.state.update({
            'holding_position': False,
            'entry_price': None,
            'stop_loss_price': None,
            'take_profit_price': None,
            'trade_id': None,
            'active_trade_index': None
        })
        self.save_state()
    
    def update_consecutive_losses(self, losses):
        """Update consecutive losses"""
        self.state['consecutive_losses'] = losses
        self.save_state()
    
    def update_trading_state(self, holding_position, entry_price=None, stop_loss_price=None, take_profit_price=None):
        """Update trading state"""
        self.state.update({
            'holding_position': holding_position,
            'entry_price': entry_price,
            'stop_loss_price': stop_loss_price,
            'take_profit_price': take_profit_price
        })
        self.save_state()

# Create global instance
state_manager = StateManager()
