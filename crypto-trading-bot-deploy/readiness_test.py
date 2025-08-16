#!/usr/bin/env python3
"""
Bot Connection and Strategy Test
"""

import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

def test_bot_readiness():
    print("🔧 BOT READINESS TEST")
    print("=" * 50)
    
    # 1. Test configuration loading
    print("\n1. CONFIGURATION LOADING:")
    try:
        from enhanced_config import get_bot_config
        config = get_bot_config()
        print("✅ Enhanced config loaded")
        
        # Check key parameters
        trading = config.config['trading']
        risk = config.config['risk_management']
        strategy = config.config['strategy_parameters']
        
        print(f"   Trading: {trading['symbol']} with {risk['stop_loss_pct']*100:.1f}% SL, {risk['take_profit_pct']*100:.1f}% TP")
        print(f"   Confidence: {strategy['confidence_threshold']*100:.0f}% threshold")
        print(f"   Position: {trading['base_position_pct']*100:.1f}% base size")
        
    except Exception as e:
        print(f"❌ Config error: {e}")
        return False

    # 2. Test API credentials
    print("\n2. API CREDENTIALS:")
    try:
        from config import BINANCE_API_KEY, BINANCE_API_SECRET
        if BINANCE_API_KEY and BINANCE_API_SECRET:
            print(f"✅ API credentials loaded (key: {BINANCE_API_KEY[:8]}...)")
        else:
            print("❌ API credentials missing")
            return False
    except Exception as e:
        print(f"❌ API error: {e}")
        return False

    # 3. Test strategy modules
    print("\n3. STRATEGY MODULES:")
    try:
        from enhanced_multi_strategy import EnhancedMultiStrategy
        from institutional_strategies import InstitutionalStrategyManager
        
        print("✅ Core strategy modules imported successfully")
        
        # Test strategy initialization (as done in bot.py)
        strategies = {
            'enhanced_multi': EnhancedMultiStrategy(),
            'institutional': InstitutionalStrategyManager()
        }
        print("✅ Core strategies initialized successfully")
        
        # Check if success rate enhancer exists
        try:
            from success_rate_enhancer import SuccessRateEnhancer
            success_enhancer = SuccessRateEnhancer(config.config)
            print("✅ Success rate enhancer available")
        except:
            print("⚠️  Success rate enhancer not available (optional)")
        
    except Exception as e:
        print(f"❌ Strategy error: {e}")
        return False

    # 4. Test market filters
    print("\n4. MARKET FILTERS:")
    try:
        filters = config.config['market_filters']
        active_filters = []
        if filters['ma_trend_filter_enabled']:
            active_filters.append("MA Trend")
        if filters['rsi_range_filter']['enabled']:
            active_filters.append("RSI Range")
        if filters['multi_timeframe_required']:
            active_filters.append("Multi-timeframe")
        if filters['support_resistance_enabled']:
            active_filters.append("Support/Resistance")
        if filters['fibonacci_levels_enabled']:
            active_filters.append("Fibonacci")
        
        print(f"✅ Active filters: {', '.join(active_filters)}")
        
    except Exception as e:
        print(f"❌ Filter error: {e}")

    # 5. Test position sizing
    print("\n5. POSITION SIZING:")
    try:
        pos_config = config.config['position_sizing']
        features = []
        if pos_config['confidence_scaling']['enabled']:
            features.append("Confidence Scaling")
        if pos_config['risk_based_sizing']['enabled']:
            features.append("Risk-based Sizing")
        if pos_config['risk_based_sizing']['compounding_enabled']:
            features.append("Compounding")
        if pos_config['loss_adjustment']['enabled']:
            features.append("Loss Adjustment")
        if pos_config['drawdown_adjustment']['enabled']:
            features.append("Drawdown Adjustment")
        
        print(f"✅ Active features: {', '.join(features)}")
        
    except Exception as e:
        print(f"❌ Position sizing error: {e}")

    print(f"\n{'='*50}")
    print("✅ BOT IS READY FOR TRADING!")
    print(f"{'='*50}")
    
    return True

if __name__ == "__main__":
    test_bot_readiness()
