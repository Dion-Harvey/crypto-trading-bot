@echo off
title AWS Crypto Bot Manager
color 0a

:MENU
cls
echo.
echo  ╔══════════════════════════════════════════════════════════════╗
echo  ║                🚀 AWS CRYPTO BOT MANAGER 🚀                  ║
echo  ╚══════════════════════════════════════════════════════════════╝
echo.
echo  📊 Bot Status and Management Options:
echo.
echo  [1] 🔍 Check Bot Status
echo  [2] 🚀 Start Bot on AWS  
echo  [3] 🛑 Stop Bot on AWS
echo  [4] 📝 View Live Bot Logs
echo  [5] 📈 View Latest Trading Activity
echo  [6] 💰 Check Account Balance
echo  [7] 🔄 Restart Bot
echo  [8] 🧪 Test AWS Connection
echo  [9] ❌ Exit
echo.
set /p choice="Select option [1-9]: "

if "%choice%"=="1" goto STATUS
if "%choice%"=="2" goto START
if "%choice%"=="3" goto STOP
if "%choice%"=="4" goto LOGS
if "%choice%"=="5" goto ACTIVITY
if "%choice%"=="6" goto BALANCE
if "%choice%"=="7" goto RESTART
if "%choice%"=="8" goto TEST
if "%choice%"=="9" goto EXIT
goto MENU

:STATUS
cls
echo 🔍 Checking Bot Status on AWS...
echo ================================
ssh -i "C:\Users\miste\Documents\cryptobot-key.pem" ubuntu@3.135.216.32 "ps aux | grep -E '(bot\.py|python.*bot)' | grep -v grep && echo '✅ Bot is running' || echo '❌ Bot is not running'"
echo.
echo 📊 System Resources:
ssh -i "C:\Users\miste\Documents\cryptobot-key.pem" ubuntu@3.135.216.32 "uptime && free -h | head -2"
pause
goto MENU

:START
cls
echo 🚀 Starting Bot on AWS...
echo ========================
ssh -i "C:\Users\miste\Documents\cryptobot-key.pem" ubuntu@3.135.216.32 "cd crypto-trading-bot && nohup python3 bot.py > bot_log.txt 2>&1 &"
echo ✅ Bot start command sent
echo ⏳ Waiting for initialization...
timeout /t 5 /nobreak >nul
ssh -i "C:\Users\miste\Documents\cryptobot-key.pem" ubuntu@3.135.216.32 "ps aux | grep bot.py | grep -v grep && echo '✅ Bot is now running' || echo '⚠️ Bot may still be starting'"
pause
goto MENU

:STOP
cls
echo 🛑 Stopping Bot on AWS...
echo ========================
ssh -i "C:\Users\miste\Documents\cryptobot-key.pem" ubuntu@3.135.216.32 "pkill -f bot.py && echo '✅ Bot stopped' || echo '❌ No bot process found'"
pause
goto MENU

:LOGS
cls
echo 📝 Live Bot Logs (Press Ctrl+C to exit)...
echo ==========================================
ssh -i "C:\Users\miste\Documents\cryptobot-key.pem" ubuntu@3.135.216.32 "tail -f crypto-trading-bot/bot_log.txt"
goto MENU

:ACTIVITY
cls
echo 📈 Latest Trading Activity...
echo ============================
ssh -i "C:\Users\miste\Documents\cryptobot-key.pem" ubuntu@3.135.216.32 "tail -20 crypto-trading-bot/bot_log.txt | grep -E '(BUY|SELL|PROFIT|LOSS|TRADE)'"
pause
goto MENU

:BALANCE
cls
echo 💰 Checking Account Balance...
echo =============================
ssh -i "C:\Users\miste\Documents\cryptobot-key.pem" ubuntu@3.135.216.32 "cd crypto-trading-bot && python3 -c \"from bot import test_connection; test_connection()\""
pause
goto MENU

:RESTART
cls
echo 🔄 Restarting Bot...
echo ==================
@echo off
echo.
echo 🚀 AWS CRYPTO TRADING BOT MANAGER
echo ==================================
echo.
echo 🎯 AWS Details:
echo    IP: 3.135.216.32
echo    User: ubuntu
echo    Key: C:\Users\miste\Documents\cryptobot-key.pem
echo.
echo 📋 Available Commands:
echo    1. Check bot status
echo    2. Start bot
echo    3. Stop bot
echo    4. View recent logs
echo    5. Upload local changes
echo    6. Restart bot
echo.
set /p choice="Enter your choice (1-6): "

if %choice%==1 (
    echo 📊 Checking bot status...
    ssh -i C:\Users\miste\Documents\cryptobot-key.pem ubuntu@3.135.216.32 "cd ~/crypto-trading-bot && ps aux | grep -v grep | grep bot.py"
) else if %choice%==2 (
    echo 🚀 Starting bot...
    ssh -i C:\Users\miste\Documents\cryptobot-key.pem ubuntu@3.135.216.32 "cd ~/crypto-trading-bot && nohup .venv/bin/python bot.py > bot_output.log 2>&1 &"
) else if %choice%==3 (
    echo 🛑 Stopping bot...
    ssh -i C:\Users\miste\Documents\cryptobot-key.pem ubuntu@3.135.216.32 "cd ~/crypto-trading-bot && pkill -f bot.py"
) else if %choice%==4 (
    echo 📄 Recent logs...
    ssh -i C:\Users\miste\Documents\cryptobot-key.pem ubuntu@3.135.216.32 "cd ~/crypto-trading-bot && tail -20 bot_output.log"
) else if %choice%==5 (
    echo 📤 Uploading changes...
    scp -i C:\Users\miste\Documents\cryptobot-key.pem bot.py ubuntu@3.135.216.32:~/crypto-trading-bot/
    scp -i C:\Users\miste\Documents\cryptobot-key.pem enhanced_config.json ubuntu@3.135.216.32:~/crypto-trading-bot/
) else if %choice%==6 (
    echo 🔄 Restarting bot...
    ssh -i C:\Users\miste\Documents\cryptobot-key.pem ubuntu@3.135.216.32 "cd ~/crypto-trading-bot && pkill -f bot.py && sleep 3 && nohup .venv/bin/python bot.py > bot_output.log 2>&1 &"
) else (
    echo ❌ Invalid choice
)

echo.
pause
echo ⏳ Stopping existing bot...
timeout /t 3 /nobreak >nul
ssh -i "C:\Users\miste\Documents\cryptobot-key.pem" ubuntu@3.135.216.32 "cd crypto-trading-bot && nohup python3 bot.py > bot_log.txt 2>&1 &"
echo ✅ Bot restarted
pause
goto MENU

:TEST
cls
echo 🧪 Testing AWS Connection...
echo ===========================
ping -n 4 3.135.216.32
echo.
ssh -i "C:\Users\miste\Documents\cryptobot-key.pem" ubuntu@3.135.216.32 "echo '✅ SSH connection successful' && date"
pause
goto MENU

:EXIT
cls
echo 👋 Goodbye! Bot will continue running on AWS.
echo ============================================
timeout /t 2 /nobreak >nul
exit
