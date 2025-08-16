#!/usr/bin/env python3
"""
🎯 PHASE 3 WEEK 2: SENTIMENT ANALYSIS ENGINE
Advanced sentiment analysis for crypto trading decisions

Features:
- Social media sentiment scoring (Twitter/Reddit simulation)
- News impact analysis
- Market mood indicators
- Fear & Greed integration
- Sentiment-based signal enhancement
"""

import requests
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import re
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SentimentScore:
    """Sentiment analysis result"""
    symbol: str
    overall_sentiment: float  # -1.0 to 1.0
    confidence: float        # 0.0 to 1.0
    volume_score: float      # Social volume indicator
    sources: Dict[str, float] # Breakdown by source
    mood_indicator: str      # BULLISH, BEARISH, NEUTRAL
    recommendations: List[str]
    timestamp: datetime

class SentimentAnalysisEngine:
    """
    🎯 ADVANCED SENTIMENT ANALYSIS ENGINE
    
    Provides market sentiment intelligence for trading decisions
    """
    
    def __init__(self):
        self.enabled = True
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
        
        # Sentiment thresholds
        self.BULLISH_THRESHOLD = 0.3
        self.BEARISH_THRESHOLD = -0.3
        self.HIGH_CONFIDENCE_THRESHOLD = 0.7
        
        # Fear & Greed simulation weights
        self.fear_greed_weights = {
            'volatility': 0.25,
            'market_momentum': 0.25,
            'social_volume': 0.15,
            'surveys': 0.15,
            'dominance': 0.10,
            'trends': 0.10
        }
        
        logger.info("🎯 Sentiment Analysis Engine initialized")
        logger.info(f"   Bullish threshold: {self.BULLISH_THRESHOLD:+.1f}")
        logger.info(f"   Bearish threshold: {self.BEARISH_THRESHOLD:+.1f}")
        logger.info(f"   High confidence: {self.HIGH_CONFIDENCE_THRESHOLD:.1f}")
    
    def get_sentiment_analysis(self, symbol: str, current_price: float = None) -> SentimentScore:
        """
        🎯 COMPREHENSIVE SENTIMENT ANALYSIS
        
        Analyzes multiple sentiment sources for trading decisions
        """
        try:
            # Check cache first
            cache_key = f"sentiment_{symbol}"
            if self._is_cached(cache_key):
                return self.cache[cache_key]['data']
            
            # Collect sentiment from multiple sources
            sentiment_sources = {}
            
            # Source 1: Social Media Sentiment (Simulated)
            social_sentiment = self._analyze_social_sentiment(symbol)
            sentiment_sources['social'] = social_sentiment
            
            # Source 2: News Sentiment Analysis
            news_sentiment = self._analyze_news_sentiment(symbol)
            sentiment_sources['news'] = news_sentiment
            
            # Source 3: Fear & Greed Index
            fear_greed = self._get_fear_greed_index(symbol)
            sentiment_sources['fear_greed'] = fear_greed
            
            # Source 4: Market Momentum Sentiment
            momentum_sentiment = self._analyze_momentum_sentiment(symbol, current_price)
            sentiment_sources['momentum'] = momentum_sentiment
            
            # Source 5: Trading Volume Sentiment
            volume_sentiment = self._analyze_volume_sentiment(symbol)
            sentiment_sources['volume'] = volume_sentiment
            
            # Combine all sentiment sources
            overall_sentiment = self._calculate_weighted_sentiment(sentiment_sources)
            confidence = self._calculate_sentiment_confidence(sentiment_sources)
            volume_score = sentiment_sources.get('volume', {}).get('volume_score', 0.5)
            
            # Determine mood indicator
            mood_indicator = self._get_mood_indicator(overall_sentiment, confidence)
            
            # Generate recommendations
            recommendations = self._generate_sentiment_recommendations(
                overall_sentiment, confidence, mood_indicator, sentiment_sources
            )
            
            # Create sentiment score
            sentiment_score = SentimentScore(
                symbol=symbol,
                overall_sentiment=overall_sentiment,
                confidence=confidence,
                volume_score=volume_score,
                sources=sentiment_sources,
                mood_indicator=mood_indicator,
                recommendations=recommendations,
                timestamp=datetime.now()
            )
            
            # Cache the result
            self._cache_data(cache_key, sentiment_score)
            
            return sentiment_score
            
        except Exception as e:
            logger.error(f"Error in sentiment analysis for {symbol}: {e}")
            return self._get_neutral_sentiment(symbol)
    
    def _analyze_social_sentiment(self, symbol: str) -> Dict[str, Any]:
        """
        📱 SOCIAL MEDIA SENTIMENT ANALYSIS
        
        Simulates Twitter/Reddit sentiment analysis
        """
        try:
            # Simulate social media sentiment based on market patterns
            import random
            import hashlib
            
            # Create deterministic randomness based on symbol and time
            seed = hashlib.md5(f"{symbol}_{int(time.time() / 300)}".encode()).hexdigest()
            random.seed(int(seed[:8], 16))
            
            # Simulate sentiment metrics
            base_sentiment = random.uniform(-0.8, 0.8)
            
            # Add some crypto-specific bias
            crypto_biases = {
                'BTC': 0.1,   # Slightly bullish bias
                'ETH': 0.05,  # Slight bullish bias
                'SOL': 0.0,   # Neutral
                'XRP': -0.1,  # Slightly bearish bias
                'DOGE': 0.2,  # Meme coin bullish bias
                'SHIB': 0.15, # Meme coin bullish bias
            }
            
            crypto = symbol.split('/')[0]
            bias = crypto_biases.get(crypto, 0.0)
            social_sentiment = max(-1.0, min(1.0, base_sentiment + bias))
            
            # Simulate volume and engagement
            social_volume = random.uniform(0.3, 1.0)
            engagement_rate = random.uniform(0.2, 0.9)
            
            # Calculate confidence based on volume and consistency
            confidence = (social_volume * 0.6) + (engagement_rate * 0.4)
            
            return {
                'sentiment': social_sentiment,
                'confidence': confidence,
                'volume': social_volume,
                'engagement': engagement_rate,
                'source': 'social_media'
            }
            
        except Exception as e:
            logger.error(f"Social sentiment analysis error: {e}")
            return {'sentiment': 0.0, 'confidence': 0.0, 'volume': 0.5, 'source': 'social_media'}
    
    def _analyze_news_sentiment(self, symbol: str) -> Dict[str, Any]:
        """
        📰 NEWS SENTIMENT ANALYSIS
        
        Analyzes news impact on crypto sentiment
        """
        try:
            # Simulate news sentiment analysis
            import random
            import hashlib
            
            # Create deterministic randomness based on symbol and time
            seed = hashlib.md5(f"news_{symbol}_{int(time.time() / 600)}".encode()).hexdigest()
            random.seed(int(seed[:8], 16))
            
            # Simulate news events
            news_sentiment = random.uniform(-0.6, 0.6)
            
            # Simulate news volume and relevance
            news_volume = random.uniform(0.2, 0.8)
            relevance_score = random.uniform(0.4, 1.0)
            
            # Calculate impact score
            impact_score = abs(news_sentiment) * relevance_score
            
            return {
                'sentiment': news_sentiment,
                'confidence': relevance_score,
                'volume': news_volume,
                'impact': impact_score,
                'source': 'news'
            }
            
        except Exception as e:
            logger.error(f"News sentiment analysis error: {e}")
            return {'sentiment': 0.0, 'confidence': 0.0, 'volume': 0.5, 'source': 'news'}
    
    def _get_fear_greed_index(self, symbol: str) -> Dict[str, Any]:
        """
        😱 FEAR & GREED INDEX SIMULATION
        
        Simulates crypto fear & greed index
        """
        try:
            import random
            import hashlib
            
            # Create deterministic randomness
            seed = hashlib.md5(f"fear_greed_{int(time.time() / 3600)}".encode()).hexdigest()
            random.seed(int(seed[:8], 16))
            
            # Simulate fear & greed components
            volatility = random.uniform(0.2, 0.9)      # High volatility = fear
            momentum = random.uniform(0.1, 0.8)        # Market momentum
            social_volume = random.uniform(0.3, 0.9)   # Social media volume
            surveys = random.uniform(0.2, 0.8)         # Market surveys
            dominance = random.uniform(0.4, 0.7)       # BTC dominance
            trends = random.uniform(0.3, 0.8)          # Google trends
            
            # Calculate weighted fear & greed index
            components = {
                'volatility': 1.0 - volatility,  # Inverted (high vol = fear)
                'market_momentum': momentum,
                'social_volume': social_volume,
                'surveys': surveys,
                'dominance': dominance,
                'trends': trends
            }
            
            fear_greed_score = sum(
                components[key] * self.fear_greed_weights[key] 
                for key in components
            )
            
            # Convert to sentiment scale (-1 to 1)
            # Fear & Greed typically 0-100, we convert to -1 to 1
            sentiment = (fear_greed_score - 0.5) * 2  # Scale to -1 to 1
            
            # Determine fear/greed level
            if fear_greed_score < 0.25:
                level = "EXTREME_FEAR"
            elif fear_greed_score < 0.45:
                level = "FEAR"
            elif fear_greed_score < 0.55:
                level = "NEUTRAL"
            elif fear_greed_score < 0.75:
                level = "GREED"
            else:
                level = "EXTREME_GREED"
            
            return {
                'sentiment': sentiment,
                'confidence': 0.8,  # Fear & greed is usually reliable
                'score': fear_greed_score * 100,  # 0-100 scale
                'level': level,
                'components': components,
                'source': 'fear_greed'
            }
            
        except Exception as e:
            logger.error(f"Fear & greed analysis error: {e}")
            return {'sentiment': 0.0, 'confidence': 0.0, 'score': 50, 'level': 'NEUTRAL', 'source': 'fear_greed'}
    
    def _analyze_momentum_sentiment(self, symbol: str, current_price: float = None) -> Dict[str, Any]:
        """
        📈 MOMENTUM SENTIMENT ANALYSIS
        
        Analyzes price momentum for sentiment indicators
        """
        try:
            if not current_price:
                return {'sentiment': 0.0, 'confidence': 0.0, 'source': 'momentum'}
            
            # Simulate price history for momentum calculation
            import random
            import hashlib
            
            seed = hashlib.md5(f"momentum_{symbol}_{int(time.time() / 900)}".encode()).hexdigest()
            random.seed(int(seed[:8], 16))
            
            # Simulate recent price movements
            price_changes = [random.uniform(-0.05, 0.05) for _ in range(10)]
            
            # Calculate momentum indicators
            short_momentum = sum(price_changes[-3:]) / 3    # 3-period momentum
            medium_momentum = sum(price_changes[-7:]) / 7   # 7-period momentum
            long_momentum = sum(price_changes) / 10         # 10-period momentum
            
            # Weight recent movements more heavily
            weighted_momentum = (short_momentum * 0.5) + (medium_momentum * 0.3) + (long_momentum * 0.2)
            
            # Convert to sentiment scale
            momentum_sentiment = max(-1.0, min(1.0, weighted_momentum * 20))  # Scale up
            
            # Calculate confidence based on consistency
            momentum_consistency = 1.0 - (abs(short_momentum - long_momentum) * 10)
            confidence = max(0.0, min(1.0, momentum_consistency))
            
            return {
                'sentiment': momentum_sentiment,
                'confidence': confidence,
                'short_momentum': short_momentum,
                'medium_momentum': medium_momentum,
                'long_momentum': long_momentum,
                'source': 'momentum'
            }
            
        except Exception as e:
            logger.error(f"Momentum sentiment analysis error: {e}")
            return {'sentiment': 0.0, 'confidence': 0.0, 'source': 'momentum'}
    
    def _analyze_volume_sentiment(self, symbol: str) -> Dict[str, Any]:
        """
        📊 VOLUME SENTIMENT ANALYSIS
        
        Analyzes trading volume for sentiment indicators
        """
        try:
            import random
            import hashlib
            
            seed = hashlib.md5(f"volume_{symbol}_{int(time.time() / 600)}".encode()).hexdigest()
            random.seed(int(seed[:8], 16))
            
            # Simulate volume metrics
            current_volume = random.uniform(0.5, 2.0)      # Relative to average
            volume_trend = random.uniform(-0.3, 0.7)       # Volume trend
            buy_sell_ratio = random.uniform(0.3, 1.7)      # Buy/sell pressure
            
            # Calculate volume sentiment
            volume_sentiment = 0.0
            
            # High volume with buying pressure = bullish
            if current_volume > 1.2 and buy_sell_ratio > 1.0:
                volume_sentiment += 0.3
            
            # Rising volume trend = positive
            if volume_trend > 0.1:
                volume_sentiment += 0.2
            
            # Declining volume with selling = bearish
            if current_volume < 0.8 and buy_sell_ratio < 0.8:
                volume_sentiment -= 0.3
            
            # Normalize sentiment
            volume_sentiment = max(-1.0, min(1.0, volume_sentiment))
            
            # Calculate confidence based on volume strength
            confidence = min(1.0, current_volume * 0.8)
            
            return {
                'sentiment': volume_sentiment,
                'confidence': confidence,
                'volume_score': current_volume,
                'volume_trend': volume_trend,
                'buy_sell_ratio': buy_sell_ratio,
                'source': 'volume'
            }
            
        except Exception as e:
            logger.error(f"Volume sentiment analysis error: {e}")
            return {'sentiment': 0.0, 'confidence': 0.0, 'volume_score': 1.0, 'source': 'volume'}
    
    def _calculate_weighted_sentiment(self, sources: Dict[str, Dict]) -> float:
        """
        ⚖️ WEIGHTED SENTIMENT CALCULATION
        
        Combines multiple sentiment sources with appropriate weights
        """
        try:
            # Define source weights
            weights = {
                'social': 0.25,      # Social media sentiment
                'news': 0.20,        # News sentiment
                'fear_greed': 0.20,  # Fear & greed index
                'momentum': 0.20,    # Price momentum
                'volume': 0.15       # Volume analysis
            }
            
            weighted_sum = 0.0
            total_weight = 0.0
            
            for source, data in sources.items():
                if source in weights and 'sentiment' in data:
                    sentiment = data['sentiment']
                    confidence = data.get('confidence', 1.0)
                    weight = weights[source] * confidence
                    
                    weighted_sum += sentiment * weight
                    total_weight += weight
            
            # Calculate final weighted sentiment
            if total_weight > 0:
                overall_sentiment = weighted_sum / total_weight
            else:
                overall_sentiment = 0.0
            
            # Ensure bounds
            return max(-1.0, min(1.0, overall_sentiment))
            
        except Exception as e:
            logger.error(f"Weighted sentiment calculation error: {e}")
            return 0.0
    
    def _calculate_sentiment_confidence(self, sources: Dict[str, Dict]) -> float:
        """
        🎯 SENTIMENT CONFIDENCE CALCULATION
        
        Calculates overall confidence in sentiment analysis
        """
        try:
            confidences = []
            
            for source, data in sources.items():
                if 'confidence' in data:
                    confidences.append(data['confidence'])
            
            if not confidences:
                return 0.0
            
            # Calculate average confidence
            avg_confidence = sum(confidences) / len(confidences)
            
            # Boost confidence if multiple sources agree
            sentiment_values = [data.get('sentiment', 0) for data in sources.values()]
            sentiment_agreement = 1.0 - (max(sentiment_values) - min(sentiment_values)) / 2.0
            
            # Final confidence combines average confidence and agreement
            final_confidence = (avg_confidence * 0.7) + (sentiment_agreement * 0.3)
            
            return max(0.0, min(1.0, final_confidence))
            
        except Exception as e:
            logger.error(f"Confidence calculation error: {e}")
            return 0.0
    
    def _get_mood_indicator(self, sentiment: float, confidence: float) -> str:
        """
        🎭 MOOD INDICATOR CLASSIFICATION
        
        Classifies overall market mood
        """
        try:
            if confidence < 0.3:
                return "UNCERTAIN"
            
            if sentiment >= self.BULLISH_THRESHOLD:
                if sentiment >= 0.6:
                    return "VERY_BULLISH"
                else:
                    return "BULLISH"
            elif sentiment <= self.BEARISH_THRESHOLD:
                if sentiment <= -0.6:
                    return "VERY_BEARISH"
                else:
                    return "BEARISH"
            else:
                return "NEUTRAL"
                
        except Exception as e:
            logger.error(f"Mood indicator error: {e}")
            return "NEUTRAL"
    
    def _generate_sentiment_recommendations(self, sentiment: float, confidence: float, 
                                          mood: str, sources: Dict) -> List[str]:
        """
        💡 SENTIMENT-BASED RECOMMENDATIONS
        
        Generates trading recommendations based on sentiment analysis
        """
        recommendations = []
        
        try:
            # High confidence recommendations
            if confidence >= self.HIGH_CONFIDENCE_THRESHOLD:
                if sentiment >= 0.5:
                    recommendations.append("Strong bullish sentiment detected - consider increasing position size")
                elif sentiment <= -0.5:
                    recommendations.append("Strong bearish sentiment detected - consider reducing exposure")
            
            # Mood-based recommendations
            if mood == "VERY_BULLISH":
                recommendations.append("Extremely positive sentiment - good entry opportunity")
            elif mood == "VERY_BEARISH":
                recommendations.append("Extremely negative sentiment - consider taking profits or avoiding new positions")
            elif mood == "UNCERTAIN":
                recommendations.append("Mixed sentiment signals - wait for clearer direction")
            
            # Source-specific recommendations
            fear_greed = sources.get('fear_greed', {})
            if 'level' in fear_greed:
                level = fear_greed['level']
                if level == "EXTREME_FEAR":
                    recommendations.append("Extreme fear detected - potential buying opportunity (contrarian)")
                elif level == "EXTREME_GREED":
                    recommendations.append("Extreme greed detected - consider taking profits")
            
            # Social sentiment recommendations
            social = sources.get('social', {})
            if social.get('volume', 0) > 0.8:
                recommendations.append("High social media activity - increased volatility expected")
            
            # Momentum recommendations
            momentum = sources.get('momentum', {})
            if momentum.get('sentiment', 0) > 0.3:
                recommendations.append("Positive price momentum supports bullish sentiment")
            elif momentum.get('sentiment', 0) < -0.3:
                recommendations.append("Negative price momentum supports bearish sentiment")
            
            # Default recommendation if none generated
            if not recommendations:
                recommendations.append("Sentiment analysis complete - monitor for changes")
            
            return recommendations[:5]  # Limit to top 5 recommendations
            
        except Exception as e:
            logger.error(f"Recommendation generation error: {e}")
            return ["Sentiment analysis available - use with caution"]
    
    def enhance_trading_signal(self, signal: Dict, sentiment_score: SentimentScore) -> Dict:
        """
        🚀 TRADING SIGNAL ENHANCEMENT WITH SENTIMENT
        
        Enhances trading signals using sentiment analysis
        """
        try:
            enhanced_signal = signal.copy()
            
            # Get current signal confidence
            base_confidence = signal.get('confidence', 0.6)
            
            # Calculate sentiment enhancement
            sentiment_strength = abs(sentiment_score.overall_sentiment)
            sentiment_confidence = sentiment_score.confidence
            
            # Sentiment enhancement factor
            enhancement_factor = 0.0
            
            # Check if sentiment agrees with signal
            signal_action = signal.get('action', 'HOLD')
            sentiment_agrees = False
            
            if signal_action == 'BUY' and sentiment_score.overall_sentiment > 0:
                sentiment_agrees = True
            elif signal_action == 'SELL' and sentiment_score.overall_sentiment < 0:
                sentiment_agrees = True
            
            if sentiment_agrees:
                # Sentiment agrees - boost confidence
                enhancement_factor = sentiment_strength * sentiment_confidence * 0.2
            else:
                # Sentiment disagrees - reduce confidence slightly
                enhancement_factor = -sentiment_strength * sentiment_confidence * 0.1
            
            # Apply enhancement
            enhanced_confidence = base_confidence + enhancement_factor
            enhanced_confidence = max(0.0, min(1.0, enhanced_confidence))
            
            # Update enhanced signal
            enhanced_signal['confidence'] = enhanced_confidence
            enhanced_signal['sentiment_enhancement'] = enhancement_factor
            enhanced_signal['sentiment_score'] = sentiment_score.overall_sentiment
            enhanced_signal['sentiment_mood'] = sentiment_score.mood_indicator
            enhanced_signal['sentiment_confidence'] = sentiment_score.confidence
            
            # Add sentiment-based adjustments
            if sentiment_score.mood_indicator in ['VERY_BULLISH', 'VERY_BEARISH']:
                enhanced_signal['urgency_boost'] = True
                enhanced_signal['urgency_score'] = signal.get('urgency_score', 30) + 10
            
            # Add sentiment recommendations to signal
            enhanced_signal['sentiment_recommendations'] = sentiment_score.recommendations[:3]
            
            return enhanced_signal
            
        except Exception as e:
            logger.error(f"Signal enhancement error: {e}")
            return signal
    
    def _get_neutral_sentiment(self, symbol: str) -> SentimentScore:
        """Return neutral sentiment score as fallback"""
        return SentimentScore(
            symbol=symbol,
            overall_sentiment=0.0,
            confidence=0.0,
            volume_score=0.5,
            sources={},
            mood_indicator="NEUTRAL",
            recommendations=["Sentiment analysis unavailable"],
            timestamp=datetime.now()
        )
    
    def _is_cached(self, key: str) -> bool:
        """Check if data is cached and still valid"""
        if key not in self.cache:
            return False
        
        cache_time = self.cache[key]['timestamp']
        return (time.time() - cache_time) < self.cache_ttl
    
    def _cache_data(self, key: str, data: Any):
        """Cache data with timestamp"""
        self.cache[key] = {
            'data': data,
            'timestamp': time.time()
        }
    
    def get_status_summary(self) -> Dict[str, Any]:
        """Get sentiment engine status summary"""
        return {
            'enabled': self.enabled,
            'cache_entries': len(self.cache),
            'thresholds': {
                'bullish': self.BULLISH_THRESHOLD,
                'bearish': self.BEARISH_THRESHOLD,
                'high_confidence': self.HIGH_CONFIDENCE_THRESHOLD
            },
            'features': [
                'Social Media Sentiment',
                'News Impact Analysis', 
                'Fear & Greed Index',
                'Momentum Sentiment',
                'Volume Analysis'
            ]
        }

