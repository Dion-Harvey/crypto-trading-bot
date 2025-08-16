#!/usr/bin/env python3
"""
Test script to debug price jump detector initialization
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_config import get_bot_config
from price_jump_detector import get_price_jump_detector

def test_price_jump_detector():
    print("🔧 Testing Price Jump Detector Initialization...")
    
    # Load config
    bot_config = get_bot_config()
    optimized_config = bot_config.config
    
    print(f"✅ Config loaded successfully")
    print(f"📊 System config keys: {list(optimized_config.get('system', {}).keys())}")
    
    # Check if price jump config exists
    system_config = optimized_config.get('system', {})
    jump_config = system_config.get('price_jump_detection', {})
    
    print(f"🔍 Price Jump Detection config: {jump_config}")
    
    # Try to initialize detector
    try:
        detector = get_price_jump_detector(optimized_config)
        print(f"✅ Price Jump Detector initialized successfully")
        
        # Get status
        status = detector.get_status()
        print(f"📊 Detector Status: {status}")
        
        # Test with a sample price
        test_price = 108000.0
        jump = detector.add_price_point(test_price)
        print(f"🧪 Test price point added: ${test_price}")
        print(f"🔍 Jump detected: {jump}")
        
        # Add another price point to test detection
        test_price2 = 108600.0  # +0.56% increase
        jump2 = detector.add_price_point(test_price2)
        print(f"🧪 Test price point 2 added: ${test_price2}")
        print(f"🔍 Jump detected: {jump2}")
        
    except Exception as e:
        print(f"❌ Error initializing detector: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_price_jump_detector()
