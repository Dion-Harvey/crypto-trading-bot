#!/usr/bin/env python3
"""
🌐 COMPREHENSIVE ALL-PAIRS TRADING SETUP
Upgrade bot to trade ALL 235 Binance US pairs with intelligent tier-based selection
"""

import json
import os
from datetime import datetime

def load_comprehensive_pairs():
    """Load the comprehensive pairs configuration"""
    try:
        with open('comprehensive_all_pairs_config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ Comprehensive pairs config not found. Run binance_us_pair_discovery.py first.")
        return None

def update_enhanced_config_with_all_pairs():
    """Update enhanced_config.json with ALL Binance US pairs"""
    
    # Load comprehensive pairs data
    comprehensive_config = load_comprehensive_pairs()
    if not comprehensive_config:
        return False
    
    # Load current enhanced config
    try:
        with open('enhanced_config.json', 'r') as f:
            current_config = json.load(f)
    except FileNotFoundError:
        print("❌ enhanced_config.json not found")
        return False
    
    # Create backup
    backup_filename = f"enhanced_config_backup_all_pairs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(backup_filename, 'w') as f:
        json.dump(current_config, f, indent=2)
    print(f"💾 Backup created: {backup_filename}")
    
    # Update configuration with ALL pairs
    current_config.update({
        "multi_currency_enabled": True,
        "currency_switching_enabled": True,
        "comprehensive_pairs_enabled": True,
        "total_supported_pairs": comprehensive_config["total_supported_pairs"],
        "supported_pairs": comprehensive_config["supported_pairs"],
        "usd_equivalent_pairs": comprehensive_config["usd_equivalent_pairs"],
        
        # Enhanced tier-based trading system
        "tier_system": comprehensive_config["tier_system"],
        
        # Updated risk management for comprehensive trading
        "risk_management": {
            **current_config.get("risk_management", {}),
            "max_concurrent_positions": 5,
            "position_size_per_pair": 0.10,  # 10% per pair
            "diversification_enabled": True,
            "tier_based_allocation": True,
            "sector_limits": comprehensive_config["risk_management"]["sector_limits"],
            
            # Enhanced opportunity scanning
            "comprehensive_scanning": {
                "enabled": True,
                "scan_frequency_seconds": 30,
                "opportunity_threshold": 25.0,  # Lower threshold for more opportunities
                "tier_priority_weights": {
                    "tier1": 1.0,
                    "tier2": 0.8,
                    "tier3": 0.6,
                    "tier4": 0.4
                }
            }
        },
        
        # Enhanced strategy parameters for comprehensive trading
        "strategy_parameters": {
            **current_config.get("strategy_parameters", {}),
            "comprehensive_mode": True,
            "multi_pair_confidence_threshold": 0.35,  # Lower threshold for more pairs
            "tier_confidence_adjustments": {
                "tier1": 1.0,    # No adjustment for tier 1
                "tier2": 0.95,   # Slightly lower threshold
                "tier3": 0.90,   # Lower threshold
                "tier4": 0.85    # Lowest threshold for emerging tokens
            },
            "dynamic_pair_selection": True,
            "max_active_monitoring": 50  # Monitor top 50 pairs actively
        }
    })
    
    # Save updated configuration
    with open('enhanced_config.json', 'w') as f:
        json.dump(current_config, f, indent=2)
    
    return True

def create_all_pairs_deployment_summary():
    """Create deployment summary for all-pairs system"""
    
    comprehensive_config = load_comprehensive_pairs()
    if not comprehensive_config:
        return
    
    summary = {
        "deployment_timestamp": datetime.now().isoformat(),
        "upgrade_type": "COMPREHENSIVE_ALL_PAIRS_SYSTEM",
        "previous_pairs": 55,
        "new_pairs": comprehensive_config["total_supported_pairs"],
        "improvement_factor": f"{comprehensive_config['total_supported_pairs'] / 55:.1f}x",
        
        "comprehensive_features": [
            f"✅ {comprehensive_config['total_supported_pairs']} total tradeable pairs",
            f"✅ Tier-based allocation system (4 tiers)",
            f"✅ {len(comprehensive_config['usd_equivalent_pairs'])} USD/USDT switching pairs",
            "✅ Enhanced opportunity scanning across ALL pairs",
            "✅ Intelligent tier-based risk management",
            "✅ Dynamic pair selection and monitoring",
            "✅ Sector diversification limits"
        ],
        
        "tier_breakdown": {
            "tier1_major": {
                "pairs": comprehensive_config["tier_system"]["tier1_major_cryptos"]["count"],
                "weight": "40%",
                "examples": comprehensive_config["tier_system"]["tier1_major_cryptos"]["pairs"][:5]
            },
            "tier2_popular": {
                "pairs": comprehensive_config["tier_system"]["tier2_popular_cryptos"]["count"],
                "weight": "30%",
                "examples": comprehensive_config["tier_system"]["tier2_popular_cryptos"]["pairs"][:5]
            },
            "tier3_defi": {
                "pairs": comprehensive_config["tier_system"]["tier3_defi_altcoins"]["count"],
                "weight": "20%",
                "examples": comprehensive_config["tier_system"]["tier3_defi_altcoins"]["pairs"][:5]
            },
            "tier4_emerging": {
                "pairs": comprehensive_config["tier_system"]["tier4_emerging_tokens"]["count"],
                "weight": "10%",
                "examples": comprehensive_config["tier_system"]["tier4_emerging_tokens"]["pairs"][:5]
            }
        },
        
        "risk_management": {
            "max_positions": 5,
            "per_pair_allocation": "10%",
            "total_exposure": "50% max",
            "diversification": "Tier-based limits enforced"
        }
    }
    
    # Save summary
    with open('all_pairs_deployment_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"📊 ALL-PAIRS DEPLOYMENT SUMMARY:")
    print(f"   🔄 Upgrade: {summary['previous_pairs']} → {summary['new_pairs']} pairs ({summary['improvement_factor']} improvement)")
    print(f"   🎯 Coverage: ALL available Binance US USDT/USD pairs")
    print(f"   🏗️ Architecture: 4-tier allocation system")
    print(f"   💱 Currency Switching: {len(comprehensive_config['usd_equivalent_pairs'])} pairs")
    print(f"   🛡️ Risk Management: 5 max positions, tier-based limits")

if __name__ == "__main__":
    print("🚀 COMPREHENSIVE ALL-PAIRS TRADING SYSTEM SETUP")
    print("=" * 60)
    
    # Update enhanced config with all pairs
    if update_enhanced_config_with_all_pairs():
        print("✅ Enhanced config updated with ALL pairs")
        
        # Create deployment summary
        create_all_pairs_deployment_summary()
        
        # Load and display final configuration
        with open('enhanced_config.json', 'r') as f:
            config = json.load(f)
        
        print(f"\n🎯 COMPREHENSIVE SYSTEM ACTIVATED!")
        print(f"   📊 Total Pairs: {config['total_supported_pairs']}")
        print(f"   🔄 Multi-Currency: {'✅' if config['multi_currency_enabled'] else '❌'}")
        print(f"   💱 Currency Switching: {'✅' if config['currency_switching_enabled'] else '❌'}")
        print(f"   🎪 Tier System: {'✅' if config.get('tier_system') else '❌'}")
        
        print(f"\n📋 TIER SUMMARY:")
        tier_system = config.get('tier_system', {})
        for tier_name, tier_data in tier_system.items():
            tier_display = tier_name.replace('_', ' ').title()
            print(f"   {tier_display}: {tier_data['count']} pairs ({tier_data['allocation_weight']*100:.0f}% weight)")
        
        print(f"\n🚀 READY TO TRADE ALL {config['total_supported_pairs']} BINANCE US PAIRS!")
        print(f"💡 Run 'python deploy_to_aws.py' to deploy the comprehensive system to AWS")
        
    else:
        print("❌ Failed to update configuration")
