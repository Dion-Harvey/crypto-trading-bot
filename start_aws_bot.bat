@echo off
echo 🚀 Starting Crypto Trading Bot on AWS...
echo ========================================

REM Connect to AWS and start the bot
ssh -i "C:\Users\miste\Documents\cryptobot-key.pem" ubuntu@3.135.216.32 "cd crypto-trading-bot && nohup python3 bot.py > bot_log.txt 2>&1 &"

if %errorlevel% equ 0 (
    echo ✅ Bot started successfully on AWS
    echo 📊 Checking bot status...
    
    REM Wait a moment then check if it's running
    timeout /t 3 /nobreak > nul
    ssh -i "C:\Users\miste\Documents\cryptobot-key.pem" ubuntu@3.135.216.32 "ps aux | grep bot.py | grep -v grep"
    
    if %errorlevel% equ 0 (
        echo ✅ Bot is running on AWS
    ) else (
        echo ⚠️ Bot may not be running, check logs
    )
) else (
    echo ❌ Failed to start bot on AWS
)

pause
