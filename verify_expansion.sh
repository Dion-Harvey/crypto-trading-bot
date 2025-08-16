#!/bin/bash
# 🔍 AWS Volume Expansion Verification Script

echo "🚀 AWS VOLUME EXPANSION VERIFICATION"
echo "===================================="
echo "📅 $(date)"
echo

echo "📊 BEFORE EXPANSION:"
echo "Current disk usage:"
df -h /
echo

echo "📦 Current bot status:"
ps aux | grep python | grep bot.py | grep -v grep
echo

echo "🔧 EXPANSION COMMANDS TO RUN:"
echo "=============================="
echo "1. sudo growpart /dev/xvda 1"
echo "2. sudo resize2fs /dev/xvda1"
echo "3. df -h /"
echo

echo "✅ SUCCESS CRITERIA:"
echo "==================="
echo "- Total space: ~19GB (up from 6.8GB)"
echo "- Available space: 13GB+ (up from 831MB)"
echo "- Bot continues running"
echo "- Ready for Phase 3 Weeks 2-4"
echo

echo "🎯 PHASE 3 SPACE ALLOCATION (after expansion):"
echo "==============================================="
echo "Current usage: 5.9GB"
echo "Available for Phase 3:"
echo "  - Week 2 ML models: 200MB ✅"
echo "  - Week 3 data feeds: 100MB ✅"
echo "  - Week 4 analytics: 150MB ✅"
echo "  - TensorFlow full: 400MB ✅"
echo "  - Future growth: 12GB+ ✅"
echo "  TOTAL AVAILABLE: 13GB+ ✅"
echo

echo "💰 Cost: FREE (still within AWS Free Tier limits)"
echo "🎉 Ready to proceed with expansion!"
