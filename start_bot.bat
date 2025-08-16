@echo off
echo Starting Enhanced Trading Bot...
echo Bot will run with 30-second loops and 5-minute cooldown  
echo Press Ctrl+C to stop the bot safely
echo.
cd /d "C:\Users\miste\Documents\crypto-trading-bot\crypto-trading-bot"
C:\Users\miste\Documents\crypto-trading-bot\crypto-trading-bot\.venv\Scripts\python.exe bot.py
pause
