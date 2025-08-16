#!/usr/bin/env powershell

Write-Host "🧹 GITHUB CLEANUP SCRIPT STARTING" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green

# Set working directory
Set-Location "c:\Users\miste\Documents\crypto-trading-bot\crypto-trading-bot"
Write-Host "📁 Working directory: $(Get-Location)"

# Count files before cleanup
$filesBefore = (Get-ChildItem).Count
Write-Host "📊 Files before cleanup: $filesBefore"
Write-Host ""

# Delete backup files
Write-Host "🗑️ STEP 1: Deleting backup files..." -ForegroundColor Yellow
$backupFiles = @(
    "bot_backup_broken.py",
    "bot_backup_20250812_183015.py", 
    "emergency_spike_detector_backup_20250812_183015.py",
    "multi_crypto_monitor_backup_20250812_183015.py",
    "config_backup.json",
    "bot_state_ec2_backup.json",
    "enhanced_config_ec2_backup.json"
)

$deletedCount = 0
foreach($file in $backupFiles) {
    if(Test-Path $file) {
        Remove-Item $file -Force
        Write-Host "✅ Deleted: $file" -ForegroundColor Green
        $deletedCount++
    }
}

# Delete enhanced config backups (pattern)
Get-ChildItem "enhanced_config.json.backup*" | ForEach-Object {
    Remove-Item $_.FullName -Force
    Write-Host "✅ Deleted: $($_.Name)" -ForegroundColor Green
    $deletedCount++
}

Write-Host "📊 Backup files deleted: $deletedCount" -ForegroundColor Cyan
Write-Host ""

# Delete test files
Write-Host "🧪 STEP 2: Deleting test files..." -ForegroundColor Yellow
$testFiles = @(
    "test_*.py"
)

$testDeletedCount = 0
Get-ChildItem "test_*.py" | ForEach-Object {
    Remove-Item $_.FullName -Force
    Write-Host "✅ Deleted: $($_.Name)" -ForegroundColor Green
    $testDeletedCount++
}

Write-Host "📊 Test files deleted: $testDeletedCount" -ForegroundColor Cyan
Write-Host ""

# Delete debug files
Write-Host "🐛 STEP 3: Deleting debug files..." -ForegroundColor Yellow
$debugDeletedCount = 0
Get-ChildItem "debug_*.py" | ForEach-Object {
    Remove-Item $_.FullName -Force
    Write-Host "✅ Deleted: $($_.Name)" -ForegroundColor Green
    $debugDeletedCount++
}

Write-Host "📊 Debug files deleted: $debugDeletedCount" -ForegroundColor Cyan
Write-Host ""

# Delete check files
Write-Host "🔍 STEP 4: Deleting diagnostic files..." -ForegroundColor Yellow
$checkDeletedCount = 0
Get-ChildItem "check_*.py" | ForEach-Object {
    Remove-Item $_.FullName -Force
    Write-Host "✅ Deleted: $($_.Name)" -ForegroundColor Green
    $checkDeletedCount++
}

Write-Host "📊 Diagnostic files deleted: $checkDeletedCount" -ForegroundColor Cyan
Write-Host ""

# Delete log files
Write-Host "📋 STEP 5: Deleting log files..." -ForegroundColor Yellow
$logFiles = @(
    "bot_log.txt",
    "daily_sync.log", 
    "daily_sync_task.log"
)

$logDeletedCount = 0
foreach($file in $logFiles) {
    if(Test-Path $file) {
        Remove-Item $file -Force
        Write-Host "✅ Deleted: $file" -ForegroundColor Green
        $logDeletedCount++
    }
}

Get-ChildItem "*.log" | ForEach-Object {
    Remove-Item $_.FullName -Force
    Write-Host "✅ Deleted: $($_.Name)" -ForegroundColor Green
    $logDeletedCount++
}

Write-Host "📊 Log files deleted: $logDeletedCount" -ForegroundColor Cyan
Write-Host ""

# Final count
$filesAfter = (Get-ChildItem).Count
$totalDeleted = $filesBefore - $filesAfter

Write-Host "🎉 CLEANUP COMPLETE!" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green
Write-Host "📊 Files before: $filesBefore" -ForegroundColor White
Write-Host "📊 Files after: $filesAfter" -ForegroundColor White
Write-Host "🗑️ Total deleted: $totalDeleted" -ForegroundColor Red
Write-Host "📈 Space saved: $([math]::Round(($totalDeleted / $filesBefore) * 100, 1))%" -ForegroundColor Green
Write-Host ""
Write-Host "✅ Repository is now cleaner and GitHub-ready!" -ForegroundColor Green
