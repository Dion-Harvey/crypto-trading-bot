#!/usr/bin/env python3
"""
Comprehensive test for enhanced multi-timeframe price jump detection
"""

import sys
import os
import time
import random
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_config import get_bot_config
from price_jump_detector import get_price_jump_detector

def test_enhanced_price_detection():
    print("🔧 Testing Enhanced Multi-Timeframe Price Jump Detection...")
    
    # Load config
    bot_config = get_bot_config()
    optimized_config = bot_config.config
    
    # Initialize detector
    detector = get_price_jump_detector(optimized_config)
    
    print("\n🚀 Testing different movement scenarios...")
    
    # Test 1: Rapid spike (should trigger 'spike' timeframe)
    print("\n📊 Test 1: Rapid Price Spike (0.6% in 30 seconds)")
    base_price = 110000.0
    detector.add_price_point(base_price)
    time.sleep(0.1)
    
    # Simulate rapid price increase
    for i in range(5):
        price = base_price * (1 + (i * 0.12 / 100))  # 0.6% total increase
        jump = detector.add_price_point(price)
        if jump:
            analysis = detector.get_jump_analysis(jump)
            print(f"   ✅ Spike detected: {jump.direction} {jump.change_pct:+.2f}% in {jump.duration_seconds:.1f}s")
            print(f"   📈 Timeframe: {analysis['timeframe']} | Urgency: {analysis['urgency']} ({analysis['urgency_score']:.1f})")
            print(f"   🎯 Speed: {analysis['speed']:.2f}%/min | Override: {analysis['override_cooldown']}")
            break
        time.sleep(0.02)
    
    # Test 2: Short trend (should trigger 'short_trend' timeframe)
    print("\n📊 Test 2: Short Trend (1.0% in 5 minutes)")
    base_price = 110500.0
    detector.add_price_point(base_price)
    
    # Simulate gradual increase over 5 minutes (compressed to 1 second)
    for i in range(10):
        price = base_price * (1 + (i * 0.1 / 100))  # 1.0% total increase
        jump = detector.add_price_point(price)
        if jump and hasattr(jump, 'timeframe') and jump.timeframe == 'short_trend':
            analysis = detector.get_jump_analysis(jump)
            print(f"   ✅ Short trend detected: {jump.direction} {jump.change_pct:+.2f}% in {jump.duration_seconds:.1f}s")
            print(f"   📈 Timeframe: {analysis['timeframe']} | Urgency: {analysis['urgency']} ({analysis['urgency_score']:.1f})")
            print(f"   🎯 Trend Alignment: {analysis['trend_alignment']} | Momentum: {analysis['momentum_strength']:.2f}")
            break
        time.sleep(0.05)
    
    # Test 3: Medium trend (should trigger 'medium_trend' timeframe)
    print("\n📊 Test 3: Medium Trend (1.5% in 15 minutes)")
    base_price = 111000.0
    detector.add_price_point(base_price)
    
    # Simulate gradual increase over 15 minutes (compressed to 2 seconds)
    for i in range(15):
        price = base_price * (1 + (i * 0.1 / 100))  # 1.5% total increase
        jump = detector.add_price_point(price)
        if jump and hasattr(jump, 'timeframe') and jump.timeframe == 'medium_trend':
            analysis = detector.get_jump_analysis(jump)
            print(f"   ✅ Medium trend detected: {jump.direction} {jump.change_pct:+.2f}% in {jump.duration_seconds:.1f}s")
            print(f"   📈 Timeframe: {analysis['timeframe']} | Urgency: {analysis['urgency']} ({analysis['urgency_score']:.1f})")
            print(f"   🎯 Trend Alignment: {analysis['trend_alignment']} | Momentum: {analysis['momentum_strength']:.2f}")
            break
        time.sleep(0.1)
    
    # Test 4: Long trend (should trigger 'long_trend' timeframe)
    print("\n📊 Test 4: Long Trend (2.0% in 30 minutes)")
    base_price = 111500.0
    detector.add_price_point(base_price)
    
    # Simulate gradual increase over 30 minutes (compressed to 3 seconds)
    for i in range(20):
        price = base_price * (1 + (i * 0.1 / 100))  # 2.0% total increase
        jump = detector.add_price_point(price)
        if jump and hasattr(jump, 'timeframe') and jump.timeframe == 'long_trend':
            analysis = detector.get_jump_analysis(jump)
            print(f"   ✅ Long trend detected: {jump.direction} {jump.change_pct:+.2f}% in {jump.duration_seconds:.1f}s")
            print(f"   📈 Timeframe: {analysis['timeframe']} | Urgency: {analysis['urgency']} ({analysis['urgency_score']:.1f})")
            print(f"   🎯 Trend Alignment: {analysis['trend_alignment']} | Momentum: {analysis['momentum_strength']:.2f}")
            break
        time.sleep(0.1)
    
    # Test 5: Show final status
    print("\n📊 Final System Status:")
    status = detector.get_status()
    print(f"   💾 Price History: {status['price_history_size']} points")
    print(f"   🎯 Recent Jumps: {status['recent_jumps_count']} total")
    print(f"   📈 Trend State: {status['current_trend']['direction']} (strength: {status['current_trend']['strength']:.2f})")
    print(f"   ⏱️ Timeframe Activity: {status['timeframe_activity']}")
    
    # Test 6: Cooldown override scenarios
    print("\n📊 Test 6: Cooldown Override Scenarios")
    test_jumps = [
        {'change_pct': 0.8, 'timeframe': 'spike', 'urgency_score': 6.5},
        {'change_pct': 1.2, 'timeframe': 'short_trend', 'urgency_score': 4.2},
        {'change_pct': 1.8, 'timeframe': 'medium_trend', 'urgency_score': 3.1},
        {'change_pct': 2.5, 'timeframe': 'long_trend', 'urgency_score': 2.8}
    ]
    
    for i, jump_data in enumerate(test_jumps):
        # Create a mock jump object
        class MockJump:
            def __init__(self, data):
                self.change_pct = data['change_pct']
                self.timeframe = data['timeframe']
                self.urgency_score = data['urgency_score']
                self.direction = 'UP'
                self.duration_seconds = 60
        
        mock_jump = MockJump(jump_data)
        should_override = detector.should_override_cooldown(mock_jump)
        
        print(f"   📊 {jump_data['timeframe']}: {jump_data['change_pct']:+.1f}% (urgency: {jump_data['urgency_score']:.1f}) → Override: {should_override}")
    
    print("\n✅ Enhanced Multi-Timeframe Price Detection Test Complete!")

if __name__ == "__main__":
    test_enhanced_price_detection()
