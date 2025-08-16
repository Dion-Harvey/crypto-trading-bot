@echo off
echo.
echo 🚨 CRYPTO TRADING BOT - AWS ONLY
echo ================================
echo.
echo ❌ This bot is configured to run ONLY on AWS EC2
echo ❌ Local execution is BLOCKED to prevent interference
echo.
echo 🎯 AWS Details:
echo    IP: 3.135.216.32
echo    User: ubuntu
echo    Key: cryptobot-key.pem
echo.
echo 💡 To manage the bot:
echo    1. ssh -i cryptobot-key.pem ubuntu@3.135.216.32
echo    2. cd ~/crypto-trading-bot
echo    3. .venv/bin/python bot.py
echo.
echo 🛑 Local execution prevented!
echo.
pause
