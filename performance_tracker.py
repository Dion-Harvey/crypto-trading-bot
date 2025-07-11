# =============================================================================
# PERFORMANCE TRACKER - Advanced Analytics for Strategy Performance
# =============================================================================

import pandas as pd
import json
from datetime import datetime, timedelta
import os

class PerformanceTracker:
    """Track and analyze strategy performance in real-time"""

    def __init__(self):
        self.performance_file = "strategy_performance.json"
        self.load_performance_data()

    def load_performance_data(self):
        """Load existing performance data or initialize new structure"""
        if os.path.exists(self.performance_file):
            try:
                with open(self.performance_file, 'r') as f:
                    self.data = json.load(f)
            except Exception:
                self.data = self.init_performance_structure()
        else:
            self.data = self.init_performance_structure()

    def init_performance_structure(self):
        """Initialize performance tracking structure"""
        return {
            "strategy_performance": {
                "RSI": {"wins": 0, "losses": 0, "total_pnl": 0},
                "Bollinger": {"wins": 0, "losses": 0, "total_pnl": 0},
                "MA-Contrarian": {"wins": 0, "losses": 0, "total_pnl": 0},
                "VWAP": {"wins": 0, "losses": 0, "total_pnl": 0}
            },
            "market_condition_performance": {
                "high_volatility": {"wins": 0, "losses": 0, "total_pnl": 0},
                "normal_volatility": {"wins": 0, "losses": 0, "total_pnl": 0},
                "strong_uptrend": {"wins": 0, "losses": 0, "total_pnl": 0},
                "strong_downtrend": {"wins": 0, "losses": 0, "total_pnl": 0}
            },
            "time_of_day_performance": {},
            "confidence_threshold_analysis": {
                "0.2-0.4": {"wins": 0, "losses": 0, "total_pnl": 0},
                "0.4-0.6": {"wins": 0, "losses": 0, "total_pnl": 0},
                "0.6-0.8": {"wins": 0, "losses": 0, "total_pnl": 0},
                "0.8-1.0": {"wins": 0, "losses": 0, "total_pnl": 0}
            },
            "trade_history": []
        }

    def save_performance_data(self):
        """Save performance data to file"""
        try:
            with open(self.performance_file, 'w') as f:
                json.dump(self.data, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving performance data: {e}")

    def record_trade_signal(self, signal, market_conditions):
        """Record when a trade signal is generated"""
        trade_record = {
            "timestamp": datetime.now().isoformat(),
            "signal": signal,
            "market_conditions": market_conditions,
            "entry_price": None,
            "exit_price": None,
            "pnl": None,
            "outcome": "pending"
        }

        self.data["trade_history"].append(trade_record)
        self.save_performance_data()
        return len(self.data["trade_history"]) - 1  # Return index for later updates

    def update_trade_outcome(self, trade_index, entry_price, exit_price=None):
        """Update trade outcome when position is closed"""
        if trade_index >= len(self.data["trade_history"]):
            return

        trade = self.data["trade_history"][trade_index]

        if entry_price and not trade["entry_price"]:
            trade["entry_price"] = entry_price

        if exit_price:
            trade["exit_price"] = exit_price

            # Calculate P&L
            if trade["signal"]["action"] == "BUY":
                pnl = exit_price - trade["entry_price"]
            else:  # SELL
                pnl = trade["entry_price"] - exit_price

            trade["pnl"] = pnl
            trade["outcome"] = "win" if pnl > 0 else "loss"

            # Update strategy performance
            self.update_strategy_performance(trade)

            # Update market condition performance
            self.update_market_condition_performance(trade)

            # Update confidence threshold analysis
            self.update_confidence_analysis(trade)

        self.save_performance_data()

    def update_strategy_performance(self, trade):
        """Update individual strategy performance metrics"""
        signal = trade["signal"]
        pnl = trade["pnl"]
        outcome = trade["outcome"]

        # Update each strategy that voted for this action
        for i, individual_signal in enumerate(signal["individual_signals"]):
            strategy_names = ["RSI", "Bollinger", "MA-Contrarian", "VWAP"]

            if i < len(strategy_names) and individual_signal["action"] == signal["action"]:
                strategy = strategy_names[i]
                self.data["strategy_performance"][strategy][outcome + "s"] += 1
                self.data["strategy_performance"][strategy]["total_pnl"] += pnl

    def update_market_condition_performance(self, trade):
        """Update market condition performance metrics"""
        market_conditions = trade["market_conditions"]
        pnl = trade["pnl"]
        outcome = trade["outcome"]

        # Update volatility performance
        vol_key = "high_volatility" if market_conditions["is_high_volatility"] else "normal_volatility"
        self.data["market_condition_performance"][vol_key][outcome + "s"] += 1
        self.data["market_condition_performance"][vol_key]["total_pnl"] += pnl

        # Update trend performance
        if market_conditions["strong_uptrend"]:
            self.data["market_condition_performance"]["strong_uptrend"][outcome + "s"] += 1
            self.data["market_condition_performance"]["strong_uptrend"]["total_pnl"] += pnl
        elif market_conditions["strong_downtrend"]:
            self.data["market_condition_performance"]["strong_downtrend"][outcome + "s"] += 1
            self.data["market_condition_performance"]["strong_downtrend"]["total_pnl"] += pnl

    def update_confidence_analysis(self, trade):
        """Update confidence threshold analysis"""
        confidence = trade["signal"]["confidence"]
        pnl = trade["pnl"]
        outcome = trade["outcome"]

        # Determine confidence bucket
        if 0.2 <= confidence < 0.4:
            bucket = "0.2-0.4"
        elif 0.4 <= confidence < 0.6:
            bucket = "0.4-0.6"
        elif 0.6 <= confidence < 0.8:
            bucket = "0.6-0.8"
        elif 0.8 <= confidence <= 1.0:
            bucket = "0.8-1.0"
        else:
            return  # Outside expected range

        self.data["confidence_threshold_analysis"][bucket][outcome + "s"] += 1
        self.data["confidence_threshold_analysis"][bucket]["total_pnl"] += pnl

    def get_strategy_win_rates(self):
        """Calculate win rates for each strategy"""
        win_rates = {}
        for strategy, stats in self.data["strategy_performance"].items():
            total_trades = stats["wins"] + stats["losses"]
            if total_trades > 0:
                win_rate = stats["wins"] / total_trades
                avg_pnl = stats["total_pnl"] / total_trades
                win_rates[strategy] = {
                    "win_rate": round(win_rate * 100, 1),
                    "total_trades": total_trades,
                    "avg_pnl": round(avg_pnl, 2),
                    "total_pnl": round(stats["total_pnl"], 2)
                }
        return win_rates

    def get_best_market_conditions(self):
        """Identify the most profitable market conditions"""
        best_conditions = {}
        for condition, stats in self.data["market_condition_performance"].items():
            total_trades = stats["wins"] + stats["losses"]
            if total_trades > 0:
                win_rate = stats["wins"] / total_trades
                avg_pnl = stats["total_pnl"] / total_trades
                best_conditions[condition] = {
                    "win_rate": round(win_rate * 100, 1),
                    "total_trades": total_trades,
                    "avg_pnl": round(avg_pnl, 2)
                }
        return best_conditions

    def get_optimal_confidence_threshold(self):
        """Find the confidence threshold with best performance"""
        best_threshold = None
        best_score = -float('inf')

        for threshold, stats in self.data["confidence_threshold_analysis"].items():
            total_trades = stats["wins"] + stats["losses"]
            if total_trades >= 5:  # Minimum trades for statistical significance
                win_rate = stats["wins"] / total_trades
                avg_pnl = stats["total_pnl"] / total_trades
                # Combined score: win rate * average PnL
                score = win_rate * avg_pnl

                if score > best_score:
                    best_score = score
                    best_threshold = {
                        "range": threshold,
                        "win_rate": round(win_rate * 100, 1),
                        "avg_pnl": round(avg_pnl, 2),
                        "total_trades": total_trades
                    }

        return best_threshold

    def print_performance_summary(self):
        """Print comprehensive performance summary"""
        print("\n" + "="*60)
        print("📊 ADVANCED PERFORMANCE ANALYTICS")
        print("="*60)

        # Strategy performance
        print("\n🎯 STRATEGY WIN RATES:")
        win_rates = self.get_strategy_win_rates()
        for strategy, stats in win_rates.items():
            print(f"   {strategy:12}: {stats['win_rate']:5.1f}% win rate ({stats['total_trades']} trades) | Avg PnL: ${stats['avg_pnl']:6.2f} | Total: ${stats['total_pnl']:7.2f}")

        # Market conditions
        print("\n🌊 BEST MARKET CONDITIONS:")
        best_conditions = self.get_best_market_conditions()
        for condition, stats in best_conditions.items():
            print(f"   {condition:15}: {stats['win_rate']:5.1f}% win rate ({stats['total_trades']} trades) | Avg PnL: ${stats['avg_pnl']:6.2f}")

        # Optimal confidence
        print("\n🎲 OPTIMAL CONFIDENCE THRESHOLD:")
        optimal = self.get_optimal_confidence_threshold()
        if optimal:
            print(f"   Range {optimal['range']}: {optimal['win_rate']}% win rate | Avg PnL: ${optimal['avg_pnl']} | Trades: {optimal['total_trades']}")
        else:
            print("   Insufficient data for analysis")

        print("\n📈 RECOMMENDATIONS:")
        self.print_recommendations()

    def print_recommendations(self):
        """Print actionable recommendations based on performance data"""
        win_rates = self.get_strategy_win_rates()

        if win_rates:
            # Find best and worst performing strategies
            best_strategy = max(win_rates.items(), key=lambda x: x[1]['win_rate'])
            worst_strategy = min(win_rates.items(), key=lambda x: x[1]['win_rate'])

            print(f"   💡 Best performing strategy: {best_strategy[0]} ({best_strategy[1]['win_rate']}% win rate)")
            print(f"   ⚠️  Worst performing strategy: {worst_strategy[0]} ({worst_strategy[1]['win_rate']}% win rate)")

            # Confidence recommendations
            optimal = self.get_optimal_confidence_threshold()
            if optimal:
                print(f"   🎯 Consider using confidence threshold in range: {optimal['range']}")

        # Market condition recommendations
        best_conditions = self.get_best_market_conditions()
        if best_conditions:
            best_condition = max(best_conditions.items(), key=lambda x: x[1]['win_rate'])
            print(f"   🌟 Most profitable market condition: {best_condition[0]} ({best_condition[1]['win_rate']}% win rate)")

# Global instance
performance_tracker = PerformanceTracker()
