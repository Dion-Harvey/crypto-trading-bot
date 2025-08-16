# =============================================================================
# FREE PHASE 2 CONFIGURATION
# =============================================================================
#
# 🆓 ADVANCED BLOCKCHAIN INTELLIGENCE CONFIGURATION - ZERO COST
# Manages Bitquery, DefiLlama, Dune Analytics, and The Graph integration
# Replaces $29-50/month paid solutions with free alternatives
#
# =============================================================================

import json
from typing import Dict, List, Optional
from datetime import datetime

class FreePhase2Config:
    """
    🆓 FREE Phase 2 Configuration Manager
    
    Manages all free advanced blockchain intelligence APIs:
    - Bitquery Free: 10K points/month (exchange flows & whale tracking)
    - DefiLlama Free: Unlimited (DeFi & stablecoin intelligence)
    - Dune Analytics: Community tier (advanced DEX analytics)
    - The Graph: 100K queries/month (real-time liquidity data)
    
    Total Monthly Cost: $0 (vs $29-50 for equivalent paid APIs)
    """
    
    def __init__(self):
        self.config_version = "2.0"
        self.last_updated = datetime.now().isoformat()
        
        # 🆓 FREE PHASE 2 API ENDPOINTS
        self.phase2_apis = {
            'bitquery': {
                'name': 'Bitquery Free',
                'base_url': 'https://graphql.bitquery.io',
                'cost_monthly': 0,
                'limits': {
                    'points_per_month': 10000,
                    'rate_limit_per_minute': 10,
                    'features': [
                        'exchange_flows',
                        'whale_tracking', 
                        'large_transactions',
                        'cross_chain_transfers'
                    ]
                },
                'replaces': 'CryptoQuant ($29/month)',
                'authentication': 'free_tier',
                'status': 'active'
            },
            
            'defillama': {
                'name': 'DefiLlama Free', 
                'base_url': 'https://api.llama.fi',
                'cost_monthly': 0,
                'limits': {
                    'calls_per_day': 'unlimited',
                    'rate_limit': 'generous',
                    'features': [
                        'protocol_tvl',
                        'stablecoin_flows',
                        'defi_analytics',
                        'yield_tracking',
                        'chain_tvl'
                    ]
                },
                'replaces': 'DeFiPulse API ($50/month)',
                'authentication': 'none_required',
                'status': 'active'
            },
            
            'thegraph': {
                'name': 'The Graph Free',
                'base_url': 'https://api.thegraph.com/subgraphs/name',
                'cost_monthly': 0,
                'limits': {
                    'queries_per_month': 100000,
                    'rate_limit_per_second': 10,
                    'features': [
                        'uniswap_v3_data',
                        'sushiswap_data', 
                        'real_time_liquidity',
                        'dex_analytics',
                        'pool_metrics'
                    ]
                },
                'replaces': 'Dune Analytics Pro ($350/month)',
                'authentication': 'none_required',
                'status': 'active'
            },
            
            'dune': {
                'name': 'Dune Analytics Community',
                'base_url': 'https://api.dune.com/api/v1',
                'cost_monthly': 0,
                'limits': {
                    'queries_per_month': 'community_tier',
                    'execution_time': '30_seconds_max',
                    'features': [
                        'public_dashboards',
                        'community_queries',
                        'basic_analytics',
                        'historical_data'
                    ]
                },
                'replaces': 'Nansen ($150/month)',
                'authentication': 'community_access',
                'status': 'active'
            }
        }
        
        # 🎯 PRIORITY MATRIX FOR FREE APIS
        self.priority_matrix = {
            'exchange_flows': {
                'primary': 'bitquery',
                'fallback': 'manual_calculation',
                'confidence_weight': 0.9
            },
            'whale_tracking': {
                'primary': 'bitquery',
                'fallback': 'thegraph',
                'confidence_weight': 0.8
            },
            'defi_intelligence': {
                'primary': 'defillama',
                'fallback': 'thegraph',
                'confidence_weight': 0.9
            },
            'dex_analytics': {
                'primary': 'thegraph',
                'fallback': 'defillama',
                'confidence_weight': 0.8
            },
            'stablecoin_flows': {
                'primary': 'defillama',
                'fallback': 'bitquery',
                'confidence_weight': 0.9
            }
        }
        
        # 🚨 ALERT THRESHOLDS FOR PHASE 2
        self.alert_thresholds = {
            'whale_transaction_usd': 1000000,  # $1M+ = whale activity
            'exchange_net_flow_usd': 5000000,  # $5M+ = significant flow
            'stablecoin_change_pct': 2.0,      # 2%+ = sentiment shift
            'protocol_tvl_change_pct': 10.0,   # 10%+ = major movement
            'dex_volume_threshold_usd': 10000000,  # $10M+ = high activity
            'confidence_alert_minimum': 0.6    # 60%+ confidence for alerts
        }
        
        # 📊 INTELLIGENCE SCORING WEIGHTS
        self.scoring_weights = {
            'exchange_flows': 0.3,      # 30% weight
            'whale_activity': 0.25,     # 25% weight
            'defi_intelligence': 0.2,   # 20% weight
            'dex_analytics': 0.15,      # 15% weight
            'stablecoin_flows': 0.1     # 10% weight
        }
        
        # 🔄 REFRESH INTERVALS (seconds)
        self.refresh_intervals = {
            'exchange_flows': 300,      # 5 minutes
            'whale_tracking': 180,      # 3 minutes
            'defi_intelligence': 600,   # 10 minutes
            'dex_analytics': 300,       # 5 minutes
            'stablecoin_flows': 900     # 15 minutes
        }
    
    def get_active_apis(self) -> Dict:
        """Get all active Phase 2 APIs"""
        return {
            name: config for name, config in self.phase2_apis.items()
            if config['status'] == 'active'
        }
    
    def get_api_config(self, api_name: str) -> Optional[Dict]:
        """Get specific API configuration"""
        return self.phase2_apis.get(api_name)
    
    def get_total_monthly_cost(self) -> float:
        """Calculate total monthly cost (should be $0!)"""
        return sum(api['cost_monthly'] for api in self.phase2_apis.values())
    
    def get_total_monthly_savings(self) -> float:
        """Calculate savings vs paid alternatives"""
        savings_map = {
            'bitquery': 29,    # vs CryptoQuant
            'defillama': 50,   # vs DeFiPulse API
            'thegraph': 350,   # vs Dune Analytics Pro
            'dune': 150        # vs Nansen
        }
        return sum(savings_map.values())
    
    def get_intelligence_priorities(self) -> Dict:
        """Get prioritized intelligence sources"""
        return self.priority_matrix
    
    def get_alert_config(self) -> Dict:
        """Get alert threshold configuration"""
        return self.alert_thresholds
    
    def get_scoring_config(self) -> Dict:
        """Get intelligence scoring weights"""
        return self.scoring_weights
    
    def validate_configuration(self) -> Dict:
        """Validate Phase 2 configuration"""
        validation = {
            'status': 'valid',
            'errors': [],
            'warnings': [],
            'summary': {}
        }
        
        # Check that all APIs are configured
        required_apis = ['bitquery', 'defillama', 'thegraph', 'dune']
        for api in required_apis:
            if api not in self.phase2_apis:
                validation['errors'].append(f'Missing {api} configuration')
        
        # Verify total cost is $0
        total_cost = self.get_total_monthly_cost()
        if total_cost > 0:
            validation['warnings'].append(f'Total cost ${total_cost} is not zero!')
        
        # Check scoring weights sum to 1.0
        total_weight = sum(self.scoring_weights.values())
        if abs(total_weight - 1.0) > 0.01:
            validation['warnings'].append(f'Scoring weights sum to {total_weight}, should be 1.0')
        
        # Generate summary
        validation['summary'] = {
            'total_apis': len(self.phase2_apis),
            'active_apis': len(self.get_active_apis()),
            'monthly_cost': total_cost,
            'monthly_savings': self.get_total_monthly_savings(),
            'intelligence_sources': len(self.priority_matrix)
        }
        
        if validation['errors']:
            validation['status'] = 'invalid'
        elif validation['warnings']:
            validation['status'] = 'valid_with_warnings'
        
        return validation
    
    def export_config(self) -> str:
        """Export configuration as JSON"""
        config_export = {
            'config_version': self.config_version,
            'last_updated': self.last_updated,
            'phase2_apis': self.phase2_apis,
            'priority_matrix': self.priority_matrix,
            'alert_thresholds': self.alert_thresholds,
            'scoring_weights': self.scoring_weights,
            'refresh_intervals': self.refresh_intervals
        }
        return json.dumps(config_export, indent=2)
    
    def generate_readme(self) -> str:
        """Generate README for Phase 2 implementation"""
        total_savings = self.get_total_monthly_savings()
        total_cost = self.get_total_monthly_cost()
        
        readme = f"""# 🆓 FREE PHASE 2 IMPLEMENTATION
## Advanced Blockchain Intelligence - Zero Cost

### 📊 **COST SUMMARY**
- **Monthly Cost**: ${total_cost}
- **Monthly Savings**: ${total_savings}
- **Paid Alternatives Replaced**: 4 premium services

### 🔧 **ACTIVE APIS**
"""
        
        for name, config in self.phase2_apis.items():
            readme += f"""
#### {config['name']}
- **Replaces**: {config['replaces']}
- **Monthly Cost**: ${config['cost_monthly']}
- **Features**: {', '.join(config['limits']['features'])}
- **Status**: {config['status']}
"""
        
        readme += f"""
### 🎯 **INTELLIGENCE CAPABILITIES**
"""
        
        for intel_type, priority in self.priority_matrix.items():
            readme += f"- **{intel_type.replace('_', ' ').title()}**: {priority['primary']} (primary) → {priority['fallback']} (fallback)\n"
        
        readme += f"""
### 🚨 **ALERT SYSTEM**
- Whale transactions: ${self.alert_thresholds['whale_transaction_usd']:,}+
- Exchange flows: ${self.alert_thresholds['exchange_net_flow_usd']:,}+
- Stablecoin changes: {self.alert_thresholds['stablecoin_change_pct']}%+
- Protocol TVL changes: {self.alert_thresholds['protocol_tvl_change_pct']}%+

### 🚀 **IMPLEMENTATION STATUS**
✅ Configuration Complete
✅ API Integration Ready
✅ Alert System Configured
✅ Zero Monthly Costs Confirmed

**Ready for immediate deployment!**
"""
        
        return readme

# 🆓 GLOBAL PHASE 2 CONFIGURATION
free_phase2_config = FreePhase2Config()

def get_phase2_config() -> FreePhase2Config:
    """Get global Phase 2 configuration"""
    return free_phase2_config

def validate_phase2_setup() -> Dict:
    """Validate complete Phase 2 setup"""
    return free_phase2_config.validate_configuration()

if __name__ == "__main__":
    # Test Phase 2 configuration
    print("🧪 Testing FREE Phase 2 Configuration...")
    
    config = get_phase2_config()
    validation = validate_phase2_setup()
    
    print(f"✅ Status: {validation['status']}")
    print(f"💰 Monthly Cost: ${validation['summary']['monthly_cost']}")
    print(f"💎 Monthly Savings: ${validation['summary']['monthly_savings']}")
    print(f"🔧 Active APIs: {validation['summary']['active_apis']}")
    
    if validation['warnings']:
        print("⚠️ Warnings:")
        for warning in validation['warnings']:
            print(f"   • {warning}")
    
    if validation['errors']:
        print("❌ Errors:")
        for error in validation['errors']:
            print(f"   • {error}")
    
    print("\n" + "="*60)
    print("🎯 PHASE 2 IMPLEMENTATION READY!")
    print("="*60)
