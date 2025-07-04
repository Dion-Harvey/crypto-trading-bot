import csv
from datetime import datetime
import os
import pandas as pd

LOG_FILE = "trade_log.csv"

def init_log():
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["timestamp", "action", "symbol", "amount", "price", "balance"])

def log_trade(action, symbol, amount, price, balance):
    with open(LOG_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([datetime.utcnow(), action, symbol, amount, price, balance])

def calculate_daily_pnl():
    pnl = 0
    with open(LOG_FILE, mode='r') as file:
        reader = csv.DictReader(file)
        trades = list(reader)
        today = datetime.utcnow().date()
        buys = []
        for row in trades:
            timestamp = datetime.fromisoformat(row["timestamp"]).date()
            if timestamp != today:
                continue
            if row["action"] == "BUY":
                buys.append(float(row["price"]))
            elif row["action"] == "SELL" and buys:
                entry = buys.pop(0)  # FIFO
                exit_price = float(row["price"])
                amount = float(row["amount"])
                pnl += (exit_price - entry) * amount
    return pnl

def generate_performance_report():
    """Generate comprehensive CSV performance report - appends to same file"""
    if not os.path.exists(LOG_FILE):
        print("⚠️ No trade log found. Cannot generate report.")
        return

    try:
        # Read trade data
        df = pd.read_csv(LOG_FILE)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['date'] = df['timestamp'].dt.date

        # Performance report filename (same file every time)
        report_filename = "performance_report.csv"
        
        # Check if performance report exists to get existing data
        existing_dates = set()
        if os.path.exists(report_filename):
            try:
                existing_df = pd.read_csv(report_filename)
                existing_dates = set(pd.to_datetime(existing_df['date']).dt.date)
            except:
                pass  # If file is corrupted, start fresh

        # Calculate daily statistics for new dates only
        daily_stats = []
        dates = df['date'].unique()

        for date in dates:
            # Skip if this date is already in the report
            if date in existing_dates:
                continue
                
            day_trades = df[df['date'] == date]
            buys = day_trades[day_trades['action'] == 'BUY']
            sells = day_trades[day_trades['action'] == 'SELL']

            # Calculate daily P&L using FIFO
            daily_pnl = 0
            buy_prices = []

            for _, trade in day_trades.iterrows():
                if trade['action'] == 'BUY':
                    buy_prices.append(trade['price'])
                elif trade['action'] == 'SELL' and buy_prices:
                    entry_price = buy_prices.pop(0)  # FIFO
                    daily_pnl += (trade['price'] - entry_price) * trade['amount']

            daily_stats.append({
                'date': date,
                'total_trades': len(day_trades),
                'buy_trades': len(buys),
                'sell_trades': len(sells),
                'daily_pnl': round(daily_pnl, 2),
                'avg_buy_price': round(buys['price'].mean(), 2) if len(buys) > 0 else 0,
                'avg_sell_price': round(sells['price'].mean(), 2) if len(sells) > 0 else 0,
                'total_volume': round(day_trades['amount'].sum(), 6)
            })

        # Append new data to performance report CSV
        if daily_stats:
            file_exists = os.path.exists(report_filename)
            with open(report_filename, 'a', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=[
                    'date', 'total_trades', 'buy_trades', 'sell_trades',
                    'daily_pnl', 'avg_buy_price', 'avg_sell_price', 'total_volume'
                ])
                
                # Write header only if file doesn't exist
                if not file_exists:
                    writer.writeheader()
                    
                writer.writerows(daily_stats)
                
            print(f"📊 Added {len(daily_stats)} new daily records to {report_filename}")
        else:
            print(f"📊 No new data to add to {report_filename}")

        # Read full report for summary statistics
        if os.path.exists(report_filename):
            full_df = pd.read_csv(report_filename)
            total_pnl = full_df['daily_pnl'].sum()
            total_trades = full_df['total_trades'].sum()
            profitable_days = len(full_df[full_df['daily_pnl'] > 0])
            total_days = len(full_df)

            # Print summary
            print(f"\n📊 PERFORMANCE REPORT UPDATED: {report_filename}")
            print("="*60)
            print(f"📅 Trading Period: {full_df['date'].min()} to {full_df['date'].max()}")
            print(f"📈 Total P&L: ${total_pnl:.2f}")
            print(f"🔄 Total Trades: {total_trades}")
            print(f"✅ Profitable Days: {profitable_days}/{total_days}")
            print(f"📊 Win Rate: {(profitable_days/total_days*100):.1f}%")
            print(f"💰 Avg Daily P&L: ${(total_pnl/total_days):.2f}")
            print("="*60)

        return report_filename

    except Exception as e:
        print(f"❌ Error generating report: {e}")
        return None

def generate_trade_analysis():
    """Generate detailed trade analysis CSV - appends to same file"""
    if not os.path.exists(LOG_FILE):
        print("⚠️ No trade log found. Cannot generate analysis.")
        return

    try:
        df = pd.read_csv(LOG_FILE)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Trade analysis filename (same file every time)
        analysis_filename = "trade_analysis.csv"
        
        # Check existing trade pairs to avoid duplicates
        existing_pairs = set()
        if os.path.exists(analysis_filename):
            try:
                existing_df = pd.read_csv(analysis_filename)
                # Create unique identifier for each trade pair
                for _, row in existing_df.iterrows():
                    pair_id = f"{row['buy_time']}_{row['sell_time']}"
                    existing_pairs.add(pair_id)
            except:
                pass  # If file is corrupted, start fresh

        # Pair buy/sell trades for analysis
        trade_pairs = []
        buy_queue = []

        for _, trade in df.iterrows():
            if trade['action'] == 'BUY':
                buy_queue.append(trade)
            elif trade['action'] == 'SELL' and buy_queue:
                buy_trade = buy_queue.pop(0)  # FIFO

                # Create unique identifier for this pair
                pair_id = f"{buy_trade['timestamp']}_{trade['timestamp']}"
                
                # Skip if this pair already exists
                if pair_id in existing_pairs:
                    continue

                profit = (trade['price'] - buy_trade['price']) * trade['amount']
                hold_time = (trade['timestamp'] - buy_trade['timestamp']).total_seconds() / 60  # minutes

                trade_pairs.append({
                    'buy_time': buy_trade['timestamp'],
                    'sell_time': trade['timestamp'],
                    'buy_price': buy_trade['price'],
                    'sell_price': trade['price'],
                    'amount': trade['amount'],
                    'profit_loss': round(profit, 2),
                    'hold_time_minutes': round(hold_time, 1),
                    'return_pct': round((trade['price'] - buy_trade['price']) / buy_trade['price'] * 100, 2)
                })

        # Append new trade pairs to analysis CSV
        if trade_pairs:
            file_exists = os.path.exists(analysis_filename)
            with open(analysis_filename, 'a', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=[
                    'buy_time', 'sell_time', 'buy_price', 'sell_price', 'amount',
                    'profit_loss', 'hold_time_minutes', 'return_pct'
                ])
                
                # Write header only if file doesn't exist
                if not file_exists:
                    writer.writeheader()
                    
                writer.writerows(trade_pairs)
                
            print(f"🔍 Added {len(trade_pairs)} new trade pairs to {analysis_filename}")
        else:
            print(f"🔍 No new trade pairs to add to {analysis_filename}")

        # Read full analysis for summary statistics
        if os.path.exists(analysis_filename):
            try:
                full_df = pd.read_csv(analysis_filename)
                if len(full_df) > 0:
                    winning_trades = len(full_df[full_df['profit_loss'] > 0])
                    avg_profit = full_df['profit_loss'].mean()
                    avg_hold_time = full_df['hold_time_minutes'].mean()
                    total_pairs = len(full_df)

                    print(f"\n🔍 TRADE ANALYSIS UPDATED: {analysis_filename}")
                    print("="*60)
                    print(f"🎯 Total Trade Pairs: {total_pairs}")
                    print(f"✅ Winning Trades: {winning_trades}")
                    print(f"📊 Win Rate: {(winning_trades/total_pairs*100):.1f}%")
                    print(f"💰 Average Profit: ${avg_profit:.2f}")
                    print(f"⏱️ Average Hold Time: {avg_hold_time:.1f} minutes")
                    print("="*60)
            except Exception as e:
                print(f"⚠️ Error reading full analysis file: {e}")

        return analysis_filename

    except Exception as e:
        print(f"❌ Error generating trade analysis: {e}")
        return None

def log_message(message):
    """
    Log a message with timestamp to console and optionally to file
    """
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    formatted_message = f"[{timestamp}] {message}"
    print(formatted_message)
    
    # Optionally write to a separate log file
    try:
        with open("bot_log.txt", "a", encoding="utf-8") as f:
            f.write(formatted_message + "\n")
    except:
        pass  # Don't fail if we can't write to log file
