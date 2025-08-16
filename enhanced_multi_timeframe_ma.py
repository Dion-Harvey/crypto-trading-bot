"""
Enhanced Multi-Timeframe MA Strategy
Prioritizes trend continuation and quick entries during sustained bullish/bearish trends
"""
import pandas as pd
from typing import Dict, List, Optional
from strategies.ma_crossover import fetch_ohlcv

def detect_enhanced_multi_timeframe_ma_signals(exchange, symbol: str, current_price: float) -> Dict:
    """
    🎯 ENHANCED STRATEGY: Trend Continuation + Quick Entry Priority
    
    1. Detects sustained bullish/bearish trends across timeframes
    2. Prioritizes 5m then 1m for quick entry signals
    3. Generates BUY signals during uptrends (not just crossovers)
    4. Calculates progressive sell targets for trend continuation
    """
    signals = {
        '1m': {'action': 'HOLD', 'confidence': 0.0, 'reasons': []},
        '5m': {'action': 'HOLD', 'confidence': 0.0, 'reasons': []},
        '15m': {'action': 'HOLD', 'confidence': 0.0, 'reasons': []},
        '30m': {'action': 'HOLD', 'confidence': 0.0, 'reasons': []},
        '1h': {'action': 'HOLD', 'confidence': 0.0, 'reasons': []},
        '2h': {'action': 'HOLD', 'confidence': 0.0, 'reasons': []},
        'combined': {'action': 'HOLD', 'confidence': 0.0, 'reasons': []},
        'trend_analysis': {},
        'sell_targets': []
    }
    
    try:
        # Get data for all timeframes
        timeframe_data = {}
        timeframe_data['1m'] = fetch_ohlcv(exchange, symbol, '1m', 50)
        timeframe_data['5m'] = fetch_ohlcv(exchange, symbol, '5m', 50)
        timeframe_data['15m'] = fetch_ohlcv(exchange, symbol, '15m', 50)
        timeframe_data['30m'] = fetch_ohlcv(exchange, symbol, '30m', 50)
        timeframe_data['1h'] = fetch_ohlcv(exchange, symbol, '1h', 50)
        timeframe_data['2h'] = fetch_ohlcv(exchange, symbol, '2h', 50)
        
        # Analyze each timeframe for trend strength and signals
        for tf in ['1m', '5m', '15m', '30m', '1h', '2h']:
            signals[tf] = _analyze_enhanced_timeframe_ma(timeframe_data[tf], current_price, tf)
        
        # 🎯 ENHANCED TREND ANALYSIS - Detect sustained trends
        trend_analysis = _analyze_multi_timeframe_trend(signals, current_price)
        signals['trend_analysis'] = trend_analysis
        
        # 🎯 PRIORITY LOGIC: 5m > 1m for quick entries during trends
        combined_signal = _generate_enhanced_combined_signal(signals, trend_analysis)
        signals['combined'] = combined_signal
        
        # 🎯 PROGRESSIVE SELL TARGETS for trend continuation
        if trend_analysis.get('overall_trend') == 'BULLISH':
            signals['sell_targets'] = _calculate_progressive_sell_targets(current_price, trend_analysis)
        
        # ADD INDIVIDUAL 5M+1M SIGNALS FOR PRIORITY SYSTEM
        signals['signal_1m'] = signals['1m']
        signals['signal_5m'] = signals['5m']
        
        return signals
        
    except Exception as e:
        return {
            '1m': {'action': 'HOLD', 'confidence': 0.0, 'reasons': [f'Error: {e}']},
            '5m': {'action': 'HOLD', 'confidence': 0.0, 'reasons': [f'Error: {e}']},
            '15m': {'action': 'HOLD', 'confidence': 0.0, 'reasons': [f'Error: {e}']},
            '30m': {'action': 'HOLD', 'confidence': 0.0, 'reasons': [f'Error: {e}']},
            '1h': {'action': 'HOLD', 'confidence': 0.0, 'reasons': [f'Error: {e}']},
            '2h': {'action': 'HOLD', 'confidence': 0.0, 'reasons': [f'Error: {e}']},
            'combined': {'action': 'HOLD', 'confidence': 0.0, 'reasons': [f'Enhanced MA error: {e}']},
            'trend_analysis': {},
            'sell_targets': []
        }

