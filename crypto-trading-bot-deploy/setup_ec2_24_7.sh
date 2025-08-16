#!/bin/bash
#
# 🚀 AWS EC2 Setup Script for 24/7 Crypto Trading Bot
# This script configures your EC2 instance for continuous bot operation
#

set -e

echo "🚀 Setting up Crypto Trading Bot for 24/7 AWS EC2 Operation"
echo "============================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}[SETUP]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root. Run as ubuntu user."
   exit 1
fi

# Variables
BOT_DIR="/home/ubuntu/crypto-trading-bot/crypto-trading-bot"
SERVICE_NAME="crypto-trading-bot"
VENV_DIR="$BOT_DIR/.venv"

print_header "Checking prerequisites..."

# Check if we're on Ubuntu
if ! grep -q "Ubuntu" /etc/os-release; then
    print_warning "This script is designed for Ubuntu. Proceeding anyway..."
fi

# Check if bot directory exists
if [ ! -d "$BOT_DIR" ]; then
    print_error "Bot directory not found at $BOT_DIR"
    print_error "Please ensure the bot code is uploaded to the EC2 instance first"
    exit 1
fi

print_status "Bot directory found: $BOT_DIR"

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    print_warning "Virtual environment not found. Creating..."
    cd "$BOT_DIR"
    python3 -m venv .venv
    source .venv/bin/activate
    pip install --upgrade pip
    
    # Install required packages
    if [ -f "requirements.txt" ]; then
        print_status "Installing dependencies from requirements.txt..."
        pip install -r requirements.txt
    else
        print_status "Installing common dependencies..."
        pip install ccxt pandas numpy python-dotenv scipy scikit-learn
    fi
else
    print_status "Virtual environment found: $VENV_DIR"
fi

print_header "Setting up systemd service..."

# Copy service file to systemd directory
sudo cp "$BOT_DIR/crypto-trading-bot.service" /etc/systemd/system/

# Set proper permissions
sudo chmod 644 /etc/systemd/system/crypto-trading-bot.service

# Reload systemd
sudo systemctl daemon-reload

print_header "Configuring service startup..."

# Enable service to start on boot
sudo systemctl enable $SERVICE_NAME

print_header "Setting up log rotation..."

# Create logrotate configuration
sudo tee /etc/logrotate.d/crypto-trading-bot > /dev/null <<EOF
$BOT_DIR/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    copytruncate
    create 644 ubuntu ubuntu
}
EOF

print_header "Setting up monitoring script..."

# Create monitoring script
cat > "$BOT_DIR/monitor_bot.sh" <<EOF
#!/bin/bash
#
# 📊 Trading Bot Monitoring Script
# Run this script to check bot status and performance
#

BOT_DIR="$BOT_DIR"
SERVICE_NAME="$SERVICE_NAME"

echo "🤖 Crypto Trading Bot Status Monitor"
echo "===================================="

# Service status
echo "📋 Service Status:"
sudo systemctl status \$SERVICE_NAME --no-pager -l

echo ""
echo "📊 Recent Performance (last 20 lines):"
tail -n 20 "\$BOT_DIR/daemon.log" | grep -E "(TRADING PERFORMANCE|Portfolio|PnL)" || echo "No recent performance data found"

echo ""
echo "📈 Recent Activity (last 10 lines):"
tail -n 10 "\$BOT_DIR/bot_log.txt" | grep -E "(BUY|SELL|EXECUTED)" || echo "No recent trading activity found"

echo ""
echo "💾 Disk Usage:"
df -h \$BOT_DIR

echo ""
echo "🔍 Process Information:"
ps aux | grep -E "(python.*bot\.py|run_bot_daemon\.py)" | grep -v grep || echo "Bot process not found"

