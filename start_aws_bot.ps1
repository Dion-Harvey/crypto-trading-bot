# AWS Bot Management Script
# Starts the crypto trading bot on AWS with proper error handling

Write-Host "🚀 Starting Crypto Trading Bot on AWS..." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

$sshKey = "C:\Users\miste\Documents\cryptobot-key.pem"
$awsHost = "ubuntu@3.135.216.32"

try {
    Write-Host "📡 Connecting to AWS instance..." -ForegroundColor Yellow
    
    # Check if instance is reachable
    $pingResult = Test-Connection -ComputerName "3.135.216.32" -Count 2 -Quiet
    if (-not $pingResult) {
        Write-Host "❌ AWS instance not reachable" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "✅ AWS instance is reachable" -ForegroundColor Green
    
    # Start the bot
    Write-Host "🤖 Starting bot process..." -ForegroundColor Yellow
    $startCommand = "cd crypto-trading-bot && nohup python3 bot.py > bot_log.txt 2>&1 &"
    
    # Use Start-Process for better control
    $sshArgs = @("-i", $sshKey, $awsHost, $startCommand)
    Start-Process -FilePath "ssh" -ArgumentList $sshArgs -Wait -WindowStyle Hidden
    
    Write-Host "✅ Bot start command executed" -ForegroundColor Green
    
    # Wait a moment for the bot to initialize
    Start-Sleep -Seconds 5
    
    # Check if bot is running
    Write-Host "🔍 Checking bot status..." -ForegroundColor Yellow
    $checkArgs = @("-i", $sshKey, $awsHost, "ps aux | grep bot.py | grep -v grep")
    $checkProcess = Start-Process -FilePath "ssh" -ArgumentList $checkArgs -Wait -PassThru -WindowStyle Hidden
    
    if ($checkProcess.ExitCode -eq 0) {
        Write-Host "✅ Bot is running on AWS!" -ForegroundColor Green
        
        # Show recent log entries
        Write-Host "📝 Recent bot activity:" -ForegroundColor Cyan
        $logArgs = @("-i", $sshKey, $awsHost, "tail -5 crypto-trading-bot/bot_log.txt")
        Start-Process -FilePath "ssh" -ArgumentList $logArgs -Wait -WindowStyle Normal
    } else {
        Write-Host "⚠️ Bot status unclear, check manually" -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "🎯 Bot deployment complete!" -ForegroundColor Green
Write-Host "Use check_aws_bot_status.bat to monitor the bot" -ForegroundColor Cyan
