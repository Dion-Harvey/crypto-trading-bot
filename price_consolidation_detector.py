"""
Price Consolidation Detection System
Detects when price has stabilized after major movements for optimal entry timing
"""

import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class ConsolidationSignal:
    """Represents a price consolidation detection result"""
    is_consolidating: bool
    consolidation_strength: float  # 0.0 to 1.0
    consolidation_duration: int    # seconds
    price_range_pct: float        # percentage range during consolidation
    volume_trend: str             # 'increasing', 'decreasing', 'stable'
    entry_recommendation: str     # 'WAIT', 'GOOD_ENTRY', 'EXCELLENT_ENTRY'
    reasons: List[str]

class PriceConsolidationDetector:
    """
    Detects price consolidation periods after major movements
    Helps identify optimal entry points when price stabilizes
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.price_history = []
        self.volume_history = []
        self.max_history_size = 200
        
        # Consolidation thresholds
        self.min_consolidation_time = 120    # 2 minutes minimum
        self.max_price_range_pct = 0.5       # 0.5% max range for tight consolidation
        self.loose_price_range_pct = 1.0     # 1.0% max range for loose consolidation
        
        print("🔍 Price Consolidation Detector initialized")
        print(f"   Min consolidation time: {self.min_consolidation_time}s")
        print(f"   Tight range threshold: {self.max_price_range_pct}%")
        print(f"   Loose range threshold: {self.loose_price_range_pct}%")
    
    def add_price_point(self, price: float, volume: float = None) -> ConsolidationSignal:
        """Add a new price point and check for consolidation"""
        current_time = time.time()
        
        # Add to history
        self.price_history.append({
            'price': price,
            'timestamp': current_time
        })
        
        if volume is not None:
            self.volume_history.append({
                'volume': volume,
                'timestamp': current_time
            })
        
        # Trim history
        self._trim_history()
        
        # Detect consolidation
        return self._detect_consolidation(price, current_time)
    
    def _trim_history(self):
        """Remove old data points"""
        current_time = time.time()
        cutoff_time = current_time - 3600  # Keep 1 hour
        
        self.price_history = [
            p for p in self.price_history 
            if p['timestamp'] > cutoff_time
        ][-self.max_history_size:]
        
        self.volume_history = [
            v for v in self.volume_history 
            if v['timestamp'] > cutoff_time
        ][-self.max_history_size:]
    
    def _detect_consolidation(self, current_price: float, current_time: float) -> ConsolidationSignal:
        """Detect if price is currently consolidating"""
        
        if len(self.price_history) < 10:
            return ConsolidationSignal(
                is_consolidating=False,
                consolidation_strength=0.0,
                consolidation_duration=0,
                price_range_pct=0.0,
                volume_trend='unknown',
                entry_recommendation='WAIT',
                reasons=['Insufficient price history']
            )
        
        # Analyze different time windows
        consolidation_5m = self._analyze_consolidation_window(300)   # 5 minutes
        consolidation_10m = self._analyze_consolidation_window(600)  # 10 minutes
        consolidation_15m = self._analyze_consolidation_window(900)  # 15 minutes
        
        # Find the best consolidation signal
        best_consolidation = max(
            [consolidation_5m, consolidation_10m, consolidation_15m],
            key=lambda x: x['strength'] if x['is_consolidating'] else 0
        )
        
        # Analyze volume trend if available
        volume_trend = self._analyze_volume_trend()
        
        # Generate recommendation
        entry_recommendation = self._generate_entry_recommendation(
            best_consolidation, volume_trend
        )
        
        return ConsolidationSignal(
            is_consolidating=best_consolidation['is_consolidating'],
            consolidation_strength=best_consolidation['strength'],
            consolidation_duration=best_consolidation['duration'],
            price_range_pct=best_consolidation['range_pct'],
            volume_trend=volume_trend,
            entry_recommendation=entry_recommendation,
            reasons=best_consolidation['reasons']
        )
    
    def _analyze_consolidation_window(self, window_seconds: int) -> Dict:
        """Analyze consolidation in a specific time window"""
        current_time = time.time()
        window_start = current_time - window_seconds
        
        # Get prices in this window
        window_prices = [
            p['price'] for p in self.price_history 
            if p['timestamp'] >= window_start
        ]
        
        if len(window_prices) < 5:
            return {
                'is_consolidating': False,
                'strength': 0.0,
                'duration': 0,
                'range_pct': 0.0,
                'reasons': [f'Insufficient data for {window_seconds}s window']
            }
        
        # Calculate price range
        high_price = max(window_prices)
        low_price = min(window_prices)
        avg_price = sum(window_prices) / len(window_prices)
        range_pct = ((high_price - low_price) / avg_price) * 100
        
        # Check for consolidation
        is_tight_consolidation = range_pct <= self.max_price_range_pct
        is_loose_consolidation = range_pct <= self.loose_price_range_pct
        
        # Calculate consolidation strength
        strength = 0.0
        reasons = []
        
        if is_tight_consolidation:
            strength = 0.9 - (range_pct / self.max_price_range_pct) * 0.4  # 0.5-0.9
            reasons.append(f'Tight consolidation: {range_pct:.2f}% range in {window_seconds//60}m')
        elif is_loose_consolidation:
            strength = 0.5 - (range_pct / self.loose_price_range_pct) * 0.3  # 0.2-0.5
            reasons.append(f'Loose consolidation: {range_pct:.2f}% range in {window_seconds//60}m')
        else:
            reasons.append(f'No consolidation: {range_pct:.2f}% range too wide')
        
        # Check price stability (low volatility)
        if len(window_prices) >= 10:
            price_changes = []
            for i in range(1, len(window_prices)):
                change = abs((window_prices[i] - window_prices[i-1]) / window_prices[i-1])
                price_changes.append(change)
            
            avg_change = sum(price_changes) / len(price_changes)
            if avg_change < 0.002:  # Less than 0.2% average change
                strength += 0.1
                reasons.append('Low volatility detected')
        
        # Duration bonus
        actual_duration = min(window_seconds, current_time - self.price_history[0]['timestamp'])
        if actual_duration >= self.min_consolidation_time:
            duration_bonus = min(0.1, (actual_duration - self.min_consolidation_time) / 600 * 0.1)
            strength += duration_bonus
            reasons.append(f'Sufficient duration: {actual_duration:.0f}s')
        
        return {
            'is_consolidating': is_tight_consolidation or is_loose_consolidation,
            'strength': min(1.0, strength),
            'duration': int(actual_duration),
            'range_pct': range_pct,
            'reasons': reasons
        }
    
    def _analyze_volume_trend(self) -> str:
        """Analyze volume trend during recent period"""
        if len(self.volume_history) < 5:
            return 'unknown'
        
        recent_volumes = [v['volume'] for v in self.volume_history[-10:]]
        if len(recent_volumes) < 5:
            return 'unknown'
        
        # Compare first half vs second half
        mid_point = len(recent_volumes) // 2
        early_avg = sum(recent_volumes[:mid_point]) / mid_point
        late_avg = sum(recent_volumes[mid_point:]) / (len(recent_volumes) - mid_point)
        
        change_ratio = late_avg / early_avg if early_avg > 0 else 1.0
        
        if change_ratio > 1.2:
            return 'increasing'
        elif change_ratio < 0.8:
            return 'decreasing'
        else:
            return 'stable'
    
    def _generate_entry_recommendation(self, consolidation: Dict, volume_trend: str) -> str:
        """Generate entry timing recommendation"""
        if not consolidation['is_consolidating']:
            return 'WAIT'
        
        strength = consolidation['strength']
        duration = consolidation['duration']
        
        # Excellent entry conditions
        if (strength >= 0.7 and 
            duration >= 180 and  # 3+ minutes
            volume_trend in ['decreasing', 'stable']):  # Volume cooling off
            return 'EXCELLENT_ENTRY'
        
        # Good entry conditions
        elif (strength >= 0.4 and 
              duration >= self.min_consolidation_time):
            return 'GOOD_ENTRY'
        
        # Otherwise wait
        else:
            return 'WAIT'
    
    def get_consolidation_status(self) -> Dict:
        """Get current consolidation status summary"""
        if not self.price_history:
            return {'status': 'No data'}
        
        latest = self.price_history[-1]
        return {
            'status': 'Active',
            'latest_price': latest['price'],
            'price_points': len(self.price_history),
            'volume_points': len(self.volume_history),
            'last_update': latest['timestamp']
        }

def create_consolidation_detector(config: Dict) -> PriceConsolidationDetector:
    """Factory function to create consolidation detector"""
    return PriceConsolidationDetector(config)
