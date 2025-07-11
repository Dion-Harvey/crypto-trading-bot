#!/usr/bin/env python3
"""
Test script to simulate actual bot price jump detection
"""

import sys
import os
import time
import ccxt
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import BINANCE_API_KEY, BINANCE_API_SECRET
from enhanced_config import get_bot_config
from price_jump_detector import get_price_jump_detector

def test_real_price_jump_detection():
    print("🔧 Testing Real Price Jump Detection...")
    
    # Load config
    bot_config = get_bot_config()
    optimized_config = bot_config.config
    
    # Initialize exchange
    exchange = ccxt.binanceus({
        'apiKey': BINANCE_API_KEY,
        'secret': BINANCE_API_SECRET,
        'enableRateLimit': True,
        'timeout': 10000,
        'sandbox': False
    })
    
    # Initialize detector
    detector = get_price_jump_detector(optimized_config)
    
    print("🚀 Starting real-time price jump detection test...")
    print("📊 Will monitor for 5 minutes, checking every 30 seconds...")
    
    for i in range(10):  # 10 iterations * 30 seconds = 5 minutes
        try:
            # Get current price
            ticker = exchange.fetch_ticker('BTC/USDC')
            current_price = ticker['last']
            
            # Test price jump detection
            jump = detector.add_price_point(current_price)
            
            timestamp = time.strftime('%H:%M:%S')
            
            if jump:
                print(f"🚀 [{timestamp}] PRICE JUMP DETECTED: {jump.direction} {jump.change_pct:+.2f}% in {jump.duration_seconds:.0f}s")
                print(f"   From ${jump.start_price:.2f} → ${jump.end_price:.2f}")
                
                # Get analysis
                analysis = detector.get_jump_analysis(jump)
                print(f"   Speed: {analysis['speed']:.2f}%/min | Urgency: {analysis['urgency']}")
                print(f"   Override Cooldown: {analysis['override_cooldown']}")
            else:
                print(f"📊 [{timestamp}] Price: ${current_price:.2f} - No jump detected")
            
            # Show current detector status
            status = detector.get_status()
            print(f"   History: {status['price_history_size']} points, Recent jumps: {status['recent_jumps_count']}")
            
            time.sleep(30)  # Wait 30 seconds
            
        except Exception as e:
            print(f"❌ Error: {e}")
            break
    
    print("✅ Test completed")

if __name__ == "__main__":
    test_real_price_jump_detection()
