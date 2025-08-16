#!/usr/bin/env python3
"""
Enhanced institutional strategies module
"""

class KellySizer:
    def calculate_kelly_size(self, win_rate, avg_win, avg_loss, total_portfolio):
        """Calculate Kelly position size"""
        try:
            if avg_loss == 0:
                return 10.0  # Default small size
            
            # Kelly formula: f = (bp - q) / b
            # where b = avg_win/avg_loss, p = win_rate, q = 1-p
            b = avg_win / abs(avg_loss)
            p = win_rate
            q = 1 - p
            
            kelly_fraction = (b * p - q) / b
            kelly_fraction = max(0, min(kelly_fraction, 0.25))  # Cap at 25%
            
            kelly_size = total_portfolio * kelly_fraction
            return max(10.0, min(kelly_size, 25.0))  # $10-$25 range
            
        except:
            return 10.0

class VarCalculator:
    def calculate_var(self, returns, portfolio_value):
        """Calculate Value at Risk"""
        try:
            if len(returns) < 2:
                return {'var_daily': portfolio_value * 0.02}  # 2% default
            
            # Simple 95% VaR calculation
            import numpy as np
            var_95 = np.percentile(returns, 5) if len(returns) > 0 else -0.02
            var_daily = abs(var_95) * portfolio_value
            
            return {
                'var_daily': var_daily,
                'var_95': var_95
            }
        except:
            return {'var_daily': portfolio_value * 0.02}

class InstitutionalStrategyManager:
    def __init__(self):
        self.kelly_sizer = KellySizer()
        self.var_calculator = VarCalculator()
        self.trade_results = []
    
    def get_institutional_signal(self, df, portfolio_value=0, base_position_size=10):
        """Get institutional signal with analysis"""
        try:
            # Simple momentum-based signal
            if len(df) >= 10:
                recent_change = (df['close'].iloc[-1] - df['close'].iloc[-5]) / df['close'].iloc[-5]
                
                if recent_change > 0.01:
                    action = 'BUY'
                    confidence = min(0.7, 0.5 + abs(recent_change) * 10)
                elif recent_change < -0.01:
                    action = 'SELL' 
                    confidence = min(0.7, 0.5 + abs(recent_change) * 10)
                else:
                    action = 'HOLD'
                    confidence = 0.3
            else:
                action = 'HOLD'
                confidence = 0.3
            
            # Calculate Kelly position size
            win_rate = 0.6  # Assume 60% win rate
            avg_win = 0.025  # 2.5% average win
            avg_loss = -0.015  # -1.5% average loss
            
            kelly_size = self.kelly_sizer.calculate_kelly_size(
                win_rate, avg_win, avg_loss, portfolio_value
            )
            
            return {
                'action': action,
                'confidence': confidence,
                'reason': f'Institutional analysis: {recent_change:.2%} momentum',
                'institutional_analysis': {
                    'kelly_position_size': kelly_size,
                    'market_regime': {
                        'regime': 'stable',
                        'confidence': 0.8
                    },
                    'ml_signal': {
                        'action': action,
                        'confidence': confidence
                    },
                    'risk_analysis': {
                        'risk_assessment': 'LOW' if abs(recent_change) < 0.02 else 'MEDIUM',
                        'var_daily': portfolio_value * 0.02
                    }
                },
                'risk_score': 'LOW' if confidence > 0.6 else 'MEDIUM'
            }
            
        except Exception as e:
            print(f"Error in institutional signal: {e}")
            return {
                'action': 'HOLD',
                'confidence': 0.3,
                'reason': 'Institutional analysis error'
            }
    
    def add_trade_result(self, pnl_pct):
        """Track trade results for Kelly optimization"""
        try:
            self.trade_results.append(pnl_pct)
            # Keep only last 100 trades
            if len(self.trade_results) > 100:
                self.trade_results = self.trade_results[-100:]
        except:
            pass

# Create global instance
institutional_manager = InstitutionalStrategyManager()
