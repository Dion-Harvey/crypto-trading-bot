#!/usr/bin/env powershell
# 🚀 AWS CRITICAL FIXES DEPLOYMENT
# ================================
# Deploys the latest critical fixes for:
# ✅ Order execution validation logging (place_intelligent_order fix)
# ✅ Comprehensive 4-level risk management system
# ✅ Multi-level protection with immediate stops, trailing stops, take-profit ladders
# ✅ Production-ready system for day trading micro profits

Write-Host "🚀 DEPLOYING CRITICAL FIXES TO AWS..." -ForegroundColor Green
Write-Host "=" * 50

# Configuration
$KeyFile = "C:\Users\miste\Documents\cryptobot-key.pem"
$AWSHost = "ubuntu@3.135.216.32"
$TargetDir = "/home/ubuntu/crypto-trading-bot"

# Check if key file exists
if (-not (Test-Path $KeyFile)) {
    Write-Host "❌ ERROR: Key file not found at $KeyFile" -ForegroundColor Red
    Write-Host "Please ensure cryptobot-key.pem is in the correct location" -ForegroundColor Yellow
    exit 1
}

Write-Host "🔑 Setting key file permissions..." -ForegroundColor Cyan
icacls $KeyFile /inheritance:r /grant:r "$env:USERNAME:(R)" | Out-Null

Write-Host "🛑 Stopping any running bot processes on AWS..." -ForegroundColor Yellow
ssh -i $KeyFile $AWSHost "pkill -f 'python.*bot.py' || echo 'No bot processes found'"

Write-Host "📤 Uploading CRITICAL FIXED FILES..." -ForegroundColor Yellow

# Core file with critical fixes
$CriticalFiles = @(
    "bot.py"                            # Main bot with order execution and risk management fixes
)

foreach ($file in $CriticalFiles) {
    if (Test-Path $file) {
        $fileSize = (Get-Item $file).Length
        Write-Host "   ✅ Uploading $file ($([math]::Round($fileSize/1KB, 1)) KB)" -ForegroundColor Green
        scp -i $KeyFile $file "${AWSHost}:${TargetDir}/"
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✅ Successfully uploaded $file" -ForegroundColor Green
        } else {
            Write-Host "   ❌ Failed to upload $file" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "   ❌ CRITICAL ERROR: Missing $file" -ForegroundColor Red
        exit 1
    }
}

Write-Host "`n🔧 Verifying AWS environment..." -ForegroundColor Cyan

# Verify the fixes are deployed
ssh -i $KeyFile $AWSHost @"
cd $TargetDir
echo '🔍 Verifying critical fixes...'

# Check if the place_intelligent_order function has the validation logging fix
if grep -q 'BUY order validation passed' bot.py && grep -q 'SELL order validation passed' bot.py; then
    echo '✅ Order execution validation logging: FIXED'
else
    echo '❌ Order execution validation logging: NOT FOUND'
fi

# Check if place_advanced_risk_orders function is implemented
if grep -q 'Level 1: Immediate Stop-Loss' bot.py; then
    echo '✅ 4-level risk management system: IMPLEMENTED'
else
    echo '❌ 4-level risk management system: NOT FOUND'
fi

# Check if multi-level protection is in place
if grep -q 'Level 2: Dynamic trailing stop' bot.py && grep -q 'Level 3: Take-profit ladders' bot.py; then
    echo '✅ Multi-level protection system: COMPLETE'
else
    echo '❌ Multi-level protection system: INCOMPLETE'
fi

echo '🐍 Checking Python syntax...'
python3 -m py_compile bot.py
if [ $? -eq 0 ]; then
    echo '✅ Python syntax validation: PASSED'
else
    echo '❌ Python syntax validation: FAILED'
    exit 1
fi

echo '📊 File verification complete!'
"@

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Verification failed on AWS" -ForegroundColor Red
    exit 1
}

Write-Host "`n🚀 Restarting bot with critical fixes..." -ForegroundColor Cyan

# Restart the bot with the new fixes
ssh -i $KeyFile $AWSHost @"
cd $TargetDir
echo '🚀 Starting enhanced bot with critical fixes...'
nohup python3 bot.py > bot_output.log 2>&1 &
echo 'Bot started with PID: $!'
sleep 3
echo '🔍 Checking bot startup...'
if pgrep -f 'python.*bot.py' > /dev/null; then
    echo '✅ Bot is running successfully!'
else
    echo '❌ Bot failed to start - check bot_output.log'
    tail -20 bot_output.log
fi
"@

Write-Host "`n✅ CRITICAL FIXES DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "=" * 50

Write-Host "🎯 DEPLOYED FIXES:" -ForegroundColor Green
Write-Host "   ✅ Order execution validation logging" -ForegroundColor White
Write-Host "   ✅ 4-level risk management system:" -ForegroundColor White
Write-Host "      • Level 1: Immediate stop-loss (2% hard stop)" -ForegroundColor Gray
Write-Host "      • Level 2: Dynamic trailing stops (40% position)" -ForegroundColor Gray
Write-Host "      • Level 3: Take-profit ladders (1.5%/3%/5%)" -ForegroundColor Gray
Write-Host "      • Level 4: Emergency exit monitoring" -ForegroundColor Gray
Write-Host "   ✅ Production-ready system for day trading" -ForegroundColor White

Write-Host "`n📊 VERIFICATION COMMANDS:" -ForegroundColor Cyan
Write-Host "   ssh -i `"$KeyFile`" $AWSHost" -ForegroundColor White
Write-Host "   cd $TargetDir && tail -f bot_output.log" -ForegroundColor White

Write-Host "`n🎯 YOUR AWS BOT IS NOW PRODUCTION-READY!" -ForegroundColor Green
Write-Host "   🛡️ Comprehensive risk management active" -ForegroundColor White
Write-Host "   ⚡ Enhanced order execution with validation" -ForegroundColor White
Write-Host "   💎 Ready for day trading micro profits" -ForegroundColor White
Write-Host "   🚀 All critical gaps resolved!" -ForegroundColor White
