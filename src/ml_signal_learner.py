#!/usr/bin/env python3
"""
🧠 ML SIGNAL LEARNING SYSTEM

Tracks signal accuracy and learns from mistakes to improve future predictions.
Records when death cross signals are incorrectly interpreted as buy signals.
"""

import json
import time
from datetime import datetime
import os

class MLSignalLearner:
    """
    Machine Learning Signal Learner
    
    Tracks signal performance and learns from trading mistakes.
    """
    
    def __init__(self):
        self.learning_file = "ml_signal_learning.json"
        self.load_learning_data()
    
    def load_learning_data(self):
        """Load existing learning data"""
        try:
            if os.path.exists(self.learning_file):
                with open(self.learning_file, 'r') as f:
                    self.learning_data = json.load(f)
            else:
                self.learning_data = {
                    'signal_outcomes': [],
                    'mistake_patterns': {},
                    'accuracy_stats': {},
                    'learned_rules': []
                }
        except Exception as e:
            print(f"Error loading learning data: {e}")
            self.learning_data = {
                'signal_outcomes': [],
                'mistake_patterns': {},
                'accuracy_stats': {},
                'learned_rules': []
            }
    
    def save_learning_data(self):
        """Save learning data to file"""
        try:
            with open(self.learning_file, 'w') as f:
                json.dump(self.learning_data, f, indent=2)
        except Exception as e:
            print(f"Error saving learning data: {e}")
    
    def record_signal_mistake(self, signal_type, signal_details, mistake_type, loss_pct=None):
        """
        Record when a signal leads to a mistake/loss
        
        Args:
            signal_type: 'death_cross', 'golden_cross', 'dip_buy', etc.
            signal_details: Dict with signal details (EMA values, confidence, etc.)
            mistake_type: 'wrong_direction', 'false_signal', 'timing_error'
            loss_pct: Percentage loss if applicable
        """
        
        mistake_record = {
            'timestamp': datetime.now().isoformat(),
            'signal_type': signal_type,
            'signal_details': signal_details,
            'mistake_type': mistake_type,
            'loss_pct': loss_pct,
            'learning_points': []
        }
        
        # Add specific learning points based on mistake type
        if signal_type == 'death_cross' and mistake_type == 'wrong_direction':
            mistake_record['learning_points'] = [
                "Death cross should NEVER result in BUY signal",
                "When EMA7 crosses below EMA25, market sentiment is bearish",
                "Dip buying should be disabled during bearish crossover trends",
                "Death cross = SELL or HOLD only, never BUY"
            ]
            
            # Record this pattern
            pattern_key = "death_cross_buy_mistake"
            if pattern_key not in self.learning_data['mistake_patterns']:
                self.learning_data['mistake_patterns'][pattern_key] = {
                    'count': 0,
                    'total_loss_pct': 0,
                    'avg_loss_pct': 0,
                    'learned_rules': []
                }
            
            pattern = self.learning_data['mistake_patterns'][pattern_key]
            pattern['count'] += 1
            if loss_pct:
                pattern['total_loss_pct'] += loss_pct
                pattern['avg_loss_pct'] = pattern['total_loss_pct'] / pattern['count']
            
            # Add learned rule
            learned_rule = {
                'rule': "NEVER_BUY_ON_DEATH_CROSS",
                'confidence': min(0.9 + (pattern['count'] * 0.02), 1.0),
                'learned_from_mistakes': pattern['count'],
                'description': "Death cross signals should never trigger buy orders - always SELL or HOLD"
            }
            
            pattern['learned_rules'].append(learned_rule)
            
            # Add to main learned rules if not already there
            rule_exists = any(r['rule'] == 'NEVER_BUY_ON_DEATH_CROSS' for r in self.learning_data['learned_rules'])
            if not rule_exists:
                self.learning_data['learned_rules'].append(learned_rule)
            else:
                # Update existing rule
                for rule in self.learning_data['learned_rules']:
                    if rule['rule'] == 'NEVER_BUY_ON_DEATH_CROSS':
                        rule['confidence'] = learned_rule['confidence']
                        rule['learned_from_mistakes'] = learned_rule['learned_from_mistakes']
        
        # Add to signal outcomes
        self.learning_data['signal_outcomes'].append(mistake_record)
        
        # Save learning data
        self.save_learning_data()
        
        print(f"🧠 ML LEARNING: Recorded mistake for {signal_type}")
        print(f"   Mistake Type: {mistake_type}")
        if loss_pct:
            print(f"   Loss: {loss_pct:.2f}%")
        print(f"   Learning Points: {len(mistake_record['learning_points'])}")
        
        return mistake_record
    
    def get_signal_confidence_adjustment(self, signal_type, signal_details):
        """
        Get confidence adjustment based on learned patterns
        
        Returns: (adjustment_factor, reasoning)
        """
        
        # Check for death cross buy mistake pattern
        if signal_type == 'death_cross' and signal_details.get('action') == 'BUY':
            return (0.0, "LEARNED RULE: Never buy on death cross - confidence set to 0")
        
        # Check for dip buying during bearish trend
        if (signal_type in ['dip_buy', 'enhanced_dip_buy'] and 
            signal_details.get('ema7', 0) < signal_details.get('ema25', 0)):
            return (0.5, "LEARNED RULE: Reduce dip buying confidence during bearish EMA trend")
        
        # Default - no adjustment
        return (1.0, "No learned adjustments apply")
    
    def get_learning_summary(self):
        """Get summary of learned patterns"""
        summary = {
            'total_mistakes_recorded': len(self.learning_data['signal_outcomes']),
            'learned_rules_count': len(self.learning_data['learned_rules']),
            'mistake_patterns': self.learning_data['mistake_patterns'],
            'learned_rules': self.learning_data['learned_rules']
        }
        
        return summary

