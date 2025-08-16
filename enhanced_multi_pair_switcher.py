#!/usr/bin/env python3
"""
🎯 ENHANCED MULTI-PAIR SWITCHER
More aggressive pair switching based on opportunities across all supported pairs
"""

import json
import time
from datetime import datetime
from log_utils import log_message

class EnhancedMultiPairSwitcher:
    def __init__(self):
        self.supported_pairs = [
            "BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT", 
            "ADA/USDT", "DOGE/USDT", "XLM/USDT", "SUI/USDT",
            "SHIB/USDT", "HBAR/USDT", "AVAX/USDT", "DOT/USDT",
            "MATIC/USDT", "LINK/USDT", "UNI/USDT", "LTC/USDT"
        ]
        self.switch_thresholds = {
            'opportunity_score_diff': 25.0,  # Switch if new opportunity is 25+ points better
            'volume_surge_advantage': 100.0,  # Switch for 100%+ volume advantage
            'price_momentum_advantage': 3.0,  # Switch for 3%+ price momentum advantage
            'cooldown_override_score': 60.0   # Override switching cooldown for ultra-high scores
        }
        
    def should_switch_from_current_pair(self, current_pair, all_opportunities):
        """
        Enhanced logic to determine if bot should switch from current pair
        """
        if not all_opportunities:
            return False, None, "No opportunities available"
        
        # Find current pair opportunity
        current_opportunity = None
        for opp in all_opportunities:
            if opp.symbol == current_pair:
                current_opportunity = opp
                break
        
        if not current_opportunity:
            # Current pair not in opportunities - find best alternative
            best_opp = max(all_opportunities, key=lambda x: x.urgency_score)
            return True, best_opp.symbol, f"Current pair {current_pair} not in opportunities, switching to {best_opp.symbol}"
        
        # Find the best alternative opportunity
        alternatives = [opp for opp in all_opportunities if opp.symbol != current_pair]
        if not alternatives:
            return False, None, "No alternative opportunities"
        
        best_alternative = max(alternatives, key=lambda x: x.urgency_score)
        
        # Decision criteria
        score_advantage = best_alternative.urgency_score - current_opportunity.urgency_score
        volume_advantage = best_alternative.volume_change - current_opportunity.volume_change
        price_advantage = abs(best_alternative.price_change_1h) - abs(current_opportunity.price_change_1h)
        
        switch_reasons = []
        
        # Check score advantage
        if score_advantage >= self.switch_thresholds['opportunity_score_diff']:
            switch_reasons.append(f"Score advantage: {score_advantage:.1f} points")
        
        # Check volume advantage
        if volume_advantage >= self.switch_thresholds['volume_surge_advantage']:
            switch_reasons.append(f"Volume surge advantage: {volume_advantage:.1f}%")
        
        # Check price momentum advantage
        if price_advantage >= self.switch_thresholds['price_momentum_advantage']:
            switch_reasons.append(f"Price momentum advantage: {price_advantage:.2f}%")
        
        # Ultra-high score override
        if best_alternative.urgency_score >= self.switch_thresholds['cooldown_override_score']:
            switch_reasons.append(f"Ultra-high urgency score: {best_alternative.urgency_score:.1f}")
        
        should_switch = len(switch_reasons) > 0
        switch_reason = "; ".join(switch_reasons) if switch_reasons else "No significant advantage"
        
        return should_switch, best_alternative.symbol if should_switch else None, switch_reason
    
    def force_immediate_switch_to_best_opportunity(self, exchange):
        """
        Force immediate switch to the best opportunity across all pairs
        """
        try:
            from comprehensive_opportunity_scanner import run_immediate_comprehensive_scan
            log_message("🔍 ENHANCED SWITCHER: Scanning all pairs for best opportunity")
            
            all_opportunities = run_immediate_comprehensive_scan(exchange)
            
            if not all_opportunities:
                return None, "No opportunities detected across all pairs"
            
            # Filter for high-quality opportunities
            quality_opportunities = [
                opp for opp in all_opportunities 
                if opp.urgency_score >= 30.0  # Lowered threshold for more switches
            ]
            
            if not quality_opportunities:
                return None, f"No quality opportunities (highest score: {max(all_opportunities, key=lambda x: x.urgency_score).urgency_score:.1f})"
            
            # Find the absolute best opportunity
            best_opportunity = max(quality_opportunities, key=lambda x: x.urgency_score)
            
            log_message(f"🎯 BEST OPPORTUNITY: {best_opportunity.symbol}")
            log_message(f"   Score: {best_opportunity.urgency_score:.1f}")
            log_message(f"   Price: {best_opportunity.price_change_1h:+.2f}% (1h), {best_opportunity.price_change_24h:+.2f}% (24h)")
            log_message(f"   Volume: {best_opportunity.volume_change:+.1f}%")
            log_message(f"   Recommendation: {best_opportunity.recommendation}")
            
            return best_opportunity.symbol, f"Best opportunity: {best_opportunity.symbol} (score: {best_opportunity.urgency_score:.1f})"
            
        except Exception as e:
            log_message(f"⚠️ Enhanced switcher error: {e}")
            return None, f"Error: {e}"
    
    def update_config_to_new_pair(self, new_pair, reason):
        """
        Update enhanced_config.json to switch to new trading pair
        """
        try:
            with open('enhanced_config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            old_pair = config['trading']['symbol']
            config['trading']['symbol'] = new_pair
            config['trading']['last_pair_switch'] = datetime.now().isoformat()
            config['trading']['switch_reason'] = reason
            
            # Clear emergency mode if switching to different pair
            if config.get('emergency_switch', {}).get('target_symbol') != new_pair:
                config['emergency_switch'] = {
                    'activated': False,
                    'target_symbol': None,
                    'previous_symbol': old_pair,
                    'reason': f"Switched to better opportunity: {new_pair}",
                    'switched_at': datetime.now().isoformat(),
                    'urgency': 'NORMAL'
                }
            
            with open('enhanced_config.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            log_message(f"🔄 CONFIG UPDATED: {old_pair} → {new_pair}")
            log_message(f"   Reason: {reason}")
            return True
            
        except Exception as e:
            log_message(f"⚠️ Config update error: {e}")
            return False

def run_enhanced_pair_switching_test(exchange):
    """Test the enhanced pair switching system"""
    
    switcher = EnhancedMultiPairSwitcher()
    
    print("🎯 TESTING ENHANCED MULTI-PAIR SWITCHING")
    
    # Get current configuration
    try:
        with open('enhanced_config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        current_pair = config['trading']['symbol']
        print(f"📊 Current active pair: {current_pair}")
    except:
        current_pair = "XLM/USDT"
        print(f"📊 Default current pair: {current_pair}")
    
    # Force check for best opportunity
    best_pair, reason = switcher.force_immediate_switch_to_best_opportunity(exchange)
    
    if best_pair and best_pair != current_pair:
        print(f"🔄 SWITCH RECOMMENDED:")
        print(f"   From: {current_pair}")
        print(f"   To: {best_pair}")
        print(f"   Reason: {reason}")
        
        # Update configuration
        if switcher.update_config_to_new_pair(best_pair, reason):
            print(f"✅ Configuration updated successfully")
        else:
            print(f"❌ Failed to update configuration")
    elif best_pair == current_pair:
        print(f"✅ CURRENT PAIR OPTIMAL: {current_pair} is still the best choice")
        print(f"   Reason: {reason}")
    else:
        print(f"⚠️ NO SWITCH: {reason}")

if __name__ == "__main__":
    # This would be integrated into the main bot
    print("🎯 ENHANCED MULTI-PAIR SWITCHER")
    print("   This system makes the bot more aggressive about switching pairs")
    print("   when better opportunities are detected across all 16 supported pairs")
