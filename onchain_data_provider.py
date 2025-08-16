# =============================================================================
# ON-CHAIN DATA PROVIDER - Strategic Enhancement
# =============================================================================
#
# Implements the document's recommendations for on-chain intelligence
# Priority: Exchange flows, stablecoin movements, smart money tracking
#
# =============================================================================

import requests
import time
from datetime import datetime, timedelta
from log_utils import log_message

try:
    from onchain_config import get_api_key, should_use_provider
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False
    def get_api_key(provider): 
        return ''
    def should_use_provider(provider): 
        return provider == 'coingecko'  # Default to CoinGecko only

class OnChainDataProvider:
    """
    🎯 ON-CHAIN INTELLIGENCE SYSTEM
    
    Implements document recommendations for predictive trading:
    1. Exchange inflows/outflows (accumulation vs distribution)
    2. Stablecoin movements (fresh capital detection)
    3. Smart money tracking (whale activity)
    4. Volume surge detection (5x multiplier alerts)
    """
    
    def __init__(self):
        self.last_fetch_time = {}
        self.cache_duration = 60  # 1 minute cache
        
        # Document-recommended thresholds
        self.SIGNIFICANT_FLOW_THRESHOLD = 1000000  # $1M+ flows
        self.STABLECOIN_SURGE_THRESHOLD = 5000000  # $5M+ stablecoin inflows
        self.VOLUME_SURGE_MULTIPLIER = 5.0  # 5x volume surge detection
        
    def get_exchange_flows(self, symbol, timeframe='1h'):
        """
        🔄 EXCHANGE FLOW ANALYSIS
        
        Monitors crypto moving to/from exchanges
        - Negative flows = tokens leaving exchanges (BULLISH accumulation)
        - Positive flows = tokens entering exchanges (BEARISH distribution)
        """
        try:
            # Using CryptoQuant-style API structure (free tier available)
            cache_key = f"flows_{symbol}_{timeframe}"
            
            if self._is_cached(cache_key):
                return self._get_cached_data(cache_key)
            
            # Simulated API call structure for CryptoQuant/CoinAPI
            api_data = self._fetch_flow_data(symbol, timeframe)
            
            if api_data:
                flow_analysis = {
                    'net_flow': api_data.get('net_flow', 0),
                    'inflow': api_data.get('inflow', 0),
                    'outflow': api_data.get('outflow', 0),
                    'flow_signal': self._analyze_flow_signal(api_data),
                    'confidence': self._calculate_flow_confidence(api_data),
                    'timestamp': datetime.now()
                }
                
                self._cache_data(cache_key, flow_analysis)
                return flow_analysis
            
            return None
            
        except Exception as e:
            log_message(f"⚠️ Error fetching exchange flows for {symbol}: {e}")
            return None
    
    def get_stablecoin_inflows(self, exchanges=['binance', 'coinbase']):
        """
        💰 STABLECOIN INFLOW DETECTION
        
        Document emphasis: "Strong bullish signal - fresh capital ready to buy"
        Monitors USDT, USDC, BUSD flows into major exchanges
        """
        try:
            cache_key = "stablecoin_inflows"
            
            if self._is_cached(cache_key):
                return self._get_cached_data(cache_key)
            
            total_inflows = 0
            stablecoin_data = {}
            
            for stable in ['USDT', 'USDC', 'BUSD']:
                # Simulated API structure
                inflow_data = self._fetch_stablecoin_data(stable, exchanges)
                if inflow_data:
                    stablecoin_data[stable] = inflow_data
                    total_inflows += inflow_data.get('total_inflow', 0)
            
            analysis = {
                'total_inflows': total_inflows,
                'stablecoin_breakdown': stablecoin_data,
                'surge_detected': total_inflows > self.STABLECOIN_SURGE_THRESHOLD,
                'bullish_signal': total_inflows > self.STABLECOIN_SURGE_THRESHOLD * 0.5,
                'confidence': min(1.0, total_inflows / self.STABLECOIN_SURGE_THRESHOLD),
                'timestamp': datetime.now()
            }
            
            self._cache_data(cache_key, analysis)
            return analysis
            
        except Exception as e:
            log_message(f"⚠️ Error fetching stablecoin inflows: {e}")
            return None
    
    def detect_volume_surge(self, symbol, lookback_hours=24):
        """
        📈 VOLUME SURGE DETECTION
        
        Document recommendation: 5x volume multiplier for spike alerts
        Identifies abnormal trading activity preceding price moves
        """
        try:
            cache_key = f"volume_surge_{symbol}"
            
            if self._is_cached(cache_key):
                return self._get_cached_data(cache_key)
            
            # Get current vs historical volume
            current_volume = self._get_current_volume(symbol)
            avg_volume = self._get_average_volume(symbol, lookback_hours)
            
            if current_volume and avg_volume:
                volume_ratio = current_volume / avg_volume
                
                surge_analysis = {
                    'current_volume': current_volume,
                    'average_volume': avg_volume,
                    'volume_ratio': volume_ratio,
                    'surge_detected': volume_ratio >= self.VOLUME_SURGE_MULTIPLIER,
                    'surge_level': self._categorize_surge(volume_ratio),
                    'confidence': min(1.0, volume_ratio / self.VOLUME_SURGE_MULTIPLIER),
                    'timestamp': datetime.now()
                }
                
                self._cache_data(cache_key, surge_analysis)
                return surge_analysis
            
            return None
            
        except Exception as e:
            log_message(f"⚠️ Error detecting volume surge for {symbol}: {e}")
            return None
    
    def get_smart_money_activity(self, symbol):
        """
        🐋 SMART MONEY TRACKING
        
        Document priority: "Whale activity peaks coincide with profit-taking spikes"
        Monitors large holder movements and institutional activity
        """
        try:
            cache_key = f"smart_money_{symbol}"
            
            if self._is_cached(cache_key):
                return self._get_cached_data(cache_key)
            
            # Simulated Nansen-style smart money data
            smart_money_data = self._fetch_smart_money_data(symbol)
            
            if smart_money_data:
                activity_analysis = {
                    'whale_accumulation': smart_money_data.get('accumulation_score', 0),
                    'institutional_flows': smart_money_data.get('institutional_flows', 0),
                    'smart_money_sentiment': smart_money_data.get('sentiment', 'neutral'),
                    'large_holder_activity': smart_money_data.get('large_holder_activity', 0),
                    'activity_signal': self._analyze_smart_money_signal(smart_money_data),
                    'confidence': smart_money_data.get('confidence', 0.5),
                    'timestamp': datetime.now()
                }
                
                self._cache_data(cache_key, activity_analysis)
                return activity_analysis
            
            return None
            
        except Exception as e:
            log_message(f"⚠️ Error fetching smart money data for {symbol}: {e}")
            return None
    
    def calculate_onchain_score(self, symbol):
        """
        🎯 UNIFIED ON-CHAIN SCORING
        
        Combines all on-chain signals into weighted score for bot integration
        Based on document's multi-factor confirmation approach
        """
        try:
            # Get all on-chain data
            flows = self.get_exchange_flows(symbol)
            stablecoin = self.get_stablecoin_inflows()
            volume = self.detect_volume_surge(symbol)
            smart_money = self.get_smart_money_activity(symbol)
            
            onchain_score = 0.0
            factors = []
            
            # Exchange flow scoring (30% weight)
            if flows and flows['flow_signal'] == 'bullish':
                flow_contribution = flows['confidence'] * 0.3
                onchain_score += flow_contribution
                factors.append(f"Exchange outflows (+{flow_contribution:.2f})")
            
            # Stablecoin inflow scoring (25% weight)
            if stablecoin and stablecoin['bullish_signal']:
                stable_contribution = stablecoin['confidence'] * 0.25
                onchain_score += stable_contribution
                factors.append(f"Stablecoin inflows (+{stable_contribution:.2f})")
            
            # Volume surge scoring (25% weight)
            if volume and volume['surge_detected']:
                volume_contribution = volume['confidence'] * 0.25
                onchain_score += volume_contribution
                factors.append(f"Volume surge (+{volume_contribution:.2f})")
            
            # Smart money scoring (20% weight)
            if smart_money and smart_money['activity_signal'] == 'bullish':
                smart_contribution = smart_money['confidence'] * 0.20
                onchain_score += smart_contribution
                factors.append(f"Smart money activity (+{smart_contribution:.2f})")
            
            return {
                'onchain_score': onchain_score,
                'max_score': 1.0,
                'contributing_factors': factors,
                'signal_strength': self._categorize_signal_strength(onchain_score),
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            log_message(f"⚠️ Error calculating on-chain score for {symbol}: {e}")
            return {'onchain_score': 0.0, 'contributing_factors': [], 'signal_strength': 'weak'}
    
    # =============================================================================
    # COINGECKO API INTEGRATION (Crypto API + DEX API)
    # =============================================================================
    
    def _fetch_coingecko_dex_flows(self, symbol):
        """
        🌟 COINGECKO DEX API - On-chain Flow Intelligence
        
        Uses CoinGecko's DEX API to track actual on-chain flows
        - DEX transaction volume
        - Liquidity pool changes  
        - Cross-chain bridge activity
        - Real on-chain accumulation signals
        """
        try:
            # Convert symbol format (BTC/USDT → bitcoin)
            coin_id = self._symbol_to_coingecko_id(symbol)
            if not coin_id:
                return None
            
            # CoinGecko DEX API endpoints (free tier)
            dex_url = f"https://api.coingecko.com/api/v3/onchain/networks/ethereum/pools/{coin_id}"
            
            headers = {'accept': 'application/json'}
            # Add API key if available for higher rate limits
            api_key = get_api_key('coingecko')
            if api_key:
                headers['x-cg-demo-api-key'] = api_key
            
            response = requests.get(dex_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                dex_data = response.json()
                
                # Analyze DEX flow patterns
                flow_analysis = self._analyze_dex_flows(dex_data)
                
                log_message(f"✅ CoinGecko DEX data retrieved for {symbol}")
                return flow_analysis
            else:
                log_message(f"⚠️ CoinGecko DEX API error: {response.status_code}")
                return None
                
        except Exception as e:
            log_message(f"⚠️ CoinGecko DEX API error: {e}")
            return None
    
    def _fetch_coingecko_volume(self, symbol):
        """
        📊 COINGECKO CRYPTO API - Volume & Market Intelligence
        
        Uses CoinGecko's main Crypto API for:
        - Real-time trading volume
        - Market cap changes
        - Price momentum indicators
        - Global market metrics
        """
        try:
            coin_id = self._symbol_to_coingecko_id(symbol)
            if not coin_id:
                return None
            
            # CoinGecko Crypto API for market data
            crypto_url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
            params = {
                'vs_currency': 'usd',
                'days': '1',  # Last 24 hours
                'interval': 'hourly'
            }
            
            headers = {'accept': 'application/json'}
            api_key = get_api_key('coingecko')
            if api_key:
                headers['x-cg-demo-api-key'] = api_key
            
            response = requests.get(crypto_url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                market_data = response.json()
                
                # Extract volume intelligence
                volume_analysis = self._analyze_crypto_volume(market_data)
                
                log_message(f"✅ CoinGecko Crypto data retrieved for {symbol}")
                return volume_analysis
            else:
                log_message(f"⚠️ CoinGecko Crypto API error: {response.status_code}")
                return None
                
        except Exception as e:
            log_message(f"⚠️ CoinGecko Crypto API error: {e}")
            return None
    
    def _analyze_market_flows_coingecko(self, symbol, timeframe):
        """
        🔍 MARKET FLOW ANALYSIS using CoinGecko data
        
        Analyzes trading patterns to infer accumulation/distribution:
        - Volume vs price divergence
        - Buying vs selling pressure indicators
        - Market maker vs retail activity patterns
        """
        try:
            volume_data = self._fetch_coingecko_volume(symbol)
            if not volume_data:
                return None
            
            current_volume = volume_data.get('current_volume', 0)
            avg_volume = volume_data.get('avg_volume_24h', 1)
            price_change = volume_data.get('price_change_24h', 0)
            
            # Analyze flow patterns based on volume-price relationship
            if current_volume > avg_volume * 2 and price_change > 0:
                # High volume + rising price = accumulation (bullish)
                net_flow = -current_volume * 0.6  # Estimate 60% net outflow from exchanges
                confidence = min(0.8, current_volume / (avg_volume * 3))
                
            elif current_volume > avg_volume * 2 and price_change < 0:
                # High volume + falling price = distribution (bearish)
                net_flow = current_volume * 0.7  # Estimate 70% net inflow to exchanges
                confidence = min(0.8, current_volume / (avg_volume * 3))
                
            else:
                # Normal volume = neutral flows
                net_flow = current_volume * 0.1 * (1 if price_change > 0 else -1)
                confidence = 0.3
            
            return {
                'net_flow': net_flow,
                'inflow': max(0, net_flow),
                'outflow': max(0, -net_flow),
                'confidence': confidence,
                'source': 'coingecko_analysis',
                'volume_ratio': current_volume / avg_volume if avg_volume > 0 else 1
            }
            
        except Exception as e:
            log_message(f"⚠️ Error analyzing market flows: {e}")
            return None
    
    def _analyze_dex_flows(self, dex_data):
        """
        🧠 DEX FLOW PATTERN ANALYSIS
        
        Analyzes on-chain DEX data to identify:
        - Liquidity pool changes (accumulation indicators)
        - Large transactions (whale activity)
        - Cross-DEX arbitrage flows
        - DeFi protocol interactions
        """
        try:
            # Extract key DEX metrics
            pools = dex_data.get('data', {}).get('pools', [])
            if not pools:
                return None
            
            total_volume_24h = 0
            total_liquidity_change = 0
            large_tx_count = 0
            
            for pool in pools:
                # Volume analysis
                volume_24h = pool.get('volume_24h_usd', 0)
                total_volume_24h += volume_24h
                
                # Liquidity change analysis
                liquidity_change = pool.get('liquidity_change_24h', 0)
                total_liquidity_change += liquidity_change
                
                # Large transaction detection
                transactions = pool.get('transactions', [])
                large_tx_count += len([tx for tx in transactions 
                                     if tx.get('amount_usd', 0) > 100000])  # $100k+ transactions
            
            # Determine flow signal based on DEX activity
            if total_liquidity_change > 0 and large_tx_count > 5:
                # Increasing liquidity + whale activity = accumulation
                net_flow = -total_volume_24h * 0.4  # Estimate net outflow from CEXs
                confidence = min(0.9, (large_tx_count / 10) + (total_liquidity_change / 1000000))
                
            elif total_liquidity_change < 0 and total_volume_24h > 10000000:  # $10M+ volume
                # Decreasing liquidity + high volume = distribution
                net_flow = total_volume_24h * 0.3  # Estimate net inflow to CEXs
                confidence = min(0.8, total_volume_24h / 50000000)  # Scale with volume
                
            else:
                # Normal DEX activity
                net_flow = total_liquidity_change * 0.5
                confidence = 0.4
            
            return {
                'net_flow': net_flow,
                'inflow': max(0, net_flow),
                'outflow': max(0, -net_flow),
                'confidence': confidence,
                'source': 'coingecko_dex',
                'large_tx_count': large_tx_count,
                'liquidity_change': total_liquidity_change,
                'dex_volume_24h': total_volume_24h
            }
            
        except Exception as e:
            log_message(f"⚠️ Error analyzing DEX flows: {e}")
            return None
    
    def _analyze_crypto_volume(self, market_data):
        """
        📈 CRYPTO VOLUME PATTERN ANALYSIS
        
        Analyzes CoinGecko market data for:
        - Volume surge detection
        - Buying pressure indicators
        - Market momentum shifts
        - Institutional vs retail activity
        """
        try:
            # Extract volume and price data
            volumes = market_data.get('total_volumes', [])
            prices = market_data.get('prices', [])
            
            if len(volumes) < 2 or len(prices) < 2:
                return None
            
            # Calculate current vs historical metrics
            current_volume = volumes[-1][1]  # Latest volume
            recent_avg = sum([v[1] for v in volumes[-6:]]) / 6  # 6-hour average
            daily_avg = sum([v[1] for v in volumes]) / len(volumes)  # 24-hour average
            
            current_price = prices[-1][1]  # Latest price
            price_change_1h = (current_price - prices[-2][1]) / prices[-2][1] if len(prices) > 1 else 0
            price_change_24h = (current_price - prices[0][1]) / prices[0][1]
            
            # Calculate volume ratios for surge detection
            volume_ratio_recent = current_volume / recent_avg if recent_avg > 0 else 1
            volume_ratio_daily = current_volume / daily_avg if daily_avg > 0 else 1
            
            return {
                'current_volume': current_volume,
                'avg_volume_6h': recent_avg,
                'avg_volume_24h': daily_avg,
                'volume_ratio_recent': volume_ratio_recent,
                'volume_ratio_daily': volume_ratio_daily,
                'price_change_1h': price_change_1h,
                'price_change_24h': price_change_24h,
                'surge_detected': volume_ratio_recent > 3.0,  # 3x recent average
                'momentum': 'bullish' if price_change_1h > 0.01 else 'bearish' if price_change_1h < -0.01 else 'neutral'
            }
            
        except Exception as e:
            log_message(f"⚠️ Error analyzing crypto volume: {e}")
            return None
    
    def _symbol_to_coingecko_id(self, symbol):
        """
        🔄 SYMBOL CONVERSION for CoinGecko APIs
        
        Converts trading symbols (BTC/USDT) to CoinGecko IDs (bitcoin)
        """
        # Common symbol mappings
        symbol_map = {
            'BTC/USDT': 'bitcoin',
            'ETH/USDT': 'ethereum', 
            'SOL/USDT': 'solana',
            'ADA/USDT': 'cardano',
            'MATIC/USDT': 'polygon',
            'DOT/USDT': 'polkadot',
            'AVAX/USDT': 'avalanche-2',
            'LINK/USDT': 'chainlink',
            'UNI/USDT': 'uniswap',
            'LTC/USDT': 'litecoin',
            'BCH/USDT': 'bitcoin-cash',
            'XLM/USDT': 'stellar',
            'VET/USDT': 'vechain',
            'ALGO/USDT': 'algorand',
            'ICP/USDT': 'internet-computer'
        }
        
        return symbol_map.get(symbol, None)
    
    def _fetch_flow_data(self, symbol, timeframe):
        """
        Fetch exchange flow data using CoinGecko DEX API and Crypto API
        Priority: CoinGecko DEX API (free) → CryptoQuant (paid)
        """
        try:
            # Phase 1: Use CoinGecko DEX API for on-chain flow intelligence
            flows = self._fetch_coingecko_dex_flows(symbol)
            if flows:
                return flows
            
            # Phase 2: Fallback to market data analysis
            market_flows = self._analyze_market_flows_coingecko(symbol, timeframe)
            if market_flows:
                return market_flows
            
            # Phase 3: Mock data for development (remove in production)
            log_message("⚠️ Using mock flow data - implement API integration")
            return {
                'net_flow': -500000,  # Negative = outflow (bullish)
                'inflow': 2000000,
                'outflow': 2500000,
                'confidence': 0.5,
                'source': 'mock'
            }
            
        except Exception as e:
            log_message(f"⚠️ Error fetching flow data: {e}")
            return None
    
    def _fetch_stablecoin_data(self, stable, exchanges):
        """Mock stablecoin API call"""
        # TODO: Implement actual API calls
        return {
            'total_inflow': 3000000,  # $3M inflow
            'exchange_breakdown': {'binance': 1800000, 'coinbase': 1200000}
        }
    
    def _get_current_volume(self, symbol):
        """Get current trading volume using CoinGecko API"""
        try:
            # Use CoinGecko API for current volume data
            volume_data = self._fetch_coingecko_volume(symbol)
            if volume_data:
                return volume_data.get('current_volume', 0)
            
            # Fallback to existing exchange connection
            # TODO: Integrate with existing exchange connection
            return 150000000  # Mock volume
            
        except Exception as e:
            log_message(f"⚠️ Error fetching current volume: {e}")
            return 0
    
    def _get_average_volume(self, symbol, hours):
        """Get historical average volume"""
        # TODO: Integrate with existing data fetching
        return 30000000  # Mock average
    
    def _fetch_smart_money_data(self, symbol):
        """Mock Nansen-style smart money data"""
        # TODO: Implement Nansen API integration
        return {
            'accumulation_score': 0.8,
            'institutional_flows': -1000000,  # Negative = accumulation
            'sentiment': 'bullish',
            'confidence': 0.85
        }
    
    def _analyze_flow_signal(self, flow_data):
        """Determine bullish/bearish signal from flow data"""
        net_flow = flow_data.get('net_flow', 0)
        if net_flow < -self.SIGNIFICANT_FLOW_THRESHOLD:
            return 'bullish'  # Large outflows = accumulation
        elif net_flow > self.SIGNIFICANT_FLOW_THRESHOLD:
            return 'bearish'  # Large inflows = distribution
        return 'neutral'
    
    def _calculate_flow_confidence(self, flow_data):
        """Calculate confidence based on flow magnitude"""
        net_flow = abs(flow_data.get('net_flow', 0))
        return min(1.0, net_flow / (self.SIGNIFICANT_FLOW_THRESHOLD * 3))
    
    def _categorize_surge(self, ratio):
        """Categorize volume surge intensity"""
        if ratio >= 10:
            return 'extreme'
        elif ratio >= 5:
            return 'high'
        elif ratio >= 3:
            return 'moderate'
        elif ratio >= 2:
            return 'mild'
        return 'normal'
    
    def _analyze_smart_money_signal(self, data):
        """Analyze smart money activity for bullish/bearish signal"""
        accumulation = data.get('accumulation_score', 0)
        if accumulation > 0.7:
            return 'bullish'
        elif accumulation < 0.3:
            return 'bearish'
        return 'neutral'
    
    def _categorize_signal_strength(self, score):
        """Categorize overall on-chain signal strength"""
        if score >= 0.8:
            return 'very_strong'
        elif score >= 0.6:
            return 'strong'
        elif score >= 0.4:
            return 'moderate'
        elif score >= 0.2:
            return 'weak'
        return 'very_weak'
    
    def _is_cached(self, key):
        """Check if data is cached and still valid"""
        if key not in self.last_fetch_time:
            return False
        return (time.time() - self.last_fetch_time[key]) < self.cache_duration
    
    def _cache_data(self, key, data):
        """Cache data with timestamp"""
        self.last_fetch_time[key] = time.time()
        # TODO: Implement actual caching mechanism
    
    def _get_cached_data(self, key):
        """Retrieve cached data"""
        # TODO: Implement actual cache retrieval
        return None
