# =============================================================================
# 5M+1M PRIORITY SYSTEM FUNCTIONS
# =============================================================================

def should_hold_position(exchange, symbol, entry_price, entry_time, current_price, current_time):
    """
    🎯 ENHANCED 5M+1M PRIORITY SYSTEM: Optimized Exit Strategy
    
    TWO-LAYER EXIT OPTIMIZATION:
    - Layer 1: Quick Exit at 0.8% (captures 89% of 0.9% peaks)
    - Layer 2: Peak Detection for larger moves (1.0%+ with trailing stop)
    
    This ensures we capture small profitable moves while still allowing
    larger trends to develop through the peak detection system.
    
    Returns: {'action': 'HOLD'/'SELL', 'reason': str, 'confidence': float}
    """
    import time
    from datetime import datetime, timedelta
    
    # Calculate hold duration
    if isinstance(entry_time, (int, float)):
        entry_dt = datetime.fromtimestamp(entry_time)
    else:
        entry_dt = entry_time
    
    if isinstance(current_time, (int, float)):
        current_dt = datetime.fromtimestamp(current_time)
    else:
        current_dt = current_time
    
    hold_minutes = (current_dt - entry_dt).total_seconds() / 60
    
    # Calculate profit/loss
    profit_loss_pct = ((current_price - entry_price) / entry_price) * 100
    
    print(f"📊 HOLD ANALYSIS: {hold_minutes:.1f}min, P/L: {profit_loss_pct:+.2f}%")
    
    # STAGE 1: 0-5 minutes - Aggressive profit taking for day trading
    if hold_minutes <= 5:
        # OPTIMIZED: 0.5% quick exit for rapid scalping
        if profit_loss_pct >= 0.5:  # Updated to 0.5% for rapid scalping
            return {
                'action': 'SELL',
                'reason': f'Quick profit target hit: +{profit_loss_pct:.2f}% (rapid scalping)',
                'confidence': 0.9
            }
        elif profit_loss_pct <= -1.5:  # Slightly tighter stop loss
            return {
                'action': 'SELL', 
                'reason': f'Quick stop loss: {profit_loss_pct:.2f}%',
                'confidence': 0.8
            }
        else:
            return {
                'action': 'HOLD',
                'reason': f'Early stage hold: {hold_minutes:.1f}min, {profit_loss_pct:+.2f}%',
                'confidence': 0.7
            }
    
    # STAGE 2: 5-15 minutes - Tighter momentum-based decisions
    elif hold_minutes <= 15:
        # Get recent momentum
        momentum = calculate_recent_momentum(exchange, symbol)
        
        if profit_loss_pct >= 0.5:  # Updated to 0.5% for rapid scalping
            if momentum['trend'] == 'BULLISH' and momentum['strength'] > 0.7:  # Higher momentum required
                return {
                    'action': 'HOLD',
                    'reason': f'Strong bullish momentum: +{profit_loss_pct:.2f}%, {momentum["strength"]:.2f}',
                    'confidence': 0.8
                }
            else:
                return {
                    'action': 'SELL',
                    'reason': f'Profit secured, weak momentum: +{profit_loss_pct:.2f}%',
                    'confidence': 0.85
                }
        elif profit_loss_pct <= -1.2:  # Tighter stop loss
            return {
                'action': 'SELL',
                'reason': f'Mid-stage stop loss: {profit_loss_pct:.2f}%',
                'confidence': 0.8
            }
        else:
            return {
                'action': 'HOLD',
                'reason': f'Mid-stage momentum hold: {momentum["trend"]} {momentum["strength"]:.2f}',
                'confidence': 0.6
            }
    
    # STAGE 3: 15+ minutes - Force close with small profits/losses
    else:
        if profit_loss_pct >= 0.5:
            return {
                'action': 'SELL',
                'reason': f'Extended hold profit: +{profit_loss_pct:.2f}% after {hold_minutes:.1f}min',
                'confidence': 0.9
            }
        elif profit_loss_pct <= -1.0:
            return {
                'action': 'SELL',
                'reason': f'Extended hold loss limit: {profit_loss_pct:.2f}% after {hold_minutes:.1f}min',
                'confidence': 0.9
            }
        else:
            return {
                'action': 'SELL',
                'reason': f'Extended hold timeout: {hold_minutes:.1f}min, {profit_loss_pct:+.2f}%',
                'confidence': 0.8
            }

def calculate_recent_momentum(exchange, symbol, lookback_minutes=10):
    """
    Calculate recent price momentum for hold decisions
    Returns: {'trend': str, 'strength': float, 'volatility': float}
    """
    try:
        # Get recent 1m candles
        ohlcv = exchange.fetch_ohlcv(symbol, '1m', limit=lookback_minutes + 5)
        if len(ohlcv) < lookback_minutes:
            return {'trend': 'NEUTRAL', 'strength': 0.5, 'volatility': 0.0}
        
        # Extract recent prices
        recent_closes = [candle[4] for candle in ohlcv[-lookback_minutes:]]
        
        # Calculate trend strength
        price_start = recent_closes[0]
        price_end = recent_closes[-1]
        total_change = (price_end - price_start) / price_start
        
        # Calculate volatility
        price_changes = []
        for i in range(1, len(recent_closes)):
            change = (recent_closes[i] - recent_closes[i-1]) / recent_closes[i-1]
            price_changes.append(abs(change))
        
        volatility = sum(price_changes) / len(price_changes) if price_changes else 0
        
        # Determine trend and strength
        if total_change > 0.002:  # 0.2% gain
            trend = 'BULLISH'
            strength = min(1.0, abs(total_change) * 50)  # Scale to 0-1
        elif total_change < -0.002:  # 0.2% loss
            trend = 'BEARISH'
            strength = min(1.0, abs(total_change) * 50)
        else:
            trend = 'NEUTRAL'
            strength = 0.5
        
        return {
            'trend': trend,
            'strength': strength,
            'volatility': volatility
        }
        
    except Exception as e:
        print(f"⚠️ Momentum calculation error: {e}")
        return {'trend': 'NEUTRAL', 'strength': 0.5, 'volatility': 0.0}