def _analyze_enhanced_timeframe_ma(df: pd.DataFrame, current_price: float, timeframe: str) -> Dict:
    """Enhanced timeframe analysis with trend continuation focus"""
    if len(df) < 30:
        return {'action': 'HOLD', 'confidence': 0.0, 'reasons': [f'Insufficient {timeframe} data']}
    
    # Calculate moving averages
    ma_7 = df['close'].rolling(7).mean()
    ma_25 = df['close'].rolling(25).mean()
    
    if len(ma_7) < 3 or len(ma_25) < 3:
        return {'action': 'HOLD', 'confidence': 0.0, 'reasons': [f'Insufficient {timeframe} MA data']}
    
    # Current and historical MA values
    ma7_current = ma_7.iloc[-1]
    ma25_current = ma_25.iloc[-1]
    ma7_previous = ma_7.iloc[-2]
    ma25_previous = ma_25.iloc[-2]
    ma7_3_periods_ago = ma_7.iloc[-3]
    ma25_3_periods_ago = ma_25.iloc[-3]
    
    # Crossover detection
    golden_cross = (ma7_previous <= ma25_previous) and (ma7_current > ma25_current)
    death_cross = (ma7_previous >= ma25_previous) and (ma7_current < ma25_current)
    
    # 🎯 TREND STRENGTH ANALYSIS
    ma_spread = abs(ma7_current - ma25_current) / ma25_current * 100
    trend_direction = 'BULLISH' if ma7_current > ma25_current else 'BEARISH'
    
    # Trend momentum (how fast MAs are diverging/converging)
    spread_previous = abs(ma7_previous - ma25_previous) / ma25_previous * 100
    spread_momentum = ma_spread - spread_previous
    
    # Price position relative to MAs
    price_above_ma7 = current_price > ma7_current
    price_above_ma25 = current_price > ma25_current
    price_above_both = price_above_ma7 and price_above_ma25
    price_below_both = not price_above_ma7 and not price_above_ma25
    
    # Trend consistency (how long has this trend been active?)
    trend_consistency = _calculate_trend_consistency(ma_7, ma_25)
    
    # Volume analysis
    volume_support = _analyze_volume_support(df)
    
    # 🚀 ENHANCED SIGNAL LOGIC
    
    # 1. ABSOLUTE PRIORITY: Fresh crossovers
    if golden_cross:
        return {
            'action': 'BUY',
            'confidence': 0.95,
            'reasons': [
                f"🟢 {timeframe} GOLDEN CROSS: MA7 crossed above MA25",
                f"Fresh crossover with {ma_spread:.2f}% spread",
                f"Volume support: {volume_support['strength']}"
            ],
            'signal_type': 'golden_cross',
            'ma7': ma7_current,
            'ma25': ma25_current,
            'spread': ma_spread,
            'trend_direction': trend_direction,
            'trend_consistency': trend_consistency,
            'timeframe': timeframe
        }
    
    elif death_cross:
        return {
            'action': 'SELL',
            'confidence': 0.95,
            'reasons': [
                f"🔴 {timeframe} DEATH CROSS: MA7 crossed below MA25",
                f"Fresh crossover with {ma_spread:.2f}% spread",
                f"Volume support: {volume_support['strength']}"
            ],
            'signal_type': 'death_cross',
            'ma7': ma7_current,
            'ma25': ma25_current,
            'spread': ma_spread,
            'trend_direction': trend_direction,
            'trend_consistency': trend_consistency,
            'timeframe': timeframe
        }
    
    # 2. 🎯 TREND CONTINUATION SIGNALS (The Key Enhancement!)
    elif trend_direction == 'BULLISH' and ma_spread > (0.3 if timeframe in ['1m', '5m'] else 0.5):
        
        # Strong bullish trend continuation
        if (price_above_both and spread_momentum > 0 and trend_consistency >= 3):
            confidence = 0.75 + min(ma_spread / 5.0, 0.15)  # Higher spread = higher confidence
            
            # Boost confidence for shorter timeframes (faster entry)
            if timeframe == '5m':
                confidence += 0.10
            elif timeframe == '1m':
                confidence += 0.05
            
            # Volume boost
            if volume_support['is_strong']:
                confidence += 0.05
            
            return {
                'action': 'BUY',
                'confidence': min(confidence, 0.90),
                'reasons': [
                    f"📈 {timeframe} STRONG BULLISH TREND: MA spread {ma_spread:.2f}%",
                    f"🎯 Trend consistency: {trend_consistency} periods",
                    f"📊 Price above both MAs, momentum: {spread_momentum:+.3f}%",
                    f"🔊 Volume: {volume_support['strength']}"
                ],
                'signal_type': 'bullish_trend_continuation',
                'ma7': ma7_current,
                'ma25': ma25_current,
                'spread': ma_spread,
                'trend_direction': trend_direction,
                'trend_consistency': trend_consistency,
                'timeframe': timeframe
            }
        
        # Moderate bullish trend
        elif price_above_both and trend_consistency >= 2:
            confidence = 0.60 + min(ma_spread / 8.0, 0.10)
            
            return {
                'action': 'BUY',
                'confidence': confidence,
                'reasons': [
                    f"📈 {timeframe} BULLISH TREND: MA spread {ma_spread:.2f}%",
                    f"🎯 Moderate trend strength: {trend_consistency} periods",
                    f"📊 Price positioned above MAs"
                ],
                'signal_type': 'bullish_trend_moderate',
                'ma7': ma7_current,
                'ma25': ma25_current,
                'spread': ma_spread,
                'trend_direction': trend_direction,
                'trend_consistency': trend_consistency,
                'timeframe': timeframe
            }
    
    # 3. BEARISH TREND CONTINUATION
    elif trend_direction == 'BEARISH' and ma_spread > (0.3 if timeframe in ['1m', '5m'] else 0.5):
        
        if (price_below_both and spread_momentum > 0 and trend_consistency >= 3):
            confidence = 0.75 + min(ma_spread / 5.0, 0.15)
            
            if timeframe == '5m':
                confidence += 0.10
            elif timeframe == '1m':
                confidence += 0.05
            
            if volume_support['is_strong']:
                confidence += 0.05
            
            return {
                'action': 'SELL',
                'confidence': min(confidence, 0.90),
                'reasons': [
                    f"📉 {timeframe} STRONG BEARISH TREND: MA spread {ma_spread:.2f}%",
                    f"🎯 Trend consistency: {trend_consistency} periods",
                    f"📊 Price below both MAs, momentum: {spread_momentum:+.3f}%"
                ],
                'signal_type': 'bearish_trend_continuation',
                'ma7': ma7_current,
                'ma25': ma25_current,
                'spread': ma_spread,
                'trend_direction': trend_direction,
                'trend_consistency': trend_consistency,
                'timeframe': timeframe
            }
    
    # 4. NO CLEAR SIGNAL
    return {
        'action': 'HOLD',
        'confidence': 0.0,
        'reasons': [
            f"📊 {timeframe}: MA7={ma7_current:.2f}, MA25={ma25_current:.2f}",
            f"📈 {trend_direction} trend, spread: {ma_spread:.2f}%",
            f"🎯 Trend consistency: {trend_consistency} periods"
        ],
        'signal_type': 'no_signal',
        'ma7': ma7_current,
        'ma25': ma25_current,
        'spread': ma_spread,
        'trend_direction': trend_direction,
        'trend_consistency': trend_consistency,
        'timeframe': timeframe
    }

