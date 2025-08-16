# Fix AWS API Keys - Clean Version
# This script fixes the API key issue on AWS

Write-Host "🔧 AWS API Key Fix" -ForegroundColor Green
Write-Host "==================" -ForegroundColor Cyan

# AWS server details
$AWS_USER = "ubuntu"
$AWS_HOST = "3.135.216.32"

# Working API keys
$API_KEY = "bN4mjzb1pIfmRZCit0zjqxACIv1JszpbPDi3Zlhbh1961qsFgvwio6UWzIyUwQND"
$API_SECRET = "Rq5p1qTSwq4qmb8xgb7kdKHZGlPVvIaiakF5jiu43dknp0nGg17jDLtuIwZ1cWza"

Write-Host "🔑 Testing SSH connection to AWS..." -ForegroundColor Yellow

# Test SSH connection
$testResult = ssh "$AWS_USER@$AWS_HOST" "echo 'test'" 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ SSH connection successful!" -ForegroundColor Green
    
    Write-Host "📝 Updating config.py on AWS..." -ForegroundColor Cyan
    
    # Create new config content and send to AWS
    @"
# config.py
# Place your Binance API credentials here. Do NOT commit this file to version control!

BINANCE_API_KEY = "$API_KEY"
BINANCE_API_SECRET = "$API_SECRET"

"@ | ssh "$AWS_USER@$AWS_HOST" "cd ~/crypto-trading-bot && cp config.py config.py.backup 2>/dev/null; cat > config.py"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Config updated successfully!" -ForegroundColor Green
        
        Write-Host "🧪 Testing API connection on AWS..." -ForegroundColor Cyan
        ssh "$AWS_USER@$AWS_HOST" "cd ~/crypto-trading-bot && python3 connection_test.py"
        
        Write-Host "🔄 Stopping old bot processes..." -ForegroundColor Cyan
        ssh "$AWS_USER@$AWS_HOST" "pkill -f python.*bot.py; exit 0"
        
        Write-Host "✅ AWS API key fix completed!" -ForegroundColor Green
        
    } else {
        Write-Host "❌ Failed to update config" -ForegroundColor Red
    }
    
} else {
    Write-Host "❌ SSH connection failed" -ForegroundColor Red
    Write-Host ""
    Write-Host "🔧 MANUAL FIX REQUIRED:" -ForegroundColor Yellow
    Write-Host "1. SSH into AWS: ssh -i your-key.pem ubuntu@3.135.216.32" -ForegroundColor White
    Write-Host "2. Edit config: cd ~/crypto-trading-bot && nano config.py" -ForegroundColor White
    Write-Host "3. Update API keys with:" -ForegroundColor White
    Write-Host "   BINANCE_API_KEY = `"$API_KEY`"" -ForegroundColor Cyan
    Write-Host "   BINANCE_API_SECRET = `"$API_SECRET`"" -ForegroundColor Cyan
    Write-Host "4. Save (Ctrl+X, Y, Enter)" -ForegroundColor White
    Write-Host "5. Test: python3 connection_test.py" -ForegroundColor White
    Write-Host "6. Stop old processes: pkill -f python.*bot.py" -ForegroundColor White
}
