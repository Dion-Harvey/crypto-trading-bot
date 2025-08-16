#!/usr/bin/env python3
"""
💰 MULTI-POSITION PORTFOLIO MANAGER
Enables holding positions in multiple cryptocurrency pairs simultaneously
"""

import json
import time
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, List, Optional
from log_utils import log_message

@dataclass
class PortfolioPosition:
    symbol: str
    entry_price: float
    quantity: float
    entry_time: datetime
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    current_pnl_pct: float = 0.0
    current_pnl_usd: float = 0.0

class MultiPositionPortfolioManager:
    def __init__(self, max_positions=5, max_allocation_per_position=0.25):
        self.max_positions = max_positions
        self.max_allocation_per_position = max_allocation_per_position  # 25% max per position
        self.active_positions: Dict[str, PortfolioPosition] = {}
        self.supported_pairs = [
            "BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT", 
            "ADA/USDT", "DOGE/USDT", "XLM/USDT", "SUI/USDT",
            "SHIB/USDT", "HBAR/USDT", "AVAX/USDT", "DOT/USDT",
            "MATIC/USDT", "LINK/USDT", "UNI/USDT", "LTC/USDT"
        ]
        
    def can_open_new_position(self, symbol: str) -> tuple[bool, str]:
        """
        Check if we can open a new position in the given symbol
        """
        if symbol in self.active_positions:
            return False, f"Already holding position in {symbol}"
        
        if len(self.active_positions) >= self.max_positions:
            return False, f"Maximum positions reached ({self.max_positions})"
        
        return True, "Can open new position"
    
    def calculate_position_size(self, symbol: str, current_price: float, 
                               total_portfolio_value: float, opportunity_score: float) -> float:
        """
        Calculate optimal position size based on portfolio allocation and opportunity score
        """
        # Base allocation (equal weight if all positions filled)
        base_allocation = min(self.max_allocation_per_position, 1.0 / self.max_positions)
        
        # Adjust based on opportunity score (0.0 to 1.0)
        score_multiplier = min(opportunity_score / 100.0, 1.0)  # Normalize urgency score
        
        # Adjust based on current portfolio positions
        position_count_adjustment = 1.0 + (0.2 * (self.max_positions - len(self.active_positions)))
        
        # Final allocation
        allocation = base_allocation * score_multiplier * position_count_adjustment
        allocation = min(allocation, self.max_allocation_per_position)
        
        position_value = total_portfolio_value * allocation
        position_size = position_value / current_price
        
        return position_size
    
    def add_position(self, symbol: str, entry_price: float, quantity: float) -> bool:
        """
        Add a new position to the portfolio
        """
        can_open, reason = self.can_open_new_position(symbol)
        if not can_open:
            log_message(f"❌ Cannot open {symbol} position: {reason}")
            return False
        
        position = PortfolioPosition(
            symbol=symbol,
            entry_price=entry_price,
            quantity=quantity,
            entry_time=datetime.now(),
            stop_loss=entry_price * 0.95,  # 5% stop loss
            take_profit=entry_price * 1.08  # 8% take profit
        )
        
        self.active_positions[symbol] = position
        log_message(f"✅ Added position: {symbol} - {quantity:.6f} @ ${entry_price:.4f}")
        return True
    
    def remove_position(self, symbol: str, exit_price: float, reason: str = "Manual exit") -> Optional[PortfolioPosition]:
        """
        Remove a position from the portfolio
        """
        if symbol not in self.active_positions:
            log_message(f"⚠️ No position to remove: {symbol}")
            return None
        
        position = self.active_positions.pop(symbol)
        
        # Calculate final P&L
        pnl_usd = (exit_price - position.entry_price) * position.quantity
        pnl_pct = ((exit_price - position.entry_price) / position.entry_price) * 100
        
        log_message(f"🔄 Closed position: {symbol}")
        log_message(f"   Entry: ${position.entry_price:.4f} → Exit: ${exit_price:.4f}")
        log_message(f"   P&L: ${pnl_usd:.2f} ({pnl_pct:+.2f}%)")
        log_message(f"   Reason: {reason}")
        
        return position
    
    def update_positions_pnl(self, exchange) -> Dict[str, Dict]:
        """
        Update P&L for all active positions
        """
        position_status = {}
        
        for symbol, position in self.active_positions.items():
            try:
                # Get current price
                ticker = exchange.fetch_ticker(symbol)
                current_price = ticker['last']
                
                # Calculate P&L
                pnl_usd = (current_price - position.entry_price) * position.quantity
                pnl_pct = ((current_price - position.entry_price) / position.entry_price) * 100
                
                # Update position
                position.current_pnl_pct = pnl_pct
                position.current_pnl_usd = pnl_usd
                
                position_status[symbol] = {
                    'current_price': current_price,
                    'entry_price': position.entry_price,
                    'quantity': position.quantity,
                    'pnl_usd': pnl_usd,
                    'pnl_pct': pnl_pct,
                    'stop_loss': position.stop_loss,
                    'take_profit': position.take_profit,
                    'age_minutes': (datetime.now() - position.entry_time).total_seconds() / 60
                }
                
            except Exception as e:
                log_message(f"⚠️ Error updating {symbol} position: {e}")
                position_status[symbol] = {'error': str(e)}
        
        return position_status
    
    def check_exit_conditions(self, exchange) -> List[tuple[str, str]]:
        """
        Check if any positions should be closed based on stop loss, take profit, or other conditions
        """
        positions_to_close = []
        
        position_status = self.update_positions_pnl(exchange)
        
        for symbol, status in position_status.items():
            if 'error' in status:
                continue
            
            position = self.active_positions[symbol]
            current_price = status['current_price']
            
            # Check stop loss
            if position.stop_loss and current_price <= position.stop_loss:
                positions_to_close.append((symbol, f"Stop loss hit: ${current_price:.4f} <= ${position.stop_loss:.4f}"))
            
            # Check take profit
            elif position.take_profit and current_price >= position.take_profit:
                positions_to_close.append((symbol, f"Take profit hit: ${current_price:.4f} >= ${position.take_profit:.4f}"))
            
            # Check for major losses (emergency exit)
            elif status['pnl_pct'] <= -15.0:
                positions_to_close.append((symbol, f"Emergency exit: {status['pnl_pct']:.2f}% loss"))
            
            # Check for aged profitable positions (take profits after 4 hours if >5% profit)
            elif status['age_minutes'] > 240 and status['pnl_pct'] > 5.0:
                positions_to_close.append((symbol, f"Aged profitable position: {status['pnl_pct']:.2f}% profit after {status['age_minutes']:.0f}min"))
        
        return positions_to_close
    
    def get_portfolio_summary(self) -> Dict:
        """
        Get summary of the entire portfolio
        """
        if not self.active_positions:
            return {
                'active_positions': 0,
                'total_pnl_usd': 0.0,
                'total_pnl_pct': 0.0,
                'positions': {}
            }
        
        total_invested = sum(pos.entry_price * pos.quantity for pos in self.active_positions.values())
        total_current_value = sum(
            (pos.entry_price + pos.current_pnl_usd / pos.quantity) * pos.quantity 
            for pos in self.active_positions.values()
        )
        total_pnl_usd = sum(pos.current_pnl_usd for pos in self.active_positions.values())
        total_pnl_pct = (total_pnl_usd / total_invested) * 100 if total_invested > 0 else 0.0
        
        positions_summary = {}
        for symbol, pos in self.active_positions.items():
            positions_summary[symbol] = {
                'quantity': pos.quantity,
                'entry_price': pos.entry_price,
                'current_pnl_pct': pos.current_pnl_pct,
                'current_pnl_usd': pos.current_pnl_usd,
                'age_minutes': (datetime.now() - pos.entry_time).total_seconds() / 60
            }
        
        return {
            'active_positions': len(self.active_positions),
            'total_invested_usd': total_invested,
            'total_current_value_usd': total_current_value,
            'total_pnl_usd': total_pnl_usd,
            'total_pnl_pct': total_pnl_pct,
            'positions': positions_summary
        }
    
    def find_best_opportunities_for_new_positions(self, exchange) -> List[tuple[str, float, str]]:
        """
        Find the best opportunities for opening new positions
        """
        opportunities = []
        
        try:
            from comprehensive_opportunity_scanner import run_immediate_comprehensive_scan
            all_opportunities = run_immediate_comprehensive_scan(exchange)
            
            # Filter for pairs we're not already holding and that meet criteria
            available_opportunities = [
                opp for opp in all_opportunities 
                if (opp.symbol not in self.active_positions and 
                    opp.urgency_score >= 40.0 and  # Minimum quality threshold
                    opp.recommendation in ["IMMEDIATE_SWITCH", "STRONG_CONSIDERATION"])
            ]
            
            # Sort by urgency score
            available_opportunities.sort(key=lambda x: x.urgency_score, reverse=True)
            
            # Take top opportunities up to available position slots
            available_slots = self.max_positions - len(self.active_positions)
            for opp in available_opportunities[:available_slots]:
                opportunities.append((
                    opp.symbol, 
                    opp.urgency_score, 
                    f"{opp.price_change_1h:+.2f}% (1h), Vol: {opp.volume_change:+.1f}%"
                ))
            
        except Exception as e:
            log_message(f"⚠️ Error finding opportunities: {e}")
        
        return opportunities

