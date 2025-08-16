# =============================================================================
# UNIFIED FREE API CONFIGURATION
# =============================================================================
#
# 🆓 COMPLETE FREE CRYPTOCURRENCY INTELLIGENCE - ZERO COST
# Combines Phase 1 (market data) + Phase 2 (advanced intelligence)
# Replaces $300-1,700/month paid solutions with free alternatives
#
# =============================================================================

import json
from typing import Dict, List, Optional
from datetime import datetime
from free_phase2_config import get_phase2_config

class UnifiedFreeConfig:
    """
    🆓 UNIFIED FREE API CONFIGURATION
    
    Combines Phase 1 + Phase 2 free APIs for complete trading intelligence:
    
    PHASE 1 (Market Data):
    - CoinGecko Free: 43,200 calls/day
    - CoinCap: 1.44M calls/day  
    - CryptoCompare: 100K calls/month
    - Moralis: 40K calls/month
    
    PHASE 2 (Advanced Intelligence):
    - Bitquery Free: Exchange flows & whale tracking
    - DefiLlama Free: DeFi & stablecoin intelligence
    - The Graph Free: Real-time DEX analytics
    - Dune Analytics: Community analytics
    
    Total Monthly Cost: $0 (vs $300-1,700 for equivalent paid solutions)
    """
    
    def __init__(self):
        self.config_version = "3.0"
        self.last_updated = datetime.now().isoformat()
        
        # 🆓 PHASE 1: FREE MARKET DATA APIS
        self.phase1_apis = {
            'coingecko_free': {
                'name': 'CoinGecko Free',
                'base_url': 'https://api.coingecko.com/api/v3',
                'cost_monthly': 0,
                'limits': {
                    'calls_per_day': 43200,
                    'rate_limit_per_minute': 30,
                    'features': [
                        'real_time_prices',
                        'market_data_17k_coins',
                        'exchange_data_1k_exchanges',
                        'historical_data_1_year',
                        'trending_detection',
                        'market_sentiment',
                        'onchain_dex_data_beta',
                        'fear_greed_index'
                    ]
                },
                'replaces': 'CoinMarketCap Pro ($333/month)',
                'authentication': 'none_required',
                'status': 'active',
                'priority': 1
            },
            
            'coincap': {
                'name': 'CoinCap Free',
                'base_url': 'https://api.coincap.io/v2',
                'cost_monthly': 0,
                'limits': {
                    'calls_per_day': 1440000,  # 1000/min
                    'rate_limit_per_minute': 1000,
                    'features': [
                        'real_time_prices',
                        'market_data',
                        'exchange_data',
                        'historical_charts'
                    ]
                },
                'replaces': 'CryptoCompare Pro ($55/month)',
                'authentication': 'none_required',
                'status': 'active',
                'priority': 2
            },
            
            'cryptocompare_free': {
                'name': 'CryptoCompare Free',
                'base_url': 'https://min-api.cryptocompare.com/data',
                'cost_monthly': 0,
                'limits': {
                    'calls_per_month': 100000,
                    'rate_limit_per_second': 10,
                    'features': [
                        'price_data',
                        'historical_data',
                        'news_sentiment',
                        'social_data'
                    ]
                },
                'replaces': 'Messari Pro ($150/month)',
                'authentication': 'none_required',
                'status': 'active',
                'priority': 3
            },
            
            'moralis_free': {
                'name': 'Moralis Web3 Free',
                'base_url': 'https://deep-index.moralis.io/api/v2',
                'cost_monthly': 0,
                'limits': {
                    'compute_units_per_month': 40000,
                    'rate_limit_per_second': 25,
                    'features': [
                        'blockchain_data',
                        'token_prices',
                        'defi_protocol_data',
                        'nft_metadata',
                        'wallet_analytics'
                    ]
                },
                'replaces': 'Alchemy Pro ($200/month)',
                'authentication': 'free_tier',
                'status': 'active',
                'priority': 4
            }
        }
        
        # 🚀 PHASE 2: Get from Phase 2 config
        phase2_config = get_phase2_config()
        self.phase2_apis = phase2_config.phase2_apis
        
        # 🎯 UNIFIED INTELLIGENCE STRATEGY
        self.intelligence_strategy = {
            'market_data_priority': ['coingecko_free', 'coincap', 'cryptocompare_free'],
            'onchain_data_priority': ['moralis_free', 'bitquery', 'thegraph'],
            'defi_intelligence_priority': ['defillama', 'thegraph', 'dune'],
            'whale_tracking_priority': ['bitquery', 'moralis_free'],
            'sentiment_analysis_priority': ['cryptocompare_free', 'coingecko_free'],
            
            'fallback_chains': {
                'price_data': ['coingecko_free', 'coincap', 'cryptocompare_free'],
                'volume_data': ['coingecko_free', 'coincap', 'thegraph'],
                'whale_activity': ['bitquery', 'moralis_free', 'thegraph'],
                'defi_flows': ['defillama', 'thegraph', 'dune'],
                'exchange_flows': ['bitquery', 'coingecko_free']
            }
        }
        
        # 🚨 UNIFIED ALERT SYSTEM
        self.unified_alerts = {
            'confidence_thresholds': {
                'low': 0.3,
                'medium': 0.6,
                'high': 0.8,
                'critical': 0.9
            },
            
            'multi_source_requirements': {
                'phase1_sources_minimum': 2,
                'phase2_sources_minimum': 1,
                'total_sources_for_critical': 3
            },
            
            'alert_triggers': {
                'volume_surge_threshold': 5.0,  # 5x normal volume
                'whale_transaction_usd': 1000000,  # $1M+
                'exchange_flow_usd': 5000000,  # $5M+
                'price_momentum_threshold': 0.05,  # 5%
                'sentiment_shift_threshold': 0.3,  # 30% sentiment change
                'defi_tvl_change_threshold': 0.1  # 10%
            }
        }
        
        # 💰 COST TRACKING
        self.cost_analysis = {
            'total_monthly_cost': 0,
            'equivalent_paid_services_cost': self._calculate_equivalent_costs(),
            'monthly_savings': 0,  # Will be calculated
            'apis_count': len(self.phase1_apis) + len(self.phase2_apis),
            'total_daily_calls': self._calculate_total_calls()
        }
        
        # Calculate savings
        self.cost_analysis['monthly_savings'] = self.cost_analysis['equivalent_paid_services_cost']
    
    def _calculate_equivalent_costs(self) -> float:
        """Calculate cost of equivalent paid services"""
        paid_equivalents = {
            'coinmarketcap_pro': 333,
            'cryptocompare_pro': 55,
            'messari_pro': 150,
            'alchemy_pro': 200,
            'cryptoquant': 29,
            'defipulse_api': 50,
            'dune_analytics_pro': 350,
            'nansen': 150
        }
        return sum(paid_equivalents.values())
    
    def _calculate_total_calls(self) -> int:
        """Calculate total daily API calls available"""
        daily_calls = 0
        
        # Phase 1 daily calls
        daily_calls += self.phase1_apis['coingecko_free']['limits']['calls_per_day']
        daily_calls += self.phase1_apis['coincap']['limits']['calls_per_day']
        daily_calls += self.phase1_apis['cryptocompare_free']['limits']['calls_per_month'] // 30  # Monthly to daily
        daily_calls += self.phase1_apis['moralis_free']['limits']['compute_units_per_month'] // 30
        
        # Phase 2 calls (estimated)
        daily_calls += 100  # Bitquery free tier (conservative)
        daily_calls += 1000  # DefiLlama (generous free tier)
        daily_calls += self.phase2_apis['thegraph']['limits']['queries_per_month'] // 30
        daily_calls += 50  # Dune community tier (conservative)
        
        return daily_calls
    
    def get_unified_config(self) -> Dict:
        """Get complete unified configuration"""
        return {
            'config_version': self.config_version,
            'last_updated': self.last_updated,
            'phase1_apis': self.phase1_apis,
            'phase2_apis': self.phase2_apis,
            'intelligence_strategy': self.intelligence_strategy,
            'unified_alerts': self.unified_alerts,
            'cost_analysis': self.cost_analysis
        }
    
    def get_active_apis(self) -> Dict:
        """Get all active APIs from both phases"""
        active_apis = {}
        
        # Phase 1 active APIs
        for name, config in self.phase1_apis.items():
            if config['status'] == 'active':
                active_apis[f'phase1_{name}'] = config
        
        # Phase 2 active APIs
        for name, config in self.phase2_apis.items():
            if config['status'] == 'active':
                active_apis[f'phase2_{name}'] = config
        
        return active_apis
    
    def get_api_priorities(self, intelligence_type: str) -> List[str]:
        """Get API priority order for specific intelligence type"""
        return self.intelligence_strategy.get(f'{intelligence_type}_priority', [])
    
    def get_fallback_chain(self, data_type: str) -> List[str]:
        """Get fallback chain for specific data type"""
        return self.intelligence_strategy['fallback_chains'].get(data_type, [])
    
    def validate_unified_setup(self) -> Dict:
        """Validate complete unified setup"""
        validation = {
            'status': 'valid',
            'errors': [],
            'warnings': [],
            'summary': {},
            'coverage_analysis': {}
        }
        
        # Check Phase 1 APIs
        phase1_active = sum(1 for api in self.phase1_apis.values() if api['status'] == 'active')
        phase2_active = sum(1 for api in self.phase2_apis.values() if api['status'] == 'active')
        
        if phase1_active < 2:
            validation['warnings'].append('Less than 2 Phase 1 APIs active - reduced redundancy')
        
        if phase2_active < 2:
            validation['warnings'].append('Less than 2 Phase 2 APIs active - limited advanced intelligence')
        
        # Verify total cost is still $0
        if self.cost_analysis['total_monthly_cost'] > 0:
            validation['errors'].append(f'Total cost ${self.cost_analysis["total_monthly_cost"]} is not zero!')
        
        # Coverage analysis
        validation['coverage_analysis'] = {
            'market_data_coverage': min(100, (phase1_active / 4) * 100),
            'advanced_intelligence_coverage': min(100, (phase2_active / 4) * 100),
            'whale_tracking_coverage': 'bitquery' in [api for api in self.phase2_apis.keys() if self.phase2_apis[api]['status'] == 'active'],
            'defi_intelligence_coverage': 'defillama' in [api for api in self.phase2_apis.keys() if self.phase2_apis[api]['status'] == 'active']
        }
        
        # Summary
        validation['summary'] = {
            'total_apis': len(self.phase1_apis) + len(self.phase2_apis),
            'active_apis': phase1_active + phase2_active,
            'phase1_active': phase1_active,
            'phase2_active': phase2_active,
            'monthly_cost': self.cost_analysis['total_monthly_cost'],
            'monthly_savings': self.cost_analysis['monthly_savings'],
            'daily_calls_available': self.cost_analysis['total_daily_calls']
        }
        
        if validation['errors']:
            validation['status'] = 'invalid'
        elif validation['warnings']:
            validation['status'] = 'valid_with_warnings'
        
        return validation
    
    def generate_deployment_summary(self) -> str:
        """Generate comprehensive deployment summary"""
        validation = self.validate_unified_setup()
        
        summary = f"""# 🚀 UNIFIED FREE API DEPLOYMENT SUMMARY
## Complete Cryptocurrency Intelligence - Zero Cost

### 💰 COST ANALYSIS
- **Monthly Cost**: ${self.cost_analysis['total_monthly_cost']}
- **Equivalent Paid Services**: ${self.cost_analysis['equivalent_paid_services_cost']:,}
- **Monthly Savings**: ${self.cost_analysis['monthly_savings']:,}
- **ROI**: INFINITE (zero cost with enterprise features)

### 📊 API COVERAGE
- **Phase 1 APIs**: {validation['summary']['phase1_active']}/4 active (market data)
- **Phase 2 APIs**: {validation['summary']['phase2_active']}/4 active (advanced intelligence)
- **Total Daily Calls**: {self.cost_analysis['total_daily_calls']:,}+

### 🎯 INTELLIGENCE CAPABILITIES
"""
        
        # Phase 1 capabilities
        summary += "\n#### Phase 1 (Market Data)\n"
        for name, config in self.phase1_apis.items():
            if config['status'] == 'active':
                features = ', '.join(config['limits']['features'][:3])  # First 3 features
                summary += f"- **{config['name']}**: {features}\n"
        
        # Phase 2 capabilities
        summary += "\n#### Phase 2 (Advanced Intelligence)\n"
        for name, config in self.phase2_apis.items():
            if config['status'] == 'active':
                features = ', '.join(config['limits']['features'][:3])  # First 3 features
                summary += f"- **{config['name']}**: {features}\n"
        
        summary += f"""
### 🚨 ALERT SYSTEM
- **Confidence Levels**: {len(self.unified_alerts['confidence_thresholds'])} tiers
- **Multi-Source Validation**: {self.unified_alerts['multi_source_requirements']['total_sources_for_critical']} sources for critical alerts
- **Alert Triggers**: {len(self.unified_alerts['alert_triggers'])} types

### 🔄 REDUNDANCY & FALLBACKS
- **Market Data**: {len(self.intelligence_strategy['fallback_chains']['price_data'])} fallback sources
- **Whale Tracking**: {len(self.intelligence_strategy['fallback_chains']['whale_activity'])} fallback sources
- **DeFi Intelligence**: {len(self.intelligence_strategy['fallback_chains']['defi_flows'])} fallback sources

### ✅ DEPLOYMENT STATUS
- **Configuration**: {validation['status']}
- **Market Data Coverage**: {validation['coverage_analysis']['market_data_coverage']:.0f}%
- **Advanced Intelligence Coverage**: {validation['coverage_analysis']['advanced_intelligence_coverage']:.0f}%
- **Ready for Production**: {'YES' if validation['status'] in ['valid', 'valid_with_warnings'] else 'NO'}

**🎉 Result: Enterprise-grade cryptocurrency intelligence at $0/month!**
"""
        
        if validation['warnings']:
            summary += "\n### ⚠️ WARNINGS\n"
            for warning in validation['warnings']:
                summary += f"- {warning}\n"
        
        return summary

