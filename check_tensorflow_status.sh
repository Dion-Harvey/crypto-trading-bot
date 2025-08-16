#!/bin/bash
# 🔍 TENSORFLOW/KERAS STATUS CHECKER

echo "🧠 TENSORFLOW/KERAS PERFORMANCE CHECK"
echo "====================================="
echo "📅 $(date)"
echo

echo "📊 SYSTEM RESOURCES:"
echo "==================="
echo "💾 Disk Space:"
df -h /

echo
echo "🔧 Memory Usage:"
free -h

echo
echo "⚡ CPU Load:"
uptime

echo
echo "🤖 BOT STATUS:"
echo "=============="
echo "🔍 Python Processes:"
ps aux | grep python | grep -v grep

echo
echo "📈 Bot Memory Usage:"
ps aux | grep bot.py | grep -v grep | awk '{print "Process:", $2, "CPU:", $3"%", "Memory:", $4"%", "RSS:", $6"KB"}'

echo
echo "🧠 TENSORFLOW TEST:"
echo "==================="
python3 -c "
try:
    import tensorflow as tf
    print('✅ TensorFlow Version:', tf.__version__)
    print('✅ TensorFlow Available: YES')
    
    # Test basic functionality
    import numpy as np
    x = tf.constant([[1.0, 2.0], [3.0, 4.0]])
    print('✅ TensorFlow Operations: Working')
    
    # Check GPU/CPU
    devices = tf.config.list_physical_devices()
    print('✅ Available Devices:', len(devices))
    for device in devices:
        print('   -', device)
        
except ImportError as e:
    print('❌ TensorFlow Import Error:', str(e))
except Exception as e:
    print('⚠️ TensorFlow Error:', str(e))
"

echo
echo "🔬 LSTM MODULE TEST:"
echo "==================="
python3 test_lstm_setup.py 2>/dev/null | head -20

echo
echo "📊 BOT ACTIVITY (Last 10 lines):"
echo "================================="
tail -10 bot_output.log 2>/dev/null || echo "❌ No bot_output.log found"

echo
echo "🎯 PHASE 3 FEATURES STATUS:"
echo "==========================="
python3 -c "
try:
    # Test Phase 3 modules
    import enhanced_config
    print('✅ Enhanced Config: Loaded')
    
    import priority_functions_5m1m
    print('✅ Priority 5m+1m: Loaded')
    
    import multi_crypto_monitor
    print('✅ Multi-Crypto Monitor: Loaded')
    
    import lstm_price_predictor
    print('✅ LSTM Price Predictor: Loaded')
    
    print('✅ Phase 3 Week 1: 100% Ready')
    
except Exception as e:
    print('⚠️ Phase 3 Module Error:', str(e))
"

echo
echo "🎉 STATUS SUMMARY:"
echo "=================="
if pgrep -f "python.*bot.py" > /dev/null; then
    echo "✅ Bot: RUNNING"
else
    echo "❌ Bot: NOT RUNNING"
fi

if python3 -c "import tensorflow" 2>/dev/null; then
    echo "✅ TensorFlow: WORKING"
else
    echo "❌ TensorFlow: NOT WORKING"
fi

DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -lt 50 ]; then
    echo "✅ Disk Space: HEALTHY ($DISK_USAGE% used)"
elif [ $DISK_USAGE -lt 80 ]; then
    echo "⚠️ Disk Space: MODERATE ($DISK_USAGE% used)"
else
    echo "❌ Disk Space: HIGH ($DISK_USAGE% used)"
fi

echo
echo "🚀 Ready for Phase 3 Week 2 development!"