echo ""
echo "📝 Log Files:"
ls -la \$BOT_DIR/*.log 2>/dev/null || echo "No log files found"
EOF

chmod +x "$BOT_DIR/monitor_bot.sh"

print_header "Setting up maintenance scripts..."

# Create backup script
cat > "$BOT_DIR/backup_bot_data.sh" <<EOF
#!/bin/bash
#
# 💾 Trading Bot Backup Script
# Backs up configuration and trading data
#

BOT_DIR="$BOT_DIR"
BACKUP_DIR="\$BOT_DIR/backups"
DATE=\$(date +%Y%m%d_%H%M%S)

mkdir -p "\$BACKUP_DIR"

echo "💾 Creating backup: backup_\$DATE.tar.gz"

tar -czf "\$BACKUP_DIR/backup_\$DATE.tar.gz" \\
    "\$BOT_DIR/enhanced_config.json" \\
    "\$BOT_DIR/bot_state.json" \\
    "\$BOT_DIR/config.json" \\
    "\$BOT_DIR"/*.log \\
    2>/dev/null

# Keep only last 10 backups
cd "\$BACKUP_DIR"
ls -t backup_*.tar.gz | tail -n +11 | xargs -r rm

echo "✅ Backup complete: \$BACKUP_DIR/backup_\$DATE.tar.gz"
echo "📂 Total backups: \$(ls backup_*.tar.gz 2>/dev/null | wc -l)"
EOF

chmod +x "$BOT_DIR/backup_bot_data.sh"

# Create update script
cat > "$BOT_DIR/update_bot.sh" <<EOF
#!/bin/bash
#
# 🔄 Trading Bot Update Script
# Safely updates bot code with backup
#

BOT_DIR="$BOT_DIR"
SERVICE_NAME="$SERVICE_NAME"

echo "🔄 Updating Trading Bot..."

# Create backup first
./backup_bot_data.sh

# Stop the service
echo "🛑 Stopping bot service..."
sudo systemctl stop \$SERVICE_NAME

# Wait for service to stop
sleep 10

echo "📥 Bot stopped. You can now update the code files."
echo "⚠️  After updating, run: sudo systemctl start \$SERVICE_NAME"
echo "📊 Monitor with: ./monitor_bot.sh"
EOF

chmod +x "$BOT_DIR/update_bot.sh"

print_header "Setting up cron jobs..."

# Add cron jobs for maintenance
(crontab -l 2>/dev/null; echo "# Trading Bot Maintenance") | crontab -
(crontab -l 2>/dev/null; echo "0 2 * * * $BOT_DIR/backup_bot_data.sh >> $BOT_DIR/backup.log 2>&1") | crontab -
(crontab -l 2>/dev/null; echo "*/15 * * * * $BOT_DIR/monitor_bot.sh > /tmp/bot_status.txt 2>&1") | crontab -

print_header "Final setup steps..."

# Ensure proper permissions
sudo chown -R ubuntu:ubuntu "$BOT_DIR"
chmod +x "$BOT_DIR/run_bot_daemon.py"

print_status "Setup complete! Here's what was configured:"
echo ""
echo "✅ Systemd service: $SERVICE_NAME"
echo "✅ Auto-start on boot: Enabled"
echo "✅ Log rotation: Configured"
echo "✅ Monitoring script: $BOT_DIR/monitor_bot.sh"
echo "✅ Backup script: $BOT_DIR/backup_bot_data.sh"
echo "✅ Update script: $BOT_DIR/update_bot.sh"
echo "✅ Cron jobs: Backup (daily 2AM) + Monitoring (every 15min)"
echo ""

print_header "Starting the bot service..."

# Start the service
sudo systemctl start $SERVICE_NAME

# Check if it started successfully
sleep 5
if sudo systemctl is-active --quiet $SERVICE_NAME; then
    print_status "🚀 Bot service started successfully!"
    print_status "📊 Check status with: ./monitor_bot.sh"
    print_status "📝 View logs with: tail -f daemon.log"
else
    print_error "❌ Failed to start bot service"
    print_error "📋 Check status with: sudo systemctl status $SERVICE_NAME"
fi

echo ""
print_header "🎯 24/7 Operation Commands:"
echo "   Start:   sudo systemctl start $SERVICE_NAME"
echo "   Stop:    sudo systemctl stop $SERVICE_NAME"
echo "   Restart: sudo systemctl restart $SERVICE_NAME"
echo "   Status:  sudo systemctl status $SERVICE_NAME"
echo "   Logs:    journalctl -u $SERVICE_NAME -f"
echo "   Monitor: ./monitor_bot.sh"
echo ""

print_status "🚀 Your crypto trading bot is now configured for 24/7 operation!"
print_status "🔍 The daemon will automatically restart the bot if it crashes"
print_status "📊 Logs are saved to: $BOT_DIR/daemon.log"
print_status "💾 Daily backups are scheduled at 2 AM"
