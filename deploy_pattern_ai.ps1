# 🚀 PHASE 3 WEEK 2 DEPLOYMENT - PATTERN RECOGNITION AI
# ========================================================
# Deploy Enhanced Bot with LSTM + Pattern Recognition AI
# Target: ubuntu@3.135.216.32 (AWS EC2)
# Key: C:\Users\miste\Documents\cryptobot-key.pem

Write-Host "🚀 PHASE 3 WEEK 2 DEPLOYMENT - PATTERN RECOGNITION AI" -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Green

$AWS_KEY = "C:\Users\miste\Documents\cryptobot-key.pem"
$AWS_HOST = "ubuntu@3.135.216.32"
$REMOTE_DIR = "~/crypto-trading-bot"

# Core files to upload
$FILES_TO_UPLOAD = @(
    "pattern_recognition_ai.py",
    "bot.py",
    "requirements.txt"
)

Write-Host "📦 Uploading files with Pattern Recognition AI..." -ForegroundColor Yellow

# Upload files one by one
foreach ($file in $FILES_TO_UPLOAD) {
    if (Test-Path $file) {
        Write-Host "  ✅ Uploading $file" -ForegroundColor Cyan
        scp -i $AWS_KEY $file ${AWS_HOST}:${REMOTE_DIR}/
        if ($LASTEXITCODE -ne 0) {
            Write-Host "  ❌ Failed to upload $file" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "  ⚠️ Warning: $file not found" -ForegroundColor Yellow
    }
}

Write-Host "🔧 Installing Pattern Recognition AI dependencies..." -ForegroundColor Yellow

# Install new dependencies and restart bot
ssh -i $AWS_KEY $AWS_HOST @"
cd $REMOTE_DIR
echo '🔧 Installing new AI dependencies...'
pip3 install opencv-python-headless>=4.8.0 --quiet
pip3 install scikit-learn>=1.3.0 --quiet  
pip3 install scipy>=1.10.0 --quiet
pip3 install tensorflow-cpu>=2.15.0 --quiet
echo '🔄 Stopping existing bot...'
pkill -f 'python.*bot.py' || true
sleep 2
echo '🚀 Starting bot with Pattern Recognition AI...'
nohup python3 bot.py > bot_output.log 2>&1 &
sleep 3
echo '✅ Checking bot status...'
ps aux | grep 'python.*bot.py' | grep -v grep
echo '🎯 Pattern Recognition AI deployment complete!'
"@

Write-Host ""
Write-Host "✅ PHASE 3 WEEK 2 DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "🧠 LSTM AI (Week 1): Active" -ForegroundColor Cyan
Write-Host "👁️ Pattern Recognition AI (Week 2): Active" -ForegroundColor Cyan
Write-Host "📊 Enhanced Signal Validation: Active" -ForegroundColor Cyan
Write-Host "🎯 Advanced Pattern Detection: Active" -ForegroundColor Cyan
Write-Host ""
Write-Host "🔍 To check bot status:" -ForegroundColor Yellow
Write-Host "ssh -i C:\Users\miste\Documents\cryptobot-key.pem ubuntu@3.135.216.32" -ForegroundColor White
Write-Host "cd ~/crypto-trading-bot && tail -f bot_output.log" -ForegroundColor White
Write-Host ""
Write-Host "📈 The bot is now running with dual AI system!" -ForegroundColor Green
