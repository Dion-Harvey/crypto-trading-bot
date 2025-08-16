@echo off
echo 🎯 RESTARTING AWS BOT WITH NATIVE TRAILING STOPS
echo ================================================

echo.
echo 1. Stopping current bot process...
ssh -i C:\Users\miste\Documents\cryptobot-key.pem ubuntu@3.135.216.32 "pkill -f python.*bot.py"
timeout /t 3 /nobreak >nul

echo.
echo 2. Starting bot with native trailing stop configuration...
ssh -i C:\Users\miste\Documents\cryptobot-key.pem ubuntu@3.135.216.32 "cd crypto-trading-bot && python3 bot.py > bot_log.txt 2>&1 &"
timeout /t 2 /nobreak >nul

echo.
echo 3. Checking bot status...
ssh -i C:\Users\miste\Documents\cryptobot-key.pem ubuntu@3.135.216.32 "ps aux | grep python.*bot.py | grep -v grep"

echo.
echo 4. Checking recent logs...
ssh -i C:\Users\miste\Documents\cryptobot-key.pem ubuntu@3.135.216.32 "cd crypto-trading-bot && tail -10 bot_log.txt"

echo.
echo ✅ Bot restart complete!
echo 🎯 Native trailing stops (0.25% callback rate) are now active
echo.
pause
