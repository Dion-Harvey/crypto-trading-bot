#!/usr/bin/env python3
"""
Enhanced success rate enhancer module for crypto trading bot
"""
import time

class SuccessEnhancer:
    def __init__(self):
        self.recent_trades = []
        self.max_recent_trades = 10
        
    def analyze_signal_quality(self, df, signal, current_price):
        """Analyze signal quality with multiple factors"""
        try:
            quality_factors = {}
            
            # Multi-timeframe analysis
            quality_factors['multi_timeframe'] = self._analyze_multi_timeframe(df)
            
            # Support/resistance levels
            quality_factors['support_resistance'] = self._analyze_support_resistance(df, current_price)
            
            # Volume profile
            quality_factors['volume_profile'] = self._analyze_volume_profile(df)
            
            # Momentum divergence
            quality_factors['momentum_divergence'] = self._analyze_momentum_divergence(df)
            
            # Market structure
            quality_factors['market_structure'] = self._analyze_market_structure(df)
            
            # Risk/reward ratio
            quality_factors['risk_reward'] = self._analyze_risk_reward(signal, current_price)
            
            # Calculate overall quality score
            overall_quality = sum(quality_factors.values()) / len(quality_factors)
            
            # Enhanced confidence calculation
            base_confidence = signal.get('confidence', 0.5)
            confidence_boost = overall_quality * 0.2  # Up to 20% boost
            enhanced_confidence = min(0.95, base_confidence + confidence_boost)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(quality_factors, signal)
            
            return {
                'overall_quality_score': overall_quality,
                'enhanced_confidence': enhanced_confidence,
                'quality_factors': quality_factors,
                'recommendations': recommendations
            }
        except Exception as e:
            # Fallback for errors
            return {
                'overall_quality_score': 0.6,
                'enhanced_confidence': signal.get('confidence', 0.5) + 0.05,
                'quality_factors': {
                    'multi_timeframe': 0.6,
                    'support_resistance': 0.6,
                    'volume_profile': 0.6,
                    'momentum_divergence': 0.6,
                    'market_structure': 0.6,
                    'risk_reward': 0.6
                },
                'recommendations': [f'Error in quality analysis: {e}']
            }
    
    def _analyze_multi_timeframe(self, df):
        """Analyze multiple timeframe alignment"""
        try:
            if len(df) < 50:
                return 0.5
            
            # Short, medium, long term trends
            short_trend = (df['close'].iloc[-5:].mean() - df['close'].iloc[-10:-5].mean()) / df['close'].iloc[-10:-5].mean()
            medium_trend = (df['close'].iloc[-10:].mean() - df['close'].iloc[-20:-10].mean()) / df['close'].iloc[-20:-10].mean()
            long_trend = (df['close'].iloc[-20:].mean() - df['close'].iloc[-40:-20].mean()) / df['close'].iloc[-40:-20].mean()
            
            # Check alignment
            trends = [short_trend, medium_trend, long_trend]
            positive_trends = sum(1 for t in trends if t > 0)
            
            if positive_trends == 3:  # All aligned up
                return 0.9
            elif positive_trends == 0:  # All aligned down
                return 0.9
            elif positive_trends == 2:  # Mostly aligned
                return 0.7
            else:  # Mixed signals
                return 0.4
        except:
            return 0.5
    
    def _analyze_support_resistance(self, df, current_price):
        """Analyze proximity to support/resistance levels"""
        try:
            if len(df) < 20:
                return 0.5
            
            # Find recent highs and lows
            recent_high = df['high'].iloc[-20:].max()
            recent_low = df['low'].iloc[-20:].min()
            
            # Distance from key levels
            distance_from_high = abs(current_price - recent_high) / recent_high
            distance_from_low = abs(current_price - recent_low) / recent_low
            
            # Better score if near support (for buy) or resistance (for sell)
            min_distance = min(distance_from_high, distance_from_low)
            
            if min_distance < 0.01:  # Very close to key level
                return 0.9
            elif min_distance < 0.02:  # Close to key level
                return 0.7
            elif min_distance < 0.05:  # Moderately close
                return 0.6
            else:  # Far from key levels
                return 0.4
        except:
            return 0.5
    
    def _analyze_volume_profile(self, df):
        """Analyze volume confirmation"""
        try:
            if 'volume' not in df.columns or len(df) < 20:
                return 0.6
            
            recent_volume = df['volume'].iloc[-5:].mean()
            avg_volume = df['volume'].iloc[-20:].mean()
            
            volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 1
            
            if volume_ratio > 1.5:  # High volume
                return 0.9
            elif volume_ratio > 1.2:  # Above average
                return 0.7
            elif volume_ratio > 0.8:  # Normal volume
                return 0.6
            else:  # Low volume
                return 0.3
        except:
            return 0.6
    
    def _analyze_momentum_divergence(self, df):
        """Analyze momentum indicators"""
        try:
            if len(df) < 14:
                return 0.5
            
            # Simple RSI calculation
            price_changes = df['close'].diff()
            gains = price_changes.where(price_changes > 0, 0).rolling(14).mean()
            losses = (-price_changes.where(price_changes < 0, 0)).rolling(14).mean()
            rs = gains / losses
            rsi = 100 - (100 / (1 + rs))
            
            current_rsi = rsi.iloc[-1]
            
            # Good momentum conditions
            if 30 <= current_rsi <= 40:  # Oversold but recovering
                return 0.9
            elif 60 <= current_rsi <= 70:  # Overbought but not extreme
                return 0.8
            elif 40 <= current_rsi <= 60:  # Neutral
                return 0.6
            else:  # Extreme conditions
                return 0.4
        except:
            return 0.5
    
    def _analyze_market_structure(self, df):
        """Analyze overall market structure"""
        try:
            if len(df) < 30:
                return 0.5
            
            # Higher highs and higher lows for uptrend
            recent_highs = df['high'].iloc[-10:]
            recent_lows = df['low'].iloc[-10:]
            
            # Check for trend structure
            higher_highs = recent_highs.iloc[-1] > recent_highs.iloc[-5]
            higher_lows = recent_lows.iloc[-1] > recent_lows.iloc[-5]
            
            if higher_highs and higher_lows:  # Clear uptrend
                return 0.8
            elif not higher_highs and not higher_lows:  # Clear downtrend
                return 0.8
            else:  # Sideways/unclear
                return 0.5
        except:
            return 0.5
    
    def _analyze_risk_reward(self, signal, current_price):
        """Analyze potential risk/reward ratio"""
        try:
            # Simple risk/reward based on recent volatility
            confidence = signal.get('confidence', 0.5)
            
            # Higher confidence suggests better risk/reward
            if confidence > 0.7:
                return 0.8
            elif confidence > 0.6:
                return 0.7
            elif confidence > 0.5:
                return 0.6
            else:
                return 0.4
        except:
            return 0.5
    
    def _generate_recommendations(self, quality_factors, signal):
        """Generate actionable recommendations"""
        recommendations = []
        
        # Check each factor and provide advice
        for factor, score in quality_factors.items():
            if score < 0.5:
                recommendations.append(f"⚠️ Low {factor.replace('_', ' ')} score ({score:.2f})")
            elif score > 0.8:
                recommendations.append(f"✅ Strong {factor.replace('_', ' ')} signal ({score:.2f})")
        
        if len(recommendations) == 0:
            recommendations.append("📊 Signal quality within normal ranges")
        
        return recommendations

