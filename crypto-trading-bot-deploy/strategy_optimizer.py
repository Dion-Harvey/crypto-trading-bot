#!/usr/bin/env python3
"""
Advanced Strategy Optimizer for Crypto Trading Bot

This module provides automated parameter optimization, backtesting,
and performance analysis for trading strategies.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
import logging
import json
import itertools
from datetime import datetime, timedelta
import concurrent.futures
from dataclasses import dataclass

@dataclass
class OptimizationResult:
    """Results from strategy optimization"""
    parameters: Dict[str, Any]
    performance_metrics: Dict[str, float]
    total_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    profit_factor: float
    total_trades: int

class AdvancedStrategyOptimizer:
    """Advanced strategy parameter optimization and backtesting"""
    
    def __init__(self, initial_balance: float = 1000.0):
        self.initial_balance = initial_balance
        self.logger = logging.getLogger(__name__)
        
        # Optimization parameter ranges
        self.parameter_ranges = {
            'rsi_period': [14, 16, 18, 20, 21, 22, 24],
            'rsi_oversold': [20, 22, 25, 28, 30],
            'rsi_overbought': [70, 72, 75, 78, 80],
            'bb_period': [18, 20, 22, 24],
            'bb_std_dev': [1.8, 2.0, 2.2, 2.4],
            'ma_fast': [3, 5, 7, 8],
            'ma_slow': [18, 20, 21, 24, 26],
            'confidence_threshold': [0.30, 0.35, 0.40, 0.45, 0.50],
            'stop_loss_pct': [0.015, 0.020, 0.025, 0.030],
            'take_profit_pct': [0.040, 0.050, 0.055, 0.060, 0.070],
            'volume_threshold': [1.5, 2.0, 2.5, 3.0],
            'volatility_threshold': [0.015, 0.020, 0.025, 0.030]
        }
        
        # Performance tracking
        self.optimization_history = []
        self.best_parameters = {}
        self.performance_baseline = None

# Legacy StrategyOptimizer for backward compatibility
class StrategyOptimizer:
    def __init__(self):
        self.trade_log_file = "trade_log.csv"
        self.performance_file = "strategy_performance.json"
        
    def load_trade_data(self):
        """Load and analyze trade data"""
        try:
            df = pd.read_csv(self.trade_log_file)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            return df
        except FileNotFoundError:
            print("❌ No trade log found. Start trading to generate data.")
            return None
    
    def calculate_metrics(self, df):
        """Calculate comprehensive performance metrics"""
        if df is None or len(df) < 2:
            return None
            
        # Basic metrics
        total_trades = len(df)
        buy_trades = df[df['action'] == 'BUY']
        sell_trades = df[df['action'] == 'SELL']
        
        # Calculate P&L for completed trade pairs
        trade_pairs = []
        balance_history = df['balance'].tolist()
        
        for i in range(1, len(df)):
            if df.iloc[i-1]['action'] == 'BUY' and df.iloc[i]['action'] == 'SELL':
                buy_price = df.iloc[i-1]['price']
                sell_price = df.iloc[i]['price']
                pnl = sell_price - buy_price
                pnl_pct = (sell_price - buy_price) / buy_price
                trade_pairs.append({
                    'buy_time': df.iloc[i-1]['timestamp'],
                    'sell_time': df.iloc[i]['timestamp'],
                    'buy_price': buy_price,
                    'sell_price': sell_price,
                    'pnl': pnl,
                    'pnl_pct': pnl_pct,
                    'hold_time': (df.iloc[i]['timestamp'] - df.iloc[i-1]['timestamp']).total_seconds() / 60
                })
        
        if not trade_pairs:
            return None
            
        trade_df = pd.DataFrame(trade_pairs)
        
        # Win/loss analysis
        wins = trade_df[trade_df['pnl_pct'] > 0]
        losses = trade_df[trade_df['pnl_pct'] <= 0]
        
        win_rate = len(wins) / len(trade_df) if len(trade_df) > 0 else 0
        avg_win = wins['pnl_pct'].mean() if len(wins) > 0 else 0
        avg_loss = losses['pnl_pct'].mean() if len(losses) > 0 else 0
        avg_hold_time = trade_df['hold_time'].mean()
        
        # Risk metrics
        profit_factor = abs(wins['pnl_pct'].sum() / losses['pnl_pct'].sum()) if len(losses) > 0 and losses['pnl_pct'].sum() != 0 else float('inf')
        max_consecutive_losses = self.calculate_max_consecutive_losses(trade_df)
        
        # Sharpe-like ratio (returns per unit of volatility)
        returns = trade_df['pnl_pct']
        sharpe_ratio = returns.mean() / returns.std() if returns.std() != 0 else 0
        
        return {
            'total_trades': len(trade_df),
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'avg_hold_time_minutes': avg_hold_time,
            'max_consecutive_losses': max_consecutive_losses,
            'sharpe_ratio': sharpe_ratio,
            'total_pnl_pct': trade_df['pnl_pct'].sum(),
            'best_trade': trade_df['pnl_pct'].max(),
            'worst_trade': trade_df['pnl_pct'].min(),
            'trade_data': trade_df
        }
    
    def calculate_max_consecutive_losses(self, trade_df):
        """Calculate maximum consecutive losses"""
        consecutive = 0
        max_consecutive = 0
        
        for pnl in trade_df['pnl_pct']:
            if pnl <= 0:
                consecutive += 1
                max_consecutive = max(max_consecutive, consecutive)
            else:
                consecutive = 0
                
        return max_consecutive
    
    def analyze_time_patterns(self, df):
        """Analyze performance by time of day and day of week"""
        if df is None or len(df) < 10:
            return None
            
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.day_name()
        
        # Group by hour and calculate average P&L
        hourly_perf = df.groupby('hour')['balance'].agg(['count', 'mean']).reset_index()
        daily_perf = df.groupby('day_of_week')['balance'].agg(['count', 'mean']).reset_index()
        
        return {
            'hourly_performance': hourly_perf.to_dict('records'),
            'daily_performance': daily_perf.to_dict('records')
        }
    
    def suggest_optimizations(self, metrics):
        """Generate optimization suggestions based on performance"""
        if metrics is None:
            return ["❌ Insufficient data for optimization suggestions."]
            
        suggestions = []
        
        # Win rate analysis
        if metrics['win_rate'] < 0.4:
            suggestions.append("🎯 Low win rate detected. Consider:")
            suggestions.append("   - Increase confidence thresholds (current: 0.35 → 0.45)")
            suggestions.append("   - Add more restrictive RSI filters (oversold < 30)")
            suggestions.append("   - Implement better trend filters")
        elif metrics['win_rate'] > 0.7:
            suggestions.append("✅ High win rate! Consider:")
            suggestions.append("   - Slightly reduce confidence thresholds to capture more opportunities")
            suggestions.append("   - Increase position sizes in high-confidence trades")
        
        # Profit factor analysis
        if metrics['profit_factor'] < 1.2:
            suggestions.append("📉 Low profit factor. Consider:")
            suggestions.append("   - Tighten stop losses (current: 3% → 2%)")
            suggestions.append("   - Extend take profits (current: 5% → 6%)")
            suggestions.append("   - Filter trades during high volatility periods")
        
        # Hold time analysis
        if metrics['avg_hold_time_minutes'] > 120:  # > 2 hours
            suggestions.append("⏱️ Long average hold times. Consider:")
            suggestions.append("   - Implement more aggressive take profits")
            suggestions.append("   - Add time-based exits (max hold: 90 minutes)")
        elif metrics['avg_hold_time_minutes'] < 15:  # < 15 minutes
            suggestions.append("⚡ Very short hold times. Consider:")
            suggestions.append("   - Increase minimum confidence requirements")
            suggestions.append("   - Add trend momentum confirmations")
        
        # Consecutive losses
        if metrics['max_consecutive_losses'] > 4:
            suggestions.append("🔴 High consecutive losses detected. Consider:")
            suggestions.append("   - Implement circuit breaker (pause after 3 losses)")
            suggestions.append("   - Reduce position sizes after losses")
            suggestions.append("   - Add market regime filters")
        
        # Risk-adjusted returns
        if metrics['sharpe_ratio'] < 0.5:
            suggestions.append("📊 Low risk-adjusted returns. Consider:")
            suggestions.append("   - Focus on higher-confidence signals only")
            suggestions.append("   - Implement volatility-based position sizing")
            suggestions.append("   - Add correlation filters with market trends")
        
        return suggestions
    
    def generate_parameter_recommendations(self, metrics):
        """Generate specific parameter recommendations"""
        if metrics is None:
            return {}
            
        recommendations = {
            "strategy_parameters": {},
            "risk_management": {},
            "position_sizing": {}
        }
        
        # Strategy parameter tuning based on performance
        if metrics['win_rate'] < 0.45:
            recommendations["strategy_parameters"] = {
                "rsi_oversold": 25,  # More conservative (from 30)
                "rsi_overbought": 75,  # More conservative (from 70)
                "bb_std_dev": 2.2,  # Wider bands (from 2.0)
                "confidence_threshold": 0.45,  # Higher threshold (from 0.35)
                "required_votes": 3  # Require more consensus (from 2)
            }
        else:
            recommendations["strategy_parameters"] = {
                "rsi_oversold": 30,
                "rsi_overbought": 70,
                "bb_std_dev": 2.0,
                "confidence_threshold": 0.35,
                "required_votes": 2
            }
        
        # Risk management tuning
        if metrics['profit_factor'] < 1.3:
            recommendations["risk_management"] = {
                "stop_loss_pct": 0.02,  # Tighter stop loss
                "take_profit_pct": 0.06,  # Wider take profit
                "max_hold_time_minutes": 90
            }
        else:
            recommendations["risk_management"] = {
                "stop_loss_pct": 0.03,
                "take_profit_pct": 0.05,
                "max_hold_time_minutes": 120
            }
        
        # Position sizing
        base_size = 15
        if metrics['sharpe_ratio'] > 1.0:
            base_size = 17  # Increase for good performance
        elif metrics['max_consecutive_losses'] > 3:
            base_size = 12  # Reduce for high risk
            
        recommendations["position_sizing"] = {
            "base_amount_usd": base_size,
            "volatility_adjustment": True,
            "confidence_scaling": True
        }
        
        return recommendations
    
    def run_full_analysis(self):
        """Run complete optimization analysis"""
        print("🔍 CRYPTO BOT PERFORMANCE ANALYSIS")
        print("=" * 50)
        
        # Load data
        df = self.load_trade_data()
        if df is None:
            return
            
        print(f"📊 Loaded {len(df)} trades")
        
        # Calculate metrics
        metrics = self.calculate_metrics(df)
        if metrics is None:
            print("❌ Insufficient trade pairs for analysis")
            return
        
        # Display current performance
        print(f"\n📈 CURRENT PERFORMANCE:")
        print(f"   Total Trades: {metrics['total_trades']}")
        print(f"   Win Rate: {metrics['win_rate']:.1%}")
        print(f"   Average Win: {metrics['avg_win']:.2%}")
        print(f"   Average Loss: {metrics['avg_loss']:.2%}")
        print(f"   Profit Factor: {metrics['profit_factor']:.2f}")
        print(f"   Avg Hold Time: {metrics['avg_hold_time_minutes']:.1f} minutes")
        print(f"   Max Consecutive Losses: {metrics['max_consecutive_losses']}")
        print(f"   Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
        print(f"   Total P&L: {metrics['total_pnl_pct']:.2%}")
        print(f"   Best Trade: {metrics['best_trade']:.2%}")
        print(f"   Worst Trade: {metrics['worst_trade']:.2%}")
        
        # Generate suggestions
        print(f"\n💡 OPTIMIZATION SUGGESTIONS:")
        suggestions = self.suggest_optimizations(metrics)
        for suggestion in suggestions:
            print(f"   {suggestion}")
        
        # Parameter recommendations
        print(f"\n⚙️ RECOMMENDED PARAMETERS:")
        recommendations = self.generate_parameter_recommendations(metrics)
        
        for category, params in recommendations.items():
            print(f"   {category.upper()}:")
            for param, value in params.items():
                print(f"     {param}: {value}")
        
        # Save recommendations
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"optimization_report_{timestamp}.json"
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics,
            "suggestions": suggestions,
            "recommendations": recommendations
        }
        
        # Remove trade_data for JSON serialization
        if 'trade_data' in report['metrics']:
            del report['metrics']['trade_data']
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n💾 Report saved to: {output_file}")
        
        return report

    def optimize_strategy_parameters(self, historical_data: pd.DataFrame, 
                                   strategy_class, optimization_method: str = 'grid_search',
                                   max_iterations: int = 1000) -> OptimizationResult:
        """
        Optimize strategy parameters using various methods
        """
        self.logger.info(f"Starting parameter optimization with {optimization_method}")
        
        if optimization_method == 'grid_search':
            return self._grid_search_optimization(historical_data, strategy_class)
        elif optimization_method == 'random_search':
            return self._random_search_optimization(historical_data, strategy_class, max_iterations)
        elif optimization_method == 'genetic_algorithm':
            return self._genetic_algorithm_optimization(historical_data, strategy_class, max_iterations)
        elif optimization_method == 'bayesian':
            return self._bayesian_optimization(historical_data, strategy_class, max_iterations)
        else:
            raise ValueError(f"Unknown optimization method: {optimization_method}")
    
    def backtest_strategy(self, historical_data: pd.DataFrame, strategy_class, 
                         parameters: Dict[str, Any], 
                         transaction_cost: float = 0.001) -> Dict[str, Any]:
        """
        Comprehensive strategy backtesting
        """
        try:
            # Initialize strategy with parameters
            if hasattr(strategy_class, '__call__'):
                strategy = strategy_class(**parameters)
            else:
                strategy = strategy_class
                for param, value in parameters.items():
                    if hasattr(strategy, param):
                        setattr(strategy, param, value)
            
            # Backtest variables
            balance = self.initial_balance
            position = 0.0
            trades = []
            equity_curve = []
            peak_balance = balance
            max_drawdown = 0.0
            
            # Trade tracking
            entry_price = 0.0
            in_position = False
            
            # Process each time period
            for i in range(1, len(historical_data)):
                current_data = historical_data.iloc[:i+1]
                current_price = current_data['close'].iloc[-1]
                
                # Skip if insufficient data
                if len(current_data) < 50:
                    equity_curve.append(balance)
                    continue
                
                # Get strategy signal
                try:
                    if hasattr(strategy, 'get_consensus_signal'):
                        signal = strategy.get_consensus_signal(current_data)
                    elif hasattr(strategy, 'get_enhanced_consensus_signal'):
                        signal = strategy.get_enhanced_consensus_signal(current_data)
                    elif hasattr(strategy, 'get_signal'):
                        signal = strategy.get_signal(current_data)
                    else:
                        # Default signal structure
                        signal = {'action': 'HOLD', 'confidence': 0.0}
                except Exception as e:
                    self.logger.warning(f"Strategy signal error at index {i}: {e}")
                    signal = {'action': 'HOLD', 'confidence': 0.0}
                
                # Process signal
                action = signal.get('action', 'HOLD')
                confidence = signal.get('confidence', 0.0)
                
                # Apply confidence threshold
                confidence_threshold = parameters.get('confidence_threshold', 0.4)
                if confidence < confidence_threshold:
                    action = 'HOLD'
                
                # Execute trades
                if action == 'BUY' and not in_position:
                    # Buy signal
                    position_size = balance * 0.95  # Use 95% of balance
                    position = position_size / current_price
                    balance = balance - position_size
                    entry_price = current_price
                    in_position = True
                    
                    # Record trade
                    trade = {
                        'timestamp': current_data.index[-1],
                        'action': 'BUY',
                        'price': current_price,
                        'quantity': position,
                        'balance': balance,
                        'confidence': confidence
                    }
                    trades.append(trade)
                    
                elif action == 'SELL' and in_position:
                    # Sell signal
                    proceeds = position * current_price * (1 - transaction_cost)
                    balance += proceeds
                    
                    # Calculate trade P&L
                    trade_return = (current_price - entry_price) / entry_price
                    
                    # Record trade
                    trade = {
                        'timestamp': current_data.index[-1],
                        'action': 'SELL',
                        'price': current_price,
                        'quantity': position,
                        'balance': balance,
                        'confidence': confidence,
                        'entry_price': entry_price,
                        'return': trade_return,
                        'pnl': proceeds - (position * entry_price)
                    }
                    trades.append(trade)
                    
                    position = 0.0
                    in_position = False
                    entry_price = 0.0
                
                # Risk management (stop loss / take profit)
                if in_position:
                    stop_loss_pct = parameters.get('stop_loss_pct', 0.025)
                    take_profit_pct = parameters.get('take_profit_pct', 0.055)
                    
                    price_change = (current_price - entry_price) / entry_price
                    
                    if price_change <= -stop_loss_pct or price_change >= take_profit_pct:
                        # Stop loss or take profit triggered
                        proceeds = position * current_price * (1 - transaction_cost)
                        balance += proceeds
                        
                        trade = {
                            'timestamp': current_data.index[-1],
                            'action': 'RISK_EXIT',
                            'price': current_price,
                            'quantity': position,
                            'balance': balance,
                            'entry_price': entry_price,
                            'return': price_change,
                            'exit_reason': 'STOP_LOSS' if price_change <= -stop_loss_pct else 'TAKE_PROFIT',
                            'pnl': proceeds - (position * entry_price)
                        }
                        trades.append(trade)
                        
                        position = 0.0
                        in_position = False
                        entry_price = 0.0
                
                # Calculate current portfolio value
                portfolio_value = balance + (position * current_price if in_position else 0)
                equity_curve.append(portfolio_value)
                
                # Update drawdown
                if portfolio_value > peak_balance:
                    peak_balance = portfolio_value
                
                current_drawdown = (peak_balance - portfolio_value) / peak_balance
                max_drawdown = max(max_drawdown, current_drawdown)
            
            # Calculate performance metrics
            performance_metrics = self._calculate_performance_metrics(
                trades, equity_curve, historical_data, max_drawdown
            )
            
            return {
                'parameters': parameters,
                'performance_metrics': performance_metrics,
                'trades': trades,
                'equity_curve': equity_curve,
                'final_balance': equity_curve[-1] if equity_curve else self.initial_balance
            }
            
        except Exception as e:
            self.logger.error(f"Backtest error: {e}")
            return {
                'parameters': parameters,
                'performance_metrics': {'total_return': -1.0, 'sharpe_ratio': -10.0, 'max_drawdown': 1.0},
                'trades': [],
                'equity_curve': [],
                'final_balance': 0.0
            }
    
    def walk_forward_optimization(self, historical_data: pd.DataFrame, strategy_class,
                                 train_period: int = 1000, test_period: int = 200,
                                 step_size: int = 100) -> Dict[str, Any]:
        """
        Walk-forward analysis for robust parameter optimization
        """
        results = []
        
        start_idx = train_period
        while start_idx + test_period < len(historical_data):
            # Training period
            train_data = historical_data.iloc[start_idx-train_period:start_idx]
            
            # Test period
            test_data = historical_data.iloc[start_idx:start_idx+test_period]
            
            # Optimize on training data
            optimization_result = self.optimize_strategy_parameters(
                train_data, strategy_class, 'random_search', max_iterations=100
            )
            
            # Test on out-of-sample data
            test_result = self.backtest_strategy(
                test_data, strategy_class, optimization_result.parameters
            )
            
            results.append({
                'train_period': (start_idx-train_period, start_idx),
                'test_period': (start_idx, start_idx+test_period),
                'optimized_parameters': optimization_result.parameters,
                'train_performance': optimization_result.performance_metrics,
                'test_performance': test_result['performance_metrics']
            })
            
            start_idx += step_size
        
        # Aggregate results
        stability_metrics = self._analyze_parameter_stability(results)
        
        return {
            'walk_forward_results': results,
            'stability_metrics': stability_metrics,
            'recommended_parameters': self._get_stable_parameters(results)
        }
    
    def monte_carlo_analysis(self, historical_data: pd.DataFrame, strategy_class,
                           parameters: Dict[str, Any], num_simulations: int = 1000) -> Dict[str, Any]:
        """
        Monte Carlo analysis for risk assessment
        """
        returns = historical_data['close'].pct_change().dropna()
        
        simulation_results = []
        
        for _ in range(num_simulations):
            # Bootstrap returns
            simulated_returns = np.random.choice(returns, len(returns), replace=True)
            
            # Create simulated price series
            simulated_prices = [historical_data['close'].iloc[0]]
            for ret in simulated_returns:
                simulated_prices.append(simulated_prices[-1] * (1 + ret))
            
            # Create simulated OHLCV data
            simulated_data = historical_data.copy()
            simulated_data['close'] = simulated_prices[:len(simulated_data)]
            
            # Run backtest
            result = self.backtest_strategy(simulated_data, strategy_class, parameters)
            simulation_results.append(result['performance_metrics'])
        
        # Analyze results
        returns_distribution = [r['total_return'] for r in simulation_results]
        sharpe_distribution = [r['sharpe_ratio'] for r in simulation_results]
        drawdown_distribution = [r['max_drawdown'] for r in simulation_results]
        
        return {
            'num_simulations': num_simulations,
            'return_statistics': {
                'mean': np.mean(returns_distribution),
                'std': np.std(returns_distribution),
                'percentiles': np.percentile(returns_distribution, [5, 25, 50, 75, 95])
            },
            'sharpe_statistics': {
                'mean': np.mean(sharpe_distribution),
                'std': np.std(sharpe_distribution),
                'percentiles': np.percentile(sharpe_distribution, [5, 25, 50, 75, 95])
            },
            'drawdown_statistics': {
                'mean': np.mean(drawdown_distribution),
                'std': np.std(drawdown_distribution),
                'percentiles': np.percentile(drawdown_distribution, [5, 25, 50, 75, 95])
            },
            'risk_metrics': {
                'var_5': np.percentile(returns_distribution, 5),
                'cvar_5': np.mean([r for r in returns_distribution if r <= np.percentile(returns_distribution, 5)]),
                'probability_of_loss': sum(1 for r in returns_distribution if r < 0) / len(returns_distribution)
            }
        }
    
    # =============================================================================
    # OPTIMIZATION METHODS
    # =============================================================================
    
    def _grid_search_optimization(self, historical_data: pd.DataFrame, 
                                strategy_class) -> OptimizationResult:
        """Grid search parameter optimization"""
        best_result = None
        best_score = -np.inf
        
        # Generate parameter combinations
        param_names = list(self.parameter_ranges.keys())
        param_values = list(self.parameter_ranges.values())
        
        total_combinations = np.prod([len(values) for values in param_values])
        self.logger.info(f"Testing {total_combinations} parameter combinations")
        
        for i, combination in enumerate(itertools.product(*param_values)):
            parameters = dict(zip(param_names, combination))
            
            # Run backtest
            result = self.backtest_strategy(historical_data, strategy_class, parameters)
            
            # Calculate composite score
            score = self._calculate_optimization_score(result['performance_metrics'])
            
            if score > best_score:
                best_score = score
                best_result = OptimizationResult(
                    parameters=parameters,
                    performance_metrics=result['performance_metrics'],
                    total_return=result['performance_metrics']['total_return'],
                    sharpe_ratio=result['performance_metrics']['sharpe_ratio'],
                    max_drawdown=result['performance_metrics']['max_drawdown'],
                    win_rate=result['performance_metrics']['win_rate'],
                    profit_factor=result['performance_metrics']['profit_factor'],
                    total_trades=result['performance_metrics']['total_trades']
                )
            
            if (i + 1) % 100 == 0:
                self.logger.info(f"Tested {i + 1}/{total_combinations} combinations")
        
        return best_result
    
    def _random_search_optimization(self, historical_data: pd.DataFrame, 
                                  strategy_class, max_iterations: int) -> OptimizationResult:
        """Random search parameter optimization"""
        best_result = None
        best_score = -np.inf
        
        for i in range(max_iterations):
            # Generate random parameters
            parameters = {}
            for param_name, param_range in self.parameter_ranges.items():
                parameters[param_name] = np.random.choice(param_range)
            
            # Run backtest
            result = self.backtest_strategy(historical_data, strategy_class, parameters)
            
            # Calculate composite score
            score = self._calculate_optimization_score(result['performance_metrics'])
            
            if score > best_score:
                best_score = score
                best_result = OptimizationResult(
                    parameters=parameters,
                    performance_metrics=result['performance_metrics'],
                    total_return=result['performance_metrics']['total_return'],
                    sharpe_ratio=result['performance_metrics']['sharpe_ratio'],
                    max_drawdown=result['performance_metrics']['max_drawdown'],
                    win_rate=result['performance_metrics']['win_rate'],
                    profit_factor=result['performance_metrics']['profit_factor'],
                    total_trades=result['performance_metrics']['total_trades']
                )
            
            if (i + 1) % 100 == 0:
                self.logger.info(f"Random search: {i + 1}/{max_iterations} iterations")
        
        return best_result
    
    def _genetic_algorithm_optimization(self, historical_data: pd.DataFrame, 
                                      strategy_class, max_iterations: int) -> OptimizationResult:
        """Genetic algorithm parameter optimization"""
        population_size = 50
        mutation_rate = 0.1
        crossover_rate = 0.8
        
        # Initialize population
        population = []
        for _ in range(population_size):
            individual = {}
            for param_name, param_range in self.parameter_ranges.items():
                individual[param_name] = np.random.choice(param_range)
            population.append(individual)
        
        best_result = None
        best_score = -np.inf
        
        for generation in range(max_iterations // population_size):
            # Evaluate population
            fitness_scores = []
            for individual in population:
                result = self.backtest_strategy(historical_data, strategy_class, individual)
                score = self._calculate_optimization_score(result['performance_metrics'])
                fitness_scores.append((score, individual, result))
                
                if score > best_score:
                    best_score = score
                    best_result = OptimizationResult(
                        parameters=individual,
                        performance_metrics=result['performance_metrics'],
                        total_return=result['performance_metrics']['total_return'],
                        sharpe_ratio=result['performance_metrics']['sharpe_ratio'],
                        max_drawdown=result['performance_metrics']['max_drawdown'],
                        win_rate=result['performance_metrics']['win_rate'],
                        profit_factor=result['performance_metrics']['profit_factor'],
                        total_trades=result['performance_metrics']['total_trades']
                    )
            
            # Sort by fitness
            fitness_scores.sort(key=lambda x: x[0], reverse=True)
            
            # Select parents (top 50%)
            parents = [individual for _, individual, _ in fitness_scores[:population_size//2]]
            
            # Create new population
            new_population = parents.copy()  # Keep best individuals
            
            # Generate offspring
            while len(new_population) < population_size:
                if np.random.random() < crossover_rate:
                    # Crossover
                    parent1, parent2 = np.random.choice(len(parents), 2, replace=False)
                    child = self._crossover(parents[parent1], parents[parent2])
                else:
                    # Mutation
                    parent = np.random.choice(parents)
                    child = self._mutate(parent, mutation_rate)
                
                new_population.append(child)
            
            population = new_population
            
            if generation % 10 == 0:
                self.logger.info(f"GA Generation {generation}: Best score = {best_score:.4f}")
        
        return best_result
    
    def _bayesian_optimization(self, historical_data: pd.DataFrame, 
                             strategy_class, max_iterations: int) -> OptimizationResult:
        """Bayesian optimization (simplified implementation)"""
        # This is a simplified version - in practice, you'd use libraries like scikit-optimize
        # For now, implement as intelligent random search with exploitation/exploration
        
        best_result = None
        best_score = -np.inf
        explored_params = []
        scores = []
        
        for i in range(max_iterations):
            if i < 20:
                # Exploration phase - random search
                parameters = {}
                for param_name, param_range in self.parameter_ranges.items():
                    parameters[param_name] = np.random.choice(param_range)
            else:
                # Exploitation phase - guided search based on previous results
                parameters = self._intelligent_parameter_selection(explored_params, scores)
            
            # Run backtest
            result = self.backtest_strategy(historical_data, strategy_class, parameters)
            score = self._calculate_optimization_score(result['performance_metrics'])
            
            explored_params.append(parameters)
            scores.append(score)
            
            if score > best_score:
                best_score = score
                best_result = OptimizationResult(
                    parameters=parameters,
                    performance_metrics=result['performance_metrics'],
                    total_return=result['performance_metrics']['total_return'],
                    sharpe_ratio=result['performance_metrics']['sharpe_ratio'],
                    max_drawdown=result['performance_metrics']['max_drawdown'],
                    win_rate=result['performance_metrics']['win_rate'],
                    profit_factor=result['performance_metrics']['profit_factor'],
                    total_trades=result['performance_metrics']['total_trades']
                )
            
            if (i + 1) % 50 == 0:
                self.logger.info(f"Bayesian optimization: {i + 1}/{max_iterations} iterations")
        
        return best_result
    
    # =============================================================================
    # HELPER METHODS
    # =============================================================================
    
    def _calculate_performance_metrics(self, trades: List[Dict], equity_curve: List[float],
                                     historical_data: pd.DataFrame, max_drawdown: float) -> Dict[str, float]:
        """Calculate comprehensive performance metrics"""
        if not equity_curve or len(equity_curve) < 2:
            return {
                'total_return': -1.0,
                'sharpe_ratio': -10.0,
                'max_drawdown': 1.0,
                'win_rate': 0.0,
                'profit_factor': 0.0,
                'total_trades': 0,
                'avg_trade_return': 0.0,
                'volatility': 1.0
            }
        
        # Calculate returns
        returns = pd.Series(equity_curve).pct_change().dropna()
        total_return = (equity_curve[-1] - self.initial_balance) / self.initial_balance
        
        # Sharpe ratio (assuming 0% risk-free rate)
        if len(returns) > 1 and returns.std() > 0:
            sharpe_ratio = returns.mean() / returns.std() * np.sqrt(252)  # Annualized
        else:
            sharpe_ratio = -10.0
        
        # Trade-based metrics
        completed_trades = [t for t in trades if 'return' in t]
        
        if completed_trades:
            trade_returns = [t['return'] for t in completed_trades]
            winning_trades = [r for r in trade_returns if r > 0]
            losing_trades = [r for r in trade_returns if r < 0]
            
            win_rate = len(winning_trades) / len(trade_returns)
            avg_trade_return = np.mean(trade_returns)
            
            # Profit factor
            gross_profit = sum(winning_trades) if winning_trades else 0
            gross_loss = abs(sum(losing_trades)) if losing_trades else 1e-6
            profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
        else:
            win_rate = 0.0
            avg_trade_return = 0.0
            profit_factor = 0.0
        
        # Volatility
        volatility = returns.std() * np.sqrt(252) if len(returns) > 1 else 1.0
        
        return {
            'total_return': total_return,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'total_trades': len(completed_trades),
            'avg_trade_return': avg_trade_return,
            'volatility': volatility
        }
    
    def _calculate_optimization_score(self, metrics: Dict[str, float]) -> float:
        """Calculate composite optimization score"""
        # Weighted combination of metrics
        weights = {
            'total_return': 0.3,
            'sharpe_ratio': 0.25,
            'max_drawdown': -0.2,  # Negative weight (lower is better)
            'win_rate': 0.15,
            'profit_factor': 0.1
        }
        
        score = 0.0
        for metric, weight in weights.items():
            value = metrics.get(metric, 0.0)
            
            # Normalize metrics
            if metric == 'total_return':
                normalized_value = min(value, 2.0)  # Cap at 200% return
            elif metric == 'sharpe_ratio':
                normalized_value = min(value / 3.0, 1.0)  # Normalize to 0-1
            elif metric == 'max_drawdown':
                normalized_value = value  # Already 0-1, lower is better
            elif metric == 'win_rate':
                normalized_value = value  # Already 0-1
            elif metric == 'profit_factor':
                normalized_value = min(value / 3.0, 1.0)  # Normalize to 0-1
            else:
                normalized_value = value
            
            score += weight * normalized_value
        
        # Penalty for insufficient trades
        if metrics.get('total_trades', 0) < 10:
            score *= 0.5  # Penalize strategies with too few trades
        
        return score
    
    def _crossover(self, parent1: Dict, parent2: Dict) -> Dict:
        """Genetic algorithm crossover"""
        child = {}
        for param_name in parent1.keys():
            if np.random.random() < 0.5:
                child[param_name] = parent1[param_name]
            else:
                child[param_name] = parent2[param_name]
        return child
    
    def _mutate(self, individual: Dict, mutation_rate: float) -> Dict:
        """Genetic algorithm mutation"""
        mutated = individual.copy()
        for param_name, param_range in self.parameter_ranges.items():
            if np.random.random() < mutation_rate:
                mutated[param_name] = np.random.choice(param_range)
        return mutated
    
    def _intelligent_parameter_selection(self, explored_params: List[Dict], 
                                       scores: List[float]) -> Dict:
        """Intelligent parameter selection for Bayesian-like optimization"""
        # Find best parameters
        best_idx = np.argmax(scores)
        best_params = explored_params[best_idx]
        
        # Add some exploration around best parameters
        new_params = {}
        for param_name, param_range in self.parameter_ranges.items():
            current_value = best_params[param_name]
            
            if np.random.random() < 0.7:  # 70% chance to stay near best
                # Find current index in range
                try:
                    current_idx = param_range.index(current_value)
                    # Select nearby value
                    if current_idx > 0 and current_idx < len(param_range) - 1:
                        new_params[param_name] = param_range[current_idx + np.random.choice([-1, 0, 1])]
                    else:
                        new_params[param_name] = current_value
                except ValueError:
                    new_params[param_name] = np.random.choice(param_range)
            else:  # 30% chance for exploration
                new_params[param_name] = np.random.choice(param_range)
        
        return new_params
    
    def _analyze_parameter_stability(self, walk_forward_results: List[Dict]) -> Dict:
        """Analyze parameter stability across walk-forward tests"""
        param_variations = {}
        
        # Collect all parameter values
        for result in walk_forward_results:
            params = result['optimized_parameters']
            for param_name, param_value in params.items():
                if param_name not in param_variations:
                    param_variations[param_name] = []
                param_variations[param_name].append(param_value)
        
        # Calculate stability metrics
        stability_metrics = {}
        for param_name, values in param_variations.items():
            unique_values = len(set(values))
            total_values = len(values)
            stability_score = 1 - (unique_values / total_values)
            
            stability_metrics[param_name] = {
                'stability_score': stability_score,
                'unique_values': unique_values,
                'most_common': max(set(values), key=values.count),
                'value_distribution': {val: values.count(val) for val in set(values)}
            }
        
        return stability_metrics
    
    def _get_stable_parameters(self, walk_forward_results: List[Dict]) -> Dict:
        """Get most stable parameters from walk-forward analysis"""
        stability_metrics = self._analyze_parameter_stability(walk_forward_results)
        
        stable_params = {}
        for param_name, metrics in stability_metrics.items():
            # Use most common value for stable parameters
            stable_params[param_name] = metrics['most_common']
        
        return stable_params
    
    def save_optimization_results(self, filepath: str, results: Dict) -> None:
        """Save optimization results to file"""
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2, default=str)
    
    def load_optimization_results(self, filepath: str) -> Dict:
        """Load optimization results from file"""
        with open(filepath, 'r') as f:
            return json.load(f)
