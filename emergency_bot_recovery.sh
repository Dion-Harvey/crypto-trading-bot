#!/bin/bash
"""
🛡️ EMERGENCY BOT RECOVERY SCRIPT
=================================

Quick recovery script for when the bot crashes or stops responding.
This script can be run manually or called by monitoring systems.

Usage:
    ./emergency_bot_recovery.sh [reason]

Features:
- Immediate bot restart with state preservation
- Backup of current state before restart
- Health check after restart
- Logging of all recovery actions
"""

set -e

# Configuration
BOT_DIR="/home/ubuntu/crypto-trading-bot-deploy"
RECOVERY_LOG="$BOT_DIR/recovery.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
REASON="${1:-Manual recovery}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_entry() {
    echo "[$TIMESTAMP] $1" >> "$RECOVERY_LOG"
    echo -e "${GREEN}[RECOVERY]${NC} $1"
}

log_warning() {
    echo "[$TIMESTAMP] WARNING: $1" >> "$RECOVERY_LOG"
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo "[$TIMESTAMP] ERROR: $1" >> "$RECOVERY_LOG"
    echo -e "${RED}[ERROR]${NC} $1"
}

cd "$BOT_DIR"

echo -e "${BLUE}🛡️ CRYPTO BOT EMERGENCY RECOVERY${NC}"
echo -e "${BLUE}=================================${NC}"
echo ""

log_entry "Emergency recovery initiated - Reason: $REASON"

# Step 1: Check current bot status
echo -e "${YELLOW}📊 Checking current bot status...${NC}"
BOT_PID=$(pgrep -f "bot.py" || echo "")

if [ -n "$BOT_PID" ]; then
    log_entry "Found running bot process: PID $BOT_PID"
    
    # Check if process is responsive
    if kill -0 "$BOT_PID" 2>/dev/null; then
        log_entry "Bot process is responsive"
        PROCESS_RESPONSIVE=true
    else
        log_warning "Bot process exists but not responsive"
        PROCESS_RESPONSIVE=false
    fi
else
    log_warning "No bot process found"
    PROCESS_RESPONSIVE=false
fi

# Step 2: Backup current state
echo -e "${YELLOW}💾 Backing up current state...${NC}"
BACKUP_TIMESTAMP=$(date '+%Y%m%d_%H%M%S')

if [ -f "bot_state.json" ]; then
    cp "bot_state.json" "bot_state.json.recovery_backup_$BACKUP_TIMESTAMP"
    log_entry "Bot state backed up to bot_state.json.recovery_backup_$BACKUP_TIMESTAMP"
fi

if [ -f "enhanced_config.json" ]; then
    cp "enhanced_config.json" "enhanced_config.json.recovery_backup_$BACKUP_TIMESTAMP"
    log_entry "Config backed up to enhanced_config.json.recovery_backup_$BACKUP_TIMESTAMP"
fi

if [ -f "bot_log.txt" ]; then
    cp "bot_log.txt" "bot_log.txt.recovery_backup_$BACKUP_TIMESTAMP"
    log_entry "Logs backed up to bot_log.txt.recovery_backup_$BACKUP_TIMESTAMP"
fi

# Step 3: Terminate existing bot processes
if [ -n "$BOT_PID" ]; then
    echo -e "${YELLOW}🛑 Terminating existing bot process...${NC}"
    log_entry "Attempting graceful termination of PID $BOT_PID"
    
    # Try graceful termination first
    if kill -TERM "$BOT_PID" 2>/dev/null; then
        log_entry "Sent SIGTERM to bot process"
        
        # Wait up to 15 seconds for graceful shutdown
        for i in {1..15}; do
            if ! kill -0 "$BOT_PID" 2>/dev/null; then
                log_entry "Bot process terminated gracefully after ${i}s"
                break
            fi
            sleep 1
        done
        
        # Force kill if still running
        if kill -0 "$BOT_PID" 2>/dev/null; then
            log_warning "Graceful termination failed, using force kill"
            kill -KILL "$BOT_PID" 2>/dev/null || true
            sleep 2
        fi
    else
        log_warning "Could not send termination signal, process may be zombie"
    fi
fi

# Kill any remaining python processes related to the bot
echo -e "${YELLOW}🧹 Cleaning up any remaining bot processes...${NC}"
pkill -f "bot.py" 2>/dev/null || true
sleep 3

# Step 4: Check environment
echo -e "${YELLOW}🔍 Checking environment...${NC}"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    log_error "Virtual environment not found!"
    exit 1
fi

# Check if bot.py exists
if [ ! -f "bot.py" ]; then
    log_error "bot.py not found!"
    exit 1
fi

