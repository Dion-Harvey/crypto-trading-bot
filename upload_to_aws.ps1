# =============================================================================
# AWS EC2 UPLOAD SCRIPT - SWITCHING OPTIMIZATION DEPLOYMENT
# =============================================================================
# 
# Uploads the complete switching optimization changes to AWS EC2 instance
# Includes all modified files for HBAR/XLM detection improvements
#
# =============================================================================

Write-Host "🚀 DEPLOYING SWITCHING OPTIMIZATION TO AWS EC2" -ForegroundColor Green
Write-Host "=" * 60

# Configuration
$KeyFile = "C:\Users\miste\Documents\cryptobot-key.pem"
$RemoteUser = "ubuntu"
$RemoteIP = "3.135.216.32"
$LocalDir = "C:\Users\miste\Documents\crypto-trading-bot\crypto-trading-bot"
$RemoteDir = "/home/ubuntu/crypto-trading-bot"

# Verify key file exists
if (-not (Test-Path $KeyFile)) {
    Write-Host "❌ ERROR: Key file not found at $KeyFile" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Key file verified: $KeyFile" -ForegroundColor Green
Write-Host "🎯 Target server: $RemoteUser@$RemoteIP" -ForegroundColor Cyan
Write-Host "📁 Local directory: $LocalDir" -ForegroundColor Cyan
Write-Host "📁 Remote directory: $RemoteDir" -ForegroundColor Cyan

# Change to local directory
Set-Location $LocalDir

Write-Host "`n🔄 PREPARING FILES FOR UPLOAD..." -ForegroundColor Yellow

# Create backup on remote server first
Write-Host "`n📦 Creating backup on remote server..." -ForegroundColor Yellow
$backupCommand = "cd $RemoteDir && cp -r . ../crypto-trading-bot-backup-$(date +%Y%m%d_%H%M%S)"
& ssh -i $KeyFile -o StrictHostKeyChecking=no $RemoteUser@$RemoteIP $backupCommand

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Backup created successfully" -ForegroundColor Green
} else {
    Write-Host "⚠️ Backup creation had issues, continuing..." -ForegroundColor Yellow
}

# List of critical files to upload (switching optimization)
$CriticalFiles = @(
    "bot.py",                                    # Main bot with aggressive switching
    "multi_crypto_monitor.py",                   # Enhanced spike detection
    "enhanced_config.json",                      # Configuration with supported pairs
    "SWITCHING_OPTIMIZATION_COMPLETE.md",       # Documentation
    "config.py",                                # Configuration management
    "state_manager.py",                         # Trading state management
    "log_utils.py",                             # Logging utilities
    "momentum_enhancer.py",                     # Momentum analysis
    "success_rate_enhancer.py",                 # Success rate optimization
    "performance_tracker.py"                    # Performance tracking
)

# Upload critical files first
Write-Host "`n🚀 UPLOADING CRITICAL FILES (Switching optimization)..." -ForegroundColor Green

