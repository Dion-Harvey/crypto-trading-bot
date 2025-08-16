#!/usr/bin/env python3
"""
🎯 PHASE 3 WEEK 2: ADVANCED PATTERN RECOGNITION AI
=================================================

Chart Pattern Recognition System for Crypto Trading
- Head & Shoulders, Triangles, Flags, Wedges
- Volume Pattern Analysis  
- Support/Resistance Level Detection
- Breakout Prediction with Timing
- Pattern Confidence Scoring (0-100%)

Technology Stack: OpenCV + scikit-learn + NumPy (100% FREE)
Monthly Cost: $0 - Pure CPU processing
Performance Target: +8-12% signal accuracy improvement

Integrates with existing LSTM AI for compound intelligence.
"""

import numpy as np
import pandas as pd
import cv2
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from scipy.signal import find_peaks, argrelextrema
from scipy.stats import linregress
import warnings
warnings.filterwarnings('ignore')

class PatternRecognitionAI:
    """
    🧠 Advanced Pattern Recognition AI Engine
    
    Detects chart patterns, support/resistance levels, and predicts breakouts
    using computer vision and machine learning techniques.
    """
    
    def __init__(self, config=None):
        self.config = config or {}
        self.pattern_memory = {}  # Store recent patterns for trend analysis
        self.support_resistance_levels = {}  # Cache S/R levels
        self.pattern_confidence_threshold = 65  # Minimum confidence for pattern signals
        
        # Pattern detection parameters
        self.min_pattern_length = 20  # Minimum candles for pattern
        self.max_pattern_length = 100  # Maximum candles for pattern
        self.volume_confirmation_threshold = 1.2  # 20% above average volume
        
        print("✅ 🎯 Phase 3 Week 2: Pattern Recognition AI initialized!")
        print("🔍 Features: Chart patterns, S/R levels, breakout prediction")
        print("💰 Cost: $0 - OpenCV + scikit-learn")
    
    def analyze_chart_patterns(self, df, symbol='BTC/USDT'):
        """
        🔍 COMPREHENSIVE CHART PATTERN ANALYSIS
        
        Detects multiple pattern types and returns confidence-scored signals.
        """
        try:
            if len(df) < self.min_pattern_length:
                return {'patterns': [], 'confidence': 0, 'action': 'HOLD'}
            
            patterns_detected = []
            overall_confidence = 0
            
            # 1. HEAD & SHOULDERS PATTERN
            h_s_pattern = self._detect_head_shoulders(df)
            if h_s_pattern['confidence'] > 50:
                patterns_detected.append(h_s_pattern)
                overall_confidence += h_s_pattern['confidence'] * 0.3
            
            # 2. TRIANGLE PATTERNS
            triangle_pattern = self._detect_triangles(df)
            if triangle_pattern['confidence'] > 50:
                patterns_detected.append(triangle_pattern)
                overall_confidence += triangle_pattern['confidence'] * 0.25
            
            # 3. FLAG & PENNANT PATTERNS
            flag_pattern = self._detect_flags_pennants(df)
            if flag_pattern['confidence'] > 50:
                patterns_detected.append(flag_pattern)
                overall_confidence += flag_pattern['confidence'] * 0.2
            
            # 4. WEDGE PATTERNS
            wedge_pattern = self._detect_wedges(df)
            if wedge_pattern['confidence'] > 50:
                patterns_detected.append(wedge_pattern)
                overall_confidence += wedge_pattern['confidence'] * 0.15
            
            # 5. DOUBLE TOP/BOTTOM
            double_pattern = self._detect_double_top_bottom(df)
            if double_pattern['confidence'] > 50:
                patterns_detected.append(double_pattern)
                overall_confidence += double_pattern['confidence'] * 0.1
            
            # Determine overall action based on pattern consensus
            bullish_patterns = [p for p in patterns_detected if p['direction'] == 'bullish']
            bearish_patterns = [p for p in patterns_detected if p['direction'] == 'bearish']
            
            if len(bullish_patterns) > len(bearish_patterns):
                action = 'BUY'
            elif len(bearish_patterns) > len(bullish_patterns):
                action = 'SELL'
            else:
                action = 'HOLD'
            
            # Cap confidence at 95% to leave room for other signals
            final_confidence = min(overall_confidence, 95) / 100
            
            return {
                'patterns': patterns_detected,
                'confidence': final_confidence,
                'action': action,
                'pattern_count': len(patterns_detected),
                'symbol': symbol,
                'analysis_timestamp': pd.Timestamp.now()
            }
            
        except Exception as e:
            print(f"⚠️ Pattern analysis error for {symbol}: {e}")
            return {'patterns': [], 'confidence': 0, 'action': 'HOLD'}
    
    def _detect_head_shoulders(self, df):
        """
        🔍 HEAD & SHOULDERS PATTERN DETECTION
        
        Detects both regular and inverted head & shoulders patterns.
        """
        try:
            prices = df['close'].values
            highs = df['high'].values
            lows = df['low'].values
            
            # Find peaks and troughs
            peaks, _ = find_peaks(highs, distance=5)
            troughs, _ = find_peaks(-lows, distance=5)
            
            if len(peaks) < 3:
                return {'pattern': 'head_shoulders', 'confidence': 0, 'direction': 'neutral'}
            
            # Look for classic H&S pattern (3 peaks with middle being highest)
            for i in range(len(peaks) - 2):
                peak1, peak2, peak3 = peaks[i], peaks[i+1], peaks[i+2]
                
                # Check if middle peak is higher (head)
                if highs[peak2] > highs[peak1] and highs[peak2] > highs[peak3]:
                    # Check if shoulders are roughly equal
                    shoulder_diff = abs(highs[peak1] - highs[peak3]) / highs[peak2]
                    
                    if shoulder_diff < 0.1:  # Shoulders within 10% of each other
                        # Calculate neckline
                        if len(troughs) >= 2:
                            relevant_troughs = [t for t in troughs if peak1 < t < peak3]
                            if len(relevant_troughs) >= 2:
                                neckline_level = np.mean([lows[t] for t in relevant_troughs[:2]])
                                current_price = prices[-1]
                                
                                # Pattern confidence based on symmetry and volume
                                symmetry_score = (1 - shoulder_diff) * 100
                                volume_confirmation = self._check_volume_confirmation(df, peak2)
                                
                                confidence = min(85, symmetry_score + volume_confirmation)
                                
                                return {
                                    'pattern': 'head_shoulders',
                                    'confidence': confidence,
                                    'direction': 'bearish',
                                    'neckline': neckline_level,
                                    'target': neckline_level - (highs[peak2] - neckline_level),
                                    'current_price': current_price,
                                    'breakout_imminent': current_price < neckline_level * 1.02
                                }
            
            # Check for inverted head & shoulders
            if len(troughs) >= 3:
                for i in range(len(troughs) - 2):
                    trough1, trough2, trough3 = troughs[i], troughs[i+1], troughs[i+2]
                    
                    if lows[trough2] < lows[trough1] and lows[trough2] < lows[trough3]:
                        shoulder_diff = abs(lows[trough1] - lows[trough3]) / lows[trough2]
                        
                        if shoulder_diff < 0.1:
                            # Find neckline
                            relevant_peaks = [p for p in peaks if trough1 < p < trough3]
                            if len(relevant_peaks) >= 2:
                                neckline_level = np.mean([highs[p] for p in relevant_peaks[:2]])
                                current_price = prices[-1]
                                
                                symmetry_score = (1 - shoulder_diff) * 100
                                volume_confirmation = self._check_volume_confirmation(df, trough2)
                                
                                confidence = min(85, symmetry_score + volume_confirmation)
                                
                                return {
                                    'pattern': 'inverted_head_shoulders',
                                    'confidence': confidence,
                                    'direction': 'bullish',
                                    'neckline': neckline_level,
                                    'target': neckline_level + (neckline_level - lows[trough2]),
                                    'current_price': current_price,
                                    'breakout_imminent': current_price > neckline_level * 0.98
                                }
            
            return {'pattern': 'head_shoulders', 'confidence': 0, 'direction': 'neutral'}
            
        except Exception as e:
            return {'pattern': 'head_shoulders', 'confidence': 0, 'direction': 'neutral'}
    
    def _detect_triangles(self, df):
        """
        🔺 TRIANGLE PATTERN DETECTION
        
        Detects ascending, descending, and symmetrical triangles.
        """
        try:
            prices = df['close'].values
            highs = df['high'].values
            lows = df['low'].values
            
            if len(df) < 30:
                return {'pattern': 'triangle', 'confidence': 0, 'direction': 'neutral'}
            
            # Use recent 30-50 candles for triangle detection
            recent_data = df.tail(40)
            recent_highs = recent_data['high'].values
            recent_lows = recent_data['low'].values
            
            # Find peaks and troughs in recent data
            peaks, _ = find_peaks(recent_highs, distance=3)
            troughs, _ = find_peaks(-recent_lows, distance=3)
            
            if len(peaks) >= 2 and len(troughs) >= 2:
                # Calculate trend lines
                peak_times = peaks
                peak_prices = recent_highs[peaks]
                trough_times = troughs
                trough_prices = recent_lows[troughs]
                
                # Linear regression for trend lines
                if len(peak_times) >= 2:
                    peak_slope, peak_intercept, peak_r_value, _, _ = linregress(peak_times, peak_prices)
                    
                if len(trough_times) >= 2:
                    trough_slope, trough_intercept, trough_r_value, _, _ = linregress(trough_times, trough_prices)
                
                # Determine triangle type
                if len(peak_times) >= 2 and len(trough_times) >= 2:
                    # Check line quality (R-squared > 0.5 for good fit)
                    if peak_r_value**2 > 0.5 and trough_r_value**2 > 0.5:
                        current_price = prices[-1]
                        
                        # Ascending Triangle: Flat resistance, rising support
                        if abs(peak_slope) < 0.1 and trough_slope > 0.1:
                            resistance_level = np.mean(peak_prices)
                            confidence = min(80, (peak_r_value**2 + trough_r_value**2) * 50)
                            
                            return {
                                'pattern': 'ascending_triangle',
                                'confidence': confidence,
                                'direction': 'bullish',
                                'resistance': resistance_level,
                                'support_slope': trough_slope,
                                'breakout_target': resistance_level * 1.05,
                                'breakout_imminent': current_price > resistance_level * 0.98
                            }
                        
                        # Descending Triangle: Falling resistance, flat support
                        elif peak_slope < -0.1 and abs(trough_slope) < 0.1:
                            support_level = np.mean(trough_prices)
                            confidence = min(80, (peak_r_value**2 + trough_r_value**2) * 50)
                            
                            return {
                                'pattern': 'descending_triangle',
                                'confidence': confidence,
                                'direction': 'bearish',
                                'support': support_level,
                                'resistance_slope': peak_slope,
                                'breakout_target': support_level * 0.95,
                                'breakout_imminent': current_price < support_level * 1.02
                            }
                        
                        # Symmetrical Triangle: Converging lines
                        elif peak_slope < -0.05 and trough_slope > 0.05:
                            apex_distance = self._calculate_triangle_apex(peak_times, peak_prices, trough_times, trough_prices)
                            confidence = min(75, (peak_r_value**2 + trough_r_value**2) * 40)
                            
                            return {
                                'pattern': 'symmetrical_triangle',
                                'confidence': confidence,
                                'direction': 'neutral',  # Direction depends on breakout
                                'apex_distance': apex_distance,
                                'convergence_zone': (np.mean(peak_prices[-2:]) + np.mean(trough_prices[-2:])) / 2,
                                'breakout_imminent': apex_distance < 5
                            }
            
            return {'pattern': 'triangle', 'confidence': 0, 'direction': 'neutral'}
            
        except Exception as e:
            return {'pattern': 'triangle', 'confidence': 0, 'direction': 'neutral'}
    
    def _detect_flags_pennants(self, df):
        """
        🚩 FLAG & PENNANT PATTERN DETECTION
        
        Detects continuation patterns after strong moves.
        """
        try:
            if len(df) < 25:
                return {'pattern': 'flag', 'confidence': 0, 'direction': 'neutral'}
            
            prices = df['close'].values
            volumes = df['volume'].values if 'volume' in df.columns else np.ones(len(df))
            
            # Look for strong initial move (flagpole)
            recent_data = df.tail(25)
            flagpole_start = len(recent_data) - 20
            flagpole_end = len(recent_data) - 15
            consolidation_start = flagpole_end
            
            if flagpole_start >= 0 and consolidation_start < len(recent_data):
                # Calculate flagpole move
                flagpole_move = (recent_data.iloc[flagpole_end]['close'] - 
                               recent_data.iloc[flagpole_start]['close']) / recent_data.iloc[flagpole_start]['close']
                
                # Require significant move (>2%) for flagpole
                if abs(flagpole_move) > 0.02:
                    # Analyze consolidation period
                    consolidation_data = recent_data.iloc[consolidation_start:]
                    consolidation_range = (consolidation_data['high'].max() - 
                                         consolidation_data['low'].min()) / consolidation_data['close'].mean()
                    
                    # Flag: consolidation range should be small relative to flagpole
                    if consolidation_range < abs(flagpole_move) * 0.5:
                        # Check for decreasing volume during consolidation
                        early_volumes = volumes[consolidation_start:consolidation_start+3]
                        late_volumes = volumes[-3:]
                        
                        volume_decrease = np.mean(late_volumes) < np.mean(early_volumes) * 0.8
                        
                        # Calculate confidence
                        range_score = (1 - consolidation_range / abs(flagpole_move)) * 50
                        volume_score = 20 if volume_decrease else 10
                        move_score = min(30, abs(flagpole_move) * 1000)
                        
                        confidence = min(85, range_score + volume_score + move_score)
                        
                        if confidence > 50:
                            direction = 'bullish' if flagpole_move > 0 else 'bearish'
                            current_price = prices[-1]
                            
                            # Calculate breakout target
                            if direction == 'bullish':
                                breakout_target = current_price * (1 + abs(flagpole_move))
                                resistance = consolidation_data['high'].max()
                                breakout_imminent = current_price > resistance * 0.99
                            else:
                                breakout_target = current_price * (1 - abs(flagpole_move))
                                support = consolidation_data['low'].min()
                                breakout_imminent = current_price < support * 1.01
                            
                            return {
                                'pattern': 'flag',
                                'confidence': confidence,
                                'direction': direction,
                                'flagpole_move': flagpole_move,
                                'consolidation_range': consolidation_range,
                                'breakout_target': breakout_target,
                                'breakout_imminent': breakout_imminent
                            }
            
            return {'pattern': 'flag', 'confidence': 0, 'direction': 'neutral'}
            
        except Exception as e:
            return {'pattern': 'flag', 'confidence': 0, 'direction': 'neutral'}
    
    def _detect_wedges(self, df):
        """
        🔻 WEDGE PATTERN DETECTION
        
        Detects rising and falling wedge patterns.
        """
        try:
            if len(df) < 30:
                return {'pattern': 'wedge', 'confidence': 0, 'direction': 'neutral'}
            
            recent_data = df.tail(35)
            highs = recent_data['high'].values
            lows = recent_data['low'].values
            
            # Find peaks and troughs
            peaks, _ = find_peaks(highs, distance=3)
            troughs, _ = find_peaks(-lows, distance=3)
            
            if len(peaks) >= 3 and len(troughs) >= 3:
                # Calculate trend lines for recent peaks and troughs
                peak_times = peaks[-3:]
                peak_prices = highs[peak_times]
                trough_times = troughs[-3:]
                trough_prices = lows[trough_times]
                
                if len(peak_times) >= 2 and len(trough_times) >= 2:
                    peak_slope, _, peak_r_value, _, _ = linregress(peak_times, peak_prices)
                    trough_slope, _, trough_r_value, _, _ = linregress(trough_times, trough_prices)
                    
                    # Check for converging lines (both should trend in same direction)
                    if peak_r_value**2 > 0.4 and trough_r_value**2 > 0.4:
                        # Rising Wedge: Both lines rising, but resistance rises slower
                        if peak_slope > 0 and trough_slope > 0 and peak_slope < trough_slope:
                            confidence = min(75, (peak_r_value**2 + trough_r_value**2) * 45)
                            
                            return {
                                'pattern': 'rising_wedge',
                                'confidence': confidence,
                                'direction': 'bearish',  # Rising wedges are bearish
                                'resistance_slope': peak_slope,
                                'support_slope': trough_slope,
                                'apex_approaching': True
                            }
                        
                        # Falling Wedge: Both lines falling, but support falls faster
                        elif peak_slope < 0 and trough_slope < 0 and peak_slope > trough_slope:
                            confidence = min(75, (peak_r_value**2 + trough_r_value**2) * 45)
                            
                            return {
                                'pattern': 'falling_wedge',
                                'confidence': confidence,
                                'direction': 'bullish',  # Falling wedges are bullish
                                'resistance_slope': peak_slope,
                                'support_slope': trough_slope,
                                'apex_approaching': True
                            }
            
            return {'pattern': 'wedge', 'confidence': 0, 'direction': 'neutral'}
            
        except Exception as e:
            return {'pattern': 'wedge', 'confidence': 0, 'direction': 'neutral'}
    
    def _detect_double_top_bottom(self, df):
        """
        🔄 DOUBLE TOP/BOTTOM PATTERN DETECTION
        
        Detects classic reversal patterns.
        """
        try:
            if len(df) < 25:
                return {'pattern': 'double', 'confidence': 0, 'direction': 'neutral'}
            
            highs = df['high'].values
            lows = df['low'].values
            
            # Find significant peaks and troughs
            peaks, _ = find_peaks(highs, distance=5, height=np.percentile(highs, 70))
            troughs, _ = find_peaks(-lows, distance=5)
            
            # Double Top Detection
            if len(peaks) >= 2:
                for i in range(len(peaks) - 1):
                    peak1, peak2 = peaks[i], peaks[i + 1]
                    
                    # Check if peaks are similar height (within 2%)
                    height_diff = abs(highs[peak1] - highs[peak2]) / max(highs[peak1], highs[peak2])
                    
                    if height_diff < 0.02 and (peak2 - peak1) > 10:  # Sufficient time between peaks
                        # Find valley between peaks
                        valley_start, valley_end = peak1, peak2
                        valley_data = df.iloc[valley_start:valley_end+1]
                        valley_low = valley_data['low'].min()
                        
                        # Calculate neckline and confirmation
                        neckline = valley_low
                        current_price = df['close'].iloc[-1]
                        
                        # Pattern strength based on depth and symmetry
                        depth = (min(highs[peak1], highs[peak2]) - valley_low) / min(highs[peak1], highs[peak2])
                        symmetry_score = (1 - height_diff) * 100
                        
                        if depth > 0.03:  # Minimum 3% retracement
                            confidence = min(80, symmetry_score + depth * 1000)
                            
                            return {
                                'pattern': 'double_top',
                                'confidence': confidence,
                                'direction': 'bearish',
                                'neckline': neckline,
                                'target': neckline - (min(highs[peak1], highs[peak2]) - neckline),
                                'breakout_imminent': current_price < neckline * 1.01
                            }
            
            # Double Bottom Detection
            if len(troughs) >= 2:
                for i in range(len(troughs) - 1):
                    trough1, trough2 = troughs[i], troughs[i + 1]
                    
                    height_diff = abs(lows[trough1] - lows[trough2]) / max(lows[trough1], lows[trough2])
                    
                    if height_diff < 0.02 and (trough2 - trough1) > 10:
                        # Find peak between troughs
                        peak_start, peak_end = trough1, trough2
                        peak_data = df.iloc[peak_start:peak_end+1]
                        peak_high = peak_data['high'].max()
                        
                        neckline = peak_high
                        current_price = df['close'].iloc[-1]
                        
                        depth = (neckline - max(lows[trough1], lows[trough2])) / neckline
                        symmetry_score = (1 - height_diff) * 100
                        
                        if depth > 0.03:
                            confidence = min(80, symmetry_score + depth * 1000)
                            
                            return {
                                'pattern': 'double_bottom',
                                'confidence': confidence,
                                'direction': 'bullish',
                                'neckline': neckline,
                                'target': neckline + (neckline - max(lows[trough1], lows[trough2])),
                                'breakout_imminent': current_price > neckline * 0.99
                            }
            
            return {'pattern': 'double', 'confidence': 0, 'direction': 'neutral'}
            
        except Exception as e:
            return {'pattern': 'double', 'confidence': 0, 'direction': 'neutral'}
    
    def detect_support_resistance_levels(self, df, symbol='BTC/USDT'):
        """
        📊 DYNAMIC SUPPORT & RESISTANCE LEVEL DETECTION
        
        Uses clustering to identify key price levels.
        """
        try:
            if len(df) < 50:
                return {'support_levels': [], 'resistance_levels': [], 'confidence': 0}
            
            highs = df['high'].values
            lows = df['low'].values
            volumes = df['volume'].values if 'volume' in df.columns else np.ones(len(df))
            
            # Combine significant highs and lows
            peaks, _ = find_peaks(highs, distance=3)
            troughs, _ = find_peaks(-lows, distance=3)
            
            # Create price points with volumes as weights
            price_points = []
            weights = []
            
            for peak in peaks:
                price_points.append(highs[peak])
                weights.append(volumes[peak])
            
            for trough in troughs:
                price_points.append(lows[trough])
                weights.append(volumes[trough])
            
            if len(price_points) < 5:
                return {'support_levels': [], 'resistance_levels': [], 'confidence': 0}
            
            # Use DBSCAN clustering to find price levels
            price_array = np.array(price_points).reshape(-1, 1)
            
            # Scale prices for clustering
            scaler = StandardScaler()
            scaled_prices = scaler.fit_transform(price_array)
            
            # Cluster similar price levels
            clustering = DBSCAN(eps=0.3, min_samples=2).fit(scaled_prices)
            labels = clustering.labels_
            
            # Extract significant levels
            current_price = df['close'].iloc[-1]
            support_levels = []
            resistance_levels = []
            
            for label in set(labels):
                if label != -1:  # Ignore noise points
                    cluster_points = [price_points[i] for i in range(len(price_points)) if labels[i] == label]
                    cluster_weights = [weights[i] for i in range(len(weights)) if labels[i] == label]
                    
                    # Weighted average for level
                    level = np.average(cluster_points, weights=cluster_weights)
                    strength = len(cluster_points) * np.mean(cluster_weights)
                    
                    # Classify as support or resistance
                    if level < current_price:
                        support_levels.append({'level': level, 'strength': strength, 'touches': len(cluster_points)})
                    else:
                        resistance_levels.append({'level': level, 'strength': strength, 'touches': len(cluster_points)})
            
            # Sort by strength
            support_levels.sort(key=lambda x: x['strength'], reverse=True)
            resistance_levels.sort(key=lambda x: x['strength'], reverse=True)
            
            # Calculate overall confidence based on level quality
            total_levels = len(support_levels) + len(resistance_levels)
            confidence = min(90, total_levels * 10 + np.mean([level['touches'] for level in support_levels + resistance_levels]) * 5)
            
            return {
                'support_levels': support_levels[:5],  # Top 5 support levels
                'resistance_levels': resistance_levels[:5],  # Top 5 resistance levels
                'confidence': confidence,
                'current_price': current_price,
                'symbol': symbol
            }
            
        except Exception as e:
            print(f"⚠️ S/R level detection error for {symbol}: {e}")
            return {'support_levels': [], 'resistance_levels': [], 'confidence': 0}
    
    def predict_breakout_probability(self, df, patterns, sr_levels, symbol='BTC/USDT'):
        """
        🎯 BREAKOUT PREDICTION ENGINE
        
        Combines pattern analysis with S/R levels to predict breakout timing and direction.
        """
        try:
            current_price = df['close'].iloc[-1]
            recent_volume = df['volume'].iloc[-10:].mean() if 'volume' in df.columns else 1
            avg_volume = df['volume'].iloc[-50:].mean() if 'volume' in df.columns else 1
            
            breakout_signals = []
            
            # 1. Pattern-based breakout signals
            for pattern in patterns['patterns']:
                if pattern.get('breakout_imminent', False):
                    breakout_signals.append({
                        'type': 'pattern',
                        'source': pattern['pattern'],
                        'direction': pattern['direction'],
                        'confidence': pattern['confidence'],
                        'target': pattern.get('target', current_price * 1.05),
                        'timeframe': 'immediate'
                    })
            
            # 2. Support/Resistance breakout signals
            for resistance in sr_levels['resistance_levels'][:2]:  # Check top 2 resistance levels
                distance_to_resistance = (resistance['level'] - current_price) / current_price
                if 0 < distance_to_resistance < 0.02:  # Within 2% of resistance
                    volume_surge = recent_volume > avg_volume * 1.3
                    
                    if volume_surge:
                        breakout_signals.append({
                            'type': 'resistance_breakout',
                            'source': f"R-Level: ${resistance['level']:.2f}",
                            'direction': 'bullish',
                            'confidence': min(85, resistance['strength'] / 1000 + 30),
                            'target': resistance['level'] * 1.05,
                            'timeframe': 'short_term'
                        })
            
            for support in sr_levels['support_levels'][:2]:  # Check top 2 support levels
                distance_to_support = (current_price - support['level']) / current_price
                if 0 < distance_to_support < 0.02:  # Within 2% of support
                    volume_surge = recent_volume > avg_volume * 1.3
                    
                    if volume_surge:
                        breakout_signals.append({
                            'type': 'support_breakdown',
                            'source': f"S-Level: ${support['level']:.2f}",
                            'direction': 'bearish',
                            'confidence': min(85, support['strength'] / 1000 + 30),
                            'target': support['level'] * 0.95,
                            'timeframe': 'short_term'
                        })
            
            # 3. Volume-based momentum breakout
            if recent_volume > avg_volume * 2:  # 100% volume increase
                price_momentum = (current_price - df['close'].iloc[-5]) / df['close'].iloc[-5]
                
                if abs(price_momentum) > 0.01:  # 1%+ move with volume
                    direction = 'bullish' if price_momentum > 0 else 'bearish'
                    breakout_signals.append({
                        'type': 'volume_momentum',
                        'source': 'High Volume + Price Movement',
                        'direction': direction,
                        'confidence': min(75, abs(price_momentum) * 5000),
                        'target': current_price * (1 + price_momentum * 2),
                        'timeframe': 'immediate'
                    })
            
            # Calculate overall breakout probability
            if breakout_signals:
                avg_confidence = np.mean([signal['confidence'] for signal in breakout_signals])
                signal_consensus = len(breakout_signals)
                
                # Bonus for multiple confirming signals
                consensus_bonus = min(20, signal_consensus * 5)
                overall_probability = min(95, avg_confidence + consensus_bonus)
                
                # Determine primary direction
                bullish_signals = [s for s in breakout_signals if s['direction'] == 'bullish']
                bearish_signals = [s for s in breakout_signals if s['direction'] == 'bearish']
                
                if len(bullish_signals) > len(bearish_signals):
                    primary_direction = 'bullish'
                elif len(bearish_signals) > len(bullish_signals):
                    primary_direction = 'bearish'
                else:
                    primary_direction = 'neutral'
                
                return {
                    'breakout_probability': overall_probability / 100,
                    'primary_direction': primary_direction,
                    'signals': breakout_signals,
                    'signal_count': len(breakout_signals),
                    'confidence_level': 'high' if overall_probability > 75 else 'medium' if overall_probability > 50 else 'low'
                }
            
            return {
                'breakout_probability': 0,
                'primary_direction': 'neutral',
                'signals': [],
                'signal_count': 0,
                'confidence_level': 'low'
            }
            
        except Exception as e:
            print(f"⚠️ Breakout prediction error for {symbol}: {e}")
            return {'breakout_probability': 0, 'primary_direction': 'neutral', 'signals': []}
    
    def enhance_signal_with_patterns(self, base_signal, df, symbol='BTC/USDT'):
        """
        🎯 SIGNAL ENHANCEMENT WITH PATTERN RECOGNITION
        
        Enhances existing trading signals with pattern analysis.
        """
        try:
            # Run full pattern analysis
            patterns = self.analyze_chart_patterns(df, symbol)
            sr_levels = self.detect_support_resistance_levels(df, symbol)
            breakout_prediction = self.predict_breakout_probability(df, patterns, sr_levels, symbol)
            
            # Create enhanced signal
            enhanced_signal = base_signal.copy()
            
            # Pattern confirmation boost
            pattern_boost = 0
            if patterns['action'] == base_signal.get('action', 'HOLD'):
                pattern_boost = patterns['confidence'] * 0.15  # Up to 15% boost
            
            # Support/Resistance confirmation
            sr_boost = 0
            current_price = df['close'].iloc[-1]
            
            if base_signal.get('action') == 'BUY':
                # Check if we're near strong support
                for support in sr_levels['support_levels'][:2]:
                    distance = abs(current_price - support['level']) / current_price
                    if distance < 0.02:  # Within 2%
                        sr_boost += min(0.1, support['strength'] / 10000)
            
            elif base_signal.get('action') == 'SELL':
                # Check if we're near strong resistance
                for resistance in sr_levels['resistance_levels'][:2]:
                    distance = abs(current_price - resistance['level']) / current_price
                    if distance < 0.02:  # Within 2%
                        sr_boost += min(0.1, resistance['strength'] / 10000)
            
            # Breakout timing boost
            breakout_boost = 0
            if breakout_prediction['breakout_probability'] > 0.7:
                if breakout_prediction['primary_direction'] == 'bullish' and base_signal.get('action') == 'BUY':
                    breakout_boost = 0.1
                elif breakout_prediction['primary_direction'] == 'bearish' and base_signal.get('action') == 'SELL':
                    breakout_boost = 0.1
            
            # Apply enhancements
            original_confidence = base_signal.get('confidence', 0.5)
            total_boost = pattern_boost + sr_boost + breakout_boost
            enhanced_confidence = min(0.95, original_confidence + total_boost)
            
            enhanced_signal.update({
                'confidence': enhanced_confidence,
                'pattern_enhancement': pattern_boost,
                'sr_enhancement': sr_boost,
                'breakout_enhancement': breakout_boost,
                'pattern_analysis': patterns,
                'sr_levels': sr_levels,
                'breakout_prediction': breakout_prediction,
                'enhancement_applied': True
            })
            
            return enhanced_signal
            
        except Exception as e:
            print(f"⚠️ Pattern enhancement error for {symbol}: {e}")
            return base_signal
    
    def _check_volume_confirmation(self, df, index):
        """Check if volume confirms the pattern at given index"""
        try:
            if 'volume' not in df.columns:
                return 10  # Default score if no volume data
            
            volumes = df['volume'].values
            if index >= len(volumes):
                return 10
            
            current_volume = volumes[index]
            avg_volume = np.mean(volumes[max(0, index-20):index])
            
            if current_volume > avg_volume * self.volume_confirmation_threshold:
                return 25  # High volume confirmation
            elif current_volume > avg_volume:
                return 15  # Moderate volume confirmation
            else:
                return 5   # Low volume confirmation
                
        except:
            return 10
    
    def _calculate_triangle_apex(self, peak_times, peak_prices, trough_times, trough_prices):
        """Calculate distance to triangle apex convergence"""
        try:
            if len(peak_times) < 2 or len(trough_times) < 2:
                return float('inf')
            
            # Simple linear projection to find convergence point
            peak_slope = (peak_prices[-1] - peak_prices[0]) / (peak_times[-1] - peak_times[0])
            trough_slope = (trough_prices[-1] - trough_prices[0]) / (trough_times[-1] - trough_times[0])
            
            if peak_slope == trough_slope:
                return float('inf')  # Parallel lines
            
            # Find intersection point
            apex_time = ((trough_prices[0] - peak_prices[0]) + 
                        peak_slope * peak_times[0] - trough_slope * trough_times[0]) / (peak_slope - trough_slope)
            
            current_time = max(peak_times[-1], trough_times[-1])
            return max(0, apex_time - current_time)
            
        except:
            return float('inf')