def check_anti_whipsaw_protection(signal, current_price, df, lookback_minutes=5):
    """
    Anti-whipsaw protection to prevent rapid buy/sell cycles
    Returns True if signal should be allowed, False if filtered
    """
    try:
        # Check for recent rapid price movements that might indicate whipsaw conditions
        if len(df) < lookback_minutes:
            return True  # Not enough data, allow signal
        
        # Calculate recent price volatility
        recent_prices = df['close'].iloc[-lookback_minutes:]
        price_changes = recent_prices.pct_change().abs()
        avg_volatility = price_changes.mean()
        
        # If volatility is extremely high, be more cautious
        if avg_volatility > 0.01:  # More than 1% average change per minute
            confidence_threshold = 0.65  # Require higher confidence
        else:
            confidence_threshold = 0.55  # Normal threshold
        
        signal_confidence = signal.get('confidence', 0.0)
        
        # Allow signal if confidence meets the dynamic threshold
        if signal_confidence >= confidence_threshold:
            return True
        
        # Additional check: avoid trading if we just had opposite signals
        action = signal.get('action', 'HOLD')
        if hasattr(check_anti_whipsaw_protection, 'last_signal_action'):
            last_action = check_anti_whipsaw_protection.last_signal_action
            if action != last_action and action in ['BUY', 'SELL']:
                # Different action from last time, require even higher confidence
                if signal_confidence < 0.7:
                    return False
        
        # Store current action for next check
        check_anti_whipsaw_protection.last_signal_action = action
        
        return True
    
    except Exception as e:
        print(f"Anti-whipsaw protection error: {e}")
        return True  # Default to allowing signal if error occurs

# Create global instance
success_enhancer = SuccessEnhancer()