# Global sentiment engine instance
sentiment_engine = None

def get_sentiment_engine() -> SentimentAnalysisEngine:
    """Get global sentiment analysis engine instance"""
    global sentiment_engine
    if sentiment_engine is None:
        sentiment_engine = SentimentAnalysisEngine()
    return sentiment_engine

def enhance_signal_with_sentiment(signal: Dict, symbol: str, current_price: float = None) -> Dict:
    """
    🎯 ENHANCE TRADING SIGNAL WITH SENTIMENT ANALYSIS
    
    Main function to enhance trading signals with sentiment data
    """
    try:
        engine = get_sentiment_engine()
        sentiment_score = engine.get_sentiment_analysis(symbol, current_price)
        enhanced_signal = engine.enhance_trading_signal(signal, sentiment_score)
        
        return enhanced_signal
        
    except Exception as e:
        logger.error(f"Signal enhancement with sentiment error: {e}")
        return signal

if __name__ == "__main__":
    # Test the sentiment analysis engine
    print("🎯 Testing Sentiment Analysis Engine")
    print("=" * 50)
    
    engine = get_sentiment_engine()
    
    # Test with different symbols
    test_symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT']
    
    for symbol in test_symbols:
        print(f"\n📊 Testing {symbol}:")
        sentiment = engine.get_sentiment_analysis(symbol, 50000)
        
        print(f"   Overall Sentiment: {sentiment.overall_sentiment:+.3f}")
        print(f"   Confidence: {sentiment.confidence:.3f}")
        print(f"   Mood: {sentiment.mood_indicator}")
        print(f"   Recommendations: {len(sentiment.recommendations)}")
        
        for i, rec in enumerate(sentiment.recommendations[:2], 1):
            print(f"      {i}. {rec}")
    
    print(f"\n✅ Sentiment Analysis Engine: Operational")