def demonstrate_multi_position_concept():
    """
    Demonstrate how multi-position portfolio would work
    """
    print("\n" + "="*80)
    print("💰 MULTI-POSITION PORTFOLIO CONCEPT DEMONSTRATION")
    print("="*80)
    
    portfolio = MultiPositionPortfolioManager(max_positions=5)
    
    print(f"📊 PORTFOLIO SETUP:")
    print(f"   Max positions: {portfolio.max_positions}")
    print(f"   Max allocation per position: {portfolio.max_allocation_per_position * 100:.1f}%")
    print(f"   Supported pairs: {len(portfolio.supported_pairs)}")
    
    # Simulate adding positions
    mock_positions = [
        ("BTC/USDT", 63000.0, 0.001587),  # ~$100
        ("ETH/USDT", 3200.0, 0.03125),    # ~$100
        ("SOL/USDT", 140.0, 0.714),       # ~$100
        ("XRP/USDT", 0.52, 192.3),        # ~$100
    ]
    
    print(f"\n🎯 SIMULATED POSITIONS:")
    for symbol, price, quantity in mock_positions:
        portfolio.add_position(symbol, price, quantity)
    
    # Show portfolio summary
    summary = portfolio.get_portfolio_summary()
    print(f"\n📊 PORTFOLIO SUMMARY:")
    print(f"   Active positions: {summary['active_positions']}")
    print(f"   Total invested: ${summary['total_invested_usd']:.2f}")
    print(f"   Available slots: {portfolio.max_positions - len(portfolio.active_positions)}")
    
    print(f"\n💡 HOW THIS WOULD WORK:")
    print(f"   1. 🔍 Bot scans ALL 16 pairs for opportunities")
    print(f"   2. 💰 Bot can hold up to {portfolio.max_positions} positions simultaneously")
    print(f"   3. 📊 Each position gets max {portfolio.max_allocation_per_position*100:.0f}% of portfolio")
    print(f"   4. 🎯 Bot opens new positions when high-quality opportunities arise")
    print(f"   5. 🔄 Bot closes positions based on stop-loss, take-profit, or better opportunities")
    print(f"   6. 📈 Portfolio is diversified across multiple winning positions")
    
    print(f"\n⚠️ IMPLEMENTATION REQUIREMENTS:")
    print(f"   • Modify bot.py main loop to handle multiple positions")
    print(f"   • Update risk management for portfolio-level risk")
    print(f"   • Implement position sizing based on opportunity quality")
    print(f"   • Add portfolio rebalancing logic")
    print(f"   • Update state management for multiple positions")
    
    print("="*80)

if __name__ == "__main__":
    demonstrate_multi_position_concept()
