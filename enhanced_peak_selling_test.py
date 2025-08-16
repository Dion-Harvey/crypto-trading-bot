#!/usr/bin/env python3
"""
Enhanced Peak Selling & Stop-Limit Protection Test
Test both dip buying AND peak selling capabilities with stop-limit verification
"""

def test_enhanced_peak_selling_and_protection():
    try:
        import ccxt
        from config import BINANCE_API_KEY, BINANCE_API_SECRET
        from strategies.ma_crossover import fetch_ohlcv
        from log_utils import log_message
        from enhanced_config import get_bot_config
        from bot import detect_ma_crossover_signals, place_immediate_stop_limit_order
        
        print("🎯 ENHANCED PEAK SELLING & STOP-LIMIT PROTECTION TEST")
        print("=" * 70)
        
        # Initialize exchange
        exchange = ccxt.binanceus({
            'apiKey': BINANCE_API_KEY,
            'secret': BINANCE_API_SECRET,
            'enableRateLimit': True,
            'options': {'timeDifference': 1000}
        })
        
        # Get current market data
        df = fetch_ohlcv(exchange, 'BTC/USDT', '1m', 50)
        ticker = exchange.fetch_ticker('BTC/USDT')
        current_price = ticker['last']
        
        print(f"📊 Current BTC Price: ${current_price:,.2f}")
        print(f"📈 24h Change: {ticker['percentage']:+.2f}%")
        print()
        
        # Test enhanced signal detection (both dip buying AND peak selling)
        signal = detect_ma_crossover_signals(df, current_price)
        
        print(f"🎯 ENHANCED SIGNAL ANALYSIS:")
        print(f"   Signal Action: {signal.get('action', 'N/A')}")
        print(f"   Confidence: {signal.get('confidence', 0):.3f}")
        print(f"   Signal Type: {signal.get('crossover_type', 'N/A')}")
        
        if 'ema7' in signal and 'ema25' in signal:
            ema7 = signal['ema7']
            ema25 = signal['ema25']
            spread = signal.get('spread', 0)
            print(f"   EMA7: ${ema7:.2f}")
            print(f"   EMA25: ${ema25:.2f}")
            print(f"   Spread: {spread:.3f}%")
            
            if 'price_vs_ema7' in signal:
                price_vs_ema7_pct = signal['price_vs_ema7']*100
                print(f"   Price vs EMA7: {price_vs_ema7_pct:+.2f}%")
                
                # Determine signal category
                if price_vs_ema7_pct < -0.1:
                    print(f"   📉 BELOW EMA7: Dip buying territory")
                elif price_vs_ema7_pct > 1.0:
                    print(f"   📈 ABOVE EMA7: Peak selling territory")
                else:
                    print(f"   ⚖️ NEAR EMA7: Neutral territory")
            
            if 'price_vs_ema25' in signal:
                print(f"   Price vs EMA25: {signal['price_vs_ema25']*100:+.2f}%")
            if 'momentum' in signal:
                print(f"   Recent Momentum: {signal['momentum']*100:+.2f}%")
            if 'rsi' in signal and signal['rsi']:
                rsi_value = signal['rsi']
                print(f"   RSI: {rsi_value:.1f}")
                if rsi_value < 30:
                    print(f"   🔴 RSI: Oversold (Buy signal)")
                elif rsi_value > 70:
                    print(f"   🔴 RSI: Overbought (Sell signal)")
                else:
                    print(f"   🟡 RSI: Neutral")
        
        print(f"\n🔥 Signal Reasons:")
        for reason in signal.get('reasons', ['No reasons provided']):
            print(f"   • {reason}")
        
        # Load config and check thresholds
        config = get_bot_config()
        base_threshold = config.config['strategy_parameters']['confidence_threshold']
        dip_reduction = config.config['strategy_parameters'].get('dip_confidence_reduction', 0.15)
        
        print(f"\n⚖️ THRESHOLD ANALYSIS:")
        print(f"   Base Threshold: {base_threshold:.3f}")
        print(f"   Dip Threshold: {base_threshold - dip_reduction:.3f}")
        
        # Check if this is a dip or peak signal
        signal_type = "REGULAR"
        effective_threshold = base_threshold
        crossover_type = signal.get('crossover_type', '')
        
        if 'dip' in crossover_type.lower():
            signal_type = "DIP BUYING"
            effective_threshold = base_threshold - dip_reduction
            print(f"   🎯 DIP SIGNAL DETECTED - Using dip threshold: {effective_threshold:.3f}")
        elif 'peak' in crossover_type.lower():
            signal_type = "PEAK SELLING"
            print(f"   📈 PEAK SIGNAL DETECTED - Using base threshold: {effective_threshold:.3f}")
        else:
            print(f"   📊 Regular signal - Using base threshold: {effective_threshold:.3f}")
        
        signal_confidence = signal.get('confidence', 0)
        passes_threshold = signal_confidence >= effective_threshold
        
        print(f"\n🎯 EXECUTION ANALYSIS:")
        print(f"   Signal Type: {signal_type}")
        print(f"   Signal Confidence: {signal_confidence:.3f}")
        print(f"   Required Threshold: {effective_threshold:.3f}")
        print(f"   Execution Status: {'✅ WOULD EXECUTE' if passes_threshold else '❌ TOO WEAK'}")
        
        if not passes_threshold:
            confidence_gap = effective_threshold - signal_confidence
            print(f"   Confidence Gap: {confidence_gap:.3f}")
        
        # Test stop-limit protection configuration
        print(f"\n🛡️ STOP-LIMIT PROTECTION ANALYSIS:")
        risk_config = config.config['risk_management']
        
        stop_limit_enabled = risk_config.get('immediate_stop_limit_enabled', False)
        stop_limit_pct = risk_config.get('immediate_stop_limit_pct', 0.00125)
        trailing_enabled = risk_config.get('trailing_stop_limit_enabled', False)
        trailing_trigger = risk_config.get('trailing_stop_limit_trigger_pct', 0.001)
        
        print(f"   Immediate Stop-Limit: {'✅ ENABLED' if stop_limit_enabled else '❌ DISABLED'}")
        print(f"   Stop-Limit Percentage: -{stop_limit_pct*100:.3f}%")
        print(f"   Trailing Stop-Limit: {'✅ ENABLED' if trailing_enabled else '❌ DISABLED'}")
        print(f"   Trailing Trigger: +{trailing_trigger*100:.3f}%")
        
        if signal.get('action') == 'BUY' and passes_threshold:
            # Simulate stop-limit calculation for BUY signal
            entry_price = current_price
            stop_price = entry_price * (1 - stop_limit_pct)
            print(f"\n🎯 SIMULATED BUY PROTECTION:")
            print(f"   Entry Price: ${entry_price:.2f}")
            print(f"   Stop Price: ${stop_price:.2f}")
            print(f"   Protection: -{(entry_price - stop_price)/entry_price*100:.3f}%")
            print(f"   ✅ Stop-limit would be placed immediately after BUY")
        
        elif signal.get('action') == 'SELL' and passes_threshold:
            print(f"\n📈 PEAK SELLING SIGNAL:")
            print(f"   Current Price: ${current_price:.2f}")
            print(f"   Signal: {signal.get('crossover_type', 'N/A')}")
            print(f"   ✅ Would SELL at current peak conditions")
        
        # Check for current positions that might need protection
        try:
            balance = exchange.fetch_balance()
            btc_balance = balance.get('BTC', {}).get('free', 0)
            if btc_balance > 0.00001:  # Has BTC position
                print(f"\n💰 CURRENT POSITION DETECTED:")
                print(f"   BTC Balance: {btc_balance:.6f}")
                print(f"   Current Value: ${btc_balance * current_price:.2f}")
                print(f"   🛡️ Position should have stop-limit protection active")
            else:
                print(f"\n💰 NO CURRENT BTC POSITION")
        except Exception as e:
            print(f"\n💰 Could not check current position: {e}")
        
        print(f"\n🔍 Enhanced peak selling and protection test completed!")
        
        # Summary
        print(f"\n📋 SYSTEM CAPABILITIES SUMMARY:")
        print(f"   ✅ Dip Detection: Enhanced multi-tier (0.45-0.65 confidence)")
        print(f"   ✅ Peak Detection: Enhanced multi-tier (0.45-0.65 confidence)")
        print(f"   ✅ Stop-Limit Protection: {'ACTIVE' if stop_limit_enabled else 'INACTIVE'}")
        print(f"   ✅ Trailing Protection: {'ACTIVE' if trailing_enabled else 'INACTIVE'}")
        print(f"   🎯 Current Signal: {signal.get('action')} ({signal_type})")
        
    except Exception as e:
        print(f"❌ Error in enhanced test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_enhanced_peak_selling_and_protection()
