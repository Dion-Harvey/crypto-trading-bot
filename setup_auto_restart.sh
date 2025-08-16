#!/bin/bash
"""
🚀 CRYPTO BOT AUTO-RESTART SETUP
================================

This script sets up automatic restart capabilities for the crypto trading bot on AWS EC2.
It configures systemd services, installs the watchdog, and ensures 24/7 operation.

Features:
- Systemd service for bot auto-restart on crash/reboot
- Watchdog service for health monitoring and recovery
- Proper logging and state preservation
- Resource limits and security hardening
"""

set -e  # Exit on any error

echo "🚀 Setting up Crypto Bot Auto-Restart System..."
echo "=================================================="

# Configuration
BOT_DIR="/home/ubuntu/crypto-trading-bot-deploy"
WATCHDOG_SERVICE="crypto-bot-watchdog.service"
BOT_SERVICE="crypto-trading-bot.service"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as ubuntu user
if [ "$USER" != "ubuntu" ]; then
    log_error "This script must be run as the ubuntu user"
    exit 1
fi

# Check if in correct directory
if [ ! -f "$BOT_DIR/bot.py" ]; then
    log_error "Bot directory not found or bot.py missing: $BOT_DIR"
    exit 1
fi

cd "$BOT_DIR"

log_info "Installing system dependencies..."

# Install psutil for watchdog
if ! python3 -c "import psutil" 2>/dev/null; then
    log_info "Installing psutil..."
    .venv/bin/pip install psutil
else
    log_info "psutil already installed"
fi

# Check if systemd is available
if ! command -v systemctl >/dev/null 2>&1; then
    log_error "systemd not available - cannot set up auto-restart"
    exit 1
fi

log_info "Setting up systemd services..."

# Create systemd service for direct bot management
log_info "Creating crypto-trading-bot.service..."
sudo tee /etc/systemd/system/crypto-trading-bot.service > /dev/null << EOF
[Unit]
Description=Crypto Trading Bot
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=$BOT_DIR
Environment=PATH=$BOT_DIR/.venv/bin:/usr/local/bin:/usr/bin:/bin
ExecStart=$BOT_DIR/.venv/bin/python $BOT_DIR/bot.py
Restart=always
RestartSec=60
StandardOutput=append:$BOT_DIR/systemd_bot.log
StandardError=append:$BOT_DIR/systemd_bot.log

# Resource limits
MemoryLimit=2G
CPUQuota=80%

# Restart policy
StartLimitInterval=300
StartLimitBurst=5

# Security settings
NoNewPrivileges=yes
ProtectSystem=strict
ProtectHome=yes
ReadWritePaths=$BOT_DIR
PrivateTmp=yes

[Install]
WantedBy=multi-user.target
EOF

# Create systemd service for watchdog
log_info "Creating crypto-bot-watchdog.service..."
sudo tee /etc/systemd/system/crypto-bot-watchdog.service > /dev/null << EOF
[Unit]
Description=Crypto Trading Bot Watchdog
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=$BOT_DIR
Environment=PATH=$BOT_DIR/.venv/bin:/usr/local/bin:/usr/bin:/bin
ExecStart=$BOT_DIR/.venv/bin/python $BOT_DIR/crypto-bot-watchdog.py
Restart=always
RestartSec=30
StandardOutput=append:$BOT_DIR/systemd_watchdog.log
StandardError=append:$BOT_DIR/systemd_watchdog.log

# Resource limits
MemoryLimit=1G
CPUQuota=50%

# Security settings
NoNewPrivileges=yes
ProtectSystem=strict
ProtectHome=yes
ReadWritePaths=$BOT_DIR
PrivateTmp=yes

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
log_info "Reloading systemd daemon..."
sudo systemctl daemon-reload

# Enable services to start on boot
log_info "Enabling services for auto-start on boot..."
sudo systemctl enable crypto-trading-bot.service
sudo systemctl enable crypto-bot-watchdog.service

log_info "Setting up log rotation..."

# Create logrotate configuration
sudo tee /etc/logrotate.d/crypto-bot > /dev/null << EOF
$BOT_DIR/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 644 ubuntu ubuntu
    postrotate
        systemctl reload-or-restart crypto-trading-bot crypto-bot-watchdog
    endscript
}
EOF

log_info "Creating management scripts..."

# Create start script
cat > start_bot_system.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting Crypto Bot System..."
sudo systemctl start crypto-trading-bot
sudo systemctl start crypto-bot-watchdog
echo "✅ Bot system started"
systemctl status crypto-trading-bot crypto-bot-watchdog --no-pager -l
EOF

# Create stop script
cat > stop_bot_system.sh << 'EOF'
#!/bin/bash
echo "🛑 Stopping Crypto Bot System..."
sudo systemctl stop crypto-bot-watchdog
sudo systemctl stop crypto-trading-bot
echo "✅ Bot system stopped"
EOF

# Create status script
cat > status_bot_system.sh << 'EOF'
#!/bin/bash
echo "📊 Crypto Bot System Status"
echo "=========================="
echo ""
echo "🤖 Trading Bot Service:"
systemctl status crypto-trading-bot --no-pager -l
echo ""
echo "🛡️ Watchdog Service:"
systemctl status crypto-bot-watchdog --no-pager -l
echo ""
echo "📊 Resource Usage:"
ps aux | head -1
ps aux | grep -E "(bot\.py|crypto-bot-watchdog)" | grep -v grep || echo "No bot processes found"
echo ""
echo "📈 Recent Logs:"
echo "Bot logs:"
tail -5 systemd_bot.log 2>/dev/null || echo "No bot logs yet"
echo ""
echo "Watchdog logs:"
tail -5 systemd_watchdog.log 2>/dev/null || echo "No watchdog logs yet"
EOF

