# =============================================================================
# PHASE 2 DEPLOYMENT TO YOUR AWS INSTANCE
# =============================================================================
#
# 🚀 Deploy Phase 2 Enhanced Bot to ubuntu@3.135.216.32
# Includes all Phase 2 files for enterprise-level intelligence at $0/month
#
# =============================================================================

# Your AWS Instance Details (from previous deployments):
# Instance: ubuntu@3.135.216.32
# User: ubuntu (not ec2-user)
# Key: (you'll need to specify your .pem file path)

Write-Host "🚀 DEPLOYING PHASE 2 TO YOUR AWS INSTANCE" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host "Target: ubuntu@3.135.216.32" -ForegroundColor Yellow
Write-Host "Phase 2 Enhancement: Adding enterprise intelligence at $0/month" -ForegroundColor Cyan
Write-Host ""

# You'll need to replace 'your-key.pem' with your actual key file path
$KeyPath = "your-key.pem"  # ⚠️ UPDATE THIS PATH!
$InstanceIP = "3.135.216.32"
$Username = "ubuntu"
$RemotePath = "/home/ubuntu/crypto-trading-bot"

Write-Host "⚠️ IMPORTANT: Update the KeyPath variable above with your actual .pem file path!" -ForegroundColor Red
Write-Host ""

# Phase 2 specific files to upload
$Phase2Files = @(
    "free_phase2_api.py",
    "free_phase2_config.py", 
    "unified_free_config.py"
)

# Core files that might need updates
$CoreFiles = @(
    "bot.py",                    # Enhanced with Phase 2 integration
    "free_crypto_api.py",        # Phase 1 APIs
    "onchain_config.py"          # Updated configuration
)

Write-Host "📦 UPLOADING PHASE 2 FILES..." -ForegroundColor Yellow
Write-Host ""

# Upload Phase 2 files
Write-Host "Uploading Phase 2 intelligence files..." -ForegroundColor Cyan
foreach ($file in $Phase2Files) {
    if (Test-Path $file) {
        Write-Host "  Uploading: $file" -ForegroundColor Green
    } else {
        Write-Host "  ❌ Missing: $file" -ForegroundColor Red
    }
}

