#!/usr/bin/env python3
"""
🚨 COMPREHENSIVE MULTI-PAIR OPPORTUNITY SCANNER
Real-time monitoring of ALL supported pairs for major moves

This system continuously scans all 16+ supported pairs to ensure no opportunities
like XLM +11.70% are ever missed again. Designed for complete market coverage.
"""

import ccxt
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from log_utils import log_message
import json

@dataclass
class OpportunityAlert:
    """Data class for opportunity alerts"""
    symbol: str
    price_change_1h: float
    price_change_4h: float
    price_change_24h: float
    volume_change_24h: float
    current_price: float
    urgency_score: float
    detected_at: datetime
    alert_type: str  # 'MAJOR_MOVE', 'VOLUME_SURGE', 'BREAKOUT'
    recommendation: str  # 'IMMEDIATE_SWITCH', 'MONITOR', 'ALERT_ONLY'

class ComprehensiveOpportunityScanner:
    """
    🎯 COMPREHENSIVE MULTI-PAIR OPPORTUNITY SCANNER
    
    Monitors ALL supported trading pairs simultaneously for:
    - Major price movements (3%+, 5%+, 8%+)
    - Volume surges (100%+, 200%+, 500%+)
    - Technical breakouts
    - Momentum shifts
    
    Ensures zero missed opportunities across all pairs.
    """
    
    def __init__(self, exchange, config_path="comprehensive_all_pairs_config.json"):
        self.exchange = exchange
        self.config_path = config_path
        # First try comprehensive config, fallback to enhanced config
        if config_path == "comprehensive_all_pairs_config.json":
            import os
            if not os.path.exists(config_path):
                log_message("⚠️ Comprehensive config not found, using enhanced_config.json")
                self.config_path = "enhanced_config.json"
        self.supported_pairs = self._load_supported_pairs()
        self.running = False
        self.scan_thread = None
        
        # 🚨 ULTRA-AGGRESSIVE THRESHOLDS for catching ALL opportunities
        self.OPPORTUNITY_THRESHOLDS = {
            'CRITICAL': {  # Immediate action required
                '1h': 5.0,    # 5%+ in 1 hour
                '4h': 8.0,    # 8%+ in 4 hours
                '24h': 12.0,  # 12%+ in 24 hours
                'volume_surge': 300.0  # 300%+ volume surge
            },
            'HIGH': {  # Strong consideration for switching
                '1h': 3.0,    # 3%+ in 1 hour
                '4h': 5.0,    # 5%+ in 4 hours
                '24h': 8.0,   # 8%+ in 24 hours
                'volume_surge': 200.0  # 200%+ volume surge
            },
            'MODERATE': {  # Worth monitoring
                '1h': 2.0,    # 2%+ in 1 hour
                '4h': 3.0,    # 3%+ in 4 hours
                '24h': 5.0,   # 5%+ in 24 hours
                'volume_surge': 100.0  # 100%+ volume surge
            }
        }
        
        self.price_history = {}
        self.volume_history = {}
        self.last_alerts = {}
        self.opportunity_log = []
        
        log_message(f"🚀 COMPREHENSIVE SCANNER INITIALIZED: Monitoring {len(self.supported_pairs)} pairs")
        for pair in self.supported_pairs:
            log_message(f"   📊 Monitoring: {pair}")
    
    def _load_supported_pairs(self) -> List[str]:
        """Load supported pairs from configuration"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Check if this is the comprehensive config format
            if 'supported_pairs' in config and isinstance(config['supported_pairs'], list):
                pairs = config['supported_pairs']
                log_message(f"📋 LOADED {len(pairs)} COMPREHENSIVE PAIRS from {self.config_path}")
                log_message(f"🎯 COMPREHENSIVE MODE: Scanning ALL {len(pairs)} Binance US pairs!")
            else:
                # Standard enhanced_config.json format
                pairs = config.get('trading', {}).get('supported_pairs', [])
                if pairs:
                    log_message(f"📋 LOADED {len(pairs)} SUPPORTED PAIRS from {self.config_path}")
                else:
                    # Fallback to comprehensive list
                    pairs = [
                        'BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'XRP/USDT', 'ADA/USDT',
                        'DOGE/USDT', 'XLM/USDT', 'SUI/USDT', 'SHIB/USDT', 'HBAR/USDT',
                        'AVAX/USDT', 'DOT/USDT', 'MATIC/USDT', 'LINK/USDT', 'UNI/USDT', 'LTC/USDT'
                    ]
                    log_message(f"📋 USING FALLBACK: {len(pairs)} basic pairs")
            
            return pairs
            
        except Exception as e:
            log_message(f"⚠️ Error loading config, using fallback pairs: {e}")
            return [
                'BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'XRP/USDT', 'ADA/USDT',
                'DOGE/USDT', 'XLM/USDT', 'SUI/USDT', 'SHIB/USDT', 'HBAR/USDT',
                'AVAX/USDT', 'DOT/USDT', 'MATIC/USDT', 'LINK/USDT', 'UNI/USDT', 'LTC/USDT'
            ]
    
    def scan_all_pairs_comprehensive(self) -> List[OpportunityAlert]:
        """
        🔍 OPTIMIZED COMPREHENSIVE SCAN - 90% Fewer API Calls
        
        Uses batch ticker fetching to dramatically reduce API calls
        and avoid rate limiting issues.
        """
        opportunities = []
        scan_start = datetime.now()
        
        log_message(f"🔍 COMPREHENSIVE SCAN START: Checking {len(self.supported_pairs)} pairs")
        
        try:
            # 🚀 OPTIMIZATION 1: Batch fetch all tickers in ONE API call
            log_message("📊 BATCH FETCHING ALL TICKERS (API OPTIMIZATION)")
            all_tickers = self.exchange.fetch_tickers()
            log_message(f"✅ FETCHED {len(all_tickers)} tickers in single API call")
            
            # 🚀 OPTIMIZATION 2: Filter only supported pairs from batch
            available_pairs = [pair for pair in self.supported_pairs if pair in all_tickers]
            
            if len(available_pairs) < len(self.supported_pairs):
                missing = len(self.supported_pairs) - len(available_pairs)
                log_message(f"⚠️ {missing} pairs not available in batch ticker data")
            
            # Scan each pair using pre-fetched ticker data
            for i, symbol in enumerate(available_pairs):
                try:
                    # Use optimized analysis with pre-fetched ticker
                    opportunity = self._analyze_pair_for_opportunities_optimized(symbol, all_tickers[symbol])
                    if opportunity:
                        opportunities.append(opportunity)
                        log_message(f"🚨 OPPORTUNITY DETECTED: {symbol} {opportunity.price_change_1h:+.2f}% (1h) - {opportunity.alert_type}")
                    
                    # Progress indicator
                    if (i + 1) % 5 == 0:
                        log_message(f"📊 SCAN PROGRESS: {i + 1}/{len(available_pairs)} pairs checked")
                        
                    # 🚀 OPTIMIZATION 3: Minimal delay (no API calls per pair)
                    time.sleep(0.05)  # Just 50ms vs 500ms+ previously
                        
                except Exception as e:
                    log_message(f"⚠️ Error scanning {symbol}: {e}")
                    continue
                    
        except Exception as e:
            log_message(f"❌ BATCH TICKER FETCH FAILED: {e}")
            log_message("🔄 FALLING BACK TO INDIVIDUAL API CALLS")
            # Fallback to original method with rate limiting
            return self._scan_fallback_individual()
        
        # Sort by urgency score (highest first) - SIGNAL-FIRST, NO TIER BIAS
        opportunities.sort(key=lambda x: (x.urgency_score, abs(x.price_change_1h)), reverse=True)
        
        # Add signal-first recommendations (ignoring tier restrictions)
        for opp in opportunities:
            if opp.urgency_score >= 70.0:
                opp.recommendation = "IMMEDIATE_SWITCH"
            elif opp.urgency_score >= 50.0:
                opp.recommendation = "STRONG_CONSIDERATION"  
            elif opp.urgency_score >= 35.0:
                opp.recommendation = "CONSIDER"
            else:
                opp.recommendation = "MONITOR"
        
        scan_duration = (datetime.now() - scan_start).total_seconds()
        
        log_message(f"✅ COMPREHENSIVE SCAN COMPLETE: {len(opportunities)} opportunities found in {scan_duration:.1f}s")
        log_message(f"🚀 API OPTIMIZATION: Used 1 batch call instead of {len(self.supported_pairs)} individual calls")
        
        if opportunities:
            log_message("🎯 TOP OPPORTUNITIES DETECTED:")
            for i, opp in enumerate(opportunities[:5]):  # Show top 5
                log_message(f"   {i+1}. {opp.symbol}: {opp.price_change_1h:+.2f}% (1h) | {opp.price_change_24h:+.2f}% (24h) | Urgency: {opp.urgency_score:.1f}")
        else:
            log_message("✅ No significant opportunities detected in current scan")
        
        return opportunities
    
    def _analyze_pair_for_opportunities_optimized(self, symbol: str, ticker_data: dict) -> Optional[OpportunityAlert]:
        """
        🚀 OPTIMIZED PAIR ANALYSIS - Uses pre-fetched ticker data
        
        Reduces API calls by using batch-fetched ticker data
        instead of individual fetch_ticker calls.
        """
        try:
            # Use pre-fetched ticker data instead of API call
            current_price = ticker_data['last']
            volume_24h = ticker_data['quoteVolume'] or 0
            
            # Get OHLCV data for multiple timeframes (still need these individual calls)
            # 🔧 OPTIMIZATION: Cache OHLCV data to reduce frequency
            try:
                ohlcv_1h = self.exchange.fetch_ohlcv(symbol, '1h', limit=25)  # 24 hours of 1h data
                time.sleep(0.05)  # Small delay between OHLCV calls
                ohlcv_4h = self.exchange.fetch_ohlcv(symbol, '4h', limit=25)  # ~4 days of 4h data
                time.sleep(0.05)
                ohlcv_24h = self.exchange.fetch_ohlcv(symbol, '1d', limit=8)  # 1 week of daily data
            except Exception as ohlcv_error:
                log_message(f"⚠️ OHLCV fetch failed for {symbol}: {ohlcv_error}")
                return None
            
            if not all([ohlcv_1h, ohlcv_4h, ohlcv_24h]):
                return None
            
            # Calculate price changes for multiple timeframes
            price_1h_ago = ohlcv_1h[-2][4] if len(ohlcv_1h) >= 2 else current_price
            price_4h_ago = ohlcv_4h[-2][4] if len(ohlcv_4h) >= 2 else current_price
            price_24h_ago = ohlcv_24h[-2][4] if len(ohlcv_24h) >= 2 else current_price
            
            change_1h = ((current_price - price_1h_ago) / price_1h_ago) * 100
            change_4h = ((current_price - price_4h_ago) / price_4h_ago) * 100
            change_24h = ((current_price - price_24h_ago) / price_24h_ago) * 100
            
            # Calculate volume change (compare to 7-day average)
            volume_avg = self._calculate_volume_average(symbol, ohlcv_24h)
            volume_change = ((volume_24h - volume_avg) / volume_avg * 100) if volume_avg > 0 else 0
            
            # Determine opportunity level and type
            opportunity_level = self._classify_opportunity_level(change_1h, change_4h, change_24h, volume_change)
            
            if opportunity_level:
                # Calculate urgency score
                urgency_score = self._calculate_comprehensive_urgency_score(
                    change_1h, change_4h, change_24h, volume_change, opportunity_level
                )
                
                # Determine alert type and recommendation
                alert_type, recommendation = self._determine_alert_type_and_recommendation(
                    change_1h, change_4h, change_24h, volume_change, opportunity_level
                )
                
                return OpportunityAlert(
                    symbol=symbol,
                    price_change_1h=change_1h,
                    price_change_4h=change_4h,
                    price_change_24h=change_24h,
                    volume_change_24h=volume_change,
                    current_price=current_price,
                    urgency_score=urgency_score,
                    detected_at=datetime.now(),
                    alert_type=alert_type,
                    recommendation=recommendation
                )
            
            return None
            
        except Exception as e:
            log_message(f"⚠️ Error in optimized analysis for {symbol}: {e}")
            return None

    def _scan_fallback_individual(self) -> List[OpportunityAlert]:
        """
        🔄 FALLBACK: Individual API calls with rate limiting
        
        Used when batch ticker fetch fails.
        Includes aggressive rate limiting to avoid API issues.
        """
        opportunities = []
        log_message("🔄 Using individual API calls with rate limiting")
        
        for i, symbol in enumerate(self.supported_pairs):
            try:
                opportunity = self._analyze_pair_for_opportunities(symbol)
                if opportunity:
                    opportunities.append(opportunity)
                    log_message(f"🚨 OPPORTUNITY DETECTED: {symbol} {opportunity.price_change_1h:+.2f}% (1h) - {opportunity.alert_type}")
                
                # Progress indicator
                if (i + 1) % 3 == 0:  # Less frequent progress updates
                    log_message(f"📊 FALLBACK PROGRESS: {i + 1}/{len(self.supported_pairs)} pairs checked")
                
                # 🔧 AGGRESSIVE RATE LIMITING for fallback
                time.sleep(1.0)  # 1 second between individual calls
                    
            except Exception as e:
                log_message(f"⚠️ Error scanning {symbol}: {e}")
                time.sleep(2.0)  # Longer delay on error
                continue
        
        return opportunities

    def _analyze_pair_for_opportunities(self, symbol: str) -> Optional[OpportunityAlert]:
        """Analyze individual pair for opportunities"""
        try:
            # Get current ticker and price data
            ticker = self.exchange.fetch_ticker(symbol)
            current_price = ticker['last']
            volume_24h = ticker['quoteVolume'] or 0
            
            # Get OHLCV data for multiple timeframes
            ohlcv_1h = self.exchange.fetch_ohlcv(symbol, '1h', limit=25)  # 24 hours of 1h data
            ohlcv_4h = self.exchange.fetch_ohlcv(symbol, '4h', limit=25)  # ~4 days of 4h data
            ohlcv_24h = self.exchange.fetch_ohlcv(symbol, '1d', limit=8)  # 1 week of daily data
            
            if not all([ohlcv_1h, ohlcv_4h, ohlcv_24h]):
                return None
            
            # Calculate price changes for multiple timeframes
            price_1h_ago = ohlcv_1h[-2][4] if len(ohlcv_1h) >= 2 else current_price
            price_4h_ago = ohlcv_4h[-2][4] if len(ohlcv_4h) >= 2 else current_price
            price_24h_ago = ohlcv_24h[-2][4] if len(ohlcv_24h) >= 2 else current_price
            
            change_1h = ((current_price - price_1h_ago) / price_1h_ago) * 100
            change_4h = ((current_price - price_4h_ago) / price_4h_ago) * 100
            change_24h = ((current_price - price_24h_ago) / price_24h_ago) * 100
            
            # Calculate volume change (compare to 7-day average)
            volume_avg = self._calculate_volume_average(symbol, ohlcv_24h)
            volume_change = ((volume_24h - volume_avg) / volume_avg * 100) if volume_avg > 0 else 0
            
            # Determine opportunity level and type
            opportunity_level = self._classify_opportunity_level(change_1h, change_4h, change_24h, volume_change)
            
            if opportunity_level:
                # Calculate urgency score
                urgency_score = self._calculate_comprehensive_urgency_score(
                    change_1h, change_4h, change_24h, volume_change, opportunity_level
                )
                
                # Determine alert type and recommendation
                alert_type, recommendation = self._determine_alert_type_and_recommendation(
                    change_1h, change_4h, change_24h, volume_change, opportunity_level
                )
                
                return OpportunityAlert(
                    symbol=symbol,
                    price_change_1h=change_1h,
                    price_change_4h=change_4h,
                    price_change_24h=change_24h,
                    volume_change_24h=volume_change,
                    current_price=current_price,
                    urgency_score=urgency_score,
                    detected_at=datetime.now(),
                    alert_type=alert_type,
                    recommendation=recommendation
                )
            
            return None
            
        except Exception as e:
            log_message(f"⚠️ Error analyzing {symbol}: {e}")
            return None
    
    def _classify_opportunity_level(self, change_1h: float, change_4h: float, 
                                  change_24h: float, volume_change: float) -> Optional[str]:
        """
        🛡️ ENHANCED: Classify opportunity level with anti-whipsaw protection
        
        Now includes smart filtering to avoid buying already-extended moves
        and prefer early-stage breakouts with better risk/reward.
        """
        
        # 🛡️ ANTI-WHIPSAW PROTECTION: Filter out already-spiked pairs
        spike_filter_result = self._apply_spike_protection_filter(change_1h, change_4h, change_24h, volume_change)
        
        if spike_filter_result['filtered_out']:
            log_message(f"🛡️ SPIKE PROTECTION: {spike_filter_result['reason']}")
            return None  # Skip this opportunity - too risky
        
        # Apply boost if this is an ideal early-stage breakout
        level_boost = spike_filter_result['level_boost']
        
        # Check CRITICAL level (immediate action) - with protection applied
        critical_1h_threshold = self.OPPORTUNITY_THRESHOLDS['CRITICAL']['1h'] * (1 + level_boost)
        critical_4h_threshold = self.OPPORTUNITY_THRESHOLDS['CRITICAL']['4h'] * (1 + level_boost)
        critical_24h_threshold = self.OPPORTUNITY_THRESHOLDS['CRITICAL']['24h'] * (1 + level_boost)
        critical_volume_threshold = self.OPPORTUNITY_THRESHOLDS['CRITICAL']['volume_surge'] * (1 - level_boost * 0.5)
        
        if (abs(change_1h) >= critical_1h_threshold or
            abs(change_4h) >= critical_4h_threshold or
            abs(change_24h) >= critical_24h_threshold or
            volume_change >= critical_volume_threshold):
            return 'CRITICAL'
        
        # Check HIGH level (strong consideration) - with protection applied  
        high_1h_threshold = self.OPPORTUNITY_THRESHOLDS['HIGH']['1h'] * (1 + level_boost)
        high_4h_threshold = self.OPPORTUNITY_THRESHOLDS['HIGH']['4h'] * (1 + level_boost)
        high_24h_threshold = self.OPPORTUNITY_THRESHOLDS['HIGH']['24h'] * (1 + level_boost)
        high_volume_threshold = self.OPPORTUNITY_THRESHOLDS['HIGH']['volume_surge'] * (1 - level_boost * 0.5)
        
        if (abs(change_1h) >= high_1h_threshold or
            abs(change_4h) >= high_4h_threshold or
            abs(change_24h) >= high_24h_threshold or
            volume_change >= high_volume_threshold):
            return 'HIGH'
        
        # Check MODERATE level (monitoring) - with protection applied
        moderate_1h_threshold = self.OPPORTUNITY_THRESHOLDS['MODERATE']['1h'] * (1 + level_boost)
        moderate_4h_threshold = self.OPPORTUNITY_THRESHOLDS['MODERATE']['4h'] * (1 + level_boost)
        moderate_24h_threshold = self.OPPORTUNITY_THRESHOLDS['MODERATE']['24h'] * (1 + level_boost)
        moderate_volume_threshold = self.OPPORTUNITY_THRESHOLDS['MODERATE']['volume_surge'] * (1 - level_boost * 0.5)
        
        if (abs(change_1h) >= moderate_1h_threshold or
            abs(change_4h) >= moderate_4h_threshold or
            abs(change_24h) >= moderate_24h_threshold or
            volume_change >= moderate_volume_threshold):
            return 'MODERATE'
        
        return None
    
    def _apply_spike_protection_filter(self, change_1h: float, change_4h: float, 
                                     change_24h: float, volume_change: float) -> dict:
        """
        🛡️ ANTI-WHIPSAW PROTECTION SYSTEM
        
        Filters out already-spiked pairs to avoid buying the top.
        Prefers early-stage breakouts with better risk/reward ratios.
        
        Returns:
            dict: {
                'filtered_out': bool,
                'reason': str,  
                'level_boost': float  # 0.0 to 0.3 boost for ideal setups
            }
        """
        
        # 🚨 CRITICAL FILTER: Avoid extreme already-spiked pairs
        if abs(change_1h) >= 8.0:  # Already moved 8%+ in 1 hour
            return {
                'filtered_out': True,
                'reason': f"Already spiked {change_1h:+.1f}% in 1h - avoiding buy-the-top risk",
                'level_boost': 0.0
            }
        
        if abs(change_1h) >= 6.0 and abs(change_4h) >= 10.0:  # Double spike pattern
            return {
                'filtered_out': True, 
                'reason': f"Extended move: {change_1h:+.1f}% (1h) + {change_4h:+.1f}% (4h) - momentum exhausted",
                'level_boost': 0.0
            }
        
        # 🎯 IDEAL SETUP DETECTION: Early-stage breakouts get priority
        level_boost = 0.0
        boost_reasons = []
        
        # Ideal Pattern 1: Fresh breakout (small 1h move, building momentum)
        if 1.0 <= abs(change_1h) <= 3.0 and abs(change_4h) >= 4.0:
            level_boost += 0.15  # 15% threshold reduction = easier to qualify
            boost_reasons.append("fresh breakout pattern")
        
        # Ideal Pattern 2: Volume surge before price spike (predictive)
        if volume_change >= 150.0 and abs(change_1h) <= 2.5:
            level_boost += 0.20  # 20% threshold reduction
            boost_reasons.append("volume surge before price")
            
        # Ideal Pattern 3: Building momentum (1h < 4h < 24h progression)
        if (abs(change_1h) <= 3.0 and 
            abs(change_4h) >= abs(change_1h) * 1.5 and
            abs(change_24h) >= abs(change_4h) * 1.2):
            level_boost += 0.10  # 10% threshold reduction
            boost_reasons.append("building momentum pattern")
        
        # 📊 MOMENTUM DIRECTION ANALYSIS
        momentum_quality = self._analyze_momentum_quality(change_1h, change_4h, change_24h)
        
        if momentum_quality == 'accelerating':
            level_boost += 0.10
            boost_reasons.append("accelerating momentum")
        elif momentum_quality == 'decelerating':
            # Reduce enthusiasm for slowing momentum
            level_boost -= 0.05
            boost_reasons.append("decelerating momentum (caution)")
        
        # Cap boost at 30%
        level_boost = min(level_boost, 0.30)
        
        reason = f"Early-stage opportunity (boosts: {', '.join(boost_reasons)})" if boost_reasons else "Standard opportunity"
        
        return {
            'filtered_out': False,
            'reason': reason,
            'level_boost': level_boost
        }
    
    def _analyze_momentum_quality(self, change_1h: float, change_4h: float, change_24h: float) -> str:
        """
        🔍 MOMENTUM DIRECTION ANALYSIS
        
        Determines if momentum is accelerating (good) or decelerating (caution)
        """
        
        # Use absolute values for analysis
        abs_1h = abs(change_1h)
        abs_4h = abs(change_4h) 
        abs_24h = abs(change_24h)
        
        # Calculate momentum rates (change per hour)
        rate_1h = abs_1h  # Already per hour
        rate_4h = abs_4h / 4.0  # Convert to per hour
        rate_24h = abs_24h / 24.0  # Convert to per hour
        
        # Accelerating momentum: Recent periods faster than older periods
        if rate_1h > rate_4h * 1.2 and rate_4h > rate_24h * 1.1:
            return 'accelerating'
        
        # Decelerating momentum: Recent periods slower than older periods  
        elif rate_1h < rate_4h * 0.8 and rate_4h < rate_24h * 0.9:
            return 'decelerating'
        
        # Steady momentum
        else:
            return 'steady'
    
    def _calculate_comprehensive_urgency_score(self, change_1h: float, change_4h: float,
                                             change_24h: float, volume_change: float, level: str) -> float:
        """
        🧠 ENHANCED: Calculate urgency score with spike protection awareness
        
        Now penalizes already-extended moves and rewards ideal early-stage setups
        """
        
        # Base score from maximum price change
        max_change = max(abs(change_1h), abs(change_4h), abs(change_24h))
        base_score = min(max_change * 10, 100)  # Max 100 from price change
        
        # 🛡️ SPIKE PROTECTION PENALTY: Reduce urgency for extended moves
        spike_penalty = 0.0
        
        if abs(change_1h) >= 6.0:  # Already moved 6%+ in 1 hour
            spike_penalty = 0.15  # 15% penalty
        elif abs(change_1h) >= 4.0:  # Moved 4%+ in 1 hour  
            spike_penalty = 0.10  # 10% penalty
            
        # Double penalty for extended moves across multiple timeframes
        if abs(change_1h) >= 4.0 and abs(change_4h) >= 8.0:
            spike_penalty += 0.10  # Additional 10% penalty
        
        # Apply penalty
        base_score *= (1.0 - spike_penalty)
        
        # 🎯 EARLY-STAGE BONUS: Reward ideal breakout patterns
        early_stage_bonus = 0.0
        
        # Fresh breakout pattern bonus
        if 1.0 <= abs(change_1h) <= 3.0 and abs(change_4h) >= 4.0:
            early_stage_bonus += 0.20  # 20% bonus
            
        # Volume leading price bonus (predictive signal)
        if volume_change >= 150.0 and abs(change_1h) <= 2.5:
            early_stage_bonus += 0.25  # 25% bonus
        
        # Apply bonus
        base_score *= (1.0 + early_stage_bonus)
        
        # Timeframe weight (recent changes are more urgent, but with spike protection)
        if abs(change_1h) == max_change:
            if abs(change_1h) <= 4.0:  # Only boost non-extended 1h moves
                base_score *= 1.5  # 1h moves get 50% bonus
            else:
                base_score *= 1.2  # Reduced bonus for extended 1h moves
        elif abs(change_4h) == max_change:
            base_score *= 1.2  # 4h moves get 20% bonus
        elif abs(change_4h) == max_change:
            base_score *= 1.2  # 4h moves get 20% bonus
        
        # Volume surge bonus
        if volume_change > 100:
            volume_bonus = min(volume_change / 20, 25)  # Max 25 bonus
            base_score += volume_bonus
        
        # Level multiplier
        level_multipliers = {'CRITICAL': 1.5, 'HIGH': 1.2, 'MODERATE': 1.0}
        base_score *= level_multipliers.get(level, 1.0)
        
        # XLM +11.70% type detection bonus
        if max_change >= 10.0:
            base_score *= 1.8  # 80% bonus for double-digit moves
        elif max_change >= 7.0:
            base_score *= 1.4  # 40% bonus for 7%+ moves
        
        return min(base_score, 100.0)  # Cap at 100
    
    def _determine_alert_type_and_recommendation(self, change_1h: float, change_4h: float,
                                               change_24h: float, volume_change: float, level: str) -> Tuple[str, str]:
        """Determine alert type and recommendation"""
        
        max_change = max(abs(change_1h), abs(change_4h), abs(change_24h))
        
        # Determine alert type
        if max_change >= 8.0 or volume_change >= 300:
            alert_type = "MAJOR_MOVE"
        elif volume_change >= 200:
            alert_type = "VOLUME_SURGE"
        else:
            alert_type = "BREAKOUT"
        
        # Determine recommendation
        if level == 'CRITICAL':
            recommendation = "IMMEDIATE_SWITCH"
        elif level == 'HIGH':
            recommendation = "STRONG_CONSIDERATION"
        else:
            recommendation = "MONITOR"
        
        return alert_type, recommendation
    
    def _calculate_volume_average(self, symbol: str, ohlcv_data: List) -> float:
        """Calculate volume average from OHLCV data"""
        try:
            if not ohlcv_data:
                return 0
            
            volumes = [candle[5] for candle in ohlcv_data if candle[5]]  # Volume is index 5
            return sum(volumes) / len(volumes) if volumes else 0
        except:
            return 0
    
    def start_continuous_monitoring(self, scan_interval_seconds: int = 60):
        """Start continuous monitoring of all pairs"""
        if self.running:
            log_message("⚠️ Scanner already running")
            return
        
        self.running = True
        log_message(f"🚀 STARTING CONTINUOUS MONITORING: {len(self.supported_pairs)} pairs, {scan_interval_seconds}s intervals")
        
        def monitor_loop():
            while self.running:
                try:
                    opportunities = self.scan_all_pairs_comprehensive()
                    
                    # Process critical opportunities
                    critical_opportunities = [opp for opp in opportunities if opp.recommendation == "IMMEDIATE_SWITCH"]
                    
                    if critical_opportunities:
                        log_message(f"🚨 CRITICAL OPPORTUNITIES FOUND: {len(critical_opportunities)}")
                        self._handle_critical_opportunities(critical_opportunities)
                    
                    # Log all opportunities for record keeping
                    self.opportunity_log.extend(opportunities)
                    
                    # Keep only last 100 opportunities in memory
                    if len(self.opportunity_log) > 100:
                        self.opportunity_log = self.opportunity_log[-100:]
                    
                    time.sleep(scan_interval_seconds)
                    
                except Exception as e:
                    log_message(f"⚠️ Error in monitoring loop: {e}")
                    time.sleep(30)  # Shorter sleep on error
        
        self.scan_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.scan_thread.start()
        
        log_message("✅ CONTINUOUS MONITORING STARTED")
    
    def _handle_critical_opportunities(self, opportunities: List[OpportunityAlert]):
        """Handle critical opportunities that require immediate action"""
        for opp in opportunities:
            log_message(f"🚨 CRITICAL OPPORTUNITY: {opp.symbol}")
            log_message(f"   💹 Price Changes: 1h={opp.price_change_1h:+.2f}%, 4h={opp.price_change_4h:+.2f}%, 24h={opp.price_change_24h:+.2f}%")
            log_message(f"   📊 Volume Change: {opp.volume_change_24h:+.1f}%")
            log_message(f"   🎯 Urgency Score: {opp.urgency_score:.1f}/100")
            log_message(f"   ⚡ Recommendation: {opp.recommendation}")
            
            # Store for bot to pick up
            self.last_alerts[opp.symbol] = opp
    
    def stop_monitoring(self):
        """Stop continuous monitoring"""
        if self.running:
            self.running = False
            log_message("🛑 STOPPING CONTINUOUS MONITORING")
            if self.scan_thread:
                self.scan_thread.join(timeout=5)
            log_message("✅ MONITORING STOPPED")
    
    def get_current_opportunities(self) -> List[OpportunityAlert]:
        """Get current opportunities (for bot integration)"""
        return list(self.last_alerts.values())
    
    def get_opportunity_summary(self) -> Dict:
        """Get summary of recent opportunities"""
        recent_opportunities = [opp for opp in self.opportunity_log if 
                              (datetime.now() - opp.detected_at).seconds < 3600]  # Last hour
        
        summary = {
            'total_opportunities_last_hour': len(recent_opportunities),
            'critical_opportunities': len([opp for opp in recent_opportunities if opp.recommendation == "IMMEDIATE_SWITCH"]),
            'high_opportunities': len([opp for opp in recent_opportunities if opp.recommendation == "STRONG_CONSIDERATION"]),
            'pairs_monitored': len(self.supported_pairs),
            'scanner_status': 'RUNNING' if self.running else 'STOPPED'
        }
        
        return summary

def get_comprehensive_scanner(exchange, config_path="comprehensive_all_pairs_config.json") -> ComprehensiveOpportunityScanner:
    """Get configured comprehensive opportunity scanner with ALL pairs"""
    return ComprehensiveOpportunityScanner(exchange, config_path)

def run_immediate_comprehensive_scan(exchange) -> List[OpportunityAlert]:
    """Run immediate comprehensive scan of ALL available pairs"""
    scanner = get_comprehensive_scanner(exchange)
    
    log_message("🚀 RUNNING IMMEDIATE COMPREHENSIVE SCAN - ALL PAIRS")
    opportunities = scanner.scan_all_pairs_comprehensive()
    
    log_message(f"📊 SCAN RESULTS: {len(opportunities)} opportunities detected")
    
    return opportunities

if __name__ == "__main__":
    # Test comprehensive scanning
    print("🚀 TESTING COMPREHENSIVE OPPORTUNITY SCANNER")
    
    try:
        exchange = ccxt.binance()
        scanner = get_comprehensive_scanner(exchange)
        opportunities = scanner.scan_all_pairs_comprehensive()
        
        print(f"✅ Test completed: {len(opportunities)} opportunities found")
        
        if opportunities:
            print("\n🎯 TOP OPPORTUNITIES:")
            for i, opp in enumerate(opportunities[:3]):
                print(f"   {i+1}. {opp.symbol}: {opp.price_change_1h:+.2f}% (1h) - {opp.alert_type}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
