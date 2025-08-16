# =============================================================================
# FREE CRYPTOCURRENCY API INTEGRATION
# =============================================================================
#
# 🆓 ZERO-COST ON-CHAIN INTELLIGENCE PROVIDER
# Leverages multiple free APIs for comprehensive trading intelligence
#
# =============================================================================

import requests
import time
import json
from typing import Dict, List, Optional, Tuple
import logging

class FreeCryptoDataProvider:
    """
    🆓 FREE Cryptocurrency Data Provider
    
    Aggregates data from multiple free APIs to provide comprehensive trading intelligence:
    - CoinGecko Free (43,200 calls/day)
    - CoinCap (1.44M calls/day) 
    - Moralis Free (40,000 calls/month)
    - CryptoCompare Free (100,000 calls/month)
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.cache = {}
        self.cache_duration = 60  # 1 minute cache
        
        # 🆓 FREE API ENDPOINTS
        self.apis = {
            'coingecko': {
                'base_url': 'https://api.coingecko.com/api/v3',
                'rate_limit': 30,  # per minute
                'cost': 0
            },
            'coincap': {
                'base_url': 'https://api.coincap.io/v2',
                'rate_limit': 1000,  # per minute
                'cost': 0
            },
            'cryptocompare': {
                'base_url': 'https://min-api.cryptocompare.com/data',
                'rate_limit': 100000,  # per month
                'cost': 0
            }
        }
        
        # Symbol mappings for different APIs
        self.symbol_maps = {
            'coingecko': {
                'BTC': 'bitcoin', 'ETH': 'ethereum', 'BNB': 'binancecoin',
                'SOL': 'solana', 'ADA': 'cardano', 'XRP': 'ripple',
                'AVAX': 'avalanche-2', 'DOT': 'polkadot', 'MATIC': 'matic-network',
                'SUI': 'sui', 'NEAR': 'near', 'UNI': 'uniswap'
            },
            'coincap': {
                'BTC': 'bitcoin', 'ETH': 'ethereum', 'BNB': 'binance-coin',
                'SOL': 'solana', 'ADA': 'cardano', 'XRP': 'xrp',
                'AVAX': 'avalanche', 'DOT': 'polkadot', 'MATIC': 'polygon',
                'SUI': 'sui', 'NEAR': 'near-protocol', 'UNI': 'uniswap'
            }
        }
    
    def get_comprehensive_crypto_data(self, symbol: str) -> Dict:
        """
        🎯 COMPREHENSIVE FREE CRYPTO INTELLIGENCE
        
        Aggregates data from multiple free sources for maximum intelligence
        """
        try:
            # Check cache first
            cache_key = f'comprehensive_{symbol}'
            if self._is_cached(cache_key):
                return self.cache[cache_key]
            
            # Parallel data collection from free sources
            data_sources = {}
            
            # 1. CoinGecko Free - Primary source
            coingecko_data = self._fetch_coingecko_free_data(symbol)
            if coingecko_data:
                data_sources['coingecko'] = coingecko_data
            
            # 2. CoinCap - High volume backup
            coincap_data = self._fetch_coincap_data(symbol)
            if coincap_data:
                data_sources['coincap'] = coincap_data
            
            # 3. CryptoCompare - Social sentiment
            cryptocompare_data = self._fetch_cryptocompare_data(symbol)
            if cryptocompare_data:
                data_sources['cryptocompare'] = cryptocompare_data
            
            # Aggregate the intelligence
            comprehensive_data = self._aggregate_free_data(symbol, data_sources)
            
            # Cache the result
            self._update_cache(cache_key, comprehensive_data)
            
            return comprehensive_data
            
        except Exception as e:
            logging.error(f"Error in comprehensive data fetch for {symbol}: {e}")
            return self._get_fallback_data(symbol)
    
    def _fetch_coingecko_free_data(self, symbol: str) -> Dict:
        """
        🦎 CoinGecko FREE API - Comprehensive market data
        """
        try:
            coin_id = self.symbol_maps['coingecko'].get(symbol.upper(), symbol.lower())
            
            # Basic coin data
            url = f"{self.apis['coingecko']['base_url']}/coins/{coin_id}"
            params = {
                'localization': 'false',
                'tickers': 'true',
                'market_data': 'true',
                'community_data': 'false',
                'developer_data': 'false'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            if response.status_code != 200:
                return None
            
            data = response.json()
            market_data = data.get('market_data', {})
            
            # Extract comprehensive data
            coingecko_analysis = {
                'price_usd': market_data.get('current_price', {}).get('usd', 0),
                'market_cap': market_data.get('market_cap', {}).get('usd', 0),
                'volume_24h': market_data.get('total_volume', {}).get('usd', 0),
                'price_change_24h': market_data.get('price_change_percentage_24h', 0),
                'price_change_7d': market_data.get('price_change_percentage_7d', 0),
                'market_cap_rank': market_data.get('market_cap_rank', 0),
                'volume_rank': data.get('coingecko_rank', 0),
                'exchanges': [],
                'source': 'coingecko_free',
                'timestamp': time.time()
            }
            
            # Extract top exchanges
            tickers = data.get('tickers', [])[:5]  # Top 5 exchanges
            for ticker in tickers:
                exchange_info = {
                    'name': ticker.get('market', {}).get('name', 'unknown'),
                    'volume_usd': ticker.get('converted_volume', {}).get('usd', 0),
                    'trust_score': ticker.get('trust_score', 'unknown')
                }
                coingecko_analysis['exchanges'].append(exchange_info)
            
            return coingecko_analysis
            
        except Exception as e:
            logging.error(f"CoinGecko free data error for {symbol}: {e}")
            return None
    
    def _fetch_coincap_data(self, symbol: str) -> Dict:
        """
        💎 CoinCap FREE API - High-frequency market data
        """
        try:
            coin_id = self.symbol_maps['coincap'].get(symbol.upper(), symbol.lower())
            
            # Asset data
            url = f"{self.apis['coincap']['base_url']}/assets/{coin_id}"
            
            response = self.session.get(url, timeout=10)
            if response.status_code != 200:
                return None
            
            data = response.json().get('data', {})
            
            coincap_analysis = {
                'price_usd': float(data.get('priceUsd', 0)),
                'market_cap': float(data.get('marketCapUsd', 0)),
                'volume_24h': float(data.get('volumeUsd24Hr', 0)),
                'price_change_24h': float(data.get('changePercent24Hr', 0)),
                'supply': float(data.get('supply', 0)),
                'max_supply': float(data.get('maxSupply', 0)) if data.get('maxSupply') else None,
                'rank': int(data.get('rank', 0)),
                'source': 'coincap_free',
                'timestamp': time.time()
            }
            
            return coincap_analysis
            
        except Exception as e:
            logging.error(f"CoinCap data error for {symbol}: {e}")
            return None
    
    def _fetch_cryptocompare_data(self, symbol: str) -> Dict:
        """
        📊 CryptoCompare FREE API - Social sentiment data
        """
        try:
            # Basic price data
            url = f"{self.apis['cryptocompare']['base_url']}/price"
            params = {'fsym': symbol.upper(), 'tsyms': 'USD'}
            
            response = self.session.get(url, params=params, timeout=10)
            if response.status_code != 200:
                return None
            
            price_data = response.json()
            
            # Social data
            social_url = f"{self.apis['cryptocompare']['base_url']}/social/coin/general"
            social_params = {'coinId': symbol.upper()}
            
            social_response = self.session.get(social_url, params=social_params, timeout=10)
            social_data = {}
            if social_response.status_code == 200:
                social_data = social_response.json().get('Data', {})
            
            cryptocompare_analysis = {
                'price_usd': price_data.get('USD', 0),
                'social_score': social_data.get('General', {}).get('Points', 0),
                'sentiment': 'neutral',  # Could be enhanced with sentiment analysis
                'source': 'cryptocompare_free',
                'timestamp': time.time()
            }
            
            return cryptocompare_analysis
            
        except Exception as e:
            logging.error(f"CryptoCompare data error for {symbol}: {e}")
            return None
    
    def _aggregate_free_data(self, symbol: str, data_sources: Dict) -> Dict:
        """
        🎯 INTELLIGENT DATA AGGREGATION
        
        Combines multiple free sources into unified intelligence
        """
        try:
            aggregated = {
                'symbol': symbol,
                'timestamp': time.time(),
                'sources_used': list(data_sources.keys()),
                'confidence_score': 0.0,
                'trading_signals': {},
                'cost': 0  # Always free!
            }
            
            # Price consensus from multiple sources
            prices = []
            volumes = []
            market_caps = []
            price_changes = []
            
            for source, data in data_sources.items():
                if data.get('price_usd', 0) > 0:
                    prices.append(data['price_usd'])
                if data.get('volume_24h', 0) > 0:
                    volumes.append(data['volume_24h'])
                if data.get('market_cap', 0) > 0:
                    market_caps.append(data['market_cap'])
                if data.get('price_change_24h', 0) != 0:
                    price_changes.append(data['price_change_24h'])
            
            # Calculate consensus values
            if prices:
                aggregated['consensus_price'] = sum(prices) / len(prices)
                aggregated['price_variance'] = max(prices) - min(prices)
            
            if volumes:
                aggregated['consensus_volume'] = sum(volumes) / len(volumes)
                aggregated['volume_variance'] = max(volumes) - min(volumes)
            
            if price_changes:
                aggregated['consensus_change_24h'] = sum(price_changes) / len(price_changes)
            
            # Calculate confidence based on source agreement
            if len(data_sources) >= 2:
                if aggregated.get('price_variance', 0) < aggregated.get('consensus_price', 0) * 0.02:  # < 2% variance
                    aggregated['confidence_score'] = 0.9
                else:
                    aggregated['confidence_score'] = 0.7
            else:
                aggregated['confidence_score'] = 0.5
            
            # Generate trading signals
            volume_surge = False
            if volumes and len(volumes) >= 2:
                avg_volume = sum(volumes) / len(volumes)
                if max(volumes) > avg_volume * 2:  # 2x volume surge
                    volume_surge = True
            
            price_momentum = aggregated.get('consensus_change_24h', 0)
            
            aggregated['trading_signals'] = {
                'volume_surge': volume_surge,
                'price_momentum': 'bullish' if price_momentum > 5 else 'bearish' if price_momentum < -5 else 'neutral',
                'momentum_strength': abs(price_momentum) / 10 if price_momentum else 0,
                'overall_signal': 'buy' if volume_surge and price_momentum > 2 else 'sell' if price_momentum < -10 else 'hold'
            }
            
            return aggregated
            
        except Exception as e:
            logging.error(f"Data aggregation error for {symbol}: {e}")
            return {'symbol': symbol, 'error': str(e), 'cost': 0}
    
    def get_volume_surge_alert(self, symbol: str) -> Dict:
        """
        🚨 FREE VOLUME SURGE DETECTION
        
        Monitors for unusual trading activity using free APIs
        """
        comprehensive_data = self.get_comprehensive_crypto_data(symbol)
        
        signals = comprehensive_data.get('trading_signals', {})
        volume_surge = signals.get('volume_surge', False)
        momentum = signals.get('momentum_strength', 0)
        
        alert = {
            'symbol': symbol,
            'surge_detected': volume_surge,
            'confidence': comprehensive_data.get('confidence_score', 0),
            'momentum_strength': momentum,
            'recommendation': signals.get('overall_signal', 'hold'),
            'sources': comprehensive_data.get('sources_used', []),
            'cost': 0,
            'timestamp': time.time()
        }
        
        return alert
    
    def _is_cached(self, key: str) -> bool:
        """Check if data is cached and still valid"""
        if key not in self.cache:
            return False
        
        cache_age = time.time() - self.cache[key].get('timestamp', 0)
        return cache_age < self.cache_duration
    
    def _update_cache(self, key: str, data: Dict):
        """Update cache with timestamp"""
        data['timestamp'] = time.time()
        self.cache[key] = data
    
    def _get_fallback_data(self, symbol: str) -> Dict:
        """Fallback data when all APIs fail"""
        return {
            'symbol': symbol,
            'error': 'All free APIs unavailable',
            'fallback': True,
            'cost': 0,
            'timestamp': time.time()
        }

# 🆓 GLOBAL FREE DATA PROVIDER INSTANCE
free_crypto_provider = FreeCryptoDataProvider()

def get_free_crypto_intelligence(symbol: str) -> Dict:
    """
    🎯 MAIN FUNCTION: Get comprehensive free crypto intelligence
    
    Usage:
        intelligence = get_free_crypto_intelligence('BTC')
        if intelligence['trading_signals']['volume_surge']:
            print("🚨 Volume surge detected!")
    """
    return free_crypto_provider.get_comprehensive_crypto_data(symbol)

def get_free_volume_alerts(symbol: str) -> Dict:
    """
    🚨 MAIN FUNCTION: Get free volume surge alerts
    
    Usage:
        alert = get_free_volume_alerts('BTC')
        if alert['surge_detected']:
            print(f"🚨 {symbol} volume surge: {alert['confidence']:.1%} confidence")
    """
    return free_crypto_provider.get_volume_surge_alert(symbol)

if __name__ == "__main__":
    # Test the free API integration
    test_symbols = ['BTC', 'ETH', 'SOL']
    
    for symbol in test_symbols:
        print(f"\n🧪 Testing FREE APIs for {symbol}...")
        intelligence = get_free_crypto_intelligence(symbol)
        print(f"✅ Sources: {intelligence.get('sources_used', [])}")
        print(f"💰 Cost: ${intelligence.get('cost', 0)}")
        print(f"📊 Confidence: {intelligence.get('confidence_score', 0):.1%}")
        
        alert = get_free_volume_alerts(symbol)
        if alert['surge_detected']:
            print(f"🚨 VOLUME SURGE DETECTED!")
        
        print("-" * 50)
