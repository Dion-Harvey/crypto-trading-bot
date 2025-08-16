📋 AWS UPLOAD CHECKLIST - WITH ALL RECENT FIXES
===============================================
Date: July 27, 2025
Status: Ready for deployment

🔧 CRITICAL FIXES TO DEPLOY:
============================

1. ✅ STOP-LIMIT ORDER ACCUMULATION FIX
   📁 bot.py                         # Contains cancel_all_stop_limit_orders() fix
   📁 emergency_order_cleanup.py     # Manual cleanup utility
   📁 fix_verification.py            # Verification tool

2. ✅ MULTI-PAIR COMMUNICATION FIX  
   📁 enhanced_config.py             # Runtime config reload capability
   📁 start_multipair_system.py      # Multi-process orchestration
   📁 multi_pair_scanner.py          # Opportunity scanner
   📁 check_multipair_status.py      # System status checker

3. ✅ 16-PAIR MONITORING SYSTEM
   📁 enhanced_config.json           # Contains all 16 trading pairs

🎯 DEPLOYMENT FILE CHECKLIST:
============================

CORE APPLICATION (MUST UPLOAD):
✅ bot.py                           # ⚠️ CRITICAL: Contains order accumulation fix
✅ config.py                        # API keys and basic configuration  
✅ enhanced_config.json             # ⚠️ CRITICAL: 16-pair configuration
✅ enhanced_config.py               # ⚠️ CRITICAL: Runtime reload fix
✅ requirements.txt                 # Python dependencies

MULTI-PAIR SYSTEM (MUST UPLOAD):
✅ start_multipair_system.py        # ⚠️ CRITICAL: Multi-pair orchestration
✅ multi_pair_scanner.py            # ⚠️ CRITICAL: Opportunity scanner  
✅ check_multipair_status.py        # System status verification

EMERGENCY UTILITIES (NEW - MUST UPLOAD):
✅ emergency_order_cleanup.py       # ⚠️ NEW: Manual order cleanup
✅ fix_verification.py              # ⚠️ NEW: Fix verification tool

STRATEGY FILES:
✅ strategies/ma_crossover.py
✅ strategies/multi_strategy_optimized.py
✅ strategies/hybrid_strategy.py

SUPPORT MODULES:
✅ enhanced_multi_strategy.py
✅ institutional_strategies.py  
✅ log_utils.py
✅ performance_tracker.py
✅ state_manager.py
✅ success_rate_enhancer.py

STATE FILES (OPTIONAL):
📊 bot_state.json                   # Trading state
📊 trade_log.csv                    # Trading history
📊 performance_report.csv           # Performance data

🚨 DEPLOYMENT PRIORITY:
======================

HIGH PRIORITY (Must upload immediately):
1. bot.py                          # Stop-limit accumulation fix
2. enhanced_config.py              # Runtime reload fix  
3. enhanced_config.json            # 16-pair configuration
4. start_multipair_system.py       # Multi-pair system
5. emergency_order_cleanup.py      # Emergency cleanup

MEDIUM PRIORITY:
6. multi_pair_scanner.py           # Scanner component
7. check_multipair_status.py       # Status checker
8. fix_verification.py             # Verification tool

LOW PRIORITY:
9. All other support files         # Can be uploaded after core fixes

🎯 VERIFICATION AFTER DEPLOYMENT:
================================

1. SSH to AWS instance
2. Run: python3 check_multipair_status.py
3. Verify 16 pairs are configured  
4. Test: python3 emergency_order_cleanup.py (dry run)
5. Start system: python3 start_multipair_system.py

🚀 EXPECTED RESULTS AFTER DEPLOYMENT:
====================================

✅ Bot monitors all 16 pairs simultaneously
✅ No more stop-limit order accumulation
✅ Clean order management (1 stop-limit per position)
✅ Real-time communication between scanner and main bot
✅ Emergency cleanup tools available for manual fixes
✅ Auto-recovery if scanner process fails

⚠️ PRE-DEPLOYMENT REMINDERS:
============================

1. 🔑 Ensure API keys are set in config.py
2. 🧹 Stop current bot before deployment
3. 📊 Backup current state files
4. 💰 Test with small amounts first
5. 📱 Monitor system closely after restart

🔧 DEPLOYMENT COMMAND:
=====================

Run in PowerShell:
.\aws_deploy_with_fixes.ps1

This will upload ALL critical fixes and verify the deployment.