def _calculate_trend_consistency(ma_7: pd.Series, ma_25: pd.Series) -> int:
    """Calculate how many consecutive periods the trend has been consistent"""
    consistency = 0
    current_trend = ma_7.iloc[-1] > ma_25.iloc[-1]
    
    for i in range(2, min(len(ma_7), 10)):  # Check up to 10 periods back
        past_trend = ma_7.iloc[-i] > ma_25.iloc[-i]
        if past_trend == current_trend:
            consistency += 1
        else:
            break
    
    return consistency

def _analyze_volume_support(df: pd.DataFrame) -> Dict:
    """Analyze volume support for the current move"""
    if 'volume' not in df.columns or len(df) < 10:
        return {'strength': 'Unknown', 'is_strong': False}
    
    try:
        recent_volume = df['volume'].iloc[-5:].mean()
        avg_volume = df['volume'].iloc[-20:].mean()
        volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 1.0
        
        if volume_ratio > 1.5:
            return {'strength': 'Strong', 'is_strong': True, 'ratio': volume_ratio}
        elif volume_ratio > 1.2:
            return {'strength': 'Moderate', 'is_strong': True, 'ratio': volume_ratio}
        else:
            return {'strength': 'Weak', 'is_strong': False, 'ratio': volume_ratio}
    except:
        return {'strength': 'Unknown', 'is_strong': False}

