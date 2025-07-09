"""
Multi-Timeframe MA Crossover Detection
Enhanced crossover detection using multiple timeframes for better responsiveness
"""

import pandas as pd
from typing import Dict, List, Optional
from strategies.ma_crossover import fetch_ohlcv

def detect_multi_timeframe_ma_signals(exchange, symbol: str, current_price: float) -> Dict:
    """
    Enhanced MA crossover detection using multiple timeframes:
    - 1-minute MA7/MA25 (fast signals)
    - 5-minute MA7/MA25 (trend confirmation)
    - Combined analysis for better accuracy
    """
    
    signals = {
        '1m': {'action': 'HOLD', 'confidence': 0.0, 'reasons': []},
        '5m': {'action': 'HOLD', 'confidence': 0.0, 'reasons': []},
        'combined': {'action': 'HOLD', 'confidence': 0.0, 'reasons': []}
    }
    
    try:
        # Get data for both timeframes
        df_1m = fetch_ohlcv(exchange, symbol, '1m', 50)
        df_5m = fetch_ohlcv(exchange, symbol, '5m', 50)
        
        # Analyze 1-minute timeframe (fast signals)
        signals['1m'] = _analyze_timeframe_ma(df_1m, current_price, '1m')
        
        # Analyze 5-minute timeframe (trend confirmation)
        signals['5m'] = _analyze_timeframe_ma(df_5m, current_price, '5m')
        
        # Combine signals for final decision
        signals['combined'] = _combine_timeframe_signals(signals['1m'], signals['5m'])
        
        return signals
        
    except Exception as e:
        return {
            '1m': {'action': 'HOLD', 'confidence': 0.0, 'reasons': [f'Error: {e}']},
            '5m': {'action': 'HOLD', 'confidence': 0.0, 'reasons': [f'Error: {e}']},
            'combined': {'action': 'HOLD', 'confidence': 0.0, 'reasons': [f'Multi-timeframe error: {e}']}
        }

def _analyze_timeframe_ma(df: pd.DataFrame, current_price: float, timeframe: str) -> Dict:
    """Analyze MA crossover for a specific timeframe"""
    
    if len(df) < 30:
        return {'action': 'HOLD', 'confidence': 0.0, 'reasons': [f'Insufficient {timeframe} data']}
    
    # Calculate moving averages
    ma_7 = df['close'].rolling(7).mean()
    ma_25 = df['close'].rolling(25).mean()
    
    if len(ma_7) < 2 or len(ma_25) < 2:
        return {'action': 'HOLD', 'confidence': 0.0, 'reasons': [f'Insufficient {timeframe} MA data']}
    
    # Current and previous MA values
    ma7_current = ma_7.iloc[-1]
    ma25_current = ma_25.iloc[-1]
    ma7_previous = ma_7.iloc[-2]
    ma25_previous = ma_25.iloc[-2]
    
    # Crossover detection
    golden_cross = (ma7_previous <= ma25_previous) and (ma7_current > ma25_current)
    death_cross = (ma7_previous >= ma25_previous) and (ma7_current < ma25_current)
    
    # Current trend strength
    ma_spread = abs(ma7_current - ma25_current) / ma25_current * 100
    price_above_ma7 = current_price > ma7_current
    price_above_ma25 = current_price > ma25_current
    
    # Volume analysis
    volume_surge = False
    if 'volume' in df.columns and len(df) >= 10:
        try:
            avg_volume = df['volume'].rolling(10).mean().iloc[-1]
            current_volume = df['volume'].iloc[-1]
            volume_surge = current_volume > (avg_volume * 1.2)
        except:
            pass
    
    # Timeframe-specific confidence adjustments
    base_confidence = 0.65 if timeframe == '1m' else 0.75  # 5m gets higher base confidence
    
    # GOLDEN CROSS ANALYSIS
    if golden_cross:
        confidence = base_confidence
        reasons = [f"🟢 {timeframe} GOLDEN CROSS: MA7 > MA25"]
        
        # Confirmations
        if volume_surge:
            confidence += 0.10
            reasons.append(f"📊 {timeframe} volume surge")
        
        if price_above_ma7 and price_above_ma25:
            confidence += 0.05
            reasons.append(f"📈 Price above both {timeframe} MAs")
        
        if ma_spread > (0.2 if timeframe == '1m' else 0.4):
            confidence += 0.05
            reasons.append(f"📏 Strong {timeframe} spread: {ma_spread:.2f}%")
        
        # Momentum check
        if len(ma_7) >= 3:
            ma7_momentum = (ma7_current - ma_7.iloc[-3]) / ma_7.iloc[-3]
            if ma7_momentum > 0.002:
                confidence += 0.05
                reasons.append(f"🚀 {timeframe} MA7 momentum")
        
        return {
            'action': 'BUY',
            'confidence': min(0.95, confidence),
            'reasons': reasons,
            'ma7': ma7_current,
            'ma25': ma25_current,
            'spread': ma_spread,
            'timeframe': timeframe,
            'crossover_type': 'golden_cross'
        }
    
    # DEATH CROSS ANALYSIS
    elif death_cross:
        confidence = base_confidence
        reasons = [f"🔴 {timeframe} DEATH CROSS: MA7 < MA25"]
        
        # Confirmations
        if volume_surge:
            confidence += 0.10
            reasons.append(f"📊 {timeframe} volume surge")
        
        if not price_above_ma7 and not price_above_ma25:
            confidence += 0.05
            reasons.append(f"📉 Price below both {timeframe} MAs")
        
        if ma_spread > (0.2 if timeframe == '1m' else 0.4):
            confidence += 0.05
            reasons.append(f"📏 Strong {timeframe} spread: {ma_spread:.2f}%")
        
        # Momentum check
        if len(ma_7) >= 3:
            ma7_momentum = (ma7_current - ma_7.iloc[-3]) / ma_7.iloc[-3]
            if ma7_momentum < -0.002:
                confidence += 0.05
                reasons.append(f"📉 {timeframe} MA7 momentum")
        
        return {
            'action': 'SELL',
            'confidence': min(0.95, confidence),
            'reasons': reasons,
            'ma7': ma7_current,
            'ma25': ma25_current,
            'spread': ma_spread,
            'timeframe': timeframe,
            'crossover_type': 'death_cross'
        }
    
    # TREND CONTINUATION SIGNALS
    elif ma7_current > ma25_current and ma_spread > (0.8 if timeframe == '1m' else 1.2):
        if price_above_ma7 and price_above_ma25:
            confidence = 0.60 + (min(ma_spread, 4) / 4 * 0.20)
            reasons = [
                f"📈 {timeframe} bullish trend: {ma_spread:.2f}% spread",
                f"🎯 Price above both {timeframe} MAs"
            ]
            
            if volume_surge:
                confidence += 0.05
                reasons.append(f"📊 {timeframe} volume support")
            
            return {
                'action': 'BUY',
                'confidence': confidence,
                'reasons': reasons,
                'ma7': ma7_current,
                'ma25': ma25_current,
                'spread': ma_spread,
                'timeframe': timeframe,
                'crossover_type': 'bullish_trend'
            }
    
    elif ma7_current < ma25_current and ma_spread > (0.8 if timeframe == '1m' else 1.2):
        if not price_above_ma7 and not price_above_ma25:
            confidence = 0.60 + (min(ma_spread, 4) / 4 * 0.20)
            reasons = [
                f"📉 {timeframe} bearish trend: {ma_spread:.2f}% spread",
                f"🎯 Price below both {timeframe} MAs"
            ]
            
            if volume_surge:
                confidence += 0.05
                reasons.append(f"📊 {timeframe} volume support")
            
            return {
                'action': 'SELL',
                'confidence': confidence,
                'reasons': reasons,
                'ma7': ma7_current,
                'ma25': ma25_current,
                'spread': ma_spread,
                'timeframe': timeframe,
                'crossover_type': 'bearish_trend'
            }
    
    # NO CLEAR SIGNAL
    return {
        'action': 'HOLD',
        'confidence': 0.0,
        'reasons': [
            f"📊 {timeframe}: MA7={ma7_current:.4f}, MA25={ma25_current:.4f}",
            f"📈 Spread: {ma_spread:.2f}% - No clear signal"
        ],
        'ma7': ma7_current,
        'ma25': ma25_current,
        'spread': ma_spread,
        'timeframe': timeframe,
        'crossover_type': 'no_signal'
    }

