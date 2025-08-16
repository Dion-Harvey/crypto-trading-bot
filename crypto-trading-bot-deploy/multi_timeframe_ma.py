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
        '15m': {'action': 'HOLD', 'confidence': 0.0, 'reasons': []},
        '30m': {'action': 'HOLD', 'confidence': 0.0, 'reasons': []},
        '1h': {'action': 'HOLD', 'confidence': 0.0, 'reasons': []},
        '2h': {'action': 'HOLD', 'confidence': 0.0, 'reasons': []},
        'combined': {'action': 'HOLD', 'confidence': 0.0, 'reasons': []}
    }

    try:

        # Get data for all timeframes
        df_1m = fetch_ohlcv(exchange, symbol, '1m', 50)
        df_5m = fetch_ohlcv(exchange, symbol, '5m', 50)
        df_15m = fetch_ohlcv(exchange, symbol, '15m', 50)
        df_30m = fetch_ohlcv(exchange, symbol, '30m', 50)
        df_1h = fetch_ohlcv(exchange, symbol, '1h', 50)
        df_2h = fetch_ohlcv(exchange, symbol, '2h', 50)

        # Analyze each timeframe
        signals['1m'] = _analyze_timeframe_ma(df_1m, current_price, '1m')
        signals['5m'] = _analyze_timeframe_ma(df_5m, current_price, '5m')
        signals['15m'] = _analyze_timeframe_ma(df_15m, current_price, '15m')
        signals['30m'] = _analyze_timeframe_ma(df_30m, current_price, '30m')
        signals['1h'] = _analyze_timeframe_ma(df_1h, current_price, '1h')
        signals['2h'] = _analyze_timeframe_ma(df_2h, current_price, '2h')

        # Combine signals for final decision (longest actionable timeframe takes priority)
        signals['combined'] = _combine_multi_timeframe_signals([
            signals['1m'], signals['5m'], signals['15m'], signals['30m'], signals['1h'], signals['2h']
        ])

        return signals

    except Exception as e:
        return {
            '1m': {'action': 'HOLD', 'confidence': 0.0, 'reasons': [f'Error: {e}']},
            '5m': {'action': 'HOLD', 'confidence': 0.0, 'reasons': [f'Error: {e}']},
            '15m': {'action': 'HOLD', 'confidence': 0.0, 'reasons': [f'Error: {e}']},
            '30m': {'action': 'HOLD', 'confidence': 0.0, 'reasons': [f'Error: {e}']},
            '1h': {'action': 'HOLD', 'confidence': 0.0, 'reasons': [f'Error: {e}']},
            '2h': {'action': 'HOLD', 'confidence': 0.0, 'reasons': [f'Error: {e}']},
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

    # GOLDEN CROSS ANALYSIS (ABSOLUTE PRIORITY)
    if golden_cross:
        return {
            'action': 'BUY',
            'confidence': 1.0,
            'reasons': [
                f"🟢 {timeframe} GOLDEN CROSS: MA7 crossed above MA25",
                f"MA7 prev: {ma7_previous:.4f} → {ma7_current:.4f}",
                f"MA25 prev: {ma25_previous:.4f} → {ma25_current:.4f}",
                f"Spread: {ma_spread:.2f}%"
            ],
            'ma7': ma7_current,
            'ma25': ma25_current,
            'spread': ma_spread,
            'timeframe': timeframe,
            'crossover_type': 'golden_cross'
        }
    # DEATH CROSS ANALYSIS (ABSOLUTE PRIORITY)
    elif death_cross:
        return {
            'action': 'SELL',
            'confidence': 1.0,
            'reasons': [
                f"🔴 {timeframe} DEATH CROSS: MA7 crossed below MA25",
                f"MA7 prev: {ma7_previous:.4f} → {ma7_current:.4f}",
                f"MA25 prev: {ma25_previous:.4f} → {ma25_current:.4f}",
                f"Spread: {ma_spread:.2f}%"
            ],
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


def _combine_multi_timeframe_signals(signals: list) -> Dict:
    """
    Combine signals from multiple timeframes (1m, 5m, 15m, 30m, 60m, 120m) for final decision.
    The longest actionable timeframe (not HOLD) takes priority.
    If all HOLD, return HOLD.
    """
    # Priority: 5m > 30m > 1h > 2h > 15m > 1m
    tf_order = ['5m', '30m', '1h', '2h', '15m', '1m']
    tf_signal_map = {s.get('timeframe', tf): s for s, tf in zip(signals, tf_order)}

    for tf in tf_order:
        sig = tf_signal_map.get(tf, {})
        if sig.get('action', 'HOLD') != 'HOLD' and sig.get('confidence', 0.0) > 0.5:
            # Use this as the final signal
            reasons = [
                f"⏳ {tf} signal takes priority: {sig['action']} (confidence: {sig['confidence']:.2f})"
            ] + sig.get('reasons', [])
            return {
                'action': sig['action'],
                'confidence': sig['confidence'],
                'reasons': reasons,
                'priority_timeframe': tf,
                'signals': tf_signal_map
            }
    # If all HOLD or weak, return HOLD with reasons
    reasons = [f"No actionable signal from any timeframe (1m, 5m, 15m, 30m, 60m, 120m)"]
    for tf in tf_order:
        sig = tf_signal_map.get(tf, {})
        reasons.append(f"{tf}: {sig.get('action', 'HOLD')} (confidence: {sig.get('confidence', 0.0):.2f})")
    return {
        'action': 'HOLD',
        'confidence': 0.0,
        'reasons': reasons,
        'priority_timeframe': None,
        'signals': tf_signal_map
    }