def _analyze_multi_timeframe_trend(signals: Dict, current_price: float) -> Dict:
    """🎯 ENHANCED: Analyze overall trend across all timeframes"""
    
    timeframes = ['1m', '5m', '15m', '30m', '1h', '2h']
    bullish_count = 0
    bearish_count = 0
    trend_strengths = []
    
    # Count trend directions and strengths
    for tf in timeframes:
        signal = signals.get(tf, {})
        trend_dir = signal.get('trend_direction')
        spread = signal.get('spread', 0)
        consistency = signal.get('trend_consistency', 0)
        
        if trend_dir == 'BULLISH':
            bullish_count += 1
            trend_strengths.append(spread + consistency * 0.1)
        elif trend_dir == 'BEARISH':
            bearish_count += 1
            trend_strengths.append(-(spread + consistency * 0.1))
    
    # Determine overall trend
    total_timeframes = len(timeframes)
    bullish_pct = bullish_count / total_timeframes
    bearish_pct = bearish_count / total_timeframes
    
    if bullish_pct >= 0.67:  # 67% or more bullish
        overall_trend = 'BULLISH'
        trend_strength = 'STRONG' if bullish_pct >= 0.83 else 'MODERATE'
    elif bearish_pct >= 0.67:  # 67% or more bearish
        overall_trend = 'BEARISH'
        trend_strength = 'STRONG' if bearish_pct >= 0.83 else 'MODERATE'
    else:
        overall_trend = 'MIXED'
        trend_strength = 'WEAK'
    
    # Calculate average trend strength
    avg_strength = sum(trend_strengths) / len(trend_strengths) if trend_strengths else 0
    
    return {
        'overall_trend': overall_trend,
        'trend_strength': trend_strength,
        'bullish_timeframes': bullish_count,
        'bearish_timeframes': bearish_count,
        'bullish_percentage': bullish_pct * 100,
        'bearish_percentage': bearish_pct * 100,
        'average_strength': avg_strength,
        'consensus_level': max(bullish_pct, bearish_pct) * 100
    }

