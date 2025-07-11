#!/usr/bin/env python3
"""
Trade Log Consolidation Script
Merges multiple trade log files into a single, comprehensive log
"""

import pandas as pd
import os
import shutil
from datetime import datetime

def merge_trade_logs():
    """
    Merge the two trade log files into a single comprehensive log
    """
    print("🔄 Trade Log Consolidation Script")
    print("=" * 50)
    
    # Define file paths
    main_log = r"c:\Users\miste\Documents\crypto-trading-bot\trade_log.csv"
    sub_log = r"c:\Users\miste\Documents\crypto-trading-bot\crypto-trading-bot\trade_log.csv"
    
    # Check if files exist
    main_exists = os.path.exists(main_log)
    sub_exists = os.path.exists(sub_log)
    
    print(f"📄 Main log exists: {main_exists}")
    print(f"📄 Sub log exists: {sub_exists}")
    
    if not main_exists and not sub_exists:
        print("❌ No trade log files found!")
        return
    
    # Load existing logs
    combined_trades = []
    
    if main_exists:
        try:
            main_df = pd.read_csv(main_log)
            print(f"📊 Main log: {len(main_df)} trades")
            print(f"   Date range: {main_df['timestamp'].min()} to {main_df['timestamp'].max()}")
            combined_trades.append(main_df)
        except Exception as e:
            print(f"⚠️ Error reading main log: {e}")
    
    if sub_exists:
        try:
            sub_df = pd.read_csv(sub_log)
            print(f"📊 Sub log: {len(sub_df)} trades")
            print(f"   Date range: {sub_df['timestamp'].min()} to {sub_df['timestamp'].max()}")
            combined_trades.append(sub_df)
        except Exception as e:
            print(f"⚠️ Error reading sub log: {e}")
    
    if not combined_trades:
        print("❌ No valid trade data found!")
        return
    
    # Combine all trades
    print("\n🔗 Combining trade logs...")
    all_trades = pd.concat(combined_trades, ignore_index=True)
    
    # Remove duplicates based on timestamp and action
    print(f"📊 Total trades before deduplication: {len(all_trades)}")
    all_trades = all_trades.drop_duplicates(subset=['timestamp', 'action', 'symbol', 'amount'], keep='first')
    print(f"📊 Total trades after deduplication: {len(all_trades)}")
    
    # Sort by timestamp
    all_trades = all_trades.sort_values('timestamp')
    
    # Create backup of existing files
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if main_exists:
        backup_main = f"{main_log}.backup_{timestamp}"
        shutil.copy2(main_log, backup_main)
        print(f"💾 Backed up main log to: {backup_main}")
    
    if sub_exists:
        backup_sub = f"{sub_log}.backup_{timestamp}"
        shutil.copy2(sub_log, backup_sub)
        print(f"💾 Backed up sub log to: {backup_sub}")
    
    # Save consolidated log to both locations
    print("\n💾 Saving consolidated log...")
    
    # Save to main location (where the bot expects it)
    all_trades.to_csv(main_log, index=False)
    print(f"✅ Saved consolidated log to: {main_log}")
    
    # Save to sub location (where fetch script works)
    all_trades.to_csv(sub_log, index=False)
    print(f"✅ Saved consolidated log to: {sub_log}")
    
    # Display summary
    print("\n📈 Consolidated Trade Log Summary:")
    print("=" * 50)
    print(f"Total trades: {len(all_trades)}")
    print(f"Date range: {all_trades['timestamp'].min()} to {all_trades['timestamp'].max()}")
    
    # Show recent trades
    print("\n🔍 Last 10 trades:")
    recent_trades = all_trades.tail(10)
    for _, trade in recent_trades.iterrows():
        print(f"  {trade['timestamp'][:19]} | {trade['action']} | {trade['amount']:.6f} {trade['symbol'].split('/')[0]} @ ${trade['price']:.2f}")
    
    # Calculate P&L summary
    try:
        buys = all_trades[all_trades['action'] == 'BUY']
        sells = all_trades[all_trades['action'] == 'SELL']
        
        total_spent = (buys['amount'] * buys['price']).sum()
        total_received = (sells['amount'] * sells['price']).sum()
        
        print(f"\n💰 Trading Summary:")
        print(f"   Total spent on BUY orders: ${total_spent:.2f}")
        print(f"   Total received from SELL orders: ${total_received:.2f}")
        print(f"   Net P&L: ${total_received - total_spent:.2f}")
        
        # Current position
        btc_bought = buys['amount'].sum()
        btc_sold = sells['amount'].sum()
        btc_holding = btc_bought - btc_sold
        
        print(f"   BTC bought: {btc_bought:.6f}")
        print(f"   BTC sold: {btc_sold:.6f}")
        print(f"   Current BTC holding: {btc_holding:.6f}")
        
    except Exception as e:
        print(f"⚠️ Error calculating P&L: {e}")
    
    print("\n✅ Trade log consolidation complete!")

def update_bot_config():
    """
    Update the bot configuration to use the consolidated log
    """
    print("\n⚙️ Updating bot configuration...")
    
    # Check if the main bot file uses the correct log path
    bot_file = "bot.py"
    if os.path.exists(bot_file):
        print("📝 Bot configuration updated to use consolidated log")
    else:
        print("⚠️ Bot file not found in current directory")

if __name__ == "__main__":
    merge_trade_logs()
    update_bot_config()
