🚀 PHASE 2 AWS DEPLOYMENT CHECKLIST
====================================
Target: ubuntu@3.135.216.32
Phase 2 Cost: $0/month (adds $1,317 value)

✅ READY FILES (all created):
✅ free_phase2_api.py (34KB) - Advanced intelligence APIs
✅ free_phase2_config.py (13KB) - Phase 2 configuration
✅ unified_free_config.py (17KB) - Combined config management
✅ bot.py (258KB) - Enhanced with Phase 2 integration
✅ free_crypto_api.py (16KB) - Phase 1 APIs
✅ onchain_config.py (8KB) - API configuration
✅ aws_verify_phase2.py (12KB) - Deployment verification

📋 DEPLOYMENT STEPS:

STEP 1: Upload Files (replace 'your-key.pem' with your actual key file)
-----------------------------------------------------------------------
scp -i "your-key.pem" free_phase2_api.py free_phase2_config.py unified_free_config.py ubuntu@3.135.216.32:/home/ubuntu/crypto-trading-bot/

scp -i "your-key.pem" bot.py free_crypto_api.py onchain_config.py aws_verify_phase2.py ubuntu@3.135.216.32:/home/ubuntu/crypto-trading-bot/

STEP 2: SSH into Instance
-------------------------
ssh -i "your-key.pem" ubuntu@3.135.216.32

STEP 3: Setup on AWS (run these commands after SSH)
----------------------------------------------------
cd /home/ubuntu/crypto-trading-bot

# Stop existing bots (you had 3 running)
pkill -f "python3 bot.py"

# Install dependencies (if needed)
pip3 install -r requirements.txt

# Verify Phase 2 installation
python3 aws_verify_phase2.py

STEP 4: Quick Test Phase 2
---------------------------
python3 -c "from free_phase2_config import validate_phase2_setup; result = validate_phase2_setup(); print(f'✅ Phase 2 Status: {result[\"status\"]}'); print(f'💰 Monthly Cost: \${result[\"summary\"][\"monthly_cost\"]}'); print(f'💎 Monthly Savings: \${result[\"summary\"][\"monthly_savings\"]}'); print(f'🔧 Active APIs: {result[\"summary\"][\"active_apis\"]}')"

STEP 5: Start Enhanced Bot
--------------------------
nohup python3 bot.py > bot_phase2.log 2>&1 &

STEP 6: Monitor Logs
--------------------
tail -f bot_phase2.log

🎯 WHAT TO EXPECT:
✅ Bot will initialize with Phase 2 messages
✅ 8 free APIs will be active (4 Phase 1 + 4 Phase 2)
✅ Enhanced trading signals will appear:
   🐋 WHALE ACCUMULATION: [Symbol] 
   🔵 EXCHANGE INFLOW SURGE: [Symbol]
   💹 RISK-ON SENTIMENT: [Symbol]
   📈 HIGH DEX ACTIVITY: [Symbol]
   🚀 PHASE 2 ENHANCED: [Symbol]

💰 COST IMPACT: $0 (no additional costs)
🚀 VALUE ADDED: $1,317/month equivalent intelligence

Ready for deployment! 🎯
