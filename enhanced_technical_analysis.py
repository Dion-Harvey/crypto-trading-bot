#!/usr/bin/env python3
"""
Enhanced Technical Analysis Module for Crypto Trading Bot

This module provides advanced technical indicators, pattern recognition,
and multi-timeframe analysis for improved signal quality.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging

class EnhancedTechnicalAnalysis:
    """Advanced technical analysis with multi-timeframe indicators and pattern recognition"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    # =============================================================================
    # ENHANCED OSCILLATORS
    # =============================================================================
    
    def calculate_stochastic_rsi(self, df: pd.DataFrame, period: int = 14, k_period: int = 3, d_period: int = 3) -> Dict:
        """
        Calculate Stochastic RSI - more sensitive than regular RSI for crypto
        
        Returns:
        - stoch_rsi_k: %K line
        - stoch_rsi_d: %D line (signal line)
        - signal: BUY/SELL/HOLD based on oversold/overbought levels
        - divergence: Boolean indicating RSI divergence
        """
        # Calculate RSI first
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0).rolling(period).mean()
        loss = -delta.where(delta < 0, 0).rolling(period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        # Calculate Stochastic of RSI
        rsi_min = rsi.rolling(period).min()
        rsi_max = rsi.rolling(period).max()
        stoch_rsi = (rsi - rsi_min) / (rsi_max - rsi_min) * 100
        
        # Smooth with %K and %D lines
        stoch_rsi_k = stoch_rsi.rolling(k_period).mean()
        stoch_rsi_d = stoch_rsi_k.rolling(d_period).mean()
        
        # Generate signals
        current_k = stoch_rsi_k.iloc[-1] if len(stoch_rsi_k) > 0 else 50
        current_d = stoch_rsi_d.iloc[-1] if len(stoch_rsi_d) > 0 else 50
        prev_k = stoch_rsi_k.iloc[-2] if len(stoch_rsi_k) > 1 else 50
        prev_d = stoch_rsi_d.iloc[-2] if len(stoch_rsi_d) > 1 else 50
        
        # Signal generation
        signal = 'HOLD'
        confidence = 0.0
        
        # Golden cross in oversold region (strong buy)
        if current_k > current_d and prev_k <= prev_d and current_k < 30:
            signal = 'BUY'
            confidence = min(1.0, (30 - current_k) / 30 * 1.5)
        # Death cross in overbought region (strong sell)
        elif current_k < current_d and prev_k >= prev_d and current_k > 70:
            signal = 'SELL'
            confidence = min(1.0, (current_k - 70) / 30 * 1.5)
        # Extreme oversold without crossover
        elif current_k < 10 and current_d < 15:
            signal = 'BUY'
            confidence = min(1.0, (15 - current_k) / 15)
        # Extreme overbought without crossover
        elif current_k > 90 and current_d > 85:
            signal = 'SELL'
            confidence = min(1.0, (current_k - 85) / 15)
        
        # Check for divergence (price vs RSI)
        divergence = self._detect_rsi_divergence(df['close'], rsi)
        
        return {
            'stoch_rsi_k': stoch_rsi_k,
            'stoch_rsi_d': stoch_rsi_d,
            'signal': signal,
            'confidence': confidence,
            'divergence': divergence,
            'values': {'k': current_k, 'd': current_d}
        }
    
    def calculate_williams_r(self, df: pd.DataFrame, period: int = 14) -> Dict:
        """
        Williams %R - excellent for identifying overbought/oversold conditions in crypto
        """
        high_max = df['high'].rolling(period).max()
        low_min = df['low'].rolling(period).min()
        williams_r = -100 * (high_max - df['close']) / (high_max - low_min)
        
        current_wr = williams_r.iloc[-1] if len(williams_r) > 0 else -50
        
        signal = 'HOLD'
        confidence = 0.0
        
        if current_wr <= -80:  # Oversold
            signal = 'BUY'
            confidence = min(1.0, abs(current_wr + 80) / 20)
        elif current_wr >= -20:  # Overbought
            signal = 'SELL'
            confidence = min(1.0, abs(-20 - current_wr) / 20)
        
        return {
            'williams_r': williams_r,
            'signal': signal,
            'confidence': confidence,
            'value': current_wr
        }
    
    def calculate_money_flow_index(self, df: pd.DataFrame, period: int = 14) -> Dict:
        """
        Money Flow Index - combines price and volume for better signals
        """
        typical_price = (df['high'] + df['low'] + df['close']) / 3
        money_flow = typical_price * df['volume']
        
        # Positive and negative money flow
        positive_flow = money_flow.where(typical_price > typical_price.shift(1), 0)
        negative_flow = money_flow.where(typical_price < typical_price.shift(1), 0)
        
        # Money flow ratio and index
        positive_mf = positive_flow.rolling(period).sum()
        negative_mf = negative_flow.rolling(period).sum()
        mfi = 100 - (100 / (1 + positive_mf / negative_mf))
        
        current_mfi = mfi.iloc[-1] if len(mfi) > 0 else 50
        
        signal = 'HOLD'
        confidence = 0.0
        
        if current_mfi <= 20:  # Oversold with volume confirmation
            signal = 'BUY'
            confidence = min(1.0, (20 - current_mfi) / 20 * 1.2)
        elif current_mfi >= 80:  # Overbought with volume confirmation
            signal = 'SELL'
            confidence = min(1.0, (current_mfi - 80) / 20 * 1.2)
        
        return {
            'mfi': mfi,
            'signal': signal,
            'confidence': confidence,
            'value': current_mfi
        }
    
    # =============================================================================
    # PATTERN RECOGNITION
    # =============================================================================
    
    def detect_reversal_patterns(self, df: pd.DataFrame, lookback: int = 20) -> Dict:
        """
        Detect classic reversal patterns: Double Top/Bottom, Head & Shoulders, etc.
        """
        patterns = {
            'double_bottom': False,
            'double_top': False,
            'head_shoulders': False,
            'inverse_head_shoulders': False,
            'falling_wedge': False,
            'rising_wedge': False,
            'confidence': 0.0,
            'signal': 'HOLD'
        }
        
        if len(df) < lookback:
            return patterns
        
        recent_data = df.tail(lookback)
        highs = recent_data['high']
        lows = recent_data['low']
        closes = recent_data['close']
        
        # Double Bottom Detection
        low_points = self._find_local_extrema(lows, 'min', min_distance=5)
        if len(low_points) >= 2:
            last_two_lows = low_points[-2:]
            price_diff = abs(lows.iloc[last_two_lows[0]] - lows.iloc[last_two_lows[1]])
            price_tolerance = lows.iloc[last_two_lows[0]] * 0.02  # 2% tolerance
            
            if price_diff <= price_tolerance and last_two_lows[1] - last_two_lows[0] >= 5:
                patterns['double_bottom'] = True
                patterns['signal'] = 'BUY'
                patterns['confidence'] = 0.7
        
        # Double Top Detection
        high_points = self._find_local_extrema(highs, 'max', min_distance=5)
        if len(high_points) >= 2:
            last_two_highs = high_points[-2:]
            price_diff = abs(highs.iloc[last_two_highs[0]] - highs.iloc[last_two_highs[1]])
            price_tolerance = highs.iloc[last_two_highs[0]] * 0.02  # 2% tolerance
            
            if price_diff <= price_tolerance and last_two_highs[1] - last_two_highs[0] >= 5:
                patterns['double_top'] = True
                patterns['signal'] = 'SELL'
                patterns['confidence'] = 0.7
        
        # Falling Wedge (Bullish)
        if self._detect_wedge_pattern(recent_data, 'falling'):
            patterns['falling_wedge'] = True
            patterns['signal'] = 'BUY'
            patterns['confidence'] = max(patterns['confidence'], 0.6)
        
        # Rising Wedge (Bearish)
        if self._detect_wedge_pattern(recent_data, 'rising'):
            patterns['rising_wedge'] = True
            patterns['signal'] = 'SELL'
            patterns['confidence'] = max(patterns['confidence'], 0.6)
        
        return patterns
    
    def detect_support_resistance(self, df: pd.DataFrame, lookback: int = 50, tolerance: float = 0.01) -> Dict:
        """
        Detect key support and resistance levels
        """
        if len(df) < lookback:
            return {'support': None, 'resistance': None, 'strength': 0}
        
        recent_data = df.tail(lookback)
        current_price = df['close'].iloc[-1]
        
        # Find pivot points
        highs = recent_data['high']
        lows = recent_data['low']
        
        # Identify potential support levels (from lows)
        support_levels = []
        for i in range(2, len(lows) - 2):
            if (lows.iloc[i] < lows.iloc[i-1] and lows.iloc[i] < lows.iloc[i+1] and
                lows.iloc[i] < lows.iloc[i-2] and lows.iloc[i] < lows.iloc[i+2]):
                support_levels.append(lows.iloc[i])
        
        # Identify potential resistance levels (from highs)
        resistance_levels = []
        for i in range(2, len(highs) - 2):
            if (highs.iloc[i] > highs.iloc[i-1] and highs.iloc[i] > highs.iloc[i+1] and
                highs.iloc[i] > highs.iloc[i-2] and highs.iloc[i] > highs.iloc[i+2]):
                resistance_levels.append(highs.iloc[i])
        
        # Find nearest levels
        support = None
        resistance = None
        
        if support_levels:
            valid_supports = [s for s in support_levels if s < current_price]
            if valid_supports:
                support = max(valid_supports)  # Nearest support below current price
        
        if resistance_levels:
            valid_resistances = [r for r in resistance_levels if r > current_price]
            if valid_resistances:
                resistance = min(valid_resistances)  # Nearest resistance above current price
        
        # Calculate strength based on how many times levels were tested
        strength = 0
        if support:
            touches = sum(1 for low in lows if abs(low - support) / support <= tolerance)
            strength += touches * 0.1
        
        if resistance:
            touches = sum(1 for high in highs if abs(high - resistance) / resistance <= tolerance)
            strength += touches * 0.1
        
        return {
            'support': support,
            'resistance': resistance,
            'strength': min(1.0, strength),
            'distance_to_support': (current_price - support) / current_price if support else None,
            'distance_to_resistance': (resistance - current_price) / current_price if resistance else None
        }
    
    # =============================================================================
    # VOLUME ANALYSIS
    # =============================================================================
    
    def analyze_volume_profile(self, df: pd.DataFrame, lookback: int = 100) -> Dict:
        """
        Advanced volume analysis including VWAP, volume surges, and accumulation/distribution
        """
        if len(df) < lookback:
            return {'volume_signal': 'HOLD', 'confidence': 0.0}
        
        recent_data = df.tail(lookback)
        
        # Volume metrics
        avg_volume = recent_data['volume'].mean()
        current_volume = df['volume'].iloc[-1]
        volume_ratio = current_volume / avg_volume
        
        # VWAP calculation
        vwap = (recent_data['volume'] * (recent_data['high'] + recent_data['low'] + recent_data['close']) / 3).cumsum() / recent_data['volume'].cumsum()
        current_price = df['close'].iloc[-1]
        vwap_current = vwap.iloc[-1]
        
        # On-Balance Volume (OBV)
        obv = self._calculate_obv(recent_data)
        obv_trend = 'rising' if obv.iloc[-1] > obv.iloc[-5] else 'falling'
        
        # Accumulation/Distribution Line
        ad_line = self._calculate_ad_line(recent_data)
        ad_trend = 'accumulation' if ad_line.iloc[-1] > ad_line.iloc[-5] else 'distribution'
        
        # Volume surge detection
        volume_surge = volume_ratio > 2.0  # Current volume > 2x average
        
        # Price-Volume divergence
        price_change = (df['close'].iloc[-1] - df['close'].iloc[-6]) / df['close'].iloc[-6]
        volume_change = (recent_data['volume'].tail(5).mean() - recent_data['volume'].head(5).mean()) / recent_data['volume'].head(5).mean()
        
        # Signal generation
        signal = 'HOLD'
        confidence = 0.0
        
        # Bullish volume patterns
        if (volume_surge and current_price > vwap_current and 
            obv_trend == 'rising' and ad_trend == 'accumulation'):
            signal = 'BUY'
            confidence = min(1.0, volume_ratio * 0.3)
        
        # Bearish volume patterns
        elif (volume_surge and current_price < vwap_current and 
              obv_trend == 'falling' and ad_trend == 'distribution'):
            signal = 'SELL'
            confidence = min(1.0, volume_ratio * 0.3)
        
        # Volume divergence signals
        elif price_change > 0.02 and volume_change < -0.3:  # Price up, volume down (bearish)
            signal = 'SELL'
            confidence = 0.4
        elif price_change < -0.02 and volume_change > 0.3:  # Price down, volume up (bullish)
            signal = 'BUY'
            confidence = 0.4
        
        return {
            'volume_signal': signal,
            'confidence': confidence,
            'volume_ratio': volume_ratio,
            'vwap_position': 'above' if current_price > vwap_current else 'below',
            'obv_trend': obv_trend,
            'ad_trend': ad_trend,
            'volume_surge': volume_surge,
            'metrics': {
                'volume_ratio': volume_ratio,
                'vwap': vwap_current,
                'obv': obv.iloc[-1],
                'ad_line': ad_line.iloc[-1]
            }
        }
    
    # =============================================================================
    # MULTI-TIMEFRAME ANALYSIS
    # =============================================================================
    
    def multi_timeframe_consensus(self, df_1m: pd.DataFrame, df_5m: pd.DataFrame, 
                                 df_15m: pd.DataFrame) -> Dict:
        """
        Analyze multiple timeframes for confluence
        Note: In practice, you'd fetch different timeframe data from the exchange
        For now, we'll simulate this by resampling the 1m data
        """
        # Simulate higher timeframes by resampling
        df_5m_sim = self._resample_ohlcv(df_1m, '5T')
        df_15m_sim = self._resample_ohlcv(df_1m, '15T')
        
        signals = {}
        
        # Analyze each timeframe
        for name, df in [('1m', df_1m), ('5m', df_5m_sim), ('15m', df_15m_sim)]:
            if len(df) < 20:
                continue
                
            # RSI signal
            rsi = self._calculate_rsi(df, 14)
            rsi_signal = 'BUY' if rsi.iloc[-1] < 30 else 'SELL' if rsi.iloc[-1] > 70 else 'HOLD'
            
            # Trend signal
            ma_short = df['close'].rolling(5).mean()
            ma_long = df['close'].rolling(20).mean()
            trend_signal = 'BUY' if ma_short.iloc[-1] > ma_long.iloc[-1] else 'SELL'
            
            signals[name] = {
                'rsi_signal': rsi_signal,
                'trend_signal': trend_signal,
                'rsi_value': rsi.iloc[-1]
            }
        
        # Calculate consensus
        buy_votes = sum(1 for tf in signals.values() 
                       if tf['rsi_signal'] == 'BUY' or tf['trend_signal'] == 'BUY')
        sell_votes = sum(1 for tf in signals.values() 
                        if tf['rsi_signal'] == 'SELL' or tf['trend_signal'] == 'SELL')
        
        consensus_signal = 'BUY' if buy_votes > sell_votes else 'SELL' if sell_votes > buy_votes else 'HOLD'
        consensus_strength = max(buy_votes, sell_votes) / (len(signals) * 2) if signals else 0
        
        return {
            'consensus_signal': consensus_signal,
            'consensus_strength': consensus_strength,
            'timeframe_signals': signals,
            'alignment': buy_votes if consensus_signal == 'BUY' else sell_votes
        }
    
    # =============================================================================
    # HELPER METHODS
    # =============================================================================
    
    def _detect_rsi_divergence(self, price: pd.Series, rsi: pd.Series, lookback: int = 10) -> bool:
        """Detect bullish/bearish divergence between price and RSI"""
        if len(price) < lookback or len(rsi) < lookback:
            return False
        
        recent_price = price.tail(lookback)
        recent_rsi = rsi.tail(lookback)
        
        # Find price highs and lows
        price_highs = self._find_local_extrema(recent_price, 'max')
        price_lows = self._find_local_extrema(recent_price, 'min')
        rsi_highs = self._find_local_extrema(recent_rsi, 'max')
        rsi_lows = self._find_local_extrema(recent_rsi, 'min')
        
        # Bullish divergence: price makes lower low, RSI makes higher low
        if len(price_lows) >= 2 and len(rsi_lows) >= 2:
            if (recent_price.iloc[price_lows[-1]] < recent_price.iloc[price_lows[-2]] and
                recent_rsi.iloc[rsi_lows[-1]] > recent_rsi.iloc[rsi_lows[-2]]):
                return True
        
        # Bearish divergence: price makes higher high, RSI makes lower high
        if len(price_highs) >= 2 and len(rsi_highs) >= 2:
            if (recent_price.iloc[price_highs[-1]] > recent_price.iloc[price_highs[-2]] and
                recent_rsi.iloc[rsi_highs[-1]] < recent_rsi.iloc[rsi_highs[-2]]):
                return True
        
        return False
    
    def _find_local_extrema(self, series: pd.Series, extrema_type: str, min_distance: int = 3) -> List[int]:
        """Find local maxima or minima in a series"""
        extrema = []
        for i in range(min_distance, len(series) - min_distance):
            if extrema_type == 'max':
                if all(series.iloc[i] > series.iloc[j] for j in range(i - min_distance, i + min_distance + 1) if j != i):
                    extrema.append(i)
            elif extrema_type == 'min':
                if all(series.iloc[i] < series.iloc[j] for j in range(i - min_distance, i + min_distance + 1) if j != i):
                    extrema.append(i)
        return extrema
    
    def _detect_wedge_pattern(self, df: pd.DataFrame, pattern_type: str) -> bool:
        """Detect rising or falling wedge patterns"""
        if len(df) < 15:
            return False
        
        highs = df['high']
        lows = df['low']
        
        # Simple trend line detection
        if pattern_type == 'falling':
            # Falling wedge: both highs and lows declining, but lows declining slower
            high_trend = np.polyfit(range(len(highs)), highs, 1)[0]
            low_trend = np.polyfit(range(len(lows)), lows, 1)[0]
            return high_trend < 0 and low_trend < 0 and abs(low_trend) < abs(high_trend)
        elif pattern_type == 'rising':
            # Rising wedge: both highs and lows rising, but highs rising slower
            high_trend = np.polyfit(range(len(highs)), highs, 1)[0]
            low_trend = np.polyfit(range(len(lows)), lows, 1)[0]
            return high_trend > 0 and low_trend > 0 and high_trend < low_trend
        
        return False
    
    def _calculate_rsi(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate RSI"""
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0).rolling(period).mean()
        loss = -delta.where(delta < 0, 0).rolling(period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def _calculate_obv(self, df: pd.DataFrame) -> pd.Series:
        """Calculate On-Balance Volume"""
        obv = [0]
        for i in range(1, len(df)):
            if df['close'].iloc[i] > df['close'].iloc[i-1]:
                obv.append(obv[-1] + df['volume'].iloc[i])
            elif df['close'].iloc[i] < df['close'].iloc[i-1]:
                obv.append(obv[-1] - df['volume'].iloc[i])
            else:
                obv.append(obv[-1])
        return pd.Series(obv, index=df.index)
    
    def _calculate_ad_line(self, df: pd.DataFrame) -> pd.Series:
        """Calculate Accumulation/Distribution Line"""
        money_flow_multiplier = ((df['close'] - df['low']) - (df['high'] - df['close'])) / (df['high'] - df['low'])
        money_flow_volume = money_flow_multiplier * df['volume']
        return money_flow_volume.cumsum()
    
    def _resample_ohlcv(self, df: pd.DataFrame, timeframe: str) -> pd.DataFrame:
        """Resample OHLCV data to higher timeframe"""
        if df.index.dtype != 'datetime64[ns]':
            df = df.copy()
            df.index = pd.to_datetime(df.index)
        
        resampled = df.resample(timeframe).agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        }).dropna()
        
        return resampled
