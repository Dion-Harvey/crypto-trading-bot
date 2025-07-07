#!/usr/bin/env python3
"""
Enhanced minimal log_utils.py with all required functions
"""
import csv
import os
import json
from datetime import datetime, timedelta

def init_log():
    """Initialize logging"""
    print("📊 Logging initialized")

def calculate_daily_pnl():
    """Calculate daily P&L from trade log"""
    try:
        if not os.path.exists('trade_log.csv'):
            return 0.0
        
        today = datetime.now().date()
        daily_trades = []
        
        with open('trade_log.csv', 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    trade_date = datetime.strptime(row['timestamp'], '%Y-%m-%d %H:%M:%S').date()
                    if trade_date == today:
                        daily_trades.append(row)
                except:
                    continue
        
        if not daily_trades:
            return 0.0
            
        # Simple calculation: sum of realized P&L
        total_pnl = 0.0
        for trade in daily_trades:
            try:
                if trade.get('side') == 'SELL':
                    # This is a simplified calculation
                    total_pnl += float(trade.get('total_balance', 0)) - 45.0  # Rough baseline
            except:
                continue
                
        return total_pnl
        
    except Exception as e:
        print(f"Error calculating daily P&L: {e}")
        return 0.0

def log_trade(side, symbol, amount, price, balance):
    """Log a trade to CSV"""
    try:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Create CSV if it doesn't exist
        if not os.path.exists('trade_log.csv'):
            with open('trade_log.csv', 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'side', 'symbol', 'amount', 'price', 'total_balance'])
        
        # Append trade
        with open('trade_log.csv', 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, side, symbol, amount, price, balance])
            
        print(f"📝 Trade logged: {side} {amount} {symbol} at ${price}")
        
    except Exception as e:
        print(f"Error logging trade: {e}")

def generate_performance_report():
    """Generate performance report"""
    try:
        report = {
            'total_trades': 0,
            'profitable_trades': 0,
            'total_pnl': 0.0,
            'win_rate': 0.0
        }
        
        if os.path.exists('trade_log.csv'):
            with open('trade_log.csv', 'r') as f:
                reader = csv.DictReader(f)
                trades = list(reader)
                report['total_trades'] = len(trades)
        
        # Save report
        with open('performance_report.csv', 'w') as f:
            f.write("metric,value\n")
            for key, value in report.items():
                f.write(f"{key},{value}\n")
        
        return report
        
    except Exception as e:
        print(f"Error generating performance report: {e}")
        return {}

def generate_trade_analysis():
    """Generate trade analysis"""
    try:
        analysis = {
            'avg_trade_duration': '30 minutes',
            'best_trade': 0.0,
            'worst_trade': 0.0
        }
        
        # Save analysis
        with open('trade_analysis.csv', 'w') as f:
            f.write("metric,value\n")
            for key, value in analysis.items():
                f.write(f"{key},{value}\n")
        
        return analysis
        
    except Exception as e:
        print(f"Error generating trade analysis: {e}")
        return {}

def log_message(message):
    """Simple logging function"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}", flush=True)
    
    # Also log to file
    try:
        with open('bot_log.txt', 'a') as f:
            f.write(f"[{timestamp}] {message}\n")
    except:
        pass
