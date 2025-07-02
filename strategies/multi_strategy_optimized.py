import pandas as pd
import numpy as np

class RSIStrategy:
    def __init__(self, period=21, oversold=25, overbought=75):  # Optimized for crypto volatility
        self.period = period
        self.oversold = oversold
        self.overbought = overbought
        self.name = f"RSI_{period}_{oversold}_{overbought}"

    def calculate_rsi(self, df):
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0).rolling(self.period).mean()
        loss = -delta.where(delta < 0, 0).rolling(self.period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def get_signal(self, df):
        if len(df) < self.period + 1:
            return {'action': 'HOLD', 'confidence': 0, 'reason': 'Insufficient data for RSI'}

        rsi = self.calculate_rsi(df)
        current_rsi = rsi.iloc[-1]
        rsi_slope = rsi.iloc[-1] - rsi.iloc[-3] if len(rsi) >= 3 else 0  # RSI momentum

        if current_rsi <= self.oversold:
            # Higher confidence for deeper oversold + positive momentum
            depth_factor = max(0.1, (self.oversold - current_rsi) / 25)
            momentum_bonus = 0.2 if rsi_slope > 2 else 0  # Positive RSI divergence
            confidence = min(1.0, depth_factor + momentum_bonus)
            return {
                'action': 'BUY',
                'confidence': confidence,
                'reason': f'RSI BUY: Oversold {current_rsi:.1f} (slope: {rsi_slope:.1f})'
            }
        elif current_rsi >= self.overbought:
            # Higher confidence for deeper overbought + negative momentum
            depth_factor = max(0.1, (current_rsi - self.overbought) / 25)
            momentum_bonus = 0.2 if rsi_slope < -2 else 0  # Negative RSI divergence
            confidence = min(1.0, depth_factor + momentum_bonus)
            return {
                'action': 'SELL',
                'confidence': confidence,
                'reason': f'RSI SELL: Overbought {current_rsi:.1f} (slope: {rsi_slope:.1f})'
            }
        else:
            return {'action': 'HOLD', 'confidence': 0, 'reason': f'RSI neutral: {current_rsi:.1f}'}

class BollingerBandsStrategy:
    def __init__(self, period=20, std_dev=2.2):  # Slightly wider bands for crypto
        self.period = period
        self.std_dev = std_dev
        self.name = f"BB_{period}_{std_dev}"

    def calculate_bands(self, df):
        sma = df['close'].rolling(self.period).mean()
        std = df['close'].rolling(self.period).std()
        return sma, sma + (std * self.std_dev), sma - (std * self.std_dev)

    def get_signal(self, df):
        if len(df) < self.period:
            return {'action': 'HOLD', 'confidence': 0, 'reason': 'Insufficient data for BB'}

        sma, upper, lower = self.calculate_bands(df)
        price = df['close'].iloc[-1]
        current_upper = upper.iloc[-1]
        current_lower = lower.iloc[-1]
        current_sma = sma.iloc[-1]

        # Calculate band width for volatility context
        band_width = (current_upper - current_lower) / current_sma
        is_squeeze = band_width < 0.04  # Low volatility squeeze

        # Distance from bands
        upper_distance = (current_upper - price) / (current_upper - current_sma)
        lower_distance = (price - current_lower) / (current_sma - current_lower)

        if price <= current_lower * 1.015:  # Touch or near lower band
            confidence = min(1.0, max(0.15, (1 - lower_distance) * 1.2))
            if is_squeeze:
                confidence *= 1.3  # Higher confidence during squeezes
            return {
                'action': 'BUY',
                'confidence': confidence,
                'reason': f'BB BUY: Price ${price:.2f} near lower ${current_lower:.2f} (squeeze: {is_squeeze})'
            }
        elif price >= current_upper * 0.985:  # Touch or near upper band
            confidence = min(1.0, max(0.15, (1 - upper_distance) * 1.2))
            if is_squeeze:
                confidence *= 1.3  # Higher confidence during squeezes
            return {
                'action': 'SELL',
                'confidence': confidence,
                'reason': f'BB SELL: Price ${price:.2f} near upper ${current_upper:.2f} (squeeze: {is_squeeze})'
            }
        else:
            return {'action': 'HOLD', 'confidence': 0, 'reason': f'BB neutral: Price ${price:.2f} in middle range'}

class MeanReversionStrategy:
    def __init__(self, fast=5, slow=21, signal_line=9):  # Optimized periods
        self.fast = fast
        self.slow = slow
        self.signal_line = signal_line
        self.name = f"MeanReversion_{fast}_{slow}_{signal_line}"

    def get_signal(self, df):
        if len(df) < max(self.slow, self.signal_line) + 1:
            return {'action': 'HOLD', 'confidence': 0, 'reason': 'Insufficient data for MR'}

        # Multi-timeframe mean reversion
        fast_ma = df['close'].rolling(self.fast).mean()
        slow_ma = df['close'].rolling(self.slow).mean()
        price = df['close'].iloc[-1]
        
        # Calculate percentage deviations
        fast_dev = (price - fast_ma.iloc[-1]) / fast_ma.iloc[-1]
        slow_dev = (price - slow_ma.iloc[-1]) / slow_ma.iloc[-1]
        
        # Price momentum
        momentum_3 = (price - df['close'].iloc[-4]) / df['close'].iloc[-4] if len(df) >= 4 else 0
        momentum_5 = (price - df['close'].iloc[-6]) / df['close'].iloc[-6] if len(df) >= 6 else 0

        # Mean reversion signals
        if fast_dev < -0.008 and slow_dev < -0.015:  # Significant deviation below both MAs
            confidence = min(1.0, max(0.2, abs(slow_dev) * 40))
            # Bonus for momentum divergence (price falling but momentum slowing)
            if momentum_3 > momentum_5:
                confidence *= 1.2
            return {
                'action': 'BUY',
                'confidence': confidence,
                'reason': f'MR BUY: Price below MAs (fast: {fast_dev:.3f}, slow: {slow_dev:.3f})'
            }
        elif fast_dev > 0.008 and slow_dev > 0.015:  # Significant deviation above both MAs
            confidence = min(1.0, max(0.2, abs(slow_dev) * 40))
            # Bonus for momentum divergence (price rising but momentum slowing)
            if momentum_3 < momentum_5:
                confidence *= 1.2
            return {
                'action': 'SELL',
                'confidence': confidence,
                'reason': f'MR SELL: Price above MAs (fast: {fast_dev:.3f}, slow: {slow_dev:.3f})'
            }
        else:
            return {'action': 'HOLD', 'confidence': 0, 'reason': 'MR neutral: Price near MAs'}

class VWAPEnhancedStrategy:
    def __init__(self, period=30):  # Longer period for better VWAP
        self.period = period
        self.name = f"VWAP_Enhanced_{period}"

    def calculate_vwap(self, df):
        if len(df) < self.period:
            return None
        typical = (df['high'] + df['low'] + df['close']) / 3
        recent_data = df.tail(self.period)
        recent_typical = typical.tail(self.period)

        total_volume = recent_data['volume'].sum()
        if total_volume == 0:
            return None

        vwap = (recent_typical * recent_data['volume']).sum() / total_volume
        return vwap

    def get_signal(self, df):
        if len(df) < self.period:
            return {'action': 'HOLD', 'confidence': 0, 'reason': 'Insufficient data for VWAP'}

        price = df['close'].iloc[-1]
        vwap = self.calculate_vwap(df)

        if vwap is None:
            return {'action': 'HOLD', 'confidence': 0, 'reason': 'VWAP calculation failed'}

        # Enhanced volume analysis
        recent_vol_5 = df['volume'].tail(5).mean()
        recent_vol_15 = df['volume'].tail(15).mean()
        long_vol = df['volume'].tail(self.period).mean()
        
        vol_surge = recent_vol_5 / long_vol if long_vol > 0 else 1
        vol_trend = recent_vol_5 / recent_vol_15 if recent_vol_15 > 0 else 1

        deviation = (price - vwap) / vwap
        
        # VWAP signals with volume confirmation
        if deviation < -0.004 and vol_surge > 1.5:  # Price below VWAP with volume
            confidence = min(1.0, max(0.15, abs(deviation) * 120 * min(vol_surge / 2, 1.5)))
            if vol_trend > 1.2:  # Volume increasing
                confidence *= 1.3
            return {
                'action': 'BUY',
                'confidence': confidence,
                'reason': f'VWAP BUY: {deviation*100:.1f}% below VWAP, vol surge {vol_surge:.1f}x'
            }
        elif deviation > 0.004 and vol_surge > 1.5:  # Price above VWAP with volume
            confidence = min(1.0, max(0.15, abs(deviation) * 120 * min(vol_surge / 2, 1.5)))
            if vol_trend > 1.2:  # Volume increasing
                confidence *= 1.3
            return {
                'action': 'SELL',
                'confidence': confidence,
                'reason': f'VWAP SELL: {deviation*100:.1f}% above VWAP, vol surge {vol_surge:.1f}x'
            }
        else:
            return {'action': 'HOLD', 'confidence': 0, 'reason': f'VWAP neutral: {deviation*100:.1f}% from VWAP'}

class MultiStrategyOptimized:
    def __init__(self):
        self.strategies = [
            RSIStrategy(),
            BollingerBandsStrategy(),
            MeanReversionStrategy(),
            VWAPEnhancedStrategy()
        ]
        self.name = "Multi_Strategy_Optimized_BTC"

    def analyze_market_conditions(self, df):
        """Enhanced market condition analysis"""
        if len(df) < 50:
            return {
                'volatility': 0.01,
                'momentum': 0,
                'trend': 'neutral',
                'is_high_volatility': False,
                'is_consolidating': False,
                'volume_trend': 'normal',
                'market_phase': 'uncertain'
            }

        current_price = df['close'].iloc[-1]

        # Multi-timeframe volatility
        vol_5min = df['close'].rolling(5).std().iloc[-1] / current_price
        vol_20min = df['close'].rolling(20).std().iloc[-1] / current_price
        vol_50min = df['close'].rolling(50).std().iloc[-1] / current_price

        # Momentum analysis
        momentum_short = (current_price - df['close'].iloc[-6]) / df['close'].iloc[-6] if len(df) >= 6 else 0
        momentum_medium = (current_price - df['close'].iloc[-15]) / df['close'].iloc[-15] if len(df) >= 15 else 0
        momentum_long = (current_price - df['close'].iloc[-30]) / df['close'].iloc[-30] if len(df) >= 30 else 0

        # Trend detection with multiple confirmations
        sma_10 = df['close'].rolling(10).mean().iloc[-1]
        sma_30 = df['close'].rolling(30).mean().iloc[-1]
        sma_50 = df['close'].rolling(50).mean().iloc[-1]
        
        price_above_sma10 = current_price > sma_10
        price_above_sma30 = current_price > sma_30
        price_above_sma50 = current_price > sma_50
        sma10_above_sma30 = sma_10 > sma_30
        sma30_above_sma50 = sma_30 > sma_50

        # Volume analysis
        recent_volume = df['volume'].tail(10).mean() if 'volume' in df.columns else 1
        avg_volume = df['volume'].tail(50).mean() if 'volume' in df.columns else 1
        volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 1

        # Market phase detection
        if all([price_above_sma10, price_above_sma30, sma10_above_sma30, momentum_medium > 0.02]):
            market_phase = 'strong_uptrend'
        elif all([not price_above_sma10, not price_above_sma30, not sma10_above_sma30, momentum_medium < -0.02]):
            market_phase = 'strong_downtrend'
        elif vol_5min < 0.008 and abs(momentum_short) < 0.005:
            market_phase = 'consolidation'
        else:
            market_phase = 'transitional'

        return {
            'volatility': vol_20min,
            'volatility_5min': vol_5min,
            'momentum_short': momentum_short,
            'momentum_medium': momentum_medium,
            'momentum_long': momentum_long,
            'trend': market_phase,
            'is_high_volatility': vol_20min > 0.025,
            'is_consolidating': market_phase == 'consolidation',
            'volume_ratio': volume_ratio,
            'market_phase': market_phase,
            'price_vs_smas': {
                'above_sma10': price_above_sma10,
                'above_sma30': price_above_sma30,
                'above_sma50': price_above_sma50
            }
        }

    def get_consensus_signal(self, df):
        signals = [s.get_signal(df) for s in self.strategies]
        votes = {'BUY': 0, 'SELL': 0, 'HOLD': 0}
        confidence = {'BUY': 0.0, 'SELL': 0.0}
        strategy_details = {}

        for i, s in enumerate(signals):
            votes[s['action']] += 1
            if s['action'] in confidence:
                confidence[s['action']] += s['confidence']
            strategy_details[self.strategies[i].name] = s

        # Market conditions analysis
        market_conditions = self.analyze_market_conditions(df)

        # Dynamic consensus thresholds based on market conditions
        action = 'HOLD'
        final_confidence = 0
        reason = "No clear consensus"

        # Adjust consensus requirements based on market phase
        if market_conditions['market_phase'] == 'consolidation':
            # Require stronger consensus in consolidation (mean reversion favored)
            required_votes_strong = 3
            required_votes_moderate = 2
        elif market_conditions['market_phase'] in ['strong_uptrend', 'strong_downtrend']:
            # More conservative in strong trends (avoid fighting the trend)
            required_votes_strong = 4  # All strategies must agree
            required_votes_moderate = 3
        else:
            # Normal requirements for transitional markets
            required_votes_strong = 3
            required_votes_moderate = 2

        # Enhanced consensus logic with market-aware thresholds
        if votes['BUY'] >= required_votes_strong:
            avg_confidence = confidence['BUY'] / votes['BUY']
            final_confidence = min(1.0, avg_confidence * 1.15)  # Boost for strong consensus
            reason = f"STRONG BUY: {votes['BUY']}/4 strategies ({market_conditions['market_phase']})"
            action = 'BUY'

        elif votes['BUY'] >= required_votes_moderate and votes['SELL'] <= 1:
            avg_confidence = confidence['BUY'] / votes['BUY']
            final_confidence = min(0.85, avg_confidence * 0.95)  # Moderate confidence
            reason = f"MODERATE BUY: {votes['BUY']}/4 strategies ({market_conditions['market_phase']})"
            action = 'BUY'

        elif votes['SELL'] >= required_votes_strong:
            avg_confidence = confidence['SELL'] / votes['SELL']
            final_confidence = min(1.0, avg_confidence * 1.15)  # Boost for strong consensus
            reason = f"STRONG SELL: {votes['SELL']}/4 strategies ({market_conditions['market_phase']})"
            action = 'SELL'

        elif votes['SELL'] >= required_votes_moderate and votes['BUY'] <= 1:
            avg_confidence = confidence['SELL'] / votes['SELL']
            final_confidence = min(0.85, avg_confidence * 0.95)  # Moderate confidence
            reason = f"MODERATE SELL: {votes['SELL']}/4 strategies ({market_conditions['market_phase']})"
            action = 'SELL'

        # Market condition adjustments
        if market_conditions['is_high_volatility']:
            final_confidence *= 0.75  # Reduce confidence in high volatility
            reason += " (high vol penalty)"

        if market_conditions['volume_ratio'] < 0.6:  # Low volume
            final_confidence *= 0.85  # Reduce confidence with low volume
            reason += " (low vol penalty)"

        # Filter against strong trends (enhanced)
        if action == 'BUY' and market_conditions['market_phase'] == 'strong_downtrend':
            if market_conditions['momentum_medium'] < -0.03:  # Very strong downtrend
                final_confidence *= 0.5  # Heavily penalize counter-trend trades
                reason += " (strong downtrend filter)"
        elif action == 'SELL' and market_conditions['market_phase'] == 'strong_uptrend':
            if market_conditions['momentum_medium'] > 0.03:  # Very strong uptrend
                final_confidence *= 0.5  # Heavily penalize counter-trend trades
                reason += " (strong uptrend filter)"

        return {
            'action': action,
            'confidence': round(final_confidence, 3),
            'reason': reason,
            'individual_signals': strategy_details,
            'vote_count': votes,
            'market_conditions': market_conditions
        }
