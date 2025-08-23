# PowerShell script to check recent LINK activity
$logFile = "c:\Users\miste\Documents\crypto-trading-bot\crypto-trading-bot\bot_log.txt"

Write-Host "🔍 CHECKING RECENT LINK ACTIVITY" -ForegroundColor Cyan
Write-Host "=" * 50

# Get last 200 lines and filter for LINK-related entries
$recentLines = Get-Content $logFile -Tail 200
$linkEntries = $recentLines | Select-String -Pattern "LINK" | Select-Object -Last 20

Write-Host "📊 RECENT LINK LOG ENTRIES:" -ForegroundColor Yellow
if ($linkEntries.Count -eq 0) {
    Write-Host "   📭 No recent LINK entries found in last 200 log lines" -ForegroundColor Gray
} else {
    foreach ($entry in $linkEntries) {
        Write-Host "   $entry" -ForegroundColor White
    }
}

Write-Host ""
Write-Host "🔍 CHECKING FOR SELL ORDERS:" -ForegroundColor Yellow
$sellEntries = $recentLines | Select-String -Pattern "SELL" | Select-Object -Last 10

if ($sellEntries.Count -eq 0) {
    Write-Host "   📭 No recent SELL entries found" -ForegroundColor Gray
} else {
    foreach ($entry in $sellEntries) {
        Write-Host "   $entry" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "🔍 CHECKING LAST 20 LOG ENTRIES:" -ForegroundColor Yellow
$lastEntries = Get-Content $logFile -Tail 20
foreach ($entry in $lastEntries) {
    Write-Host "   $entry" -ForegroundColor Gray
}
