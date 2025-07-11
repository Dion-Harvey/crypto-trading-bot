#!/usr/bin/env python3
"""
Market Microstructure Analysis Module for Crypto Trading Bot

This module analyzes market microstructure including spread analysis,
liquidity assessment, and institutional flow detection.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging

class MarketMicrostructureAnalyzer:
    """Advanced market microstructure analysis for crypto trading"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def analyze_market_structure(self, df: pd.DataFrame, orderbook_data: Optional[Dict] = None) -> Dict:
        """
        Comprehensive market structure analysis
        """
        if len(df) < 20:
            return {'structure_signal': 'HOLD', 'confidence': 0.0}
        
        # Liquidity analysis
        liquidity_analysis = self._analyze_liquidity(df)
        
        # Market regime detection
        regime_analysis = self._detect_market_regime(df)
        
        # Volatility structure
        volatility_structure = self._analyze_volatility_structure(df)
        
        # Price efficiency analysis
        efficiency_analysis = self._analyze_price_efficiency(df)
        
        # Order flow toxicity (simplified)
        toxicity_analysis = self._analyze_order_flow_toxicity(df)
        
        # Composite signal
        signal, confidence = self._generate_microstructure_signal(
            liquidity_analysis, regime_analysis, volatility_structure,
            efficiency_analysis, toxicity_analysis
        )
        
        return {
            'structure_signal': signal,
            'confidence': confidence,
            'liquidity': liquidity_analysis,
            'regime': regime_analysis,
            'volatility_structure': volatility_structure,
            'price_efficiency': efficiency_analysis,
            'flow_toxicity': toxicity_analysis,
            'market_quality': self._assess_market_quality(
                liquidity_analysis, volatility_structure, efficiency_analysis
            )
        }
    
    def analyze_spread_dynamics(self, df: pd.DataFrame) -> Dict:
        """
        Analyze bid-ask spread dynamics and market impact
        Note: Simplified version using OHLCV data
        """
        # Estimate spread from high-low range
        estimated_spread = (df['high'] - df['low']) / df['close']
        
        # Rolling spread statistics
        avg_spread = estimated_spread.rolling(20).mean()
        spread_volatility = estimated_spread.rolling(20).std()
        
        # Spread trend
        recent_spread = estimated_spread.tail(5).mean()
        historical_spread = estimated_spread.rolling(50).mean().iloc[-1]
        
        spread_trend = 'widening' if recent_spread > historical_spread * 1.2 else \
                      'tightening' if recent_spread < historical_spread * 0.8 else 'stable'
        
        # Market impact estimation
        impact_analysis = self._estimate_market_impact(df)
        
        return {
            'current_spread_estimate': estimated_spread.iloc[-1],
            'spread_trend': spread_trend,
            'spread_volatility': spread_volatility.iloc[-1] if len(spread_volatility) > 0 else 0,
            'relative_spread': recent_spread / historical_spread if historical_spread > 0 else 1,
            'market_impact': impact_analysis,
            'liquidity_signal': self._generate_liquidity_signal(spread_trend, impact_analysis)
        }
    
    def detect_institutional_flow(self, df: pd.DataFrame, volume_threshold_multiplier: float = 3.0) -> Dict:
        """
        Detect institutional order flow patterns
        """
        # Large block detection
        avg_volume = df['volume'].rolling(50).mean()
        large_blocks = df[df['volume'] > avg_volume * volume_threshold_multiplier]
        
        # TWAP/VWAP deviation analysis
        twap = df['close'].rolling(20).mean()
        vwap = self._calculate_vwap(df, 20)
        
        # Price impact of large blocks
        institutional_signals = []
        
        for idx in large_blocks.index:
            if idx in df.index:
                block_idx = df.index.get_loc(idx)
                if block_idx < len(df) - 5:  # Ensure we have data after the block
                    
                    # Analyze price impact after large volume
                    pre_price = df['close'].iloc[max(0, block_idx-3):block_idx].mean()
                    post_price = df['close'].iloc[block_idx+1:min(len(df), block_idx+6)].mean()
                    
                    if pre_price > 0:
                        impact = (post_price - pre_price) / pre_price
                        
                        # Classify as institutional based on sustained impact
                        if abs(impact) > 0.002:  # 0.2% sustained impact
                            institutional_signals.append({
                                'timestamp': idx,
                                'volume': df.loc[idx, 'volume'],
                                'impact': impact,
                                'direction': 'buying' if impact > 0 else 'selling',
                                'strength': min(1.0, abs(impact) * 100)
                            })
        
        # Stealth trading detection (consistent small orders)
        stealth_patterns = self._detect_stealth_trading(df)
        
        # Aggregate institutional flow
        recent_institutional = [s for s in institutional_signals if s['timestamp'] in df.tail(20).index]
        
        if recent_institutional:
            net_flow = sum(s['impact'] * s['strength'] for s in recent_institutional)
            avg_strength = np.mean([s['strength'] for s in recent_institutional])
            
            flow_direction = 'institutional_buying' if net_flow > 0 else 'institutional_selling'
            confidence = min(1.0, avg_strength)
        else:
            flow_direction = 'retail_dominated'
            confidence = 0.3
        
        return {
            'flow_type': flow_direction,
            'confidence': confidence,
            'institutional_blocks': len(recent_institutional),
            'stealth_patterns': stealth_patterns,
            'block_details': recent_institutional[-3:] if recent_institutional else [],
            'flow_intensity': abs(net_flow) if recent_institutional else 0
        }
    
    def analyze_order_book_pressure(self, orderbook_snapshot: Optional[Dict] = None) -> Dict:
        """
        Analyze order book pressure and imbalances
        Note: This would require real orderbook data
        """
        if not orderbook_snapshot:
            return {'pressure': 'unknown', 'imbalance': 0, 'signal': 'HOLD'}
        
        bids = orderbook_snapshot.get('bids', [])
        asks = orderbook_snapshot.get('asks', [])
        
        if not bids or not asks:
            return {'pressure': 'unknown', 'imbalance': 0, 'signal': 'HOLD'}
        
        # Calculate order book imbalance
        bid_volume = sum(price * volume for price, volume in bids[:10])  # Top 10 levels
        ask_volume = sum(price * volume for price, volume in asks[:10])
        
        total_volume = bid_volume + ask_volume
        if total_volume > 0:
            imbalance = (bid_volume - ask_volume) / total_volume
        else:
            imbalance = 0
        
        # Pressure analysis
        if imbalance > 0.2:
            pressure = 'buy_pressure'
            signal = 'BUY'
        elif imbalance < -0.2:
            pressure = 'sell_pressure'
            signal = 'SELL'
        else:
            pressure = 'balanced'
            signal = 'HOLD'
        
        # Spread analysis
        best_bid = bids[0][0] if bids else 0
        best_ask = asks[0][0] if asks else 0
        spread = (best_ask - best_bid) / best_ask if best_ask > 0 else 0
        
        return {
            'pressure': pressure,
            'imbalance': imbalance,
            'signal': signal,
            'confidence': min(1.0, abs(imbalance) * 2),
            'spread': spread,
            'bid_volume': bid_volume,
            'ask_volume': ask_volume
        }
    
    # =============================================================================
    # HELPER METHODS
    # =============================================================================
    
    def _analyze_liquidity(self, df: pd.DataFrame) -> Dict:
        """Analyze market liquidity"""
        # Volume-based liquidity measures
        volume_consistency = 1 - (df['volume'].rolling(20).std() / df['volume'].rolling(20).mean()).iloc[-1]
        
        # Price impact measure (simplified)
        returns = df['close'].pct_change()
        volume_normalized = df['volume'] / df['volume'].rolling(50).mean()
        
        # Correlation between returns and volume (Amihud illiquidity)
        if len(returns) >= 20 and len(volume_normalized) >= 20:
            illiquidity = abs(returns.tail(20)).corr(volume_normalized.tail(20))
            liquidity_score = 1 - (illiquidity if not np.isnan(illiquidity) else 0.5)
        else:
            liquidity_score = 0.5
        
        # High-low spread as liquidity proxy
        spread_ratio = ((df['high'] - df['low']) / df['close']).rolling(20).mean().iloc[-1]
        
        # Composite liquidity score
        composite_liquidity = (volume_consistency * 0.4 + liquidity_score * 0.4 + 
                             (1 - min(spread_ratio, 0.05) / 0.05) * 0.2)
        
        return {
            'liquidity_score': max(0, min(1, composite_liquidity)),
            'volume_consistency': max(0, min(1, volume_consistency)),
            'price_impact_score': liquidity_score,
            'spread_tightness': 1 - min(spread_ratio, 0.05) / 0.05,
            'liquidity_level': 'high' if composite_liquidity > 0.7 else 'medium' if composite_liquidity > 0.4 else 'low'
        }
    
    def _detect_market_regime(self, df: pd.DataFrame) -> Dict:
        """Detect current market regime"""
        returns = df['close'].pct_change()
        volume = df['volume']
        
        # Volatility regime
        volatility = returns.rolling(20).std()
        current_vol = volatility.iloc[-1]
        avg_vol = volatility.rolling(100).mean().iloc[-1]
        
        vol_regime = 'high' if current_vol > avg_vol * 1.5 else 'low' if current_vol < avg_vol * 0.7 else 'normal'
        
        # Trend regime
        ma_short = df['close'].rolling(10).mean()
        ma_long = df['close'].rolling(50).mean()
        
        if ma_short.iloc[-1] > ma_long.iloc[-1] * 1.02:
            trend_regime = 'uptrend'
        elif ma_short.iloc[-1] < ma_long.iloc[-1] * 0.98:
            trend_regime = 'downtrend'
        else:
            trend_regime = 'sideways'
        
        # Volume regime
        avg_volume = volume.rolling(50).mean()
        current_volume = volume.rolling(10).mean().iloc[-1]
        
        volume_regime = 'high' if current_volume > avg_volume.iloc[-1] * 1.3 else 'low' if current_volume < avg_volume.iloc[-1] * 0.7 else 'normal'
        
        # Market stress indicators
        stress_indicators = self._calculate_stress_indicators(df)
        
        return {
            'volatility_regime': vol_regime,
            'trend_regime': trend_regime,
            'volume_regime': volume_regime,
            'market_stress': stress_indicators,
            'regime_stability': self._assess_regime_stability(df),
            'regime_strength': self._calculate_regime_strength(vol_regime, trend_regime, volume_regime)
        }
    
    def _analyze_volatility_structure(self, df: pd.DataFrame) -> Dict:
        """Analyze volatility term structure"""
        returns = df['close'].pct_change()
        
        # Multiple timeframe volatilities
        vol_1 = returns.rolling(5).std()    # Short-term
        vol_2 = returns.rolling(20).std()   # Medium-term
        vol_3 = returns.rolling(50).std()   # Long-term
        
        # Volatility term structure
        if len(vol_1) > 0 and len(vol_2) > 0 and len(vol_3) > 0:
            current_vol_1 = vol_1.iloc[-1]
            current_vol_2 = vol_2.iloc[-1]
            current_vol_3 = vol_3.iloc[-1]
            
            # Structure shape
            if current_vol_1 > current_vol_2 > current_vol_3:
                structure = 'backwardation'  # High short-term vol
            elif current_vol_1 < current_vol_2 < current_vol_3:
                structure = 'contango'  # Rising vol term structure
            else:
                structure = 'mixed'
        else:
            structure = 'insufficient_data'
            current_vol_1 = current_vol_2 = current_vol_3 = 0
        
        # Volatility clustering
        vol_clustering = self._measure_volatility_clustering(returns)
        
        return {
            'term_structure': structure,
            'short_term_vol': current_vol_1,
            'medium_term_vol': current_vol_2,
            'long_term_vol': current_vol_3,
            'volatility_clustering': vol_clustering,
            'vol_of_vol': returns.rolling(20).std().rolling(10).std().iloc[-1] if len(returns) >= 30 else 0
        }
    
    def _analyze_price_efficiency(self, df: pd.DataFrame) -> Dict:
        """Analyze price discovery efficiency"""
        returns = df['close'].pct_change()
        
        # Serial correlation (random walk test)
        if len(returns) >= 20:
            serial_corr = returns.autocorr(lag=1)
            efficiency_score = 1 - abs(serial_corr) if not np.isnan(serial_corr) else 0.5
        else:
            efficiency_score = 0.5
        
        # Variance ratio test (simplified)
        if len(returns) >= 50:
            var_1 = returns.rolling(1).var().mean()
            var_5 = returns.rolling(5).var().mean() / 5
            variance_ratio = var_5 / var_1 if var_1 > 0 else 1
            variance_efficiency = 1 - abs(variance_ratio - 1)
        else:
            variance_efficiency = 0.5
        
        # Price reversal patterns
        reversal_tendency = self._measure_reversal_tendency(df)
        
        # Composite efficiency
        composite_efficiency = (efficiency_score * 0.4 + variance_efficiency * 0.4 + 
                              (1 - reversal_tendency) * 0.2)
        
        return {
            'efficiency_score': max(0, min(1, composite_efficiency)),
            'serial_correlation': serial_corr if 'serial_corr' in locals() else 0,
            'variance_ratio': variance_ratio if 'variance_ratio' in locals() else 1,
            'reversal_tendency': reversal_tendency,
            'market_efficiency': 'high' if composite_efficiency > 0.7 else 'medium' if composite_efficiency > 0.4 else 'low'
        }
    
    def _analyze_order_flow_toxicity(self, df: pd.DataFrame) -> Dict:
        """Analyze order flow toxicity (adverse selection)"""
        returns = df['close'].pct_change()
        volume = df['volume']
        
        # Volume-weighted price impact
        volume_weighted_returns = returns * volume / volume.rolling(20).mean()
        
        # Toxicity measures
        if len(volume_weighted_returns) >= 20:
            toxicity = volume_weighted_returns.rolling(20).std().iloc[-1]
            avg_toxicity = volume_weighted_returns.rolling(100).std().iloc[-1] if len(volume_weighted_returns) >= 100 else toxicity
            
            relative_toxicity = toxicity / avg_toxicity if avg_toxicity > 0 else 1
        else:
            relative_toxicity = 1
        
        # Flow direction consistency
        price_direction = np.sign(returns)
        volume_direction = np.sign(volume.diff())
        
        if len(price_direction) >= 10 and len(volume_direction) >= 10:
            flow_consistency = (price_direction.tail(10) == volume_direction.tail(10)).mean()
        else:
            flow_consistency = 0.5
        
        # Toxicity classification
        if relative_toxicity > 1.5:
            toxicity_level = 'high'
        elif relative_toxicity > 1.2:
            toxicity_level = 'medium'
        else:
            toxicity_level = 'low'
        
        return {
            'toxicity_level': toxicity_level,
            'relative_toxicity': relative_toxicity,
            'flow_consistency': flow_consistency,
            'adverse_selection_risk': relative_toxicity * (1 - flow_consistency)
        }
    
    def _generate_microstructure_signal(self, liquidity_analysis: Dict, regime_analysis: Dict,
                                      volatility_structure: Dict, efficiency_analysis: Dict,
                                      toxicity_analysis: Dict) -> Tuple[str, float]:
        """Generate composite microstructure signal"""
        
        signals = []
        confidences = []
        
        # Liquidity signal
        if liquidity_analysis['liquidity_level'] == 'high':
            signals.append('BUY')  # High liquidity favors trading
            confidences.append(0.3)
        elif liquidity_analysis['liquidity_level'] == 'low':
            signals.append('HOLD')  # Low liquidity increases risk
            confidences.append(0.2)
        
        # Regime signal
        if (regime_analysis['trend_regime'] == 'uptrend' and 
            regime_analysis['volume_regime'] == 'high'):
            signals.append('BUY')
            confidences.append(0.4)
        elif (regime_analysis['trend_regime'] == 'downtrend' and 
              regime_analysis['volume_regime'] == 'high'):
            signals.append('SELL')
            confidences.append(0.4)
        
        # Volatility structure signal
        if volatility_structure['term_structure'] == 'backwardation':
            # High short-term vol suggests mean reversion opportunity
            signals.append('BUY')  # Contrarian
            confidences.append(0.3)
        
        # Efficiency signal
        if efficiency_analysis['market_efficiency'] == 'low':
            # Inefficient markets may have more opportunities
            signals.append('BUY')
            confidences.append(0.2)
        
        # Toxicity signal
        if toxicity_analysis['toxicity_level'] == 'high':
            signals.append('HOLD')  # High toxicity means higher adverse selection
            confidences.append(0.3)
        
        # Aggregate signals
        buy_votes = signals.count('BUY')
        sell_votes = signals.count('SELL')
        hold_votes = signals.count('HOLD')
        
        if buy_votes > max(sell_votes, hold_votes):
            signal = 'BUY'
            confidence = np.mean([c for i, c in enumerate(confidences) if signals[i] == 'BUY'])
        elif sell_votes > max(buy_votes, hold_votes):
            signal = 'SELL'
            confidence = np.mean([c for i, c in enumerate(confidences) if signals[i] == 'SELL'])
        else:
            signal = 'HOLD'
            confidence = np.mean(confidences) if confidences else 0.0
        
        return signal, confidence
    
    def _calculate_vwap(self, df: pd.DataFrame, period: int) -> pd.Series:
        """Calculate Volume Weighted Average Price"""
        typical_price = (df['high'] + df['low'] + df['close']) / 3
        vwap = (typical_price * df['volume']).rolling(period).sum() / df['volume'].rolling(period).sum()
        return vwap
    
    def _estimate_market_impact(self, df: pd.DataFrame) -> Dict:
        """Estimate market impact of trades"""
        returns = df['close'].pct_change()
        volume = df['volume']
        
        # Normalized volume
        norm_volume = volume / volume.rolling(50).mean()
        
        # Impact estimation
        if len(returns) >= 20 and len(norm_volume) >= 20:
            impact_correlation = abs(returns.tail(20)).corr(norm_volume.tail(20))
            if np.isnan(impact_correlation):
                impact_correlation = 0.1
        else:
            impact_correlation = 0.1
        
        # Classify impact
        if impact_correlation > 0.3:
            impact_level = 'high'
        elif impact_correlation > 0.15:
            impact_level = 'medium'
        else:
            impact_level = 'low'
        
        return {
            'impact_level': impact_level,
            'impact_correlation': impact_correlation,
            'estimated_cost': impact_correlation * 0.001  # Rough estimate in %
        }
    
    def _generate_liquidity_signal(self, spread_trend: str, impact_analysis: Dict) -> Dict:
        """Generate liquidity-based trading signal"""
        signal = 'HOLD'
        confidence = 0.0
        
        if spread_trend == 'tightening' and impact_analysis['impact_level'] == 'low':
            signal = 'BUY'  # Good liquidity conditions
            confidence = 0.4
        elif spread_trend == 'widening' and impact_analysis['impact_level'] == 'high':
            signal = 'HOLD'  # Poor liquidity conditions
            confidence = 0.2
        
        return {
            'signal': signal,
            'confidence': confidence,
            'reasoning': f"Spread {spread_trend}, impact {impact_analysis['impact_level']}"
        }
    
    def _detect_stealth_trading(self, df: pd.DataFrame) -> Dict:
        """Detect stealth trading patterns (consistent small orders)"""
        volume = df['volume']
        avg_volume = volume.rolling(50).mean()
        
        # Look for consistent small volumes with price movement
        small_volume_threshold = avg_volume * 0.7
        small_volume_periods = volume < small_volume_threshold.iloc[-1]
        
        if len(small_volume_periods) >= 10:
            recent_small_volume = small_volume_periods.tail(10).sum()
            
            # Check if small volumes coincide with price movement
            price_movement = abs(df['close'].pct_change()).tail(10).sum()
            
            if recent_small_volume >= 7 and price_movement > 0.02:  # 7/10 small volume periods with 2%+ movement
                return {
                    'detected': True,
                    'pattern_strength': recent_small_volume / 10,
                    'price_movement': price_movement,
                    'description': 'Consistent small volumes with price movement suggests stealth trading'
                }
        
        return {'detected': False}
    
    def _calculate_stress_indicators(self, df: pd.DataFrame) -> Dict:
        """Calculate market stress indicators"""
        returns = df['close'].pct_change()
        volume = df['volume']
        
        # VIX-like measure (rolling volatility percentile)
        if len(returns) >= 100:
            current_vol = returns.rolling(20).std().iloc[-1]
            vol_percentile = (returns.rolling(20).std().rank(pct=True) * 100).iloc[-1]
        else:
            vol_percentile = 50
        
        # Volume stress (volume spikes)
        volume_stress = (volume > volume.rolling(20).mean() * 2).rolling(10).sum().iloc[-1] / 10
        
        # Price gap stress
        gaps = abs(df['open'] - df['close'].shift(1)) / df['close'].shift(1)
        gap_stress = (gaps > gaps.rolling(50).quantile(0.95)).rolling(10).sum().iloc[-1] / 10
        
        # Composite stress
        composite_stress = (vol_percentile / 100 * 0.5 + volume_stress * 0.3 + gap_stress * 0.2)
        
        return {
            'volatility_stress': vol_percentile,
            'volume_stress': volume_stress,
            'gap_stress': gap_stress,
            'composite_stress': composite_stress,
            'stress_level': 'high' if composite_stress > 0.7 else 'medium' if composite_stress > 0.4 else 'low'
        }
    
    def _assess_regime_stability(self, df: pd.DataFrame) -> float:
        """Assess stability of current market regime"""
        returns = df['close'].pct_change()
        
        # Trend consistency
        trend_direction = np.sign(returns)
        trend_consistency = abs(trend_direction.rolling(20).mean()).iloc[-1] if len(trend_direction) >= 20 else 0.5
        
        # Volatility stability
        vol = returns.rolling(10).std()
        vol_stability = 1 - (vol.rolling(20).std() / vol.rolling(20).mean()).iloc[-1] if len(vol) >= 20 else 0.5
        vol_stability = max(0, min(1, vol_stability))
        
        return (trend_consistency + vol_stability) / 2
    
    def _calculate_regime_strength(self, vol_regime: str, trend_regime: str, volume_regime: str) -> float:
        """Calculate regime strength"""
        strength = 0.0
        
        # Volatility regime strength
        if vol_regime in ['high', 'low']:
            strength += 0.3
        
        # Trend regime strength
        if trend_regime in ['uptrend', 'downtrend']:
            strength += 0.4
        
        # Volume regime strength
        if volume_regime in ['high', 'low']:
            strength += 0.3
        
        return strength
    
    def _measure_volatility_clustering(self, returns: pd.Series) -> float:
        """Measure volatility clustering (GARCH effects)"""
        if len(returns) < 30:
            return 0.5
        
        abs_returns = abs(returns)
        autocorr = abs_returns.autocorr(lag=1)
        
        return max(0, min(1, autocorr)) if not np.isnan(autocorr) else 0.5
    
    def _measure_reversal_tendency(self, df: pd.DataFrame) -> float:
        """Measure price reversal tendency"""
        returns = df['close'].pct_change()
        
        if len(returns) < 10:
            return 0.5
        
        # Count directional reversals
        direction_changes = (np.sign(returns) != np.sign(returns.shift(1))).rolling(20).mean()
        
        return direction_changes.iloc[-1] if len(direction_changes) > 0 else 0.5
    
    def _assess_market_quality(self, liquidity_analysis: Dict, volatility_structure: Dict,
                              efficiency_analysis: Dict) -> Dict:
        """Assess overall market quality"""
        
        # Quality components
        liquidity_score = liquidity_analysis['liquidity_score']
        efficiency_score = efficiency_analysis['efficiency_score']
        
        # Volatility appropriateness (not too high, not too low)
        vol_score = 1.0
        if volatility_structure['term_structure'] == 'backwardation':
            vol_score = 0.7  # High short-term vol is concerning
        elif volatility_structure['term_structure'] == 'contango':
            vol_score = 0.8  # Rising vol term structure
        
        # Composite quality
        overall_quality = (liquidity_score * 0.4 + efficiency_score * 0.4 + vol_score * 0.2)
        
        quality_level = 'excellent' if overall_quality > 0.8 else \
                       'good' if overall_quality > 0.6 else \
                       'fair' if overall_quality > 0.4 else 'poor'
        
        return {
            'overall_score': overall_quality,
            'quality_level': quality_level,
            'components': {
                'liquidity': liquidity_score,
                'efficiency': efficiency_score,
                'volatility_structure': vol_score
            },
            'trading_recommendation': 'favorable' if overall_quality > 0.6 else 'caution' if overall_quality > 0.4 else 'avoid'
        }
