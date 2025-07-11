# PowerShell Script for Windows Task Scheduler
# This script runs the daily sync and handles logging properly

# Set working directory
$WorkingDir = "c:\Users\miste\Documents\crypto-trading-bot\crypto-trading-bot"
Set-Location $WorkingDir

# Create log entry
$LogFile = "daily_sync_task.log"
$Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

# Function to log messages
function Write-Log {
    param([string]$Message)
    $LogEntry = "$Timestamp - $Message"
    Add-Content -Path $LogFile -Value $LogEntry
    Write-Host $LogEntry
}

Write-Log "Starting Crypto Trading Bot Daily Sync"

try {
    # Run the daily sync
    $Result = python windows_daily_sync.py --test
    
    if ($LASTEXITCODE -eq 0) {
        Write-Log "Daily sync completed successfully"
    } else {
        Write-Log "Daily sync failed with exit code: $LASTEXITCODE"
    }
    
    Write-Log "Check daily_sync.log for detailed results"
    
} catch {
    Write-Log "Error running daily sync: $($_.Exception.Message)"
}

Write-Log "Daily sync task completed"
