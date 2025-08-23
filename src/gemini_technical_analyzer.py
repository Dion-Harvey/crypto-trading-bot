#!/usr/bin/env python3
"""
🚀 GEMINI AI TECHNICAL ANALYSIS ENGINE
Phase 1 LLM Integration for Enhanced Trading Intelligence

Features:
- Real-time chart pattern analysis with Gemini AI
- Support/resistance level identification
- Breakout probability assessment
- Market sentiment analysis
- Technical indicator interpretation
- Risk assessment and trade recommendations

Cost: ~$0.18/month (extremely cost-effective)
"""

import google.generativeai as genai
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import os
from decimal import Decimal

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class GeminiAnalysis:
    """Gemini AI analysis result"""
    symbol: str
    sentiment: str  # BULLISH, BEARISH, NEUTRAL
    confidence: float  # 0.0 to 1.0
    chart_pattern: str
    support_level: float
    resistance_level: float
    breakout_probability: float
    risk_level: str  # LOW, MEDIUM, HIGH
    recommendation: str  # BUY, SELL, HOLD
    reasoning: str
    key_levels: List[float]
    timestamp: datetime

class GeminiTechnicalAnalyzer:
    """
    🚀 GEMINI AI TECHNICAL ANALYSIS ENGINE
    
    Provides AI-powered technical analysis for trading decisions
    Ultra-low cost implementation (~$0.18/month)
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Gemini AI analyzer"""
        self.enabled = False
        self.api_key = api_key or self._load_api_key_from_config() or os.getenv('GEMINI_API_KEY')
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
        self.call_count = 0
        self.daily_limit = 100  # Conservative daily limit
        self.last_reset = datetime.now().date()
        
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                self.enabled = True
                logger.info("✅ Gemini AI Technical Analyzer initialized")
                logger.info("💰 Estimated cost: ~$0.18/month")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Gemini AI: {e}")
                self.enabled = False
        else:
            logger.warning("⚠️ Gemini API key not provided - using simulation mode")
    
    def _load_api_key_from_config(self) -> Optional[str]:
        """Load Gemini API key from enhanced_config.json"""
        try:
            config_path = os.path.join(os.getcwd(), 'enhanced_config.json')
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    api_key = config.get('api_keys', {}).get('gemini_ai', {}).get('api_key', '')
                    if api_key and len(api_key) > 10:
                        return api_key
        except Exception as e:
            logger.debug(f"Could not load API key from config: {e}")
        return None
            
    def _reset_daily_counter(self):
        """Reset daily call counter"""
        current_date = datetime.now().date()
        if current_date != self.last_reset:
            self.call_count = 0
            self.last_reset = current_date
            
    def _can_make_call(self) -> bool:
        """Check if we can make an API call"""
        self._reset_daily_counter()
        return self.call_count < self.daily_limit
        
    def _create_analysis_prompt(self, symbol: str, price_data: Dict, indicators: Dict) -> str:
        """Create comprehensive analysis prompt for Gemini"""
        
        current_price = price_data.get('current_price', 0)
        price_change_24h = price_data.get('price_change_24h', 0)
        volume = price_data.get('volume', 0)
        high_24h = price_data.get('high_24h', current_price)
        low_24h = price_data.get('low_24h', current_price)
        
        prompt = f"""
CRYPTO TECHNICAL ANALYSIS REQUEST

Symbol: {symbol}
Current Price: ${current_price:.4f}
24h Change: {price_change_24h:.2f}%
24h High: ${high_24h:.4f}
24h Low: ${low_24h:.4f}
Volume: {volume:,.0f}

Technical Indicators:
- MA7: ${indicators.get('ma7', 0):.4f}
- MA25: ${indicators.get('ma25', 0):.4f}
- RSI: {indicators.get('rsi', 50):.1f}
- MACD: {indicators.get('macd', 0):.4f}
- MACD Signal: {indicators.get('macd_signal', 0):.4f}
- Bollinger Upper: ${indicators.get('bb_upper', 0):.4f}
- Bollinger Lower: ${indicators.get('bb_lower', 0):.4f}
- Volume MA: {indicators.get('volume_ma', 0):,.0f}

Please provide technical analysis in this EXACT JSON format:
{{
    "sentiment": "BULLISH/BEARISH/NEUTRAL",
    "confidence": 0.75,
    "chart_pattern": "Golden Cross/Death Cross/Ascending Triangle/etc",
    "support_level": 1.234,
    "resistance_level": 1.456,
    "breakout_probability": 0.65,
    "risk_level": "LOW/MEDIUM/HIGH",
    "recommendation": "BUY/SELL/HOLD",
    "reasoning": "Brief explanation of analysis",
    "key_levels": [1.200, 1.300, 1.400]
}}

Focus on:
1. MA7/MA25 crossover signals (primary strategy)
2. RSI overbought/oversold conditions
3. Volume confirmation
4. Support/resistance levels
5. Risk assessment for position sizing
"""
        return prompt
        
    def analyze_technical_patterns(self, symbol: str, price_data: Dict, indicators: Dict) -> Optional[GeminiAnalysis]:
        """
        Analyze technical patterns using Gemini AI
        
        Args:
            symbol: Trading symbol (e.g., 'BTC/USDT')
            price_data: Current price information
            indicators: Technical indicators
            
        Returns:
            GeminiAnalysis object or None if analysis fails
        """
        
        # Check cache first
        cache_key = f"{symbol}_{int(time.time() // self.cache_ttl)}"
        if cache_key in self.cache:
            logger.debug(f"📋 Using cached analysis for {symbol}")
            return self.cache[cache_key]
            
        # Check if we can make API call
        if not self._can_make_call():
            logger.warning(f"⚠️ Daily API limit reached ({self.daily_limit}), using fallback")
            return self._fallback_analysis(symbol, price_data, indicators)
            
        if not self.enabled:
            return self._fallback_analysis(symbol, price_data, indicators)
            
        try:
            # Create analysis prompt
            prompt = self._create_analysis_prompt(symbol, price_data, indicators)
            
            # Make Gemini API call
            logger.debug(f"🤖 Requesting Gemini analysis for {symbol}")
            response = self.model.generate_content(prompt)
            self.call_count += 1
            
            # Parse JSON response
            response_text = response.text.strip()
            
            # Extract JSON from response (in case there's extra text)
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_text = response_text[json_start:json_end]
                analysis_data = json.loads(json_text)
                
                # Create analysis object
                analysis = GeminiAnalysis(
                    symbol=symbol,
                    sentiment=analysis_data.get('sentiment', 'NEUTRAL'),
                    confidence=float(analysis_data.get('confidence', 0.5)),
                    chart_pattern=analysis_data.get('chart_pattern', 'Unknown'),
                    support_level=float(analysis_data.get('support_level', price_data.get('low_24h', 0))),
                    resistance_level=float(analysis_data.get('resistance_level', price_data.get('high_24h', 0))),
                    breakout_probability=float(analysis_data.get('breakout_probability', 0.5)),
                    risk_level=analysis_data.get('risk_level', 'MEDIUM'),
                    recommendation=analysis_data.get('recommendation', 'HOLD'),
                    reasoning=analysis_data.get('reasoning', 'AI analysis completed'),
                    key_levels=analysis_data.get('key_levels', []),
                    timestamp=datetime.now()
                )
                
                # Cache the result
                self.cache[cache_key] = analysis
                
                logger.info(f"✅ Gemini analysis for {symbol}: {analysis.sentiment} ({analysis.confidence:.1%} confidence)")
                logger.info(f"📊 Pattern: {analysis.chart_pattern}, Recommendation: {analysis.recommendation}")
                
                return analysis
                
            else:
                logger.error(f"❌ Invalid JSON response from Gemini for {symbol}")
                return self._fallback_analysis(symbol, price_data, indicators)
                
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON parsing error for {symbol}: {e}")
            return self._fallback_analysis(symbol, price_data, indicators)
            
        except Exception as e:
            logger.error(f"❌ Gemini API error for {symbol}: {e}")
            return self._fallback_analysis(symbol, price_data, indicators)
            
    def _fallback_analysis(self, symbol: str, price_data: Dict, indicators: Dict) -> GeminiAnalysis:
        """Provide fallback technical analysis when Gemini is unavailable"""
        
        current_price = price_data.get('current_price', 0)
        ma7 = indicators.get('ma7', current_price)
        ma25 = indicators.get('ma25', current_price)
        rsi = indicators.get('rsi', 50)
        
        # Simple technical analysis
        if ma7 > ma25 and rsi < 70:
            sentiment = "BULLISH"
            recommendation = "BUY"
            confidence = 0.6
        elif ma7 < ma25 and rsi > 30:
            sentiment = "BEARISH"
            recommendation = "SELL"
            confidence = 0.6
        else:
            sentiment = "NEUTRAL"
            recommendation = "HOLD"
            confidence = 0.4
            
        # Determine risk level
        if rsi > 80 or rsi < 20:
            risk_level = "HIGH"
        elif rsi > 70 or rsi < 30:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
            
        return GeminiAnalysis(
            symbol=symbol,
            sentiment=sentiment,
            confidence=confidence,
            chart_pattern="Standard MA Analysis",
            support_level=price_data.get('low_24h', current_price * 0.95),
            resistance_level=price_data.get('high_24h', current_price * 1.05),
            breakout_probability=0.5,
            risk_level=risk_level,
            recommendation=recommendation,
            reasoning=f"Fallback analysis: MA7 {'>' if ma7 > ma25 else '<'} MA25, RSI {rsi:.1f}",
            key_levels=[current_price * 0.95, current_price, current_price * 1.05],
            timestamp=datetime.now()
        )
        
    def get_enhanced_signals(self, symbol: str, price_data: Dict, indicators: Dict, 
                           traditional_signals: Dict) -> Dict:
        """
        Enhance traditional trading signals with Gemini AI analysis
        
        Args:
            symbol: Trading symbol
            price_data: Current price data
            indicators: Technical indicators
            traditional_signals: Existing signal analysis
            
        Returns:
            Enhanced signal dictionary
        """
        
        # Get Gemini analysis
        gemini_analysis = self.analyze_technical_patterns(symbol, price_data, indicators)
        
        if not gemini_analysis:
            return traditional_signals
            
        # Enhance traditional signals with AI insights
        enhanced_signals = traditional_signals.copy()
        
        # Add Gemini insights
        enhanced_signals.update({
            'gemini_sentiment': gemini_analysis.sentiment,
            'gemini_confidence': gemini_analysis.confidence,
            'gemini_recommendation': gemini_analysis.recommendation,
            'chart_pattern': gemini_analysis.chart_pattern,
            'ai_support_level': gemini_analysis.support_level,
            'ai_resistance_level': gemini_analysis.resistance_level,
            'breakout_probability': gemini_analysis.breakout_probability,
            'ai_risk_level': gemini_analysis.risk_level,
            'ai_reasoning': gemini_analysis.reasoning,
            'ai_enhanced': True
        })
        
        # Adjust signal strength based on AI confidence
        if 'signal_strength' in enhanced_signals:
            ai_multiplier = 0.5 + (gemini_analysis.confidence * 0.5)  # 0.5 to 1.0
            enhanced_signals['signal_strength'] *= ai_multiplier
            
        # Add pattern-based signal enhancement
        if gemini_analysis.chart_pattern in ['Golden Cross', 'Bullish Breakout', 'Ascending Triangle']:
            enhanced_signals['pattern_boost'] = 0.2
        elif gemini_analysis.chart_pattern in ['Death Cross', 'Bearish Breakdown', 'Descending Triangle']:
            enhanced_signals['pattern_boost'] = -0.2
        else:
            enhanced_signals['pattern_boost'] = 0.0
            
        logger.debug(f"🚀 Enhanced signals for {symbol} with Gemini AI")
        
        return enhanced_signals
        
    def get_daily_usage_stats(self) -> Dict:
        """Get daily usage statistics"""
        self._reset_daily_counter()
        
        estimated_cost = (self.call_count * 800) * 0.00000015  # ~800 tokens per call
        
        return {
            'calls_made': self.call_count,
            'daily_limit': self.daily_limit,
            'remaining_calls': max(0, self.daily_limit - self.call_count),
            'estimated_daily_cost': estimated_cost,
            'estimated_monthly_cost': estimated_cost * 30,
            'enabled': self.enabled,
            'api_key_configured': bool(self.api_key)
        }
        
    def is_enabled(self) -> bool:
        """Check if Gemini analyzer is enabled and functional"""
        return self.enabled and bool(self.api_key)

