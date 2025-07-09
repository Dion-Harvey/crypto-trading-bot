#!/usr/bin/env python3
"""
Trade Log Management Solution
Provides ongoing synchronization and management of trade logs
"""

import pandas as pd
import os
import shutil
from datetime import datetime

class TradeLogManager:
    def __init__(self):
        self.main_log = r"c:\Users\miste\Documents\crypto-trading-bot\trade_log.csv"
        self.sub_log = r"c:\Users\miste\Documents\crypto-trading-bot\crypto-trading-bot\trade_log.csv"
        
    def sync_logs(self):
        """
        Synchronize both trade logs to ensure they have the same data
        """
        print("🔄 Synchronizing trade logs...")
        
        # Find the most recent version
        main_exists = os.path.exists(self.main_log)
        sub_exists = os.path.exists(self.sub_log)
        
        if not main_exists and not sub_exists:
            print("❌ No trade logs found!")
            return False
        
        # Choose the most recent or most complete log
        source_log = None
        if main_exists and sub_exists:
            main_mod = os.path.getmtime(self.main_log)
            sub_mod = os.path.getmtime(self.sub_log)
            
            # Also check record count
            main_count = len(pd.read_csv(self.main_log))
            sub_count = len(pd.read_csv(self.sub_log))
            
            # Use the one with more records, or if equal, the more recent
            if main_count > sub_count:
                source_log = self.main_log
                print(f"📊 Using main log as source ({main_count} records)")
            elif sub_count > main_count:
                source_log = self.sub_log
                print(f"📊 Using sub log as source ({sub_count} records)")
            else:
                source_log = self.main_log if main_mod > sub_mod else self.sub_log
                print(f"📊 Using most recent log as source")
        elif main_exists:
            source_log = self.main_log
            print("📊 Using main log as source")
        else:
            source_log = self.sub_log
            print("📊 Using sub log as source")
        
        # Copy the source to both locations
        if source_log == self.main_log:
            if sub_exists:
                shutil.copy2(self.main_log, self.sub_log)
                print(f"✅ Copied main log to sub log")
        else:
            if main_exists:
                shutil.copy2(self.sub_log, self.main_log)
                print(f"✅ Copied sub log to main log")
        
        # If one doesn't exist, create it
        if not os.path.exists(self.main_log):
            shutil.copy2(source_log, self.main_log)
            print(f"✅ Created main log")
        
        if not os.path.exists(self.sub_log):
            shutil.copy2(source_log, self.sub_log)
            print(f"✅ Created sub log")
        
        print("✅ Trade logs synchronized!")
        return True
    
    def verify_sync(self):
        """
        Verify that both logs are in sync
        """
        print("\n🔍 Verifying log synchronization...")
        
        if not os.path.exists(self.main_log) or not os.path.exists(self.sub_log):
            print("❌ One or both logs missing!")
            return False
        
        try:
            main_df = pd.read_csv(self.main_log)
            sub_df = pd.read_csv(self.sub_log)
            
            main_count = len(main_df)
            sub_count = len(sub_df)
            
            print(f"📊 Main log: {main_count} records")
            print(f"📊 Sub log: {sub_count} records")
            
            if main_count == sub_count:
                # Check if the last few records match
                if main_count > 0:
                    main_last = main_df.tail(5)
                    sub_last = sub_df.tail(5)
                    
                    if main_last.equals(sub_last):
                        print("✅ Logs are perfectly synchronized!")
                        return True
                    else:
                        print("⚠️ Logs have same count but different content")
                        return False
                else:
                    print("✅ Both logs are empty and synchronized")
                    return True
            else:
                print("⚠️ Logs have different record counts")
                return False
                
        except Exception as e:
            print(f"❌ Error verifying sync: {e}")
            return False
    
    def get_log_stats(self):
        """
        Get statistics about the current trade logs
        """
        print("\n📈 Trade Log Statistics:")
        print("=" * 50)
        
        for log_name, log_path in [("Main", self.main_log), ("Sub", self.sub_log)]:
            if os.path.exists(log_path):
                try:
                    df = pd.read_csv(log_path)
                    print(f"\n📊 {log_name} Log ({log_path}):")
                    print(f"   Records: {len(df)}")
                    if len(df) > 0:
                        print(f"   Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
                        print(f"   Last modified: {datetime.fromtimestamp(os.path.getmtime(log_path))}")
                        
                        # Show recent activity
                        recent = df.tail(3)
                        print(f"   Recent trades:")
                        for _, trade in recent.iterrows():
                            print(f"     {trade['timestamp'][:19]} | {trade['action']} | {trade['amount']:.6f} @ ${trade['price']:.2f}")
                except Exception as e:
                    print(f"❌ Error reading {log_name} log: {e}")
            else:
                print(f"\n❌ {log_name} Log not found!")

def main():
    """
    Main function to manage trade logs
    """
    print("🔧 Trade Log Management System")
    print("=" * 50)
    
    manager = TradeLogManager()
    
    # Show current status
    manager.get_log_stats()
    
    # Sync logs
    if manager.sync_logs():
        # Verify sync
        manager.verify_sync()
        
        # Show updated stats
        manager.get_log_stats()
    
    print("\n✅ Trade log management complete!")
    print("\n💡 Recommendations:")
    print("1. The bot will now use the main log: c:\\Users\\miste\\Documents\\crypto-trading-bot\\trade_log.csv")
    print("2. The fetch script will update both locations for consistency")
    print("3. Run this script periodically to ensure logs stay synchronized")

if __name__ == "__main__":
    main()
