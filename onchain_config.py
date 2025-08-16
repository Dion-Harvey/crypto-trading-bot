# =============================================================================
# ON-CHAIN DATA CONFIGURATION
# =============================================================================
#
# 🆓 FREE CRYPTOCURRENCY API CONFIGURATION
# Phase 1: 100% FREE APIs - No cost, no credit card required!
# Phase 2: Optional paid upgrades for advanced features
#
# =============================================================================

# 🆓 PHASE 1: COMPLETELY FREE APIS (Cost: $0/month)
ONCHAIN_CONFIG = {
    
    # 🦎 CoinGecko FREE - THE CHAMPION (NO COST!)
    'coingecko_free': {
        'enabled': True,    # ✅ Ready to use immediately!
        'api_key': None,    # ✅ NO API KEY REQUIRED for free tier
        'base_url': 'https://api.coingecko.com/api/v3',
        'dex_api_url': 'https://api.coingecko.com/api/v3/onchain',  # ✅ FREE ON-CHAIN DEX DATA!
        'rate_limit': 30,   # requests per minute = 43,200/day (FREE!)
        'cost_per_month': 0,
        'features': {
            'crypto_api': True,      # ✅ 17,000+ cryptocurrencies
            'dex_api': True,         # ✅ 200+ blockchains, 1,600+ DEXes
            'global_data': True,     # ✅ Market sentiment, fear & greed
            'trending': True,        # ✅ Trending coins detection
            'exchanges': True,       # ✅ 1,000+ exchange data
            'historical': True,      # ✅ 1 year historical data
            'volume_data': True,     # ✅ Real-time volume analysis
            'market_cap': True       # ✅ Market cap & price changes
        },
        'priority': 'primary'  # Primary free data source
    },
    
    # 💎 CoinCap FREE - BACKUP POWERHOUSE (NO COST!)
    'coincap_free': {
        'enabled': True,    # ✅ Ready to use immediately!
        'api_key': None,    # ✅ NO API KEY REQUIRED
        'base_url': 'https://api.coincap.io/v2',
        'rate_limit': 1000, # requests per minute = 1.44M/day (FREE!)
        'cost_per_month': 0,
        'features': {
            'prices': True,         # ✅ Real-time prices
            'market_data': True,    # ✅ Market cap, volume
            'exchanges': True,      # ✅ Exchange data
            'historical': True      # ✅ Historical charts
        },
        'priority': 'backup'  # Backup/validation source
    },
    
    # 🌐 Moralis FREE - ON-CHAIN SPECIALIST (NO COST!)
    'moralis_free': {
        'enabled': True,    # ✅ Ready with free account
        'api_key': '',      # Add your FREE Moralis API key
        'base_url': 'https://deep-index.moralis.io/api/v2.2',
        'rate_limit': 40000, # requests per month (FREE!)
        'cost_per_month': 0,
        'features': {
            'onchain_data': True,   # ✅ Real-time blockchain data
            'token_prices': True,   # ✅ Cross-chain token prices
            'defi_metrics': True,   # ✅ DeFi protocol data
            'wallet_analytics': True # ✅ Wallet transaction analysis
        },
        'priority': 'onchain'  # Specialized on-chain intelligence
    },
    
    # 📊 CryptoCompare FREE - COMPREHENSIVE DATA (NO COST!)
    'cryptocompare_free': {
        'enabled': True,    # ✅ Ready to use immediately!
        'api_key': None,    # ✅ NO API KEY REQUIRED for basic tier
        'base_url': 'https://min-api.cryptocompare.com/data',
        'rate_limit': 100000, # requests per month (FREE!)
        'cost_per_month': 0,
        'features': {
            'prices': True,         # ✅ Real-time prices
            'historical': True,     # ✅ Historical data
            'news': True,           # ✅ Crypto news sentiment
            'social': True          # ✅ Social sentiment data
        },
        'priority': 'secondary'  # Secondary data source
    },
    
    # 💰 PAID OPTIONS (Phase 2 - Optional upgrades)
    # CryptoQuant (Basic Plan - $29/month) - OPTIONAL
    'cryptoquant': {
        'enabled': False,  # Optional upgrade
        'api_key': '',     # Add your CryptoQuant API key
        'base_url': 'https://api.cryptoquant.com/v1',
        'rate_limit': 10,  # requests per minute
        'cost_per_month': 29,
        'priority': 'premium'  # Premium exchange flows
    },
    
    
    # 🏆 PREMIUM OPTIONS (Phase 3 - Advanced features)
    'nansen': {
        'enabled': False,   # Premium subscription required
        'api_key': '',      # Nansen API key
        'base_url': 'https://api.nansen.ai/v1',
        'rate_limit': 1000, # requests per month (varies by plan)
        'cost_per_month': 150,
        'priority': 'premium'
    },
    
    'glassnode': {
        'enabled': False,   # Professional plan required
        'api_key': '',      # Glassnode API key
        'base_url': 'https://api.glassnode.com/v1',
        'rate_limit': 1000, # requests per month
        'cost_per_month': 199,
        'priority': 'premium'
    }
}

