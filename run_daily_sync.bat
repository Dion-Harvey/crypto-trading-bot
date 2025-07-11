@echo off
REM Windows Task Scheduler Helper Script
REM This script will run the daily sync scheduler

echo Starting Crypto Trading Bot Daily Sync...
echo Time: %DATE% %TIME%

cd /d "c:\Users\miste\Documents\crypto-trading-bot\crypto-trading-bot"

REM Run the daily sync job
python daily_sync_scheduler.py --test

echo.
echo Daily sync completed at %DATE% %TIME%
echo Check daily_sync.log for detailed results