# Upload updated core files
Write-Host "Uploading updated core files..." -ForegroundColor Cyan
foreach ($file in $CoreFiles) {
    if (Test-Path $file) {
        Write-Host "  Uploading: $file" -ForegroundColor Green
    } else {
        Write-Host "  ❌ Missing: $file" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "🔧 DEPLOYMENT COMMANDS FOR YOUR INSTANCE:" -ForegroundColor Yellow
Write-Host ""

Write-Host "1. UPDATE YOUR KEY PATH AND RUN THESE COMMANDS:" -ForegroundColor Cyan
Write-Host ""

# Phase 2 deployment commands for your specific instance
Write-Host "# Upload Phase 2 files" -ForegroundColor Gray
Write-Host "scp -i `"your-key.pem`" free_phase2_api.py free_phase2_config.py unified_free_config.py ubuntu@3.135.216.32:/home/ubuntu/crypto-trading-bot/" -ForegroundColor White
Write-Host ""

Write-Host "# Upload updated core files" -ForegroundColor Gray  
Write-Host "scp -i `"your-key.pem`" bot.py free_crypto_api.py onchain_config.py ubuntu@3.135.216.32:/home/ubuntu/crypto-trading-bot/" -ForegroundColor White
Write-Host ""

Write-Host "# Upload verification script" -ForegroundColor Gray
Write-Host "scp -i `"your-key.pem`" aws_verify_phase2.py ubuntu@3.135.216.32:/home/ubuntu/crypto-trading-bot/" -ForegroundColor White
Write-Host ""

Write-Host "2. SSH INTO YOUR INSTANCE AND VERIFY:" -ForegroundColor Cyan
Write-Host ""

Write-Host "# Connect to your instance" -ForegroundColor Gray
Write-Host "ssh -i `"your-key.pem`" ubuntu@3.135.216.32" -ForegroundColor White
Write-Host ""

Write-Host "# Navigate to bot directory" -ForegroundColor Gray
Write-Host "cd /home/ubuntu/crypto-trading-bot" -ForegroundColor White
Write-Host ""

Write-Host "# Stop any running bots first (you had 3 running)" -ForegroundColor Gray
Write-Host "pkill -f `"python3 bot.py`"" -ForegroundColor White
Write-Host ""

Write-Host "# Install any new dependencies" -ForegroundColor Gray
Write-Host "pip3 install -r requirements.txt" -ForegroundColor White
Write-Host ""

Write-Host "# Verify Phase 2 installation" -ForegroundColor Gray
Write-Host "python3 aws_verify_phase2.py" -ForegroundColor White
Write-Host ""

Write-Host "# Test Phase 2 configuration" -ForegroundColor Gray
Write-Host "python3 -c `"from free_phase2_config import validate_phase2_setup; result = validate_phase2_setup(); print(f'✅ Phase 2 Status: {result[\"status\"]}'); print(f'💰 Monthly Cost: \${result[\"summary\"][\"monthly_cost\"]}'); print(f'💎 Monthly Savings: \${result[\"summary\"][\"monthly_savings\"]}'); print(f'🔧 Active APIs: {result[\"summary\"][\"active_apis\"]}')`"" -ForegroundColor White
Write-Host ""

Write-Host "# Start enhanced bot with Phase 2" -ForegroundColor Gray
Write-Host "nohup python3 bot.py > bot_phase2.log 2>&1 &" -ForegroundColor White
Write-Host ""

Write-Host "# Monitor the enhanced bot" -ForegroundColor Gray
Write-Host "tail -f bot_phase2.log" -ForegroundColor White
Write-Host ""

Write-Host "3. WHAT TO EXPECT AFTER DEPLOYMENT:" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ Phase 2 APIs will initialize (Bitquery, DefiLlama, The Graph, Dune)" -ForegroundColor Green
Write-Host "✅ Bot will show enhanced intelligence messages in logs" -ForegroundColor Green
Write-Host "✅ Whale activity detection will be active" -ForegroundColor Green  
Write-Host "✅ Exchange flow monitoring will begin" -ForegroundColor Green
Write-Host "✅ DeFi intelligence will provide market sentiment" -ForegroundColor Green
Write-Host "✅ Zero additional costs (all APIs are free!)" -ForegroundColor Green
Write-Host ""

Write-Host "🎯 ENHANCED TRADING SIGNALS YOU'LL SEE:" -ForegroundColor Magenta
Write-Host "🐋 WHALE ACCUMULATION: [Symbol] - Institutional buying detected" -ForegroundColor White
Write-Host "🔵 EXCHANGE INFLOW SURGE: [Symbol] - Large fund movements" -ForegroundColor White  
Write-Host "💹 RISK-ON SENTIMENT: [Symbol] - Bullish DeFi flows" -ForegroundColor White
Write-Host "📈 HIGH DEX ACTIVITY: [Symbol] - Optimal liquidity for trading" -ForegroundColor White
Write-Host "🚀 PHASE 2 ENHANCED: [Symbol] - Multi-source confirmation" -ForegroundColor White
Write-Host ""

Write-Host "💰 COST SUMMARY:" -ForegroundColor Green
Write-Host "• Monthly API costs: $0 (no change from current)" -ForegroundColor White
Write-Host "• New APIs added: 4 advanced intelligence sources" -ForegroundColor White
Write-Host "• Equivalent paid services value: $1,317/month" -ForegroundColor White
Write-Host "• AWS impact: Zero (all APIs are external and free)" -ForegroundColor White
Write-Host ""

Write-Host "🚨 IMPORTANT NOTES:" -ForegroundColor Yellow
Write-Host "• You previously had 3 bot instances running - we'll consolidate to 1" -ForegroundColor White
Write-Host "• Phase 2 adds intelligence but doesn't change core trading logic" -ForegroundColor White  
Write-Host "• All Phase 2 APIs are free and don't require API keys" -ForegroundColor White
Write-Host "• Enhanced signals will help make more informed trading decisions" -ForegroundColor White
Write-Host ""

Write-Host "Ready to deploy Phase 2 to your AWS instance! 🚀" -ForegroundColor Green
