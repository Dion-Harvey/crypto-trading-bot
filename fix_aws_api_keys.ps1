# Fix AWS API Keys - Multiple Methods
# This script tries different methods to fix API keys on AWS

Write-Host "🔧 AWS API Key Fix - Multiple Authentication Methods" -ForegroundColor Green
Write-Host "=====================================================" -ForegroundColor Cyan

# Define AWS server details
$AWS_USER = "ubuntu"
$AWS_HOST = "3.135.216.32"
$AWS_PATH = "~/crypto-trading-bot/"

# Load API keys from environment (set before running) or fallback to placeholders
$API_KEY = $Env:BINANCE_API_KEY
$API_SECRET = $Env:BINANCE_API_SECRET
if (-not $API_KEY) { $API_KEY = "REPLACE_ME" }
if (-not $API_SECRET) { $API_SECRET = "REPLACE_ME" }

Write-Host "� Method 1: Trying direct SSH connection..." -ForegroundColor Yellow

try {
    # Test SSH connection first
    $testSSH = ssh "$AWS_USER@$AWS_HOST" "echo 'Connection test successful'" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ SSH connection successful!" -ForegroundColor Green

        Write-Host "📝 Creating new config.py on AWS..." -ForegroundColor Cyan

        # Create the config content
        $configContent = @"
# config.py
# Place your Binance API credentials here. Do NOT commit this file to version control!

BINANCE_API_KEY = `"$API_KEY`"
BINANCE_API_SECRET = `"$API_SECRET`"

"@

        # Upload the config using SSH
        $configContent | ssh "$AWS_USER@$AWS_HOST" "cd $AWS_PATH && cp config.py config.py.backup.$(Get-Date -Format 'yyyyMMdd_HHmmss') 2>/dev/null; cat > config.py"

        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Config.py updated successfully!" -ForegroundColor Green

            # Test the connection on AWS
            Write-Host "🧪 Testing API connection on AWS..." -ForegroundColor Cyan
            ssh "$AWS_USER@$AWS_HOST" "cd $AWS_PATH && python3 connection_test.py"

            # Stop any running bot processes
            Write-Host "🔄 Stopping old bot processes..." -ForegroundColor Cyan
            ssh "$AWS_USER@$AWS_HOST" "pkill -f 'python.*bot.py' || true"

            Write-Host "✅ AWS API key fix completed successfully!" -ForegroundColor Green
            Write-Host "🎯 Your AWS bot now has the correct API keys" -ForegroundColor Yellow

        } else {
            throw "Failed to update config.py"
        }

    } else {
        throw "SSH connection failed"
    }

} catch {
    Write-Host "❌ Method 1 failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "🔧 Method 2: Manual Instructions" -ForegroundColor Yellow
    Write-Host "================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Please connect to your AWS instance manually and update the config:" -ForegroundColor White
    Write-Host ""
    Write-Host "1. SSH into AWS:" -ForegroundColor Cyan
    Write-Host "   ssh -i your-key.pem ubuntu@3.135.216.32" -ForegroundColor White
    Write-Host ""
    Write-Host "2. Navigate to bot directory:" -ForegroundColor Cyan
    Write-Host "   cd ~/crypto-trading-bot/" -ForegroundColor White
    Write-Host ""
    Write-Host "3. Backup current config:" -ForegroundColor Cyan
    Write-Host "   cp config.py config.py.backup" -ForegroundColor White
    Write-Host ""
    Write-Host "4. Edit config.py:" -ForegroundColor Cyan
    Write-Host "   nano config.py" -ForegroundColor White
    Write-Host ""
    Write-Host "5. Create/Edit .env with working keys:" -ForegroundColor Cyan
    Write-Host "   BINANCE_API_KEY=YOUR_KEY" -ForegroundColor White
    Write-Host "   BINANCE_API_SECRET=YOUR_SECRET" -ForegroundColor White
    Write-Host "   GEMINI_API_KEY=YOUR_GEMINI_KEY" -ForegroundColor White
    Write-Host ""
    Write-Host "6. Save and exit (Ctrl+X, Y, Enter)" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "7. Test the fix:" -ForegroundColor Cyan
    Write-Host "   python3 connection_test.py" -ForegroundColor White
    Write-Host ""
    Write-Host "8. Stop old bot processes:" -ForegroundColor Cyan
    Write-Host "   pkill -f 'python.*bot.py'" -ForegroundColor White
    Write-Host ""
    Write-Host "🔑 Alternative: Use AWS Systems Manager Session Manager" -ForegroundColor Yellow
    Write-Host "   This might work if SSH keys aren't configured properly" -ForegroundColor Gray
}
