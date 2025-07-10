# AWS Upload Script for Enhanced Price Jump Detection System (PowerShell)
# Upload all enhanced files including the new multi-timeframe detection system

Write-Host "🚀 Uploading Enhanced Price Jump Detection System to AWS..." -ForegroundColor Green

# Define the AWS server details
$AWS_USER = "ubuntu"
$AWS_HOST = "3.135.216.32"
$AWS_PATH = "~/crypto-trading-bot/"

# List of essential files to upload (core system)
$CORE_FILES = @(
    "bot.py",
    "enhanced_config.json",
    "price_jump_detector.py",
    "multi_timeframe_ma.py",
    "requirements.txt",
    "config.py",
    "enhanced_config.py",
    "enhanced_multi_strategy.py",
    "institutional_strategies.py",
    "log_utils.py",
    "performance_tracker.py",
    "state_manager.py",
    "success_rate_enhancer.py",
    "enhanced_technical_analysis.py"
)

# List of test files to upload (for verification)
$TEST_FILES = @(
    "test_enhanced_detection.py",
    "test_price_jump.py",
    "validate_improvements.py"
)

# List of documentation files to upload
$DOCS = @(
    "ENHANCED_PRICE_DETECTION_SUMMARY.md",
    "PRICE_JUMP_IMPROVEMENTS.md",
    "PRICE_JUMP_ANALYSIS.md"
)

# List of optional state files (if they exist)
$STATE_FILES = @(
    "bot_state.json",
    "trade_log.csv",
    "performance_report.csv"
)

Write-Host "📋 Files to upload:" -ForegroundColor Cyan
Write-Host "   🎯 Core System Files:" -ForegroundColor Yellow
foreach ($file in $CORE_FILES) {
    Write-Host "      - $file" -ForegroundColor White
}

Write-Host "   🧪 Test Files:" -ForegroundColor Yellow
foreach ($file in $TEST_FILES) {
    Write-Host "      - $file" -ForegroundColor White
}

Write-Host "   📚 Documentation:" -ForegroundColor Yellow
foreach ($file in $DOCS) {
    Write-Host "      - $file" -ForegroundColor White
}

Write-Host ""
Write-Host "⚡ Uploading core system files..." -ForegroundColor Green

# Upload core files
foreach ($file in $CORE_FILES) {
    if (Test-Path $file) {
        Write-Host "📤 Uploading $file..." -ForegroundColor Cyan
        $result = scp $file "$AWS_USER@$AWS_HOST`:$AWS_PATH"
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✅ $file uploaded successfully" -ForegroundColor Green
        } else {
            Write-Host "   ❌ $file upload failed" -ForegroundColor Red
        }
    } else {
        Write-Host "   ⚠️ $file not found locally" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "🧪 Uploading test files..." -ForegroundColor Green

# Upload test files
foreach ($file in $TEST_FILES) {
    if (Test-Path $file) {
        Write-Host "📤 Uploading $file..." -ForegroundColor Cyan
        $result = scp $file "$AWS_USER@$AWS_HOST`:$AWS_PATH"
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✅ $file uploaded successfully" -ForegroundColor Green
        } else {
            Write-Host "   ❌ $file upload failed" -ForegroundColor Red
        }
    } else {
        Write-Host "   ⚠️ $file not found locally" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "📚 Uploading documentation..." -ForegroundColor Green

# Upload documentation
foreach ($file in $DOCS) {
    if (Test-Path $file) {
        Write-Host "📤 Uploading $file..." -ForegroundColor Cyan
        $result = scp $file "$AWS_USER@$AWS_HOST`:$AWS_PATH"
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✅ $file uploaded successfully" -ForegroundColor Green
        } else {
            Write-Host "   ❌ $file upload failed" -ForegroundColor Red
        }
    } else {
        Write-Host "   ⚠️ $file not found locally" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "💾 Uploading state files (if present)..." -ForegroundColor Green

# Upload state files if they exist
foreach ($file in $STATE_FILES) {
    if (Test-Path $file) {
        Write-Host "📤 Uploading $file..." -ForegroundColor Cyan
        $result = scp $file "$AWS_USER@$AWS_HOST`:$AWS_PATH"
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✅ $file uploaded successfully" -ForegroundColor Green
        } else {
            Write-Host "   ❌ $file upload failed" -ForegroundColor Red
        }
    } else {
        Write-Host "   ⚠️ $file not found locally" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "🔍 Verifying uploads on AWS..." -ForegroundColor Cyan
ssh "$AWS_USER@$AWS_HOST" "cd $AWS_PATH; echo 'Files in AWS directory:'; ls -la *.py enhanced_config.json *.md | head -20"

Write-Host ""
Write-Host "🎯 Running quick verification test on AWS..." -ForegroundColor Cyan
ssh "$AWS_USER@$AWS_HOST" "cd $AWS_PATH; python3 -c 'import price_jump_detector; print(\"Enhanced detection system imported successfully!\")'"

Write-Host ""
Write-Host "✅ Upload complete! Next steps:" -ForegroundColor Green
Write-Host "   1. SSH into AWS: ssh $AWS_USER@$AWS_HOST" -ForegroundColor White
Write-Host "   2. Navigate to bot directory: cd $AWS_PATH" -ForegroundColor White
Write-Host "   3. Test the enhanced system: python3 test_enhanced_detection.py" -ForegroundColor White
Write-Host "   4. Restart the bot: python3 bot.py" -ForegroundColor White