def detect_5m_1m_agreement(ma_signal):
    """
    Detect when 5m and 1m timeframes agree for immediate execution
    Returns: {'agreement': bool, 'confidence': float, 'reason': str}
    """
    try:
        # Check if we have individual timeframe signals
        if 'signal_1m' not in ma_signal or 'signal_5m' not in ma_signal:
            return {'agreement': False, 'confidence': 0.0, 'reason': 'Missing timeframe data'}
        
        signal_1m = ma_signal['signal_1m']
        signal_5m = ma_signal['signal_5m']
        
        # Both must have same action
        if signal_1m['action'] != signal_5m['action']:
            return {'agreement': False, 'confidence': 0.0, 'reason': 'Different actions'}
        
        # Both must have reasonable confidence (≥40%)
        if signal_1m['confidence'] < 0.4 or signal_5m['confidence'] < 0.4:
            return {'agreement': False, 'confidence': 0.0, 'reason': 'Low individual confidence'}
        
        # Calculate combined confidence
        combined_confidence = (signal_1m['confidence'] + signal_5m['confidence']) / 2
        
        # Boost if both are strong
        if signal_1m['confidence'] >= 0.7 and signal_5m['confidence'] >= 0.7:
            combined_confidence = min(0.95, combined_confidence * 1.2)
        
        # Agreement threshold: combined confidence ≥ 60%
        agreement = combined_confidence >= 0.6
        
        if agreement:
            print(f"🎯 5M+1M AGREEMENT DETECTED!")
            print(f"   📊 1m: {signal_1m['action']} ({signal_1m['confidence']:.3f})")
            print(f"   📊 5m: {signal_5m['action']} ({signal_5m['confidence']:.3f})")
            print(f"   ✅ Combined: {combined_confidence:.3f}")
        
        return {
            'agreement': agreement,
            'confidence': combined_confidence,
            'reason': f"1m+5m {signal_1m['action']} agreement" if agreement else "Insufficient agreement"
        }
        
    except Exception as e:
        print(f"⚠️ 5m+1m agreement detection error: {e}")
        return {'agreement': False, 'confidence': 0.0, 'reason': f'Error: {e}'}

def detect_peak_and_trailing_exit(exchange, symbol, entry_price, entry_time, current_price, current_time, 
                                   peak_price=None, last_check_time=None):
    """
    Advanced peak detection with trailing stop for optimal exits
    Returns: {'action': 'HOLD'/'SELL', 'reason': str, 'confidence': float, 'peak_price': float}
    """
    import time
    from datetime import datetime, timedelta
    
    # Calculate current profit
    profit_pct = ((current_price - entry_price) / entry_price) * 100
    
    # Initialize or update peak tracking
    if peak_price is None or current_price > peak_price:
        peak_price = current_price
        peak_profit_pct = ((peak_price - entry_price) / entry_price) * 100
        print(f"🎯 NEW PEAK DETECTED: ${peak_price:.2f} (+{peak_profit_pct:.2f}%)")
    else:
        peak_profit_pct = ((peak_price - entry_price) / entry_price) * 100
    
    # Calculate drawdown from peak
    drawdown_from_peak = ((peak_price - current_price) / peak_price) * 100
    
    print(f"📈 PEAK ANALYSIS: Peak=${peak_price:.2f} (+{peak_profit_pct:.2f}%), "
          f"Current=${current_price:.2f} (+{profit_pct:.2f}%), "
          f"Drawdown={drawdown_from_peak:.2f}%")
    
    # ENHANCED COORDINATION: Quick exit at 0.8% works with peak detection for larger moves
    # Peak detection now focuses on 1.0%+ movements while quick exit handles 0.8-0.9%
    
    # AGGRESSIVE TRAILING STOP: Activate earlier at 0.6% profit
    if peak_profit_pct >= 0.6:  
        if drawdown_from_peak >= 0.2:  # Tight 0.2% drop from peak
            return {
                'action': 'SELL',
                'reason': f'Trailing stop: {drawdown_from_peak:.2f}% drop from peak ${peak_price:.2f} (peak detection)',
                'confidence': 0.9,
                'peak_price': peak_price
            }
    
    # PROFIT PROTECTION: Secure gains if we've reached good profit levels
    if profit_pct >= 1.2:
        if drawdown_from_peak >= 0.2:  # Even tighter for higher profits
            return {
                'action': 'SELL', 
                'reason': f'Profit protection: {profit_pct:.2f}% profit, {drawdown_from_peak:.2f}% from peak',
                'confidence': 0.85,
                'peak_price': peak_price
            }
    
    # Continue holding if conditions aren't met
    return {
        'action': 'HOLD',
        'reason': f'Peak tracking: Peak ${peak_price:.2f} (+{peak_profit_pct:.2f}%), monitoring...',
        'confidence': 0.7,
        'peak_price': peak_price
    }
