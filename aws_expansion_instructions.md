🚀 AWS EBS VOLUME EXPANSION GUIDE
=====================================

📅 Date: August 1, 2025
🎯 Goal: Expand from 8GB to 20GB for Phase 3 Weeks 2-4
💰 Cost: FREE (within AWS Free Tier)

STEP 1: AWS MANAGEMENT CONSOLE
==============================
1. 🌐 Go to: https://console.aws.amazon.com
2. 🔑 Sign in to your AWS account
3. 📍 Navigate to: Services → EC2
4. 💾 Click: "Volumes" (left sidebar under "Elastic Block Store")
5. 🎯 Find: Volume attached to your instance (should show "in-use")
6. ✅ Select: The volume (checkbox)
7. 🔧 Click: "Actions" → "Modify Volume"
8. 📏 Change: Size from 8 to 20 (GiB)
9. 💾 Click: "Modify"
10. ✅ Confirm: "Yes, Modify"

⏱️ Wait: 2-3 minutes for modification to complete

STEP 2: EC2 INSTANCE COMMANDS
=============================
After AWS console shows "Optimization Complete":

1. 🔗 SSH to your instance:
   ssh -i "C:\Users\miste\Documents\cryptobot-key.pem" ubuntu@3.135.216.32

2. 📏 Extend the partition:
   sudo growpart /dev/xvda 1

3. 📁 Resize the filesystem:
   sudo resize2fs /dev/xvda1

4. ✅ Verify expansion:
   df -h /

Expected Result:
- Before: 6.8G total, 831M available
- After: 19G+ total, 13G+ available

STEP 3: VERIFICATION
===================
✅ Check bot is still running:
   ps aux | grep bot.py

✅ Verify space:
   df -h /

✅ Test bot activity:
   tail -10 bot_output.log

🎉 SUCCESS CRITERIA
===================
- ✅ Filesystem shows ~19GB total
- ✅ Available space > 13GB  
- ✅ Bot continues running
- ✅ Ready for Phase 3 Weeks 2-4
- ✅ Still within FREE tier

💡 TROUBLESHOOTING
==================
If growpart fails:
- sudo apt update && sudo apt install cloud-guest-utils -y
- Then retry: sudo growpart /dev/xvda 1

If resize2fs fails:
- Check filesystem: sudo fsck /dev/xvda1
- Then retry: sudo resize2fs /dev/xvda1

🎯 NEXT STEPS AFTER EXPANSION
=============================
1. Install TensorFlow properly with 13GB+ space
2. Begin Phase 3 Week 2 development
3. Upload advanced ML models
4. Implement real-time data feeds

This expansion gives us room for ALL Phase 3 features! 🚀
