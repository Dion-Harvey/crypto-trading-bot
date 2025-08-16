#!/usr/bin/env python3
"""
Fetch Recent Trades from Binance US
Updates local trade logs with latest trading activity
"""

import ccxt
import pandas as pd
import json
import os
from datetime import datetime, timedelta
from config import BINANCE_API_KEY, BINANCE_API_SECRET

def fetch_recent_trades():
    """
    Fetch recent trades from Binance US and display them
    """
    try:
        # Initialize exchange
        exchange = ccxt.binanceus({
            'apiKey': BINANCE_API_KEY,
            'secret': BINANCE_API_SECRET,
            'enableRateLimit': True,
            'timeout': 30000,
            'options': {
                'recvWindow': 10000,
                'timeDifference': 1000,
                'adjustForTimeDifference': True
            }
        })

        print("🔗 Connecting to Binance US...")
        
        # Test connection
        try:
            balance = exchange.fetch_balance()
            print("✅ Connected successfully!")
            print(f"💰 Current Balance: {balance['total']['USDC']:.2f} USDC, {balance['total']['BTC']:.6f} BTC")
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return

        # Fetch recent trades for BTC/USDC
        print("\n📊 Fetching recent BTC/USDC trades...")
        
        try:
            # Get trades from the last 7 days
            since = int((datetime.now() - timedelta(days=7)).timestamp() * 1000)
            trades = exchange.fetch_my_trades('BTC/USDC', since=since, limit=50)
            
            if not trades:
                print("No recent trades found.")
                return
            
            print(f"Found {len(trades)} recent trades:\n")
            
            # Display trades in a formatted way
            print("=" * 80)
            print(f"{'Date/Time':<20} {'Side':<4} {'Amount (BTC)':<12} {'Price':<12} {'Value (USDC)':<12} {'Fee':<10}")
            print("=" * 80)
            
            total_buys = 0
            total_sells = 0
            total_fees = 0
            
            for trade in sorted(trades, key=lambda x: x['timestamp'], reverse=True):
                timestamp = datetime.fromtimestamp(trade['timestamp'] / 1000)
                side = trade['side'].upper()
                amount = trade['amount']
                price = trade['price']
                cost = trade['cost']
                fee = trade['fee']['cost'] if trade['fee'] else 0
                
                print(f"{timestamp.strftime('%Y-%m-%d %H:%M:%S'):<20} {side:<4} {amount:<12.6f} {price:<12.2f} {cost:<12.2f} {fee:<10.6f}")
                
                if side == 'BUY':
                    total_buys += cost
                else:
                    total_sells += cost
                
                total_fees += fee
            
            print("=" * 80)
            print(f"Summary:")
            print(f"  Total Buys:  ${total_buys:.2f}")
            print(f"  Total Sells: ${total_sells:.2f}")
            print(f"  Net P&L:     ${total_sells - total_buys:.2f}")
            print(f"  Total Fees:  ${total_fees:.2f}")
            print(f"  Net After Fees: ${total_sells - total_buys - total_fees:.2f}")
            
            # Update local trade log
            update_local_trade_log(trades)
            
        except Exception as e:
            print(f"❌ Error fetching trades: {e}")
            
    except Exception as e:
        print(f"❌ Error initializing exchange: {e}")

def update_local_trade_log(trades):
    """
    Update the local trade_log.csv with fetched trades
    Updates both the main log and subdirectory log for consistency
    """
    try:
        print("\n📝 Updating local trade log...")
        
        # Define log paths
        main_log = r"c:\Users\miste\Documents\crypto-trading-bot\trade_log.csv"
        sub_log = "trade_log.csv"
        
        # Try to read from main log first, then fallback to local
        log_path = main_log if os.path.exists(main_log) else sub_log
        
        # Read existing log
        try:
            existing_df = pd.read_csv(log_path)
            existing_timestamps = set(existing_df['timestamp'].values)
            print(f"📊 Found {len(existing_df)} existing trades in {log_path}")
        except FileNotFoundError:
            existing_df = pd.DataFrame(columns=['timestamp', 'action', 'symbol', 'amount', 'price', 'balance'])
            existing_timestamps = set()
            print("📊 No existing trade log found, creating new one")
        
        # Convert trades to DataFrame format
        new_trades = []
        for trade in trades:
            timestamp = datetime.fromtimestamp(trade['timestamp'] / 1000)
            timestamp_str = timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')
            
            # Skip if already exists (check with more flexible matching)
            existing_match = False
            for existing_ts in existing_timestamps:
                existing_dt = datetime.strptime(existing_ts.split('.')[0], '%Y-%m-%d %H:%M:%S')
                trade_dt = datetime.strptime(timestamp_str.split('.')[0], '%Y-%m-%d %H:%M:%S')
                
                # If timestamps are within 1 second and same action, consider it a duplicate
                if abs((trade_dt - existing_dt).total_seconds()) < 1:
                    existing_match = True
                    break
            
            if existing_match:
                continue
            
            new_trades.append({
                'timestamp': timestamp_str,
                'action': trade['side'].upper(),
                'symbol': trade['symbol'],
                'amount': trade['amount'],
                'price': trade['price'],
                'balance': trade['cost']  # Using cost as balance placeholder
            })
        
        if new_trades:
            new_df = pd.DataFrame(new_trades)
            updated_df = pd.concat([existing_df, new_df], ignore_index=True)
            updated_df = updated_df.sort_values('timestamp')
            
            # Save to both locations for consistency
            updated_df.to_csv(main_log, index=False)
            updated_df.to_csv(sub_log, index=False)
            
            print(f"✅ Added {len(new_trades)} new trades to local log")
            print(f"📊 Total trades now: {len(updated_df)}")
        else:
            print("ℹ️ No new trades to add to local log")
            
    except Exception as e:
        print(f"❌ Error updating local log: {e}")

def get_recent_trading_summary():
    """
    Get a summary of recent trading activity
    """
    try:
        print("\n📈 Recent Trading Summary:")
        
        # Get trades from last 24 hours
        since = int((datetime.now() - timedelta(hours=24)).timestamp() * 1000)
        
        exchange = ccxt.binanceus({
            'apiKey': BINANCE_API_KEY,
            'secret': BINANCE_API_SECRET,
            'enableRateLimit': True,
            'timeout': 30000,
            'options': {
                'recvWindow': 10000,
                'timeDifference': 1000,
                'adjustForTimeDifference': True
            }
        })
        
        trades = exchange.fetch_my_trades('BTC/USDC', since=since)
        
        if trades:
            print(f"  - {len(trades)} trades in last 24 hours")
            last_trade = max(trades, key=lambda x: x['timestamp'])
            last_time = datetime.fromtimestamp(last_trade['timestamp'] / 1000)
            print(f"  - Last trade: {last_trade['side'].upper()} at ${last_trade['price']:.2f} ({last_time.strftime('%Y-%m-%d %H:%M:%S')})")
        else:
            print("  - No trades in last 24 hours")
            
    except Exception as e:
        print(f"❌ Error getting trading summary: {e}")

if __name__ == "__main__":
    print("🔍 Fetching Recent Trades from Binance US")
    print("=" * 50)
    
    fetch_recent_trades()
    get_recent_trading_summary()
    
    print("\n✅ Trade fetch complete!")
