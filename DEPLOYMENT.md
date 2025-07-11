# 🔐 Cloud Deployment Setup

## API Key Configuration

**IMPORTANT**: Never commit actual API keys to GitHub!

### For Local Development:
1. Copy your API keys from `config_backup.json` (local only)
2. Update `config.py` with your actual keys
3. The bot will load keys from `config.py`

### For Cloud Deployment:
1. Use environment variables for security
2. Set these environment variables on your cloud service:
   - `BINANCE_API_KEY=your_actual_key`
   - `BINANCE_API_SECRET=your_actual_secret`

### Alternative: JSON Config Method
1. Create `config.json` with your keys (never commit this!)
2. Update bot.py to load from JSON if needed

## Security Checklist ✅
- [ ] API keys are in environment variables or local config only
- [ ] `config.py` contains placeholder values only
- [ ] `.gitignore` excludes all sensitive files
- [ ] No actual keys are committed to GitHub

## Quick Setup Commands

### Restore Local Config:
```bash
# Copy your keys back from backup
cp config_backup.json config.json
# Or manually update config.py with real keys
```

### Cloud Environment Variables:
```bash
export BINANCE_API_KEY="your_key_here"
export BINANCE_API_SECRET="your_secret_here"
```

## Files Protected by .gitignore:
- `config.py` (actual keys)
- `config.json` (actual keys)
- `config_backup.json` (backup keys)
- `bot_log.txt` (trading logs)
- `trade_log.csv` (trade history)
- `bot_state.json` (runtime state)
