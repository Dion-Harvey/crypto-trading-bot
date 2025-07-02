#!/usr/bin/env python3
"""
Dynamic Configuration Manager for Crypto Trading Bot
Automatically adjusts parameters based on performance feedback
"""

import json
import os
from datetime import datetime, timedelta
import pandas as pd

class DynamicConfig:
    def __init__(self, config_file="dynamic_config.json"):
        self.config_file = config_file
        self.default_config = {
            "strategy_parameters": {
                "rsi_period": 21,
                "rsi_oversold": 25,
                "rsi_overbought": 75,
                "bb_period": 20,
                "bb_std_dev": 2.2,
                "ma_fast": 5,
                "ma_slow": 21,
                "vwap_period": 30,
                "confidence_threshold": 0.40,
                "min_consensus_votes": 2
            },
            "risk_management": {
                "stop_loss_pct": 0.025,
                "take_profit_pct": 0.055,
                "max_drawdown_pct": 0.12,
                "daily_loss_limit": 2.50,
                "max_consecutive_losses": 3,
                "trade_cooldown_seconds": 300,
                "max_hold_time_minutes": 90
            },
            "position_sizing": {
                "base_amount_usd": 15,
                "min_amount_usd": 8,
                "max_amount_usd": 19,
                "volatility_adjustment": True,
                "confidence_scaling": True,
                "loss_reduction_factor": 0.8,
                "drawdown_reduction_factor": 0.7
            },
            "market_filters": {
                "high_volatility_threshold": 0.025,
                "volume_surge_threshold": 1.5,
                "strong_trend_threshold": 0.03,
                "consolidation_volatility": 0.008
            },
            "adaptive_settings": {
                "performance_review_days": 3,
                "min_trades_for_adjustment": 10,
                "adjustment_sensitivity": 0.1,
                "last_adjustment": None
            }
        }
        self.load_config()
    
    def load_config(self):
        """Load configuration from file or create default"""
        try:
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
            print(f"✅ Loaded configuration from {self.config_file}")
        except FileNotFoundError:
            self.config = self.default_config.copy()
            self.save_config()
            print(f"🆕 Created default configuration: {self.config_file}")
    
    def save_config(self):
        """Save current configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2, default=str)
    
    def get_strategy_params(self):
        """Get current strategy parameters"""
        return self.config["strategy_parameters"]
    
    def get_risk_params(self):
        """Get current risk management parameters"""
        return self.config["risk_management"]
    
    def get_position_params(self):
        """Get current position sizing parameters"""
        return self.config["position_sizing"]
    
    def get_market_filters(self):
        """Get current market filter parameters"""
        return self.config["market_filters"]
    
    def analyze_recent_performance(self, days_back=3):
        """Analyze recent performance for parameter adjustment"""
        try:
            df = pd.read_csv("trade_log.csv")
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Filter recent trades
            cutoff_date = datetime.now() - timedelta(days=days_back)
            recent_df = df[df['timestamp'] >= cutoff_date]
            
            if len(recent_df) < 4:  # Need at least 2 trade pairs
                return None
            
            # Calculate trade pairs and metrics
            trade_pairs = []
            for i in range(1, len(recent_df)):
                if recent_df.iloc[i-1]['action'] == 'BUY' and recent_df.iloc[i]['action'] == 'SELL':
                    buy_price = recent_df.iloc[i-1]['price']
                    sell_price = recent_df.iloc[i]['price']
                    pnl_pct = (sell_price - buy_price) / buy_price
                    hold_time = (recent_df.iloc[i]['timestamp'] - recent_df.iloc[i-1]['timestamp']).total_seconds() / 60
                    trade_pairs.append({
                        'pnl_pct': pnl_pct,
                        'hold_time': hold_time,
                        'buy_price': buy_price,
                        'sell_price': sell_price
                    })
            
            if not trade_pairs:
                return None
            
            trade_df = pd.DataFrame(trade_pairs)
            
            # Calculate key metrics
            win_rate = len(trade_df[trade_df['pnl_pct'] > 0]) / len(trade_df)
            avg_pnl = trade_df['pnl_pct'].mean()
            avg_hold_time = trade_df['hold_time'].mean()
            max_loss = trade_df['pnl_pct'].min()
            max_gain = trade_df['pnl_pct'].max()
            
            # Count consecutive losses
            consecutive_losses = 0
            for pnl in trade_df['pnl_pct'].iloc[::-1]:  # Reverse order
                if pnl <= 0:
                    consecutive_losses += 1
                else:
                    break
            
            return {
                'total_trades': len(trade_df),
                'win_rate': win_rate,
                'avg_pnl': avg_pnl,
                'avg_hold_time': avg_hold_time,
                'max_loss': max_loss,
                'max_gain': max_gain,
                'consecutive_losses': consecutive_losses,
                'total_pnl': trade_df['pnl_pct'].sum()
            }
            
        except Exception as e:
            print(f"⚠️ Could not analyze performance: {e}")
            return None
    
    def adjust_parameters(self, performance_data):
        """Dynamically adjust parameters based on performance"""
        if performance_data is None:
            return False
        
        adjustments_made = []
        sensitivity = self.config["adaptive_settings"]["adjustment_sensitivity"]
        
        # Adjust based on win rate
        if performance_data['win_rate'] < 0.4:  # Low win rate
            # Make parameters more conservative
            if self.config["strategy_parameters"]["confidence_threshold"] < 0.5:
                self.config["strategy_parameters"]["confidence_threshold"] += 0.05
                adjustments_made.append("Increased confidence threshold (low win rate)")
            
            if self.config["strategy_parameters"]["rsi_oversold"] > 20:
                self.config["strategy_parameters"]["rsi_oversold"] -= 2
                adjustments_made.append("Lowered RSI oversold threshold")
            
            if self.config["strategy_parameters"]["rsi_overbought"] < 80:
                self.config["strategy_parameters"]["rsi_overbought"] += 2
                adjustments_made.append("Raised RSI overbought threshold")
        
        elif performance_data['win_rate'] > 0.65:  # High win rate but maybe missing opportunities
            # Make parameters slightly more aggressive
            if self.config["strategy_parameters"]["confidence_threshold"] > 0.3:
                self.config["strategy_parameters"]["confidence_threshold"] -= 0.02
                adjustments_made.append("Decreased confidence threshold (high win rate)")
        
        # Adjust based on average P&L
        if performance_data['avg_pnl'] < -0.005:  # Losing on average
            # Tighter risk management
            if self.config["risk_management"]["stop_loss_pct"] > 0.015:
                self.config["risk_management"]["stop_loss_pct"] -= 0.005
                adjustments_made.append("Tightened stop loss")
            
            if self.config["position_sizing"]["base_amount_usd"] > 12:
                self.config["position_sizing"]["base_amount_usd"] -= 1
                adjustments_made.append("Reduced position size")
        
        # Adjust based on hold time
        if performance_data['avg_hold_time'] > 120:  # Holding too long
            if self.config["risk_management"]["max_hold_time_minutes"] > 60:
                self.config["risk_management"]["max_hold_time_minutes"] -= 15
                adjustments_made.append("Reduced max hold time")
            
            if self.config["risk_management"]["take_profit_pct"] < 0.08:
                self.config["risk_management"]["take_profit_pct"] += 0.005
                adjustments_made.append("Increased take profit target")
        
        elif performance_data['avg_hold_time'] < 20:  # Exiting too quickly
            if self.config["risk_management"]["take_profit_pct"] > 0.03:
                self.config["risk_management"]["take_profit_pct"] -= 0.005
                adjustments_made.append("Decreased take profit target")
        
        # Adjust based on consecutive losses
        if performance_data['consecutive_losses'] >= 3:
            # More conservative approach
            if self.config["risk_management"]["max_consecutive_losses"] > 2:
                self.config["risk_management"]["max_consecutive_losses"] -= 1
                adjustments_made.append("Reduced max consecutive losses")
            
            if self.config["strategy_parameters"]["min_consensus_votes"] < 3:
                self.config["strategy_parameters"]["min_consensus_votes"] += 1
                adjustments_made.append("Increased required consensus votes")
        
        # Adjust based on maximum loss
        if performance_data['max_loss'] < -0.04:  # Large single loss
            if self.config["risk_management"]["stop_loss_pct"] > 0.015:
                self.config["risk_management"]["stop_loss_pct"] -= 0.005
                adjustments_made.append("Tightened stop loss due to large loss")
        
        # Update last adjustment time
        if adjustments_made:
            self.config["adaptive_settings"]["last_adjustment"] = datetime.now().isoformat()
            self.save_config()
            
            print(f"🔧 PARAMETER ADJUSTMENTS MADE:")
            for adjustment in adjustments_made:
                print(f"   • {adjustment}")
            
            return True
        
        return False
    
    def should_adjust(self):
        """Check if enough time has passed and enough trades made for adjustment"""
        last_adj = self.config["adaptive_settings"]["last_adjustment"]
        if last_adj:
            last_adj_date = datetime.fromisoformat(last_adj)
            days_since = (datetime.now() - last_adj_date).days
            if days_since < self.config["adaptive_settings"]["performance_review_days"]:
                return False
        
        # Check if we have enough recent trades
        try:
            df = pd.read_csv("trade_log.csv")
            recent_cutoff = datetime.now() - timedelta(days=self.config["adaptive_settings"]["performance_review_days"])
            recent_trades = len(df[pd.to_datetime(df['timestamp']) >= recent_cutoff])
            return recent_trades >= self.config["adaptive_settings"]["min_trades_for_adjustment"]
        except:
            return False
    
    def auto_optimize(self):
        """Main method to automatically optimize parameters"""
        if not self.should_adjust():
            print("⏳ Not ready for parameter adjustment yet")
            return False
        
        print("🔍 Analyzing recent performance for auto-optimization...")
        
        performance = self.analyze_recent_performance()
        if performance is None:
            print("❌ Insufficient data for optimization")
            return False
        
        print(f"📊 Recent Performance ({self.config['adaptive_settings']['performance_review_days']} days):")
        print(f"   Trades: {performance['total_trades']}")
        print(f"   Win Rate: {performance['win_rate']:.1%}")
        print(f"   Avg P&L: {performance['avg_pnl']:.2%}")
        print(f"   Total P&L: {performance['total_pnl']:.2%}")
        print(f"   Avg Hold: {performance['avg_hold_time']:.1f} min")
        print(f"   Consecutive Losses: {performance['consecutive_losses']}")
        
        # Make adjustments
        adjusted = self.adjust_parameters(performance)
        
        if not adjusted:
            print("✅ Current parameters are performing well - no adjustments needed")
        
        return adjusted

# Convenience function for the main bot
def get_optimized_config():
    """Get current optimized configuration"""
    config_manager = DynamicConfig()
    
    # Auto-optimize if conditions are met
    config_manager.auto_optimize()
    
    return {
        'strategy': config_manager.get_strategy_params(),
        'risk': config_manager.get_risk_params(),
        'position': config_manager.get_position_params(),
        'filters': config_manager.get_market_filters()
    }

if __name__ == "__main__":
    config_manager = DynamicConfig()
    config_manager.auto_optimize()