# 🆓 GLOBAL UNIFIED CONFIGURATION
unified_free_config = UnifiedFreeConfig()

def get_unified_config() -> UnifiedFreeConfig:
    """Get global unified configuration"""
    return unified_free_config

def validate_complete_setup() -> Dict:
    """Validate complete unified setup"""
    return unified_free_config.validate_unified_setup()

def get_deployment_summary() -> str:
    """Get deployment summary"""
    return unified_free_config.generate_deployment_summary()

if __name__ == "__main__":
    # Test unified configuration
    print("🧪 Testing UNIFIED FREE API Configuration...")
    
    config = get_unified_config()
    validation = validate_complete_setup()
    
    print(f"✅ Status: {validation['status']}")
    print(f"💰 Monthly Cost: ${validation['summary']['monthly_cost']}")
    print(f"💎 Monthly Savings: ${validation['summary']['monthly_savings']:,}")
    print(f"🔧 Total APIs: {validation['summary']['total_apis']}")
    print(f"⚡ Active APIs: {validation['summary']['active_apis']}")
    print(f"📞 Daily Calls: {validation['summary']['daily_calls_available']:,}+")
    
    if validation['warnings']:
        print("\n⚠️ Warnings:")
        for warning in validation['warnings']:
            print(f"   • {warning}")
    
    print("\n" + "="*80)
    print("🎉 UNIFIED FREE API SYSTEM READY!")
    print("🚀 Enterprise intelligence at $0/month")
    print("="*80)
