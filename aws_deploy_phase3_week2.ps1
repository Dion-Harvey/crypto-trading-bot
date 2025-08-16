# 🚀 CRYPTO TRADING BOT - AWS DEPLOYMENT SCRIPT (PHASE 3 WEEK 2)
# ================================================================
# Deploy Enhanced Bot with LSTM + Pattern Recognition AI
# Target: ubuntu@3.135.216.32 (AWS EC2)
# Features: Dual AI system with advanced pattern detection
# Updated: December 27, 2024

Write-Host "🚀 PHASE 3 WEEK 2 DEPLOYMENT - PATTERN RECOGNITION AI" -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Green

$AWS_HOST = "ubuntu@3.135.216.32"
$REMOTE_DIR = "~/crypto-trading-bot"

# Core files with new AI modules
$FILES_TO_UPLOAD = @(
    "bot.py",
    "config.py", 
    "enhanced_config.json",
    "requirements.txt",
    "pattern_recognition_ai.py",
    "lstm_ai.py",
    "price_jump_detector.py",
    "multi_timeframe_ma.py",
    "enhanced_multi_timeframe_ma.py",
    "priority_functions_5m1m.py",
    "enhanced_multi_strategy.py",
    "institutional_strategies.py",
    "log_utils.py",
    "performance_tracker.py",
    "enhanced_config.py",
    "state_manager.py",
    "success_rate_enhancer.py"
)

# Strategy files
$STRATEGY_FILES = @(
    "strategies/ma_crossover.py",
    "strategies/multi_strategy_optimized.py", 
    "strategies/hybrid_strategy.py"
)

Write-Host "📦 Uploading core files..." -ForegroundColor Yellow

# Upload core files
foreach ($file in $FILES_TO_UPLOAD) {
    if (Test-Path $file) {
        Write-Host "  ✅ Uploading $file" -ForegroundColor Cyan
        scp $file ${AWS_HOST}:${REMOTE_DIR}/
        if ($LASTEXITCODE -ne 0) {
            Write-Host "  ❌ Failed to upload $file" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "  ⚠️ Warning: $file not found" -ForegroundColor Yellow
    }
}

Write-Host "📂 Uploading strategy files..." -ForegroundColor Yellow

# Create strategies directory and upload
ssh $AWS_HOST "mkdir -p ${REMOTE_DIR}/strategies"
foreach ($file in $STRATEGY_FILES) {
    if (Test-Path $file) {
        Write-Host "  ✅ Uploading $file" -ForegroundColor Cyan
        scp $file ${AWS_HOST}:${REMOTE_DIR}/$file
        if ($LASTEXITCODE -ne 0) {
            Write-Host "  ❌ Failed to upload $file" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "  ⚠️ Warning: $file not found" -ForegroundColor Yellow
    }
}

Write-Host "🔧 Installing new AI dependencies..." -ForegroundColor Yellow

# Install new dependencies for Pattern Recognition AI
$INSTALL_COMMANDS = @(
    "cd $REMOTE_DIR",
    "pip3 install --upgrade pip",
    "pip3 install opencv-python-headless>=4.8.0", 
    "pip3 install scikit-learn>=1.3.0",
    "pip3 install scipy>=1.10.0",
    "pip3 install tensorflow-cpu>=2.15.0",
    "pip3 install -r requirements.txt"
)

$INSTALL_SCRIPT = $INSTALL_COMMANDS -join "; "
ssh $AWS_HOST $INSTALL_SCRIPT

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
    exit 1
}

Write-Host "🔄 Restarting bot with new AI capabilities..." -ForegroundColor Yellow

# Stop existing bot and start with new AI
$RESTART_COMMANDS = @(
    "cd $REMOTE_DIR",
    "pkill -f 'python.*bot.py' || true",
    "sleep 2",
    "nohup python3 bot.py > bot_output.log 2>&1 &",
    "sleep 3",
    "ps aux | grep 'python.*bot.py' | grep -v grep"
)

$RESTART_SCRIPT = $RESTART_COMMANDS -join "; "
ssh $AWS_HOST $RESTART_SCRIPT

Write-Host ""
Write-Host "✅ PHASE 3 WEEK 2 DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "🧠 LSTM AI (Week 1): Active" -ForegroundColor Cyan
Write-Host "👁️ Pattern Recognition AI (Week 2): Active" -ForegroundColor Cyan
Write-Host "📊 Enhanced Signal Validation: Active" -ForegroundColor Cyan
Write-Host "🎯 Advanced Pattern Detection: Active" -ForegroundColor Cyan
Write-Host ""
Write-Host "🔍 To check bot status:" -ForegroundColor Yellow
Write-Host "ssh $AWS_HOST" -ForegroundColor White
Write-Host "cd $REMOTE_DIR && tail -f bot_output.log" -ForegroundColor White
Write-Host ""
Write-Host "📈 The bot is now running with dual AI system!" -ForegroundColor Green
