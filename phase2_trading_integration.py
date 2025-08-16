#!/usr/bin/env python3
"""
🧠 PHASE 2 INTEGRATION MODULE
Connects existing blockchain intelligence APIs to trading decisions
"""

import time
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

# Import existing Phase 2 components
try:
    from free_phase2_api import FreePhase2Provider
    from onchain_data_provider import OnChainDataProvider
    PHASE2_AVAILABLE = True
except ImportError:
    PHASE2_AVAILABLE = False

class Phase2TradingIntegration:
    """
    🎯 PHASE 2 TRADING INTELLIGENCE INTEGRATION
    
    Connects blockchain intelligence APIs to trading decisions:
    - Exchange flow analysis → Position sizing signals
    - Whale activity → Risk management alerts
    - DeFi intelligence → Opportunity identification
    - On-chain metrics → Confidence scoring
    """
    
    def __init__(self):
        self.enabled = PHASE2_AVAILABLE
        self.cache = {}
        self.cache_duration = 300  # 5 minutes
        
        if self.enabled:
            self.phase2_provider = FreePhase2Provider()
            self.onchain_provider = OnChainDataProvider()
            logging.info("✅ Phase 2 Integration: Initialized successfully")
        else:
            logging.warning("⚠️ Phase 2 Integration: APIs not available, running without blockchain intelligence")
    
    def get_trading_enhancement(self, symbol: str, current_signal: Dict) -> Dict:
        """
        🎯 ENHANCE TRADING SIGNAL WITH PHASE 2 INTELLIGENCE
        
        Takes existing trading signal and enhances with blockchain intelligence
        """
        if not self.enabled:
            return self._create_fallback_enhancement(current_signal)
        
        try:
            # Get comprehensive Phase 2 intelligence
            intelligence = self._get_cached_intelligence(symbol)
            
            # Analyze intelligence for trading insights
            enhancement = self._analyze_trading_insights(symbol, intelligence, current_signal)
            
            return enhancement
            
        except Exception as e:
            logging.error(f"Phase 2 enhancement error for {symbol}: {e}")
            return self._create_fallback_enhancement(current_signal)
    
    def _get_cached_intelligence(self, symbol: str) -> Dict:
        """Get cached Phase 2 intelligence or fetch new data"""
        cache_key = f'intelligence_{symbol}'
        
        if cache_key in self.cache:
            data, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.cache_duration:
                return data
        
        # Fetch fresh intelligence
        intelligence = self.phase2_provider.get_comprehensive_phase2_intelligence(symbol)
        onchain_data = self.onchain_provider.get_exchange_flows(symbol)
        
        # Combine data sources
        combined_intelligence = {
            'symbol': symbol,
            'timestamp': time.time(),
            'phase2_data': intelligence,
            'onchain_flows': onchain_data,
        }
        
        # Cache the data
        self.cache[cache_key] = (combined_intelligence, time.time())
        
        return combined_intelligence
    
    def _analyze_trading_insights(self, symbol: str, intelligence: Dict, current_signal: Dict) -> Dict:
        """
        🔍 ANALYZE INTELLIGENCE FOR TRADING INSIGHTS
        
        Converts blockchain intelligence into trading enhancements
        """
        enhancement = {
            'symbol': symbol,
            'original_signal': current_signal,
            'phase2_enabled': True,
            'intelligence_summary': {},
            'trading_adjustments': {},
            'confidence_boost': 0.0,
            'risk_adjustment': 1.0,
            'position_size_multiplier': 1.0,
            'urgency_boost': 0.0,
            'recommendations': []
        }
        
        phase2_data = intelligence.get('phase2_data', {})
        onchain_flows = intelligence.get('onchain_flows', {})
        
        # 1. EXCHANGE FLOW ANALYSIS
        flow_insights = self._analyze_exchange_flows(phase2_data.get('exchange_flows', {}))
        if flow_insights:
            enhancement['intelligence_summary']['exchange_flows'] = flow_insights
            enhancement['confidence_boost'] += flow_insights.get('confidence_impact', 0)
            enhancement['recommendations'].extend(flow_insights.get('recommendations', []))
        
        # 2. WHALE ACTIVITY ANALYSIS
        whale_insights = self._analyze_whale_activity(phase2_data.get('whale_activity', {}))
        if whale_insights:
            enhancement['intelligence_summary']['whale_activity'] = whale_insights
            enhancement['risk_adjustment'] *= whale_insights.get('risk_multiplier', 1.0)
            enhancement['recommendations'].extend(whale_insights.get('recommendations', []))
        
        # 3. DEFI INTELLIGENCE ANALYSIS
        defi_insights = self._analyze_defi_intelligence(phase2_data.get('defi_intelligence', {}))
        if defi_insights:
            enhancement['intelligence_summary']['defi_metrics'] = defi_insights
            enhancement['position_size_multiplier'] *= defi_insights.get('size_multiplier', 1.0)
            enhancement['recommendations'].extend(defi_insights.get('recommendations', []))
        
        # 4. ON-CHAIN FLOW ANALYSIS
        onchain_insights = self._analyze_onchain_flows(onchain_flows)
        if onchain_insights:
            enhancement['intelligence_summary']['onchain_flows'] = onchain_insights
            enhancement['urgency_boost'] += onchain_insights.get('urgency_impact', 0)
            enhancement['recommendations'].extend(onchain_insights.get('recommendations', []))
        
        # 5. CALCULATE FINAL ADJUSTMENTS
        enhancement['trading_adjustments'] = self._calculate_final_adjustments(enhancement)
        
        return enhancement
    
    def _analyze_exchange_flows(self, exchange_flows: Dict) -> Optional[Dict]:
        """Analyze exchange flow data for trading insights"""
        if not exchange_flows:
            return None
        
        insights = {
            'flow_direction': 'neutral',
            'confidence_impact': 0.0,
            'recommendations': []
        }
        
        # Look for significant inflows/outflows
        net_flow = exchange_flows.get('net_flow_24h', 0)
        flow_volume = exchange_flows.get('total_volume_24h', 0)
        
        if abs(net_flow) > 1000000:  # $1M+ significant flow
            if net_flow < 0:  # Outflow (bullish)
                insights['flow_direction'] = 'outflow_bullish'
                insights['confidence_impact'] = 0.1
                insights['recommendations'].append("🔥 Major exchange outflow detected - accumulation pattern")
            else:  # Inflow (bearish)
                insights['flow_direction'] = 'inflow_bearish'  
                insights['confidence_impact'] = -0.05
                insights['recommendations'].append("⚠️ Major exchange inflow detected - potential selling pressure")
        
        return insights
    
    def _analyze_whale_activity(self, whale_activity: Dict) -> Optional[Dict]:
        """Analyze whale activity for trading insights"""
        if not whale_activity:
            return None
        
        insights = {
            'whale_sentiment': 'neutral',
            'risk_multiplier': 1.0,
            'recommendations': []
        }
        
        whale_transactions = whale_activity.get('large_transactions_24h', 0)
        whale_accumulation = whale_activity.get('accumulation_score', 0)
        
        if whale_transactions > 10:  # High whale activity
            if whale_accumulation > 0.6:  # Accumulating
                insights['whale_sentiment'] = 'accumulating'
                insights['risk_multiplier'] = 1.2  # Increase position size
                insights['recommendations'].append("🐋 Whale accumulation detected - increased confidence")
            elif whale_accumulation < 0.4:  # Distributing
                insights['whale_sentiment'] = 'distributing'
                insights['risk_multiplier'] = 0.8  # Reduce position size
                insights['recommendations'].append("⚠️ Whale distribution detected - reduce position size")
        
        return insights
    
    def _analyze_defi_intelligence(self, defi_intelligence: Dict) -> Optional[Dict]:
        """Analyze DeFi metrics for trading insights"""
        if not defi_intelligence:
            return None
        
        insights = {
            'defi_health': 'neutral',
            'size_multiplier': 1.0,
            'recommendations': []
        }
        
        tvl_change = defi_intelligence.get('tvl_change_24h', 0)
        lending_rates = defi_intelligence.get('lending_rate', 0)
        
        if tvl_change > 0.05:  # 5%+ TVL increase
            insights['defi_health'] = 'growing'
            insights['size_multiplier'] = 1.1
            insights['recommendations'].append("📈 DeFi TVL growing - ecosystem strength")
        elif tvl_change < -0.05:  # 5%+ TVL decrease
            insights['defi_health'] = 'declining'
            insights['size_multiplier'] = 0.9
            insights['recommendations'].append("📉 DeFi TVL declining - ecosystem weakness")
        
        return insights
    
    def _analyze_onchain_flows(self, onchain_flows: Dict) -> Optional[Dict]:
        """Analyze on-chain flow data for trading insights"""
        if not onchain_flows:
            return None
        
        insights = {
            'onchain_trend': 'neutral',
            'urgency_impact': 0.0,
            'recommendations': []
        }
        
        flow_velocity = onchain_flows.get('velocity_increase', 0)
        active_addresses = onchain_flows.get('active_addresses_change', 0)
        
        if flow_velocity > 2.0:  # 2x+ velocity increase
            insights['onchain_trend'] = 'accelerating'
            insights['urgency_impact'] = 5.0
            insights['recommendations'].append("⚡ On-chain velocity surge - immediate attention needed")
        
        if active_addresses > 0.2:  # 20%+ address increase
            insights['onchain_trend'] = 'adoption_growing'
            insights['urgency_impact'] = 2.0
            insights['recommendations'].append("👥 Active address growth - network adoption increasing")
        
        return insights
    
    def _calculate_final_adjustments(self, enhancement: Dict) -> Dict:
        """Calculate final trading adjustments based on all intelligence"""
        
        # Start with original signal
        original_confidence = enhancement['original_signal'].get('confidence', 0.5)
        
        # Apply Phase 2 enhancements
        enhanced_confidence = original_confidence + enhancement['confidence_boost']
        enhanced_confidence = max(0.0, min(1.0, enhanced_confidence))  # Clamp 0-1
        
        # Position sizing
        position_multiplier = enhancement['position_size_multiplier'] * enhancement['risk_adjustment']
        position_multiplier = max(0.5, min(2.0, position_multiplier))  # Clamp 0.5-2.0x
        
        # Urgency scoring
        base_urgency = enhancement['original_signal'].get('urgency_score', 0)
        enhanced_urgency = base_urgency + enhancement['urgency_boost']
        
        return {
            'enhanced_confidence': enhanced_confidence,
            'confidence_change': enhanced_confidence - original_confidence,
            'position_size_multiplier': position_multiplier,
            'enhanced_urgency_score': enhanced_urgency,
            'urgency_change': enhancement['urgency_boost'],
            'total_recommendations': len(enhancement['recommendations'])
        }
    
    def _create_fallback_enhancement(self, current_signal: Dict) -> Dict:
        """Create fallback enhancement when Phase 2 is not available"""
        return {
            'symbol': current_signal.get('symbol', 'Unknown'),
            'original_signal': current_signal,
            'phase2_enabled': False,
            'intelligence_summary': {'status': 'Phase 2 APIs not available'},
            'trading_adjustments': {
                'enhanced_confidence': current_signal.get('confidence', 0.5),
                'confidence_change': 0.0,
                'position_size_multiplier': 1.0,
                'enhanced_urgency_score': current_signal.get('urgency_score', 0),
                'urgency_change': 0.0,
                'total_recommendations': 0
            },
            'recommendations': ['Phase 2 intelligence not available - using standard signals only']
        }
    
    def get_status_summary(self) -> Dict:
        """Get Phase 2 integration status summary"""
        return {
            'phase2_enabled': self.enabled,
            'apis_available': PHASE2_AVAILABLE,
            'cache_entries': len(self.cache),
            'last_update': datetime.now().isoformat(),
            'status': 'Active' if self.enabled else 'Disabled - APIs not available'
        }

