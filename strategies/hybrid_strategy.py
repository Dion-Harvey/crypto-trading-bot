#!/usr/bin/env python3
"""
Advanced Hybrid Strategy System
Dynamically switches between mean-reversion and trend-following based on market conditions
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import logging

class AdvancedHybridStrategy:
    """
    Adaptive strategy that switches between mean-reversion and trend-following
    based on real-time market regime detection
    """
    
    def __init__(self, adaptation_lookback: int = 50):
        self.adaptation_lookback = adaptation_lookback
        self.logger = logging.getLogger(__name__)
        
        # Strategy modes
        self.MEAN_REVERSION = "mean_reversion"
        self.TREND_FOLLOWING = "trend_following"
        self.NEUTRAL = "neutral"
        
        # Current mode tracking
        self.current_mode = self.NEUTRAL
        self.mode_confidence = 0.0
        self.mode_history = []
        
        # Performance tracking for each mode
        self.performance_tracker = {
            self.MEAN_REVERSION: {'wins': 0, 'losses': 0, 'total_return': 0.0},
            self.TREND_FOLLOWING: {'wins': 0, 'losses': 0, 'total_return': 0.0}
        }
        
    def get_adaptive_signal(self, df: pd.DataFrame, market_conditions: Optional[Dict] = None) -> Dict:
        """
        Generate adaptive signal based on current market regime
        """
        if len(df) < self.adaptation_lookback:
            return {
                'action': 'HOLD',
                'confidence': 0.0,
                'reason': 'Insufficient data for adaptive strategy',
                'mode': self.NEUTRAL,
                'regime_analysis': {}
            }
        
        # Detect current market regime
        regime_analysis = self._detect_market_regime(df)
        
        # Determine optimal strategy mode
        optimal_mode = self._determine_optimal_mode(regime_analysis, market_conditions)
        
        # Generate signal based on selected mode
        if optimal_mode == self.MEAN_REVERSION:
            signal = self._generate_mean_reversion_signal(df, regime_analysis)
        elif optimal_mode == self.TREND_FOLLOWING:
            signal = self._generate_trend_following_signal(df, regime_analysis)
        else:
            signal = self._generate_neutral_signal(df, regime_analysis)
        
        # Update mode tracking
        self._update_mode_tracking(optimal_mode, regime_analysis)
        
        # Add mode information to signal
        signal.update({
            'mode': optimal_mode,
            'mode_confidence': self.mode_confidence,
            'regime_analysis': regime_analysis,
            'performance_stats': self.performance_tracker.copy()
        })
        
        return signal
    
    def _detect_market_regime(self, df: pd.DataFrame) -> Dict:
        """
        Comprehensive market regime detection
        """
        # Price-based regime indicators
        returns = df['close'].pct_change().dropna()
        
        # 1. Trend Strength Analysis
        trend_analysis = self._analyze_trend_strength(df)
        
        # 2. Volatility Regime Analysis
        volatility_analysis = self._analyze_volatility_regime(returns)
        
        # 3. Mean Reversion Tendencies
        mean_reversion_analysis = self._analyze_mean_reversion_tendency(df)
        
        # 4. Market Microstructure
        microstructure_analysis = self._analyze_market_microstructure(df)
        
        # 5. Volume Pattern Analysis
        volume_analysis = self._analyze_volume_patterns(df)
        
        # 6. Price Action Patterns
        price_patterns = self._analyze_price_patterns(df)
        
        # Composite regime score
        regime_scores = self._calculate_regime_scores(
            trend_analysis, volatility_analysis, mean_reversion_analysis,
            microstructure_analysis, volume_analysis, price_patterns
        )
        
        return {
            'trend_analysis': trend_analysis,
            'volatility_analysis': volatility_analysis,
            'mean_reversion_analysis': mean_reversion_analysis,
            'microstructure_analysis': microstructure_analysis,
            'volume_analysis': volume_analysis,
            'price_patterns': price_patterns,
            'regime_scores': regime_scores,
            'dominant_regime': max(regime_scores.keys(), key=lambda k: regime_scores[k])
        }
    
    def _analyze_trend_strength(self, df: pd.DataFrame) -> Dict:
        """Analyze trend strength using multiple indicators"""
        
        # Multiple timeframe MAs
        ma_5 = df['close'].rolling(5).mean()
        ma_10 = df['close'].rolling(10).mean()
        ma_20 = df['close'].rolling(20).mean()
        ma_50 = df['close'].rolling(50).mean()
        
        current_price = df['close'].iloc[-1]
        
        # MA alignment score
        ma_alignment = 0
        mas = [ma_5.iloc[-1], ma_10.iloc[-1], ma_20.iloc[-1], ma_50.iloc[-1]]
        
        # Uptrend alignment
        if all(mas[i] > mas[i+1] for i in range(len(mas)-1)):
            ma_alignment = 1.0  # Perfect uptrend alignment
        elif all(mas[i] < mas[i+1] for i in range(len(mas)-1)):
            ma_alignment = -1.0  # Perfect downtrend alignment
        else:
            # Partial alignment
            upward_pairs = sum(1 for i in range(len(mas)-1) if mas[i] > mas[i+1])
            ma_alignment = (upward_pairs / (len(mas)-1)) * 2 - 1  # Normalize to [-1, 1]
        
        # Trend consistency (how long has trend been in place)
        trend_direction = np.sign(ma_5.iloc[-1] - ma_20.iloc[-1])
        consistency_periods = 0
        for i in range(1, min(20, len(df))):
            if np.sign(ma_5.iloc[-i] - ma_20.iloc[-i]) == trend_direction:
                consistency_periods += 1
            else:
                break
        
        trend_consistency = min(consistency_periods / 10, 1.0)  # Normalize to [0, 1]
        
        # Price momentum
        momentum_3 = (current_price - df['close'].iloc[-4]) / df['close'].iloc[-4] if len(df) >= 4 else 0
        momentum_10 = (current_price - df['close'].iloc[-11]) / df['close'].iloc[-11] if len(df) >= 11 else 0
        momentum_20 = (current_price - df['close'].iloc[-21]) / df['close'].iloc[-21] if len(df) >= 21 else 0
        
        # ADX-like calculation (simplified)
        high_low = df['high'] - df['low']
        high_close = abs(df['high'] - df['close'].shift(1))
        low_close = abs(df['low'] - df['close'].shift(1))
        
        true_range = np.maximum(high_low, np.maximum(high_close, low_close))
        atr = true_range.rolling(14).mean()
        
        plus_dm = np.where((df['high'] - df['high'].shift(1)) > (df['low'].shift(1) - df['low']),
                          np.maximum(df['high'] - df['high'].shift(1), 0), 0)
        minus_dm = np.where((df['low'].shift(1) - df['low']) > (df['high'] - df['high'].shift(1)),
                           np.maximum(df['low'].shift(1) - df['low'], 0), 0)
        
        plus_di = 100 * (pd.Series(plus_dm).rolling(14).mean() / atr)
        minus_di = 100 * (pd.Series(minus_dm).rolling(14).mean() / atr)
        
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(14).mean()
        
        trend_strength = adx.iloc[-1] / 100 if len(adx) > 0 and not np.isnan(adx.iloc[-1]) else 0.5
        
        return {
            'ma_alignment': ma_alignment,
            'trend_consistency': trend_consistency,
            'momentum_3': momentum_3,
            'momentum_10': momentum_10,
            'momentum_20': momentum_20,
            'trend_strength': trend_strength,
            'trend_direction': 'up' if ma_alignment > 0.3 else 'down' if ma_alignment < -0.3 else 'sideways',
            'strength_category': 'strong' if trend_strength > 0.7 else 'moderate' if trend_strength > 0.4 else 'weak'
        }
    
    def _analyze_volatility_regime(self, returns: pd.Series) -> Dict:
        """Analyze volatility regime"""
        
        # Current volatility
        current_vol = returns.rolling(20).std().iloc[-1] * np.sqrt(1440)  # Annualized
        
        # Historical volatility percentile
        vol_series = returns.rolling(20).std() * np.sqrt(1440)
        vol_percentile = (vol_series.rank(pct=True) * 100).iloc[-1] if len(vol_series) > 50 else 50
        
        # Volatility trend
        recent_vol = vol_series.tail(5).mean()
        historical_vol = vol_series.tail(50).mean()
        vol_trend = 'increasing' if recent_vol > historical_vol * 1.1 else 'decreasing' if recent_vol < historical_vol * 0.9 else 'stable'
        
        # Volatility clustering (GARCH effects)
        abs_returns = abs(returns)
        vol_clustering = abs_returns.rolling(20).std().rolling(10).std().iloc[-1] if len(abs_returns) >= 30 else 0
        
        # Regime classification
        if vol_percentile > 80:
            vol_regime = 'high_volatility'
        elif vol_percentile > 60:
            vol_regime = 'elevated_volatility'
        elif vol_percentile < 20:
            vol_regime = 'low_volatility'
        else:
            vol_regime = 'normal_volatility'
        
        return {
            'current_volatility': current_vol,
            'volatility_percentile': vol_percentile,
            'volatility_trend': vol_trend,
            'volatility_clustering': vol_clustering,
            'volatility_regime': vol_regime,
            'favorable_for_trend': vol_regime in ['elevated_volatility', 'high_volatility'],
            'favorable_for_mean_reversion': vol_regime in ['normal_volatility', 'low_volatility']
        }
    
    def _analyze_mean_reversion_tendency(self, df: pd.DataFrame) -> Dict:
        """Analyze mean reversion characteristics"""
        
        returns = df['close'].pct_change().dropna()
        
        # Serial correlation (mean reversion indicator)
        serial_corr_1 = returns.autocorr(lag=1) if len(returns) > 1 else 0
        serial_corr_5 = returns.autocorr(lag=5) if len(returns) > 5 else 0
        
        # Half-life of mean reversion (simplified)
        price_sma = df['close'].rolling(20).mean()
        deviation_from_mean = (df['close'] - price_sma) / price_sma
        
        # Count mean reversion events
        reversion_events = 0
        total_events = 0
        
        for i in range(5, len(deviation_from_mean) - 5):
            if abs(deviation_from_mean.iloc[i]) > 0.01:  # Significant deviation
                total_events += 1
                # Check if price reverted within next 5 periods
                future_deviation = deviation_from_mean.iloc[i+1:i+6]
                if any(abs(future_deviation) < abs(deviation_from_mean.iloc[i]) * 0.5):
                    reversion_events += 1
        
        mean_reversion_rate = reversion_events / total_events if total_events > 0 else 0.5
        
        # Bollinger Band analysis
        bb_sma = df['close'].rolling(20).mean()
        bb_std = df['close'].rolling(20).std()
        bb_upper = bb_sma + (bb_std * 2)
        bb_lower = bb_sma - (bb_std * 2)
        
        current_price = df['close'].iloc[-1]
        bb_position = (current_price - bb_lower.iloc[-1]) / (bb_upper.iloc[-1] - bb_lower.iloc[-1])
        
        # Extremes favor mean reversion
        at_extremes = bb_position > 0.9 or bb_position < 0.1
        
        return {
            'serial_correlation_1': serial_corr_1,
            'serial_correlation_5': serial_corr_5,
            'mean_reversion_rate': mean_reversion_rate,
            'bb_position': bb_position,
            'at_bb_extremes': at_extremes,
            'reversion_favorable': serial_corr_1 < -0.1 or mean_reversion_rate > 0.6 or at_extremes
        }
    
    def _analyze_market_microstructure(self, df: pd.DataFrame) -> Dict:
        """Analyze market microstructure indicators"""
        
        # Estimate bid-ask spread from high-low
        estimated_spread = (df['high'] - df['low']) / df['close']
        avg_spread = estimated_spread.rolling(20).mean().iloc[-1]
        
        # Price efficiency (random walk characteristics)
        returns = df['close'].pct_change().dropna()
        variance_ratio = self._calculate_variance_ratio(returns, 5) if len(returns) >= 10 else 1.0
        
        # Order flow imbalance (simplified)
        up_moves = (df['close'] > df['close'].shift(1)).rolling(20).sum()
        down_moves = (df['close'] < df['close'].shift(1)).rolling(20).sum()
        flow_imbalance = (up_moves - down_moves) / (up_moves + down_moves)
        
        current_imbalance = flow_imbalance.iloc[-1] if len(flow_imbalance) > 0 else 0
        
        return {
            'estimated_spread': avg_spread,
            'variance_ratio': variance_ratio,
            'flow_imbalance': current_imbalance,
            'market_efficiency': 'efficient' if 0.8 < variance_ratio < 1.2 else 'inefficient',
            'liquidity_level': 'high' if avg_spread < 0.001 else 'medium' if avg_spread < 0.002 else 'low'
        }
    
    def _analyze_volume_patterns(self, df: pd.DataFrame) -> Dict:
        """Analyze volume patterns for regime detection"""
        
        if 'volume' not in df.columns:
            return {'volume_signal': 'neutral', 'volume_trend': 'unknown'}
        
        volume = df['volume']
        
        # Volume trend
        recent_vol = volume.rolling(10).mean().iloc[-1]
        historical_vol = volume.rolling(50).mean().iloc[-1]
        vol_trend = 'increasing' if recent_vol > historical_vol * 1.2 else 'decreasing' if recent_vol < historical_vol * 0.8 else 'stable'
        
        # Volume spikes
        vol_threshold = volume.rolling(20).mean() + volume.rolling(20).std() * 2
        recent_spikes = (volume.tail(5) > vol_threshold.tail(5)).sum()
        
        # Price-volume correlation
        price_change = df['close'].pct_change()
        vol_change = volume.pct_change()
        pv_correlation = price_change.rolling(20).corr(vol_change).iloc[-1]
        
        return {
            'volume_trend': vol_trend,
            'recent_spikes': recent_spikes,
            'price_volume_correlation': pv_correlation if not np.isnan(pv_correlation) else 0,
            'volume_signal': 'bullish' if vol_trend == 'increasing' and pv_correlation > 0.3 else 'bearish' if vol_trend == 'increasing' and pv_correlation < -0.3 else 'neutral'
        }
    
    def _analyze_price_patterns(self, df: pd.DataFrame) -> Dict:
        """Analyze price action patterns"""
        
        # Higher highs / lower lows pattern
        highs = df['high'].rolling(5).max()
        lows = df['low'].rolling(5).min()
        
        # Count pattern occurrences in recent history
        higher_highs = sum(highs.iloc[i] > highs.iloc[i-1] for i in range(-10, 0) if i >= 1 and len(highs) > abs(i))
        lower_lows = sum(lows.iloc[i] < lows.iloc[i-1] for i in range(-10, 0) if i >= 1 and len(lows) > abs(i))
        
        # Breakout patterns
        resistance = df['high'].rolling(20).max()
        support = df['low'].rolling(20).min()
        
        current_price = df['close'].iloc[-1]
        near_resistance = current_price > resistance.iloc[-1] * 0.995
        near_support = current_price < support.iloc[-1] * 1.005
        
        # Consolidation detection
        price_range = (df['high'].rolling(20).max() - df['low'].rolling(20).min()) / df['close'].rolling(20).mean()
        consolidating = price_range.iloc[-1] < 0.05  # Less than 5% range
        
        return {
            'higher_highs_count': higher_highs,
            'lower_lows_count': lower_lows,
            'near_resistance': near_resistance,
            'near_support': near_support,
            'consolidating': consolidating,
            'pattern_signal': 'bullish' if higher_highs > 6 else 'bearish' if lower_lows > 6 else 'neutral'
        }
    
    def _calculate_regime_scores(self, trend_analysis: Dict, volatility_analysis: Dict,
                               mean_reversion_analysis: Dict, microstructure_analysis: Dict,
                               volume_analysis: Dict, price_patterns: Dict) -> Dict:
        """Calculate regime preference scores"""
        
        # Mean reversion score
        mr_score = 0.0
        
        # Favor mean reversion when:
        # - Weak trends
        # - Normal/low volatility
        # - High mean reversion tendency
        # - Market inefficiencies
        # - Near support/resistance
        
        if trend_analysis['strength_category'] == 'weak':
            mr_score += 0.3
        elif trend_analysis['strength_category'] == 'moderate':
            mr_score += 0.1
        
        if volatility_analysis['favorable_for_mean_reversion']:
            mr_score += 0.25
        
        if mean_reversion_analysis['reversion_favorable']:
            mr_score += 0.25
        
        if microstructure_analysis['market_efficiency'] == 'inefficient':
            mr_score += 0.1
        
        if price_patterns['near_resistance'] or price_patterns['near_support']:
            mr_score += 0.1
        
        # Trend following score
        tf_score = 0.0
        
        # Favor trend following when:
        # - Strong trends
        # - Higher volatility
        # - Momentum persistence
        # - Volume confirmation
        # - Breakout patterns
        
        if trend_analysis['strength_category'] == 'strong':
            tf_score += 0.4
        elif trend_analysis['strength_category'] == 'moderate':
            tf_score += 0.2
        
        if volatility_analysis['favorable_for_trend']:
            tf_score += 0.2
        
        if abs(trend_analysis['ma_alignment']) > 0.5:
            tf_score += 0.2
        
        if volume_analysis['volume_signal'] in ['bullish', 'bearish']:
            tf_score += 0.1
        
        if price_patterns['pattern_signal'] in ['bullish', 'bearish']:
            tf_score += 0.1
        
        # Neutral score (when conditions are mixed)
        neutral_score = 1.0 - mr_score - tf_score
        
        return {
            self.MEAN_REVERSION: mr_score,
            self.TREND_FOLLOWING: tf_score,
            self.NEUTRAL: max(0, neutral_score)
        }
    
    def _determine_optimal_mode(self, regime_analysis: Dict, market_conditions: Optional[Dict]) -> str:
        """Determine the optimal strategy mode"""
        
        regime_scores = regime_analysis['regime_scores']
        
        # Consider historical performance
        mr_performance = self._get_mode_performance(self.MEAN_REVERSION)
        tf_performance = self._get_mode_performance(self.TREND_FOLLOWING)
        
        # Adjust scores based on recent performance
        if mr_performance > tf_performance:
            regime_scores[self.MEAN_REVERSION] *= 1.1
        elif tf_performance > mr_performance:
            regime_scores[self.TREND_FOLLOWING] *= 1.1
        
        # Determine mode with hysteresis (avoid frequent switching)
        max_score = max(regime_scores.values())
        best_mode = max(regime_scores.keys(), key=lambda k: regime_scores[k])
        
        # Apply hysteresis: require significant improvement to switch modes
        if self.current_mode != self.NEUTRAL and best_mode != self.current_mode:
            current_score = regime_scores[self.current_mode]
            if max_score - current_score < 0.15:  # Hysteresis threshold
                best_mode = self.current_mode
        
        self.mode_confidence = max_score
        return best_mode
    
    def _generate_mean_reversion_signal(self, df: pd.DataFrame, regime_analysis: Dict) -> Dict:
        """Generate mean reversion signal"""
        
        # Use multiple mean reversion indicators
        current_price = df['close'].iloc[-1]
        
        # Bollinger Bands
        bb_sma = df['close'].rolling(20).mean().iloc[-1]
        bb_std = df['close'].rolling(20).std().iloc[-1]
        bb_upper = bb_sma + (bb_std * 2)
        bb_lower = bb_sma - (bb_std * 2)
        bb_position = (current_price - bb_lower) / (bb_upper - bb_lower)
        
        # RSI
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = -delta.where(delta < 0, 0).rolling(14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        current_rsi = rsi.iloc[-1]
        
        # Generate signal
        confidence = 0.0
        action = 'HOLD'
        reasons = []
        
        # Oversold conditions (BUY signals)
        if bb_position < 0.1:  # Below lower BB
            confidence += 0.4
            reasons.append(f'Below lower BB (pos: {bb_position:.2f})')
        
        if current_rsi < 25:  # Oversold RSI
            confidence += 0.3
            reasons.append(f'RSI oversold ({current_rsi:.1f})')
        
        # Price mean reversion setup
        sma_20 = df['close'].rolling(20).mean().iloc[-1]
        price_deviation = (current_price - sma_20) / sma_20
        
        if price_deviation < -0.02:  # 2% below 20-period average
            confidence += 0.2
            reasons.append(f'Price below SMA20 ({price_deviation:.2%})')
        
        if confidence > 0.4:
            action = 'BUY'
        
        # Overbought conditions (SELL signals)
        sell_confidence = 0.0
        if bb_position > 0.9:  # Above upper BB
            sell_confidence += 0.4
            reasons.append(f'Above upper BB (pos: {bb_position:.2f})')
        
        if current_rsi > 75:  # Overbought RSI
            sell_confidence += 0.3
            reasons.append(f'RSI overbought ({current_rsi:.1f})')
        
        if price_deviation > 0.02:  # 2% above 20-period average
            sell_confidence += 0.2
            reasons.append(f'Price above SMA20 ({price_deviation:.2%})')
        
        if sell_confidence > confidence and sell_confidence > 0.4:
            action = 'SELL'
            confidence = sell_confidence
        
        return {
            'action': action,
            'confidence': min(confidence, 1.0),
            'reason': f"Mean Reversion: {', '.join(reasons)}" if reasons else "Mean Reversion: No clear signal"
        }
    
    def _generate_trend_following_signal(self, df: pd.DataFrame, regime_analysis: Dict) -> Dict:
        """Generate trend following signal"""
        
        trend_analysis = regime_analysis['trend_analysis']
        
        # Use trend indicators
        ma_8 = df['close'].rolling(8).mean().iloc[-1]
        ma_21 = df['close'].rolling(21).mean().iloc[-1]
        current_price = df['close'].iloc[-1]
        
        confidence = 0.0
        action = 'HOLD'
        reasons = []
        
        # Trend following BUY signals
        if trend_analysis['trend_direction'] == 'up':
            confidence += 0.3
            reasons.append('Uptrend detected')
            
            if current_price > ma_8 > ma_21:
                confidence += 0.2
                reasons.append('Price above aligned MAs')
            
            if trend_analysis['momentum_3'] > 0.01:
                confidence += 0.2
                reasons.append(f'Strong momentum ({trend_analysis["momentum_3"]:.2%})')
            
            if trend_analysis['strength_category'] == 'strong':
                confidence += 0.3
                reasons.append('Strong trend strength')
            
            if confidence > 0.5:
                action = 'BUY'
        
        # Trend following SELL signals
        elif trend_analysis['trend_direction'] == 'down':
            confidence += 0.3
            reasons.append('Downtrend detected')
            
            if current_price < ma_8 < ma_21:
                confidence += 0.2
                reasons.append('Price below aligned MAs')
            
            if trend_analysis['momentum_3'] < -0.01:
                confidence += 0.2
                reasons.append(f'Strong negative momentum ({trend_analysis["momentum_3"]:.2%})')
            
            if trend_analysis['strength_category'] == 'strong':
                confidence += 0.3
                reasons.append('Strong trend strength')
            
            if confidence > 0.5:
                action = 'SELL'
        
        return {
            'action': action,
            'confidence': min(confidence, 1.0),
            'reason': f"Trend Following: {', '.join(reasons)}" if reasons else "Trend Following: No clear signal"
        }
    
    def _generate_neutral_signal(self, df: pd.DataFrame, regime_analysis: Dict) -> Dict:
        """Generate neutral/hold signal when regime is unclear"""
        
        return {
            'action': 'HOLD',
            'confidence': 0.0,
            'reason': "Neutral: Mixed regime signals - no clear trend or mean reversion opportunity"
        }
    
    def _update_mode_tracking(self, mode: str, regime_analysis: Dict) -> None:
        """Update mode tracking and history"""
        
        self.current_mode = mode
        self.mode_history.append({
            'mode': mode,
            'confidence': self.mode_confidence,
            'regime': regime_analysis['dominant_regime']
        })
        
        # Keep only recent history
        if len(self.mode_history) > 100:
            self.mode_history = self.mode_history[-100:]
    
    def _get_mode_performance(self, mode: str) -> float:
        """Get performance score for a specific mode"""
        
        stats = self.performance_tracker.get(mode, {'wins': 0, 'losses': 0, 'total_return': 0.0})
        
        total_trades = stats['wins'] + stats['losses']
        if total_trades == 0:
            return 0.0
        
        win_rate = stats['wins'] / total_trades
        avg_return = stats['total_return'] / total_trades
        
        # Composite performance score
        return win_rate * 0.7 + (avg_return * 10) * 0.3  # Weighted combination
    
    def update_performance(self, mode: str, trade_result: float) -> None:
        """Update performance tracking for a mode"""
        
        if mode in self.performance_tracker:
            if trade_result > 0:
                self.performance_tracker[mode]['wins'] += 1
            else:
                self.performance_tracker[mode]['losses'] += 1
            
            self.performance_tracker[mode]['total_return'] += trade_result
    
    def _calculate_variance_ratio(self, returns: pd.Series, k: int) -> float:
        """Calculate variance ratio for random walk test"""
        
        if len(returns) < k * 2:
            return 1.0
        
        # Variance of k-period returns
        k_period_returns = returns.rolling(k).sum().dropna()
        var_k = k_period_returns.var()
        
        # Variance of 1-period returns
        var_1 = returns.var()
        
        # Variance ratio
        variance_ratio = var_k / (k * var_1) if var_1 > 0 else 1.0
        
        return variance_ratio
    
    def get_mode_statistics(self) -> Dict:
        """Get comprehensive mode statistics"""
        
        mode_counts = {}
        for entry in self.mode_history:
            mode = entry['mode']
            mode_counts[mode] = mode_counts.get(mode, 0) + 1
        
        return {
            'current_mode': self.current_mode,
            'mode_confidence': self.mode_confidence,
            'mode_distribution': mode_counts,
            'performance_tracker': self.performance_tracker.copy(),
            'mode_history_length': len(self.mode_history)
        }

class SimpleTrendFollowing:
    """Legacy trend following class for backward compatibility"""
    def __init__(self, fast_ma=8, slow_ma=21, momentum_period=14):
        self.fast_ma = fast_ma
        self.slow_ma = slow_ma
        self.momentum_period = momentum_period
        self.name = f"TrendFollowing_{fast_ma}_{slow_ma}_{momentum_period}"

    def get_signal(self, df, market_conditions=None):
        """Generate trend following signals"""
        if len(df) < max(self.slow_ma, self.momentum_period) + 5:
            return {'action': 'HOLD', 'confidence': 0, 'reason': 'Insufficient data for trend following'}

        # Calculate moving averages
        fast_ma = df['close'].rolling(self.fast_ma).mean()
        slow_ma = df['close'].rolling(self.slow_ma).mean()
        current_price = df['close'].iloc[-1]

        # Current MA values
        fast_current = fast_ma.iloc[-1]
        slow_current = slow_ma.iloc[-1]

        # MA slopes (trend strength)
        fast_slope = (fast_ma.iloc[-1] - fast_ma.iloc[-3]) / fast_ma.iloc[-3] if fast_ma.iloc[-3] != 0 else 0
        slow_slope = (slow_ma.iloc[-1] - slow_ma.iloc[-3]) / slow_ma.iloc[-3] if slow_ma.iloc[-3] != 0 else 0

        # Momentum calculation
        momentum = (current_price - df['close'].iloc[-self.momentum_period]) / df['close'].iloc[-self.momentum_period]

        # Volume confirmation
        recent_volume = df['volume'].tail(5).mean() if 'volume' in df.columns else 1
        avg_volume = df['volume'].tail(20).mean() if 'volume' in df.columns else 1
        volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 1

        # Only trade in strong trends
        if market_conditions and market_conditions.get('market_phase') == 'strong_uptrend':
            # Strong uptrend - look for continuation signals
            if (fast_current > slow_current and
                fast_slope > 0.01 and
                slow_slope > 0.005 and
                momentum > 0.02 and
                volume_ratio > 1.1):

                confidence = min(1.0, max(0.2, momentum * 15 + (volume_ratio - 1) * 0.5))
                return {
                    'action': 'BUY',
                    'confidence': confidence,
                    'reason': f'Trend BUY: Strong uptrend continuation (momentum: {momentum:.3f})'
                }

        elif market_conditions and market_conditions.get('market_phase') == 'strong_downtrend':
            # Strong downtrend - avoid buying, suggest selling if holding
            if (fast_current < slow_current and
                fast_slope < -0.01 and
                slow_slope < -0.005 and
                momentum < -0.02 and
                volume_ratio > 1.1):

                confidence = min(1.0, max(0.2, abs(momentum) * 15 + (volume_ratio - 1) * 0.5))
                return {
                    'action': 'SELL',
                    'confidence': confidence,
                    'reason': f'Trend SELL: Strong downtrend continuation (momentum: {momentum:.3f})'
                }

        # In transitional or consolidation markets, stay neutral
        return {'action': 'HOLD', 'confidence': 0, 'reason': 'Trend: No strong trend detected'}

class HybridStrategy:
    """
    Hybrid strategy that switches between mean reversion and trend following
    based on market conditions
    """
    def __init__(self, mean_reversion_strategy, trend_following_strategy=None):
        self.mean_reversion = mean_reversion_strategy
        self.trend_following = trend_following_strategy or SimpleTrendFollowing()
        self.name = "Hybrid_MeanReversion_TrendFollowing"

    def get_consensus_signal(self, df):
        """Get signal based on market conditions"""
        # Get mean reversion signal first
        mr_signal = self.mean_reversion.get_consensus_signal(df)
        market_conditions = mr_signal.get('market_conditions', {})
        market_phase = market_conditions.get('market_phase', 'transitional')

        # Decide which strategy to use
        if market_phase in ['strong_uptrend', 'strong_downtrend']:
            # Use trend following in strong trends
            tf_signal = self.trend_following.get_signal(df, market_conditions)

            # If trend following gives a signal, use it
            if tf_signal['action'] != 'HOLD' and tf_signal['confidence'] > 0.3:
                # Enhance the mean reversion signal with trend following input
                enhanced_signal = mr_signal.copy()
                enhanced_signal['trend_following_input'] = tf_signal

                # In strong uptrends, boost BUY confidence, reduce SELL confidence
                if market_phase == 'strong_uptrend':
                    if mr_signal['action'] == 'BUY':
                        enhanced_signal['confidence'] = min(1.0, mr_signal['confidence'] * 1.2)
                        enhanced_signal['reason'] += " (trend boost)"
                    elif mr_signal['action'] == 'SELL':
                        enhanced_signal['confidence'] *= 0.6
                        enhanced_signal['reason'] += " (trend warning)"

                # In strong downtrends, boost SELL confidence, reduce BUY confidence
                elif market_phase == 'strong_downtrend':
                    if mr_signal['action'] == 'SELL':
                        enhanced_signal['confidence'] = min(1.0, mr_signal['confidence'] * 1.2)
                        enhanced_signal['reason'] += " (trend boost)"
                    elif mr_signal['action'] == 'BUY':
                        enhanced_signal['confidence'] *= 0.6
                        enhanced_signal['reason'] += " (trend warning)"

                return enhanced_signal

        # Use pure mean reversion in consolidation/transitional markets
        return mr_signal

def create_hybrid_strategy():
    """Create a hybrid strategy instance"""
    from strategies.multi_strategy_optimized import MultiStrategyOptimized

    mean_reversion = MultiStrategyOptimized()
    trend_following = SimpleTrendFollowing()

    return HybridStrategy(mean_reversion, trend_following)

if __name__ == "__main__":
    # Test the trend following strategy
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    from strategies.ma_crossover import fetch_ohlcv
    import ccxt
    from config import BINANCE_API_KEY, BINANCE_API_SECRET

    exchange = ccxt.binanceus({
        'apiKey': BINANCE_API_KEY,
        'secret': BINANCE_API_SECRET,
        'enableRateLimit': True
    })

    print("🧪 Testing Trend Following Strategy")

    try:
        df = fetch_ohlcv(exchange, 'BTC/USDT', '1m', 100)

        # Test mean reversion strategy
        hybrid = create_hybrid_strategy()
        signal = hybrid.get_consensus_signal(df)

        print(f"\n📊 Hybrid Strategy Signal:")
        print(f"   Action: {signal['action']}")
        print(f"   Confidence: {signal['confidence']:.3f}")
        print(f"   Reason: {signal['reason']}")
        print(f"   Market Phase: {signal.get('market_conditions', {}).get('market_phase', 'unknown')}")

        if 'trend_following_input' in signal:
            tf = signal['trend_following_input']
            print(f"\n🔄 Trend Following Input:")
            print(f"   Action: {tf['action']}")
            print(f"   Confidence: {tf['confidence']:.3f}")
            print(f"   Reason: {tf['reason']}")

    except Exception as e:
        print(f"❌ Test failed: {e}")
