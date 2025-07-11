#!/usr/bin/env python3
"""
Minimal log_utils.py to fix the immediate bot issue
"""
import csv
import os
from datetime import datetime, timedelta

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