def test_phase2_integration():
    """Test Phase 2 integration functionality"""
    print("🧠 TESTING PHASE 2 INTEGRATION")
    print("=" * 50)
    
    integration = Phase2TradingIntegration()
    
    # Test status
    status = integration.get_status_summary()
    print(f"Phase 2 Status: {status['status']}")
    print(f"APIs Available: {status['apis_available']}")
    
    # Test with sample signal
    sample_signal = {
        'symbol': 'BTC/USDT',
        'action': 'BUY',
        'confidence': 0.7,
        'urgency_score': 25.0,
        'reason': 'Multi-timeframe alignment'
    }
    
    print(f"\n🎯 Testing enhancement for {sample_signal['symbol']}")
    enhancement = integration.get_trading_enhancement('BTC', sample_signal)
    
    adjustments = enhancement['trading_adjustments']
    print(f"Original Confidence: {sample_signal['confidence']:.3f}")
    print(f"Enhanced Confidence: {adjustments['enhanced_confidence']:.3f}")
    print(f"Confidence Change: {adjustments['confidence_change']:+.3f}")
    print(f"Position Multiplier: {adjustments['position_size_multiplier']:.2f}x")
    print(f"Recommendations: {adjustments['total_recommendations']}")
    
    for i, rec in enumerate(enhancement['recommendations'][:3], 1):
        print(f"  {i}. {rec}")
    
    print(f"\n✅ Phase 2 Integration test complete!")

if __name__ == "__main__":
    test_phase2_integration()
