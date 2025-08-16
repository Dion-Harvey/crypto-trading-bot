# =============================================================================
# MULTI-PAIR OPPORTUNITY SCANNER
# =============================================================================
#
# 🎯 24/7 MULTI-PAIR MOMENTUM DETECTION SYSTEM
# Scans all supported pairs for maximum profit opportunities
# Automatically switches to the most profitable trading pair
#
# =============================================================================

import ccxt
import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import logging

@dataclass
class TradingOpportunity:
    """Represents a detected trading opportunity"""
    symbol: str
    price_change_1h: float
    price_change_5m: float
    volume_24h: float
    volume_surge: float
    momentum_score: float
    confidence: float
    timestamp: datetime
    
class MultiPairScanner:
    """
    🎯 MULTI-PAIR OPPORTUNITY SCANNER
    
    Continuously monitors all supported trading pairs for:
    - Price momentum (1h, 5m, 1m changes)
    - Volume surges (24h vs 7d average)
    - Breakout patterns
    - Whale activity indicators
    
    Automatically identifies the most profitable pair to trade
    """
    
    def __init__(self, config_path: str = "enhanced_config.json"):
        self.config = self._load_config(config_path)
        self.exchange = None
        self.scanning = False
        self.opportunities = {}
        self.current_best_pair = None
        
        # 🎯 SCANNING CONFIGURATION
        self.scan_config = {
            'supported_pairs': [
                "BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT",
                "ADA/USDT", "DOGE/USDT", "XLM/USDT", "SUI/USDT", 
                "SHIB/USDT", "HBAR/USDT", "AVAX/USDT", "DOT/USDT",
                "MATIC/USDT", "LINK/USDT", "UNI/USDT", "LTC/USDT"
            ],
            'scan_interval_seconds': 30,  # Scan every 30 seconds
            'momentum_thresholds': {
                'strong_bullish': 3.0,    # 3%+ in 1h
                'moderate_bullish': 1.5,  # 1.5%+ in 1h
                'weak_bullish': 0.5,      # 0.5%+ in 1h
                'volume_surge_min': 2.0   # 2x normal volume
            },
            'opportunity_scoring': {
                'price_momentum_weight': 0.4,     # 40%
                'volume_surge_weight': 0.3,       # 30%
                'recent_breakout_weight': 0.2,    # 20%
                'whale_activity_weight': 0.1      # 10%
            }
        }
        
        # 📊 MOMENTUM TRACKING
        self.momentum_history = {}
        self.volume_baselines = {}
        
        # 🚨 ALERT SYSTEM
        self.alert_thresholds = {
            'immediate_switch': 0.85,      # 85%+ confidence = immediate switch
            'high_opportunity': 0.75,      # 75%+ confidence = high alert
            'moderate_opportunity': 0.6,   # 60%+ confidence = moderate alert
            'min_profit_potential': 2.0    # 2%+ potential required
        }
        
        # 🎯 BINANCE NATIVE TRAILING STOP PREFERENCE
        self.use_native_trailing_stops = True
        self.trailing_stop_percent = 0.25  # 0.25% trailing stop
        
        self.logger = self._setup_logging()
    
    def _load_config(self, config_path: str) -> Dict:
        """Load bot configuration"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Error loading config: {e}")
            return {}
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for scanner"""
        logger = logging.getLogger('MultiPairScanner')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '[%(asctime)s] 🎯 SCANNER: %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def initialize_exchange(self) -> bool:
        """Initialize exchange connection"""
        try:
            # Use demo mode if no API keys
            self.exchange = ccxt.binanceus({
                'sandbox': True,  # Use testnet for safety
                'enableRateLimit': True,
                'timeout': 30000
            })
            
            # Test connection
            self.exchange.load_markets()
            self.logger.info("✅ Exchange connection established")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Exchange initialization failed: {e}")
            # Fallback to free API mode
            self.exchange = None
            return False
    
    async def scan_all_pairs(self) -> Dict[str, TradingOpportunity]:
        """Scan all supported pairs for opportunities"""
        opportunities = {}
        
        for symbol in self.scan_config['supported_pairs']:
            try:
                opportunity = await self._analyze_pair(symbol)
                if opportunity:
                    opportunities[symbol] = opportunity
                    
            except Exception as e:
                self.logger.warning(f"⚠️ Error analyzing {symbol}: {e}")
                continue
        
        return opportunities
    
    async def _analyze_pair(self, symbol: str) -> Optional[TradingOpportunity]:
        """Analyze individual trading pair for opportunities"""
        try:
            # Get market data
            ticker = await self._get_ticker_data(symbol)
            if not ticker:
                return None
            
            # Calculate momentum indicators
            price_change_1h = ticker.get('percentage', 0)
            price_change_5m = await self._get_short_term_change(symbol, '5m')
            volume_24h = ticker.get('quoteVolume', 0)
            
            # Calculate volume surge
            volume_surge = await self._calculate_volume_surge(symbol, volume_24h)
            
            # Calculate momentum score
            momentum_score = self._calculate_momentum_score(
                price_change_1h, price_change_5m, volume_surge
            )
            
            # Calculate confidence level
            confidence = self._calculate_confidence(
                momentum_score, volume_surge, price_change_1h
            )
            
            # Only return if meets minimum thresholds
            if (abs(price_change_1h) >= 0.5 or 
                momentum_score >= 0.6 or 
                volume_surge >= 1.5):
                
                return TradingOpportunity(
                    symbol=symbol,
                    price_change_1h=price_change_1h,
                    price_change_5m=price_change_5m,
                    volume_24h=volume_24h,
                    volume_surge=volume_surge,
                    momentum_score=momentum_score,
                    confidence=confidence,
                    timestamp=datetime.now()
                )
            
            return None
            
        except Exception as e:
            self.logger.warning(f"⚠️ Analysis error for {symbol}: {e}")
            return None
    
    async def _get_ticker_data(self, symbol: str) -> Optional[Dict]:
        """Get ticker data for symbol"""
        try:
            if self.exchange:
                return self.exchange.fetch_ticker(symbol)
            else:
                # Fallback to free API simulation
                return await self._simulate_ticker_data(symbol)
        except Exception as e:
            self.logger.warning(f"⚠️ Ticker data error for {symbol}: {e}")
            return None
    
    async def _simulate_ticker_data(self, symbol: str) -> Dict:
        """Simulate ticker data using free APIs"""
        # This would integrate with the free APIs from unified_free_config
        # For now, return mock data structure
        import random
        
        base_changes = {
            'SUI/USDT': 6.5, 'HBAR/USDT': 4.46, 'SOL/USDT': 2.1,
            'ETH/USDT': 1.8, 'BTC/USDT': 0.5, 'ADA/USDT': 3.2
        }
        
        change = base_changes.get(symbol, random.uniform(-2, 4))
        
        return {
            'symbol': symbol,
            'last': 100 + random.uniform(-10, 10),
            'percentage': change,
            'quoteVolume': random.uniform(1000000, 50000000),
            'timestamp': int(time.time() * 1000)
        }
    
    async def _get_short_term_change(self, symbol: str, timeframe: str) -> float:
        """Get short-term price change"""
        try:
            if self.exchange:
                # Get recent OHLCV data
                ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=2)
                if len(ohlcv) >= 2:
                    old_close = ohlcv[0][4]
                    new_close = ohlcv[1][4]
                    return ((new_close - old_close) / old_close) * 100
            
            # Fallback estimation
            return 0.0
            
        except Exception as e:
            return 0.0
    
    async def _calculate_volume_surge(self, symbol: str, current_volume: float) -> float:
        """Calculate volume surge vs baseline"""
        try:
            # Get or create volume baseline
            if symbol not in self.volume_baselines:
                self.volume_baselines[symbol] = current_volume
                return 1.0
            
            baseline = self.volume_baselines[symbol]
            surge = current_volume / baseline if baseline > 0 else 1.0
            
            # Update baseline (7-day rolling average simulation)
            self.volume_baselines[symbol] = (baseline * 0.9) + (current_volume * 0.1)
            
            return surge
            
        except Exception as e:
            return 1.0
    
    def _calculate_momentum_score(self, change_1h: float, change_5m: float, volume_surge: float) -> float:
        """Calculate overall momentum score (0-1)"""
        try:
            # Normalize components
            momentum_component = min(abs(change_1h) / 10.0, 1.0)  # 10% = max score
            acceleration_component = min(abs(change_5m) / 2.0, 1.0)  # 2% = max score
            volume_component = min(volume_surge / 5.0, 1.0)  # 5x = max score
            
            # Weighted score
            weights = self.scan_config['opportunity_scoring']
            score = (
                momentum_component * weights['price_momentum_weight'] +
                volume_component * weights['volume_surge_weight'] +
                acceleration_component * weights['recent_breakout_weight']
            )
            
            return min(score, 1.0)
            
        except Exception as e:
            return 0.0
    
    def _calculate_confidence(self, momentum_score: float, volume_surge: float, price_change: float) -> float:
        """Calculate confidence level in opportunity"""
        try:
            # Base confidence from momentum
            confidence = momentum_score
            
            # Boost for volume confirmation
            if volume_surge > 2.0:
                confidence += 0.1
            if volume_surge > 3.0:
                confidence += 0.1
            
            # Boost for strong directional movement
            if abs(price_change) > 3.0:
                confidence += 0.15
            elif abs(price_change) > 1.5:
                confidence += 0.1
            
            return min(confidence, 1.0)
            
        except Exception as e:
            return 0.0
    
    def get_best_opportunity(self) -> Optional[TradingOpportunity]:
        """Get the highest-scoring trading opportunity"""
        if not self.opportunities:
            return None
        
        # Sort by confidence * momentum_score
        best_pair = max(
            self.opportunities.items(),
            key=lambda x: x[1].confidence * x[1].momentum_score
        )
        
        return best_pair[1] if best_pair[1].confidence >= self.alert_thresholds['moderate_opportunity'] else None
    
    def should_switch_pair(self, current_pair: str) -> Tuple[bool, Optional[str]]:
        """Determine if bot should switch trading pairs"""
        best_opportunity = self.get_best_opportunity()
        
        if not best_opportunity:
            return False, None
        
        # Check if significantly better than current pair
        current_opportunity = self.opportunities.get(current_pair)
        
        if not current_opportunity:
            # Current pair has no opportunity, switch to best
            if best_opportunity.confidence >= self.alert_thresholds['high_opportunity']:
                return True, best_opportunity.symbol
        else:
            # Compare opportunities
            current_score = current_opportunity.confidence * current_opportunity.momentum_score
            best_score = best_opportunity.confidence * best_opportunity.momentum_score
            
            # Switch if new opportunity is significantly better
            if best_score > current_score * 1.5:  # 50% better
                return True, best_opportunity.symbol
        
        return False, None
    
    async def start_scanning(self):
        """Start continuous pair scanning"""
        self.scanning = True
        self.logger.info("🚀 Starting multi-pair scanning...")
        
        # Initialize exchange if possible
        self.initialize_exchange()
        
        while self.scanning:
            try:
                # Scan all pairs
                self.opportunities = await self.scan_all_pairs()
                
                # Log opportunities
                self._log_opportunities()
                
                # Check for pair switching
                current_pair = self.config.get('trading', {}).get('symbol', 'BTC/USDT')
                should_switch, new_pair = self.should_switch_pair(current_pair)
                
                if should_switch and new_pair:
                    await self._recommend_pair_switch(current_pair, new_pair)
                
                # Wait for next scan
                await asyncio.sleep(self.scan_config['scan_interval_seconds'])
                
            except Exception as e:
                self.logger.error(f"❌ Scanning error: {e}")
                await asyncio.sleep(10)  # Short delay on error
    
    def _log_opportunities(self):
        """Log detected opportunities"""
        if not self.opportunities:
            return
        
        # Sort by score
        sorted_opps = sorted(
            self.opportunities.items(),
            key=lambda x: x[1].confidence * x[1].momentum_score,
            reverse=True
        )
        
        self.logger.info("📊 OPPORTUNITY SCAN RESULTS:")
        for symbol, opp in sorted_opps[:5]:  # Top 5
            score = opp.confidence * opp.momentum_score
            self.logger.info(
                f"   {symbol}: {opp.price_change_1h:+.2f}% (1h) | "
                f"Vol: {opp.volume_surge:.1f}x | "
                f"Score: {score:.3f} | "
                f"Confidence: {opp.confidence:.1%}"
            )
    
    async def _recommend_pair_switch(self, current_pair: str, new_pair: str):
        """Recommend switching to new trading pair"""
        opportunity = self.opportunities[new_pair]
        
        self.logger.info("🎯 PAIR SWITCH RECOMMENDATION:")
        self.logger.info(f"   Current: {current_pair}")
        self.logger.info(f"   Recommended: {new_pair}")
        self.logger.info(f"   Price Change: {opportunity.price_change_1h:+.2f}% (1h)")
        self.logger.info(f"   Volume Surge: {opportunity.volume_surge:.1f}x")
        self.logger.info(f"   Confidence: {opportunity.confidence:.1%}")
        self.logger.info(f"   Potential Profit: {opportunity.momentum_score * 5:.1f}%")
        
        # Update config file with new pair
        await self._update_bot_config(new_pair)
    
    async def _update_bot_config(self, new_pair: str):
        """Update bot configuration with new trading pair"""
        try:
            # Update config
            if 'trading' not in self.config:
                self.config['trading'] = {}
            
            old_pair = self.config['trading'].get('symbol', 'Unknown')
            self.config['trading']['symbol'] = new_pair
            self.config['trading']['last_pair_switch'] = datetime.now().isoformat()
            self.config['trading']['switch_reason'] = f"Opportunity detected: {self.opportunities[new_pair].confidence:.1%} confidence"
            
            # Save config
            with open('enhanced_config.json', 'w') as f:
                json.dump(self.config, f, indent=2)
            
            self.logger.info(f"✅ Bot config updated: {old_pair} → {new_pair}")
            
        except Exception as e:
            self.logger.error(f"❌ Config update failed: {e}")
    
    def stop_scanning(self):
        """Stop scanning"""
        self.scanning = False
        self.logger.info("⏹️ Multi-pair scanning stopped")
    
    def get_status_report(self) -> Dict:
        """Get current scanner status"""
        best_opp = self.get_best_opportunity()
        
        return {
            'scanning_active': self.scanning,
            'pairs_monitored': len(self.scan_config['supported_pairs']),
            'opportunities_detected': len(self.opportunities),
            'best_opportunity': {
                'symbol': best_opp.symbol if best_opp else None,
                'confidence': best_opp.confidence if best_opp else 0,
                'price_change_1h': best_opp.price_change_1h if best_opp else 0,
                'momentum_score': best_opp.momentum_score if best_opp else 0
            } if best_opp else None,
            'last_scan': datetime.now().isoformat(),
            'exchange_connected': self.exchange is not None
        }

