# Daily Trade Log Automation Setup

## Overview
This document provides instructions for setting up automated daily execution of the trade log synchronization system to run just before midnight.

## Files Created

### 1. `windows_daily_sync.py` (Recommended for Windows)
- **Purpose**: Windows-compatible daily scheduler 
- **Features**: 
  - Runs at 11:55 PM daily (5 minutes before midnight)
  - Executes both `fetch_recent_trades.py` and `sync_trade_logs.py`
  - Built-in logging to `daily_sync.log`
  - Handles Unicode encoding issues on Windows
  - Pure Python implementation (no external libraries)

### 2. `run_daily_sync.ps1` (PowerShell Script)
- **Purpose**: PowerShell script for Windows Task Scheduler
- **Features**: Proper logging and error handling for scheduled tasks

### 3. `run_daily_sync.bat` (Windows Batch File)
- **Purpose**: Simple Windows batch file for basic automation
- **Usage**: Can be used with Windows Task Scheduler

### 4. `simple_daily_sync.py` (Cross-platform)
- **Purpose**: Basic daily scheduler for any platform
- **Note**: May have Unicode display issues on Windows but works functionally

## Setup Options

### Option 1: Windows Daily Scheduler (Recommended for Windows)

1. **Test the sync system**:
   ```powershell
   python windows_daily_sync.py --test
   ```

2. **Start the daily scheduler**:
   ```powershell
   python windows_daily_sync.py --schedule
   ```

3. **Run in background** (Windows):
   ```powershell
   start /min python windows_daily_sync.py --schedule
   ```

### Option 2: Windows Task Scheduler (Most Reliable)

#### Method A: Using PowerShell Script
1. **Open Task Scheduler** (Windows Key + R, type `taskschd.msc`)
2. **Create Basic Task**:
   - Name: "Crypto Bot Daily Sync"
   - Description: "Daily trade log synchronization at 11:55 PM"
3. **Set Trigger**:
   - Daily at 11:55 PM
   - Start date: Today
   - Recur every: 1 day
4. **Set Action**:
   - Program: `powershell.exe`
   - Arguments: `-ExecutionPolicy Bypass -File "c:\Users\miste\Documents\crypto-trading-bot\crypto-trading-bot\run_daily_sync.ps1"`
   - Start in: `c:\Users\miste\Documents\crypto-trading-bot\crypto-trading-bot`

#### Method B: Using Python Script Directly
1. **Create Basic Task** (same as above)
2. **Set Action**:
   - Program: `python.exe`
   - Arguments: `windows_daily_sync.py --test`
   - Start in: `c:\Users\miste\Documents\crypto-trading-bot\crypto-trading-bot`

### Option 3: Manual Batch File
Double-click `run_daily_sync.bat` to run sync manually anytime.

## Monitoring

### Log Files
- `daily_sync.log`: Contains all sync activity and results (UTF-8 encoded)
- `daily_sync_task.log`: PowerShell task execution log
- `bot_log.txt`: Original bot logging
- `trade_log.csv`: Main consolidated trade log

### Manual Verification
You can manually run the sync anytime:
```powershell
python fetch_recent_trades.py
python sync_trade_logs.py
```

Or use the automation script:
```powershell
python windows_daily_sync.py --test
```

## What Happens Daily

1. **11:55 PM**: Automated sync begins
2. **Step 1**: Fetch recent trades from Binance US API
3. **Step 2**: Update both trade log locations
4. **Step 3**: Synchronize logs between main and subdirectory
5. **Step 4**: Log results and prepare for next day

## Benefits

- **Complete Coverage**: Captures all trades, even when bot runs remotely
- **No Duplicates**: Robust duplicate detection prevents log corruption
- **Synchronized**: Both log locations stay in perfect sync
- **Automated**: Runs daily without manual intervention
- **Logged**: Full audit trail of all sync activities
- **Reliable**: Multiple fallback options for different environments
- **Windows Compatible**: Handles Unicode and encoding issues properly

## Troubleshooting

### Common Issues

1. **Script not found**: Ensure you're in the correct directory
2. **Permissions**: Run as administrator if needed
3. **Network issues**: Check internet connection for Binance API
4. **API limits**: Script respects Binance rate limits
5. **Unicode errors**: Use `windows_daily_sync.py` for Windows compatibility

### Manual Recovery
If automation fails, you can always run:
```powershell
python windows_daily_sync.py --test
```

This will immediately sync your logs and show any issues.

## Recommended Approach

### For Windows Users (Recommended)
**Option 2A (Windows Task Scheduler + PowerShell)** provides:
- System-level reliability
- Automatic restart on failure
- Better resource management
- Proper logging and error handling
- Integration with Windows services

### For Advanced Users
**Option 1 (Python Scheduler)** is good for:
- Development and testing
- Custom scheduling needs
- Direct control over the process

## Quick Start (Windows)

1. **Test everything works**:
   ```powershell
   cd "c:\Users\miste\Documents\crypto-trading-bot\crypto-trading-bot"
   python windows_daily_sync.py --test
   ```

2. **Set up automated daily sync**:
   - Open Task Scheduler
   - Create Basic Task: "Crypto Bot Daily Sync"
   - Daily at 11:55 PM
   - Action: PowerShell script `run_daily_sync.ps1`

3. **Verify setup**:
   - Right-click task → "Run" to test
   - Check `daily_sync_task.log` for results
   - Monitor `daily_sync.log` for ongoing activity

That's it! Your trade logs will now be automatically synchronized daily at 11:55 PM.