def _generate_enhanced_combined_signal(signals: Dict, trend_analysis: Dict) -> Dict:
    """🎯 ENHANCED PRIORITY LOGIC: 5m > 1m for quick entries during trends"""
    
    # Priority order: 5m > 1m > 30m > 1h > 15m > 2h
    priority_order = ['5m', '1m', '30m', '1h', '15m', '2h']
    
    overall_trend = trend_analysis.get('overall_trend', 'MIXED')
    trend_strength = trend_analysis.get('trend_strength', 'WEAK')
    consensus = trend_analysis.get('consensus_level', 0)
    
    # 🎯 CASE 1: Strong trend consensus - prioritize quick entry timeframes
    if overall_trend in ['BULLISH', 'BEARISH'] and consensus >= 67:
        
        # Look for any actionable signal in priority order
        for tf in priority_order:
            signal = signals.get(tf, {})
            action = signal.get('action', 'HOLD')
            confidence = signal.get('confidence', 0)
            signal_type = signal.get('signal_type', '')
            
            # Accept any BUY/SELL signal that aligns with trend
            if action != 'HOLD' and confidence >= 0.5:
                if (overall_trend == 'BULLISH' and action == 'BUY') or \
                   (overall_trend == 'BEARISH' and action == 'SELL'):
                    
                    # Boost confidence for trend alignment
                    enhanced_confidence = min(confidence + 0.15, 0.95)
                    
                    return {
                        'action': action,
                        'confidence': enhanced_confidence,
                        'reasons': [
                            f"🎯 {tf} PRIORITY SIGNAL: {action} during {overall_trend} trend",
                            f"📊 Trend consensus: {consensus:.1f}% ({trend_analysis['bullish_timeframes']}/{trend_analysis['bearish_timeframes']})",
                            f"⚡ Quick entry priority: {tf} timeframe",
                            f"🔄 Signal type: {signal_type}"
                        ] + signal.get('reasons', []),
                        'priority_timeframe': tf,
                        'trend_aligned': True,
                        'original_confidence': confidence,
                        'consensus_level': consensus,
                        'agreement': True
                    }
        
        # 🎯 CASE 2: Strong trend but no actionable signals - suggest trend continuation
        if overall_trend == 'BULLISH' and trend_strength == 'STRONG':
            return {
                'action': 'BUY',
                'confidence': 0.65,
                'reasons': [
                    f"📈 STRONG BULLISH TREND: {consensus:.1f}% timeframe consensus",
                    f"🎯 Trend continuation opportunity",
                    f"📊 {trend_analysis['bullish_timeframes']}/6 timeframes bullish",
                    "⚡ No fresh crossovers but sustained uptrend detected"
                ],
                'priority_timeframe': '5m',
                'trend_aligned': True,
                'signal_type': 'trend_continuation',
                'consensus_level': consensus,
                'agreement': True
            }
        
        elif overall_trend == 'BEARISH' and trend_strength == 'STRONG':
            return {
                'action': 'SELL',
                'confidence': 0.65,
                'reasons': [
                    f"📉 STRONG BEARISH TREND: {consensus:.1f}% timeframe consensus",
                    f"🎯 Trend continuation opportunity", 
                    f"📊 {trend_analysis['bearish_timeframes']}/6 timeframes bearish",
                    "⚡ No fresh crossovers but sustained downtrend detected"
                ],
                'priority_timeframe': '5m',
                'trend_aligned': True,
                'signal_type': 'trend_continuation',
                'consensus_level': consensus,
                'agreement': True
            }
    
    # 🎯 CASE 3: Mixed signals or weak trend - look for strong individual signals
    strongest_signal = None
    highest_confidence = 0
    
    for tf in priority_order:
        signal = signals.get(tf, {})
        confidence = signal.get('confidence', 0)
        
        if confidence > highest_confidence and confidence >= 0.7:
            highest_confidence = confidence
            strongest_signal = signal.copy()
            strongest_signal['priority_timeframe'] = tf
    
    if strongest_signal:
        strongest_signal['reasons'] = [
            f"🏆 Strongest individual signal: {strongest_signal['priority_timeframe']} ({highest_confidence:.3f})",
            f"📊 Mixed trend environment: {consensus:.1f}% consensus"
        ] + strongest_signal.get('reasons', [])
        strongest_signal['agreement'] = False
        strongest_signal['consensus_level'] = consensus
        return strongest_signal
    
    # 🎯 CASE 4: No actionable signals
    return {
        'action': 'HOLD',
        'confidence': 0.0,
        'reasons': [
            f"⏸️ No actionable signals detected",
            f"📊 Trend: {overall_trend} ({consensus:.1f}% consensus)",
            f"🎯 Awaiting stronger signals or trend clarity",
            f"📈 Bullish TF: {trend_analysis['bullish_timeframes']}, Bearish TF: {trend_analysis['bearish_timeframes']}"
        ],
        'priority_timeframe': None,
        'trend_aligned': False,
        'consensus_level': consensus,
        'agreement': False
    }

def _calculate_progressive_sell_targets(current_price: float, trend_analysis: Dict) -> List[Dict]:
    """🎯 Calculate progressive sell targets for trend continuation"""
    
    if trend_analysis.get('overall_trend') != 'BULLISH':
        return []
    
    strength_multiplier = 1.5 if trend_analysis.get('trend_strength') == 'STRONG' else 1.0
    base_targets = [0.02, 0.04, 0.06, 0.10]  # 2%, 4%, 6%, 10%
    
    sell_targets = []
    for i, target_pct in enumerate(base_targets):
        adjusted_target = target_pct * strength_multiplier
        target_price = current_price * (1 + adjusted_target)
        
        sell_targets.append({
            'level': i + 1,
            'target_price': target_price,
            'target_percentage': adjusted_target * 100,
            'suggested_sell_amount': 25 if i < 3 else 25,  # 25% each level
            'reasoning': f"Level {i+1}: {adjusted_target*100:.1f}% gain target"
        })
    
    return sell_targets

# Compatibility function to replace the original
def detect_multi_timeframe_ma_signals(exchange, symbol: str, current_price: float) -> Dict:
    """Compatibility wrapper for the enhanced strategy"""
    enhanced_signals = detect_enhanced_multi_timeframe_ma_signals(exchange, symbol, current_price)
    
    # Return in original format but with enhanced logic
    return {
        '1m': enhanced_signals['1m'],
        '5m': enhanced_signals['5m'],
        '15m': enhanced_signals['15m'],
        '30m': enhanced_signals['30m'],
        '1h': enhanced_signals['1h'],
        '2h': enhanced_signals['2h'],
        'combined': enhanced_signals['combined']
    }