def _combine_timeframe_signals(signal_1m: Dict, signal_5m: Dict) -> Dict:
    """Combine signals from different timeframes for final decision"""
    
    # Both timeframes agree on direction
    if signal_1m['action'] == signal_5m['action'] and signal_1m['action'] != 'HOLD':
        # Strong agreement - boost confidence
        combined_confidence = (signal_1m['confidence'] + signal_5m['confidence']) / 2
        combined_confidence = min(0.95, combined_confidence + 0.10)  # Boost for agreement
        
        reasons = [
            f"🎯 MULTI-TIMEFRAME AGREEMENT: {signal_1m['action']}",
            f"📈 1m confidence: {signal_1m['confidence']:.3f}",
            f"📈 5m confidence: {signal_5m['confidence']:.3f}",
            f"🚀 Combined confidence: {combined_confidence:.3f}"
        ]
        
        return {
            'action': signal_1m['action'],
            'confidence': combined_confidence,
            'reasons': reasons,
            'signal_1m': signal_1m,
            'signal_5m': signal_5m,
            'agreement': True
        }
    
    # Timeframes disagree - use 5m as tie-breaker (more reliable)
    elif signal_1m['action'] != signal_5m['action']:
        # 5m signal takes precedence, but with reduced confidence
        primary_signal = signal_5m if signal_5m['action'] != 'HOLD' else signal_1m
        
        # Reduce confidence due to disagreement
        combined_confidence = primary_signal['confidence'] * 0.7
        
        reasons = [
            f"⚠️ TIMEFRAME DISAGREEMENT: Using {primary_signal.get('timeframe', '5m')} signal",
            f"📊 1m: {signal_1m['action']} ({signal_1m['confidence']:.3f})",
            f"📊 5m: {signal_5m['action']} ({signal_5m['confidence']:.3f})",
            f"🎯 Final: {primary_signal['action']} ({combined_confidence:.3f})"
        ]
        
        return {
            'action': primary_signal['action'],
            'confidence': combined_confidence,
            'reasons': reasons,
            'signal_1m': signal_1m,
            'signal_5m': signal_5m,
            'agreement': False
        }
    
    # Both HOLD or low confidence
    else:
        # Take the higher confidence signal if any
        if signal_1m['confidence'] > signal_5m['confidence']:
            primary_signal = signal_1m
        else:
            primary_signal = signal_5m
        
        reasons = [
            "📊 MULTI-TIMEFRAME ANALYSIS: No strong signals",
            f"📈 1m: {signal_1m['action']} ({signal_1m['confidence']:.3f})",
            f"📈 5m: {signal_5m['action']} ({signal_5m['confidence']:.3f})",
            "⏳ Waiting for clearer multi-timeframe alignment"
        ]
        
        return {
            'action': 'HOLD',
            'confidence': max(signal_1m['confidence'], signal_5m['confidence']) * 0.8,
            'reasons': reasons,
            'signal_1m': signal_1m,
            'signal_5m': signal_5m,
            'agreement': False
        }
