# =============================================================================
# SUCCESS RATE ENHANCER - Advanced Signal Quality Filters
# =============================================================================

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from log_utils import log_message

def calculate_rsi(prices: pd.Series, window: int = 14) -> pd.Series:
    """Calculate RSI manually"""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict:
    """Calculate MACD manually"""
    ema_fast = prices.ewm(span=fast).mean()
    ema_slow = prices.ewm(span=slow).mean()
    macd_line = ema_fast - ema_slow
    macd_signal = macd_line.ewm(span=signal).mean()
    return {'macd': macd_line, 'signal': macd_signal}

def calculate_atr(high: pd.Series, low: pd.Series, close: pd.Series, window: int = 14) -> pd.Series:
    """Calculate Average True Range manually"""
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return tr.rolling(window=window).mean()

def check_anti_whipsaw_protection(signal: Dict, current_price: float, df: pd.DataFrame) -> bool:
    """
    🛡️ Anti-whipsaw protection to prevent buy-high/sell-low cycles
    
    This function prevents trading in conditions that often lead to whipsaws:
    - Rapid price reversals after recent trades
    - High volatility without clear direction
    - Choppy sideways markets
    - Recent failed trades in similar conditions
    
    Returns True if trade is safe, False if whipsaw risk is high
    """
    try:
        if len(df) < 20:
            return True  # Not enough data, allow trade
            
        # Get recent price data
        recent_prices = df['close'].tail(10).values
        current_rsi = calculate_rsi(df['close']).iloc[-1] if len(df) >= 14 else 50
        
        # 1. Check for recent rapid reversals (whipsaw indicator)
        price_changes = []
        for i in range(1, len(recent_prices)):
            change_pct = (recent_prices[i] - recent_prices[i-1]) / recent_prices[i-1]
            price_changes.append(change_pct)
        
        # Count direction changes in last 10 periods
        direction_changes = 0
        for i in range(1, len(price_changes)):
            if (price_changes[i] > 0) != (price_changes[i-1] > 0):
                direction_changes += 1
        
        # Too many direction changes = choppy market
        if direction_changes >= 6:  # More than 6 direction changes in 10 periods
            log_message("⚠️ Anti-whipsaw: Too many price reversals detected (choppy market)")
            return False
            
        # 2. Check for excessive volatility without trend
        if len(df) >= 20:
            volatility = df['close'].tail(20).std() / df['close'].tail(20).mean()
            trend_strength = abs(df['close'].iloc[-1] - df['close'].iloc[-20]) / df['close'].iloc[-20]
            
            # High volatility but low trend = whipsaw conditions
            if volatility > 0.03 and trend_strength < 0.02:
                log_message(f"⚠️ Anti-whipsaw: High volatility ({volatility:.3f}) without trend ({trend_strength:.3f})")
                return False
        
        # 3. RSI divergence check (price vs momentum)
        if len(df) >= 20:
            rsi_series = calculate_rsi(df['close'])
            if len(rsi_series) >= 10:
                recent_rsi = rsi_series.tail(10)
                
                # Check for bearish divergence on buy signals
                if signal['action'] == 'BUY':
                    price_trend = (df['close'].iloc[-1] - df['close'].iloc[-10]) / df['close'].iloc[-10]
                    rsi_trend = recent_rsi.iloc[-1] - recent_rsi.iloc[-5]
                    
                    # Price rising but RSI falling = bearish divergence
                    if price_trend > 0.01 and rsi_trend < -5:
                        log_message("⚠️ Anti-whipsaw: Bearish RSI divergence on BUY signal")
                        return False
        
        # 4. Recent failed trade pattern detection
        # If we just had a losing trade, be extra cautious about similar setups
        if hasattr(signal, 'confidence') and signal.get('confidence', 0) < 0.7:
            # For lower confidence signals, add extra whipsaw protection
            if direction_changes >= 4:
                log_message("⚠️ Anti-whipsaw: Low confidence + choppy conditions")
                return False
        
        # 5. Volume confirmation for trend strength
        if 'volume' in df.columns and len(df) >= 10:
            recent_volume = df['volume'].tail(5).mean()
            avg_volume = df['volume'].tail(20).mean()
            
            # Low volume in volatile conditions often leads to whipsaws
            if recent_volume < avg_volume * 0.7 and direction_changes >= 4:
                log_message("⚠️ Anti-whipsaw: Low volume + choppy price action")
                return False
        
        return True  # Trade passed all whipsaw checks
        
    except Exception as e:
        log_message(f"⚠️ Anti-whipsaw protection error: {e}")
        return True  # Default to allowing trade on error

