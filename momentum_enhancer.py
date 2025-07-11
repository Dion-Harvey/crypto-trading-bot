#!/usr/bin/env python3
"""
Advanced Momentum Enhancement Module

This module implements sophisticated momentum and trend confirmation filters
to improve trade signal quality and reduce false positives.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging

class MomentumEnhancer:
    """
    Advanced momentum analysis and trend confirmation system
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def analyze_momentum_confluence(self, df: pd.DataFrame) -> Dict:
        """
        Analyze momentum confluence across multiple timeframes and indicators
        """
        try:
            # Multi-timeframe momentum analysis
            momentum_signals = {
                'short_term': self._analyze_short_term_momentum(df),
                'medium_term': self._analyze_medium_term_momentum(df),
                'long_term': self._analyze_long_term_momentum(df),
                'volume_momentum': self._analyze_volume_momentum(df),
                'price_action': self._analyze_price_action_momentum(df)
            }
            
            # Calculate confluence score
            confluence_score = self._calculate_confluence_score(momentum_signals)
            
            # Determine overall momentum direction
            momentum_direction = self._determine_momentum_direction(momentum_signals)
            
            # Calculate momentum strength
            momentum_strength = self._calculate_momentum_strength(momentum_signals)
            
            return {
                'confluence_score': confluence_score,
                'direction': momentum_direction,
                'strength': momentum_strength,
                'signals': momentum_signals,
                'recommendation': self._generate_momentum_recommendation(
                    confluence_score, momentum_direction, momentum_strength
                )
            }
            
        except Exception as e:
            self.logger.error(f"Error in momentum confluence analysis: {e}")
            return {
                'confluence_score': 0.0,
                'direction': 'NEUTRAL',
                'strength': 0.0,
                'signals': {},
                'recommendation': {'action': 'HOLD', 'confidence': 0.0}
            }
    
    def _analyze_short_term_momentum(self, df: pd.DataFrame) -> Dict:
        """Analyze short-term momentum (5-15 minutes)"""
        if len(df) < 15:
            return {'score': 0.0, 'direction': 'NEUTRAL'}
        
        # Calculate short-term indicators
        close = df['close'].iloc[-15:]
        
        # RSI momentum
        rsi_14 = self._calculate_rsi(close, 14)
        rsi_momentum = (rsi_14.iloc[-1] - rsi_14.iloc[-3]) / 3
        
        # Price momentum
        price_momentum = (close.iloc[-1] - close.iloc[-5]) / close.iloc[-5]
        
        # EMA slope
        ema_5 = close.ewm(span=5).mean()
        ema_slope = (ema_5.iloc[-1] - ema_5.iloc[-3]) / ema_5.iloc[-3]
        
        # Combine signals
        momentum_score = (rsi_momentum * 0.3 + price_momentum * 100 * 0.4 + ema_slope * 100 * 0.3)
        
        direction = 'BULLISH' if momentum_score > 0.5 else 'BEARISH' if momentum_score < -0.5 else 'NEUTRAL'
        
        return {
            'score': abs(momentum_score),
            'direction': direction,
            'rsi_momentum': rsi_momentum,
            'price_momentum': price_momentum,
            'ema_slope': ema_slope
        }
    
    def _analyze_medium_term_momentum(self, df: pd.DataFrame) -> Dict:
        """Analyze medium-term momentum (15-60 minutes)"""
        if len(df) < 60:
            return {'score': 0.0, 'direction': 'NEUTRAL'}
        
        close = df['close']
        
        # MACD analysis
        macd_line, macd_signal, macd_histogram = self._calculate_macd(close)
        macd_momentum = macd_histogram.iloc[-1] - macd_histogram.iloc[-3]
        
        # Moving average convergence
        ema_20 = close.ewm(span=20).mean()
        ema_50 = close.ewm(span=50).mean()
        ma_convergence = (ema_20.iloc[-1] - ema_50.iloc[-1]) / ema_50.iloc[-1]
        
        # Trend strength
        trend_strength = self._calculate_trend_strength(close, 30)
        
        # Combine signals
        momentum_score = (abs(macd_momentum) * 0.4 + abs(ma_convergence) * 100 * 0.3 + trend_strength * 0.3)
        
        direction = 'BULLISH' if ma_convergence > 0 and macd_momentum > 0 else \
                   'BEARISH' if ma_convergence < 0 and macd_momentum < 0 else 'NEUTRAL'
        
        return {
            'score': momentum_score,
            'direction': direction,
            'macd_momentum': macd_momentum,
            'ma_convergence': ma_convergence,
            'trend_strength': trend_strength
        }
    
    def _analyze_long_term_momentum(self, df: pd.DataFrame) -> Dict:
        """Analyze long-term momentum (1-4 hours)"""
        if len(df) < 120:
            return {'score': 0.0, 'direction': 'NEUTRAL'}
        
        close = df['close']
        
        # Long-term moving averages
        sma_50 = close.rolling(50).mean()
        sma_100 = close.rolling(100).mean()
        
        # Trend direction
        long_term_trend = 'BULLISH' if sma_50.iloc[-1] > sma_100.iloc[-1] else 'BEARISH'
        
        # Momentum oscillator
        momentum_14 = close.iloc[-1] / close.iloc[-15] - 1
        momentum_30 = close.iloc[-1] / close.iloc[-31] - 1
        
        # Rate of change
        roc_20 = (close.iloc[-1] - close.iloc[-21]) / close.iloc[-21]
        
        # Combine signals
        momentum_score = (abs(momentum_14) * 0.4 + abs(momentum_30) * 0.3 + abs(roc_20) * 0.3)
        
        direction = long_term_trend if momentum_score > 0.01 else 'NEUTRAL'
        
        return {
            'score': momentum_score,
            'direction': direction,
            'momentum_14': momentum_14,
            'momentum_30': momentum_30,
            'roc_20': roc_20,
            'trend': long_term_trend
        }
    
    def _analyze_volume_momentum(self, df: pd.DataFrame) -> Dict:
        """Analyze volume-based momentum"""
        if len(df) < 20:
            return {'score': 0.0, 'direction': 'NEUTRAL'}
        
        volume = df['volume']
        close = df['close']
        
        # Volume trend
        volume_ma_5 = volume.rolling(5).mean()
        volume_ma_20 = volume.rolling(20).mean()
        volume_trend = volume_ma_5.iloc[-1] / volume_ma_20.iloc[-1] - 1
        
        # On-Balance Volume momentum
        obv = self._calculate_obv(close, volume)
        obv_momentum = (obv.iloc[-1] - obv.iloc[-5]) / abs(obv.iloc[-5]) if obv.iloc[-5] != 0 else 0
        
        # Volume-Price Trend
        vpt = self._calculate_vpt(close, volume)
        vpt_momentum = (vpt.iloc[-1] - vpt.iloc[-5]) / abs(vpt.iloc[-5]) if vpt.iloc[-5] != 0 else 0
        
        # Combine signals
        momentum_score = (abs(volume_trend) * 0.3 + abs(obv_momentum) * 0.4 + abs(vpt_momentum) * 0.3)
        
        direction = 'BULLISH' if volume_trend > 0 and obv_momentum > 0 else \
                   'BEARISH' if volume_trend < 0 and obv_momentum < 0 else 'NEUTRAL'
        
        return {
            'score': momentum_score,
            'direction': direction,
            'volume_trend': volume_trend,
            'obv_momentum': obv_momentum,
            'vpt_momentum': vpt_momentum
        }
    
    def _analyze_price_action_momentum(self, df: pd.DataFrame) -> Dict:
        """Analyze price action momentum patterns"""
        if len(df) < 10:
            return {'score': 0.0, 'direction': 'NEUTRAL'}
        
        high = df['high']
        low = df['low']
        close = df['close']
        
        # Higher highs and higher lows (bullish)
        recent_highs = high.iloc[-5:]
        recent_lows = low.iloc[-5:]
        
        higher_highs = sum(recent_highs.iloc[i] > recent_highs.iloc[i-1] for i in range(1, len(recent_highs)))
        higher_lows = sum(recent_lows.iloc[i] > recent_lows.iloc[i-1] for i in range(1, len(recent_lows)))
        
        # Lower highs and lower lows (bearish)
        lower_highs = sum(recent_highs.iloc[i] < recent_highs.iloc[i-1] for i in range(1, len(recent_highs)))
        lower_lows = sum(recent_lows.iloc[i] < recent_lows.iloc[i-1] for i in range(1, len(recent_lows)))
        
        # Candlestick momentum
        bullish_candles = sum((close.iloc[-5:] > df['open'].iloc[-5:]).astype(int))
        bearish_candles = 5 - bullish_candles
        
        # Calculate momentum score
        bullish_score = (higher_highs + higher_lows + bullish_candles) / 12
        bearish_score = (lower_highs + lower_lows + bearish_candles) / 12
        
        if bullish_score > bearish_score + 0.2:
            direction = 'BULLISH'
            momentum_score = bullish_score
        elif bearish_score > bullish_score + 0.2:
            direction = 'BEARISH'
            momentum_score = bearish_score
        else:
            direction = 'NEUTRAL'
            momentum_score = max(bullish_score, bearish_score)
        
        return {
            'score': momentum_score,
            'direction': direction,
            'higher_highs': higher_highs,
            'higher_lows': higher_lows,
            'lower_highs': lower_highs,
            'lower_lows': lower_lows,
            'bullish_candles': bullish_candles
        }
    
    def _calculate_confluence_score(self, momentum_signals: Dict) -> float:
        """Calculate overall momentum confluence score"""
        scores = []
        directions = []
        
        for signal_name, signal_data in momentum_signals.items():
            if isinstance(signal_data, dict) and 'score' in signal_data and 'direction' in signal_data:
                scores.append(signal_data['score'])
                directions.append(signal_data['direction'])
        
        if not scores:
            return 0.0
        
        # Calculate direction agreement
        bullish_count = directions.count('BULLISH')
        bearish_count = directions.count('BEARISH')
        neutral_count = directions.count('NEUTRAL')
        
        total_directions = len(directions)
        max_agreement = max(bullish_count, bearish_count, neutral_count)
        direction_agreement = max_agreement / total_directions if total_directions > 0 else 0
        
        # Combine average score with direction agreement
        avg_score = np.mean(scores)
        confluence_score = avg_score * direction_agreement
        
        return min(confluence_score, 1.0)
    
    def _determine_momentum_direction(self, momentum_signals: Dict) -> str:
        """Determine overall momentum direction"""
        directions = []
        weights = {
            'short_term': 0.25,
            'medium_term': 0.30,
            'long_term': 0.20,
            'volume_momentum': 0.15,
            'price_action': 0.10
        }
        
        weighted_votes = {'BULLISH': 0.0, 'BEARISH': 0.0, 'NEUTRAL': 0.0}
        
        for signal_name, signal_data in momentum_signals.items():
            if isinstance(signal_data, dict) and 'direction' in signal_data:
                direction = signal_data['direction']
                weight = weights.get(signal_name, 0.1)
                weighted_votes[direction] += weight
        
        # Return direction with highest weighted vote
        return max(weighted_votes, key=weighted_votes.get)
    
    def _calculate_momentum_strength(self, momentum_signals: Dict) -> float:
        """Calculate overall momentum strength"""
        scores = []
        for signal_data in momentum_signals.values():
            if isinstance(signal_data, dict) and 'score' in signal_data:
                scores.append(signal_data['score'])
        
        return np.mean(scores) if scores else 0.0
    
    def _generate_momentum_recommendation(self, confluence_score: float, direction: str, strength: float) -> Dict:
        """Generate trading recommendation based on momentum analysis"""
        if confluence_score < 0.3 or strength < 0.2:
            return {'action': 'HOLD', 'confidence': 0.0}
        
        if direction == 'BULLISH' and confluence_score > 0.6:
            confidence = min(confluence_score * strength * 1.2, 1.0)
            return {'action': 'BUY', 'confidence': confidence}
        elif direction == 'BEARISH' and confluence_score > 0.6:
            confidence = min(confluence_score * strength * 1.2, 1.0)
            return {'action': 'SELL', 'confidence': confidence}
        else:
            return {'action': 'HOLD', 'confidence': confluence_score * 0.5}
    
    # Helper methods for technical indicators
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calculate MACD"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd_line = ema_fast - ema_slow
        macd_signal = macd_line.ewm(span=signal).mean()
        macd_histogram = macd_line - macd_signal
        return macd_line, macd_signal, macd_histogram
    
    def _calculate_trend_strength(self, prices: pd.Series, period: int = 20) -> float:
        """Calculate trend strength using linear regression slope"""
        if len(prices) < period:
            return 0.0
        
        recent_prices = prices.iloc[-period:]
        x = np.arange(len(recent_prices))
        slope, _ = np.polyfit(x, recent_prices, 1)
        
        # Normalize slope relative to price
        trend_strength = abs(slope) / recent_prices.mean()
        return min(trend_strength * 100, 1.0)
    
    def _calculate_obv(self, prices: pd.Series, volume: pd.Series) -> pd.Series:
        """Calculate On-Balance Volume"""
        obv = np.where(prices > prices.shift(1), volume, 
               np.where(prices < prices.shift(1), -volume, 0)).cumsum()
        return pd.Series(obv, index=prices.index)
    
    def _calculate_vpt(self, prices: pd.Series, volume: pd.Series) -> pd.Series:
        """Calculate Volume-Price Trend"""
        vpt = (volume * ((prices - prices.shift(1)) / prices.shift(1))).cumsum()
        return vpt