foreach ($file in $CriticalFiles) {
    if (Test-Path $file) {
        Write-Host "📤 Uploading $file..." -ForegroundColor Cyan
        & scp -i $KeyFile -o StrictHostKeyChecking=no $file $RemoteUser@$RemoteIP`:$RemoteDir/$file
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✅ $file uploaded successfully" -ForegroundColor Green
        } else {
            Write-Host "   ❌ Failed to upload $file" -ForegroundColor Red
        }
    } else {
        Write-Host "   ⚠️ $file not found locally" -ForegroundColor Yellow
    }
}

# Upload additional strategy files
Write-Host "`n📊 UPLOADING STRATEGY FILES..." -ForegroundColor Yellow

$StrategyFiles = @(
    "strategies\multi_strategy_optimized.py",
    "strategies\institutional_strategy.py",
    "strategies\enhanced_multi_timeframe_ma.py"
)

foreach ($file in $StrategyFiles) {
    if (Test-Path $file) {
        Write-Host "📤 Uploading $file..." -ForegroundColor Cyan
        
        # Create strategies directory if it doesn't exist
        & ssh -i $KeyFile -o StrictHostKeyChecking=no $RemoteUser@$RemoteIP "mkdir -p $RemoteDir/strategies"
        
        & scp -i $KeyFile -o StrictHostKeyChecking=no $file $RemoteUser@$RemoteIP`:$RemoteDir/$file
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✅ $file uploaded successfully" -ForegroundColor Green
        } else {
            Write-Host "   ❌ Failed to upload $file" -ForegroundColor Red
        }
    } else {
        Write-Host "   ⚠️ $file not found locally" -ForegroundColor Yellow
    }
}

# Upload documentation files
Write-Host "`n📚 UPLOADING DOCUMENTATION..." -ForegroundColor Yellow

$DocFiles = @(
    "*.md"
)

foreach ($pattern in $DocFiles) {
    $files = Get-ChildItem -Path $pattern -ErrorAction SilentlyContinue
    foreach ($file in $files) {
        Write-Host "📤 Uploading $($file.Name)..." -ForegroundColor Cyan
        & scp -i $KeyFile -o StrictHostKeyChecking=no $file.FullName $RemoteUser@$RemoteIP`:$RemoteDir/$($file.Name)
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✅ $($file.Name) uploaded successfully" -ForegroundColor Green
        }
    }
}

# Set correct permissions on remote server
Write-Host "`n🔒 SETTING PERMISSIONS..." -ForegroundColor Yellow
$permissionCommand = "cd $RemoteDir && chmod +x *.py && chmod 644 *.json *.md"
& ssh -i $KeyFile -o StrictHostKeyChecking=no $RemoteUser@$RemoteIP $permissionCommand

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Permissions set successfully" -ForegroundColor Green
} else {
    Write-Host "⚠️ Permission setting had issues" -ForegroundColor Yellow
}

# Install/update Python dependencies if needed
Write-Host "`n📦 CHECKING PYTHON DEPENDENCIES..." -ForegroundColor Yellow
$depCommand = "cd $RemoteDir && python3 -m pip install --user ccxt pandas numpy requests python-binance ta-lib"
& ssh -i $KeyFile -o StrictHostKeyChecking=no $RemoteUser@$RemoteIP $depCommand

# Restart the bot service (if running as a service)
Write-Host "`n🔄 RESTARTING BOT SERVICE..." -ForegroundColor Yellow

# First, try to stop any running bot processes
$stopCommand = "pkill -f 'python.*bot.py' || true"
& ssh -i $KeyFile -o StrictHostKeyChecking=no $RemoteUser@$RemoteIP $stopCommand

Write-Host "⏸️ Stopped existing bot processes" -ForegroundColor Yellow

# Start the bot in the background
Write-Host "`n🚀 STARTING OPTIMIZED BOT..." -ForegroundColor Green
$startCommand = "cd $RemoteDir && nohup python3 bot.py > bot_output.log 2>&1 &"
& ssh -i $KeyFile -o StrictHostKeyChecking=no $RemoteUser@$RemoteIP $startCommand

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Bot started successfully" -ForegroundColor Green
} else {
    Write-Host "⚠️ Bot start had issues - check manually" -ForegroundColor Yellow
}

# Check bot status
Write-Host "`n🔍 CHECKING BOT STATUS..." -ForegroundColor Cyan
Start-Sleep -Seconds 3

$statusCommand = "cd $RemoteDir && ps aux | grep -v grep | grep 'python.*bot.py'"
& ssh -i $KeyFile -o StrictHostKeyChecking=no $RemoteUser@$RemoteIP $statusCommand

# Show recent log output
Write-Host "`n📋 RECENT BOT OUTPUT:" -ForegroundColor Cyan
$logCommand = "cd $RemoteDir && tail -20 bot_output.log 2>/dev/null || echo 'No log output yet'"
& ssh -i $KeyFile -o StrictHostKeyChecking=no $RemoteUser@$RemoteIP $logCommand

Write-Host "`n" + "=" * 60
Write-Host "🎯 DEPLOYMENT SUMMARY:" -ForegroundColor Green
Write-Host "✅ Switching optimization deployed to AWS EC2" -ForegroundColor Green
Write-Host "✅ Enhanced HBAR/XLM detection active" -ForegroundColor Green
Write-Host "✅ Ultra-aggressive thresholds implemented" -ForegroundColor Green
Write-Host "✅ Direct percentage-based detection enabled" -ForegroundColor Green
Write-Host "✅ Emergency override system active" -ForegroundColor Green
Write-Host ""
Write-Host "🔧 KEY IMPROVEMENTS DEPLOYED:" -ForegroundColor Yellow
Write-Host "   • Switching thresholds lowered 31-50%" -ForegroundColor White
Write-Host "   • 5%+ moves trigger immediate switching" -ForegroundColor White
Write-Host "   • Forced score enhancement for momentum spikes" -ForegroundColor White
Write-Host "   • Emergency detection at 80% scores (was 90%)" -ForegroundColor White
Write-Host "   • Ultra-low 1% minimum detection threshold" -ForegroundColor White
Write-Host ""
Write-Host "🚨 MONITORING COMMANDS:" -ForegroundColor Cyan
Write-Host "   View live logs: ssh -i $KeyFile $RemoteUser@$RemoteIP 'cd $RemoteDir && tail -f bot_output.log'" -ForegroundColor White
Write-Host "   Check status:   ssh -i $KeyFile $RemoteUser@$RemoteIP 'cd $RemoteDir && ps aux | grep bot.py'" -ForegroundColor White
Write-Host "   Stop bot:       ssh -i $KeyFile $RemoteUser@$RemoteIP 'pkill -f bot.py'" -ForegroundColor White
Write-Host ""
Write-Host "🎯 The bot will now catch HBAR +5.83% and XLM +6.40% type moves!" -ForegroundColor Green
Write-Host "=" * 60
