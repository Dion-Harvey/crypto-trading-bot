# AWS Upload Script for Price Jump Detection Improvements (PowerShell)
# Upload all enhanced files to AWS server

Write-Host "🚀 Uploading Price Jump Detection Improvements to AWS..." -ForegroundColor Green

# Define the AWS server details
$AWS_USER = "ubuntu"
$AWS_HOST = "3.135.216.32"
$AWS_PATH = "~/crypto-trading-bot/"

# List of files to upload
$FILES = @(
    "bot.py",
    "enhanced_config.json", 
    "price_jump_detector.py",
    "multi_timeframe_ma.py",
    "PRICE_JUMP_IMPROVEMENTS.md",
    "PRICE_JUMP_ANALYSIS.md",
    "validate_improvements.py",
    "test_imports.py"
)

Write-Host "📋 Files to upload:" -ForegroundColor Cyan
foreach ($file in $FILES) {
    Write-Host "   - $file" -ForegroundColor White
}

Write-Host ""
Write-Host "⚡ Uploading files..." -ForegroundColor Yellow

# Upload each file
foreach ($file in $FILES) {
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
ssh "$AWS_USER@$AWS_HOST" "cd $AWS_PATH; ls -la price_jump_detector.py multi_timeframe_ma.py"

Write-Host ""
Write-Host "🧪 Testing imports on AWS..." -ForegroundColor Cyan
ssh "$AWS_USER@$AWS_HOST" "cd $AWS_PATH; python3 test_imports.py"

Write-Host ""
Write-Host "✅ AWS upload complete!" -ForegroundColor Green
Write-Host "🎯 Price jump detection improvements are now deployed on AWS" -ForegroundColor Green
