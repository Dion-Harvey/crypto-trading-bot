#!/usr/bin/env python3
"""
Advanced Volume Analysis Module for Crypto Trading Bot

This module provides sophisticated volume-based indicators and analysis
including institutional flow detection, volume patterns, and liquidity analysis.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging

class VolumeAnalyzer:
    """Advanced volume analysis for crypto trading"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def analyze_volume_flow(self, df: pd.DataFrame, lookback: int = 50) -> Dict:
        """
        Comprehensive volume flow analysis to detect institutional activity
        """
        if len(df) < lookback:
            return {'flow_signal': 'HOLD', 'confidence': 0.0}
        
        recent_data = df.tail(lookback)
        
        # Volume metrics
        avg_volume = recent_data['volume'].rolling(20).mean()
        current_volume = df['volume'].iloc[-1]
        volume_sma_20 = avg_volume.iloc[-1]
        
        # Volume surge detection (multiple thresholds)
        volume_ratios = {
            'current_vs_avg': current_volume / volume_sma_20,
            'recent_5_vs_avg': recent_data['volume'].tail(5).mean() / volume_sma_20,
            'recent_10_vs_avg': recent_data['volume'].tail(10).mean() / volume_sma_20
        }
        
        # Price-Volume relationship analysis
        price_changes = recent_data['close'].pct_change()
        volume_changes = recent_data['volume'].pct_change()
        
        # Positive Volume Index (PVI) and Negative Volume Index (NVI)
        pvi, nvi = self._calculate_pvi_nvi(recent_data)
        
        # Volume-Weighted RSI
        vw_rsi = self._calculate_volume_weighted_rsi(recent_data)
        
        # Ease of Movement (EOM)
        eom = self._calculate_ease_of_movement(recent_data)
        
        # Chaikin Money Flow
        cmf = self._calculate_chaikin_money_flow(recent_data)
        
        # Force Index
        force_index = self._calculate_force_index(recent_data)
        
        # Volume analysis signals
        signals = self._generate_volume_signals(
            volume_ratios, pvi, nvi, vw_rsi, eom, cmf, force_index, recent_data
        )
        
        return {
            'flow_signal': signals['primary_signal'],
            'confidence': signals['confidence'],
            'volume_metrics': {
                'current_vs_avg_ratio': volume_ratios['current_vs_avg'],
                'volume_trend': self._get_volume_trend(recent_data['volume']),
                'institutional_flow': signals['institutional_flow'],
                'retail_sentiment': signals['retail_sentiment']
            },
            'indicators': {
                'pvi': pvi.iloc[-1] if len(pvi) > 0 else 0,
                'nvi': nvi.iloc[-1] if len(nvi) > 0 else 0,
                'vw_rsi': vw_rsi.iloc[-1] if len(vw_rsi) > 0 else 50,
                'eom': eom.iloc[-1] if len(eom) > 0 else 0,
                'cmf': cmf.iloc[-1] if len(cmf) > 0 else 0,
                'force_index': force_index.iloc[-1] if len(force_index) > 0 else 0
            },
            'detailed_analysis': signals['details']
        }
    
    def detect_volume_patterns(self, df: pd.DataFrame, lookback: int = 30) -> Dict:
        """
        Detect specific volume patterns that often precede price movements
        """
        if len(df) < lookback:
            return {'patterns': [], 'signal': 'HOLD', 'confidence': 0.0}
        
        recent_data = df.tail(lookback)
        patterns = []
        confidence = 0.0
        signal = 'HOLD'
        
        # 1. Volume Climax (Selling or Buying)
        volume_climax = self._detect_volume_climax(recent_data)
        if volume_climax['detected']:
            patterns.append(volume_climax)
            confidence = max(confidence, volume_climax['confidence'])
            signal = volume_climax['signal']
        
        # 2. Volume Dry-Up (Low Volume Consolidation)
        volume_dryup = self._detect_volume_dryup(recent_data)
        if volume_dryup['detected']:
            patterns.append(volume_dryup)
            # Volume dry-up usually means consolidation before breakout
            confidence = max(confidence, volume_dryup['confidence'] * 0.6)
        
        # 3. Volume Divergence
        volume_divergence = self._detect_volume_divergence(recent_data)
        if volume_divergence['detected']:
            patterns.append(volume_divergence)
            confidence = max(confidence, volume_divergence['confidence'])
            signal = volume_divergence['signal']
        
        # 4. Distribution/Accumulation Patterns
        distribution_pattern = self._detect_distribution_accumulation(recent_data)
        if distribution_pattern['detected']:
            patterns.append(distribution_pattern)
            confidence = max(confidence, distribution_pattern['confidence'])
            signal = distribution_pattern['signal']
        
        # 5. Volume Breakout Confirmation
        breakout_confirmation = self._detect_volume_breakout(recent_data)
        if breakout_confirmation['detected']:
            patterns.append(breakout_confirmation)
            confidence = max(confidence, breakout_confirmation['confidence'])
            signal = breakout_confirmation['signal']
        
        return {
            'patterns': patterns,
            'signal': signal,
            'confidence': min(1.0, confidence),
            'pattern_count': len(patterns),
            'strongest_pattern': max(patterns, key=lambda x: x['confidence']) if patterns else None
        }
    
    def analyze_order_flow(self, df: pd.DataFrame, tick_data: Optional[pd.DataFrame] = None) -> Dict:
        """
        Analyze order flow and market microstructure
        Note: This is a simplified version as true order flow requires tick data
        """
        if len(df) < 20:
            return {'flow_signal': 'HOLD', 'confidence': 0.0}
        
        # Simplified order flow analysis using OHLCV data
        recent_data = df.tail(20)
        
        # Delta analysis (buying vs selling pressure)
        delta = self._calculate_price_volume_delta(recent_data)
        
        # Cumulative delta
        cumulative_delta = delta.cumsum()
        
        # Volume at price levels (simplified)
        volume_profile = self._create_simple_volume_profile(recent_data)
        
        # Absorption analysis (large volume with small price movement)
        absorption = self._detect_absorption(recent_data)
        
        # Imbalance detection
        imbalance = self._detect_order_imbalance(recent_data)
        
        # Generate order flow signal
        signal = 'HOLD'
        confidence = 0.0
        
        current_delta = delta.iloc[-1] if len(delta) > 0 else 0
        delta_trend = cumulative_delta.iloc[-1] - cumulative_delta.iloc[-6] if len(cumulative_delta) >= 6 else 0
        
        if delta_trend > 0 and absorption['buying_absorption']:
            signal = 'BUY'
            confidence = min(1.0, abs(delta_trend) * 2 + absorption['strength'])
        elif delta_trend < 0 and absorption['selling_absorption']:
            signal = 'SELL'
            confidence = min(1.0, abs(delta_trend) * 2 + absorption['strength'])
        
        return {
            'flow_signal': signal,
            'confidence': confidence,
            'metrics': {
                'current_delta': current_delta,
                'cumulative_delta': cumulative_delta.iloc[-1] if len(cumulative_delta) > 0 else 0,
                'delta_trend': delta_trend,
                'poc': volume_profile['poc'],  # Point of Control
                'value_area_high': volume_profile['vah'],
                'value_area_low': volume_profile['val']
            },
            'absorption': absorption,
            'imbalance': imbalance
        }
    
    # =============================================================================
    # INDICATOR CALCULATIONS
    # =============================================================================
    
    def _calculate_pvi_nvi(self, df: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
        """Calculate Positive and Negative Volume Index"""
        pvi = [100]  # Start with base value
        nvi = [100]
        
        for i in range(1, len(df)):
            price_change = (df['close'].iloc[i] - df['close'].iloc[i-1]) / df['close'].iloc[i-1]
            
            if df['volume'].iloc[i] > df['volume'].iloc[i-1]:
                # Volume increased - update PVI
                pvi.append(pvi[-1] * (1 + price_change))
                nvi.append(nvi[-1])
            else:
                # Volume decreased - update NVI
                pvi.append(pvi[-1])
                nvi.append(nvi[-1] * (1 + price_change))
        
        return pd.Series(pvi, index=df.index), pd.Series(nvi, index=df.index)
    
    def _calculate_volume_weighted_rsi(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Volume-Weighted RSI"""
        # Volume-weighted price changes
        price_change = df['close'].diff()
        volume_weighted_change = price_change * df['volume']
        
        # Separate gains and losses
        gains = volume_weighted_change.where(volume_weighted_change > 0, 0)
        losses = -volume_weighted_change.where(volume_weighted_change < 0, 0)
        
        # Calculate average gains and losses
        avg_gains = gains.rolling(period).sum() / df['volume'].rolling(period).sum()
        avg_losses = losses.rolling(period).sum() / df['volume'].rolling(period).sum()
        
        # Calculate RSI
        rs = avg_gains / avg_losses
        vw_rsi = 100 - (100 / (1 + rs))
        
        return vw_rsi
    
    def _calculate_ease_of_movement(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Ease of Movement"""
        high_low = df['high'] - df['low']
        high_low_avg = (df['high'] + df['low']) / 2
        
        # Distance moved
        dm = high_low_avg - high_low_avg.shift(1)
        
        # Box ratio (volume / (high - low))
        box_ratio = df['volume'] / high_low
        
        # 1-period EMV
        emv_1 = dm / box_ratio
        
        # Multi-period EMV
        emv = emv_1.rolling(period).mean()
        
        return emv
    
    def _calculate_chaikin_money_flow(self, df: pd.DataFrame, period: int = 20) -> pd.Series:
        """Calculate Chaikin Money Flow"""
        # Money Flow Multiplier
        mf_multiplier = ((df['close'] - df['low']) - (df['high'] - df['close'])) / (df['high'] - df['low'])
        
        # Money Flow Volume
        mf_volume = mf_multiplier * df['volume']
        
        # Chaikin Money Flow
        cmf = mf_volume.rolling(period).sum() / df['volume'].rolling(period).sum()
        
        return cmf
    
    def _calculate_force_index(self, df: pd.DataFrame, period: int = 13) -> pd.Series:
        """Calculate Force Index"""
        price_change = df['close'] - df['close'].shift(1)
        force_index = price_change * df['volume']
        
        # Smooth with EMA
        return force_index.ewm(span=period).mean()
    
    def _calculate_price_volume_delta(self, df: pd.DataFrame) -> pd.Series:
        """Calculate simplified price-volume delta"""
        # Simplified: positive if close > open, negative if close < open
        delta = []
        for i in range(len(df)):
            if df['close'].iloc[i] > df['open'].iloc[i]:
                delta.append(df['volume'].iloc[i])  # Buying volume
            elif df['close'].iloc[i] < df['open'].iloc[i]:
                delta.append(-df['volume'].iloc[i])  # Selling volume
            else:
                delta.append(0)  # Neutral
        
        return pd.Series(delta, index=df.index)
    
    # =============================================================================
    # PATTERN DETECTION
    # =============================================================================
    
    def _detect_volume_climax(self, df: pd.DataFrame) -> Dict:
        """Detect volume climax patterns"""
        volume = df['volume']
        prices = df['close']
        
        # Find the highest volume in the period
        max_volume_idx = volume.idxmax()
        max_volume = volume.loc[max_volume_idx]
        avg_volume = volume.mean()
        
        # Check if max volume is significantly higher
        if max_volume > avg_volume * 3:  # Volume climax threshold
            price_at_climax = prices.loc[max_volume_idx]
            recent_prices = prices.tail(5)
            
            # Selling climax: high volume with price decline
            if price_at_climax == recent_prices.min():
                return {
                    'detected': True,
                    'type': 'selling_climax',
                    'signal': 'BUY',  # Contrarian signal
                    'confidence': min(1.0, (max_volume / avg_volume - 3) / 10),
                    'description': f'Selling climax detected with {max_volume/avg_volume:.1f}x volume'
                }
            
            # Buying climax: high volume with price peak
            elif price_at_climax == recent_prices.max():
                return {
                    'detected': True,
                    'type': 'buying_climax',
                    'signal': 'SELL',  # Contrarian signal
                    'confidence': min(1.0, (max_volume / avg_volume - 3) / 10),
                    'description': f'Buying climax detected with {max_volume/avg_volume:.1f}x volume'
                }
        
        return {'detected': False}
    
    def _detect_volume_dryup(self, df: pd.DataFrame) -> Dict:
        """Detect volume dry-up patterns"""
        volume = df['volume']
        recent_volume = volume.tail(5).mean()
        avg_volume = volume.mean()
        
        # Volume dry-up: recent volume significantly below average
        if recent_volume < avg_volume * 0.5:
            return {
                'detected': True,
                'type': 'volume_dryup',
                'signal': 'WATCH',  # Consolidation signal
                'confidence': 0.6,
                'description': f'Volume dry-up: {recent_volume/avg_volume:.1f}x average volume'
            }
        
        return {'detected': False}
    
    def _detect_volume_divergence(self, df: pd.DataFrame) -> Dict:
        """Detect price-volume divergence"""
        prices = df['close']
        volume = df['volume']
        
        # Price trend (last 10 periods)
        price_start = prices.iloc[-10]
        price_end = prices.iloc[-1]
        price_trend = (price_end - price_start) / price_start
        
        # Volume trend (last 10 periods)
        volume_start = volume.iloc[-10:].iloc[:5].mean()
        volume_end = volume.iloc[-5:].mean()
        volume_trend = (volume_end - volume_start) / volume_start
        
        # Detect divergence
        if price_trend > 0.02 and volume_trend < -0.2:  # Price up, volume down
            return {
                'detected': True,
                'type': 'bearish_divergence',
                'signal': 'SELL',
                'confidence': min(1.0, abs(volume_trend) * 2),
                'description': 'Bearish divergence: price rising with declining volume'
            }
        elif price_trend < -0.02 and volume_trend > 0.2:  # Price down, volume up
            return {
                'detected': True,
                'type': 'bullish_divergence',
                'signal': 'BUY',
                'confidence': min(1.0, volume_trend * 2),
                'description': 'Bullish divergence: price falling with increasing volume'
            }
        
        return {'detected': False}
    
    def _detect_distribution_accumulation(self, df: pd.DataFrame) -> Dict:
        """Detect distribution and accumulation patterns"""
        # Calculate A/D line
        ad_line = self._calculate_ad_line(df)
        price = df['close']
        
        # Trend analysis
        ad_trend = ad_line.iloc[-1] - ad_line.iloc[-10] if len(ad_line) >= 10 else 0
        price_trend = price.iloc[-1] - price.iloc[-10] if len(price) >= 10 else 0
        
        # Accumulation: A/D line rising
        if ad_trend > 0 and price_trend <= 0:
            return {
                'detected': True,
                'type': 'accumulation',
                'signal': 'BUY',
                'confidence': min(1.0, abs(ad_trend) / 1000000),  # Adjust scale
                'description': 'Accumulation pattern: A/D line rising despite price'
            }
        
        # Distribution: A/D line falling
        elif ad_trend < 0 and price_trend >= 0:
            return {
                'detected': True,
                'type': 'distribution',
                'signal': 'SELL',
                'confidence': min(1.0, abs(ad_trend) / 1000000),  # Adjust scale
                'description': 'Distribution pattern: A/D line falling despite price'
            }
        
        return {'detected': False}
    
    def _detect_volume_breakout(self, df: pd.DataFrame) -> Dict:
        """Detect volume-confirmed breakouts"""
        volume = df['volume']
        price = df['close']
        
        # Calculate recent breakout
        price_range_20 = price.rolling(20).max() - price.rolling(20).min()
        recent_range = price_range_20.iloc[-1]
        current_price = price.iloc[-1]
        
        # Check for breakout
        resistance = price.rolling(20).max().iloc[-2]  # Previous high
        support = price.rolling(20).min().iloc[-2]  # Previous low
        
        current_volume = volume.iloc[-1]
        avg_volume = volume.rolling(20).mean().iloc[-1]
        
        # Upward breakout with volume
        if current_price > resistance * 1.005 and current_volume > avg_volume * 1.5:
            return {
                'detected': True,
                'type': 'upward_breakout',
                'signal': 'BUY',
                'confidence': min(1.0, (current_volume / avg_volume - 1.5) / 2),
                'description': f'Upward breakout with {current_volume/avg_volume:.1f}x volume'
            }
        
        # Downward breakout with volume
        elif current_price < support * 0.995 and current_volume > avg_volume * 1.5:
            return {
                'detected': True,
                'type': 'downward_breakout',
                'signal': 'SELL',
                'confidence': min(1.0, (current_volume / avg_volume - 1.5) / 2),
                'description': f'Downward breakout with {current_volume/avg_volume:.1f}x volume'
            }
        
        return {'detected': False}
    
    # =============================================================================
    # HELPER METHODS
    # =============================================================================
    
    def _generate_volume_signals(self, volume_ratios: Dict, pvi: pd.Series, nvi: pd.Series,
                                vw_rsi: pd.Series, eom: pd.Series, cmf: pd.Series,
                                force_index: pd.Series, df: pd.DataFrame) -> Dict:
        """Generate composite volume signals"""
        
        signals = []
        confidences = []
        
        # Volume surge analysis
        if volume_ratios['current_vs_avg'] > 2.0:
            # High volume - check direction
            price_change = (df['close'].iloc[-1] - df['close'].iloc[-2]) / df['close'].iloc[-2]
            if price_change > 0.005:  # Price up with volume
                signals.append('BUY')
                confidences.append(min(1.0, volume_ratios['current_vs_avg'] * 0.2))
            elif price_change < -0.005:  # Price down with volume
                signals.append('SELL')
                confidences.append(min(1.0, volume_ratios['current_vs_avg'] * 0.2))
        
        # Volume-weighted RSI
        if len(vw_rsi) > 0:
            vw_rsi_val = vw_rsi.iloc[-1]
            if vw_rsi_val < 25:
                signals.append('BUY')
                confidences.append((25 - vw_rsi_val) / 25)
            elif vw_rsi_val > 75:
                signals.append('SELL')
                confidences.append((vw_rsi_val - 75) / 25)
        
        # Chaikin Money Flow
        if len(cmf) > 0:
            cmf_val = cmf.iloc[-1]
            if cmf_val > 0.2:
                signals.append('BUY')
                confidences.append(min(1.0, cmf_val * 2))
            elif cmf_val < -0.2:
                signals.append('SELL')
                confidences.append(min(1.0, abs(cmf_val) * 2))
        
        # Force Index
        if len(force_index) > 0:
            fi_val = force_index.iloc[-1]
            if fi_val > 0:
                signals.append('BUY')
                confidences.append(min(1.0, abs(fi_val) / 100000))  # Adjust scale
            elif fi_val < 0:
                signals.append('SELL')
                confidences.append(min(1.0, abs(fi_val) / 100000))
        
        # Determine primary signal
        buy_votes = signals.count('BUY')
        sell_votes = signals.count('SELL')
        
        if buy_votes > sell_votes:
            primary_signal = 'BUY'
            confidence = np.mean([c for i, c in enumerate(confidences) if signals[i] == 'BUY'])
        elif sell_votes > buy_votes:
            primary_signal = 'SELL'
            confidence = np.mean([c for i, c in enumerate(confidences) if signals[i] == 'SELL'])
        else:
            primary_signal = 'HOLD'
            confidence = 0.0
        
        return {
            'primary_signal': primary_signal,
            'confidence': confidence,
            'institutional_flow': 'accumulation' if buy_votes > sell_votes else 'distribution' if sell_votes > buy_votes else 'neutral',
            'retail_sentiment': 'bullish' if volume_ratios['current_vs_avg'] > 1.5 and buy_votes > 0 else 'bearish' if volume_ratios['current_vs_avg'] > 1.5 and sell_votes > 0 else 'neutral',
            'details': {
                'buy_signals': buy_votes,
                'sell_signals': sell_votes,
                'signal_breakdown': list(zip(signals, confidences))
            }
        }
    
    def _get_volume_trend(self, volume: pd.Series) -> str:
        """Determine volume trend"""
        if len(volume) < 10:
            return 'insufficient_data'
        
        recent_avg = volume.tail(5).mean()
        earlier_avg = volume.iloc[-10:-5].mean()
        
        if recent_avg > earlier_avg * 1.2:
            return 'increasing'
        elif recent_avg < earlier_avg * 0.8:
            return 'decreasing'
        else:
            return 'stable'
    
    def _calculate_ad_line(self, df: pd.DataFrame) -> pd.Series:
        """Calculate Accumulation/Distribution Line"""
        money_flow_multiplier = ((df['close'] - df['low']) - (df['high'] - df['close'])) / (df['high'] - df['low'])
        money_flow_volume = money_flow_multiplier * df['volume']
        return money_flow_volume.cumsum()
    
    def _create_simple_volume_profile(self, df: pd.DataFrame) -> Dict:
        """Create simplified volume profile"""
        # Divide price range into bins
        price_min = df['low'].min()
        price_max = df['high'].max()
        price_range = price_max - price_min
        
        if price_range == 0:
            return {'poc': df['close'].iloc[-1], 'vah': price_max, 'val': price_min}
        
        # Simple volume at price calculation
        volume_at_price = {}
        for i in range(len(df)):
            price_level = round((df['close'].iloc[i] - price_min) / price_range * 20) / 20  # 20 bins
            if price_level not in volume_at_price:
                volume_at_price[price_level] = 0
            volume_at_price[price_level] += df['volume'].iloc[i]
        
        # Find Point of Control (highest volume)
        poc_level = max(volume_at_price.keys(), key=lambda x: volume_at_price[x])
        poc_price = price_min + poc_level * price_range
        
        # Simple value area (70% of volume around POC)
        total_volume = sum(volume_at_price.values())
        target_volume = total_volume * 0.7
        
        vah = poc_price
        val = poc_price
        accumulated_volume = volume_at_price[poc_level]
        
        # Expand around POC
        levels = sorted(volume_at_price.keys())
        poc_idx = levels.index(poc_level)
        
        i = 1
        while accumulated_volume < target_volume and (poc_idx - i >= 0 or poc_idx + i < len(levels)):
            if poc_idx + i < len(levels):
                level = levels[poc_idx + i]
                accumulated_volume += volume_at_price[level]
                vah = price_min + level * price_range
            if poc_idx - i >= 0:
                level = levels[poc_idx - i]
                accumulated_volume += volume_at_price[level]
                val = price_min + level * price_range
            i += 1
        
        return {
            'poc': poc_price,
            'vah': vah,
            'val': val
        }
    
    def _detect_absorption(self, df: pd.DataFrame) -> Dict:
        """Detect volume absorption patterns"""
        volume = df['volume']
        price_range = df['high'] - df['low']
        
        # High volume with small price movement indicates absorption
        avg_volume = volume.rolling(10).mean()
        avg_range = price_range.rolling(10).mean()
        
        current_volume = volume.iloc[-1]
        current_range = price_range.iloc[-1]
        
        # Absorption thresholds
        volume_threshold = avg_volume.iloc[-1] * 2
        range_threshold = avg_range.iloc[-1] * 0.5
        
        buying_absorption = (current_volume > volume_threshold and 
                           current_range < range_threshold and 
                           df['close'].iloc[-1] > df['open'].iloc[-1])
        
        selling_absorption = (current_volume > volume_threshold and 
                            current_range < range_threshold and 
                            df['close'].iloc[-1] < df['open'].iloc[-1])
        
        strength = min(1.0, (current_volume / avg_volume.iloc[-1] - 2) / 3) if current_volume > volume_threshold else 0
        
        return {
            'buying_absorption': buying_absorption,
            'selling_absorption': selling_absorption,
            'strength': strength
        }
    
    def _detect_order_imbalance(self, df: pd.DataFrame) -> Dict:
        """Detect order flow imbalances"""
        # Simplified imbalance detection using price action
        delta = self._calculate_price_volume_delta(df)
        
        # Recent imbalance
        recent_delta = delta.tail(5).sum()
        total_volume = df['volume'].tail(5).sum()
        
        if total_volume > 0:
            imbalance_ratio = recent_delta / total_volume
        else:
            imbalance_ratio = 0
        
        return {
            'imbalance_ratio': imbalance_ratio,
            'direction': 'buy_side' if imbalance_ratio > 0.2 else 'sell_side' if imbalance_ratio < -0.2 else 'balanced',
            'strength': min(1.0, abs(imbalance_ratio) * 5)
        }
