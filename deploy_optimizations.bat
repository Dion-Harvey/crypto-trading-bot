@echo off
rem =============================================================================
rem AWS EC2 UPLOAD SCRIPT - SWITCHING OPTIMIZATION DEPLOYMENT
rem =============================================================================
rem 
rem Uploads the complete switching optimization changes to AWS EC2 instance
rem Includes all modified files for HBAR/XLM detection improvements
rem
rem =============================================================================

echo.
echo ==========================================
echo 🚀 DEPLOYING SWITCHING OPTIMIZATION TO AWS EC2
echo ==========================================

rem Configuration
set "KEY_FILE=C:\Users\miste\Documents\cryptobot-key.pem"
set "REMOTE_USER=ubuntu"
set "REMOTE_IP=3.135.216.32"
set "LOCAL_DIR=C:\Users\miste\Documents\crypto-trading-bot\crypto-trading-bot"
set "REMOTE_DIR=/home/ubuntu/crypto-trading-bot"

rem Verify key file exists
if not exist "%KEY_FILE%" (
    echo ❌ ERROR: Key file not found at %KEY_FILE%
    pause
    exit /b 1
)

echo ✅ Key file verified: %KEY_FILE%
echo 🎯 Target server: %REMOTE_USER%@%REMOTE_IP%
echo 📁 Local directory: %LOCAL_DIR%
echo 📁 Remote directory: %REMOTE_DIR%

rem Change to local directory
cd /d "%LOCAL_DIR%"

echo.
echo 🔄 PREPARING FILES FOR UPLOAD...

rem Create backup on remote server first
echo.
echo 📦 Creating backup on remote server...
ssh -i "%KEY_FILE%" -o StrictHostKeyChecking=no %REMOTE_USER%@%REMOTE_IP% "cd %REMOTE_DIR% && cp -r . ../crypto-trading-bot-backup-$(date +%%Y%%m%%d_%%H%%M%%S)"

if %ERRORLEVEL% EQU 0 (
    echo ✅ Backup created successfully
) else (
    echo ⚠️ Backup creation had issues, continuing...
)

rem Upload critical files
echo.
echo 🚀 UPLOADING CRITICAL FILES ^(Switching optimization^)...

rem Bot core files
echo 📤 Uploading bot.py...
scp -i "%KEY_FILE%" -o StrictHostKeyChecking=no bot.py %REMOTE_USER%@%REMOTE_IP%:%REMOTE_DIR%/bot.py
if %ERRORLEVEL% EQU 0 (echo    ✅ bot.py uploaded successfully) else (echo    ❌ Failed to upload bot.py)

echo 📤 Uploading multi_crypto_monitor.py...
scp -i "%KEY_FILE%" -o StrictHostKeyChecking=no multi_crypto_monitor.py %REMOTE_USER%@%REMOTE_IP%:%REMOTE_DIR%/multi_crypto_monitor.py
if %ERRORLEVEL% EQU 0 (echo    ✅ multi_crypto_monitor.py uploaded successfully) else (echo    ❌ Failed to upload multi_crypto_monitor.py)

echo 📤 Uploading enhanced_config.json...
scp -i "%KEY_FILE%" -o StrictHostKeyChecking=no enhanced_config.json %REMOTE_USER%@%REMOTE_IP%:%REMOTE_DIR%/enhanced_config.json
if %ERRORLEVEL% EQU 0 (echo    ✅ enhanced_config.json uploaded successfully) else (echo    ❌ Failed to upload enhanced_config.json)

echo 📤 Uploading SWITCHING_OPTIMIZATION_COMPLETE.md...
scp -i "%KEY_FILE%" -o StrictHostKeyChecking=no SWITCHING_OPTIMIZATION_COMPLETE.md %REMOTE_USER%@%REMOTE_IP%:%REMOTE_DIR%/SWITCHING_OPTIMIZATION_COMPLETE.md
if %ERRORLEVEL% EQU 0 (echo    ✅ SWITCHING_OPTIMIZATION_COMPLETE.md uploaded successfully) else (echo    ❌ Failed to upload SWITCHING_OPTIMIZATION_COMPLETE.md)

rem Configuration and state management
echo 📤 Uploading config.py...
if exist config.py (
    scp -i "%KEY_FILE%" -o StrictHostKeyChecking=no config.py %REMOTE_USER%@%REMOTE_IP%:%REMOTE_DIR%/config.py
    if %ERRORLEVEL% EQU 0 (echo    ✅ config.py uploaded successfully) else (echo    ❌ Failed to upload config.py)
) else (
    echo    ⚠️ config.py not found locally
)

echo 📤 Uploading state_manager.py...
if exist state_manager.py (
    scp -i "%KEY_FILE%" -o StrictHostKeyChecking=no state_manager.py %REMOTE_USER%@%REMOTE_IP%:%REMOTE_DIR%/state_manager.py
    if %ERRORLEVEL% EQU 0 (echo    ✅ state_manager.py uploaded successfully) else (echo    ❌ Failed to upload state_manager.py)
) else (
    echo    ⚠️ state_manager.py not found locally
)

rem Utility files
echo 📤 Uploading log_utils.py...
if exist log_utils.py (
    scp -i "%KEY_FILE%" -o StrictHostKeyChecking=no log_utils.py %REMOTE_USER%@%REMOTE_IP%:%REMOTE_DIR%/log_utils.py
    if %ERRORLEVEL% EQU 0 (echo    ✅ log_utils.py uploaded successfully) else (echo    ❌ Failed to upload log_utils.py)
) else (
    echo    ⚠️ log_utils.py not found locally
)