# Global instance
gemini_analyzer = None

def get_gemini_analyzer() -> GeminiTechnicalAnalyzer:
    """Get global Gemini analyzer instance"""
    global gemini_analyzer
    if gemini_analyzer is None:
        gemini_analyzer = GeminiTechnicalAnalyzer()
    return gemini_analyzer

def initialize_gemini_api(api_key: str) -> bool:
    """
    Initialize Gemini API with provided key
    
    Args:
        api_key: Gemini API key
        
    Returns:
        True if successful, False otherwise
    """
    global gemini_analyzer
    try:
        gemini_analyzer = GeminiTechnicalAnalyzer(api_key=api_key)
        return gemini_analyzer.is_enabled()
    except Exception as e:
        logger.error(f"❌ Failed to initialize Gemini API: {e}")
        return False

if __name__ == "__main__":
    # Test the Gemini analyzer
    analyzer = GeminiTechnicalAnalyzer()
    
    # Sample data for testing
    test_price_data = {
        'current_price': 43250.00,
        'price_change_24h': 2.35,
        'high_24h': 43500.00,
        'low_24h': 42100.00,
        'volume': 1500000000
    }
    
    test_indicators = {
        'ma7': 42800.00,
        'ma25': 41500.00,
        'rsi': 65.2,
        'macd': 125.50,
        'macd_signal': 98.30,
        'bb_upper': 44000.00,
        'bb_lower': 41000.00,
        'volume_ma': 1200000000
    }
    
    # Test analysis
    result = analyzer.analyze_technical_patterns('BTC/USDT', test_price_data, test_indicators)
    if result:
        print(f"✅ Analysis Result: {result.sentiment} - {result.recommendation}")
        print(f"📊 Pattern: {result.chart_pattern}")
        print(f"🎯 Confidence: {result.confidence:.1%}")
        print(f"💡 Reasoning: {result.reasoning}")
    
    # Usage stats
    stats = analyzer.get_daily_usage_stats()
    print(f"📈 Daily Usage: {stats['calls_made']}/{stats['daily_limit']}")
    print(f"💰 Estimated Cost: ${stats['estimated_monthly_cost']:.4f}/month")
