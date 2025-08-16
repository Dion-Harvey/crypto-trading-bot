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

@dataclass  # type: ignore
class PriceJump:
    """Represents a detected price jump"""
    start_price: float
    end_price: float
    change_pct: float
    duration_seconds: float
    direction: str  # 'UP' or 'DOWN'
    timestamp: float

class PriceJumpDetector:
    """Enhanced multi-timeframe price movement detector for both spikes and trends"""

    def __init__(self, config: Dict):
        self.config = config
        self.price_history: List[PricePoint] = []
        self.max_history_size = 500  # Increased for longer trend tracking

        # Multi-timeframe detection windows
        self.detection_windows = {
            'spike': 60,        # 1 minute for rapid spikes
            'short_trend': 300, # 5 minutes for short trends
            'medium_trend': 900, # 15 minutes for medium trends
            'long_trend': 1800   # 30 minutes for sustained movements
        }

        # Multi-threshold system
        self.thresholds = {
            'spike': 0.5,       # 0.5% for rapid spikes
            'short_trend': 0.8, # 0.8% for 5-minute trends
            'medium_trend': 1.2, # 1.2% for 15-minute trends
            'long_trend': 1.8    # 1.8% for 30-minute trends
        }

        # Configuration from enhanced_config.json
        self.enabled = config.get('system', {}).get('price_jump_detection', {}).get('enabled', True)
        self.override_cooldown = config.get('system', {}).get('price_jump_detection', {}).get('override_cooldown', True)

        # Recent jumps tracking with categories
        self.recent_jumps: List[PriceJump] = []
        self.jump_cooldown_seconds = 30

        # Trend tracking
        self.trend_state = {
            'direction': None,  # 'UP', 'DOWN', or None
            'strength': 0.0,    # 0.0 to 1.0
            'duration': 0.0,    # seconds
            'start_price': None,
            'peak_change': 0.0
        }

        print(f"🔍 Enhanced Multi-Timeframe Price Detection initialized:")
        print(f"   Enabled: {self.enabled}")
        print(f"   Spike Detection: {self.thresholds['spike']}% in {self.detection_windows['spike']}s")
        print(f"   Short Trend: {self.thresholds['short_trend']}% in {self.detection_windows['short_trend']}s")
        print(f"   Medium Trend: {self.thresholds['medium_trend']}% in {self.detection_windows['medium_trend']}s")
        print(f"   Long Trend: {self.thresholds['long_trend']}% in {self.detection_windows['long_trend']}s")
        print(f"   Override Cooldown: {self.override_cooldown}")

    def add_price_point(self, price: float) -> Optional[PriceJump]:
        """Add a new price point and check for multi-timeframe movements"""
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

        # Update trend state
        self._update_trend_state(price, current_time)

        # Check for movements across all timeframes
        detected_jump = self._detect_multi_timeframe_movement(price, current_time)

        return detected_jump

    def _detect_multi_timeframe_movement(self, current_price: float, current_time: float) -> Optional[PriceJump]:
        """Detect movements across multiple timeframes"""
        if len(self.price_history) < 2:
            return None

        best_jump = None
        best_urgency = 0

        # Check each timeframe
        for timeframe, window_seconds in self.detection_windows.items():
            threshold = self.thresholds[timeframe]

            # Find relevant price points within this window
            window_start = current_time - window_seconds
            relevant_points = [p for p in self.price_history if p.timestamp >= window_start]

            if len(relevant_points) < 2:
                continue

            # Get the earliest price in the window
            earliest_point = min(relevant_points, key=lambda p: p.timestamp)

            # Calculate price change
            price_change = (current_price - earliest_point.price) / earliest_point.price
            change_pct = price_change * 100

            # Check if this meets the threshold for this timeframe
            if abs(change_pct) >= threshold:
                # Check if we haven't detected this movement recently
                if not self._is_duplicate_jump(current_price, current_time, timeframe):
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

                    # Add timeframe metadata
                    jump.timeframe = timeframe
                    jump.threshold_met = threshold

                    # Calculate urgency (higher for shorter timeframes with bigger moves)
                    urgency = self._calculate_urgency(jump, timeframe)

                    # Keep the most urgent jump
                    if urgency > best_urgency:
                        best_jump = jump
                        best_urgency = urgency

        # Store the best jump if found
        if best_jump:
            best_jump.urgency_score = best_urgency
            self.recent_jumps.append(best_jump)

        return best_jump

    def _calculate_urgency(self, jump: PriceJump, timeframe: str) -> float:
        """Calculate urgency score for a jump"""
        # Base urgency on magnitude and speed
        magnitude_factor = abs(jump.change_pct) / self.thresholds[timeframe]
        speed_factor = abs(jump.change_pct) / (jump.duration_seconds / 60)  # %/minute

        # Timeframe multipliers (shorter timeframes = higher urgency)
        timeframe_multipliers = {
            'spike': 4.0,        # Highest urgency for rapid spikes
            'short_trend': 2.0,  # High urgency for short trends
            'medium_trend': 1.0, # Medium urgency for medium trends
            'long_trend': 0.5    # Lower urgency for long trends
        }

        timeframe_factor = timeframe_multipliers.get(timeframe, 1.0)

        # Calculate final urgency
        urgency = magnitude_factor * speed_factor * timeframe_factor

        return min(urgency, 10.0)  # Cap at 10.0

    def _update_trend_state(self, current_price: float, current_time: float):
        """Update ongoing trend state"""
        if len(self.price_history) < 10:
            return

        # Look at last 10 price points to determine trend
        recent_points = self.price_history[-10:]

        # Calculate trend direction and strength
        price_changes = []
        for i in range(1, len(recent_points)):
            change = (recent_points[i].price - recent_points[i-1].price) / recent_points[i-1].price
            price_changes.append(change)

        # Determine trend direction
        positive_changes = sum(1 for c in price_changes if c > 0)
        negative_changes = sum(1 for c in price_changes if c < 0)

        if positive_changes > negative_changes * 1.5:
            new_direction = 'UP'
        elif negative_changes > positive_changes * 1.5:
            new_direction = 'DOWN'
        else:
            new_direction = None

        # Update trend state
        if new_direction != self.trend_state['direction']:
            # Trend direction changed
            self.trend_state['direction'] = new_direction
            self.trend_state['start_price'] = recent_points[0].price
            self.trend_state['duration'] = 0
            self.trend_state['peak_change'] = 0

        # Update trend metrics
        if self.trend_state['direction'] and self.trend_state['start_price']:
            self.trend_state['duration'] = current_time - recent_points[0].timestamp
            current_change = (current_price - self.trend_state['start_price']) / self.trend_state['start_price'] * 100

            if abs(current_change) > abs(self.trend_state['peak_change']):
                self.trend_state['peak_change'] = current_change

            # Calculate strength (0.0 to 1.0)
            self.trend_state['strength'] = min(1.0, abs(current_change) / 2.0)  # 2% = full strength

    def _is_duplicate_jump(self, current_price: float, current_time: float, timeframe: str = None) -> bool:
        """Check if we've already detected this jump recently"""
        for jump in self.recent_jumps:
            if current_time - jump.timestamp < self.jump_cooldown_seconds:
                # Similar price range and recent timing suggests same jump
                price_similarity = abs(current_price - jump.end_price) / jump.end_price

                # For same timeframe, use stricter similarity check
                if hasattr(jump, 'timeframe') and jump.timeframe == timeframe:
                    if price_similarity < 0.002:  # Within 0.2% for same timeframe
                        return True
                elif price_similarity < 0.005:  # Within 0.5% for different timeframes
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
        """Enhanced cooldown override logic for multi-timeframe detection"""
        if not self.override_cooldown:
            return False

        # Check jump attributes
        timeframe = getattr(jump, 'timeframe', 'spike')
        urgency_score = getattr(jump, 'urgency_score', 0)

        # Override criteria based on timeframe
        if timeframe == 'spike':
            # For rapid spikes, override on significant magnitude or high speed
            return abs(jump.change_pct) >= 0.8 or urgency_score >= 6.0
        elif timeframe == 'short_trend':
            # For short trends, override on strong momentum
            return abs(jump.change_pct) >= 1.0 or urgency_score >= 4.0
        elif timeframe == 'medium_trend':
            # For medium trends, override on sustained movement
            return abs(jump.change_pct) >= 1.5 or urgency_score >= 3.0
        elif timeframe == 'long_trend':
            # For long trends, override on significant sustained movement
            return abs(jump.change_pct) >= 2.0 or urgency_score >= 2.0

        # Fallback to original logic
        return abs(jump.change_pct) >= 1.0 or urgency_score >= 5.0

    def get_jump_analysis(self, jump: PriceJump) -> Dict:
        """Get detailed analysis of a price jump with enhanced multi-timeframe data"""
        timeframe = getattr(jump, 'timeframe', 'spike')
        urgency_score = getattr(jump, 'urgency_score', 0)

        # Enhanced urgency classification
        if urgency_score >= 6.0:
            urgency_level = 'CRITICAL'
        elif urgency_score >= 4.0:
            urgency_level = 'HIGH'
        elif urgency_score >= 2.0:
            urgency_level = 'MEDIUM'
        else:
            urgency_level = 'LOW'

        return {
            'magnitude': abs(jump.change_pct),
            'direction': jump.direction,
            'speed': abs(jump.change_pct) / (jump.duration_seconds / 60),  # %/minute
            'urgency': urgency_level,
            'urgency_score': urgency_score,
            'timeframe': timeframe,
            'threshold_met': getattr(jump, 'threshold_met', 0.5),
            'override_cooldown': self.should_override_cooldown(jump),
            'start_price': jump.start_price,
            'end_price': jump.end_price,
            'duration': jump.duration_seconds,
            'trend_alignment': self._check_trend_alignment(jump),
            'momentum_strength': self._calculate_momentum_strength(jump)
        }

    def _check_trend_alignment(self, jump: PriceJump) -> str:
        """Check if jump aligns with current trend"""
        if not self.trend_state['direction']:
            return 'NEUTRAL'

        if jump.direction == self.trend_state['direction']:
            return 'ALIGNED'
        else:
            return 'COUNTER_TREND'

    def _calculate_momentum_strength(self, jump: PriceJump) -> float:
        """Calculate momentum strength (0.0 to 1.0)"""
        if len(self.price_history) < 5:
            return 0.5

        # Look at recent price velocity
        recent_points = self.price_history[-5:]
        velocities = []

        for i in range(1, len(recent_points)):
            time_diff = recent_points[i].timestamp - recent_points[i-1].timestamp
            if time_diff > 0:
                price_change = (recent_points[i].price - recent_points[i-1].price) / recent_points[i-1].price
                velocity = abs(price_change) / time_diff  # %/second
                velocities.append(velocity)

        if not velocities:
            return 0.5

        avg_velocity = sum(velocities) / len(velocities)
        # Normalize to 0-1 scale (0.001 %/second = full strength)
        return min(1.0, avg_velocity / 0.001)

    def get_trend_state(self) -> Dict:
        """Get current trend state information"""
        return {
            'direction': self.trend_state['direction'],
            'strength': self.trend_state['strength'],
            'duration_seconds': self.trend_state['duration'],
            'peak_change_pct': self.trend_state['peak_change'],
            'start_price': self.trend_state['start_price'],
            'is_sustained': self.trend_state['duration'] > 300,  # 5+ minutes
            'is_strong': self.trend_state['strength'] > 0.6
        }

    def get_status(self) -> Dict:
        """Get current detector status with enhanced information"""
        return {
            'enabled': self.enabled,
            'detection_windows': self.detection_windows,
            'thresholds': self.thresholds,
            'recent_jumps_count': len(self.recent_jumps),
            'last_5min_jumps': len(self.get_recent_jumps(5)),
            'last_15min_jumps': len(self.get_recent_jumps(15)),
            'last_30min_jumps': len(self.get_recent_jumps(30)),
            'price_history_size': len(self.price_history),
            'current_trend': {
                'direction': self.trend_state['direction'],
                'strength': self.trend_state['strength'],
                'duration_seconds': self.trend_state['duration'],
                'peak_change_pct': self.trend_state['peak_change'],
                'start_price': self.trend_state['start_price'],
                'is_sustained': self.trend_state['duration'] > 300,
                'is_strong': self.trend_state['strength'] > 0.6
            },
            'timeframe_activity': self._get_timeframe_activity()
        }

    def _get_timeframe_activity(self) -> Dict:
        """Get activity breakdown by timeframe"""
        activity = {tf: 0 for tf in self.detection_windows.keys()}

        for jump in self.recent_jumps:
            timeframe = getattr(jump, 'timeframe', 'spike')
            if timeframe in activity:
                activity[timeframe] += 1

        return activity

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