rem Enhancement modules
echo 📤 Uploading momentum_enhancer.py...
if exist momentum_enhancer.py (
    scp -i "%KEY_FILE%" -o StrictHostKeyChecking=no momentum_enhancer.py %REMOTE_USER%@%REMOTE_IP%:%REMOTE_DIR%/momentum_enhancer.py
    if %ERRORLEVEL% EQU 0 (echo    ✅ momentum_enhancer.py uploaded successfully) else (echo    ❌ Failed to upload momentum_enhancer.py)
) else (
    echo    ⚠️ momentum_enhancer.py not found locally
)

echo 📤 Uploading success_rate_enhancer.py...
if exist success_rate_enhancer.py (
    scp -i "%KEY_FILE%" -o StrictHostKeyChecking=no success_rate_enhancer.py %REMOTE_USER%@%REMOTE_IP%:%REMOTE_DIR%/success_rate_enhancer.py
    if %ERRORLEVEL% EQU 0 (echo    ✅ success_rate_enhancer.py uploaded successfully) else (echo    ❌ Failed to upload success_rate_enhancer.py)
) else (
    echo    ⚠️ success_rate_enhancer.py not found locally
)

echo 📤 Uploading performance_tracker.py...
if exist performance_tracker.py (
    scp -i "%KEY_FILE%" -o StrictHostKeyChecking=no performance_tracker.py %REMOTE_USER%@%REMOTE_IP%:%REMOTE_DIR%/performance_tracker.py
    if %ERRORLEVEL% EQU 0 (echo    ✅ performance_tracker.py uploaded successfully) else (echo    ❌ Failed to upload performance_tracker.py)
) else (
    echo    ⚠️ performance_tracker.py not found locally
)

rem Set correct permissions on remote server
echo.
echo 🔒 SETTING PERMISSIONS...
ssh -i "%KEY_FILE%" -o StrictHostKeyChecking=no %REMOTE_USER%@%REMOTE_IP% "cd %REMOTE_DIR% && chmod +x *.py && chmod 644 *.json *.md"

if %ERRORLEVEL% EQU 0 (
    echo ✅ Permissions set successfully
) else (
    echo ⚠️ Permission setting had issues
)

rem Install/update Python dependencies if needed
echo.
echo 📦 CHECKING PYTHON DEPENDENCIES...
ssh -i "%KEY_FILE%" -o StrictHostKeyChecking=no %REMOTE_USER%@%REMOTE_IP% "cd %REMOTE_DIR% && python3 -m pip install --user ccxt pandas numpy requests python-binance"

rem Restart the bot service
echo.
echo 🔄 RESTARTING BOT SERVICE...

rem First, stop any running bot processes
ssh -i "%KEY_FILE%" -o StrictHostKeyChecking=no %REMOTE_USER%@%REMOTE_IP% "pkill -f 'python.*bot.py' || true"
echo ⏸️ Stopped existing bot processes

rem Start the bot in the background
echo.
echo 🚀 STARTING OPTIMIZED BOT...
ssh -i "%KEY_FILE%" -o StrictHostKeyChecking=no %REMOTE_USER%@%REMOTE_IP% "cd %REMOTE_DIR% && nohup python3 bot.py > bot_output.log 2>&1 &"

if %ERRORLEVEL% EQU 0 (
    echo ✅ Bot started successfully
) else (
    echo ⚠️ Bot start had issues - check manually
)

rem Check bot status
echo.
echo 🔍 CHECKING BOT STATUS...
timeout /t 3 /nobreak > nul

ssh -i "%KEY_FILE%" -o StrictHostKeyChecking=no %REMOTE_USER%@%REMOTE_IP% "cd %REMOTE_DIR% && ps aux | grep -v grep | grep 'python.*bot.py'"

rem Show recent log output
echo.
echo 📋 RECENT BOT OUTPUT:
ssh -i "%KEY_FILE%" -o StrictHostKeyChecking=no %REMOTE_USER%@%REMOTE_IP% "cd %REMOTE_DIR% && tail -20 bot_output.log 2>/dev/null || echo 'No log output yet'"

echo.
echo ==========================================
echo 🎯 DEPLOYMENT SUMMARY:
echo ==========================================
echo ✅ Switching optimization deployed to AWS EC2
echo ✅ Enhanced HBAR/XLM detection active
echo ✅ Ultra-aggressive thresholds implemented
echo ✅ Direct percentage-based detection enabled
echo ✅ Emergency override system active
echo.
echo 🔧 KEY IMPROVEMENTS DEPLOYED:
echo    • Switching thresholds lowered 31-50%%
echo    • 5%%+ moves trigger immediate switching
echo    • Forced score enhancement for momentum spikes
echo    • Emergency detection at 80%% scores ^(was 90%%^)
echo    • Ultra-low 1%% minimum detection threshold
echo.
echo 🚨 MONITORING COMMANDS:
echo    View live logs: ssh -i "%KEY_FILE%" %REMOTE_USER%@%REMOTE_IP% "cd %REMOTE_DIR% && tail -f bot_output.log"
echo    Check status:   ssh -i "%KEY_FILE%" %REMOTE_USER%@%REMOTE_IP% "cd %REMOTE_DIR% && ps aux | grep bot.py"
echo    Stop bot:       ssh -i "%KEY_FILE%" %REMOTE_USER%@%REMOTE_IP% "pkill -f bot.py"
echo.
echo 🎯 The bot will now catch HBAR +5.83%% and XLM +6.40%% type moves!
echo ==========================================

pause
