@echo off
echo 📊 Checking AWS Bot Status...
echo =============================

echo 🔍 Checking for running bot processes...
ssh -i "C:\Users\miste\Documents\cryptobot-key.pem" ubuntu@3.135.216.32 "ps aux | grep -E '(bot\.py|python.*bot)' | grep -v grep"

echo.
echo 📝 Latest bot log entries...
ssh -i "C:\Users\miste\Documents\cryptobot-key.pem" ubuntu@3.135.216.32 "tail -10 crypto-trading-bot/bot_log.txt"

echo.
echo 🕒 AWS instance uptime...
ssh -i "C:\Users\miste\Documents\cryptobot-key.pem" ubuntu@3.135.216.32 "uptime"

pause
