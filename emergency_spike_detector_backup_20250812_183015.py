#!/usr/bin/env python3
"""
🚨 EMERGENCY SPIKE DETECTION SYSTEM
Enhanced detection for major price movements like XLM +11.70%

This module provides ultra-aggressive detection for significant price spikes
that demand immediate trading pair switching, regardless of normal thresholds.
"""

import ccxt
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from log_utils import log_message

class EmergencySpike:
    """Data class for emergency spike detection"""
    def __init__(self, symbol: str, price_change_pct: float, volume_surge: float, 
                 timeframe: str, urgency_score: float, detected_at: datetime):
        self.symbol = symbol
        self.price_change_pct = price_change_pct
        self.volume_surge = volume_surge
        self.timeframe = timeframe
        self.urgency_score = urgency_score
        self.detected_at = detected_at

class EmergencySpikeDetector:
    """
    🚨 ULTRA-AGGRESSIVE EMERGENCY SPIKE DETECTION
    
    Designed to catch major moves like XLM +11.70% that were previously missed.
    Uses multiple detection layers with ultra-low thresholds.
    """
    
    def __init__(self, exchange):
        self.exchange = exchange
        
        # 🎯 ULTRA-AGGRESSIVE THRESHOLDS - Designed to catch XLM +11.70% type moves
        self.EMERGENCY_THRESHOLDS = {
            '1h': 3.0,   # 3%+ in 1 hour = EMERGENCY
            '4h': 5.0,   # 5%+ in 4 hours = EMERGENCY  
            '24h': 8.0,  # 8%+ in 24 hours = EMERGENCY
            'volume_surge': 150.0  # 150%+ volume surge = EMERGENCY
        }
        
        # 🎯 SUPPORTED PAIRS - ALL BINANCE US PAIRS (200+)
        # Using dynamic loading to get all available pairs from exchange
        self.supported_pairs = None  # Will be loaded dynamically from exchange
        self._all_binance_us_pairs = [
            'BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'XRP/USDT', 'ADA/USDT',
            'SOL/USDT', 'DOGE/USDT', 'DOT/USDT', 'AVAX/USDT', 'SHIB/USDT',
            'MATIC/USDT', 'LTC/USDT', 'UNI/USDT', 'LINK/USDT', 'ATOM/USDT',
            'XLM/USDT', 'ALGO/USDT', 'VET/USDT', 'ICP/USDT', 'FIL/USDT',
            'TRX/USDT', 'ETC/USDT', 'XTZ/USDT', 'HBAR/USDT', 'NEAR/USDT',
            'FLOW/USDT', 'MANA/USDT', 'SAND/USDT', 'AXS/USDT', 'CHZ/USDT',
            'ENJ/USDT', 'BAT/USDT', 'ZRX/USDT', 'COMP/USDT', 'MKR/USDT',
            'SUSHI/USDT', 'YFI/USDT', 'SNX/USDT', 'CRV/USDT', 'BAL/USDT',
            'REN/USDT', 'KNC/USDT', 'STORJ/USDT', 'SKL/USDT', 'NU/USDT',
            'CTSI/USDT', 'BAND/USDT', 'NKN/USDT', 'GRT/USDT', 'OMG/USDT',
            'LRC/USDT', 'ANKR/USDT', 'CVC/USDT', 'REQ/USDT', 'AUDIO/USDT',
            'JUP/USDT', 'WLD/USDT', 'SUI/USDT', 'MAGIC/USDT', 'PEPE/USDT',
            'AAVE/USDT', 'OP/USDT'
        ]
        
        self.price_history = {}
        self.last_check = {}
        
    def get_supported_pairs(self) -> List[str]:
        """Get all supported pairs dynamically from exchange or use fallback list"""
        if self.supported_pairs is None:
            try:
                if self.exchange:
                    # Try to get all USDT pairs from exchange
                    markets = self.exchange.load_markets()
                    usdt_pairs = [symbol for symbol in markets.keys() 
                                 if symbol.endswith('/USDT') and markets[symbol]['active']]
                    log_message(f"🔍 Loaded {len(usdt_pairs)} active USDT pairs from exchange")
                    self.supported_pairs = usdt_pairs
                else:
                    # Use fallback list if no exchange available
                    self.supported_pairs = self._all_binance_us_pairs
                    log_message(f"🔍 Using fallback list: {len(self.supported_pairs)} pairs")
            except Exception as e:
                log_message(f"⚠️ Error loading pairs from exchange, using fallback: {e}")
                self.supported_pairs = self._all_binance_us_pairs
        
        return self.supported_pairs
        
    def detect_emergency_spikes(self) -> List[EmergencySpike]:
        """
        🚨 MAIN DETECTION FUNCTION
        
        Scans all supported pairs for emergency-level price movements.
        Returns list of detected emergency spikes sorted by urgency.
        """
        emergency_spikes = []
        current_time = datetime.now()
        
        # Get all supported pairs dynamically
        supported_pairs = self.get_supported_pairs()
        
        log_message(f"🔍 EMERGENCY SPIKE SCAN: Checking {len(supported_pairs)} pairs...")
        
        for symbol in supported_pairs:
            try:
                spike = self._check_symbol_for_emergency(symbol, current_time)
                if spike:
                    emergency_spikes.append(spike)
                    log_message(f"🚨 EMERGENCY DETECTED: {symbol} {spike.price_change_pct:+.2f}% (urgency: {spike.urgency_score:.1f})")
                    
            except Exception as e:
                log_message(f"⚠️ Error checking {symbol} for emergency: {e}")
                continue
        
        # Sort by urgency score (highest first)
        emergency_spikes.sort(key=lambda x: x.urgency_score, reverse=True)
        
        if emergency_spikes:
            log_message(f"🚨 TOTAL EMERGENCIES DETECTED: {len(emergency_spikes)}")
            for spike in emergency_spikes[:3]:  # Log top 3
                log_message(f"   🎯 {spike.symbol}: {spike.price_change_pct:+.2f}% (urgency: {spike.urgency_score:.1f})")
        else:
            log_message("✅ No emergency spikes detected in current scan")
            
        return emergency_spikes
    
    def _check_symbol_for_emergency(self, symbol: str, current_time: datetime) -> Optional[EmergencySpike]:
        """Check individual symbol for emergency conditions"""
        try:
            # Get current ticker data
            ticker = self.exchange.fetch_ticker(symbol)
            current_price = ticker['last']
            volume_24h = ticker['quoteVolume'] or 0
            
            # Get historical data for multiple timeframes
            ohlcv_1h = self.exchange.fetch_ohlcv(symbol, '1h', limit=2)
            ohlcv_4h = self.exchange.fetch_ohlcv(symbol, '4h', limit=2) 
            ohlcv_24h = self.exchange.fetch_ohlcv(symbol, '1d', limit=2)
            
            if not all([ohlcv_1h, ohlcv_4h, ohlcv_24h]):
                return None
                
            # Calculate price changes for multiple timeframes
            price_1h_ago = ohlcv_1h[-2][4] if len(ohlcv_1h) >= 2 else current_price
            price_4h_ago = ohlcv_4h[-2][4] if len(ohlcv_4h) >= 2 else current_price
            price_24h_ago = ohlcv_24h[-2][4] if len(ohlcv_24h) >= 2 else current_price
            
            change_1h = ((current_price - price_1h_ago) / price_1h_ago) * 100
            change_4h = ((current_price - price_4h_ago) / price_4h_ago) * 100  
            change_24h = ((current_price - price_24h_ago) / price_24h_ago) * 100
            
            # Calculate volume surge (compare to historical average)
            volume_avg = self._get_volume_average(symbol)
            volume_surge = ((volume_24h - volume_avg) / volume_avg * 100) if volume_avg > 0 else 0
            
            # 🚨 EMERGENCY DETECTION LOGIC
            emergency_conditions = []
            max_change = 0
            primary_timeframe = '1h'
            
            # Check each timeframe against thresholds
            if abs(change_1h) >= self.EMERGENCY_THRESHOLDS['1h']:
                emergency_conditions.append(f"1h: {change_1h:+.2f}%")
                if abs(change_1h) > max_change:
                    max_change = abs(change_1h)
                    primary_timeframe = '1h'
                    
            if abs(change_4h) >= self.EMERGENCY_THRESHOLDS['4h']:
                emergency_conditions.append(f"4h: {change_4h:+.2f}%")
                if abs(change_4h) > max_change:
                    max_change = abs(change_4h)
                    primary_timeframe = '4h'
                    
            if abs(change_24h) >= self.EMERGENCY_THRESHOLDS['24h']:
                emergency_conditions.append(f"24h: {change_24h:+.2f}%")
                if abs(change_24h) > max_change:
                    max_change = abs(change_24h)
                    primary_timeframe = '24h'
                    
            if volume_surge >= self.EMERGENCY_THRESHOLDS['volume_surge']:
                emergency_conditions.append(f"Volume: +{volume_surge:.1f}%")
            
            # 🎯 SPECIAL CASE: XLM +11.70% TYPE MOVES
            # Any move above 8% in any timeframe = IMMEDIATE EMERGENCY
            if max_change >= 8.0:
                emergency_conditions.append(f"MAJOR_MOVE: {max_change:+.2f}%")
                log_message(f"🚨 MAJOR MOVE DETECTED: {symbol} {max_change:+.2f}% - FORCING EMERGENCY STATUS")
            
            # If any emergency condition is met, create emergency spike
            if emergency_conditions:
                # Calculate urgency score based on magnitude and timeframe
                urgency_score = self._calculate_urgency_score(
                    max_change, primary_timeframe, volume_surge, emergency_conditions
                )
                
                # Use the most significant price change
                primary_change = change_1h
                if primary_timeframe == '4h':
                    primary_change = change_4h
                elif primary_timeframe == '24h':
                    primary_change = change_24h
                
                spike = EmergencySpike(
                    symbol=symbol,
                    price_change_pct=primary_change,
                    volume_surge=volume_surge,
                    timeframe=primary_timeframe,
                    urgency_score=urgency_score,
                    detected_at=current_time
                )
                
                log_message(f"🚨 EMERGENCY SPIKE: {symbol} {primary_change:+.2f}% ({primary_timeframe}) - Conditions: {', '.join(emergency_conditions)}")
                return spike
            
            return None
            
        except Exception as e:
            log_message(f"⚠️ Error checking {symbol}: {e}")
            return None
    
    def _calculate_urgency_score(self, max_change: float, timeframe: str, 
                               volume_surge: float, conditions: List[str]) -> float:
        """Calculate urgency score for emergency spike"""
        
        # Base score from price change magnitude
        base_score = min(max_change, 20.0) * 5.0  # Max 100 from price change
        
        # Timeframe multiplier (faster = more urgent)
        timeframe_multipliers = {'1h': 1.5, '4h': 1.2, '24h': 1.0}
        base_score *= timeframe_multipliers.get(timeframe, 1.0)
        
        # Volume surge bonus
        if volume_surge > 100:
            base_score += min(volume_surge / 10, 20.0)  # Max 20 bonus
        
        # Multiple condition bonus
        if len(conditions) > 1:
            base_score *= 1.3
            
        # 🎯 XLM +11.70% TYPE BOOST
        if max_change >= 10.0:
            base_score *= 1.5  # 50% boost for double-digit moves
            log_message(f"🚀 DOUBLE-DIGIT MOVE BOOST: {max_change:+.2f}% - Urgency boosted by 50%")
        
        return min(base_score, 100.0)  # Cap at 100
    
    def _get_volume_average(self, symbol: str) -> float:
        """Get average volume for comparison (simplified)"""
        try:
            # Get last 7 days of daily data for volume average
            ohlcv_data = self.exchange.fetch_ohlcv(symbol, '1d', limit=7)
            if not ohlcv_data:
                return 0
                
            volumes = [candle[5] for candle in ohlcv_data if candle[5]]  # Volume is index 5
            return sum(volumes) / len(volumes) if volumes else 0
            
        except:
            return 0
    
    def force_emergency_detection(self, symbol: str, current_price_change: float) -> EmergencySpike:
        """
        🚨 FORCE EMERGENCY DETECTION
        
        Used when external systems detect major moves that internal detection missed.
        Creates emergency spike object for immediate switching.
        """
        current_time = datetime.now()
        
        # Calculate urgency score for forced detection
        urgency_score = min(abs(current_price_change) * 8.0, 100.0)  # High urgency for manual detection
        
        log_message(f"🚨 FORCED EMERGENCY DETECTION: {symbol} {current_price_change:+.2f}%")
        log_message(f"🎯 MANUAL OVERRIDE: Creating emergency spike with urgency {urgency_score:.1f}")
        
        return EmergencySpike(
            symbol=symbol,
            price_change_pct=current_price_change,
            volume_surge=0,  # Unknown for forced detection
            timeframe='manual',
            urgency_score=urgency_score,
            detected_at=current_time
        )