def get_pattern_recognition_ai(config=None):
    """
    🎯 Factory function to get Pattern Recognition AI instance
    """
    return PatternRecognitionAI(config)


# Test function for pattern recognition
def test_pattern_recognition():
    """
    🧪 Test the pattern recognition system with sample data
    """
    try:
        print("🧪 Testing Pattern Recognition AI...")
        
        # Create sample data
        dates = pd.date_range(start='2025-01-01', periods=100, freq='1H')
        np.random.seed(42)
        
        # Generate price data with patterns
        base_price = 50000
        prices = [base_price]
        
        for i in range(99):
            # Add some trending and random components
            trend = 0.0001 * i
            noise = np.random.normal(0, 0.002)
            new_price = prices[-1] * (1 + trend + noise)
            prices.append(new_price)
        
        df = pd.DataFrame({
            'timestamp': dates,
            'open': prices,
            'high': [p * 1.01 for p in prices],
            'low': [p * 0.99 for p in prices],
            'close': prices,
            'volume': np.random.randint(1000, 5000, 100)
        })
        
        # Test pattern recognition
        pattern_ai = get_pattern_recognition_ai()
        
        patterns = pattern_ai.analyze_chart_patterns(df)
        sr_levels = pattern_ai.detect_support_resistance_levels(df)
        breakout_pred = pattern_ai.predict_breakout_probability(df, patterns, sr_levels)
        
        print(f"✅ Patterns detected: {len(patterns['patterns'])}")
        print(f"✅ S/R levels found: {len(sr_levels['support_levels']) + len(sr_levels['resistance_levels'])}")
        print(f"✅ Breakout probability: {breakout_pred['breakout_probability']:.1%}")
        print("🎯 Pattern Recognition AI test completed successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Pattern Recognition test failed: {e}")
        return False


if __name__ == "__main__":
    test_pattern_recognition()
