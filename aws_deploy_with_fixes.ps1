#!/usr/bin/env powershell
# 🚀 AWS DEPLOYMENT SCRIPT WITH ALL RECENT FIXES
# ===============================================
# Deploys the enhanced multi-pair trading bot with:
# ✅ Multi-pair communication fixes
# ✅ Stop-limit order accumulation fixes  
# ✅ 16-pair monitoring system
# ✅ Emergency cleanup utilities

Write-Host "🚀 DEPLOYING ENHANCED CRYPTO TRADING BOT TO AWS..." -ForegroundColor Green
Write-Host "=" * 60

# Configuration
$KeyFile = "C:\Users\miste\Downloads\cryptobot-key.pem"
$AWSHost = "ubuntu@3.135.216.32"
$TargetDir = "~/cryptobot/crypto-trading-bot/"

# Check if key file exists
if (-not (Test-Path $KeyFile)) {
    Write-Host "❌ ERROR: Key file not found at $KeyFile" -ForegroundColor Red
    Write-Host "Please ensure cryptobot-key.pem is in your Downloads folder" -ForegroundColor Yellow
    exit 1
}

Write-Host "🔑 Setting key file permissions..." -ForegroundColor Cyan
icacls $KeyFile /inheritance:r /grant:r "$env:USERNAME:(R)" | Out-Null

Write-Host "📁 Creating directory structure on AWS..." -ForegroundColor Cyan
ssh -i $KeyFile $AWSHost "mkdir -p $TargetDir/strategies"

Write-Host "📤 Uploading CORE APPLICATION FILES..." -ForegroundColor Yellow

# Core application files with fixes
$CoreFiles = @(
    "bot.py",                           # Main bot with stop-limit fix
    "config.py",                        # Configuration
    "enhanced_config.json",             # Enhanced configuration with 16 pairs
    "enhanced_config.py",               # Configuration management with runtime reload
    "requirements.txt"                  # Dependencies
)

foreach ($file in $CoreFiles) {
    if (Test-Path $file) {
        Write-Host "   ✅ Uploading $file" -ForegroundColor Green
        scp -i $KeyFile $file "${AWSHost}:${TargetDir}/"
    } else {
        Write-Host "   ❌ Missing: $file" -ForegroundColor Red
    }
}

Write-Host "`n📤 Uploading MULTI-PAIR SYSTEM FILES..." -ForegroundColor Yellow

# Multi-pair system files
$MultiPairFiles = @(
    "start_multipair_system.py",       # Multi-pair orchestration system
    "multi_pair_scanner.py",           # Opportunity scanner
    "check_multipair_status.py"        # Status checker
)

foreach ($file in $MultiPairFiles) {
    if (Test-Path $file) {
        Write-Host "   ✅ Uploading $file" -ForegroundColor Green
        scp -i $KeyFile $file "${AWSHost}:${TargetDir}/"
    } else {
        Write-Host "   ❌ Missing: $file" -ForegroundColor Red
    }
}

Write-Host "`n📤 Uploading EMERGENCY UTILITIES..." -ForegroundColor Yellow

# Emergency utilities for order management
$EmergencyFiles = @(
    "emergency_order_cleanup.py",      # Emergency order cleanup
    "fix_verification.py"              # Fix verification tool
)

foreach ($file in $EmergencyFiles) {
    if (Test-Path $file) {
        Write-Host "   ✅ Uploading $file" -ForegroundColor Green
        scp -i $KeyFile $file "${AWSHost}:${TargetDir}/"
    } else {
        Write-Host "   ⚠️  Missing: $file (will create on AWS)" -ForegroundColor Yellow
    }
}

Write-Host "`n📤 Uploading STRATEGY FILES..." -ForegroundColor Yellow

# Strategy files
$StrategyFiles = @(
    "strategies/ma_crossover.py",
    "strategies/multi_strategy_optimized.py", 
    "strategies/hybrid_strategy.py"
)

foreach ($file in $StrategyFiles) {
    if (Test-Path $file) {
        Write-Host "   ✅ Uploading $file" -ForegroundColor Green
        scp -i $KeyFile $file "${AWSHost}:${TargetDir}/$file"
    } else {
        Write-Host "   ❌ Missing: $file" -ForegroundColor Red
    }
}

Write-Host "`n📤 Uploading SUPPORT MODULES..." -ForegroundColor Yellow

# Support modules
$SupportFiles = @(
    "enhanced_multi_strategy.py",
    "institutional_strategies.py",
    "log_utils.py",
    "performance_tracker.py",
    "state_manager.py",
    "success_rate_enhancer.py"
)

foreach ($file in $SupportFiles) {
    if (Test-Path $file) {
        Write-Host "   ✅ Uploading $file" -ForegroundColor Green
        scp -i $KeyFile $file "${AWSHost}:${TargetDir}/"
    } else {
        Write-Host "   ⚠️  Missing: $file" -ForegroundColor Yellow
    }
}

Write-Host "`n📊 Uploading STATE FILES (optional)..." -ForegroundColor Yellow

# State files (optional)
$StateFiles = @(
    "bot_state.json",
    "trade_log.csv", 
    "performance_report.csv"
)

foreach ($file in $StateFiles) {
    if (Test-Path $file) {
        Write-Host "   ✅ Uploading $file" -ForegroundColor Green
        scp -i $KeyFile $file "${AWSHost}:${TargetDir}/"
    } else {
        Write-Host "   ⚠️  Not found: $file (will be created)" -ForegroundColor Yellow
    }
}

Write-Host "`n🔧 Setting up AWS environment..." -ForegroundColor Cyan

# Install dependencies and set permissions
ssh -i $KeyFile $AWSHost @"
cd $TargetDir
echo '🐍 Installing Python dependencies...'
pip3 install -r requirements.txt

echo '🔐 Setting file permissions...'
chmod 600 config.py
chmod +x *.py

echo '📊 Checking system status...'
python3 -c 'from enhanced_config import get_bot_config; print(f\"✅ Config loaded: {len(get_bot_config().get_supported_pairs())} pairs\")'

echo '🎯 AWS deployment complete!'
"@

Write-Host "`n✅ DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "=" * 60
Write-Host "🎯 Next steps:" -ForegroundColor Cyan
Write-Host "   1. SSH into AWS: ssh -i `"$KeyFile`" $AWSHost" -ForegroundColor White
Write-Host "   2. Navigate to bot: cd $TargetDir" -ForegroundColor White
Write-Host "   3. Check status: python3 check_multipair_status.py" -ForegroundColor White
Write-Host "   4. Start system: python3 start_multipair_system.py" -ForegroundColor White

Write-Host "`n🚀 FIXES DEPLOYED:" -ForegroundColor Green
Write-Host "   ✅ Multi-pair communication system" -ForegroundColor White
Write-Host "   ✅ Stop-limit order accumulation fix" -ForegroundColor White  
Write-Host "   ✅ 16-pair monitoring system" -ForegroundColor White
Write-Host "   ✅ Emergency cleanup utilities" -ForegroundColor White
Write-Host "   ✅ Runtime config reload capability" -ForegroundColor White

Write-Host "`n⚠️  IMPORTANT REMINDERS:" -ForegroundColor Yellow
Write-Host "   🔑 Verify your API keys are set in config.py" -ForegroundColor White
Write-Host "   🧹 Run emergency_order_cleanup.py if needed" -ForegroundColor White
Write-Host "   📊 Monitor the system with check_multipair_status.py" -ForegroundColor White
Write-Host "   💰 Start with small amounts for testing" -ForegroundColor White