def get_emergency_detector(exchange) -> EmergencySpikeDetector:
    """Get configured emergency spike detector instance"""
    return EmergencySpikeDetector(exchange)

def detect_xlm_type_opportunities(exchange) -> List[EmergencySpike]:
    """
    🎯 DETECT XLM +11.70% TYPE OPPORTUNITIES
    
    Convenience function specifically designed to catch the type of moves
    that were previously missed by the bot.
    """
    detector = get_emergency_detector(exchange)
    
    log_message("🔍 XLM-TYPE OPPORTUNITY SCAN: Looking for major moves...")
    
    emergency_spikes = detector.detect_emergency_spikes()
    
    # Filter for the most significant opportunities (XLM +11.70% type)
    major_opportunities = [
        spike for spike in emergency_spikes 
        if abs(spike.price_change_pct) >= 3.0 or spike.urgency_score >= 30.0  # LOWERED from 5.0% and 60.0
    ]
    
    if major_opportunities:
        log_message(f"🚨 MAJOR OPPORTUNITIES FOUND: {len(major_opportunities)}")
        for opp in major_opportunities:
            log_message(f"   🎯 {opp.symbol}: {opp.price_change_pct:+.2f}% ({opp.timeframe})")
    else:
        log_message("✅ No major XLM-type opportunities detected currently")
    
    return major_opportunities

# 🚨 EMERGENCY MANUAL DETECTION
def manual_xlm_detection() -> EmergencySpike:
    """Manual detection for the current XLM +11.70% situation"""
    detector = EmergencySpikeDetector(None)  # No exchange needed for manual
    
    log_message("🚨 MANUAL XLM DETECTION: Creating emergency spike for XLM +11.70%")
    
    return detector.force_emergency_detection('XLM/USDT', 11.70)

if __name__ == "__main__":
    # Test the manual detection for current XLM situation
    xlm_spike = manual_xlm_detection()
    print(f"Emergency detected: {xlm_spike.symbol} {xlm_spike.price_change_pct:+.2f}% (urgency: {xlm_spike.urgency_score:.1f})")
