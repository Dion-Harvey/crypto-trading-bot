#!/usr/bin/env python3
"""
Enhanced Configuration System for Crypto Trading Bot
Centralizes all configurable parameters with validation and documentation
"""

import json
import os
from datetime import datetime

class BotConfig:
    def __init__(self, config_file="enhanced_config.json"):
        self.config_file = config_file
        self.default_config = {
            "trading": {
                "symbol": "BTC/USDT",
                "base_amount_usd": 15,
                "min_amount_usd": 8,
                "max_amount_usd": 19,
                "use_intelligent_orders": True,
                "limit_order_timeout_seconds": 20,
                "trade_cooldown_seconds": 300
            },
            "risk_management": {
                "stop_loss_pct": 0.025,
                "take_profit_pct": 0.055,
                "emergency_exit_pct": 0.08,
                "max_drawdown_pct": 0.12,
                "daily_loss_limit_usd": 2.50,
                "max_consecutive_losses": 3,
                "consecutive_loss_cooldown_minutes": 15,
                "daily_loss_pause_hours": 1
            },
            "strategy_parameters": {
                "confidence_threshold": 0.40,
                "high_volatility_confidence_multiplier": 1.3,
                "extreme_condition_confidence_multiplier": 0.9,
                "min_consensus_votes": 2,
                "strong_consensus_votes": 3,
                "rsi_period": 21,
                "rsi_oversold": 25,
                "rsi_overbought": 75,
                "rsi_momentum_threshold": 2,
                "bb_period": 20,
                "bb_std_dev": 2.2,
                "bb_touch_tolerance_pct": 0.015,
                "mr_fast_ma": 5,
                "mr_slow_ma": 21,
                "mr_signal_line": 9,
                "mr_deviation_threshold": 0.008,
                "vwap_period": 30,
                "vwap_deviation_threshold": 0.004,
                "vwap_volume_surge_threshold": 1.5
            },
            "market_filters": {
                "high_volatility_threshold": 0.025,
                "very_high_volatility_threshold": 0.03,
                "consolidation_volatility_threshold": 0.008,
                "strong_trend_threshold": 0.03,
                "volume_confirmation_threshold": 1.2,
                "trend_detection_periods": [5, 10, 20, 50],
                "trend_thresholds": [0.015, 0.025, 0.04, 0.06]
            },
            "position_sizing": {
                "volatility_factors": {
                    "very_high": 0.6,    # > 3%
                    "high": 0.75,        # > 2%
                    "medium": 0.9,       # > 1.5%
                    "low": 1.1           # <= 1.5%
                },
                "confidence_scaling": {
                    "enabled": True,
                    "min_factor": 0.7,
                    "max_factor": 1.3,
                    "scaling_multiplier": 1.2
                },
                "loss_adjustment": {
                    "enabled": True,
                    "min_factor": 0.4,
                    "reduction_per_loss": 0.2
                },
                "drawdown_adjustment": {
                    "enabled": True,
                    "threshold": 0.1,
                    "min_factor": 0.3,
                    "scaling_factor": 3
                },
                "time_adjustment": {
                    "enabled": True,
                    "low_liquidity_hours": [2, 3, 4, 5, 6],
                    "low_liquidity_factor": 0.8
                }
            },
            "adaptive_optimization": {
                "enabled": True,
                "review_period_days": 3,
                "min_trades_for_adjustment": 10,
                "adjustment_sensitivity": 0.1,
                "auto_adjust_confidence": True,
                "auto_adjust_risk": True,
                "auto_adjust_position_size": True
            },
            "lstm_predictor": {
                "enabled": True,
                "sequence_length": 30,
                "prediction_horizon": 5,
                "lstm_units": 64,
                "dropout_rate": 0.2,
                "learning_rate": 0.001,
                "batch_size": 32,
                "epochs": 50,
                "validation_split": 0.2,
                "min_training_samples": 200,
                "confidence_threshold": 0.65,
                "min_accuracy_threshold": 0.60,
                "retrain_interval_hours": 24,
                "model_dir": "models/lstm",
                "enhancement_timeframes": ["5m", "15m"],
                "max_enhancement_boost": 0.20
            },
            "logging": {
                "log_level": "INFO",
                "log_individual_strategies": True,
                "log_market_conditions": True,
                "log_position_sizing": True,
                "log_risk_management": True,
                "performance_tracking": True
            },
            "system": {
                "loop_interval_seconds": 60,
                "connection_retry_attempts": 3,
                "connection_retry_delay": 5,
                "state_save_frequency": "after_each_trade",
                "backup_config_on_change": True
            }
        }
        self.load_config()
        self.last_config_mtime = 0  # Track file modification time for runtime reload
        
    def load_config(self):
        """Load configuration from file or create default"""
        try:
            with open(self.config_file, 'r') as f:
                loaded_config = json.load(f)
            
            # Merge with defaults to handle missing keys
            self.config = self._deep_merge(self.default_config, loaded_config)
            
            # Update modification time
            self.last_config_mtime = os.path.getmtime(self.config_file)
            print(f"✅ Loaded enhanced configuration from {self.config_file}")
            
        except FileNotFoundError:
            print(f"⚠️ Config file not found, creating default: {self.config_file}")
            self.config = self.default_config.copy()
            self.save_config()
        except Exception as e:
            print(f"❌ Error loading config: {e}")
            self.config = self.default_config.copy()
            
    def reload_config_if_changed(self):
        """Reload configuration if file has been modified (for runtime updates)"""
        try:
            current_mtime = os.path.getmtime(self.config_file)
            if current_mtime > self.last_config_mtime:
                old_symbol = self.config.get('trading', {}).get('symbol', 'Unknown')
                self.load_config()
                new_symbol = self.config.get('trading', {}).get('symbol', 'Unknown')
                
                if old_symbol != new_symbol:
                    print(f"🔄 CONFIG RELOADED: Trading pair changed {old_symbol} → {new_symbol}")
                    return True
                else:
                    print(f"🔄 CONFIG RELOADED: Configuration updated")
                    return True
            return False
        except Exception as e:
            print(f"⚠️ Config reload check failed: {e}")
            return False
            
            # Save merged config to ensure all new defaults are included
            self.save_config()
            
        except FileNotFoundError:
            self.config = self.default_config.copy()
            self.save_config()
            print(f"🆕 Created enhanced configuration: {self.config_file}")
        except json.JSONDecodeError as e:
            print(f"⚠️ Invalid JSON in config file: {e}")
            self.config = self.default_config.copy()
            self.save_config()
    
    def _deep_merge(self, default, loaded):
        """Deep merge loaded config with defaults"""
        result = default.copy()
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result
    
    def save_config(self):
        """Save current configuration to file"""
        if self.config.get('system', {}).get('backup_config_on_change', True):
            self._create_backup()
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"⚠️ Failed to save config: {e}")
    
    def _create_backup(self):
        """Create backup of current config"""
        if os.path.exists(self.config_file):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{self.config_file}.backup_{timestamp}"
            try:
                import shutil
                shutil.copy2(self.config_file, backup_name)
            except:
                pass  # Backup is best effort
    
    def get(self, section, key=None, default=None):
        """Get configuration value"""
        if key is None:
            return self.config.get(section, default)
        return self.config.get(section, {}).get(key, default)
    
    def set(self, section, key, value):
        """Set configuration value"""
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
        self.save_config()
    
    def get_trading_config(self):
        """Get trading configuration"""
        return self.config['trading']
    
    def get_risk_config(self):
        """Get risk management configuration"""
        return self.config['risk_management']
    
    def get_strategy_config(self):
        """Get strategy parameters configuration"""
        return self.config['strategy_parameters']
    
    def get_market_filters_config(self):
        """Get market filters configuration"""
        return self.config['market_filters']
    
    def get_position_sizing_config(self):
        """Get position sizing configuration"""
        return self.config['position_sizing']
    
    def get_api_config(self):
        """Get API configuration for exchange connections"""
        return self.config.get('api_keys', {}).get('binance', {})
    
    def validate_config(self):
        """Validate configuration values"""
        errors = []
        
        # Validate risk management
        risk = self.config['risk_management']
        if risk['stop_loss_pct'] >= risk['take_profit_pct']:
            errors.append("Stop loss must be less than take profit")
        
        if risk['stop_loss_pct'] <= 0 or risk['stop_loss_pct'] > 0.2:
            errors.append("Stop loss should be between 0% and 20%")
        
        # Validate position sizing
        trading = self.config['trading']
        if trading['min_amount_usd'] > trading['max_amount_usd']:
            errors.append("Min amount cannot be greater than max amount")
        
        # Validate strategy parameters
        strategy = self.config['strategy_parameters']
        if strategy['confidence_threshold'] <= 0 or strategy['confidence_threshold'] > 1:
            errors.append("Confidence threshold must be between 0 and 1")
        
        if errors:
            print("⚠️ Configuration validation errors:")
            for error in errors:
                print(f"   • {error}")
            return False
        
        return True
    
    def get_current_trading_symbol(self):
        """Get current active trading symbol"""
        return self.config.get('trading', {}).get('symbol', 'BTC/USDT')
    
    def get_supported_pairs(self):
        """Get list of all supported trading pairs"""
        return self.config.get('trading', {}).get('supported_pairs', ['BTC/USDT'])
    
    def print_summary(self):
        """Print configuration summary"""
        print("\n⚙️ CURRENT CONFIGURATION SUMMARY:")
        print(f"   Symbol: {self.config['trading']['symbol']}")
        print(f"   Base Trade Size: ${self.config['trading']['base_amount_usd']}")
        print(f"   Stop Loss: {self.config['risk_management']['stop_loss_pct']:.1%}")
        print(f"   Take Profit: {self.config['risk_management']['take_profit_pct']:.1%}")
        print(f"   Confidence Threshold: {self.config['strategy_parameters']['confidence_threshold']:.3f}")
        print(f"   Trade Cooldown: {self.config['trading']['trade_cooldown_seconds']//60} minutes")
        print(f"   Intelligent Orders: {'✅' if self.config['trading']['use_intelligent_orders'] else '❌'}")
        print(f"   Auto-Optimization: {'✅' if self.config['adaptive_optimization']['enabled'] else '❌'}")

# Global config instance
_bot_config = None

def get_bot_config():
    """Get the global bot configuration instance"""
    global _bot_config
    if _bot_config is None:
        _bot_config = BotConfig()
    return _bot_config

if __name__ == "__main__":
    config = BotConfig()
    config.print_summary()
    is_valid = config.validate_config()
    print(f"\nConfiguration valid: {'✅' if is_valid else '❌'}")
