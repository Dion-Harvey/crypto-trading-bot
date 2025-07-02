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
    """Generate comprehensive CSV performance report"""
    if not os.path.exists(LOG_FILE):
        print("⚠️ No trade log found. Cannot generate report.")
        return

    try:
        # Read trade data
        df = pd.read_csv(LOG_FILE)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['date'] = df['timestamp'].dt.date

        # Calculate daily statistics
        daily_stats = []
        dates = df['date'].unique()

        for date in dates:
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

        # Create performance report CSV
        report_filename = f"performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        with open(report_filename, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=[
                'date', 'total_trades', 'buy_trades', 'sell_trades',
                'daily_pnl', 'avg_buy_price', 'avg_sell_price', 'total_volume'
            ])
            writer.writeheader()
            writer.writerows(daily_stats)

        # Calculate overall statistics
        total_pnl = sum([stat['daily_pnl'] for stat in daily_stats])
        total_trades = sum([stat['total_trades'] for stat in daily_stats])
        profitable_days = len([stat for stat in daily_stats if stat['daily_pnl'] > 0])

        # Print summary
        print(f"\n📊 PERFORMANCE REPORT GENERATED: {report_filename}")
        print("="*60)
        print(f"📅 Trading Period: {min(dates)} to {max(dates)}")
        print(f"📈 Total P&L: ${total_pnl:.2f}")
        print(f"🔄 Total Trades: {total_trades}")
        print(f"✅ Profitable Days: {profitable_days}/{len(daily_stats)}")
        print(f"📊 Win Rate: {(profitable_days/len(daily_stats)*100):.1f}%")
        print(f"💰 Avg Daily P&L: ${(total_pnl/len(daily_stats)):.2f}")
        print("="*60)

        return report_filename

    except Exception as e:
        print(f"❌ Error generating report: {e}")
        return None

def generate_trade_analysis():
    """Generate detailed trade analysis CSV"""
    if not os.path.exists(LOG_FILE):
        print("⚠️ No trade log found. Cannot generate analysis.")
        return

    try:
        df = pd.read_csv(LOG_FILE)
        df['timestamp'] = pd.to_datetime(df['timestamp'])

        # Pair buy/sell trades for analysis
        trade_pairs = []
        buy_queue = []

        for _, trade in df.iterrows():
            if trade['action'] == 'BUY':
                buy_queue.append(trade)
            elif trade['action'] == 'SELL' and buy_queue:
                buy_trade = buy_queue.pop(0)  # FIFO

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

        # Create trade analysis CSV
        analysis_filename = f"trade_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        with open(analysis_filename, 'w', newline='') as file:
            if trade_pairs:
                writer = csv.DictWriter(file, fieldnames=trade_pairs[0].keys())
                writer.writeheader()
                writer.writerows(trade_pairs)

        # Print analysis summary
        if trade_pairs:
            winning_trades = [t for t in trade_pairs if t['profit_loss'] > 0]
            avg_profit = sum([t['profit_loss'] for t in trade_pairs]) / len(trade_pairs)
            avg_hold_time = sum([t['hold_time_minutes'] for t in trade_pairs]) / len(trade_pairs)

            print(f"\n🔍 TRADE ANALYSIS GENERATED: {analysis_filename}")
            print("="*60)
            print(f"🎯 Completed Trade Pairs: {len(trade_pairs)}")
            print(f"✅ Winning Trades: {len(winning_trades)}")
            print(f"📊 Win Rate: {(len(winning_trades)/len(trade_pairs)*100):.1f}%")
            print(f"💰 Average Profit: ${avg_profit:.2f}")
            print(f"⏱️ Average Hold Time: {avg_hold_time:.1f} minutes")
            print("="*60)

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