# Create restart script
cat > restart_bot_system.sh << 'EOF'
#!/bin/bash
echo "🔄 Restarting Crypto Bot System..."
sudo systemctl restart crypto-trading-bot
sudo systemctl restart crypto-bot-watchdog
echo "✅ Bot system restarted"
systemctl status crypto-trading-bot crypto-bot-watchdog --no-pager -l
EOF

# Make scripts executable
chmod +x start_bot_system.sh stop_bot_system.sh status_bot_system.sh restart_bot_system.sh

log_info "Creating monitoring script..."

# Create comprehensive monitoring script
cat > monitor_bot_health.sh << 'EOF'
#!/bin/bash
echo "🔍 Crypto Bot Health Monitor"
echo "============================"
echo ""

# Check system services
echo "📊 Service Status:"
systemctl is-active crypto-trading-bot && echo "✅ Trading Bot: ACTIVE" || echo "❌ Trading Bot: INACTIVE"
systemctl is-active crypto-bot-watchdog && echo "✅ Watchdog: ACTIVE" || echo "❌ Watchdog: INACTIVE"
echo ""

# Check processes
echo "🔄 Process Status:"
if pgrep -f "bot.py" > /dev/null; then
    echo "✅ Bot process: RUNNING"
    echo "   PID: $(pgrep -f 'bot.py')"
    echo "   Memory: $(ps -o pid,rss,pmem,comm -p $(pgrep -f 'bot.py') | tail -1 | awk '{print $2/1024 " MB (" $3 "%)"}')"
else
    echo "❌ Bot process: NOT RUNNING"
fi

if pgrep -f "crypto-bot-watchdog.py" > /dev/null; then
    echo "✅ Watchdog process: RUNNING"
    echo "   PID: $(pgrep -f 'crypto-bot-watchdog.py')"
else
    echo "❌ Watchdog process: NOT RUNNING"
fi
echo ""

# Check recent activity
echo "📈 Recent Activity:"
if [ -f "bot_log.txt" ]; then
    last_log=$(stat -c %Y bot_log.txt)
    current_time=$(date +%s)
    time_diff=$((current_time - last_log))
    
    if [ $time_diff -lt 300 ]; then
        echo "✅ Bot log activity: RECENT (${time_diff}s ago)"
    elif [ $time_diff -lt 900 ]; then
        echo "⚠️ Bot log activity: OLD (${time_diff}s ago)"
    else
        echo "❌ Bot log activity: STALE (${time_diff}s ago)"
    fi
    
    echo "   Last log entry:"
    tail -1 bot_log.txt | sed 's/^/   /'
else
    echo "❌ No bot log file found"
fi
echo ""

# Check disk space
echo "💾 Disk Space:"
df -h . | awk 'NR==2 {print "   Used: " $3 "/" $2 " (" $5 ")"}'
echo ""

# Check network connectivity
echo "🌐 Network Status:"
if ping -c 1 api.binance.com > /dev/null 2>&1; then
    echo "✅ Binance API: REACHABLE"
else
    echo "❌ Binance API: UNREACHABLE"
fi

# Show system uptime
echo ""
echo "⏰ System Uptime:"
uptime | sed 's/^/   /'
EOF

chmod +x monitor_bot_health.sh

log_info "Setting up cron jobs for monitoring..."

# Add cron job for periodic health monitoring (every 5 minutes)
(crontab -l 2>/dev/null; echo "*/5 * * * * cd $BOT_DIR && ./monitor_bot_health.sh >> health_monitor.log 2>&1") | crontab -

# Add cron job for daily log cleanup (keep last 7 days)
(crontab -l 2>/dev/null; echo "0 2 * * * find $BOT_DIR -name '*.log' -mtime +7 -delete") | crontab -

log_info "Testing the setup..."

# Test watchdog script syntax
if python3 -m py_compile crypto-bot-watchdog.py; then
    log_info "✅ Watchdog script syntax: OK"
else
    log_error "❌ Watchdog script syntax: ERROR"
    exit 1
fi

# Test systemd configuration
if sudo systemctl daemon-reload; then
    log_info "✅ Systemd configuration: OK"
else
    log_error "❌ Systemd configuration: ERROR"
    exit 1
fi

echo ""
echo "🎉 AUTO-RESTART SETUP COMPLETE!"
echo "==============================="
echo ""
echo "📋 Available Commands:"
echo "   ./start_bot_system.sh     - Start the bot system"
echo "   ./stop_bot_system.sh      - Stop the bot system"
echo "   ./restart_bot_system.sh   - Restart the bot system"
echo "   ./status_bot_system.sh    - Check system status"
echo "   ./monitor_bot_health.sh   - Detailed health check"
echo ""
echo "🔧 Management Commands:"
echo "   sudo systemctl start crypto-trading-bot"
echo "   sudo systemctl stop crypto-trading-bot"
echo "   sudo systemctl status crypto-trading-bot"
echo "   sudo systemctl start crypto-bot-watchdog"
echo "   sudo systemctl stop crypto-bot-watchdog"
echo ""
echo "📊 Log Files:"
echo "   systemd_bot.log          - Bot service logs"
echo "   systemd_watchdog.log     - Watchdog service logs"
echo "   watchdog.log             - Watchdog activity log"
echo "   health_monitor.log       - Health monitoring log"
echo ""
echo "⚡ CURRENT STATUS:"
./status_bot_system.sh
echo ""
echo "🚀 To start the auto-restart system now:"
echo "   ./start_bot_system.sh"
echo ""
echo "✅ The bot will now automatically restart on:"
echo "   - System reboot"
echo "   - Process crash"
echo "   - Memory/CPU issues"
echo "   - Trading inactivity"
echo "   - Network problems"