# 🆓 FREE API PRIORITY (Zero cost strategy)
DATA_SOURCE_PRIORITY = {
    'exchange_flows': ['coingecko_free', 'moralis_free', 'coincap_free'],      # CoinGecko DEX API leads
    'stablecoin_flows': ['coingecko_free', 'moralis_free', 'cryptocompare_free'], # Multi-source validation
    'volume_data': ['coingecko_free', 'coincap_free', 'cryptocompare_free'],   # High-frequency volume data
    'dex_analytics': ['coingecko_free', 'moralis_free'],                       # Specialized DEX intelligence
    'smart_money': ['moralis_free', 'coingecko_free'],                         # On-chain wallet analytics
    'defi_metrics': ['moralis_free', 'coingecko_free'],                        # DeFi protocol analysis
    'market_sentiment': ['coingecko_free', 'cryptocompare_free'],              # Sentiment & social data
    'price_data': ['coingecko_free', 'coincap_free', 'cryptocompare_free'],    # Multi-source price validation
    'trending_analysis': ['coingecko_free', 'cryptocompare_free']              # Trend detection
}

# 🎯 FREE TIER CAPACITY ANALYSIS
FREE_TIER_CAPACITY = {
    'daily_api_calls': 43200 + 1440000 + 3333 + 3333,  # CoinGecko + CoinCap + Moralis + CryptoCompare
    'monthly_cost': 0,
    'features_available': [
        'real_time_prices', 'volume_analysis', 'dex_data', 'market_sentiment',
        'trending_detection', 'exchange_data', 'historical_data', 'onchain_intelligence'
    ],
    'coverage': {
        'cryptocurrencies': 17000,
        'exchanges': 1000,
        'blockchains': 200,
        'dex_protocols': 1600
    }
}

# Alert Thresholds (from document analysis)
ALERT_THRESHOLDS = {
    'significant_flow': 1000000,      # $1M+ exchange flows
    'stablecoin_surge': 5000000,      # $5M+ stablecoin inflows  
    'volume_surge_multiplier': 5.0,   # 5x normal volume
    'whale_threshold': 1000000,       # $1M+ whale transactions
    'confidence_threshold': 0.7       # Minimum confidence for alerts
}

# Integration Settings
INTEGRATION_SETTINGS = {
    'cache_duration': 60,             # 1 minute cache
    'retry_attempts': 3,              # API retry attempts
    'timeout_seconds': 10,            # API timeout
    'fallback_enabled': True,         # Use backup data sources
    'debug_logging': True             # Enhanced logging for development
}

# Phase 1 Implementation Priority
PHASE_1_APIS = ['coingecko']          # Start with free APIs
PHASE_2_APIS = ['cryptoquant', 'coinapi']  # Add basic paid APIs
PHASE_3_APIS = ['nansen', 'glassnode']     # Premium analytics

def get_active_providers():
    """Return list of currently enabled providers"""
    return [provider for provider, config in ONCHAIN_CONFIG.items() 
            if config.get('enabled', False)]

def get_api_key(provider):
    """Safely get API key for provider"""
    return ONCHAIN_CONFIG.get(provider, {}).get('api_key', '')

def should_use_provider(provider):
    """Check if provider should be used based on configuration"""
    config = ONCHAIN_CONFIG.get(provider, {})
    return config.get('enabled', False) and config.get('api_key', '') != ''
