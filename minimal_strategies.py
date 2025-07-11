#!/usr/bin/env python3
"""
Minimal strategy classes to get the bot running
"""

class MultiStrategyOptimized:
    def get_consensus_signal(self, df):
        """Minimal strategy implementation"""
        return {
            'action': 'HOLD',
            'confidence': 0.5,
            'reason': 'Minimal strategy implementation'
        }

class EnhancedMultiStrategy:
    def get_enhanced_consensus_signal(self, df):
        """Minimal enhanced strategy implementation"""
        return {
            'action': 'HOLD', 
            'confidence': 0.5,
            'reason': 'Minimal enhanced strategy implementation'
        }

class AdvancedHybridStrategy:
    def get_adaptive_signal(self, df):
        """Minimal adaptive strategy implementation"""
        return {
            'action': 'HOLD',
            'confidence': 0.5,
            'reason': 'Minimal adaptive strategy implementation',
            'mode': 'neutral'
        }