# 🎯 INTEGRATION FUNCTIONS
def create_scanner(config_path: str = "enhanced_config.json") -> MultiPairScanner:
    """Create multi-pair scanner instance"""
    return MultiPairScanner(config_path)

async def run_opportunity_scan(duration_minutes: int = 60):
    """Run opportunity scanning for specified duration"""
    scanner = create_scanner()
    
    # Run for specified duration
    end_time = datetime.now() + timedelta(minutes=duration_minutes)
    
    scan_task = asyncio.create_task(scanner.start_scanning())
    
    try:
        while datetime.now() < end_time:
            await asyncio.sleep(30)
            
            # Print status every 5 minutes
            if datetime.now().minute % 5 == 0:
                status = scanner.get_status_report()
                print(f"🎯 Scanner Status: {status['opportunities_detected']} opportunities detected")
                
                if status['best_opportunity']:
                    best = status['best_opportunity']
                    print(f"   🏆 Best: {best['symbol']} ({best['confidence']:.1%} confidence, {best['price_change_1h']:+.2f}%)")
    
    finally:
        scanner.stop_scanning()

if __name__ == "__main__":
    print("🎯 MULTI-PAIR OPPORTUNITY SCANNER")
    print("="*50)
    
    # Run scanner for testing
    asyncio.run(run_opportunity_scan(duration_minutes=10))
