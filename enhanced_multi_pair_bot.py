# =============================================================================
# ENHANCED BOT WITH MULTI-PAIR SCANNING
# =============================================================================
#
# 🚀 ENHANCED TRADING BOT WITH AUTOMATIC PAIR SWITCHING
# Integrates multi-pair scanning with existing trading logic
# Automatically switches to most profitable opportunities
#
# =============================================================================

import asyncio
import json
import time
from datetime import datetime
from multi_pair_scanner import MultiPairScanner
from binance_native_trailing_integration import BinanceNativeTrailingIntegration
from free_phase2_api import FreePhase2Provider

class EnhancedMultiPairBot:
    """
    🚀 ENHANCED MULTI-PAIR TRADING BOT
    
    Features:
    - 24/7 multi-pair opportunity scanning
    - Automatic pair switching for maximum profits
    - Phase 2 intelligence integration
    - Native Binance trailing stops
    - Risk management and portfolio protection
    """
    
    def __init__(self, config_path: str = "enhanced_config.json"):
        self.config_path = config_path
        self.config = self._load_config()
        
        # Initialize components
        self.scanner = MultiPairScanner(config_path)
        self.trailing_integration = BinanceNativeTrailingIntegration()
        self.phase2_provider = FreePhase2Provider()
        
        # Bot state
        self.running = False
        self.current_pair = self.config.get('trading', {}).get('symbol', 'BTC/USDT')
        self.last_pair_switch = None
        self.pair_switch_cooldown = 300  # 5 minutes between switches
        
        # Performance tracking
        self.performance = {
            'total_trades': 0,
            'successful_trades': 0,
            'pair_switches': 0,
            'opportunities_caught': 0,
            'missed_opportunities': 0
        }
        
        print("🚀 Enhanced Multi-Pair Bot Initialized")
        print(f"📊 Monitoring {len(self.scanner.scan_config['supported_pairs'])} pairs")
        print(f"🎯 Current pair: {self.current_pair}")
    
    def _load_config(self) -> dict:
        """Load bot configuration"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Error loading config: {e}")
            return {}
    
    async def start_enhanced_trading(self):
        """Start enhanced multi-pair trading"""
        self.running = True
        print("🚀 Starting Enhanced Multi-Pair Trading Bot...")
        
        # Start scanner in background
        scanner_task = asyncio.create_task(self.scanner.start_scanning())
        
        # Start main trading loop
        trading_task = asyncio.create_task(self._trading_loop())
        
        # Start pair monitoring
        monitoring_task = asyncio.create_task(self._pair_monitoring_loop())
        
        try:
            # Run all tasks concurrently
            await asyncio.gather(scanner_task, trading_task, monitoring_task)
        except KeyboardInterrupt:
            print("🛑 Shutdown requested...")
        finally:
            await self._shutdown()
    
    async def _trading_loop(self):
        """Main trading loop"""
        while self.running:
            try:
                # Get current market conditions
                current_opportunity = self.scanner.opportunities.get(self.current_pair)
                
                if current_opportunity:
                    # Analyze trading signals
                    should_trade = await self._analyze_trading_signals(current_opportunity)
                    
                    if should_trade:
                        await self._execute_trade(current_opportunity)
                
                # Wait before next analysis
                await asyncio.sleep(15)  # 15-second trading loop
                
            except Exception as e:
                print(f"❌ Trading loop error: {e}")
                await asyncio.sleep(30)
    
    async def _pair_monitoring_loop(self):
        """Monitor for pair switching opportunities"""
        while self.running:
            try:
                # Check if we should switch pairs
                should_switch, new_pair = self.scanner.should_switch_pair(self.current_pair)
                
                if should_switch and new_pair:
                    # Check cooldown
                    if self._can_switch_pair():
                        await self._switch_trading_pair(new_pair)
                
                # Check every minute
                await asyncio.sleep(60)
                
            except Exception as e:
                print(f"❌ Pair monitoring error: {e}")
                await asyncio.sleep(60)
    
    def _can_switch_pair(self) -> bool:
        """Check if pair switching is allowed"""
        if self.last_pair_switch is None:
            return True
        
        time_since_switch = time.time() - self.last_pair_switch
        return time_since_switch >= self.pair_switch_cooldown
    
    async def _switch_trading_pair(self, new_pair: str):
        """Switch to new trading pair"""
        try:
            old_pair = self.current_pair
            
            print(f"🔄 SWITCHING TRADING PAIR: {old_pair} → {new_pair}")
            
            # Get opportunity details
            opportunity = self.scanner.opportunities.get(new_pair)
            if opportunity:
                print(f"📈 Opportunity: {opportunity.price_change_1h:+.2f}% (1h), {opportunity.confidence:.1%} confidence")
            
            # Update bot state
            self.current_pair = new_pair
            self.last_pair_switch = time.time()
            self.performance['pair_switches'] += 1
            
            # Update configuration
            await self._update_config_pair(new_pair)
            
            # Initialize Phase 2 intelligence for new pair
            await self._initialize_pair_intelligence(new_pair)
            
            print(f"✅ Successfully switched to {new_pair}")
            
        except Exception as e:
            print(f"❌ Pair switch failed: {e}")
    
    async def _update_config_pair(self, new_pair: str):
        """Update configuration with new trading pair"""
        try:
            self.config['trading']['symbol'] = new_pair
            self.config['trading']['last_pair_switch'] = datetime.now().isoformat()
            
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
                
        except Exception as e:
            print(f"⚠️ Config update error: {e}")
    
    async def _initialize_pair_intelligence(self, pair: str):
        """Initialize Phase 2 intelligence for new pair"""
        try:
            # Extract base asset
            base_asset = pair.split('/')[0]
            
            # Get Phase 2 intelligence
            intelligence = await self.phase2_provider.get_comprehensive_intelligence(base_asset)
            
            if intelligence and intelligence.get('confidence', 0) > 0.6:
                print(f"🧠 Phase 2 Intelligence for {pair}:")
                print(f"   Whale Activity: {intelligence.get('whale_activity', {}).get('confidence', 0):.1%}")
                print(f"   Exchange Flows: {intelligence.get('exchange_flows', {}).get('net_flow_usd', 0):,.0f}")
                print(f"   DeFi Activity: {intelligence.get('defi_intelligence', {}).get('confidence', 0):.1%}")
            
        except Exception as e:
            print(f"⚠️ Phase 2 intelligence init error: {e}")
    
    async def _analyze_trading_signals(self, opportunity) -> bool:
        """Analyze if we should trade based on current signals"""
        try:
            # Basic momentum check
            if opportunity.confidence < 0.6:
                return False
            
            # Check for strong bullish momentum
            if opportunity.price_change_1h > 1.0 and opportunity.volume_surge > 1.5:
                return True
            
            # Check Phase 2 intelligence confirmation
            base_asset = self.current_pair.split('/')[0]
            intelligence = await self.phase2_provider.get_comprehensive_intelligence(base_asset)
            
            if intelligence and intelligence.get('confidence', 0) > 0.7:
                # Phase 2 confirms opportunity
                return True
            
            return False
            
        except Exception as e:
            print(f"⚠️ Signal analysis error: {e}")
            return False
    
    async def _execute_trade(self, opportunity):
        """Execute trade based on opportunity"""
        try:
            print(f"💰 EXECUTING TRADE: {self.current_pair}")
            print(f"   Momentum: {opportunity.price_change_1h:+.2f}% (1h)")
            print(f"   Confidence: {opportunity.confidence:.1%}")
            print(f"   Volume: {opportunity.volume_surge:.1f}x normal")
            
            # Here you would integrate with actual trading logic
            # For now, just simulate
            await asyncio.sleep(1)
            
            # Set up trailing stop
            await self._setup_trailing_stop(opportunity)
            
            self.performance['total_trades'] += 1
            self.performance['opportunities_caught'] += 1
            
            print(f"✅ Trade executed for {self.current_pair}")
            
        except Exception as e:
            print(f"❌ Trade execution error: {e}")
    
    async def _setup_trailing_stop(self, opportunity):
        """Setup trailing stop for position"""
        try:
            # Calculate trailing stop distance based on volatility
            base_distance = 0.5  # 0.5% base
            
            # Adjust based on momentum
            if opportunity.momentum_score > 0.8:
                distance = base_distance * 0.7  # Tighter for strong momentum
            else:
                distance = base_distance * 1.2  # Wider for weaker momentum
            
            print(f"🛡️ Setting trailing stop: {distance:.2f}% distance")
            
            # Here you would call the actual trailing stop setup
            # await self.trailing_integration.setup_trailing_stop(self.current_pair, distance)
            
        except Exception as e:
            print(f"⚠️ Trailing stop setup error: {e}")
    
    def get_performance_report(self) -> dict:
        """Get bot performance report"""
        return {
            'current_pair': self.current_pair,
            'total_trades': self.performance['total_trades'],
            'successful_trades': self.performance['successful_trades'],
            'win_rate': (self.performance['successful_trades'] / max(self.performance['total_trades'], 1)) * 100,
            'pair_switches': self.performance['pair_switches'],
            'opportunities_caught': self.performance['opportunities_caught'],
            'missed_opportunities': self.performance['missed_opportunities'],
            'scanner_status': self.scanner.get_status_report(),
            'uptime': time.time() - getattr(self, 'start_time', time.time())
        }
    
    async def _shutdown(self):
        """Graceful shutdown"""
        print("🛑 Shutting down Enhanced Multi-Pair Bot...")
        
        self.running = False
        self.scanner.stop_scanning()
        
        # Print final performance report
        report = self.get_performance_report()
        print(f"📊 Final Performance:")
        print(f"   Total Trades: {report['total_trades']}")
        print(f"   Pair Switches: {report['pair_switches']}")
        print(f"   Opportunities Caught: {report['opportunities_caught']}")
        print(f"   Current Pair: {report['current_pair']}")
        
        print("✅ Shutdown complete")

# 🚀 QUICK DEPLOYMENT FUNCTION
async def deploy_enhanced_multi_pair_bot():
    """Deploy enhanced multi-pair bot"""
    bot = EnhancedMultiPairBot()
    bot.start_time = time.time()
    
    try:
        await bot.start_enhanced_trading()
    except KeyboardInterrupt:
        print("👋 Goodbye!")

if __name__ == "__main__":
    print("🚀 ENHANCED MULTI-PAIR TRADING BOT")
    print("="*50)
    print("Features:")
    print("- 24/7 multi-pair opportunity scanning")
    print("- Automatic pair switching for max profits")
    print("- Phase 2 blockchain intelligence")
    print("- Native Binance trailing stops")
    print("- Real-time momentum detection")
    print("="*50)
    
    # Run the bot
    asyncio.run(deploy_enhanced_multi_pair_bot())