# Check if config exists
if [ ! -f "enhanced_config.json" ]; then
    log_error "enhanced_config.json not found!"
    exit 1
fi

# Test virtual environment
if ! .venv/bin/python -c "import sys; print(f'Python: {sys.version}')" > /dev/null 2>&1; then
    log_error "Virtual environment is corrupted!"
    exit 1
fi

log_entry "Environment checks passed"

# Step 5: Start the bot
echo -e "${YELLOW}🚀 Starting the bot...${NC}"
log_entry "Attempting to start bot process"

cd "$BOT_DIR"

# Start bot in background with proper logging
nohup .venv/bin/python bot.py > bot_recovery.log 2>&1 &
NEW_BOT_PID=$!

log_entry "Bot started with PID $NEW_BOT_PID"

# Step 6: Verify startup
echo -e "${YELLOW}✅ Verifying bot startup...${NC}"
sleep 10  # Give bot time to initialize

# Check if process is still running
if kill -0 "$NEW_BOT_PID" 2>/dev/null; then
    log_entry "Bot process is running successfully"
    
    # Check for recent log activity
    if [ -f "bot_recovery.log" ] && [ -s "bot_recovery.log" ]; then
        log_entry "Bot is generating logs"
        
        # Show recent log output
        echo -e "${GREEN}📈 Recent bot output:${NC}"
        tail -5 bot_recovery.log | sed 's/^/   /'
        
    else
        log_warning "Bot started but no logs detected yet"
    fi
    
    # Update the main log file
    if [ -f "bot_recovery.log" ]; then
        cat bot_recovery.log >> bot_log.txt
    fi
    
else
    log_error "Bot process failed to start!"
    
    # Show error logs if available
    if [ -f "bot_recovery.log" ]; then
        echo -e "${RED}❌ Error output:${NC}"
        cat bot_recovery.log | sed 's/^/   /'
    fi
    
    exit 1
fi

# Step 7: Final health check
echo -e "${YELLOW}🏥 Running health check...${NC}"

# Test basic connectivity
if timeout 10 .venv/bin/python -c "
import sys
sys.path.append('.')
try:
    from connection_test import test_connection
    result = test_connection()
    if result:
        print('✅ API connection test passed')
    else:
        print('❌ API connection test failed')
        sys.exit(1)
except Exception as e:
    print(f'❌ Connection test error: {e}')
    sys.exit(1)
" 2>/dev/null; then
    log_entry "API connectivity test passed"
else
    log_warning "API connectivity test failed or timed out"
fi

# Check recent trading activity
RECENT_ACTIVITY=false
if [ -f "bot_log.txt" ]; then
    # Look for recent trading signals or activity
    if tail -20 bot_log.txt | grep -q -E "(BUY|SELL|Signal|MULTI-TIMEFRAME)" 2>/dev/null; then
        log_entry "Recent trading activity detected"
        RECENT_ACTIVITY=true
    fi
fi

echo ""
echo -e "${GREEN}🎉 RECOVERY COMPLETE!${NC}"
echo -e "${GREEN}===================${NC}"
echo ""
echo -e "${BLUE}📊 Recovery Summary:${NC}"
echo -e "   Reason: $REASON"
echo -e "   New PID: $NEW_BOT_PID"
echo -e "   Backup timestamp: $BACKUP_TIMESTAMP"
echo -e "   API connectivity: $([ "$?" -eq 0 ] && echo "✅ OK" || echo "⚠️ Check needed")"
echo -e "   Recent activity: $([ "$RECENT_ACTIVITY" = true ] && echo "✅ Detected" || echo "⚠️ None yet")"
echo ""

log_entry "Recovery completed successfully"

# Create status file
cat > recovery_status.txt << EOF
Last Recovery: $TIMESTAMP
Reason: $REASON
New PID: $NEW_BOT_PID
Backup Files:
  - bot_state.json.recovery_backup_$BACKUP_TIMESTAMP
  - enhanced_config.json.recovery_backup_$BACKUP_TIMESTAMP
  - bot_log.txt.recovery_backup_$BACKUP_TIMESTAMP

Next Steps:
1. Monitor bot activity for 15-30 minutes
2. Check bot_log.txt for normal operation
3. Verify trading signals are being generated
4. Check exchange connectivity and balance

Commands:
  tail -f bot_log.txt          # Monitor real-time logs
  ps aux | grep bot.py         # Check process status
  ./monitor_bot_health.sh      # Run comprehensive health check
EOF

echo -e "${BLUE}📋 Status file created: recovery_status.txt${NC}"
echo -e "${BLUE}📈 Monitor bot: tail -f bot_log.txt${NC}"
echo ""

exit 0
