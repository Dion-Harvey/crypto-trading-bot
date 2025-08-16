# =============================================================================
# MULTI-CRYPTO MONITORING SYSTEM
# =============================================================================
#
# Monitors multiple cryptocurrencies and selects the best performers for trading
# Uses relative strength analysis, momentum scoring, and risk-adjusted metrics
#
# =============================================================================

import ccxt
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from log_utils import log_message

@dataclass
class CryptoMetrics:
    """Data class to store cryptocurrency performance metrics"""
    symbol: str
    price: float
    volume_24h: float
    momentum_1h: float
    momentum_4h: float
    momentum_24h: float
    volatility: float
    rsi: float
    ma_alignment_score: float
    trend_strength: float
    relative_strength_score: float
    liquidity_score: float
    final_score: float
    recommended_allocation: float

class MultiCryptoMonitor:
    """
    🎯 MULTI-CRYPTOCURRENCY MONITORING SYSTEM
    
    Monitors multiple crypto assets and selects the best performers for trading.
    Uses sophisticated scoring algorithms to rank assets by potential profitability.
    """
    
    def __init__(self, exchange):
        self.exchange = exchange
        
        # 🎯 CRYPTOCURRENCY WATCHLIST  
        # Updated for USDT-based trading pairs with user-specified assets
        self.watchlist = {
            'BTC/USDT': {'weight': 1.0, 'min_volume': 1000000},    # Bitcoin - Primary
            'ETH/USDT': {'weight': 0.9, 'min_volume': 500000},     # Ethereum
            'SOL/USDT': {'weight': 0.9, 'min_volume': 200000},     # Solana - INCREASED
            'SUI/USDT': {'weight': 0.8, 'min_volume': 50000},      # SUI - INCREASED for spike detection
            'XRP/USDT': {'weight': 0.7, 'min_volume': 300000},     # XRP/Ripple
            'ADA/USDT': {'weight': 0.7, 'min_volume': 150000},     # Cardano
            'DOGE/USDT': {'weight': 0.6, 'min_volume': 250000},    # Dogecoin
            'XLM/USDT': {'weight': 0.6, 'min_volume': 80000},      # Stellar
            'HBAR/USDT': {'weight': 0.6, 'min_volume': 80000},     # Hedera
            'SKL/USDT': {'weight': 0.6, 'min_volume': 80000},      # SKALE Network - ADDED for spike detection
            'MATIC/USDT': {'weight': 0.6, 'min_volume': 100000},   # Polygon - ADDED for layer-2 opportunities
            'LTC/USDT': {'weight': 0.6, 'min_volume': 150000},     # Litecoin - ADDED for established alt opportunities
            'SHIB/USDT': {'weight': 0.4, 'min_volume': 100000},    # Shiba Inu
        }
        
        # 🎯 SCORING WEIGHTS - ENHANCED FOR HIGH-VOLUME OPPORTUNITY DETECTION
        self.scoring_weights = {
            'momentum_30m': 0.35,     # INCREASED: Short-term momentum (30min) - catch SOL-type moves
            'momentum_2h': 0.25,      # INCREASED: Medium-term momentum (2h) - trend confirmation  
            'momentum_12h': 0.20,     # INCREASED: Long-term momentum (12h) - daily trend bias
            'volatility': 0.08,       # Volatility (higher = more opportunity)
            'rsi_mean_reversion': 0.07, # RSI-based opportunities
            'ma_alignment': 0.03,     # REDUCED: Moving average trend alignment (less weight)
            'trend_strength': 0.01,   # REDUCED: Overall trend strength (less weight)
            'liquidity': 0.01        # REDUCED: Liquidity and volume (less weight)
        }
        
        # 🎯 POSITION ALLOCATION RULES - ULTRA-AGGRESSIVE OPPORTUNITY DETECTION
        self.allocation_rules = {
            'max_assets': 2,           # Maximum assets to trade simultaneously
            'min_score_threshold': 0.01, # ULTRA-LOW: Catch almost any momentum like HBAR/XLM moves
            'top_asset_allocation': 0.7, # 70% to best asset
            'second_asset_allocation': 0.3, # 30% to second best
            'rebalance_threshold': 0.02, # ULTRA-LOW: 2% score difference to trigger rebalance (maximum sensitivity)
        }
        
        self.last_update = 0
        self.update_interval = 180  # Update every 3 minutes for day trading (faster than 5 min)
        self.crypto_data = {}
        self.current_rankings = []
        
    def fetch_crypto_data(self, symbol: str, timeframes=['30m', '2h', '12h']) -> Dict:
        """Fetch comprehensive data for a single cryptocurrency - DAY TRADING OPTIMIZED"""
        try:
            # Get current ticker data
            ticker = self.exchange.fetch_ticker(symbol)
            
            # Get OHLCV data for different timeframes
            ohlcv_data = {}
            for tf in timeframes:
                try:
                    ohlcv = self.exchange.fetch_ohlcv(symbol, tf, limit=100)
                    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                    ohlcv_data[tf] = df
                except Exception as e:
                    log_message(f"⚠️ Error fetching {tf} data for {symbol}: {e}")
                    continue
            
            return {
                'ticker': ticker,
                'ohlcv': ohlcv_data,
                'symbol': symbol,
                'timestamp': time.time()
            }
            
        except Exception as e:
            log_message(f"❌ Error fetching data for {symbol}: {e}")
            return None
    
    def calculate_momentum(self, df: pd.DataFrame, periods: List[float] = [0.5, 2, 12]) -> Dict[str, float]:
        """Calculate momentum over different periods - DAY TRADING OPTIMIZED (30min, 2h, 12h)"""
        # Convert hours to 30min periods (since we're using 30m timeframe)
        period_intervals = [max(1, int(p * 2)) for p in periods]  # 0.5h=1, 2h=4, 12h=24 intervals
        
        if len(df) < max(period_intervals):
            return {f'momentum_{p}h' if p >= 1 else f'momentum_{int(p*60)}m': 0.0 for p in periods}
        
        momentum = {}
        current_price = df['close'].iloc[-1]
        
        for i, period in enumerate(periods):
            interval = period_intervals[i]
            if len(df) >= interval:
                past_price = df['close'].iloc[-interval]
                momentum_pct = (current_price - past_price) / past_price
                key = f'momentum_{period}h' if period >= 1 else f'momentum_{int(period*60)}m'
                momentum[key] = momentum_pct
            else:
                key = f'momentum_{period}h' if period >= 1 else f'momentum_{int(period*60)}m'
                momentum[key] = 0.0
                
        return momentum
    
    def calculate_volatility(self, df: pd.DataFrame, period: int = 24) -> float:
        """Calculate recent volatility (higher = more trading opportunity)"""
        if len(df) < period:
            return 0.0
        
        recent_returns = df['close'].pct_change().tail(period).dropna()
        volatility = recent_returns.std() * np.sqrt(24)  # Annualized volatility
        return volatility
    
    def calculate_rsi(self, df: pd.DataFrame, period: int = 14) -> float:
        """Calculate RSI for mean reversion opportunities"""
        if len(df) < period + 1:
            return 50.0
        
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1] if not np.isnan(rsi.iloc[-1]) else 50.0
    
    def calculate_ma_alignment_score(self, df: pd.DataFrame) -> float:
        """Calculate moving average alignment score (trend confirmation)"""
        if len(df) < 50:
            return 0.0
        
        # Calculate multiple moving averages
        ma_7 = df['close'].rolling(7).mean().iloc[-1]
        ma_25 = df['close'].rolling(25).mean().iloc[-1]
        ma_50 = df['close'].rolling(50).mean().iloc[-1]
        current_price = df['close'].iloc[-1]
        
        # Score based on bullish alignment: Price > MA7 > MA25 > MA50
        score = 0.0
        if current_price > ma_7:
            score += 0.4
        if ma_7 > ma_25:
            score += 0.3
        if ma_25 > ma_50:
            score += 0.3
            
        return score
    
    def calculate_trend_strength(self, df: pd.DataFrame) -> float:
        """Calculate overall trend strength using multiple indicators"""
        if len(df) < 50:
            return 0.0
        
        # ADX-like calculation for trend strength
        high_low = df['high'] - df['low']
        high_close_prev = np.abs(df['high'] - df['close'].shift(1))
        low_close_prev = np.abs(df['low'] - df['close'].shift(1))
        
        true_range = np.maximum(high_low, np.maximum(high_close_prev, low_close_prev))
        atr = true_range.rolling(14).mean().iloc[-1]
        
        # Normalize trend strength
        price_range = df['close'].rolling(14).max().iloc[-1] - df['close'].rolling(14).min().iloc[-1]
        trend_strength = min(1.0, atr / price_range if price_range > 0 else 0.0)
        
        return trend_strength
    
    def calculate_liquidity_score(self, ticker: Dict, watchlist_config: Dict) -> float:
        """Calculate liquidity score based on volume and spread"""
        volume_24h = ticker.get('quoteVolume', 0)
        bid_ask_spread = ticker.get('percentage', 0)  # Simplified spread metric
        
        # Volume score (higher is better)
        min_volume = watchlist_config.get('min_volume', 50000)
        volume_score = min(1.0, volume_24h / min_volume) if min_volume > 0 else 1.0
        
        # Spread score (lower spread is better)
        spread_score = max(0.0, 1.0 - (bid_ask_spread / 2.0)) if bid_ask_spread else 1.0
        
        return (volume_score * 0.7 + spread_score * 0.3)
    
    def calculate_rsi_opportunity_score(self, rsi: float) -> float:
        """Calculate opportunity score based on RSI mean reversion potential"""
        if rsi < 30:
            return 0.8  # Oversold - good buy opportunity
        elif rsi < 40:
            return 0.6  # Moderately oversold
        elif rsi > 70:
            return 0.8  # Overbought - good sell opportunity
        elif rsi > 60:
            return 0.6  # Moderately overbought
        else:
            return 0.3  # Neutral territory
    
    def calculate_crypto_metrics(self, crypto_data: Dict) -> Optional[CryptoMetrics]:
        """Calculate comprehensive metrics for a single cryptocurrency"""
        try:
            symbol = crypto_data['symbol']
            ticker = crypto_data['ticker']
            ohlcv = crypto_data['ohlcv']
            
            # Use 30m data for primary calculations (day trading optimized)
            if '30m' not in ohlcv or len(ohlcv['30m']) < 50:
                log_message(f"⚠️ Insufficient 30m data for {symbol}")
                return None
            
            df_30m = ohlcv['30m']
            current_price = ticker['last']
            
            # Calculate all metrics
            momentum = self.calculate_momentum(df_30m)
            volatility = self.calculate_volatility(df_30m)
            rsi = self.calculate_rsi(df_30m)
            ma_alignment = self.calculate_ma_alignment_score(df_30m)
            trend_strength = self.calculate_trend_strength(df_30m)
            liquidity_score = self.calculate_liquidity_score(ticker, self.watchlist[symbol])
            
            # Calculate relative strength score using new day trading timeframes
            relative_strength_score = (
                momentum['momentum_30m'] * self.scoring_weights['momentum_30m'] +
                momentum['momentum_2h'] * self.scoring_weights['momentum_2h'] +
                momentum['momentum_12h'] * self.scoring_weights['momentum_12h'] +
                volatility * self.scoring_weights['volatility'] +
                self.calculate_rsi_opportunity_score(rsi) * self.scoring_weights['rsi_mean_reversion'] +
                ma_alignment * self.scoring_weights['ma_alignment'] +
                trend_strength * self.scoring_weights['trend_strength'] +
                liquidity_score * self.scoring_weights['liquidity']
            )
            
            # 🚀 ENHANCED: Momentum alignment bonuses for high-volume opportunities like SOL
            momentum_30m = momentum['momentum_30m']
            momentum_2h = momentum['momentum_2h']
            momentum_12h = momentum['momentum_12h']
            
            # 🚨 ULTRA-AGGRESSIVE SPIKE DETECTION - Catch HBAR +5.83% and XLM +6.40% moves
            if momentum_30m > 0.08:  # 8%+ recent spike
                relative_strength_score = max(relative_strength_score * 3.0, 0.95)  # Force 95%+ score for 8%+ moves
                log_message(f"🚨 MAJOR SPIKE DETECTED: {symbol} +{momentum_30m*100:.1f}% - FORCING 95%+ score")
            elif momentum_30m > 0.05:  # 5%+ strong move (HBAR/XLM scenario)
                relative_strength_score = max(relative_strength_score * 2.5, 0.85)  # Force 85%+ score for 5%+ moves  
                log_message(f"🚀 STRONG MOVE: {symbol} +{momentum_30m*100:.1f}% - FORCING 85%+ score")
            elif momentum_30m > 0.03:  # 3%+ solid move
                relative_strength_score = max(relative_strength_score * 2.0, 0.70)  # Force 70%+ score for 3%+ moves
                log_message(f"📈 SOLID MOVE: {symbol} +{momentum_30m*100:.1f}% - FORCING 70%+ score")
            elif momentum_30m > 0.02:  # 2%+ moderate move
                relative_strength_score *= 1.75  # Strong boost for 2%+ moves
                log_message(f"� MODERATE MOVE: {symbol} +{momentum_30m*100:.1f}% - 75% bonus applied")
            
            # Bonus for aligned positive momentum (catches uptrends like SOL moves)
            if momentum_30m > 0 and momentum_2h > 0:
                relative_strength_score *= 1.15  # 15% bonus for aligned momentum
                
            # Extra bonus for strong momentum acceleration (1%+ moves)
            if momentum_30m > 0.01 and momentum_2h > 0.005:  # 1%+ recent, 0.5%+ medium term
                relative_strength_score *= 1.10  # Additional 10% bonus
                
            # Bonus for any positive recent momentum (catches early moves)
            if momentum_30m > 0.002:  # Even 0.2% recent momentum gets a boost
                relative_strength_score += 0.05  # Flat bonus to help cross threshold
            
            # Apply symbol weight
            symbol_weight = self.watchlist[symbol]['weight']
            final_score = relative_strength_score * symbol_weight
            
            return CryptoMetrics(
                symbol=symbol,
                price=current_price,
                volume_24h=ticker.get('quoteVolume', 0),
                momentum_1h=momentum['momentum_30m'],  # Map to 30m for day trading
                momentum_4h=momentum['momentum_2h'],   # Map to 2h for day trading  
                momentum_24h=momentum['momentum_12h'], # Map to 12h for day trading
                volatility=volatility,
                rsi=rsi,
                ma_alignment_score=ma_alignment,
                trend_strength=trend_strength,
                relative_strength_score=relative_strength_score,
                liquidity_score=liquidity_score,
                final_score=final_score,
                recommended_allocation=0.0  # Will be calculated later
            )
            
        except Exception as e:
            log_message(f"❌ Error calculating metrics for {symbol}: {e}")
            return None
    
    def update_all_crypto_data(self) -> bool:
        """Update data for all cryptocurrencies in watchlist"""
        try:
            log_message("🔄 Updating multi-crypto data...")
            successful_updates = 0
            
            for symbol in self.watchlist.keys():
                crypto_data = self.fetch_crypto_data(symbol)
                if crypto_data:
                    metrics = self.calculate_crypto_metrics(crypto_data)
                    if metrics:
                        self.crypto_data[symbol] = metrics
                        successful_updates += 1
                
                # Small delay to avoid rate limiting
                time.sleep(0.2)
            
            if successful_updates > 0:
                self.last_update = time.time()
                log_message(f"✅ Updated data for {successful_updates}/{len(self.watchlist)} cryptocurrencies")
                return True
            else:
                log_message("❌ Failed to update any cryptocurrency data")
                return False
                
        except Exception as e:
            log_message(f"❌ Error updating crypto data: {e}")
            return False
    
    def rank_cryptocurrencies(self) -> List[CryptoMetrics]:
        """Rank all cryptocurrencies by their performance scores"""
        if not self.crypto_data:
            return []
        
        # Filter by minimum score threshold
        min_score = self.allocation_rules['min_score_threshold']
        
        # 🔍 DEBUG: Log all scores for opportunity analysis
        log_message(f"🔍 SCORING DEBUG (threshold: {min_score:.3f}):")
        for symbol, metrics in self.crypto_data.items():
            status = "✅ PASS" if metrics.final_score >= min_score else "❌ FAIL"
            log_message(f"   {symbol}: {metrics.final_score:.3f} | 30m:{metrics.momentum_1h:+.3f} 2h:{metrics.momentum_4h:+.3f} | {status}")
        
        eligible_cryptos = [
            metrics for metrics in self.crypto_data.values() 
            if metrics.final_score >= min_score
        ]
        
        log_message(f"🎯 Found {len(eligible_cryptos)}/{len(self.crypto_data)} cryptos above threshold {min_score:.3f}")
        
        # Sort by final score (descending)
        ranked_cryptos = sorted(eligible_cryptos, key=lambda x: x.final_score, reverse=True)
        
        # Calculate recommended allocations
        max_assets = self.allocation_rules['max_assets']
        top_assets = ranked_cryptos[:max_assets]
        
        if len(top_assets) >= 2:
            top_assets[0].recommended_allocation = self.allocation_rules['top_asset_allocation']
            top_assets[1].recommended_allocation = self.allocation_rules['second_asset_allocation']
        elif len(top_assets) == 1:
            top_assets[0].recommended_allocation = 1.0
        
        self.current_rankings = ranked_cryptos
        return ranked_cryptos
    
    def get_trading_recommendations(self) -> Dict:
        """Get current trading recommendations based on crypto rankings"""
        if time.time() - self.last_update > self.update_interval:
            self.update_all_crypto_data()
        
        rankings = self.rank_cryptocurrencies()
        
        if not rankings:
            return {
                'status': 'no_opportunities',
                'message': 'No cryptocurrencies meet minimum score threshold',
                'recommendations': []
            }
        
        recommendations = []
        for i, crypto in enumerate(rankings[:self.allocation_rules['max_assets']]):
            recommendations.append({
                'rank': i + 1,
                'symbol': crypto.symbol,
                'score': crypto.final_score,
                'allocation': crypto.recommended_allocation,
                'metrics': {
                    'price': crypto.price,
                    'momentum_1h': f"{crypto.momentum_1h:+.2%}",
                    'momentum_4h': f"{crypto.momentum_4h:+.2%}",
                    'momentum_24h': f"{crypto.momentum_24h:+.2%}",
                    'rsi': f"{crypto.rsi:.1f}",
                    'volatility': f"{crypto.volatility:.2%}",
                    'trend_alignment': f"{crypto.ma_alignment_score:.2f}",
                }
            })
        
        return {
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'total_opportunities': len(rankings),
            'recommendations': recommendations
        }
    
    def log_current_rankings(self):
        """Log current cryptocurrency rankings for monitoring"""
        if not self.current_rankings:
            return
        
        log_message("🏆 MULTI-CRYPTO RANKINGS:")
        log_message("=" * 80)
        
        for i, crypto in enumerate(self.current_rankings[:5], 1):
            log_message(f"{i}. {crypto.symbol}")
            log_message(f"   Score: {crypto.final_score:.3f} | Price: ${crypto.price:.2f}")
            log_message(f"   Momentum: 1h:{crypto.momentum_1h:+.2%} 4h:{crypto.momentum_4h:+.2%} 24h:{crypto.momentum_24h:+.2%}")
            log_message(f"   RSI: {crypto.rsi:.1f} | Vol: {crypto.volatility:.2%} | Trend: {crypto.ma_alignment_score:.2f}")
            if crypto.recommended_allocation > 0:
                log_message(f"   🎯 RECOMMENDED: {crypto.recommended_allocation:.1%} allocation")
            log_message("")

def get_multi_crypto_monitor(exchange):
    """Factory function to get the multi-crypto monitor instance"""
    if not hasattr(get_multi_crypto_monitor, 'instance'):
        get_multi_crypto_monitor.instance = MultiCryptoMonitor(exchange)
    return get_multi_crypto_monitor.instance
