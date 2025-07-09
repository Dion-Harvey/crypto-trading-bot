"""
Price Jump Detection Module
Detects significant price movements and triggers immediate analysis
"""

import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import pandas as pd

@dataclass
class PricePoint:
    """Represents a price point with timestamp"""
    timestamp: float
    price: float
    
@dataclass
class PriceJump:
    """Represents a detected price jump"""
    start_price: float
    end_price: float
    change_pct: float
    duration_seconds: float
    direction: str  # 'UP' or 'DOWN'
    timestamp: float
    
class PriceJumpDetector:
    """Detects significant price movements in real-time"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.price_history: List[PricePoint] = []
        self.max_history_size = 100
        
        # Configuration from enhanced_config.json
        self.enabled = config.get('system', {}).get('price_jump_detection', {}).get('enabled', True)
        self.threshold_pct = config.get('system', {}).get('price_jump_detection', {}).get('threshold_pct', 0.5)
        self.detection_window = config.get('system', {}).get('price_jump_detection', {}).get('detection_window_seconds', 60)
        self.override_cooldown = config.get('system', {}).get('price_jump_detection', {}).get('override_cooldown', True)
        
        # Recent jumps tracking
        self.recent_jumps: List[PriceJump] = []
        self.jump_cooldown_seconds = 30  # Don't detect same jump repeatedly
        
        print(f"🔍 Price Jump Detection initialized:")
        print(f"   Enabled: {self.enabled}")
        print(f"   Threshold: {self.threshold_pct}%")
        print(f"   Detection Window: {self.detection_window}s")
        print(f"   Override Cooldown: {self.override_cooldown}")
    
    def add_price_point(self, price: float) -> Optional[PriceJump]:
        """Add a new price point and check for jumps"""
        if not self.enabled:
            return None
            
        current_time = time.time()
        
        # Add to history
        self.price_history.append(PricePoint(current_time, price))
        
        # Trim history to prevent memory issues
        if len(self.price_history) > self.max_history_size:
            self.price_history = self.price_history[-self.max_history_size:]
        
        # Clean old jumps
        self._clean_old_jumps()
        
        # Check for price jumps
        return self._detect_jump(price, current_time)
    
    def _detect_jump(self, current_price: float, current_time: float) -> Optional[PriceJump]:
        """Detect if current price represents a significant jump"""
        if len(self.price_history) < 2:
            return None
        
        # Find the oldest price point within detection window
        window_start = current_time - self.detection_window
        relevant_points = [p for p in self.price_history if p.timestamp >= window_start]
        
        if len(relevant_points) < 2:
            return None
        
        # Get the earliest price in the window
        earliest_point = min(relevant_points, key=lambda p: p.timestamp)
        
        # Calculate price change
        price_change = (current_price - earliest_point.price) / earliest_point.price
        change_pct = price_change * 100
        
        # Check if this meets our jump threshold
        if abs(change_pct) >= self.threshold_pct:
            # Check if we haven't detected this jump recently
            if not self._is_duplicate_jump(current_price, current_time):
                direction = 'UP' if change_pct > 0 else 'DOWN'
                duration = current_time - earliest_point.timestamp
                
                jump = PriceJump(
                    start_price=earliest_point.price,
                    end_price=current_price,
                    change_pct=change_pct,
                    duration_seconds=duration,
                    direction=direction,
                    timestamp=current_time
                )
                
                # Store this jump
                self.recent_jumps.append(jump)
                
                return jump
        
        return None
    
    def _is_duplicate_jump(self, current_price: float, current_time: float) -> bool:
        """Check if we've already detected this jump recently"""
        for jump in self.recent_jumps:
            if current_time - jump.timestamp < self.jump_cooldown_seconds:
                # Similar price range and recent timing suggests same jump
                price_similarity = abs(current_price - jump.end_price) / jump.end_price
                if price_similarity < 0.005:  # Within 0.5% price similarity
                    return True
        return False
    
    def _clean_old_jumps(self):
        """Remove old jumps from tracking"""
        current_time = time.time()
        cutoff_time = current_time - (self.jump_cooldown_seconds * 3)  # Keep 3x cooldown period
        self.recent_jumps = [j for j in self.recent_jumps if j.timestamp > cutoff_time]
    
    def get_recent_jumps(self, minutes: int = 5) -> List[PriceJump]:
        """Get all jumps from the last N minutes"""
        cutoff_time = time.time() - (minutes * 60)
        return [j for j in self.recent_jumps if j.timestamp > cutoff_time]
    
    def should_override_cooldown(self, jump: PriceJump) -> bool:
        """Determine if this jump should override trade cooldown"""
        if not self.override_cooldown:
            return False
        
        # Override for significant jumps
        if abs(jump.change_pct) >= 1.0:  # 1% or more
            return True
        
        # Override for rapid jumps
        if abs(jump.change_pct) >= 0.7 and jump.duration_seconds <= 30:
            return True
        
        return False
    
    def get_jump_analysis(self, jump: PriceJump) -> Dict:
        """Get detailed analysis of a price jump"""
        return {
            'magnitude': abs(jump.change_pct),
            'direction': jump.direction,
            'speed': abs(jump.change_pct) / (jump.duration_seconds / 60),  # %/minute
            'urgency': 'HIGH' if abs(jump.change_pct) >= 1.0 else 'MEDIUM',
            'override_cooldown': self.should_override_cooldown(jump),
            'start_price': jump.start_price,
            'end_price': jump.end_price,
            'duration': jump.duration_seconds
        }
    
    def get_status(self) -> Dict:
        """Get current detector status"""
        return {
            'enabled': self.enabled,
            'threshold_pct': self.threshold_pct,
            'detection_window': self.detection_window,
            'recent_jumps_count': len(self.recent_jumps),
            'last_5min_jumps': len(self.get_recent_jumps(5)),
            'price_history_size': len(self.price_history)
        }

# Global instance
_detector = None

def get_price_jump_detector(config: Dict) -> PriceJumpDetector:
    """Get or create global price jump detector instance"""
    global _detector
    if _detector is None:
        _detector = PriceJumpDetector(config)
    return _detector

def detect_price_jump(price: float, config: Dict) -> Optional[PriceJump]:
    """Convenience function to detect price jumps"""
    detector = get_price_jump_detector(config)
    return detector.add_price_point(price)