class SuccessRateEnhancer:
    """
    Advanced signal quality filters to improve win rate through:
    - Multi-timeframe analysis
    - Support/resistance detection
    - Momentum divergence analysis
    - Volume profile analysis
    - Market structure analysis
    """
    
    def __init__(self):
        self.support_levels = []
        self.resistance_levels = []
        self.last_structure_update = 0
        
    def analyze_signal_quality(self, df: pd.DataFrame, signal: Dict, current_price: float) -> Dict:
        """
        Comprehensive signal quality analysis to improve win rate
        Returns enhanced signal with quality score and recommendations
        """
        try:
            quality_analysis = {
                'overall_quality_score': 0.0,
                'quality_factors': {},
                'recommendations': [],
                'filters_passed': {},
                'enhanced_confidence': signal.get('confidence', 0.0)
            }
            
            # 1. Multi-timeframe confirmation
            mtf_score = self._analyze_multi_timeframe(df, signal)
            quality_analysis['quality_factors']['multi_timeframe'] = mtf_score
            
            # 2. Support/Resistance analysis
            sr_score = self._analyze_support_resistance(df, current_price, signal)
            quality_analysis['quality_factors']['support_resistance'] = sr_score
            
            # 3. Volume profile analysis
            volume_score = self._analyze_volume_profile(df, signal)
            quality_analysis['quality_factors']['volume_profile'] = volume_score
            
            # 4. Momentum divergence analysis
            momentum_score = self._analyze_momentum_divergence(df, signal)
            quality_analysis['quality_factors']['momentum_divergence'] = momentum_score
            
            # 5. Market structure analysis
            structure_score = self._analyze_market_structure(df, signal)
            quality_analysis['quality_factors']['market_structure'] = structure_score
            
            # 6. Risk/Reward analysis
            rr_score = self._analyze_risk_reward(df, current_price, signal)
            quality_analysis['quality_factors']['risk_reward'] = rr_score
            
            # Calculate overall quality score (weighted average)
            weights = {
                'multi_timeframe': 0.20,
                'support_resistance': 0.25,
                'volume_profile': 0.15,
                'momentum_divergence': 0.15,
                'market_structure': 0.15,
                'risk_reward': 0.10
            }
            
            overall_score = sum(
                quality_analysis['quality_factors'][factor] * weight 
                for factor, weight in weights.items()
            )
            
            quality_analysis['overall_quality_score'] = overall_score
            
            # Enhance confidence based on quality score
            confidence_multiplier = 0.5 + (overall_score * 0.5)  # 0.5 to 1.0 multiplier
            quality_analysis['enhanced_confidence'] = min(0.95, signal.get('confidence', 0.0) * confidence_multiplier)
            
            # Generate recommendations
            quality_analysis['recommendations'] = self._generate_recommendations(quality_analysis)
            
            # Set quality filters
            quality_analysis['filters_passed'] = {
                'minimum_quality': overall_score >= 0.6,
                'strong_quality': overall_score >= 0.75,
                'exceptional_quality': overall_score >= 0.85
            }
            
            return quality_analysis
            
        except Exception as e:
            log_message(f"❌ Error in signal quality analysis: {e}")
            return {
                'overall_quality_score': 0.3,
                'quality_factors': {},
                'recommendations': ['Quality analysis failed - use caution'],
                'filters_passed': {'minimum_quality': False},
                'enhanced_confidence': signal.get('confidence', 0.0) * 0.8
            }
    
    def _analyze_multi_timeframe(self, df: pd.DataFrame, signal: Dict) -> float:
        """Analyze trend alignment across multiple timeframes"""
        try:
            if len(df) < 50:
                return 0.3
            
            score = 0.0
            
            # Short-term trend (5-period)
            ma5 = df['close'].rolling(5).mean()
            short_trend = 1 if ma5.iloc[-1] > ma5.iloc[-5] else -1
            
            # Medium-term trend (20-period)
            ma20 = df['close'].rolling(20).mean()
            medium_trend = 1 if ma20.iloc[-1] > ma20.iloc[-10] else -1
            
            # Long-term trend (50-period)
            ma50 = df['close'].rolling(50).mean()
            long_trend = 1 if ma50.iloc[-1] > ma50.iloc[-20] else -1
            
            # Check alignment with signal
            if signal.get('action') == 'BUY':
                # For BUY signals, prefer aligned uptrends
                if short_trend == 1 and medium_trend == 1:
                    score += 0.4
                elif short_trend == 1:
                    score += 0.2
                    
                if long_trend == 1:
                    score += 0.3
                elif long_trend == -1 and medium_trend == 1:
                    # Counter-trend opportunity (medium-term up, long-term down)
                    score += 0.2
                    
            elif signal.get('action') == 'SELL':
                # For SELL signals, prefer aligned downtrends or overbought in uptrend
                if short_trend == -1 and medium_trend == -1:
                    score += 0.4
                elif short_trend == -1:
                    score += 0.2
                    
                # In uptrend, selling at resistance can be profitable
                if long_trend == 1 and short_trend == -1:
                    score += 0.3
            
            # Price position relative to moving averages
            current_price = df['close'].iloc[-1]
            if current_price > ma5.iloc[-1] > ma20.iloc[-1]:
                score += 0.3 if signal.get('action') == 'BUY' else 0.1
            elif current_price < ma5.iloc[-1] < ma20.iloc[-1]:
                score += 0.3 if signal.get('action') == 'SELL' else 0.1
                
            return min(1.0, score)
            
        except Exception as e:
            log_message(f"❌ Multi-timeframe analysis error: {e}")
            return 0.3
    
    def _analyze_support_resistance(self, df: pd.DataFrame, current_price: float, signal: Dict) -> float:
        """Analyze proximity to support/resistance levels"""
        try:
            if len(df) < 20:
                return 0.3
            
            score = 0.0
            
            # Calculate pivot points (simplified)
            high_20 = df['high'].rolling(20).max()
            low_20 = df['low'].rolling(20).min()
            
            # Recent highs and lows as resistance/support
            recent_high = df['high'].iloc[-10:].max()
            recent_low = df['low'].iloc[-10:].min()
            
            # Support/resistance strength
            price_range = recent_high - recent_low
            
            if signal.get('action') == 'BUY':
                # Good to buy near support
                distance_to_support = (current_price - recent_low) / price_range
                if distance_to_support < 0.2:  # Within 20% of support
                    score += 0.6
                elif distance_to_support < 0.4:  # Within 40% of support
                    score += 0.3
                    
                # Avoid buying near resistance
                distance_to_resistance = (recent_high - current_price) / price_range
                if distance_to_resistance > 0.5:  # Far from resistance
                    score += 0.4
                    
            elif signal.get('action') == 'SELL':
                # Good to sell near resistance
                distance_to_resistance = (recent_high - current_price) / price_range
                if distance_to_resistance < 0.2:  # Within 20% of resistance
                    score += 0.6
                elif distance_to_resistance < 0.4:  # Within 40% of resistance
                    score += 0.3
                    
                # Avoid selling near support
                distance_to_support = (current_price - recent_low) / price_range
                if distance_to_support > 0.5:  # Far from support
                    score += 0.4
            
            return min(1.0, score)
            
        except Exception as e:
            log_message(f"❌ Support/resistance analysis error: {e}")
            return 0.3
    
    def _analyze_volume_profile(self, df: pd.DataFrame, signal: Dict) -> float:
        """Analyze volume patterns for signal confirmation"""
        try:
            if 'volume' not in df.columns or len(df) < 20:
                return 0.5  # Neutral score if no volume data
            
            score = 0.0
            
            # Recent volume vs average
            recent_volume = df['volume'].iloc[-5:].mean()
            avg_volume = df['volume'].iloc[-20:].mean()
            volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 1
            
            # Volume confirmation for signals
            if signal.get('action') in ['BUY', 'SELL']:
                if volume_ratio > 1.5:  # High volume confirmation
                    score += 0.5
                elif volume_ratio > 1.2:  # Moderate volume confirmation
                    score += 0.3
                elif volume_ratio < 0.8:  # Low volume - reduce confidence
                    score -= 0.2
            
            # Price-volume relationship
            price_change = (df['close'].iloc[-1] - df['close'].iloc[-5]) / df['close'].iloc[-5]
            
            if abs(price_change) > 0.01:  # Significant price movement
                if signal.get('action') == 'BUY' and price_change < 0 and volume_ratio > 1.3:
                    # Buying dip with high volume - good signal
                    score += 0.3
                elif signal.get('action') == 'SELL' and price_change > 0 and volume_ratio > 1.3:
                    # Selling rally with high volume - good signal
                    score += 0.3
            
            # Volume trend
            volume_trend = (df['volume'].iloc[-5:].mean() - df['volume'].iloc[-10:-5].mean()) / df['volume'].iloc[-10:-5].mean()
            if volume_trend > 0.2:  # Increasing volume
                score += 0.2
            
            return max(0.0, min(1.0, score + 0.3))  # Base score of 0.3
            
        except Exception as e:
            log_message(f"❌ Volume profile analysis error: {e}")
            return 0.5
    
    def _analyze_momentum_divergence(self, df: pd.DataFrame, signal: Dict) -> float:
        """Analyze momentum indicators for divergence signals"""
        try:
            if len(df) < 30:
                return 0.4
            
            score = 0.0
            
            # Calculate RSI
            rsi = calculate_rsi(df['close'])
            
            # Calculate MACD
            macd_data = calculate_macd(df['close'])
            macd_line = macd_data['macd']
            macd_signal = macd_data['signal']
            
            # RSI divergence analysis
            price_trend = df['close'].iloc[-5:].mean() - df['close'].iloc[-10:-5].mean()
            rsi_trend = rsi.iloc[-5:].mean() - rsi.iloc[-10:-5].mean()
            
            if signal.get('action') == 'BUY':
                # Bullish divergence: price down, RSI up
                if price_trend < 0 and rsi_trend > 0:
                    score += 0.4
                # Oversold RSI
                if rsi.iloc[-1] < 30:
                    score += 0.3
                # MACD bullish crossover
                if len(macd_line) > 1 and macd_line.iloc[-1] > macd_signal.iloc[-1] and macd_line.iloc[-2] <= macd_signal.iloc[-2]:
                    score += 0.3
                    
            elif signal.get('action') == 'SELL':
                # Bearish divergence: price up, RSI down
                if price_trend > 0 and rsi_trend < 0:
                    score += 0.4
                # Overbought RSI
                if rsi.iloc[-1] > 70:
                    score += 0.3
                # MACD bearish crossover
                if len(macd_line) > 1 and macd_line.iloc[-1] < macd_signal.iloc[-1] and macd_line.iloc[-2] >= macd_signal.iloc[-2]:
                    score += 0.3
            
            return min(1.0, score)
            
        except Exception as e:
            log_message(f"❌ Momentum divergence analysis error: {e}")
            return 0.4
    
    def _analyze_market_structure(self, df: pd.DataFrame, signal: Dict) -> float:
        """Analyze market structure for trend continuation/reversal"""
        try:
            if len(df) < 20:
                return 0.4
            
            score = 0.0
            
            # Higher highs/lower lows analysis
            recent_highs = df['high'].iloc[-10:]
            recent_lows = df['low'].iloc[-10:]
            
            # Check for higher highs and higher lows (uptrend)
            higher_highs = recent_highs.iloc[-1] > recent_highs.iloc[-5]
            higher_lows = recent_lows.iloc[-1] > recent_lows.iloc[-5]
            
            # Check for lower highs and lower lows (downtrend)
            lower_highs = recent_highs.iloc[-1] < recent_highs.iloc[-5]
            lower_lows = recent_lows.iloc[-1] < recent_lows.iloc[-5]
            
            if signal.get('action') == 'BUY':
                if higher_highs and higher_lows:
                    score += 0.5  # Strong uptrend structure
                elif higher_lows:
                    score += 0.3  # Support holding
                elif lower_lows and not lower_highs:
                    score += 0.2  # Potential reversal
                    
            elif signal.get('action') == 'SELL':
                if lower_highs and lower_lows:
                    score += 0.5  # Strong downtrend structure
                elif lower_highs:
                    score += 0.3  # Resistance holding
                elif higher_highs and not higher_lows:
                    score += 0.2  # Potential reversal
            
            # Volatility consideration
            volatility = df['close'].pct_change().rolling(10).std().iloc[-1]
            if volatility < 0.02:  # Low volatility - more predictable
                score += 0.2
            elif volatility > 0.05:  # High volatility - less predictable
                score -= 0.1
            
            return max(0.0, min(1.0, score + 0.3))  # Base score of 0.3
            
        except Exception as e:
            log_message(f"❌ Market structure analysis error: {e}")
            return 0.4
    
    def _analyze_risk_reward(self, df: pd.DataFrame, current_price: float, signal: Dict) -> float:
        """Analyze risk/reward ratio for the signal"""
        try:
            if len(df) < 20:
                return 0.4
            
            score = 0.0
            
            # Calculate ATR for stop loss estimation
            atr = calculate_atr(df['high'], df['low'], df['close']) if all(col in df.columns for col in ['high', 'low']) else None
            current_atr = atr.iloc[-1] if atr is not None and len(atr) > 0 else current_price * 0.02
            
            # Support/resistance levels for target estimation
            recent_high = df['high'].iloc[-20:].max()
            recent_low = df['low'].iloc[-20:].min()
            
            if signal.get('action') == 'BUY':
                # Estimated stop loss (below recent support or ATR-based)
                stop_loss = max(recent_low, current_price - (current_atr * 2))
                risk = current_price - stop_loss
                
                # Estimated target (next resistance or ATR-based)
                target = min(recent_high, current_price + (current_atr * 3))
                reward = target - current_price
                
            elif signal.get('action') == 'SELL':
                # Estimated stop loss (above recent resistance or ATR-based)
                stop_loss = min(recent_high, current_price + (current_atr * 2))
                risk = stop_loss - current_price
                
                # Estimated target (next support or ATR-based)
                target = max(recent_low, current_price - (current_atr * 3))
                reward = current_price - target
                
            else:
                return 0.4
            
            # Calculate risk/reward ratio
            if risk > 0:
                rr_ratio = reward / risk
                
                if rr_ratio >= 3.0:  # Excellent R:R
                    score += 0.8
                elif rr_ratio >= 2.0:  # Good R:R
                    score += 0.6
                elif rr_ratio >= 1.5:  # Acceptable R:R
                    score += 0.4
                elif rr_ratio >= 1.0:  # Minimal R:R
                    score += 0.2
                else:  # Poor R:R
                    score += 0.0
            
            return min(1.0, score)
            
        except Exception as e:
            log_message(f"❌ Risk/reward analysis error: {e}")
            return 0.4
    
    def _generate_recommendations(self, quality_analysis: Dict) -> List[str]:
        """Generate actionable recommendations based on quality analysis"""
        recommendations = []
        
        overall_score = quality_analysis['overall_quality_score']
        factors = quality_analysis['quality_factors']
        
        if overall_score >= 0.8:
            recommendations.append("🟢 Excellent signal quality - high confidence trade")
        elif overall_score >= 0.6:
            recommendations.append("🟡 Good signal quality - proceed with normal position size")
        else:
            recommendations.append("🔴 Below-average signal quality - consider reducing position size")
        
        # Specific recommendations based on factors
        if factors.get('multi_timeframe', 0) < 0.5:
            recommendations.append("⚠️ Mixed timeframe signals - use caution")
        
        if factors.get('volume_profile', 0) < 0.4:
            recommendations.append("📉 Low volume confirmation - wait for better entry")
        
        if factors.get('support_resistance', 0) > 0.7:
            recommendations.append("🎯 Excellent S/R positioning - good entry point")
        
        if factors.get('risk_reward', 0) < 0.4:
            recommendations.append("⚖️ Poor risk/reward ratio - consider alternative entry")
        
        return recommendations

# Global instance for use in bot
success_enhancer = SuccessRateEnhancer()
