@echo off
echo 🔧 AWS API Key Fix
echo ==================

set AWS_USER=ubuntu
set AWS_HOST=3.135.216.32

echo 🔑 Testing SSH connection to AWS...

:: Test SSH connection
ssh %AWS_USER%@%AWS_HOST% "echo Connection test" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ SSH connection successful!
    echo 📝 Updating config.py on AWS...
    
    :: Create temporary config file
    echo # config.py > temp_config.py
    echo # Place your Binance API credentials here. Do NOT commit this file to version control! >> temp_config.py
    echo. >> temp_config.py
    echo BINANCE_API_KEY = "bN4mjzb1pIfmRZCit0zjqxACIv1JszpbPDi3Zlhbh1961qsFgvwio6UWzIyUwQND" >> temp_config.py
    echo BINANCE_API_SECRET = "Rq5p1qTSwq4qmb8xgb7kdKHZGlPVvIaiakF5jiu43dknp0nGg17jDLtuIwZ1cWza" >> temp_config.py
    echo. >> temp_config.py
    
    :: Upload to AWS
    scp temp_config.py %AWS_USER%@%AWS_HOST%:~/crypto-trading-bot/config.py
    if %errorlevel% equ 0 (
        echo ✅ Config uploaded successfully!
        
        echo 🧪 Testing API connection on AWS...
        ssh %AWS_USER%@%AWS_HOST% "cd ~/crypto-trading-bot && python3 connection_test.py"
        
        echo 🔄 Stopping old bot processes...
        ssh %AWS_USER%@%AWS_HOST% "pkill -f 'python.*bot.py'; exit 0"
        
        echo ✅ AWS API key fix completed!
    ) else (
        echo ❌ Failed to upload config
    )
    
    :: Clean up
    del temp_config.py
    
) else (
    echo ❌ SSH connection failed
    echo.
    echo 🔧 MANUAL FIX REQUIRED:
    echo 1. SSH into AWS: ssh -i your-key.pem ubuntu@3.135.216.32
    echo 2. Edit config: cd ~/crypto-trading-bot ^&^& nano config.py
    echo 3. Update API keys with:
    echo    BINANCE_API_KEY = "bN4mjzb1pIfmRZCit0zjqxACIv1JszpbPDi3Zlhbh1961qsFgvwio6UWzIyUwQND"
    echo    BINANCE_API_SECRET = "Rq5p1qTSwq4qmb8xgb7kdKHZGlPVvIaiakF5jiu43dknp0nGg17jDLtuIwZ1cWza"
    echo 4. Save (Ctrl+X, Y, Enter)
    echo 5. Test: python3 connection_test.py
    echo 6. Stop old processes: pkill -f 'python.*bot.py'
)

pause