# Global instance
ml_signal_learner = MLSignalLearner()

def record_death_cross_buy_mistake(signal_details, loss_pct=None):
    """
    Record the specific mistake where death cross resulted in buy signal
    """
    return ml_signal_learner.record_signal_mistake(
        signal_type='death_cross',
        signal_details=signal_details,
        mistake_type='wrong_direction',
        loss_pct=loss_pct
    )

def apply_ml_learning_to_signal(signal):
    """
    Apply ML learning adjustments to trading signals
    """
    if not signal or 'action' not in signal:
        return signal
    
    signal_type = signal.get('crossover_type', 'unknown')
    adjustment_factor, reasoning = ml_signal_learner.get_signal_confidence_adjustment(signal_type, signal)
    
    if adjustment_factor != 1.0:
        original_confidence = signal.get('confidence', 0)
        signal['confidence'] = original_confidence * adjustment_factor
        signal['ml_adjustment'] = {
            'factor': adjustment_factor,
            'reasoning': reasoning,
            'original_confidence': original_confidence
        }
        
        # If confidence drops to 0, change action to HOLD
        if signal['confidence'] <= 0.1:
            signal['action'] = 'HOLD'
            signal['reasons'].append(f"ML OVERRIDE: {reasoning}")
    
    return signal

if __name__ == "__main__":
    # Test the learning system
    learner = MLSignalLearner()
    
    # Simulate the EGLD death cross buy mistake
    signal_details = {
        'action': 'BUY',
        'crossover_type': 'death_cross',
        'ema7': 14.95,
        'ema25': 15.05,
        'confidence': 0.8,
        'symbol': 'EGLD/USDT'
    }
    
    # Record the mistake
    learner.record_signal_mistake(
        signal_type='death_cross',
        signal_details=signal_details,
        mistake_type='wrong_direction',
        loss_pct=2.5  # Assuming 2.5% loss
    )
    
    print("\n📊 LEARNING SUMMARY:")
    summary = learner.get_learning_summary()
    print(json.dumps(summary, indent=2))
