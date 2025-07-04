#!/usr/bin/env python3
"""
Enhanced Signal Filter

This module implements advanced signal filtering and confirmation mechanisms
to reduce false positives and improve trading accuracy.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import logging

class EnhancedSignalFilter:
    """
    Advanced signal filtering system with multiple confirmation layers
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.min_confirmation_score = 0.7
        self.volatility_adjustment_factor = 0.8
    
    def filter_signal(self, signal: Dict, df: pd.DataFrame, market_conditions: Dict) -> Dict:
        """
        Apply comprehensive signal filtering and confirmation
        """
        try:
            if signal['action'] == 'HOLD':
                return signal
            
            # Apply multiple filter layers
            filters = [
                self._trend_confirmation_filter(signal, df),
                self._volatility_filter(signal, df, market_conditions),
                self._volume_confirmation_filter(signal, df),
                self._momentum_confirmation_filter(signal, df),
                self._support_resistance_filter(signal, df),
                self._market_structure_filter(signal, df),
                self._risk_reward_filter(signal, df)
            ]
            
            # Calculate overall confirmation score
            confirmation_score = self._calculate_confirmation_score(filters)
            
            # Apply confirmation score to signal confidence
            filtered_confidence = signal['confidence'] * confirmation_score
            
            # Determine if signal passes filtering
            if confirmation_score < self.min_confirmation_score:
                return {
                    'action': 'HOLD',
                    'confidence': 0.0,
                    'reason': f"Signal filtered out - insufficient confirmation (score: {confirmation_score:.2f})",
                    'original_signal': signal,
                    'filter_results': filters
                }
            
            # Enhance the signal with filtering information
            enhanced_signal = signal.copy()
            enhanced_signal['confidence'] = min(filtered_confidence, 0.95)
            enhanced_signal['confirmation_score'] = confirmation_score
            enhanced_signal['filter_results'] = filters
            enhanced_signal['reason'] += f" | Confirmed (score: {confirmation_score:.2f})"
            
            return enhanced_signal
            
        except Exception as e:
            self.logger.error(f"Error in signal filtering: {e}")
            return {
                'action': 'HOLD',
                'confidence': 0.0,
                'reason': f'Signal filtering error: {str(e)}'
            }
    
    def _trend_confirmation_filter(self, signal: Dict, df: pd.DataFrame) -> Dict:
        """Filter based on trend confirmation across multiple timeframes"""
        try:
            close = df['close']
            
            # Multiple timeframe trend analysis
            ema_9 = close.ewm(span=9).mean()
            ema_21 = close.ewm(span=21).mean()
            ema_50 = close.ewm(span=50).mean()
            
            current_price = close.iloc[-1]
            
            # Trend alignment score
            trend_score = 0.0
            
            if signal['action'] == 'BUY':
                # For buy signals, check for uptrend alignment
                if current_price > ema_9.iloc[-1]:
                    trend_score += 0.3
                if ema_9.iloc[-1] > ema_21.iloc[-1]:
                    trend_score += 0.3
                if ema_21.iloc[-1] > ema_50.iloc[-1]:
                    trend_score += 0.4
            
            elif signal['action'] == 'SELL':
                # For sell signals, check for downtrend alignment
                if current_price < ema_9.iloc[-1]:
                    trend_score += 0.3
                if ema_9.iloc[-1] < ema_21.iloc[-1]:
                    trend_score += 0.3
                if ema_21.iloc[-1] < ema_50.iloc[-1]:
                    trend_score += 0.4
            
            return {
                'name': 'trend_confirmation',
                'score': trend_score,
                'passed': trend_score > 0.6,
                'details': f"Trend alignment score: {trend_score:.2f}"
            }
            
        except Exception as e:
            self.logger.warning(f"Trend confirmation filter error: {e}")
            return {'name': 'trend_confirmation', 'score': 0.0, 'passed': False, 'details': 'Error'}
    
    def _volatility_filter(self, signal: Dict, df: pd.DataFrame, market_conditions: Dict) -> Dict:
        """Filter based on volatility conditions"""
        try:
            # Get volatility from market conditions
            volatility = market_conditions.get('volatility', 0.02)
            
            # Adjust thresholds based on volatility
            if volatility > 0.04:  # Very high volatility
                volatility_score = 0.3  # Reduce confidence in high volatility
            elif volatility > 0.025:  # High volatility
                volatility_score = 0.6
            elif volatility < 0.008:  # Very low volatility
                volatility_score = 0.5  # Reduce confidence in low volatility
            else:  # Normal volatility
                volatility_score = 1.0
            
            # Additional volatility-based checks
            close = df['close']
            atr = self._calculate_atr(df, 14)
            current_atr = atr.iloc[-1] if len(atr) > 0 else 0
            
            # Check if current volatility is conducive to the signal
            if signal['action'] in ['BUY', 'SELL'] and current_atr > close.iloc[-1] * 0.05:
                volatility_score *= 0.7  # Reduce confidence in extreme volatility
            
            return {
                'name': 'volatility_filter',
                'score': volatility_score,
                'passed': volatility_score > 0.5,
                'details': f"Volatility: {volatility:.3f}, ATR: {current_atr:.2f}"
            }
            
        except Exception as e:
            self.logger.warning(f"Volatility filter error: {e}")
            return {'name': 'volatility_filter', 'score': 0.5, 'passed': True, 'details': 'Error'}
    
    def _volume_confirmation_filter(self, signal: Dict, df: pd.DataFrame) -> Dict:
        """Filter based on volume confirmation"""
        try:
            volume = df['volume']
            
            # Calculate volume indicators
            volume_ma_5 = volume.rolling(5).mean()
            volume_ma_20 = volume.rolling(20).mean()
            
            current_volume = volume.iloc[-1]
            recent_avg_volume = volume_ma_5.iloc[-1]
            baseline_volume = volume_ma_20.iloc[-1]
            
            # Volume confirmation score
            volume_score = 0.0
            
            # Check for volume surge
            if current_volume > recent_avg_volume * 1.5:
                volume_score += 0.4
            elif current_volume > recent_avg_volume * 1.2:
                volume_score += 0.2
            
            # Check for above-average volume
            if recent_avg_volume > baseline_volume * 1.1:
                volume_score += 0.3
            
            # Check for consistent volume
            recent_volumes = volume.iloc[-3:]
            if all(v > baseline_volume * 0.8 for v in recent_volumes):
                volume_score += 0.3
            
            return {
                'name': 'volume_confirmation',
                'score': volume_score,
                'passed': volume_score > 0.4,
                'details': f"Current: {current_volume:.0f}, 5MA: {recent_avg_volume:.0f}, 20MA: {baseline_volume:.0f}"
            }
            
        except Exception as e:
            self.logger.warning(f"Volume confirmation filter error: {e}")
            return {'name': 'volume_confirmation', 'score': 0.5, 'passed': True, 'details': 'Error'}
    
    def _momentum_confirmation_filter(self, signal: Dict, df: pd.DataFrame) -> Dict:
        """Filter based on momentum confirmation"""
        try:
            close = df['close']
            
            # Calculate momentum indicators
            rsi = self._calculate_rsi(close, 14)
            momentum_10 = close.pct_change(10)
            
            current_rsi = rsi.iloc[-1]
            current_momentum = momentum_10.iloc[-1]
            
            momentum_score = 0.0
            
            if signal['action'] == 'BUY':
                # For buy signals, look for oversold conditions recovering
                if 25 <= current_rsi <= 45:  # RSI in buy zone but not oversold
                    momentum_score += 0.4
                if current_momentum > 0.005:  # Positive momentum
                    momentum_score += 0.3
                if rsi.iloc[-1] > rsi.iloc[-2]:  # RSI improving
                    momentum_score += 0.3
            
            elif signal['action'] == 'SELL':
                # For sell signals, look for overbought conditions weakening
                if 55 <= current_rsi <= 75:  # RSI in sell zone but not overbought
                    momentum_score += 0.4
                if current_momentum < -0.005:  # Negative momentum
                    momentum_score += 0.3
                if rsi.iloc[-1] < rsi.iloc[-2]:  # RSI deteriorating
                    momentum_score += 0.3
            
            return {
                'name': 'momentum_confirmation',
                'score': momentum_score,
                'passed': momentum_score > 0.5,
                'details': f"RSI: {current_rsi:.1f}, Momentum: {current_momentum:.3f}"
            }
            
        except Exception as e:
            self.logger.warning(f"Momentum confirmation filter error: {e}")
            return {'name': 'momentum_confirmation', 'score': 0.5, 'passed': True, 'details': 'Error'}
    
    def _support_resistance_filter(self, signal: Dict, df: pd.DataFrame) -> Dict:
        """Filter based on support/resistance levels"""
        try:
            high = df['high']
            low = df['low']
            close = df['close']
            
            current_price = close.iloc[-1]
            
            # Find recent support and resistance levels
            recent_highs = high.rolling(10, center=True).max()
            recent_lows = low.rolling(10, center=True).min()
            
            # Get significant levels
            resistance_levels = recent_highs.dropna().unique()[-5:]  # Last 5 resistance levels
            support_levels = recent_lows.dropna().unique()[-5:]     # Last 5 support levels
            
            sr_score = 0.0
            
            if signal['action'] == 'BUY':
                # Check distance from support
                closest_support = max([s for s in support_levels if s <= current_price], default=0)
                if closest_support > 0:
                    distance_from_support = (current_price - closest_support) / current_price
                    if distance_from_support < 0.02:  # Within 2% of support
                        sr_score += 0.5
                
                # Check distance from resistance
                closest_resistance = min([r for r in resistance_levels if r >= current_price], default=float('inf'))
                if closest_resistance != float('inf'):
                    distance_to_resistance = (closest_resistance - current_price) / current_price
                    if distance_to_resistance > 0.015:  # More than 1.5% to resistance
                        sr_score += 0.5
            
            elif signal['action'] == 'SELL':
                # Check distance from resistance
                closest_resistance = min([r for r in resistance_levels if r >= current_price], default=float('inf'))
                if closest_resistance != float('inf'):
                    distance_from_resistance = (closest_resistance - current_price) / current_price
                    if distance_from_resistance < 0.02:  # Within 2% of resistance
                        sr_score += 0.5
                
                # Check distance from support
                closest_support = max([s for s in support_levels if s <= current_price], default=0)
                if closest_support > 0:
                    distance_to_support = (current_price - closest_support) / current_price
                    if distance_to_support > 0.015:  # More than 1.5% from support
                        sr_score += 0.5
            
            return {
                'name': 'support_resistance',
                'score': sr_score,
                'passed': sr_score > 0.4,
                'details': f"SR score: {sr_score:.2f}"
            }
            
        except Exception as e:
            self.logger.warning(f"Support/resistance filter error: {e}")
            return {'name': 'support_resistance', 'score': 0.5, 'passed': True, 'details': 'Error'}
    
    def _market_structure_filter(self, signal: Dict, df: pd.DataFrame) -> Dict:
        """Filter based on market structure analysis"""
        try:
            close = df['close']
            high = df['high']
            low = df['low']
            
            # Analyze market structure
            structure_score = 0.0
            
            # Check for clean price action
            recent_candles = df.iloc[-5:]
            body_sizes = abs(recent_candles['close'] - recent_candles['open'])
            wick_sizes = (recent_candles['high'] - recent_candles['low']) - body_sizes
            
            avg_body_ratio = (body_sizes / (recent_candles['high'] - recent_candles['low'])).mean()
            
            if avg_body_ratio > 0.6:  # Strong directional candles
                structure_score += 0.4
            
            # Check for consistent direction
            if signal['action'] == 'BUY':
                bullish_candles = (recent_candles['close'] > recent_candles['open']).sum()
                if bullish_candles >= 3:
                    structure_score += 0.3
            elif signal['action'] == 'SELL':
                bearish_candles = (recent_candles['close'] < recent_candles['open']).sum()
                if bearish_candles >= 3:
                    structure_score += 0.3
            
            # Check for breakout patterns
            recent_range = high.iloc[-20:].max() - low.iloc[-20:].min()
            current_position = (close.iloc[-1] - low.iloc[-20:].min()) / recent_range
            
            if signal['action'] == 'BUY' and current_position > 0.7:
                structure_score += 0.3
            elif signal['action'] == 'SELL' and current_position < 0.3:
                structure_score += 0.3
            
            return {
                'name': 'market_structure',
                'score': structure_score,
                'passed': structure_score > 0.5,
                'details': f"Structure score: {structure_score:.2f}, Body ratio: {avg_body_ratio:.2f}"
            }
            
        except Exception as e:
            self.logger.warning(f"Market structure filter error: {e}")
            return {'name': 'market_structure', 'score': 0.5, 'passed': True, 'details': 'Error'}
    
    def _risk_reward_filter(self, signal: Dict, df: pd.DataFrame) -> Dict:
        """Filter based on risk/reward ratio"""
        try:
            close = df['close']
            high = df['high']
            low = df['low']
            
            current_price = close.iloc[-1]
            atr = self._calculate_atr(df, 14)
            current_atr = atr.iloc[-1] if len(atr) > 0 else current_price * 0.02
            
            # Calculate potential risk/reward
            if signal['action'] == 'BUY':
                # For buy: risk = ATR downside, reward = ATR * 2 upside
                stop_loss = current_price - current_atr
                take_profit = current_price + (current_atr * 2)
                risk = current_price - stop_loss
                reward = take_profit - current_price
            elif signal['action'] == 'SELL':
                # For sell: risk = ATR upside, reward = ATR * 2 downside
                stop_loss = current_price + current_atr
                take_profit = current_price - (current_atr * 2)
                risk = stop_loss - current_price
                reward = current_price - take_profit
            else:
                return {'name': 'risk_reward', 'score': 1.0, 'passed': True, 'details': 'N/A for HOLD'}
            
            # Calculate risk/reward ratio
            rr_ratio = reward / risk if risk > 0 else 0
            
            # Score based on risk/reward ratio
            if rr_ratio >= 2.0:
                rr_score = 1.0
            elif rr_ratio >= 1.5:
                rr_score = 0.8
            elif rr_ratio >= 1.0:
                rr_score = 0.6
            else:
                rr_score = 0.3
            
            return {
                'name': 'risk_reward',
                'score': rr_score,
                'passed': rr_score > 0.6,
                'details': f"R/R ratio: {rr_ratio:.2f}, Risk: {risk:.2f}, Reward: {reward:.2f}"
            }
            
        except Exception as e:
            self.logger.warning(f"Risk/reward filter error: {e}")
            return {'name': 'risk_reward', 'score': 0.5, 'passed': True, 'details': 'Error'}
    
    def _calculate_confirmation_score(self, filters: List[Dict]) -> float:
        """Calculate overall confirmation score from all filters"""
        if not filters:
            return 0.0
        
        # Weight different filters
        filter_weights = {
            'trend_confirmation': 0.25,
            'momentum_confirmation': 0.20,
            'volume_confirmation': 0.15,
            'support_resistance': 0.15,
            'market_structure': 0.10,
            'volatility_filter': 0.10,
            'risk_reward': 0.05
        }
        
        total_score = 0.0
        total_weight = 0.0
        
        for filter_result in filters:
            filter_name = filter_result.get('name', '')
            filter_score = filter_result.get('score', 0.0)
            weight = filter_weights.get(filter_name, 0.1)
            
            total_score += filter_score * weight
            total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.0
    
    # Helper methods
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _calculate_atr(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average True Range"""
        high = df['high']
        low = df['low']
        close = df['close']
        
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        
        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = true_range.rolling(period).mean()
        
        return atr
