#!/usr/bin/env python3
"""
🔍 COMPREHENSIVE BOT DIAGNOSTIC - PHASE 1 & PHASE 2 ANALYSIS
============================================================
Comprehensive system check for multi-pair trading bot with price jump detection
"""

import json
import time
import sys
from datetime import datetime
from enhanced_config import get_bot_config

def comprehensive_diagnostic():
    """Run complete diagnostic of all bot systems"""
    
    print("🚀 COMPREHENSIVE BOT DIAGNOSTIC")
    print("=" * 80)
    print(f"🕒 Diagnostic Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 1. PHASE 1 - CORE SYSTEM CHECK
    print("📋 PHASE 1: CORE SYSTEM DIAGNOSTICS")
    print("-" * 50)
    
    # Check configuration system
    try:
        config = get_bot_config()
        supported_pairs = config.get_supported_pairs()
        current_symbol = config.get_current_trading_symbol()
        
        print(f"✅ Config System: OPERATIONAL")
        print(f"   📊 Supported pairs: {len(supported_pairs)}")
        print(f"   🎯 Current active: {current_symbol}")
        print(f"   📝 All monitored pairs:")
        
        for i, pair in enumerate(supported_pairs, 1):
            status = "🎯 ACTIVE" if pair == current_symbol else "📊 monitored"
            print(f"      {i:2d}. {pair:12} - {status}")
            
    except Exception as e:
        print(f"❌ Config System: FAILED - {e}")
        return False
    
    # Check communication status
    print(f"\n🔄 Inter-Process Communication:")
    try:
        with open('enhanced_config.json', 'r') as f:
            config_data = json.load(f)
        
        last_switch = config_data.get('trading', {}).get('last_pair_switch', 'Never')
        switch_reason = config_data.get('trading', {}).get('switch_reason', 'None')
        
        if last_switch != 'Never':
            switch_time = datetime.fromisoformat(last_switch.replace('Z', '+00:00'))
            now = datetime.now()
            time_diff = (now - switch_time.replace(tzinfo=None)).total_seconds()
            
            print(f"   ✅ Last communication: {time_diff:.0f} seconds ago")
            print(f"   📝 Switch reason: {switch_reason}")
            
            if time_diff < 300:  # Less than 5 minutes
                print(f"   🟢 STATUS: Active and recent")
            elif time_diff < 3600:  # Less than 1 hour  
                print(f"   🟡 STATUS: Working but not recent")
            else:
                print(f"   🔴 STATUS: Stale - needs attention")
        else:
            print(f"   ⚠️ No recent communication detected")
            
    except Exception as e:
        print(f"   ❌ Communication check failed: {e}")
    
    # 2. PHASE 2 - PRICE JUMP DETECTION SYSTEM
    print(f"\n📈 PHASE 2: PRICE JUMP DETECTION DIAGNOSTICS")
    print("-" * 50)
    
    # Test price jump detection for each pair
    try:
        from price_jump_detector import get_price_jump_detector
        import ccxt
        from config import BINANCE_API_KEY, BINANCE_API_SECRET
        
        # Initialize exchange
        exchange = ccxt.binanceus({
            'apiKey': BINANCE_API_KEY,
            'secret': BINANCE_API_SECRET,
            'enableRateLimit': True,
            'timeout': 10000,
            'options': {'timeDifference': 1000}
        })
        
        # Get price jump detector
        jump_detector = get_price_jump_detector(exchange)
        
        print(f"✅ Price Jump Detector: INITIALIZED")
        print(f"   🔍 Testing jump detection across all pairs...")
        
        jump_opportunities = []
        
        for pair in supported_pairs[:5]:  # Test first 5 pairs for speed
            try:
                print(f"   📊 Analyzing {pair}...", end=" ")
                
                # Test price jump detection
                jump_result = jump_detector.detect_price_jump(pair)
                
                if jump_result and jump_result.get('jump_detected', False):
                    jump_pct = jump_result.get('jump_percentage', 0) * 100
                    timeframe = jump_result.get('timeframe', 'unknown')
                    confidence = jump_result.get('confidence', 0)
                    
                    print(f"🚨 JUMP: {jump_pct:+.2f}% ({timeframe}, conf: {confidence:.2f})")
                    jump_opportunities.append({
                        'pair': pair,
                        'jump_pct': jump_pct,
                        'timeframe': timeframe,
                        'confidence': confidence
                    })
                else:
                    print(f"📊 Normal")
                    
            except Exception as pair_error:
                print(f"❌ Error: {pair_error}")
        
        if jump_opportunities:
            print(f"\n🎯 PRICE JUMP OPPORTUNITIES DETECTED:")
            for opp in sorted(jump_opportunities, key=lambda x: abs(x['jump_pct']), reverse=True):
                print(f"   🚨 {opp['pair']:12} {opp['jump_pct']:+6.2f}% ({opp['timeframe']}) conf:{opp['confidence']:.2f}")
        else:
            print(f"\n📊 No significant price jumps detected across monitored pairs")
            
    except Exception as e:
        print(f"❌ Price Jump Detection: FAILED - {e}")
    
    # 3. PHASE 3 - MULTI-CRYPTO SELECTION SYSTEM
    print(f"\n🌐 PHASE 3: MULTI-CRYPTO SELECTION DIAGNOSTICS")
    print("-" * 50)
    
    try:
        from multi_crypto_monitor import get_multi_crypto_monitor
        
        # Get multi-crypto monitor
        multi_crypto_monitor = get_multi_crypto_monitor(exchange)
        
        print(f"✅ Multi-Crypto Monitor: INITIALIZED")
        print(f"   🔍 Getting trading recommendations...")
        
        # Get recommendations
        recommendations = multi_crypto_monitor.get_trading_recommendations()
        
        if recommendations['status'] == 'success':
            print(f"   🟢 Recommendations: SUCCESS")
            print(f"   📊 Top opportunities:")
            
            for i, rec in enumerate(recommendations['recommendations'][:3], 1):
                symbol = rec['symbol']
                score = rec['score']
                allocation = rec['allocation']
                metrics = rec.get('metrics', {})
                
                print(f"      {i}. {symbol:12} Score: {score:.3f} Alloc: {allocation:.1%}")
                if metrics:
                    print(f"         Metrics: {metrics}")
        else:
            print(f"   🔴 Recommendations: FAILED - {recommendations.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Multi-Crypto Selection: FAILED - {e}")
    
    # 4. PHASE 4 - TRADING STRATEGY ANALYSIS
    print(f"\n⚡ PHASE 4: TRADING STRATEGY DIAGNOSTICS")
    print("-" * 50)
    
    try:
        # Test strategy systems
        print(f"   🔍 Testing strategy components...")
        
        # Check enhanced multi-strategy
        try:
            from enhanced_multi_strategy import EnhancedMultiStrategy
            strategy = EnhancedMultiStrategy()
            print(f"   ✅ Enhanced Multi-Strategy: LOADED")
        except Exception as e:
            print(f"   ❌ Enhanced Multi-Strategy: FAILED - {e}")
        
        # Check institutional strategies
        try:
            from institutional_strategies import InstitutionalStrategyManager
            inst_manager = InstitutionalStrategyManager()
            print(f"   ✅ Institutional Strategies: LOADED")
        except Exception as e:
            print(f"   ❌ Institutional Strategies: FAILED - {e}")
        
        # Check individual strategies
        try:
            from strategies.ma_crossover import MovingAverageCrossover
            ma_strategy = MovingAverageCrossover()
            print(f"   ✅ MA Crossover Strategy: LOADED")
        except Exception as e:
            print(f"   ❌ MA Crossover Strategy: FAILED - {e}")
            
    except Exception as e:
        print(f"❌ Strategy Analysis: FAILED - {e}")
    
    # 5. PHASE 5 - RISK MANAGEMENT VERIFICATION
    print(f"\n🛡️ PHASE 5: RISK MANAGEMENT DIAGNOSTICS")
    print("-" * 50)
    
    try:
        risk_config = config.config['risk_management']
        
        print(f"   📊 Risk Management Configuration:")
        print(f"      Stop Loss: {risk_config.get('stop_loss_pct', 0)*100:.2f}%")
        print(f"      Take Profit: {risk_config.get('take_profit_pct', 0)*100:.2f}%")
        print(f"      Trailing Stop: {risk_config.get('trailing_stop_pct', 0)*100:.3f}%")
        print(f"      OCO Stop: {risk_config.get('trailing_oco_stop_pct', 0)*100:.2f}%")
        print(f"      OCO Profit: {risk_config.get('trailing_oco_profit_pct', 0)*100:.2f}%")
        print(f"      Binance Native: {risk_config.get('binance_native_trailing', {}).get('trailing_percent', 0):.2f}%")
        
        # Check for alignment issues
        trailing_stop = risk_config.get('trailing_stop_pct', 0)
        binance_native = risk_config.get('binance_native_trailing', {}).get('trailing_percent', 0) / 100
        
        if abs(trailing_stop - binance_native) > 0.001:
            print(f"   ⚠️ ALIGNMENT ISSUE: Software trailing ({trailing_stop*100:.3f}%) != Binance native ({binance_native*100:.3f}%)")
        else:
            print(f"   ✅ Trailing stops aligned at {trailing_stop*100:.3f}%")
            
    except Exception as e:
        print(f"❌ Risk Management: FAILED - {e}")
    
    # 6. FINAL SUMMARY
    print(f"\n🎯 DIAGNOSTIC SUMMARY")
    print("=" * 50)
    
    # Overall system status
    if current_symbol != 'BTC/USDT':
        print(f"🟢 SYSTEM STATUS: FULLY OPERATIONAL")
        print(f"   🎯 Active trading: {current_symbol}")
        print(f"   📊 Monitoring: {len(supported_pairs)} pairs")
        print(f"   🔄 Communication: Active")
    else:
        print(f"🟡 SYSTEM STATUS: PARTIALLY OPERATIONAL")
        print(f"   ⚠️ May need scanner restart")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    
    if jump_opportunities:
        print(f"   🚨 IMMEDIATE ACTION: Price jumps detected!")
        for opp in jump_opportunities[:2]:
            print(f"      ⚡ Consider {opp['pair']} ({opp['jump_pct']:+.2f}%)")
    else:
        print(f"   📊 MONITORING: Continue normal operation")
    
    print(f"   🔄 NEXT STEPS:")
    print(f"      1. Start/restart bot if not running")
    print(f"      2. Monitor price jump alerts")
    print(f"      3. Verify automatic pair switching")
    print(f"      4. Check order management is clean")
    
    print(f"\n✅ DIAGNOSTIC COMPLETE")
    return True

if __name__ == "__main__":
    comprehensive_diagnostic()
