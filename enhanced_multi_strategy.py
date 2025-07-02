#!/usr/bin/env python3
"""
Enhanced Multi-Strategy Trading System with Advanced Technical Analysis

This module integrates advanced technical indicators, volume analysis,
pattern recognition, and market microstructure analysis for superior signal quality.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import logging

# Import our enhanced analysis modules
from enhanced_technical_analysis import EnhancedTechnicalAnalysis
from volume_analyzer import VolumeAnalyzer
from market_microstructure import MarketMicrostructureAnalyzer

class EnhancedMultiStrategy:
    """
    Advanced multi-strategy system with comprehensive market analysis
    """

    def __init__(self, confidence_threshold: float = 0.45):
        self.confidence_threshold = confidence_threshold
        self.logger = logging.getLogger(__name__)

        # Initialize analysis modules
        self.technical_analyzer = EnhancedTechnicalAnalysis()
        self.volume_analyzer = VolumeAnalyzer()
        self.microstructure_analyzer = MarketMicrostructureAnalyzer()

        # Strategy components
        self.strategies = {
            'multi_rsi_binance': self._enhanced_rsi_strategy,  # Updated to reflect Binance multi-RSI
            'stochastic_rsi': self._stochastic_rsi_strategy,
            'williams_r': self._williams_r_strategy,
            'money_flow_index': self._money_flow_index_strategy,
            'volume_flow': self._volume_flow_strategy,
            'pattern_recognition': self._pattern_recognition_strategy,
            'support_resistance': self._support_resistance_strategy,
            'microstructure': self._microstructure_strategy,
            'multi_timeframe': self._multi_timeframe_strategy
        }

        # Strategy weights (can be adjusted based on performance)
        self.strategy_weights = {
            'multi_rsi_binance': 1.3,  # Increased weight for sophisticated multi-RSI
            'stochastic_rsi': 1.2,  # Higher weight for more sophisticated indicator
            'williams_r': 0.8,
            'money_flow_index': 1.1,  # Volume-based, good for crypto
            'volume_flow': 1.3,  # Important for crypto
            'pattern_recognition': 1.0,
            'support_resistance': 0.9,
            'microstructure': 1.1,
            'multi_timeframe': 1.2
        }

    def get_enhanced_consensus_signal(self, df: pd.DataFrame, orderbook_data: Optional[Dict] = None) -> Dict:
        """
        Get comprehensive consensus signal from all enhanced strategies
        """
        if len(df) < 50:
            return {
                'action': 'HOLD',
                'confidence': 0.0,
                'reason': 'Insufficient data for enhanced analysis',
                'strategy_signals': {},
                'market_analysis': {},
                'risk_assessment': {}
            }

        # Run all strategy analyses
        strategy_signals = {}
        total_weighted_confidence = 0.0
        weighted_votes = {'BUY': 0.0, 'SELL': 0.0, 'HOLD': 0.0}

        for strategy_name, strategy_func in self.strategies.items():
            try:
                signal = strategy_func(df, orderbook_data)
                strategy_signals[strategy_name] = signal

                # Apply strategy weight
                weight = self.strategy_weights.get(strategy_name, 1.0)
                weighted_confidence = signal['confidence'] * weight

                # Accumulate weighted votes
                weighted_votes[signal['action']] += weighted_confidence
                total_weighted_confidence += weighted_confidence

            except Exception as e:
                self.logger.warning(f"Error in strategy {strategy_name}: {e}")
                strategy_signals[strategy_name] = {
                    'action': 'HOLD',
                    'confidence': 0.0,
                    'reason': f'Error: {str(e)}'
                }

        # Determine consensus action
        if total_weighted_confidence > 0:
            normalized_votes = {k: v / total_weighted_confidence for k, v in weighted_votes.items()}
        else:
            normalized_votes = {'BUY': 0.0, 'SELL': 0.0, 'HOLD': 1.0}

        # Find dominant signal
        consensus_action = max(normalized_votes.keys(), key=lambda k: normalized_votes[k])
        consensus_confidence = normalized_votes[consensus_action]

        # Apply confidence threshold
        if consensus_confidence < self.confidence_threshold:
            consensus_action = 'HOLD'
            consensus_confidence = 0.0

        # Generate comprehensive market analysis
        market_analysis = self._comprehensive_market_analysis(df, orderbook_data)

        # Risk assessment
        risk_assessment = self._assess_trading_risk(df, strategy_signals, market_analysis)

        # Adjust signal based on risk
        if risk_assessment['risk_level'] == 'high' and consensus_action != 'HOLD':
            consensus_confidence *= 0.7  # Reduce confidence in high-risk conditions

        # Generate detailed reason
        primary_strategies = [name for name, signal in strategy_signals.items()
                            if signal['action'] == consensus_action and signal['confidence'] > 0.3]

        reason = self._generate_consensus_reason(consensus_action, primary_strategies,
                                               market_analysis, normalized_votes)

        return {
            'action': consensus_action,
            'confidence': min(1.0, consensus_confidence),
            'reason': reason,
            'strategy_signals': strategy_signals,
            'weighted_votes': normalized_votes,
            'market_analysis': market_analysis,
            'risk_assessment': risk_assessment,
            'signal_quality': self._assess_signal_quality(strategy_signals, market_analysis),
            'execution_timing': self._assess_execution_timing(df, market_analysis)
        }

    # =============================================================================
    # INDIVIDUAL STRATEGY METHODS
    # =============================================================================

    def _enhanced_rsi_strategy(self, df: pd.DataFrame, orderbook_data: Optional[Dict] = None) -> Dict:
        """Enhanced Multi-RSI strategy using Binance standard RSI(6), RSI(12), RSI(24)"""
        if len(df) < 25:
            return {'action': 'HOLD', 'confidence': 0.0, 'reason': 'Insufficient data'}

        # Calculate Binance-standard RSI periods
        delta = df['close'].diff()

        # RSI(6) - Very short-term, highly sensitive
        gain_6 = delta.where(delta > 0, 0).rolling(6).mean()
        loss_6 = -delta.where(delta < 0, 0).rolling(6).mean()
        rsi_6 = 100 - (100 / (1 + gain_6 / loss_6))

        # RSI(12) - Short-term momentum
        gain_12 = delta.where(delta > 0, 0).rolling(12).mean()
        loss_12 = -delta.where(delta < 0, 0).rolling(12).mean()
        rsi_12 = 100 - (100 / (1 + gain_12 / loss_12))

        # RSI(24) - Medium-term trend
        gain_24 = delta.where(delta > 0, 0).rolling(24).mean()
        loss_24 = -delta.where(delta < 0, 0).rolling(24).mean()
        rsi_24 = 100 - (100 / (1 + gain_24 / loss_24))

        # Current RSI values
        current_rsi_6 = rsi_6.iloc[-1]
        current_rsi_12 = rsi_12.iloc[-1]
        current_rsi_24 = rsi_24.iloc[-1]

        # Multi-RSI consensus analysis
        rsi_values = [current_rsi_6, current_rsi_12, current_rsi_24]
        rsi_weights = [0.5, 0.3, 0.2]  # Higher weight to more sensitive RSI(6)

        # Weighted average RSI
        weighted_rsi = sum(rsi * weight for rsi, weight in zip(rsi_values, rsi_weights))

        # RSI momentum analysis (slope)
        rsi_6_slope = rsi_6.iloc[-1] - rsi_6.iloc[-3] if len(rsi_6) >= 3 else 0
        rsi_12_slope = rsi_12.iloc[-1] - rsi_12.iloc[-3] if len(rsi_12) >= 3 else 0

        # Consensus strength (how many RSIs agree)
        oversold_count = sum(1 for rsi in rsi_values if rsi <= 30)
        overbought_count = sum(1 for rsi in rsi_values if rsi >= 70)

        # Divergence detection using RSI(12) as primary
        divergence = self.technical_analyzer._detect_rsi_divergence(df['close'], rsi_12)

        # Enhanced signal generation with multi-RSI consensus
        if oversold_count >= 2:  # At least 2 RSIs show oversold
            # Crypto-optimized oversold threshold (30 instead of 25)
            confidence = min(1.0, (35 - weighted_rsi) / 35 * 1.4)

            # Boost confidence based on consensus strength
            if oversold_count == 3:  # All RSIs oversold
                confidence *= 1.3
            elif current_rsi_6 <= 25:  # Very oversold on fast RSI
                confidence *= 1.2

            # Momentum confirmation
            if rsi_6_slope > 2:  # RSI(6) turning up strongly
                confidence *= 1.15
            elif rsi_6_slope > 0 and rsi_12_slope > 0:  # Both turning up
                confidence *= 1.1

            # Divergence confirmation
            if divergence:
                confidence *= 1.2

            return {
                'action': 'BUY',
                'confidence': min(1.0, confidence),
                'reason': f'Multi-RSI oversold: RSI6={current_rsi_6:.1f}, RSI12={current_rsi_12:.1f}, RSI24={current_rsi_24:.1f} ({oversold_count}/3 oversold, div: {divergence})'
            }

        elif overbought_count >= 2:  # At least 2 RSIs show overbought
            # Crypto-optimized overbought threshold (70 instead of 75)
            confidence = min(1.0, (weighted_rsi - 65) / 35 * 1.4)

            # Boost confidence based on consensus strength
            if overbought_count == 3:  # All RSIs overbought
                confidence *= 1.3
            elif current_rsi_6 >= 75:  # Very overbought on fast RSI
                confidence *= 1.2

            # Momentum confirmation
            if rsi_6_slope < -2:  # RSI(6) turning down strongly
                confidence *= 1.15
            elif rsi_6_slope < 0 and rsi_12_slope < 0:  # Both turning down
                confidence *= 1.1

            # Divergence confirmation
            if divergence:
                confidence *= 1.2

            return {
                'action': 'SELL',
                'confidence': min(1.0, confidence),
                'reason': f'Multi-RSI overbought: RSI6={current_rsi_6:.1f}, RSI12={current_rsi_12:.1f}, RSI24={current_rsi_24:.1f} ({overbought_count}/3 overbought, div: {divergence})'
            }

        return {
            'action': 'HOLD',
            'confidence': 0.0,
            'reason': f'Multi-RSI neutral: RSI6={current_rsi_6:.1f}, RSI12={current_rsi_12:.1f}, RSI24={current_rsi_24:.1f}'
        }

    def _stochastic_rsi_strategy(self, df: pd.DataFrame, orderbook_data: Optional[Dict] = None) -> Dict:
        """Stochastic RSI strategy"""
        stoch_rsi_result = self.technical_analyzer.calculate_stochastic_rsi(df)
        return {
            'action': stoch_rsi_result['signal'],
            'confidence': stoch_rsi_result['confidence'],
            'reason': f"Stoch RSI: %K={stoch_rsi_result['values']['k']:.1f}, %D={stoch_rsi_result['values']['d']:.1f}"
        }

    def _williams_r_strategy(self, df: pd.DataFrame, orderbook_data: Optional[Dict] = None) -> Dict:
        """Williams %R strategy"""
        williams_result = self.technical_analyzer.calculate_williams_r(df)
        return {
            'action': williams_result['signal'],
            'confidence': williams_result['confidence'],
            'reason': f"Williams %R: {williams_result['value']:.1f}"
        }

    def _money_flow_index_strategy(self, df: pd.DataFrame, orderbook_data: Optional[Dict] = None) -> Dict:
        """Money Flow Index strategy"""
        mfi_result = self.technical_analyzer.calculate_money_flow_index(df)
        return {
            'action': mfi_result['signal'],
            'confidence': mfi_result['confidence'],
            'reason': f"MFI: {mfi_result['value']:.1f}"
        }

    def _volume_flow_strategy(self, df: pd.DataFrame, orderbook_data: Optional[Dict] = None) -> Dict:
        """Advanced volume flow analysis"""
        volume_analysis = self.volume_analyzer.analyze_volume_flow(df)
        return {
            'action': volume_analysis['flow_signal'],
            'confidence': volume_analysis['confidence'],
            'reason': f"Volume Flow: {volume_analysis['volume_metrics']['institutional_flow']}"
        }

    def _pattern_recognition_strategy(self, df: pd.DataFrame, orderbook_data: Optional[Dict] = None) -> Dict:
        """Pattern recognition strategy"""
        patterns = self.technical_analyzer.detect_reversal_patterns(df)
        if patterns['confidence'] > 0:
            return {
                'action': patterns['signal'],
                'confidence': patterns['confidence'],
                'reason': f"Pattern: {[p for p, v in patterns.items() if v and p != 'confidence' and p != 'signal']}"
            }

        return {'action': 'HOLD', 'confidence': 0.0, 'reason': 'No significant patterns detected'}

    def _support_resistance_strategy(self, df: pd.DataFrame, orderbook_data: Optional[Dict] = None) -> Dict:
        """Support and resistance strategy"""
        sr_analysis = self.technical_analyzer.detect_support_resistance(df)

        if sr_analysis['strength'] > 0.3:
            current_price = df['close'].iloc[-1]

            # Near support - potential buy
            if (sr_analysis['support'] and
                sr_analysis['distance_to_support'] and
                sr_analysis['distance_to_support'] < 0.02):
                return {
                    'action': 'BUY',
                    'confidence': sr_analysis['strength'],
                    'reason': f"Near support: ${sr_analysis['support']:.2f} (strength: {sr_analysis['strength']:.2f})"
                }

            # Near resistance - potential sell
            elif (sr_analysis['resistance'] and
                  sr_analysis['distance_to_resistance'] and
                  sr_analysis['distance_to_resistance'] < 0.02):
                return {
                    'action': 'SELL',
                    'confidence': sr_analysis['strength'],
                    'reason': f"Near resistance: ${sr_analysis['resistance']:.2f} (strength: {sr_analysis['strength']:.2f})"
                }

        return {'action': 'HOLD', 'confidence': 0.0, 'reason': 'No significant S/R levels nearby'}

    def _microstructure_strategy(self, df: pd.DataFrame, orderbook_data: Optional[Dict] = None) -> Dict:
        """Market microstructure strategy"""
        microstructure = self.microstructure_analyzer.analyze_market_structure(df, orderbook_data)
        return {
            'action': microstructure['structure_signal'],
            'confidence': microstructure['confidence'],
            'reason': f"Microstructure: {microstructure['market_quality']['quality_level']} quality"
        }

    def _multi_timeframe_strategy(self, df: pd.DataFrame, orderbook_data: Optional[Dict] = None) -> Dict:
        """Multi-timeframe consensus strategy"""
        mtf_analysis = self.technical_analyzer.multi_timeframe_consensus(df, df, df)
        return {
            'action': mtf_analysis['consensus_signal'],
            'confidence': mtf_analysis['consensus_strength'],
            'reason': f"MTF consensus: {mtf_analysis['alignment']}/{len(mtf_analysis['timeframe_signals'])*2} signals aligned"
        }

    # =============================================================================
    # COMPREHENSIVE ANALYSIS METHODS
    # =============================================================================

    def _comprehensive_market_analysis(self, df: pd.DataFrame, orderbook_data: Optional[Dict] = None) -> Dict:
        """Perform comprehensive market analysis"""

        # Volume analysis
        volume_patterns = self.volume_analyzer.detect_volume_patterns(df)
        institutional_flow = self.microstructure_analyzer.detect_institutional_flow(df)

        # Market structure
        market_structure = self.microstructure_analyzer.analyze_market_structure(df, orderbook_data)

        # Volatility and trend analysis
        returns = df['close'].pct_change()
        current_volatility = returns.rolling(20).std().iloc[-1] * np.sqrt(1440)  # Annualized

        # Crypto-optimized trend strength using Binance standard MA periods
        # MA7 (1 week) - captures short-term momentum in 24/7 crypto markets
        # MA25 (3.5 weeks) - medium-term trend, better for crypto volatility cycles
        # MA99 (14+ weeks) - long-term trend, crypto-optimized replacement for MA200
        ma_7 = df['close'].rolling(7).mean()    # Short-term (1 week in crypto)
        ma_25 = df['close'].rolling(25).mean()  # Medium-term (3.5 weeks)
        ma_99 = df['close'].rolling(99).mean()  # Long-term (14+ weeks)

        trend_strength = 0.0
        trend_direction = 'neutral'

        # Enhanced crypto trend detection with additional confluence factors
        current_price = df['close'].iloc[-1]

        # Calculate trend alignment score
        ma7_vs_25 = (ma_7.iloc[-1] - ma_25.iloc[-1]) / ma_25.iloc[-1] if ma_25.iloc[-1] > 0 else 0
        ma25_vs_99 = (ma_25.iloc[-1] - ma_99.iloc[-1]) / ma_99.iloc[-1] if ma_99.iloc[-1] > 0 else 0
        price_vs_ma7 = (current_price - ma_7.iloc[-1]) / ma_7.iloc[-1] if ma_7.iloc[-1] > 0 else 0

        # Crypto-optimized trend detection with momentum consideration
        if ma_7.iloc[-1] > ma_25.iloc[-1] > ma_99.iloc[-1]:
            trend_direction = 'strong_uptrend'
            # Strengthen signal if momentum is increasing
            trend_strength = 0.8 + min(0.2, abs(ma7_vs_25) * 10)  # Cap at 1.0
        elif ma_7.iloc[-1] < ma_25.iloc[-1] < ma_99.iloc[-1]:
            trend_direction = 'strong_downtrend'
            trend_strength = 0.8 + min(0.2, abs(ma7_vs_25) * 10)  # Cap at 1.0
        elif ma_7.iloc[-1] > ma_25.iloc[-1]:
            trend_direction = 'uptrend'
            trend_strength = 0.5
        elif ma_7.iloc[-1] < ma_25.iloc[-1]:
            trend_direction = 'downtrend'
            trend_strength = 0.5

        # Market phase detection
        market_phase = self._detect_market_phase(df)

        return {
            'volatility': current_volatility,
            'trend_direction': trend_direction,
            'trend_strength': trend_strength,
            'market_phase': market_phase,
            'volume_patterns': volume_patterns,
            'institutional_flow': institutional_flow,
            'market_structure': market_structure,
            'liquidity_conditions': market_structure.get('liquidity', {}),
            'market_stress': market_structure.get('regime', {}).get('market_stress', {}),
            'trading_conditions': self._assess_trading_conditions(current_volatility, trend_strength, market_structure)
        }

    def _assess_trading_risk(self, df: pd.DataFrame, strategy_signals: Dict, market_analysis: Dict) -> Dict:
        """Assess trading risk based on multiple factors"""

        risk_factors = []
        risk_score = 0.0

        # Volatility risk
        volatility = market_analysis.get('volatility', 0.0)
        if volatility > 0.8:  # High volatility
            risk_factors.append('high_volatility')
            risk_score += 0.3
        elif volatility > 0.5:
            risk_score += 0.1

        # Market structure risk
        market_quality = market_analysis.get('market_structure', {}).get('market_quality', {})
        if market_quality.get('quality_level') == 'poor':
            risk_factors.append('poor_market_quality')
            risk_score += 0.2

        # Liquidity risk
        liquidity = market_analysis.get('liquidity_conditions', {})
        if liquidity.get('liquidity_level') == 'low':
            risk_factors.append('low_liquidity')
            risk_score += 0.2

        # Strategy disagreement risk
        signal_actions = [s['action'] for s in strategy_signals.values() if s['confidence'] > 0.1]
        if len(set(signal_actions)) > 2:  # High disagreement
            risk_factors.append('strategy_disagreement')
            risk_score += 0.1

        # Market stress risk
        stress_level = market_analysis.get('market_stress', {}).get('stress_level', 'low')
        if stress_level == 'high':
            risk_factors.append('market_stress')
            risk_score += 0.3
        elif stress_level == 'medium':
            risk_score += 0.1

        # Trend reversal risk
        if market_analysis.get('market_phase') == 'reversal':
            risk_factors.append('potential_reversal')
            risk_score += 0.15

        # Determine risk level
        if risk_score >= 0.6:
            risk_level = 'high'
        elif risk_score >= 0.3:
            risk_level = 'medium'
        else:
            risk_level = 'low'

        return {
            'risk_level': risk_level,
            'risk_score': min(1.0, risk_score),
            'risk_factors': risk_factors,
            'recommended_position_adjustment': self._get_position_adjustment(risk_level, risk_score)
        }

    def _assess_signal_quality(self, strategy_signals: Dict, market_analysis: Dict) -> Dict:
        """Assess the quality of trading signals"""

        # Signal consensus
        signals_with_confidence = [(s['action'], s['confidence']) for s in strategy_signals.values()
                                 if s['confidence'] > 0.1]

        if not signals_with_confidence:
            return {'quality': 'poor', 'score': 0.0, 'factors': ['no_signals']}

        # Calculate consensus strength
        actions = [action for action, _ in signals_with_confidence]
        confidences = [conf for _, conf in signals_with_confidence]

        # Count votes
        buy_votes = actions.count('BUY')
        sell_votes = actions.count('SELL')
        hold_votes = actions.count('HOLD')

        total_votes = len(actions)
        consensus_ratio = max(buy_votes, sell_votes, hold_votes) / total_votes if total_votes > 0 else 0

        # Average confidence
        avg_confidence = np.mean(confidences) if confidences else 0

        # Market condition alignment
        market_conditions_favorable = (
            market_analysis.get('trading_conditions', {}).get('favorable', False) and
            market_analysis.get('market_structure', {}).get('market_quality', {}).get('quality_level') in ['excellent', 'good']
        )

        # Calculate quality score
        quality_score = (consensus_ratio * 0.4 + avg_confidence * 0.4 +
                        (0.2 if market_conditions_favorable else 0))

        # Determine quality level
        if quality_score >= 0.8:
            quality = 'excellent'
        elif quality_score >= 0.6:
            quality = 'good'
        elif quality_score >= 0.4:
            quality = 'fair'
        else:
            quality = 'poor'

        quality_factors = []
        if consensus_ratio > 0.7:
            quality_factors.append('strong_consensus')
        if avg_confidence > 0.6:
            quality_factors.append('high_confidence')
        if market_conditions_favorable:
            quality_factors.append('favorable_conditions')

        return {
            'quality': quality,
            'score': quality_score,
            'consensus_ratio': consensus_ratio,
            'avg_confidence': avg_confidence,
            'factors': quality_factors
        }

    def _assess_execution_timing(self, df: pd.DataFrame, market_analysis: Dict) -> Dict:
        """Assess optimal execution timing"""

        # Current market conditions
        volatility = market_analysis.get('volatility', 0.0)
        liquidity_level = market_analysis.get('liquidity_conditions', {}).get('liquidity_level', 'medium')

        # Time-based factors (simplified - would need real-time data)
        current_hour = pd.Timestamp.now().hour

        # Market hours assessment (assuming UTC)
        if 13 <= current_hour <= 21:  # US market hours
            market_hours_factor = 'high_activity'
        elif 8 <= current_hour <= 17:  # European market hours
            market_hours_factor = 'medium_activity'
        else:
            market_hours_factor = 'low_activity'

        # Execution recommendation
        if liquidity_level == 'high' and volatility < 0.5:
            execution_quality = 'optimal'
            recommendation = 'execute_immediately'
        elif liquidity_level == 'medium' and volatility < 0.8:
            execution_quality = 'good'
            recommendation = 'execute_with_limit_orders'
        elif volatility > 0.8:
            execution_quality = 'challenging'
            recommendation = 'wait_for_volatility_reduction'
        else:
            execution_quality = 'acceptable'
            recommendation = 'execute_with_caution'

        return {
            'execution_quality': execution_quality,
            'recommendation': recommendation,
            'market_hours_factor': market_hours_factor,
            'optimal_execution_window': self._get_optimal_execution_window(volatility, liquidity_level)
        }

    # =============================================================================
    # HELPER METHODS
    # =============================================================================

    def _detect_market_phase(self, df: pd.DataFrame) -> str:
        """Detect current market phase"""
        if len(df) < 100:  # Need more data for MA99
            return 'insufficient_data'

        # Price action analysis using crypto-optimized periods
        ma_25 = df['close'].rolling(25).mean()  # Medium-term
        ma_99 = df['close'].rolling(99).mean()  # Long-term

        # Volatility analysis (keep 20 period for consistency)
        returns = df['close'].pct_change()
        current_vol = returns.rolling(20).std().iloc[-1]
        avg_vol = returns.rolling(100).std().iloc[-1] if len(returns) >= 100 else current_vol

        # Volume analysis
        volume_trend = self.volume_analyzer._get_volume_trend(df['volume'])

        # Phase determination using crypto-optimized MAs
        price_above_ma25 = df['close'].iloc[-1] > ma_25.iloc[-1]
        price_above_ma99 = df['close'].iloc[-1] > ma_99.iloc[-1]
        ma25_above_ma99 = ma_25.iloc[-1] > ma_99.iloc[-1]

        high_vol = current_vol > avg_vol * 1.3

        if price_above_ma25 and price_above_ma99 and ma25_above_ma99:
            if high_vol and volume_trend == 'increasing':
                return 'strong_uptrend'
            else:
                return 'uptrend'
        elif not price_above_ma25 and not price_above_ma99 and not ma25_above_ma99:
            if high_vol and volume_trend == 'increasing':
                return 'strong_downtrend'
            else:
                return 'downtrend'
        elif high_vol:
            return 'reversal'
        else:
            return 'consolidation'

    def _assess_trading_conditions(self, volatility: float, trend_strength: float,
                                 market_structure: Dict) -> Dict:
        """Assess overall trading conditions"""

        conditions = []
        favorable = True

        # Volatility assessment
        if 0.2 <= volatility <= 0.6:  # Optimal volatility range for crypto
            conditions.append('optimal_volatility')
        elif volatility > 0.8:
            conditions.append('high_volatility')
            favorable = False
        elif volatility < 0.1:
            conditions.append('low_volatility')

        # Trend assessment
        if trend_strength > 0.6:
            conditions.append('strong_trend')
        elif trend_strength > 0.3:
            conditions.append('moderate_trend')
        else:
            conditions.append('weak_trend')

        # Market quality
        quality = market_structure.get('market_quality', {}).get('quality_level', 'fair')
        if quality in ['excellent', 'good']:
            conditions.append('good_market_quality')
        else:
            favorable = False

        return {
            'favorable': favorable,
            'conditions': conditions,
            'overall_assessment': 'favorable' if favorable else 'challenging'
        }

    def _get_position_adjustment(self, risk_level: str, risk_score: float) -> Dict:
        """Get position size adjustment based on risk"""
        if risk_level == 'high':
            return {
                'size_multiplier': 0.5,
                'recommendation': 'reduce_position_size',
                'justification': f'High risk (score: {risk_score:.2f}) - reduce exposure'
            }
        elif risk_level == 'medium':
            return {
                'size_multiplier': 0.8,
                'recommendation': 'moderate_position_size',
                'justification': f'Medium risk (score: {risk_score:.2f}) - moderate exposure'
            }
        else:
            return {
                'size_multiplier': 1.0,
                'recommendation': 'normal_position_size',
                'justification': f'Low risk (score: {risk_score:.2f}) - normal exposure'
            }

    def _get_optimal_execution_window(self, volatility: float, liquidity_level: str) -> str:
        """Get optimal execution window"""
        if volatility > 0.8:
            return 'wait_for_calm'
        elif liquidity_level == 'low':
            return 'wait_for_higher_liquidity'
        else:
            return 'immediate'

    def _generate_consensus_reason(self, action: str, primary_strategies: List[str],
                                 market_analysis: Dict, votes: Dict) -> str:
        """Generate detailed reason for consensus signal"""

        if action == 'HOLD':
            return f"HOLD consensus - insufficient confidence or conflicting signals (votes: {votes})"

        # Primary contributing strategies
        strategy_summary = ', '.join(primary_strategies[:3])  # Top 3 strategies

        # Market context
        market_phase = market_analysis.get('market_phase', 'unknown')
        trend = market_analysis.get('trend_direction', 'neutral')

        # Volume context
        institutional_flow = market_analysis.get('institutional_flow', {}).get('flow_type', 'unknown')

        reason = f"{action} consensus from {strategy_summary} | "
        reason += f"Market: {market_phase} ({trend}) | "
        reason += f"Flow: {institutional_flow} | "
        reason += f"Confidence: {votes[action]:.2f}"

        return reason

    def get_strategy_performance_metrics(self) -> Dict:
        """Get performance metrics for each strategy (placeholder for future implementation)"""
        return {
            'individual_performance': {strategy: {'win_rate': 0.0, 'avg_return': 0.0}
                                     for strategy in self.strategies.keys()},
            'optimal_weights': self.strategy_weights.copy()
        }
