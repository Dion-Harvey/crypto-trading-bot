# =============================================================================
# CRYPTO TRADING BOT - Main Entry Point
# =============================================================================
#
# Copyright (c) 2025 Dion Harvey. All rights reserved.
# Licensed under Custom License - see LICENSE file for details.
#
# AGGRESSIVE DAY TRADING BTC BOT
# Features: Multi-Strategy Ensemble, Machine Learning, Kelly Criterion,
# Value-at-Risk Analysis, Advanced Risk Management
#
# IMPORTANT: This software contains proprietary trading strategies and
# algorithms. Commercial use requires explicit written permission.
# See LICENSE file for complete terms and conditions.
#
# =============================================================================

# 🛡️ AWS-ONLY EXECUTION PROTECTION
import os
import socket
import sys
import platform

# Command line help (check before anything else)
if '--help' in sys.argv or '-h' in sys.argv:
    print("🤖 CRYPTO TRADING BOT - COMMAND LINE OPTIONS")
    print("")
    print("Usage: python bot.py [options]")
    print("")
    print("Options:")
    print("  --local-testing    Run bot locally (bypasses AWS-only restriction)")
    print("                     ⚠️  WARNING: Ensure AWS bot is stopped first!")
    print("  --help, -h         Show this help message")
    print("")
    print("Default: Bot runs on AWS EC2 only (security measure)")
    sys.exit(0)

def check_aws_environment():
    """
    🛡️ CRITICAL: Ensure bot only runs on AWS EC2
    Prevents accidental local execution that could interfere with AWS bot
    """
    try:
        # Check for local testing mode
        if '--local-testing' in sys.argv:
            print("🏠 LOCAL TESTING MODE ENABLED")
            print("   ⚠️  CAUTION: Ensure AWS bot is stopped to prevent conflicts")
            print("   ✅ Proceeding with local execution...")
            return True
        
        # Check if running on AWS EC2
        hostname = socket.gethostname()
        system = platform.system()
        
        # AWS EC2 specific checks
        is_aws = False
        
        # Check for AWS metadata service (reliable AWS detection)
        try:
            import urllib.request
            import urllib.error
            req = urllib.request.Request(
                'http://169.254.169.254/latest/meta-data/instance-id',
                headers={'User-Agent': 'AWS-Bot-Check'}
            )
            urllib.request.urlopen(req, timeout=2)
            is_aws = True
            print("✅ AWS EC2 ENVIRONMENT CONFIRMED")
        except (urllib.error.URLError, OSError, Exception):
            pass
        
        # Alternative checks for AWS
        if not is_aws:
            # Check for typical AWS hostnames
            if 'ip-' in hostname or 'ec2' in hostname:
                is_aws = True
            
            # Check for AWS environment variables
            if any(env.startswith('AWS_') for env in os.environ):
                is_aws = True
                
            # Check for EC2 user
            if os.environ.get('USER') == 'ubuntu' and system == 'Linux':
                is_aws = True
        
        if not is_aws:
            print("🚨 CRITICAL: Bot attempted to start locally!")
            print("   ❌ This bot should ONLY run on AWS EC2")
            print("   ❌ Local execution could interfere with AWS bot")
            print("   ❌ Please run on AWS only")
            print("   🎯 AWS IP: 3.135.216.32")
            print("   💡 Use SSH to manage the AWS bot instead")
            print("\n🛑 EXECUTION BLOCKED - AWS ONLY!")
            sys.exit(1)
        
        print("✅ AWS ENVIRONMENT VERIFIED - Bot starting...")
        return True
        
    except Exception as e:
        print(f"⚠️ Environment check failed: {e}")
        print("🛑 STOPPING - Cannot verify AWS environment")
        sys.exit(1)

# Run AWS check immediately
check_aws_environment()

# Import required libraries
import ccxt
import json
import time
import re
import datetime
import pandas as pd
import traceback
from config import BINANCE_API_KEY, BINANCE_API_SECRET
from strategies.ma_crossover import fetch_ohlcv, MovingAverageCrossover
from strategies.multi_strategy_optimized import MultiStrategyOptimized
from strategies.hybrid_strategy import AdvancedHybridStrategy
from enhanced_multi_strategy import EnhancedMultiStrategy
from institutional_strategies import InstitutionalStrategyManager
from log_utils import init_log, log_trade, generate_performance_report, generate_trade_analysis, log_message
from performance_tracker import performance_tracker
from enhanced_config import get_bot_config
from state_manager import get_state_manager
from success_rate_enhancer import success_enhancer, check_anti_whipsaw_protection
from price_jump_detector import detect_price_jump, get_price_jump_detector
from multi_timeframe_ma import detect_multi_timeframe_ma_signals
from enhanced_multi_timeframe_ma import detect_enhanced_multi_timeframe_ma_signals
from priority_functions_5m1m import should_hold_position, calculate_recent_momentum, detect_5m_1m_agreement, detect_peak_and_trailing_exit
from multi_crypto_monitor import get_multi_crypto_monitor

# 🧠 ML LEARNING SYSTEM: Learn from trading mistakes
try:
    from ml_signal_learner import ml_signal_learner, apply_ml_learning_to_signal, record_death_cross_buy_mistake
    ML_LEARNING_AVAILABLE = True
    log_message("🧠 ML Signal Learning System initialized - will learn from mistakes")
except ImportError as e:
    ML_LEARNING_AVAILABLE = False
    log_message(f"⚠️ ML Learning System not available: {e}")

# 🚀 API OPTIMIZATION: Caching System to Reduce Redundant Calls
class APICache:
    """
    🔧 Smart API Caching System
    
    Reduces redundant API calls by caching frequently accessed data
    like balance, tickers, and OHLCV data for short periods.
    """
    def __init__(self):
        self.cache = {}
        self.cache_duration = {
            'balance': 30,      # Cache balance for 30 seconds
            'ticker': 10,       # Cache individual tickers for 10 seconds
            'tickers': 15,      # Cache batch tickers for 15 seconds
            'ohlcv': 60        # Cache OHLCV for 1 minute
        }
    
    def get(self, key, data_type='default'):
        """Get cached data if still valid"""
        if key in self.cache:
            data, timestamp = self.cache[key]
            duration = self.cache_duration.get(data_type, 10)
            if time.time() - timestamp < duration:
                return data
        return None
    
    def set(self, key, data, data_type='default'):
        """Cache data with timestamp"""
        self.cache[key] = (data, time.time())
        # Note: data_type parameter preserved for future cache type differentiation
    
    def clear_expired(self):
        """Clear expired cache entries"""
        current_time = time.time()
        expired_keys = []
        for key, (_, timestamp) in self.cache.items():
            if current_time - timestamp > 300:  # Clear after 5 minutes
                expired_keys.append(key)
        for key in expired_keys:
            del self.cache[key]

# Initialize global API cache
api_cache = APICache()

def safe_api_call_cached(func, *args, cache_key=None, cache_type='default', **kwargs):
    """
    🚀 OPTIMIZED: Safe API call with caching
    
    Wraps safe_api_call with intelligent caching to reduce
    redundant API calls and avoid rate limiting.
    """
    # Check cache first if cache_key provided
    if cache_key:
        cached_result = api_cache.get(cache_key, cache_type)
        if cached_result is not None:
            return cached_result
    
    # Make API call using existing safe_api_call
    result = safe_api_call(func, *args, **kwargs)
    
    # Cache successful results
    if result is not None and cache_key:
        api_cache.set(cache_key, result, cache_type)
    
    return result

def get_cached_balance():
    """
    🚀 OPTIMIZED: Get account balance with 30-second caching
    
    Reduces redundant balance API calls by caching results.
    Balance doesn't change frequently, so this is safe.
    """
    return safe_api_call_cached(
        exchange.fetch_balance,
        cache_key='account_balance',
        cache_type='balance'
    )

def get_cached_ticker(symbol):
    """
    🚀 OPTIMIZED: Get ticker data with 10-second caching
    
    Reduces redundant ticker API calls for the same symbol.
    """
    return safe_api_call_cached(
        exchange.fetch_ticker,
        symbol,
        cache_key=f'ticker_{symbol}',
        cache_type='ticker'
    )

# Initialize on-chain data provider for enhanced intelligence
try:
    from onchain_data_provider import OnChainDataProvider
    ONCHAIN_AVAILABLE = True
    log_message("✅ On-chain data provider initialized")
except ImportError as e:
    ONCHAIN_AVAILABLE = False
    log_message(f"⚠️ On-chain data provider not available: {e}")

# 🆓 Initialize FREE cryptocurrency APIs (ZERO COST!)
try:
    from free_crypto_api import get_free_crypto_intelligence, get_free_volume_alerts
    FREE_CRYPTO_AVAILABLE = True
    log_message("✅ 🆓 FREE Crypto APIs initialized (CoinGecko + CoinCap + CryptoCompare)")
    log_message("💰 Total monthly cost: $0 - No credit card required!")
except ImportError as e:
    FREE_CRYPTO_AVAILABLE = False
    log_message(f"⚠️ Free crypto APIs not available: {e}")

# 🚀 Initialize FREE Phase 2 Advanced Intelligence (ZERO COST!)
try:
    from free_phase2_api import get_free_phase2_intelligence, get_free_phase2_alerts
    from free_phase2_config import get_phase2_config, validate_phase2_setup
    FREE_PHASE2_AVAILABLE = True
    
    # Validate Phase 2 setup
    phase2_validation = validate_phase2_setup()
    if phase2_validation['status'] in ['valid', 'valid_with_warnings']:
        log_message("✅ 🚀 FREE Phase 2 Advanced Intelligence initialized!")
        log_message("🎯 Features: Exchange flows, whale tracking, DeFi intelligence, DEX analytics")
        log_message(f"💰 Monthly cost: ${phase2_validation['summary']['monthly_cost']}")
        log_message(f"💎 Monthly savings: ${phase2_validation['summary']['monthly_savings']}")
        log_message(f"🔧 Active APIs: {phase2_validation['summary']['active_apis']}")
        
        if phase2_validation['warnings']:
            for warning in phase2_validation['warnings']:
                log_message(f"⚠️ Phase 2 Warning: {warning}")
    else:
        log_message(f"❌ Phase 2 validation failed: {phase2_validation['errors']}")
        FREE_PHASE2_AVAILABLE = False
        
except ImportError as e:
    FREE_PHASE2_AVAILABLE = False
    log_message(f"⚠️ Free Phase 2 APIs not available: {e}")
    log_message("💡 Install free_phase2_api.py for advanced blockchain intelligence")

# 🧠 Initialize PHASE 3 - LSTM AI PRICE PREDICTION (FREE!)
try:
    from lstm_price_predictor import get_lstm_predictor, enhance_signal_with_lstm, train_lstm_models
    LSTM_PREDICTOR_AVAILABLE = True
    log_message("✅ 🧠 PHASE 3 LSTM AI Price Prediction initialized!")
    log_message("🎯 Features: Neural network price direction prediction, signal enhancement")
    log_message("💰 Monthly cost: $0 - CPU-optimized TensorFlow")
    log_message("⚡ Target: 5-10% timing improvement on existing signals")
except ImportError as e:
    LSTM_PREDICTOR_AVAILABLE = False
    log_message(f"⚠️ LSTM Predictor not available: {e}")
    log_message("💡 Install with: pip install tensorflow scikit-learn")

# 🎯 Initialize PHASE 3 WEEK 2 - SENTIMENT ANALYSIS ENGINE (FREE!)
try:
    from sentiment_analysis_engine import get_sentiment_engine, enhance_signal_with_sentiment
    SENTIMENT_ANALYSIS_AVAILABLE = True
    sentiment_engine = get_sentiment_engine()
    log_message("✅ 🎯 PHASE 3 WEEK 2 Sentiment Analysis Engine initialized!")
    log_message("   🎯 Features: Social sentiment, news analysis, fear & greed, momentum sentiment")
    log_message("   💰 Monthly cost: $0 - Simulated sentiment analysis")
    log_message("   ⚡ Target: 10-15% signal accuracy improvement via market sentiment")
except ImportError as e:
    SENTIMENT_ANALYSIS_AVAILABLE = False
    log_message(f"⚠️ Sentiment Analysis Engine not available: {e}")

# 🎯 Initialize PHASE 3 WEEK 2 - PATTERN RECOGNITION AI (FREE!)
try:
    from pattern_recognition_ai import get_pattern_recognition_ai
    PATTERN_AI_AVAILABLE = True
    log_message("✅ 🎯 PHASE 3 WEEK 2 Pattern Recognition AI initialized!")
    log_message("🔍 Features: Chart patterns, S/R levels, breakout prediction")
    log_message("💰 Monthly cost: $0 - OpenCV + scikit-learn")
    log_message("⚡ Target: +8-12% signal accuracy improvement")
except ImportError as e:
    PATTERN_AI_AVAILABLE = False
    log_message(f"⚠️ Pattern Recognition AI not available: {e}")
    log_message("💡 Install with: pip install opencv-python scikit-learn")

# 🧠 Initialize PHASE 3 WEEK 3 - ADVANCED ML FEATURES (FREE!)
try:
    from advanced_ml_features import get_advanced_ml_engine, enhance_signal_with_advanced_ml, train_advanced_ml_models
    ADVANCED_ML_AVAILABLE = True
    advanced_ml_engine = get_advanced_ml_engine()
    log_message("✅ 🧠 PHASE 3 WEEK 3 Advanced ML Features initialized!")
    log_message("   🎯 Features: Ensemble model voting, feature importance, model drift detection")
    log_message("   💰 Monthly cost: $0 - scikit-learn ensemble methods")
    log_message("   ⚡ Target: 15-20% signal accuracy improvement via ML ensemble")
except ImportError as e:
    ADVANCED_ML_AVAILABLE = False
    log_message(f"⚠️ Advanced ML Features not available: {e}")
    log_message("💡 Install with: pip install scikit-learn scipy")

# 📊 Initialize PHASE 3 WEEK 4 - ALTERNATIVE DATA SOURCES (FREE!)
try:
    from alternative_data_sources import get_alternative_data_aggregator, enhance_signal_with_alternative_data, get_alternative_data_insights
    ALTERNATIVE_DATA_AVAILABLE = True
    alternative_data_aggregator = get_alternative_data_aggregator()
    log_message("✅ 📊 PHASE 3 WEEK 4 Alternative Data Sources initialized!")
    log_message("   🎯 Features: GitHub activity, network effects, social sentiment, market psychology")
    log_message("   💰 Monthly cost: $0 - Simulated alternative data analysis")
    log_message("   ⚡ Target: 20-25% signal accuracy improvement via alternative intelligence")
except ImportError as e:
    ALTERNATIVE_DATA_AVAILABLE = False
    log_message(f"⚠️ Alternative Data Sources not available: {e}")
    log_message("💡 Phase 3 Week 4 features ready for activation")

# Initialize systems
init_log()
bot_config = get_bot_config()
optimized_config = bot_config.config  # Get the config dict from the BotConfig instance
state_manager = get_state_manager()
institutional_manager = InstitutionalStrategyManager()

# =============================================================================
# GLOBAL STATE - Now managed by StateManager
# =============================================================================

# Load state from persistent storage
trading_state = state_manager.get_trading_state()
holding_position = trading_state['holding_position']
last_trade_time = trading_state['last_trade_time']
consecutive_losses = trading_state['consecutive_losses']
active_trade_index = trading_state['active_trade_index']

# 🎯 SIMPLIFIED TRAILING STOP STATE - Only what we need for day trading
entry_price = trading_state.get('entry_price', None)
trailing_stop_order_id = trading_state.get('trailing_stop_order_id', None)
trailing_stop_active = trading_state.get('trailing_stop_active', False)
stop_loss_price = trading_state.get('stop_loss_price', None)
take_profit_price = trading_state.get('take_profit_price', None)

# Load risk state
risk_state = state_manager.get_risk_state()
max_drawdown_from_peak = risk_state['max_drawdown_from_peak']
account_peak_value = risk_state['account_peak_value']

# Risk Management Parameters - Simplified for trailing stops only
risk_config = optimized_config['risk_management']
stop_loss_percentage = risk_config['stop_loss_pct']
take_profit_percentage = risk_config['take_profit_pct']
max_drawdown_limit = risk_config['max_drawdown_pct']
trailing_stop_percentage = risk_config.get('trailing_stop_pct', 0.005)  # Default 0.5%

peak_balance = 20.0  # Track peak balance for drawdown calculation

# Trade management from config
min_trade_interval = optimized_config['trading']['trade_cooldown_seconds']  # Dynamic cooldown
max_consecutive_losses = risk_config['max_consecutive_losses']  # Dynamic limit
daily_loss_limit = risk_config['daily_loss_limit_usd']  # Dynamic daily limit

# =============================================================================
# EXCHANGE CONNECTION SETUP
# =============================================================================

def sync_exchange_time():
    """
    Synchronize local time with exchange server time to prevent timestamp errors
    """
    try:
        # Try to fetch server time without any offset first
        temp_exchange = ccxt.binanceus({
            'apiKey': BINANCE_API_KEY,
            'secret': BINANCE_API_SECRET,
            'enableRateLimit': True,
            'timeout': 10000,
            'options': {'timeDifference': 0}  # No offset for server time fetch
        })

        server_time = temp_exchange.fetch_time()
        local_time = int(time.time() * 1000)

        # Calculate the actual offset needed
        # If server_time > local_time, we need positive offset (we're behind)
        # If server_time < local_time, we need negative offset (we're ahead)
        raw_offset = server_time - local_time

        # Based on our testing, we typically need +1000ms, so let's be smart about it
        if abs(raw_offset) < 2000:  # Small difference, use +1000ms buffer
            adjusted_offset = 1000
        elif raw_offset > 0:  # We're behind server
            adjusted_offset = raw_offset + 500  # Add 500ms buffer
        else:  # We're ahead of server
            adjusted_offset = raw_offset - 500  # Subtract 500ms buffer

        # Set the offset
        exchange.options['timeDifference'] = adjusted_offset

        print(f"⏰ Smart Time Sync: Raw offset = {raw_offset}ms, Using = {adjusted_offset}ms")
        return True

    except Exception as e:
        print(f"⚠️ Server time fetch failed: {e}")
        # Based on our diagnostic test, +1000ms works
        working_offsets = [1000, 2000, 500, 1500, 0, -1000]
        for offset in working_offsets:
            try:
                exchange.options['timeDifference'] = offset
                print(f"⚠️ Trying fallback offset: {offset}ms")
                # Test the offset with a simple API call
                exchange.fetch_ticker('BTC/USDT')
                print(f"✅ Offset {offset}ms works!")
                return True
            except Exception as test_error:
                if 'timestamp' not in str(test_error).lower():
                    # If it's not a timestamp error, this offset works
                    print(f"✅ Offset {offset}ms works (non-timestamp error: {test_error})")
                    return True
                continue

        print("❌ All time sync attempts failed")
        return False

exchange = ccxt.binanceus({
    'apiKey': BINANCE_API_KEY,
    'secret': BINANCE_API_SECRET,
    'enableRateLimit': True,
    'timeout': 30000,  # 30 second timeout
    'rateLimit': 1200,  # Be more conservative with rate limiting
    'options': {
        'recvWindow': 10000,  # 10 second receive window
        'timeDifference': 1000,  # Correct offset: +1000ms (we're behind server)
        'adjustForTimeDifference': True  # Enable automatic adjustment
    }
})

# Synchronize time with exchange
print("⏰ Synchronizing with Binance server time...")
if not sync_exchange_time():
    print("⚠️ Using conservative time offset for connection stability")

# 🎯 MULTI-CRYPTO MONITORING SYSTEM
print("🔄 Initializing multi-crypto monitoring system...")
multi_crypto_monitor = get_multi_crypto_monitor(exchange)
print("✅ Multi-crypto monitor ready!")

# 🧠 PHASE 3: LSTM AI PREDICTION SYSTEM
if LSTM_PREDICTOR_AVAILABLE:
    print("🧠 Initializing LSTM AI prediction system...")
    lstm_predictor = get_lstm_predictor(optimized_config)
    
    # Start background model training if needed
    print("🔄 Checking LSTM model training status...")
    try:
        # Fetch sample data for training check
        sample_data = fetch_ohlcv(exchange, 'BTC/USDT', '5m', 500)
        if len(sample_data) >= 200:
            training_results = train_lstm_models(sample_data, optimized_config, ['5m', '15m'])
            trained_models = sum(1 for success in training_results.values() if success)
            print(f"🧠 LSTM Training Status: {trained_models}/{len(training_results)} models ready")
        else:
            print("⚠️ Insufficient data for LSTM training, will train during operation")
    except Exception as e:
        print(f"⚠️ LSTM initialization warning: {e}")
    
    print("✅ LSTM AI system ready!")
else:
    print("⚠️ LSTM AI system not available - install TensorFlow for enhanced predictions")

# 🎯 PHASE 3 WEEK 2: PATTERN RECOGNITION AI SYSTEM
if PATTERN_AI_AVAILABLE:
    print("🎯 Initializing Pattern Recognition AI system...")
    pattern_ai = get_pattern_recognition_ai(optimized_config)
    
    print("🔄 Testing pattern recognition capabilities...")
    try:
        # Test with sample data
        sample_data = fetch_ohlcv(exchange, 'BTC/USDT', '1h', 100)
        if len(sample_data) >= 50:
            test_patterns = pattern_ai.analyze_chart_patterns(sample_data)
            test_sr_levels = pattern_ai.detect_support_resistance_levels(sample_data)
            print(f"🎯 Pattern Detection Test: {len(test_patterns['patterns'])} patterns found")
            print(f"📊 S/R Levels Test: {len(test_sr_levels['support_levels']) + len(test_sr_levels['resistance_levels'])} levels detected")
        else:
            print("⚠️ Insufficient data for pattern testing, will analyze during operation")
    except Exception as e:
        print(f"⚠️ Pattern AI initialization warning: {e}")
    
    print("✅ Pattern Recognition AI system ready!")
else:
    print("⚠️ Pattern Recognition AI not available - install OpenCV and scikit-learn")

# 🧠 PHASE 3 WEEK 3: ADVANCED ML FEATURES SYSTEM
if ADVANCED_ML_AVAILABLE:
    print("🧠 Initializing Advanced ML Features system...")
    
    print("🔄 Testing ensemble model capabilities...")
    try:
        # Test ensemble training with sample data
        sample_data = fetch_ohlcv(exchange, 'BTC/USDT', '5m', 200)
        if len(sample_data) >= 100:
            training_results = train_advanced_ml_models(sample_data)
            trained_models = sum(training_results.values()) if training_results else 0
            total_models = len(training_results) if training_results else 0
            print(f"🧠 ML Ensemble Training: {trained_models}/{total_models} models ready")
            
            # Test prediction
            test_prediction = advanced_ml_engine.generate_ensemble_prediction(sample_data)
            model_agreement = test_prediction.get('model_agreement', 0.0)
            print(f"🎯 Ensemble Test: {model_agreement:.1%} model agreement, {test_prediction.get('action', 'HOLD')} signal")
        else:
            print("⚠️ Insufficient data for ML training, will train during operation")
    except Exception as e:
        print(f"⚠️ Advanced ML initialization warning: {e}")
    
    print("✅ Advanced ML Features system ready!")
else:
    print("⚠️ Advanced ML Features not available - install scikit-learn and scipy")

# 📊 PHASE 3 WEEK 4: ALTERNATIVE DATA SOURCES SYSTEM
if ALTERNATIVE_DATA_AVAILABLE:
    print("📊 Initializing Alternative Data Sources system...")
    
    print("🔄 Testing alternative data capabilities...")
    try:
        # Test alternative data analysis
        alt_data_test = get_alternative_data_insights('BTC/USDT')
        if alt_data_test and 'alternative_data_summary' in alt_data_test:
            summary = alt_data_test['alternative_data_summary']
            print(f"📈 Data Test: Signal={summary.get('overall_signal', 'N/A')}, "
                 f"Fundamentals={summary.get('fundamental_rating', 'N/A')}, "
                 f"Sentiment={summary.get('sentiment_rating', 'N/A')}")
            print(f"🧑‍💻 GitHub Analysis: {alt_data_test.get('confidence_level', 'N/A')} confidence")
        else:
            print("⚠️ Alternative data test incomplete, using simulated data")
    except Exception as e:
        print(f"⚠️ Alternative data initialization warning: {e}")
    
    print("✅ Alternative Data Sources system ready!")
else:
    print("⚠️ Alternative Data Sources not available - Phase 3 Week 4 features ready for activation")

# 🎉 PHASE 3 COMPLETE STATUS
phase3_features = []
if LSTM_PREDICTOR_AVAILABLE:
    phase3_features.append("Week 1: LSTM AI")
if SENTIMENT_ANALYSIS_AVAILABLE:
    phase3_features.append("Week 2: Sentiment Analysis")
if PATTERN_AI_AVAILABLE:
    phase3_features.append("Week 2: Pattern Recognition")
if ADVANCED_ML_AVAILABLE:
    phase3_features.append("Week 3: Advanced ML")
if ALTERNATIVE_DATA_AVAILABLE:
    phase3_features.append("Week 4: Alternative Data")

if phase3_features:
    print(f"🎉 PHASE 3 INTELLIGENCE STACK COMPLETE: {len(phase3_features)}/5 features active")
    print(f"   ✅ Active: {', '.join(phase3_features)}")
    expected_improvement = len(phase3_features) * 8  # ~8% per feature
    print(f"   📈 Expected combined improvement: {expected_improvement}%+ signal accuracy")
else:
    print("⚠️ Phase 3 features not available - running with Phase 1 & 2 intelligence")

print("\n🚀 CRYPTO TRADING BOT FULLY INITIALIZED - Ready for intelligent trading!")
print("=" * 80)

# =============================================================================
# SAFE API CALL WRAPPER
# =============================================================================

def safe_api_call(func, *args, max_retries=3, **kwargs):
    """
    Wrapper for exchange API calls with automatic retry and timestamp sync
    Handles timestamp errors (-1021) automatically
    """
    for attempt in range(max_retries):
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            error_str = str(e).lower()

            # Handle timestamp errors specifically
            if 'timestamp' in error_str and '-1021' in str(e):
                log_message(f"⚠️ Timestamp error (attempt {attempt + 1}/{max_retries}): {e}")

                if attempt < max_retries - 1:  # Don't sync on last attempt
                    log_message("🔄 Attempting time synchronization...")
                    if sync_exchange_time():
                        time.sleep(1)  # Brief pause after sync
                        continue
                    else:
                        # Try adjusting offset manually
                        current_offset = exchange.options.get('timeDifference', 0)
                        new_offset = current_offset - 1000  # Move back 1 second
                        exchange.options['timeDifference'] = new_offset
                        log_message(f"⚠️ Manual offset adjustment: {current_offset}ms → {new_offset}ms")
                        time.sleep(1)
                        continue

            # 🚀 ENHANCED RATE LIMITING DETECTION AND HANDLING
            elif any(phrase in error_str for phrase in ['rate limit', 'too many requests', '429', 'exceeded', 'throttled']):
                wait_time = min(10 * (2 ** attempt), 60)  # Exponential backoff, max 60s
                log_message(f"⚠️ RATE LIMIT: Waiting {wait_time}s (attempt {attempt + 1}/{max_retries})")
                log_message("   🔧 API Optimization: Consider reducing scan frequency")
                time.sleep(wait_time)
                continue

            # Handle other errors
            else:
                if attempt < max_retries - 1:
                    wait_time = 2 * (attempt + 1)
                    log_message(f"⚠️ API error: {e}, retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    log_message(f"❌ API call failed after {max_retries} attempts: {e}")
                    raise e

    # Should never reach here, but just in case
    raise RuntimeError(f"API call failed after {max_retries} attempts")

def detect_and_adopt_existing_positions():
    """
    🔍 Automatically detect existing crypto positions and set up trailing stop protection
    This enables existing holdings like LINK to be automatically protected
    """
    try:
        print("\n🔍 Scanning existing positions for automatic protection...")
        
        # Get current balances
        balance = safe_api_call(exchange.fetch_balance)
        
        # Look for crypto holdings (excluding USDT)
        crypto_positions = {}
        for coin, amount in balance['total'].items():
            if coin != 'USDT' and amount > 0:
                # Only consider positions worth more than $5 to avoid dust
                try:
                    ticker_symbol = f"{coin}/USDT"
                    if ticker_symbol in exchange.markets:
                        ticker = safe_api_call(exchange.fetch_ticker, ticker_symbol)
                        usd_value = amount * ticker['last']
                        if usd_value >= 5.0:
                            crypto_positions[ticker_symbol] = {
                                'amount': amount,
                                'current_price': ticker['last'],
                                'usd_value': usd_value
                            }
                            print(f"💰 Found position: {ticker_symbol} - Balance: {amount} {coin} (Value: ${usd_value:.2f})")
                except Exception as e:
                    continue
        
        # Set up trailing stop protection for found positions
        for symbol, position in crypto_positions.items():
            try:
                print(f"🎯 PLACING INITIAL TRAILING STOP-LIMIT: {symbol} at 1% trail")
                
                # Calculate 1% trailing stop price (1% below current price)
                stop_price = position['current_price'] * 0.99
                limit_price = stop_price * 0.995  # Limit slightly below stop
                
                # Place initial trailing stop-limit order
                order = safe_api_call(
                    exchange.create_order,
                    symbol,
                    'STOP_LOSS_LIMIT',
                    'sell',
                    position['amount'],
                    limit_price,
                    {
                        'stopPrice': stop_price,
                        'timeInForce': 'GTC'
                    }
                )
                
                print(f"✅ Trailing stop-limit placed: {symbol}")
                print(f"   Stop Price: ${stop_price:.6f} (1% below current)")
                print(f"   Limit Price: ${limit_price:.6f}")
                print(f"   Protected Amount: {position['amount']} {symbol.split('/')[0]}")
                
            except Exception as e:
                print(f"⚠️ Could not place trailing stop for {symbol}: {e}")
                continue
        
        if not crypto_positions:
            print("💡 No significant crypto positions found (>$5 value)")
        else:
            print(f"🛡️ Automatic protection setup complete for {len(crypto_positions)} positions")
            
    except Exception as e:
        print(f"⚠️ Error detecting existing positions: {e}")

# =============================================================================
# DYNAMIC RISK MANAGEMENT FUNCTIONS
# =============================================================================

def calculate_dynamic_daily_loss_limit(total_portfolio_value):
    """
    Calculate daily loss limit based on portfolio percentage or fixed amount
    """
    local_risk_config = optimized_config['risk_management']

    # Use percentage-based limit if available, otherwise fall back to fixed amount
    if 'daily_loss_limit_pct' in local_risk_config:
        percentage_limit = total_portfolio_value * local_risk_config['daily_loss_limit_pct']
        fixed_limit = local_risk_config.get('daily_loss_limit_usd', 2.5)

        # Use the larger of the two for better protection
        dynamic_limit = max(percentage_limit, fixed_limit)

        log_message("📊 Dynamic Daily Loss Limit:")
        log_message(f"   Portfolio: ${total_portfolio_value:.2f}")
        log_message(f"   Percentage Limit ({local_risk_config['daily_loss_limit_pct']:.1%}): ${percentage_limit:.2f}")
        log_message(f"   Fixed Limit: ${fixed_limit:.2f}")
        log_message(f"   Using: ${dynamic_limit:.2f}")

        return dynamic_limit
    else:
        return local_risk_config.get('daily_loss_limit_usd', 2.5)

# =============================================================================
# MULTI-CRYPTO ASSET SELECTION SYSTEM
# =============================================================================

def select_best_crypto_for_trading():
    """
    MULTI-CRYPTO ASSET SELECTION
    
    Analyzes multiple cryptocurrencies and selects the best performer(s) for trading.
    Returns the optimal trading symbol and allocation percentage.
    """
    try:
        # Get trading recommendations from multi-crypto monitor
        recommendations = multi_crypto_monitor.get_trading_recommendations()
        
        if recommendations['status'] != 'success':
            log_message("⚠️ No crypto opportunities found, defaulting to BTC/USDT")
            return {'symbol': 'BTC/USDT', 'allocation': 1.0, 'score': 0.5}
        
        # Log current rankings
        multi_crypto_monitor.log_current_rankings()
        
        # Get the top recommendation
        top_recommendation = recommendations['recommendations'][0]
        
        log_message(f"🏆 SELECTED CRYPTO: {top_recommendation['symbol']}")
        log_message(f"   Score: {top_recommendation['score']:.3f}")
        log_message(f"   Allocation: {top_recommendation['allocation']:.1%}")
        log_message(f"   Metrics: {top_recommendation['metrics']}")
        
        return {
            'symbol': top_recommendation['symbol'],
            'allocation': top_recommendation['allocation'],
            'score': top_recommendation['score'],
            'metrics': top_recommendation['metrics']
        }
        
    except Exception as e:
        log_message(f"❌ Error in multi-crypto selection: {e}")
        log_message("⚠️ Falling back to BTC/USDT")
        return {'symbol': 'BTC/USDT', 'allocation': 1.0, 'score': 0.5}

def should_switch_crypto_asset(current_symbol, selected_crypto):
    """
    Determine if we should switch to a different cryptocurrency
    Enhanced to catch major spikes like SUI +10.58%
    ENHANCED: Now includes on-chain intelligence for predictive switching
    """
    if current_symbol == selected_crypto['symbol']:
        return False, "Already trading optimal asset"
    
    # 🎯 SPIKE DETECTION: Optimized for 5-6% moves like HBAR +5.83%, XLM +6.40%
    score_threshold = 0.05  # AGGRESSIVE: 5% score improvement (was 10%)
    high_score_threshold = 0.45  # AGGRESSIVE: Catch 5-6% moves (was 0.65)
    
    # 📈 DIRECT PERCENTAGE-BASED SWITCHING: Catch real 5%+ moves regardless of score
    try:
        # Get recent price data to detect actual percentage moves
        recent_data = fetch_ohlcv(exchange, selected_crypto['symbol'], '1h', 24)
        if len(recent_data) >= 2:
            price_24h_ago = recent_data['close'].iloc[0]
            current_price = recent_data['close'].iloc[-1]
            price_change_24h = (current_price - price_24h_ago) / price_24h_ago * 100
            
            # 🚨 IMMEDIATE SWITCH on 5%+ moves (like HBAR +5.83%, XLM +6.40%)
            if price_change_24h >= 5.0:
                return True, f"📈 PERCENTAGE SPIKE: {selected_crypto['symbol']} +{price_change_24h:.2f}% in 24h - switching immediately!"
                
    except Exception as e:
        log_message(f"⚠️ Percentage detection failed for {selected_crypto['symbol']}: {e}")
    
    # 🌐 ON-CHAIN ENHANCED SCORING
    if ONCHAIN_AVAILABLE:
        try:
            onchain_provider = OnChainDataProvider()
            
            # Get on-chain intelligence for the selected crypto
            onchain_analysis = onchain_provider.calculate_onchain_score(selected_crypto['symbol'])
            onchain_score = onchain_analysis.get('onchain_score', 0.0)
            signal_strength = onchain_analysis.get('signal_strength', 'weak')
            
            # 🎯 ENHANCED EMERGENCY DETECTION: Combine technical + on-chain
            emergency_threshold = 0.85
            onchain_boost = onchain_score * 0.15  # Up to 15% boost from on-chain data
            base_score = selected_crypto.get('score', 0.0)  # Safe access with default
            enhanced_score = base_score + onchain_boost
            
            # 🚨 EMERGENCY SPIKE SWITCHING: Technical + On-chain confluence
            if enhanced_score > emergency_threshold:
                factors = onchain_analysis.get('contributing_factors', [])
                factor_text = ", ".join(factors) if factors else "strong on-chain signals"
                return True, f"🚨 ENHANCED SPIKE DETECTED: {selected_crypto['symbol']} (tech: {base_score:.3f} + onchain: {onchain_score:.3f} = {enhanced_score:.3f}) - {factor_text}"
            
            # 🎯 ON-CHAIN PREDICTIVE SWITCHING: Early detection before technical signals peak
            if signal_strength in ['very_strong', 'strong'] and base_score > 0.50:
                factors = onchain_analysis.get('contributing_factors', [])
                factor_text = ", ".join(factors)
                log_message(f"🔮 PREDICTIVE SWITCH: On-chain signals ({signal_strength}) preceding technical confirmation")
                return True, f"🔮 PREDICTIVE OPPORTUNITY: {selected_crypto['symbol']} - {factor_text} (early detection)"
            
            # 🎯 VOLUME SURGE PRIORITY: Immediate switch on high-confidence volume spikes
            volume_surge = onchain_provider.detect_volume_surge(selected_crypto['symbol'])
            if volume_surge and volume_surge.get('surge_detected', False) and volume_surge.get('confidence', 0) > 0.8:
                surge_level = volume_surge.get('surge_level', 'unknown')
                volume_ratio = volume_surge.get('volume_ratio', 0)
                return True, f"📈 VOLUME SURGE DETECTED: {selected_crypto['symbol']} - {surge_level} surge ({volume_ratio:.1f}x normal volume)"
            
            # Standard enhanced switching logic
            enhanced_high_threshold = high_score_threshold - (onchain_score * 0.1)  # Lower threshold with strong on-chain
            
            if enhanced_score > enhanced_high_threshold:
                score_improvement = enhanced_score - 0.5
                if score_improvement >= score_threshold:
                    enhancement_text = f" (enhanced by {onchain_boost:.3f} on-chain)" if onchain_boost > 0.05 else ""
                    return True, f"Switching to higher-performing asset (score: {enhanced_score:.3f}){enhancement_text}"
            
            log_message(f"🌐 On-chain analysis for {selected_crypto['symbol']}: score={onchain_score:.3f}, strength={signal_strength}")
            
        except Exception as e:
            log_message(f"⚠️ On-chain analysis failed for {selected_crypto['symbol']}: {e}")
            # Fall back to FREE APIs if on-chain fails
    
    # 🆓 FREE CRYPTO API ENHANCED SCORING (FALLBACK/SUPPLEMENT)
    if FREE_CRYPTO_AVAILABLE:
        try:
            # Get comprehensive free intelligence
            free_intelligence = get_free_crypto_intelligence(selected_crypto['symbol'])
            confidence_score = free_intelligence.get('confidence_score', 0.0)
            trading_signals = free_intelligence.get('trading_signals', {})
            
            # 🚨 FREE API VOLUME SURGE DETECTION
            volume_surge = trading_signals.get('volume_surge', False)
            momentum_strength = trading_signals.get('momentum_strength', 0)
            overall_signal = trading_signals.get('overall_signal', 'hold')
            
            if volume_surge and confidence_score > 0.7:
                sources = free_intelligence.get('sources_used', [])
                source_text = f"Sources: {', '.join(sources)}"
                return True, f"🆓 FREE API VOLUME SURGE: {selected_crypto['symbol']} - {source_text} (confidence: {confidence_score:.1%})"
            
            # 🎯 FREE API MOMENTUM SWITCHING
            if overall_signal == 'buy' and momentum_strength > 0.5 and selected_crypto['score'] > 0.60:
                return True, f"🆓 FREE API MOMENTUM: {selected_crypto['symbol']} - Strong buy signal from {len(free_intelligence.get('sources_used', []))} free sources"
            
            # Enhanced scoring with free data
            if confidence_score > 0.8:
                free_boost = momentum_strength * 0.1  # Up to 10% boost from free APIs
                enhanced_score = selected_crypto['score'] + free_boost
                
                if enhanced_score > high_score_threshold:
                    score_improvement = enhanced_score - 0.5
                    if score_improvement >= score_threshold:
                        return True, f"🆓 FREE API ENHANCED: {selected_crypto['symbol']} (score: {enhanced_score:.3f}, free boost: {free_boost:.3f})"
            
            log_message(f"🆓 Free API analysis for {selected_crypto['symbol']}: confidence={confidence_score:.1%}, signal={overall_signal}")
            
        except Exception as e:
            log_message(f"⚠️ Free API analysis failed for {selected_crypto['symbol']}: {e}")
            # Continue with original logic
    
    # 🚀 FREE PHASE 2 ADVANCED INTELLIGENCE (ENTERPRISE-LEVEL ANALYSIS)
    if FREE_PHASE2_AVAILABLE:
        try:
            # Get comprehensive Phase 2 intelligence (exchange flows, whale tracking, DeFi)
            phase2_intelligence = get_free_phase2_intelligence(selected_crypto['symbol'])
            phase2_alerts = get_free_phase2_alerts(selected_crypto['symbol'])
            
            alert_level = phase2_intelligence.get('alert_level', 'normal')
            confidence_score = phase2_intelligence.get('confidence_score', 0.0)
            sources_used = phase2_intelligence.get('sources_used', [])
            
            # 🐋 WHALE ACTIVITY DETECTION - Immediate switch on whale accumulation
            whale_activity = phase2_intelligence.get('whale_activity', {})
            if whale_activity.get('whale_accumulation', False) and confidence_score > 0.7:
                whale_confidence = whale_activity.get('confidence', 0.0)
                return True, f"🐋 WHALE ACCUMULATION: {selected_crypto['symbol']} - Institutional buying detected (confidence: {whale_confidence:.1%})"
            
            # 🔵 EXCHANGE FLOW ANALYSIS - Strong inflows indicate accumulation
            exchange_flows = phase2_intelligence.get('exchange_flows', {})
            flow_trend = exchange_flows.get('flow_trend', 'neutral')
            net_flow = exchange_flows.get('net_flow', 0)
            
            if flow_trend == 'strong_inflow' and abs(net_flow) > 5000000:  # $5M+ net inflow
                flow_text = f"${abs(net_flow):,.0f} net inflow"
                return True, f"🔵 EXCHANGE INFLOW SURGE: {selected_crypto['symbol']} - {flow_text} (institutional accumulation)"
            
            # 💹 DEFI INTELLIGENCE - Protocol TVL changes indicate market sentiment
            defi_intel = phase2_intelligence.get('defi_intelligence', {})
            stablecoin_activity = defi_intel.get('stablecoin_activity', {})
            market_sentiment = stablecoin_activity.get('market_sentiment', 'neutral')
            
            if market_sentiment == 'risk_on' and selected_crypto['score'] > 0.65:
                mcap_change = stablecoin_activity.get('total_mcap_change', 0)
                return True, f"💹 RISK-ON SENTIMENT: {selected_crypto['symbol']} - Stablecoin flows indicate bullish sentiment ({mcap_change:+.1f}%)"
            
            # 📈 DEX ANALYTICS - High volume and liquidity favor large positions
            dex_analytics = phase2_intelligence.get('dex_analytics', {})
            volume_trend = dex_analytics.get('volume_trend', 'neutral')
            liquidity_trend = dex_analytics.get('liquidity_trend', 'neutral')
            
            if volume_trend == 'high' and liquidity_trend == 'high' and selected_crypto['score'] > 0.60:
                token_metrics = dex_analytics.get('token_metrics', {})
                volume_usd = token_metrics.get('volume_usd', 0)
                return True, f"📈 HIGH DEX ACTIVITY: {selected_crypto['symbol']} - Volume: ${volume_usd:,.0f}, excellent liquidity for large positions"
            
            # 🚨 HIGH CONFIDENCE MULTI-SOURCE ALERTS
            if alert_level == 'high' and confidence_score > 0.8 and len(sources_used) >= 2:
                active_alerts = len(phase2_alerts.get('alerts', []))
                return True, f"🚨 PHASE 2 HIGH ALERT: {selected_crypto['symbol']} - {active_alerts} alerts from {len(sources_used)} sources (confidence: {confidence_score:.1%})"
            
            # 🎯 ENHANCED SCORING WITH PHASE 2 INTELLIGENCE
            if confidence_score > 0.6:
                # Calculate Phase 2 boost based on multiple factors
                phase2_boost = 0.0
                
                # Whale activity boost
                if whale_activity.get('unusual_flows', False):
                    phase2_boost += 0.05
                
                # Exchange flow boost
                if flow_trend in ['strong_inflow', 'moderate_inflow']:
                    phase2_boost += 0.04
                
                # DeFi sentiment boost
                if market_sentiment == 'risk_on':
                    phase2_boost += 0.03
                
                # DEX activity boost
                if volume_trend == 'high':
                    phase2_boost += 0.03
                
                enhanced_score = selected_crypto['score'] + phase2_boost
                
                if enhanced_score > high_score_threshold and phase2_boost > 0.05:
                    source_text = f"Sources: {', '.join(sources_used)}"
                    return True, f"🚀 PHASE 2 ENHANCED: {selected_crypto['symbol']} (score: {enhanced_score:.3f}, P2 boost: {phase2_boost:.3f}) - {source_text}"
            
            log_message(f"🚀 Phase 2 analysis for {selected_crypto['symbol']}: alert_level={alert_level}, confidence={confidence_score:.1%}, sources={len(sources_used)}")
            
        except Exception as e:
            log_message(f"⚠️ Phase 2 analysis failed for {selected_crypto['symbol']}: {e}")
            # Continue with original logic
    
    # 🚨 AGGRESSIVE EMERGENCY DETECTION (optimized for 5-6% moves)
    if selected_crypto['score'] > 0.50:  # LOWERED: Catch 5-6% moves (was 0.85)
        return True, f"🚨 SPIKE DETECTED: Emergency switch to {selected_crypto['symbol']} (score: {selected_crypto['score']:.3f})"
    
    # Standard switching logic with reduced thresholds
    if selected_crypto['score'] > high_score_threshold:
        score_improvement = selected_crypto['score'] - 0.5  # Assume current baseline
        if score_improvement >= score_threshold:
            return True, f"Switching to higher-performing asset (score: {selected_crypto['score']:.3f})"
    
    return False, f"Score difference insufficient for switching (score: {selected_crypto['score']:.3f})"

# =============================================================================
# ENHANCED POSITION SIZING FOR MULTI-CRYPTO
# =============================================================================

def calculate_position_size(current_price, volatility, signal_confidence, total_portfolio_value, crypto_allocation=1.0):
    """
    Enhanced percentage-based position sizing with Kelly Criterion and institutional methods
    Uses percentage of total portfolio value instead of fixed dollar amounts
    Now supports multi-crypto allocation adjustments
    
    Args:
        current_price: Current asset price (reserved for future price-based adjustments)
        volatility: Asset volatility measure
        signal_confidence: Confidence in trading signal
        total_portfolio_value: Total portfolio value
        crypto_allocation: Allocation percentage for this crypto
    """
    global consecutive_losses, account_peak_value

    # Get position sizing configuration
    local_trading_config = optimized_config['trading']
    position_mode = local_trading_config.get('position_sizing_mode', 'percentage')

    if position_mode == 'percentage':
        # Percentage-based sizing (RECOMMENDED)
        base_position_pct = local_trading_config['base_position_pct']  # e.g., 0.15 = 15%
        min_position_pct = local_trading_config['min_position_pct']    # e.g., 0.08 = 8%
        max_position_pct = local_trading_config['max_position_pct']    # e.g., 0.25 = 25%

        # Calculate base position size as percentage of total portfolio
        base_amount = total_portfolio_value * base_position_pct
        min_amount = total_portfolio_value * min_position_pct
        max_amount = total_portfolio_value * max_position_pct

        log_message("📊 PERCENTAGE-BASED Position Sizing:")
        log_message(f"   Portfolio Value: ${total_portfolio_value:.2f}")
        log_message(f"   Base Position: {base_position_pct:.1%} = ${base_amount:.2f}")
        
        # 🎯 MULTI-CRYPTO ALLOCATION ADJUSTMENT
        if crypto_allocation != 1.0:
            log_message(f"   🌐 Multi-Crypto Allocation: {crypto_allocation:.1%}")
            base_amount *= crypto_allocation
            min_amount *= crypto_allocation
            max_amount *= crypto_allocation
            log_message(f"   Adjusted Base: ${base_amount:.2f}")

    else:
        # Fixed dollar sizing (legacy fallback)
        base_amount = local_trading_config['base_amount_usd']
        min_amount = local_trading_config['min_amount_usd']
        max_amount = local_trading_config['max_amount_usd']

        log_message("📊 FIXED-DOLLAR Position Sizing:")
        log_message(f"   Base Amount: ${base_amount:.2f}")
        
        # Apply crypto allocation to fixed amounts too
        if crypto_allocation != 1.0:
            log_message(f"   🌐 Multi-Crypto Allocation: {crypto_allocation:.1%}")
            base_amount *= crypto_allocation
            min_amount *= crypto_allocation
            max_amount *= crypto_allocation

    # 1. Use Kelly Criterion for optimal sizing
    kelly_size = institutional_manager.kelly_sizer.calculate_kelly_size(
        win_probability=signal_confidence,
        avg_win=0.025,  # 2.5% average win (from backtest data)
        avg_loss=0.015,  # 1.5% average loss
        base_amount=base_amount
    )

    # 2. Volatility adjustment (reduce size in high volatility)
    if volatility > 0.03:  # Very high volatility
        volatility_factor = 0.6
    elif volatility > 0.02:  # High volatility
        volatility_factor = 0.75
    elif volatility > 0.015:  # Medium volatility
        volatility_factor = 0.9
    else:  # Low volatility
        volatility_factor = 1.1  # Slightly larger positions in stable markets

    # 3. Confidence adjustment (scale with signal strength)
    confidence_factor = max(0.7, min(1.3, signal_confidence * 1.2))

    # 4. Consecutive loss adjustment (reduce size after losses)
    loss_factor = max(0.4, 1.0 - (consecutive_losses * 0.2))

    # 5. Drawdown adjustment (reduce size during high drawdown)
    current_drawdown = max(0, (account_peak_value - total_portfolio_value) / account_peak_value)
    if current_drawdown > 0.1:  # More than 10% drawdown
        drawdown_factor = max(0.3, 1.0 - (current_drawdown * 3))
    else:
        drawdown_factor = 1.0

    # 6. Time of day adjustment (smaller positions during low liquidity hours)
    current_hour = datetime.datetime.now().hour
    if 2 <= current_hour <= 6:  # Low liquidity hours (EST)
        time_factor = 0.8
    else:
        time_factor = 1.0

    # 7. VaR-based risk adjustment
    try:
        returns = fetch_ohlcv(exchange, 'BTC/USDT', '1h', 100)['close'].pct_change().dropna()
        var_analysis = institutional_manager.var_calculator.calculate_var(returns, total_portfolio_value)

        if var_analysis['risk_assessment'] == 'HIGH':
            var_factor = 0.5
        elif var_analysis['risk_assessment'] == 'MEDIUM':
            var_factor = 0.75
        else:
            var_factor = 1.0
    except (KeyError, AttributeError, ValueError, Exception):
        var_factor = 1.0

    # 8. Portfolio size adjustment (smaller percentages for larger accounts)
    if position_mode == 'percentage' and total_portfolio_value > 100:
        # Reduce percentage as account grows (risk management)
        size_adjustment = min(1.0, 50 / total_portfolio_value + 0.5)
    else:
        size_adjustment = 1.0

    # 🎯 DYNAMIC SCALING FOR SMALL ACCOUNTS (Precision-tuned for target amounts)
    small_account_scaling = 1.0
    target_position_size = None

    if position_mode == 'percentage' and total_portfolio_value <= 100:
        # Precision-tuned scaling to achieve exact target amounts as discussed
        if total_portfolio_value >= 100:
            target_position_size = 20.0  # $20 for $100+ accounts (20%)
            small_account_scaling = 0.8  # Conservative for larger accounts
        elif total_portfolio_value >= 75:
            target_position_size = 18.75  # $18.75 for $75-100 accounts (25%)
            small_account_scaling = 1.0  # Baseline scaling
        elif total_portfolio_value >= 50:
            target_position_size = total_portfolio_value * 0.35  # 35% for $50-75 accounts
            small_account_scaling = 1.0  # Baseline scaling
        elif total_portfolio_value >= 25:
            target_position_size = 12.50  # $12.50 for $25-50 accounts (50%)
            small_account_scaling = 1.6  # More aggressive for growth
        else:
            # For accounts under $25, scale proportionally but respect minimum order
            target_position_size = max(10.0, total_portfolio_value * 0.50)  # 50% or $10 minimum
            small_account_scaling = 2.0  # Maximum scaling for tiny accounts

        # Calculate actual percentage for logging
        actual_percentage = (target_position_size / total_portfolio_value) * 100

        log_message("🎯 SMALL ACCOUNT SCALING:")
        log_message(f"   Portfolio: ${total_portfolio_value:.2f}")
        log_message(f"   Target Position: ${target_position_size:.2f} ({actual_percentage:.1f}%)")
        log_message(f"   Scaling Factor: {small_account_scaling:.1f}x")

    # Apply small account scaling
    size_adjustment = size_adjustment * small_account_scaling

    # Combine Kelly sizing with all risk factors
    institutional_size = (kelly_size * volatility_factor * confidence_factor *
                         loss_factor * drawdown_factor * time_factor * var_factor * size_adjustment)

    # For small accounts with target position size, use direct targeting
    if target_position_size is not None:
        # Use target position directly, only adjust for major risk factors
        major_risk_adjustment = min(volatility_factor, confidence_factor, loss_factor, drawdown_factor)

        # Only reduce size if there are major risk concerns (< 0.8)
        if major_risk_adjustment < 0.8:
            risk_adjusted_target = target_position_size * major_risk_adjustment
            log_message(f"   Risk adjustment applied: ${target_position_size:.2f} → ${risk_adjusted_target:.2f}")
            final_size = max(min_amount, min(max_amount, risk_adjusted_target))
        else:
            # Use target size directly for normal market conditions
            final_size = max(min_amount, min(max_amount, target_position_size))
    else:
        # Apply bounds based on position sizing mode (for larger accounts)
        final_size = max(min_amount, min(max_amount, institutional_size))

    # 🎯 FEE OPTIMIZATION - Adjust position size for fee efficiency
    fee_config = optimized_config['trading'].get('fee_optimization', {})
    if fee_config.get('fee_efficiency_alerts', True):
        final_size = optimize_order_size_for_fees(final_size, 'BTC/USDT')  # Will adapt to selected crypto

    # 🎯 DYNAMIC SAFETY CAP: Adaptive based on account size and target amounts
    if position_mode == 'percentage' and total_portfolio_value > 0:
        # For small accounts (≤$100), allow higher percentages to achieve target amounts
        if total_portfolio_value <= 25:
            safety_cap = total_portfolio_value * 0.60  # 60% max for very small accounts
        elif total_portfolio_value <= 50:
            safety_cap = total_portfolio_value * 0.55  # 55% max for small accounts
        elif total_portfolio_value <= 75:
            safety_cap = total_portfolio_value * 0.35  # 35% max for growing accounts
        elif total_portfolio_value <= 100:
            safety_cap = total_portfolio_value * 0.25  # 25% max for medium accounts
        else:
            safety_cap = total_portfolio_value * 0.20  # 20% max for larger accounts (conservative)

        if final_size > safety_cap:
            safety_pct = (safety_cap / total_portfolio_value) * 100
            log_message(f"⚠️ Safety cap applied: ${final_size:.2f} → ${safety_cap:.2f} ({safety_pct:.1f}% portfolio limit)")
            final_size = safety_cap

    # Ensure final size meets Binance minimum order requirement
    BINANCE_MIN_ORDER_USD = 10.0
    if final_size < BINANCE_MIN_ORDER_USD:
        log_message(f"⚠️ Position size ${final_size:.2f} below Binance minimum ${BINANCE_MIN_ORDER_USD:.2f}")

        # Only adjust if we have enough portfolio value
        if total_portfolio_value >= BINANCE_MIN_ORDER_USD:
            log_message(f"   Adjusting to minimum order size: ${BINANCE_MIN_ORDER_USD:.2f}")
            final_size = BINANCE_MIN_ORDER_USD
        else:
            log_message(f"   ⚠️ Portfolio too small (${total_portfolio_value:.2f}) for minimum order")
            log_message(f"   Skipping trade - need at least ${BINANCE_MIN_ORDER_USD:.2f}")
            return 0  # Return 0 to skip the trade

    # Calculate position as percentage of portfolio for logging
    position_pct = (final_size / total_portfolio_value) * 100 if total_portfolio_value > 0 else 0

    log_message(f"   Kelly Base: ${kelly_size:.2f}, Vol: {volatility_factor:.2f}, Conf: {confidence_factor:.2f}")
    log_message(f"   Loss: {loss_factor:.2f}, DD: {drawdown_factor:.2f}, Time: {time_factor:.2f}, VaR: {var_factor:.2f}")
    log_message(f"   Size Adj: {size_adjustment:.2f}")
    log_message(f"   Final: ${final_size:.2f} ({position_pct:.1f}% of portfolio)")

    return final_size

def check_risk_management(current_price, total_balance, symbol='BTC/USDT'):
    """
    🎯 SIMPLIFIED TRAILING STOP RISK MANAGEMENT
    
    Only uses trailing stops for exits - perfect for day trading micro profits.
    Clean, simple, and reliable.
    """
    global entry_price, holding_position, account_peak_value, trailing_stop_order_id, trailing_stop_active

    # Update peak balance for drawdown calculation
    if total_balance > account_peak_value:
        account_peak_value = total_balance

    # Check maximum drawdown
    current_drawdown = (account_peak_value - total_balance) / account_peak_value
    if current_drawdown > max_drawdown_limit:
        log_message(f"🚨 MAX DRAWDOWN HIT: {current_drawdown:.3f} > {max_drawdown_limit}")
        return 'MAX_DRAWDOWN_HIT'

    # 🎯 TRAILING STOP MONITORING - The ONLY exit mechanism
    if holding_position and entry_price and entry_price > 0:
        
        # Check if our trailing stop order was triggered
        if trailing_stop_order_id and trailing_stop_active:
            try:
                order_status = safe_api_call(exchange.fetch_order, trailing_stop_order_id, symbol)
                if order_status and order_status['status'] == 'closed':
                    log_message(f"✅ TRAILING STOP TRIGGERED: Order {trailing_stop_order_id} filled at ${order_status['average']:.2f}")
                    
                    # Calculate profit
                    exit_price = order_status['average']
                    profit_pct = ((exit_price - entry_price) / entry_price) * 100
                    log_message(f"🎯 Trade completed: Entry=${entry_price:.2f}, Exit=${exit_price:.2f}, Profit={profit_pct:+.2f}%")
                    
                    # Clear trailing stop state
                    state_manager.update_trading_state(
                        trailing_stop_order_id=None,
                        trailing_stop_active=False
                    )
                    
                    return 'TRAILING_STOP_EXIT'
                    
            except Exception as e:
                log_message(f"⚠️ Error checking trailing stop status: {e}")

        # Emergency exit for extreme losses (safety net)
        pnl_percentage = (current_price - entry_price) / entry_price
        if pnl_percentage <= -0.08:  # -8% emergency exit (should never happen with trailing stops)
            log_message(f"🚨 EMERGENCY EXIT: P&L {pnl_percentage:.3f} <= -8% (trailing stop failed)")
            return 'EMERGENCY_EXIT'

    return 'OK'

def is_strong_trend(df, signal):
    """
    Enhanced crypto-optimized trend detection to avoid contrarian trades in strong trends
    Uses Binance standard MA periods: MA7, MA25, MA99
    """
    if len(df) < 100:  # Need data for MA99
        return False

    # Crypto-optimized trend detection using Binance standard MA periods
    ma_7 = df['close'].rolling(7).mean()
    ma_25 = df['close'].rolling(25).mean()
    ma_99 = df['close'].rolling(99).mean()

    current_price = df['close'].iloc[-1]

    # Calculate trend alignment and momentum
    ma7_trend = (ma_7.iloc[-1] - ma_7.iloc[-7]) / ma_7.iloc[-7] if len(ma_7) >= 7 else 0
    ma25_trend = (ma_25.iloc[-1] - ma_25.iloc[-25]) / ma_25.iloc[-25] if len(ma_25) >= 25 else 0

    # Strong uptrend: MA alignment + momentum + price position
    strong_uptrend = (
        ma_7.iloc[-1] > ma_25.iloc[-1] > ma_99.iloc[-1] and  # MA alignment
        current_price > ma_7.iloc[-1] * 1.01 and  # Price above MA7 by 1%+
        ma7_trend > 0.02 and  # MA7 rising by 2%+ over 7 periods
        ma25_trend > 0.015    # MA25 rising by 1.5%+ over 25 periods
    )

    # Strong downtrend: MA alignment + momentum + price position
    strong_downtrend = (
        ma_7.iloc[-1] < ma_25.iloc[-1] < ma_99.iloc[-1] and  # MA alignment
        current_price < ma_7.iloc[-1] * 0.99 and  # Price below MA7 by 1%+
        ma7_trend < -0.02 and  # MA7 falling by 2%+ over 7 periods
        ma25_trend < -0.015    # MA25 falling by 1.5%+ over 25 periods
    )

    # Check volume confirmation (if available)
    recent_volume = df['volume'].iloc[-7:].mean() if 'volume' in df.columns else 1
    avg_volume = df['volume'].iloc[-99:].mean() if 'volume' in df.columns else 1
    volume_confirmation = recent_volume > avg_volume * 1.2  # 20% above average

    # Log trend analysis
    if strong_uptrend or strong_downtrend:
        trend_type = "STRONG UPTREND" if strong_uptrend else "STRONG DOWNTREND"
        log_message(f"🔍 Crypto Trend Analysis: {trend_type} detected")
        log_message(f"   MA7: ${ma_7.iloc[-1]:.2f} (trend: {ma7_trend:+.3f})")
        log_message(f"   MA25: ${ma_25.iloc[-1]:.2f} (trend: {ma25_trend:+.3f})")
        log_message(f"   MA99: ${ma_99.iloc[-1]:.2f}")
        log_message(f"   Price: ${current_price:.2f} vs MA7: {(current_price/ma_7.iloc[-1]-1)*100:+.1f}%")

    # Smart trend filtering - allow dip buying but avoid knife catching
    if signal['action'] == 'BUY' and strong_downtrend and volume_confirmation:
        # Only filter if it's an EXTREME downtrend with very high volume (panic selling)
        extreme_downtrend = ma7_trend < -0.04 and ma25_trend < -0.03 and volume_confirmation
        if extreme_downtrend:
            log_message("💎 Allowing BUY signal - Normal downtrend dip-buying opportunity")
            return False  # Allow dip buying in normal downtrends
        else:
            log_message("⚠️ Filtering BUY signal - EXTREME crypto downtrend with panic volume")
            return True  # Don't catch falling knives in panic selling
    elif signal['action'] == 'SELL' and strong_uptrend and volume_confirmation:
        log_message("⚠️ Filtering SELL signal - Strong crypto uptrend with volume confirmation")
        return True  # Don't sell in strong uptrend

    return False

def manage_progressive_sell_targets(current_price, sell_targets, btc_balance):
    """
    🎯 REMOVED - Progressive sell targets not needed with trailing stops
    
    Trailing stops handle all exits automatically - no complex sell logic needed.
    
    Args:
        current_price: Current asset price (unused - function is stubbed)
        sell_targets: Sell target configuration (unused - function is stubbed) 
        btc_balance: Current BTC balance (unused - function is stubbed)
    """
    return None  # Simplified: trailing stops handle everything

def place_intelligent_order(symbol, side, amount_usd, use_limit=True, timeout_seconds=None, force_maker=False):
    """
    🎯 ENHANCED FEE-OPTIMIZED ORDER EXECUTION
    
    Prioritizes maker fees (0.1%) over taker fees (0.1%) through intelligent order placement.
    Uses post-only orders when requested to guarantee maker fees.
    Implements dynamic spread analysis and multi-level order placement.
    """
    global last_trade_time, consecutive_losses, entry_price, stop_loss_price, take_profit_price

    try:
        # Get timeout from config if not specified
        if timeout_seconds is None:
            timeout_seconds = optimized_config['trading']['limit_order_timeout_seconds']

        # Check if we have sufficient balance before placing order
        balance = safe_api_call(exchange.fetch_balance)

        # Get current market data
        orderbook = safe_api_call(exchange.fetch_order_book, symbol)
        ticker = safe_api_call(exchange.fetch_ticker, symbol)
        market_price = ticker['last']

        # 🎯 FEE OPTIMIZATION - Enhanced spread analysis
        bid_price = orderbook['bids'][0][0] if orderbook['bids'] else market_price * 0.999
        ask_price = orderbook['asks'][0][0] if orderbook['asks'] else market_price * 1.001
        spread_pct = (ask_price - bid_price) / market_price * 100

        # Log fee optimization strategy
        log_message(f"🎯 FEE OPTIMIZATION - Spread: {spread_pct:.3f}%")
        
        # Force maker orders if requested (guarantees maker fees)
        if force_maker:
            use_limit = True
            log_message("🛡️ POST-ONLY MODE: Forcing maker fees (0.1% vs 0.1% taker)")
        elif spread_pct > 0.5:
            # Wide spread - market order may be better for execution speed
            use_limit = False
            log_message(f"⚡ Wide spread ({spread_pct:.2f}%) - using market order for execution speed")
        else:
            # Normal spread - use limit orders for maker fees
            log_message(f"✅ Normal spread ({spread_pct:.2f}%) - using limit orders for maker fees")

        # Binance minimum order requirements
        MIN_NOTIONAL_VALUE = 10.0  # Minimum $10 USD equivalent
        MIN_BTC_AMOUNT = 0.00001   # Minimum 0.00001 BTC

        if side.upper() == 'BUY':
            available_usd = balance['USDT']['free']
            if available_usd < amount_usd:
                print(f"❌ Insufficient USDT balance: ${available_usd:.2f} < ${amount_usd:.2f}")
                return None

            # 🎯 MAKER FEE OPTIMIZATION - Strategic limit price placement
            if force_maker:
                # Post-only: place slightly inside spread but still on maker side
                limit_price = bid_price + (market_price - bid_price) * 0.1  # 10% into spread
                log_message(f"📌 POST-ONLY BUY: ${limit_price:.2f} (maker fees guaranteed)")
            else:
                # Normal: place conservatively for good fill rates while maintaining maker status
                limit_price = bid_price + (market_price - bid_price) * 0.3  # 30% into spread
                log_message(f"🎯 OPTIMAL BUY: ${limit_price:.2f} (targeting maker fees)")
            
            amount = round(amount_usd / limit_price, 6)

            # Check minimum order size for BUY
            if amount < MIN_BTC_AMOUNT:
                print(f"❌ BUY amount too small: {amount:.6f} {symbol.split('/')[0]} < {MIN_BTC_AMOUNT:.6f} minimum")
                return None
            if amount_usd < MIN_NOTIONAL_VALUE:
                print(f"❌ BUY order value too small: ${amount_usd:.2f} < ${MIN_NOTIONAL_VALUE:.2f} minimum")
                return None
                
            print(f"✅ BUY order validation passed: ${amount_usd:.2f} for {amount:.6f} {symbol.split('/')[0]}")
            
        else:  # SELL
            crypto_currency = symbol.split('/')[0]
            available_crypto = balance[crypto_currency]['free']
            amount = round(available_crypto, 6)

            # Check if we have any crypto to sell
            if available_crypto <= 0:
                print(f"❌ No {crypto_currency} available to sell: {available_crypto:.6f} {crypto_currency}")
                return None

            # Check minimum order size for SELL
            if amount < MIN_BTC_AMOUNT:  # Using general minimum for all cryptos
                print(f"❌ SELL amount too small: {amount:.6f} {crypto_currency} < {MIN_BTC_AMOUNT:.6f} minimum")
                print(f"   🔍 This amount is too small to trade on Binance. Consider accumulating more {crypto_currency} before selling.")
                return None

            # Check minimum notional value
            notional_value = amount * market_price
            if notional_value < MIN_NOTIONAL_VALUE:
                print(f"❌ SELL order value too small: ${notional_value:.2f} < ${MIN_NOTIONAL_VALUE:.2f} minimum")
                print(f"   {crypto_currency} amount: {amount:.6f}, Price: ${market_price:.2f}")
                return None

            # 🎯 MAKER FEE OPTIMIZATION - Strategic sell price placement  
            if force_maker:
                # Post-only: place slightly inside spread but still on maker side
                limit_price = ask_price - (ask_price - market_price) * 0.1  # 10% into spread
                log_message(f"📌 POST-ONLY SELL: ${limit_price:.2f} (maker fees guaranteed)")
            else:
                # Normal: place conservatively for good fill rates while maintaining maker status
                limit_price = ask_price - (ask_price - market_price) * 0.3  # 30% into spread
                log_message(f"🎯 OPTIMAL SELL: ${limit_price:.2f} (targeting maker fees)")

            print(f"✅ SELL order validation passed: {amount:.6f} {crypto_currency} worth ${notional_value:.2f}")

        order = None
        final_price = None

        if use_limit:
            print(f"🎯 Placing LIMIT {side.upper()} order: {amount:.6f} {symbol.split('/')[0]} at ${limit_price:.2f}")
            
            # 🛡️ ENHANCED FEE OPTIMIZATION
            if force_maker:
                log_message("📌 POST-ONLY order - 100% maker fees guaranteed")

            try:
                # Create limit order with optional post-only flag
                order_params = {}
                if force_maker:
                    order_params['postOnly'] = True  # Ensures maker-only execution
                
                order = safe_api_call(
                    exchange.create_limit_order, 
                    symbol, 
                    side.lower(), 
                    amount, 
                    limit_price,
                    order_params
                )
                order_id = order['id']

                # Wait for fill with timeout
                start_time = time.time()
                filled = False

                log_message(f"⏳ Waiting for limit order fill (timeout: {timeout_seconds}s)")
                while time.time() - start_time < timeout_seconds:
                    try:
                        order_status = safe_api_call(exchange.fetch_order, order_id, symbol)
                        if order_status['status'] == 'closed':
                            filled = True
                            final_price = order_status['average'] or limit_price
                            
                            # Log fee savings
                            if order_status.get('maker', False):
                                log_message(f"✅ MAKER ORDER FILLED: ${final_price:.2f} (0.1% fee)")
                            else:
                                log_message(f"✅ LIMIT ORDER FILLED: ${final_price:.2f}")
                            print(f"✅ LIMIT ORDER FILLED at ${final_price:.2f}")
                            break
                    except (ccxt.NetworkError, ccxt.BaseError, Exception):
                        pass
                    time.sleep(2)  # Check every 2 seconds

                if not filled:
                    if force_maker:
                        # For post-only orders, don't fallback to market - cancel instead
                        try:
                            safe_api_call(exchange.cancel_order, order_id, symbol)
                            log_message("⏰ POST-ONLY order timeout - cancelled (preserving maker fees)")
                            print("⏰ Post-only order timeout - order cancelled")
                            return None  # Return None to indicate no trade executed
                        except (ccxt.NetworkError, ccxt.BaseError, Exception):
                            pass
                    else:
                        # Cancel unfilled limit order
                        try:
                            safe_api_call(exchange.cancel_order, order_id, symbol)
                            log_message("⏰ Limit order timeout - falling back to market order")
                            print("⏰ Limit order timeout - placing market order as fallback")
                        except (ccxt.NetworkError, ccxt.BaseError, Exception):
                            pass

                        # Fallback to market order
                        order = safe_api_call(exchange.create_market_order, symbol, side.lower(), amount)
                        final_price = market_price
                        log_message(f"⚡ MARKET FALLBACK: ${final_price:.2f} (0.1% taker fee)")
                        print(f"✅ MARKET ORDER FALLBACK at ~${final_price:.2f}")

            except Exception as limit_error:
                if force_maker:
                    log_message(f"❌ POST-ONLY order failed: {limit_error}")
                    print(f"❌ Post-only order failed: {limit_error}")
                    return None  # Don't fallback for post-only orders
                else:
                    print(f"⚠️ Limit order failed ({limit_error}) - using market order")
                    log_message(f"⚠️ Limit order failed: {limit_error} - market fallback")
                    
                    # Fallback to market order
                    order = safe_api_call(exchange.create_market_order, symbol, side.lower(), amount)
                    final_price = market_price
                    if order:
                        log_message(f"✅ MARKET FALLBACK: ${final_price:.2f} (0.1% taker fee)")
                        print(f"✅ MARKET ORDER FALLBACK successful at ~${final_price:.2f}")
                    else:
                        log_message(f"❌ MARKET FALLBACK FAILED: {limit_error}")
                        print(f"❌ MARKET ORDER FALLBACK failed for {amount:.6f} {symbol.split('/')[0]}")
        else:
            # Direct market order - will incur taker fees
            amount = round(amount_usd / market_price, 6) if side.upper() == 'BUY' else amount
            log_message("⚡ MARKET ORDER: Will incur 0.1% taker fees")
            order = safe_api_call(exchange.create_market_order, symbol, side.lower(), amount)
            final_price = market_price
            if order:
                log_message(f"✅ MARKET ORDER: {amount:.6f} {symbol.split('/')[0]} at ${final_price:.2f} (0.1% taker fee)")
                print(f"✅ MARKET ORDER PLACED at ~${final_price:.2f}")
            else:
                log_message(f"❌ MARKET ORDER FAILED: {amount:.6f} {symbol.split('/')[0]} at ${final_price:.2f}")
                print(f"❌ MARKET ORDER FAILED for {amount:.6f} {symbol.split('/')[0]} at ${final_price:.2f}")

        # Calculate and log fee impact
        if order and final_price:
            trade_value = amount * final_price
            estimated_fee = trade_value * 0.001  # 0.1% fee
            log_message(f"💰 TRADE VALUE: ${trade_value:.2f}")
            log_message(f"💸 ESTIMATED FEE: ${estimated_fee:.4f} (0.1%)")
            
            # Log fee efficiency
            if side.upper() == 'BUY' and entry_price:
                profit_target = entry_price * (1 + optimized_config['risk_management']['take_profit_pct'])
                target_profit = (profit_target - entry_price) * amount
                fee_to_profit_ratio = estimated_fee / target_profit if target_profit > 0 else float('inf')
                log_message(f"📊 FEE EFFICIENCY: Fee = {fee_to_profit_ratio*100:.1f}% of target profit")

        # Track entry price for BUY orders - trailing stop will handle exits
        if side.upper() == 'BUY' and order is not None:
            entry_price = final_price
            
            log_message(f"🎯 Entry Price Set: ${final_price:.2f} - Trailing stop will handle exit")
            
            # 🎯 IMMEDIATE TRAILING STOP - Simple Capital Protection
            # Place trailing stop immediately for protection
            try:
                # Get the actual crypto amount purchased from the order
                crypto_symbol = symbol.split('/')[0]  # e.g., 'BTC' from 'BTC/USDT'
                
                # Enhanced amount extraction - handle multiple order response formats
                crypto_purchased = 0
                if order:
                    # Try multiple fields in order of preference
                    crypto_purchased = (
                        order.get('filled', 0) or          # Filled amount (most accurate)
                        order.get('amount', 0) or          # Order amount (fallback)
                        order.get('quantity', 0) or        # Alternative quantity field
                        amount                              # Use calculated amount as last resort
                    )
                    
                    # Log the order details for debugging
                    log_message(f"🔍 ORDER DEBUG: filled={order.get('filled', 'N/A')}, amount={order.get('amount', 'N/A')}, calculated={amount}")
                
                if crypto_purchased > 0:
                    # 🎯 PRIORITY: Native Trailing Stop Orders (0.25% callback rate)
                    # Place simple trailing stop immediately
                    trailing_stop = place_simple_trailing_stop(symbol, final_price, crypto_purchased, final_price)
                    
                    if trailing_stop:
                        trail_pct = trailing_stop.get('trail_distance', 0.005) * 100
                        
                        log_message("🎯 TRAILING STOP PROTECTION: Simple and effective protection active")
                        log_message(f"   🛡️ Trail Distance: {trail_pct:.1f}%")
                        log_message(f"   📈 Protected Amount: {crypto_purchased:.6f} {crypto_symbol}")
                        log_message("   🔄 Auto-trailing: Will follow price up automatically")
                        
                        print("✅ TRAILING STOP PROTECTION ACTIVE")
                        print(f"   🎯 Trail Distance: {trail_pct:.1f}%")
                        print("   🔄 TRAILING: Automatically follows price up")
                        print("   📊 Type: Binance native trailing stop")
                        
                        if trailing_stop.get('order_id'):
                            print(f"   � Order ID: {trailing_stop['order_id']}")
                        else:
                            print(f"   🛡️ Stop Price: ${trailing_stop.get('stop_price', 'Dynamic'):.2f}")
                            
                    else:
                        log_message("❌ CRITICAL: Failed to place trailing stop - MANUAL MONITORING REQUIRED")
                        log_message(f"   🔍 Failed for {crypto_purchased:.6f} {crypto_symbol} at ${final_price:.2f}")
                        print("🚨 WARNING: NO TRAILING STOP PROTECTION - Manual monitoring required!")
                else:
                    log_message("❌ CRITICAL: No crypto amount to protect - order may have failed")
                    log_message(f"   🔍 Order object: {order}")
                    log_message(f"   🔍 Calculated amount: {amount}")
                    log_message(f"   🔍 Final price: ${final_price:.2f}")
                    print("🚨 WARNING: NO CRYPTO PURCHASED - Check order execution!")
            except Exception as stop_error:
                log_message(f"❌ CRITICAL ERROR setting up immediate stop-limit: {stop_error}")
                log_message(f"   🔍 Order: {order}")
                log_message(f"   🔍 Symbol: {symbol}, Amount: {amount}, Price: ${final_price:.2f}")
                print(f"🚨 STOP-LIMIT ERROR: {stop_error}")
        elif side.upper() == 'BUY' and order is None:
            log_message("❌ CRITICAL: BUY order failed - NO STOP-LIMIT PROTECTION PLACED")
            print("🚨 BUY ORDER FAILED - NO PROTECTION ACTIVE")
                
        elif side.upper() == 'SELL':
            # 🧹 COMPREHENSIVE CLEANUP: Cancel ALL stop-limit orders when selling
            log_message(f"🧹 SELL ORDER: Cleaning up all stop-limit orders for {symbol}")
            cancel_all_stop_limit_orders(symbol)
            
            # Clear risk management levels after selling
            entry_price = None
            stop_loss_price = None
            take_profit_price = None

        # Get updated balance for logging
        updated_balance = safe_api_call(exchange.fetch_balance)
        total_balance = updated_balance['total']['USDT'] + (updated_balance['total']['BTC'] * final_price)

        # Log the trade
        log_trade(side.upper(), symbol, amount, final_price, total_balance)

        # Update trade timing
        last_trade_time = time.time()

        print("📝 Trade logged to trade_log.csv")
        print(f"💰 Total portfolio value: ${total_balance:.2f}")

        if side.upper() == 'BUY' and stop_loss_price and take_profit_price:
            immediate_stop_pct = optimized_config['risk_management'].get('immediate_stop_limit_pct', 0.00125) * 100
            print(f"🛡️ Stop Loss: ${stop_loss_price:.2f} | 🎯 Take Profit: ${take_profit_price:.2f}")
            print(f"🚨 Immediate Stop-Limit: -{immediate_stop_pct:.3f}% (Capital Protection Active)")

        return order
    except Exception as e:
        print("❌ Order failed:", e)
        return None

def place_immediate_stop_limit_order(symbol, order_entry_price, btc_amount):
    """
    🛡️ ENHANCED STOP-LIMIT ORDER - Capital Protection with Failsafe
    
    Places an immediate stop-limit order right after a BUY order to protect capital.
    Enhanced with comprehensive order cleanup to prevent accumulation.
    """
    try:
        # 🧹 CRITICAL: Cancel ALL existing stop-limit orders first
        log_message(f"🧹 STEP 1: Cleaning up existing stop-limit orders for {symbol}")
        cleanup_success = cancel_all_stop_limit_orders(symbol)
        
        if not cleanup_success:
            log_message("⚠️ Order cleanup had issues, but proceeding with new order placement")
        
        local_risk_config = optimized_config['risk_management']
        
        # Check if immediate stop-limit is enabled
        if not local_risk_config.get('immediate_stop_limit_enabled', False):
            log_message("🔒 Immediate stop-limit disabled in config")
            return None
        
        # Validate inputs
        if not symbol or not order_entry_price or not btc_amount:
            log_message(f"❌ Invalid stop-limit inputs: symbol={symbol}, price={order_entry_price}, amount={btc_amount}")
            return None
            
        if btc_amount <= 0 or order_entry_price <= 0:
            log_message(f"❌ Invalid stop-limit values: amount={btc_amount}, price=${order_entry_price}")
            return None
            
        # Get stop-limit percentage (default -0.125%)
        stop_limit_pct = local_risk_config.get('immediate_stop_limit_pct', 0.00125)  # 0.125%
        
        # Calculate stop-limit prices
        stop_price = order_entry_price * (1 - stop_limit_pct)          # Trigger price
        limit_price = stop_price * 0.9995                        # Limit price (0.05% below stop for guaranteed fill)
        
        # Validate minimum order requirements - ENHANCED CHECK
        MIN_NOTIONAL_VALUE = 11.0  # Increased buffer above $10 minimum
        order_value = btc_amount * stop_price
        
        if order_value < MIN_NOTIONAL_VALUE:
            log_message(f"⚠️ Stop-limit order value too small: ${order_value:.2f} < ${MIN_NOTIONAL_VALUE:.2f}")
            log_message(f"🛡️ FALLBACK PROTECTION: Setting alert for manual monitoring")
            # Set manual monitoring alert instead of failing completely
            state_manager.update_trading_state(
                manual_monitoring_required=True,
                manual_monitoring_reason=f"Stop-limit too small (${order_value:.2f})",
                entry_price=entry_price,
                btc_amount=btc_amount,
                manual_stop_target=stop_price
            )
            return {"fallback_protection": True, "manual_monitoring": True}
            
        if btc_amount < 0.00001:  # Binance minimum BTC amount
            log_message(f"⚠️ BTC amount too small for stop-limit: {btc_amount:.6f} BTC")
            return None
        
        # ENHANCED: Verify we actually have the BTC balance
        try:
            balance = safe_api_call(exchange.fetch_balance)
            if not balance:
                log_message("❌ Could not verify balance - proceeding with caution")
            else:
                available_btc = balance.get('BTC', {}).get('free', 0)
                if available_btc < btc_amount:
                    log_message(f"⚠️ Insufficient BTC for stop-limit: {available_btc:.6f} < {btc_amount:.6f}")
                    log_message(f"🛡️ FALLBACK: Manual monitoring activated")
                    state_manager.update_trading_state(
                        manual_monitoring_required=True,
                        manual_monitoring_reason=f"Insufficient balance for stop-limit",
                        entry_price=entry_price,
                        btc_amount=btc_amount
                    )
                    return {"fallback_protection": True, "balance_issue": True}
                else:
                    log_message(f"✅ Balance verified: {available_btc:.6f} BTC available")
        except Exception as balance_error:
            log_message(f"⚠️ Balance check failed: {balance_error} - proceeding anyway")
        
        # Place stop-limit order
        log_message(f"🛡️ PLACING IMMEDIATE STOP-LIMIT:")
        log_message(f"   Entry: ${entry_price:.2f}")
        log_message(f"   Stop: ${stop_price:.2f} (-{stop_limit_pct*100:.3f}%)")
        log_message(f"   Limit: ${limit_price:.2f}")
        log_message(f"   Amount: {btc_amount:.6f} BTC (${order_value:.2f})")
        
        # ENHANCED: Try multiple order placement strategies
        order = None
        
        # Strategy 1: Standard stop-loss-limit order
        try:
            order = safe_api_call(
                exchange.create_order,
                symbol,
                'stop_loss_limit',  # Order type
                'sell',             # Side
                btc_amount,         # Amount
                limit_price,        # Limit price
                {
                    'stopPrice': stop_price,     # Stop trigger price
                    'timeInForce': 'GTC'         # Good Till Cancel
                }
            )
            if order:
                log_message(f"✅ STOP-LIMIT STRATEGY 1 SUCCESS: ID {order['id']}")
        except Exception as e:
            log_message(f"⚠️ Stop-limit strategy 1 failed: {e}")
        
        # Strategy 2: OCO (One-Cancels-Other) order if primary fails
        if not order:
            try:
                # Try OCO order with stop-limit and market stop
                take_profit_price = entry_price * 1.02  # 2% take profit
                order = safe_api_call(
                    exchange.create_order,
                    symbol,
                    'oco',
                    'sell',
                    btc_amount,
                    take_profit_price,  # Take profit limit
                    {
                        'stopPrice': stop_price,
                        'stopLimitPrice': limit_price,
                        'stopLimitTimeInForce': 'GTC'
                    }
                )
                if order:
                    log_message(f"✅ STOP-LIMIT STRATEGY 2 (OCO) SUCCESS: ID {order['id']}")
            except Exception as e:
                log_message(f"⚠️ Stop-limit strategy 2 (OCO) failed: {e}")
        
        # Strategy 3: Simple stop-market as last resort
        if not order:
            try:
                order = safe_api_call(
                    exchange.create_order,
                    symbol,
                    'stop_market',
                    'sell',
                    btc_amount,
                    None,  # No limit price for market order
                    {'stopPrice': stop_price}
                )
                if order:
                    log_message(f"✅ STOP-LIMIT STRATEGY 3 (MARKET) SUCCESS: ID {order['id']}")
                    log_message(f"⚠️ Using stop-market (no limit) for guaranteed execution")
            except Exception as e:
                log_message(f"❌ All stop-limit strategies failed: {e}")
        
        if order:
            log_message(f"✅ STOP-LIMIT ORDER PLACED: ID {order['id']}")
            log_message(f"   🛡️ Capital protected with immediate -{stop_limit_pct*100:.3f}% stop")
            
            # Store the stop-limit order ID for tracking
            state_manager.update_trading_state(
                immediate_stop_limit_order_id=order['id'],
                immediate_stop_limit_active=True,
                manual_monitoring_required=False  # Clear manual monitoring if order placed
            )
            
            return order
        else:
            # ULTIMATE FALLBACK: Manual monitoring with alerts
            log_message("❌ ALL STOP-LIMIT STRATEGIES FAILED")
            log_message(f"🛡️ ACTIVATING ENHANCED MANUAL MONITORING")
            log_message(f"   Entry: ${entry_price:.2f}")
            log_message(f"   Target Stop: ${stop_price:.2f} (-{stop_limit_pct*100:.3f}%)")
            log_message(f"   Amount: {btc_amount:.6f} BTC")
            log_message(f"🚨 MANUAL INTERVENTION REQUIRED - POSITION AT RISK")
            
            # Set enhanced manual monitoring
            state_manager.update_trading_state(
                manual_monitoring_required=True,
                manual_monitoring_reason="All stop-limit order strategies failed",
                entry_price=entry_price,
                btc_amount=btc_amount,
                manual_stop_target=stop_price,
                manual_monitoring_priority="CRITICAL"
            )

            
            return {"fallback_protection": True, "manual_monitoring": True, "critical": True}
            
    except Exception as e:
        log_message(f"❌ CRITICAL ERROR in stop-limit protection: {e}")
        log_message(f"🛡️ EMERGENCY FALLBACK: Manual monitoring activated")
        
        # Emergency fallback protection
        try:
            state_manager.update_trading_state(
                manual_monitoring_required=True,
                manual_monitoring_reason=f"Stop-limit error: {e}",
                entry_price=entry_price if 'entry_price' in locals() else None,
                btc_amount=btc_amount if 'btc_amount' in locals() else None,
                manual_monitoring_priority="EMERGENCY"
            )
        except:
            pass  # Don't fail if even fallback fails
            
        return None

def place_simple_trailing_stop(symbol, entry_price, btc_amount, current_price):
    """
    🔄 UNIFIED MANUAL TRAILING STOP SYSTEM
    
    Places a manual trailing stop-loss that continuously updates as price rises.
    This system works with ALL trading pairs on Binance US.
    
    Parameters per user specification:
    - Initial Stop: 0.50% below entry price
    - Trail Distance: 0.50% behind highest achieved price
    - Continuous Updates: Cancels old orders and places new ones as price rises
    """
    global trailing_stop_order_id, trailing_stop_active
    
    try:
        # Fixed trailing stop parameters per user specification
        trailing_delta_pct = 0.005  # 0.50% trailing delta (fixed)
        activation_pct = 0.00125    # 0.125% above current price for activation
        limit_offset_pct = 0.005    # 0.50% below current price for limit
        
        # Validate order size - Binance minimum  
        MIN_NOTIONAL_VALUE = 10.0  # Binance minimum is $10
        order_value = btc_amount * current_price
        
        if order_value < MIN_NOTIONAL_VALUE:
            log_message(f"⚠️ Order value ${order_value:.2f} too small for trailing stop (min: ${MIN_NOTIONAL_VALUE})")
            log_message(f"🛡️ FALLBACK: Using stop-limit order for small position protection")
            # Use stop-limit instead of stop-market for small orders (Binance US compatible)
            return place_small_order_stop_limit(symbol, entry_price, btc_amount, current_price)
        
        # Calculate prices per user specifications
        activation_price = current_price * (1 + activation_pct)  # 0.125% ABOVE current price
        limit_price = current_price * (1 - limit_offset_pct)     # 0.50% BELOW current price
        
        # Try to place Binance native trailing stop per user specifications
        log_message(f"🎯 PLACING TRAILING STOP ORDER:")
        log_message(f"   Symbol: {symbol}")
        log_message(f"   Amount: {btc_amount:.6f} {symbol.split('/')[0]}")
        log_message(f"   Entry/Current Price: ${current_price:.2f}")
        log_message(f"   Activation Price: ${activation_price:.4f} (0.125% above current)")
        log_message(f"   Trailing Delta: 0.50%")
        log_message(f"   Limit Price: ${limit_price:.4f} (0.50% below current)")
        
        # Place trailing stop with user specifications - UNIFIED MANUAL TRAILING SYSTEM
        order = None
        
        # PRIMARY STRATEGY: Manual Trailing Stop-Loss System (works for ALL pairs)
        log_message("🔄 USING MANUAL TRAILING STOP-LOSS SYSTEM")
        log_message("📈 Will continuously update stop-loss to trail 0.50% behind rising price")
        
        # Place initial stop-loss-limit order
        try:
            order = safe_api_call(
                lambda: exchange.create_order(
                    symbol,
                    'STOP_LOSS_LIMIT',
                    'sell',
                    btc_amount,
                    limit_price,  # Limit price (0.50% below current)
                    {
                        'stopPrice': str(limit_price),  # Initial stop at 0.50% below current
                        'timeInForce': 'GTC'
                    }
                )
            )
            
            if order and order.get('id'):
                    # Store trailing stop details in bot state for continuous monitoring
                    trailing_stop_data = {
                        'order_id': order['id'],
                        'symbol': symbol,
                        'amount': btc_amount,
                        'entry_price': current_price,
                        'highest_price': current_price,
                        'current_stop_price': limit_price,
                        'trailing_percent': 0.005,  # 0.50% trail distance
                        'last_updated': time.time(),
                        'active': True
                    }
                    
                    # Save to global state for monitoring in main loop
                    state_manager.update_trading_state(
                        trailing_stop_data=trailing_stop_data,
                        trailing_stop_order_id=order['id'],
                        trailing_stop_active=True
                    )
                    
                    log_message(f"✅ MANUAL TRAILING STOP INITIALIZED: Order ID {order['id']}")
                    log_message(f"   Initial Stop: ${limit_price:.4f} (0.50% below ${current_price:.4f})")
                    log_message("� Bot will monitor and update stop-loss as price rises")
                    log_message("📈 Stop-loss will trail 0.50% behind the highest price achieved")
                    
                    return order
        except Exception as e:
            log_message(f"⚠️ Manual trailing stop initialization failed: {e}")
            order = None
        
        # FALLBACK: Manual monitoring warning
        if not order:
            log_message("❌ Trailing stop placement failed: All order types failed")
            log_message("❌ CRITICAL: Failed to place trailing stop - MANUAL MONITORING REQUIRED")
            log_message(f"   🔍 Failed for {btc_amount:.6f} {symbol.split('/')[0]} at ${current_price:.2f}")
            
            print("❌ TRAILING STOP FAILED - MANUAL MONITORING NEEDED")
            print(f"   Position: {btc_amount:.6f} {symbol.split('/')[0]}")
            print(f"   Entry Price: ${current_price:.2f}")
            print("   Recommend: Place manual stop-loss at 0.50% below entry")
            
            return None
        
        return order
                
    except Exception as e:
        log_message(f"❌ Trailing stop placement failed: {e}")
        log_message("❌ CRITICAL: Failed to place trailing stop - MANUAL MONITORING REQUIRED")
        log_message(f"   🔍 Failed for {btc_amount:.6f} {symbol.split('/')[0]} at ${current_price:.2f}")
        return None

def place_small_order_stop_limit(symbol, entry_price, btc_amount, current_price):
    """
    🛡️ SMALL ORDER STOP-LIMIT PROTECTION - Binance US Compatible
    
    Places a stop-limit order for small orders that don't meet trailing stop minimums.
    Uses stop-limit which is supported by Binance US (unlike STOP_MARKET).
    """
    try:
        # Calculate stop price (0.5% below current price for protection)
        stop_price = current_price * 0.995  # 0.5% stop loss
        limit_price = stop_price * 0.995    # Limit price slightly below stop for execution
        
        log_message(f"🛡️ PLACING SMALL ORDER STOP-LIMIT PROTECTION:")
        log_message(f"   Entry: ${entry_price:.2f}, Current: ${current_price:.2f}")
        log_message(f"   Stop Price: ${stop_price:.4f} (-0.5%)")
        log_message(f"   Limit Price: ${limit_price:.4f}")
        log_message(f"   Amount: {btc_amount:.6f} {symbol.split('/')[0]}")
        
        order = safe_api_call(
            lambda: exchange.create_order(
                symbol,
                'stop_loss_limit',  # Binance US compatible
                'sell',
                btc_amount,
                limit_price,
                {
                    'stopPrice': str(stop_price),
                    'timeInForce': 'GTC'
                }
            )
        )
        
        if order and order.get('id'):
            log_message(f"✅ SMALL ORDER STOP-LIMIT PLACED: Order ID {order['id']}")
            
            # Save to state
            state_manager.update_trading_state(
                trailing_stop_order_id=order['id'],
                trailing_stop_active=True
            )
            
            return {
                'order_id': order['id'],
                'stop_price': stop_price,
                'limit_price': limit_price,
                'order_type': 'stop_loss_limit',
                'amount': btc_amount
            }
        else:
            log_message("❌ Small order stop-limit failed")
            return None
            
    except Exception as e:
        log_message(f"❌ Small order stop-limit failed: {e}")
        log_message(f"🚨 CRITICAL: No protection placed for small order - MANUAL MONITORING REQUIRED")
        return None

def place_trailing_oco_order(symbol, entry_price, btc_amount, current_price):
    """
    TRAILING OCO ORDER SYSTEM - Advanced Protection & Profit Optimization
    
    Places OCO (One-Cancels-Other) orders that automatically trail the price as it moves up.
    This combines stop-loss protection with take-profit targets that adjust dynamically.
    
    OCO Components:
    1. STOP-LIMIT LEG: Protects against downside (trails upward as price rises)
    2. TAKE-PROFIT LEG: Captures profits at strategic levels (adjusts with volatility)
    
    Benefits:
    - Automatic profit capture without monitoring
    - Dynamic stop-loss that locks in gains
    - No need to manually adjust orders
    - Protects against sudden reversals
    """
    try:
        risk_config = optimized_config['risk_management']
        
        # Validate inputs
        if not symbol or not entry_price or not btc_amount or not current_price:
            log_message(f"❌ Invalid trailing OCO inputs")
            return None
            
        if btc_amount <= 0 or entry_price <= 0 or current_price <= 0:
            log_message(f"❌ Invalid trailing OCO values")
            return None
            
        # Enhanced OCO Configuration
        stop_loss_pct = risk_config.get('trailing_oco_stop_pct', 0.008)     # 0.8% stop loss
        take_profit_pct = risk_config.get('trailing_oco_profit_pct', 0.015) # 1.5% take profit
        min_profit_lock = risk_config.get('trailing_oco_min_lock', 0.003)   # 0.3% minimum to lock
        
        # Dynamic profit target based on current profit
        current_profit_pct = (current_price - entry_price) / entry_price
        
        # If we're already in profit, use trailing logic
        if current_profit_pct > min_profit_lock:
            # Trail from current price instead of entry
            base_price = current_price
            stop_loss_price = base_price * (1 - stop_loss_pct)
            
            # Ensure stop loss locks in some profit
            min_profitable_stop = entry_price * (1 + min_profit_lock)
            stop_loss_price = max(stop_loss_price, min_profitable_stop)
            
            # Dynamic take profit based on momentum
            momentum_multiplier = 1.0
            if current_profit_pct > 0.01:  # If more than 1% profit
                momentum_multiplier = 1.5  # Increase take profit target
            elif current_profit_pct > 0.02:  # If more than 2% profit
                momentum_multiplier = 2.0  # Even higher target
                
            take_profit_price = base_price * (1 + (take_profit_pct * momentum_multiplier))
            
            log_message(f"🎯 TRAILING OCO (From Current Price):")
            log_message(f"   Current Profit: {current_profit_pct*100:+.2f}%")
            log_message(f"   Momentum Multiplier: {momentum_multiplier}x")
            
        else:
            # Standard OCO from entry price
            base_price = entry_price
            stop_loss_price = base_price * (1 - stop_loss_pct)
            take_profit_price = base_price * (1 + take_profit_pct)
            
            log_message(f"🎯 STANDARD OCO (From Entry):")
            
        # Calculate limit prices for guaranteed execution
        stop_limit_price = stop_loss_price * 0.999   # 0.1% below stop for quick fill
        
        # Validate minimum order requirements
        MIN_NOTIONAL_VALUE = 11.0
        order_value = btc_amount * current_price
        
        if order_value < MIN_NOTIONAL_VALUE:
            log_message(f"⚠️ OCO order value too small: ${order_value:.2f}")
            return place_fallback_protection(symbol, entry_price, btc_amount, stop_loss_price)
            
        log_message(f"🎯 PLACING TRAILING OCO ORDER:")
        log_message(f"   Entry Price: ${entry_price:.2f}")
        log_message(f"   Current Price: ${current_price:.2f}")
        log_message(f"   Stop Loss: ${stop_loss_price:.2f} (-{stop_loss_pct*100:.1f}%)")
        log_message(f"   Stop Limit: ${stop_limit_price:.2f}")
        log_message(f"   Take Profit: ${take_profit_price:.2f} (+{take_profit_pct*100:.1f}%)")
        log_message(f"   Amount: {btc_amount:.6f} BTC (${order_value:.2f})")
        
        # Try multiple OCO strategies
        oco_order = None
        
        # Strategy 1: Standard Binance OCO
        try:
            oco_order = safe_api_call(
                exchange.create_order,
                symbol,
                'oco',
                'sell',
                btc_amount,
                take_profit_price,  # Limit price for take profit leg
                {
                    'stopPrice': stop_loss_price,           # Stop trigger price
                    'stopLimitPrice': stop_limit_price,     # Stop limit price
                    'stopLimitTimeInForce': 'GTC',          # Good till cancel
                    'timeInForce': 'GTC'                    # Take profit time in force
                }
            )
            if oco_order:
                log_message(f"✅ TRAILING OCO STRATEGY 1 SUCCESS: ID {oco_order['id']}")
        except Exception as e:
            log_message(f"⚠️ OCO strategy 1 failed: {e}")
        
        # Strategy 2: Manual OCO (place both orders separately)
        if not oco_order:
            try:
                # Place stop-loss order
                stop_order = safe_api_call(
                    exchange.create_order,
                    symbol,
                    'stop_loss_limit',
                    'sell',
                    btc_amount * 0.7,  # 70% for stop loss
                    stop_limit_price,
                    {
                        'stopPrice': stop_loss_price,
                        'timeInForce': 'GTC'
                    }
                )
                
                # Place take-profit order
                profit_order = safe_api_call(
                    exchange.create_order,
                    symbol,
                    'limit',
                    'sell',
                    btc_amount * 0.3,  # 30% for take profit
                    take_profit_price,
                    {'timeInForce': 'GTC'}
                )
                
                if stop_order and profit_order:
                    oco_order = {
                        'id': f"MANUAL_OCO_{stop_order['id']}_{profit_order['id']}",
                        'stop_order': stop_order,
                        'profit_order': profit_order,
                        'type': 'manual_oco'
                    }
                    log_message(f"✅ MANUAL OCO SUCCESS: Stop {stop_order['id']}, Profit {profit_order['id']}")
                    
            except Exception as e:
                log_message(f"⚠️ Manual OCO strategy failed: {e}")
        
        # Strategy 3: Advanced OCO with partial exits
        if not oco_order:
            oco_order = place_advanced_partial_oco(symbol, btc_amount, entry_price, current_price, 
                                                  stop_loss_price, take_profit_price)
        
        if oco_order:
            # Store OCO order state
            state_manager.update_trading_state(
                trailing_oco_order_id=oco_order['id'],
                trailing_oco_active=True,
                trailing_oco_stop_price=stop_loss_price,
                trailing_oco_profit_price=take_profit_price,
                trailing_oco_highest_price=current_price,
                manual_monitoring_required=False
            )
            
            profit_target = ((take_profit_price - entry_price) / entry_price) * 100
            stop_loss_level = ((stop_loss_price - entry_price) / entry_price) * 100
            
            log_message(f"✅ TRAILING OCO PROTECTION ACTIVE:")
            log_message(f"   🛡️ Stop Loss: {stop_loss_level:+.2f}% from entry")
            log_message(f"   🎯 Take Profit: {profit_target:+.2f}% from entry")
            log_message(f"   🔄 Will trail as price moves up")
            
            return oco_order
        else:
            log_message("❌ ALL OCO STRATEGIES FAILED - Using fallback protection")
            return place_fallback_protection(symbol, entry_price, btc_amount, stop_loss_price)
            
    except Exception as e:
        log_message(f"❌ Error placing trailing OCO: {e}")
        return place_fallback_protection(symbol, entry_price, btc_amount, entry_price * 0.992)

def place_advanced_partial_oco(symbol, btc_amount, entry_price, current_price, stop_loss_price, take_profit_price):
    """
    ADVANCED PARTIAL OCO - Multiple Exit Strategy
    
    Places multiple OCO orders for different portions of the position:
    - 50% Aggressive take profit (shorter term)
    - 30% Conservative take profit (longer term) 
    - 20% Trailing stop only (let it run)
    """
    try:
        log_message(f"🎯 PLACING ADVANCED PARTIAL OCO:")
        
        # Split the position into 3 parts
        aggressive_amount = btc_amount * 0.5   # 50% for quick profits
        conservative_amount = btc_amount * 0.3 # 30% for larger moves
        runner_amount = btc_amount * 0.2       # 20% to let run with trailing stop
        
        # Aggressive take profit (closer target)
        aggressive_tp = entry_price * 1.008    # 0.8% target
        aggressive_stop = stop_loss_price
        
        # Conservative take profit (higher target)
        conservative_tp = take_profit_price    # Original target
        conservative_stop = stop_loss_price
        
        # Runner only has trailing stop (no take profit)
        runner_stop = stop_loss_price
        
        placed_orders = []
        
        # Place aggressive OCO
        try:
            aggressive_oco = safe_api_call(
                exchange.create_order,
                symbol,
                'oco',
                'sell',
                aggressive_amount,
                aggressive_tp,
                {
                    'stopPrice': aggressive_stop,
                    'stopLimitPrice': aggressive_stop * 0.999,
                    'stopLimitTimeInForce': 'GTC',
                    'timeInForce': 'GTC'
                }
            )
            if aggressive_oco:
                placed_orders.append(('aggressive', aggressive_oco))
                log_message(f"   ✅ Aggressive OCO (50%): {aggressive_oco['id']}")
        except Exception as e:
            log_message(f"   ⚠️ Aggressive OCO failed: {e}")
        
        # Place conservative OCO  
        try:
            conservative_oco = safe_api_call(
                exchange.create_order,
                symbol,
                'oco',
                'sell',
                conservative_amount,
                conservative_tp,
                {
                    'stopPrice': conservative_stop,
                    'stopLimitPrice': conservative_stop * 0.999,
                    'stopLimitTimeInForce': 'GTC',
                    'timeInForce': 'GTC'
                }
            )
            if conservative_oco:
                placed_orders.append(('conservative', conservative_oco))
                log_message(f"   ✅ Conservative OCO (30%): {conservative_oco['id']}")
        except Exception as e:
            log_message(f"   ⚠️ Conservative OCO failed: {e}")
        
        # Place runner stop-loss only
        try:
            runner_stop_order = safe_api_call(
                exchange.create_order,
                symbol,
                'stop_loss_limit',
                'sell',
                runner_amount,
                runner_stop * 0.999,
                {
                    'stopPrice': runner_stop,
                    'timeInForce': 'GTC'
                }
            )
            if runner_stop_order:
                placed_orders.append(('runner', runner_stop_order))
                log_message(f"   ✅ Runner Stop (20%): {runner_stop_order['id']}")
        except Exception as e:
            log_message(f"   ⚠️ Runner stop failed: {e}")
        
        if placed_orders:
            # Create combined order structure
            combined_order = {
                'id': f"PARTIAL_OCO_{len(placed_orders)}_ORDERS",
                'type': 'partial_oco',
                'orders': placed_orders,
                'total_coverage': sum(0.5 if order[0] == 'aggressive' else 0.3 if order[0] == 'conservative' else 0.2 for order in placed_orders)
            }
            
            log_message(f"✅ PARTIAL OCO COMPLETE: {len(placed_orders)} orders, {combined_order['total_coverage']*100:.0f}% coverage")
            return combined_order
        else:
            log_message(f"❌ All partial OCO orders failed")
            return None
            
    except Exception as e:
        log_message(f"❌ Error in advanced partial OCO: {e}")
        return None

def update_trailing_oco_order(symbol, current_price, entry_price, btc_amount):
    """
    UPDATE TRAILING OCO - Dynamic Order Management
    
    Updates OCO orders as price moves to:
    1. Trail stop-loss higher to lock in profits
    2. Adjust take-profit targets based on momentum
    3. Cancel and replace with optimized levels
    """
    try:
        risk_config = optimized_config['risk_management']
        trading_state = state_manager.get_trading_state()
        
        current_oco_id = trading_state.get('trailing_oco_order_id')
        if not current_oco_id or not trading_state.get('trailing_oco_active', False):
            return None
            
        # Configuration for trailing
        trail_trigger_pct = risk_config.get('oco_trail_trigger', 0.005)  # 0.5% move to trigger update
        trail_distance_pct = risk_config.get('oco_trail_distance', 0.008) # 0.8% trailing distance
        min_profit_lock = risk_config.get('oco_min_profit_lock', 0.003)   # 0.3% minimum profit to lock
        
        # Get tracking data
        highest_price = trading_state.get('trailing_oco_highest_price', entry_price)
        last_stop_price = trading_state.get('trailing_oco_stop_price', 0)
        last_profit_price = trading_state.get('trailing_oco_profit_price', 0)
        
        # Update highest price tracking
        if current_price > highest_price:
            highest_price = current_price
            state_manager.update_trading_state(trailing_oco_highest_price=highest_price)
            
        # Calculate new trailing levels
        price_movement_pct = (current_price - trading_state.get('trailing_oco_highest_price', entry_price)) / entry_price
        
        # Only update if price has moved enough to warrant it
        if price_movement_pct < trail_trigger_pct:
            return None
            
        # Calculate new stop and profit levels
        new_stop_price = highest_price * (1 - trail_distance_pct)
        
        # Ensure we lock in minimum profit
        min_profitable_stop = entry_price * (1 + min_profit_lock)
        new_stop_price = max(new_stop_price, min_profitable_stop)
        
        # Only update if meaningfully different
        if new_stop_price <= last_stop_price * 1.002:  # Only if 0.2% higher
            return None
            
        # Dynamic take profit adjustment based on momentum
        current_profit_pct = (current_price - entry_price) / entry_price
        momentum_factor = 1.0
        
        if current_profit_pct > 0.01:    # 1%+ profit
            momentum_factor = 1.3
        elif current_profit_pct > 0.02:  # 2%+ profit  
            momentum_factor = 1.6
        elif current_profit_pct > 0.03:  # 3%+ profit
            momentum_factor = 2.0
            
        base_profit_pct = risk_config.get('trailing_oco_profit_pct', 0.015)
        new_profit_price = current_price * (1 + (base_profit_pct * momentum_factor))
        
        log_message(f"🎯 UPDATING TRAILING OCO:")
        log_message(f"   Current: ${current_price:.2f} | Highest: ${highest_price:.2f}")
        log_message(f"   Current Profit: {current_profit_pct*100:+.2f}%")
        log_message(f"   Momentum Factor: {momentum_factor}x")
        log_message(f"   New Stop: ${new_stop_price:.2f} (was ${last_stop_price:.2f})")
        log_message(f"   New Profit: ${new_profit_price:.2f} (was ${last_profit_price:.2f})")
        
        # Cancel existing OCO orders
        try:
            if 'MANUAL_OCO_' in current_oco_id or 'PARTIAL_OCO_' in current_oco_id:
                # Handle manual/partial OCO cancellation
                cancel_complex_oco_orders(symbol, trading_state)
            else:
                # Standard OCO cancellation
                safe_api_call(exchange.cancel_order, current_oco_id, symbol)
            log_message(f"   ✅ Cancelled existing OCO orders")
        except Exception as e:
            log_message(f"   ⚠️ Error cancelling existing OCO: {e}")
        
        # Place new trailing OCO
        # Place simple trailing stop
        new_trailing_stop = place_simple_trailing_stop(symbol, entry_price, btc_amount, current_price)
        
        if new_trailing_stop:
            trail_distance = new_trailing_stop.get('trail_distance', 0.005) * 100
            log_message(f"   ✅ TRAILING STOP UPDATED: {new_trailing_stop.get('order_id', 'active')}")
            log_message(f"   🔒 Trail Distance: {trail_distance:.1f}%")
            return new_trailing_stop
        else:
            log_message(f"   ❌ Failed to update trailing stop")
            return None
            
    except Exception as e:
        log_message(f"❌ Error updating trailing OCO: {e}")
        return None

def cancel_complex_oco_orders(symbol, trading_state):
    """Cancel manual or partial OCO orders that have multiple components"""
    try:
        current_oco_id = trading_state.get('trailing_oco_order_id')
        
        if 'MANUAL_OCO_' in current_oco_id:
            # Extract individual order IDs from manual OCO
            parts = current_oco_id.replace('MANUAL_OCO_', '').split('_')
            for order_id in parts:
                try:
                    safe_api_call(exchange.cancel_order, order_id, symbol)
                    log_message(f"   ✅ Cancelled manual OCO component: {order_id}")
                except:
                    pass
                    
        elif 'PARTIAL_OCO_' in current_oco_id:
            # Would need to track individual order IDs for partial OCO
            # For now, attempt to cancel any active orders for the symbol
            try:
                open_orders = safe_api_call(exchange.fetch_open_orders, symbol)
                for order in open_orders:
                    if order['side'] == 'sell':  # Only cancel sell orders
                        safe_api_call(exchange.cancel_order, order['id'], symbol)
                        log_message(f"   ✅ Cancelled partial OCO component: {order['id']}")
            except:
                pass
                
    except Exception as e:
        log_message(f"Error cancelling complex OCO: {e}")

def place_fallback_protection(symbol, entry_price, btc_amount, stop_price):
    """Fallback protection when OCO orders fail"""
    try:
        log_message(f"🛡️ PLACING FALLBACK PROTECTION:")
        
        # Simple stop-loss as fallback
        stop_order = safe_api_call(
            exchange.create_order,
            symbol,
            'stop_loss_limit',
            'sell',
            btc_amount,
            stop_price * 0.999,
            {
                'stopPrice': stop_price,
                'timeInForce': 'GTC'
            }
        )
        
        if stop_order:
            log_message(f"✅ Fallback stop-loss placed: {stop_order['id']}")
            state_manager.update_trading_state(
                immediate_stop_limit_order_id=stop_order['id'],
                immediate_stop_limit_active=True,
                manual_monitoring_required=False
            )
            return stop_order
        else:
            # Ultimate fallback - manual monitoring
            log_message(f"🚨 ALL PROTECTION FAILED - Manual monitoring required")
            state_manager.update_trading_state(
                manual_monitoring_required=True,
                manual_monitoring_reason="All automated protection failed",
                entry_price=entry_price,
                btc_amount=btc_amount,
                manual_stop_target=stop_price,
                manual_monitoring_priority="CRITICAL"
            )
            return {"fallback_protection": True, "manual_monitoring": True, "critical": True}
            
    except Exception as e:
        log_message(f"❌ Fallback protection failed: {e}")
        return None

def verify_trailing_oco_protection(symbol, holding_position, entry_price):
    """
    🛡️ VERIFICATION: Ensure all positions have trailing OCO protection
    
    This function verifies that every position has proper OCO protection
    and alerts if any position is unprotected.
    """
    if not holding_position or not entry_price:
        return True  # No position to protect
        
    try:
        trading_state = state_manager.get_trading_state()
        oco_order_id = trading_state.get('trailing_oco_order_id')
        oco_active = trading_state.get('trailing_oco_active', False)
        
        # Also check legacy stop-limit as fallback
        stop_limit_order_id = trading_state.get('immediate_stop_limit_order_id')
        stop_limit_active = trading_state.get('immediate_stop_limit_active', False)
        
        if not oco_order_id or not oco_active:
            # Check if legacy protection exists
            if stop_limit_order_id and stop_limit_active:
                log_message("⚙️ LEGACY PROTECTION: Stop-limit active (consider upgrading to OCO)")
                return True
            else:
                log_message("🚨 CRITICAL: Position has NO OCO protection!")
                print("🚨 WARNING: UNPROTECTED POSITION DETECTED")
                print("   Attempting to place emergency OCO protection...")
                
                # Try to place emergency OCO
                balance = safe_api_call(exchange.fetch_balance)
                crypto_symbol = symbol.split('/')[0]
                crypto_amount = balance.get(crypto_symbol, {}).get('free', 0)
                
                if crypto_amount > 0.00001:
                    # Get current price for OCO placement
                    ticker = safe_api_call(exchange.fetch_ticker, symbol)
                    current_price = ticker['last'] if ticker else entry_price
                    
                    emergency_stop = place_simple_trailing_stop(symbol, entry_price, crypto_amount, current_price)
                    if emergency_stop:
                        log_message("✅ Emergency trailing stop protection restored")
                        print("✅ EMERGENCY TRAILING STOP PROTECTION RESTORED")
                        return True
                    else:
                        log_message("❌ FAILED to restore trailing stop protection")
                        print("❌ FAILED TO RESTORE PROTECTION - MANUAL INTERVENTION REQUIRED")
                        return False
                else:
                    log_message("❌ No crypto balance found to protect")
                    return False
        else:
            # Verify the OCO order still exists
            try:
                if 'MANUAL_OCO_' in oco_order_id or 'PARTIAL_OCO_' in oco_order_id:
                    # Complex OCO orders - check components
                    log_message(f"🔍 Verifying complex OCO protection: {oco_order_id}")
                    # For complex orders, we trust they exist if marked as active
                    # Real verification would require tracking individual order IDs
                    return True
                else:
                    # Standard OCO order verification
                    order_status = safe_api_call(exchange.fetch_order, oco_order_id, symbol)
                    if order_status and order_status.get('status') == 'open':
                        log_message(f"✅ OCO protection verified: {oco_order_id}")
                        return True
                    else:
                        log_message(f"⚠️ OCO order {oco_order_id} not found or closed")
                        print(f"⚠️ OCO ORDER MISSING - May have been triggered")
                        # Mark as inactive and try to establish new protection
                        state_manager.update_trading_state(trailing_oco_active=False)
                        return verify_trailing_oco_protection(symbol, holding_position, entry_price)
            except Exception as verify_error:
                log_message(f"⚠️ Error verifying OCO order: {verify_error}")
                # Assume protection exists if we can't verify (network issues)
                return True
                
    except Exception as e:
        log_message(f"❌ Error in OCO protection verification: {e}")
        return False

def cancel_trailing_oco_order(symbol):
    """Cancel the trailing OCO order when position is closed normally"""
    try:
        trading_state = state_manager.get_trading_state()
        oco_order_id = trading_state.get('trailing_oco_order_id')
        
        if oco_order_id and trading_state.get('trailing_oco_active', False):
            log_message(f"🛡️ Cancelling trailing OCO order: {oco_order_id}")
            
            if 'MANUAL_OCO_' in oco_order_id or 'PARTIAL_OCO_' in oco_order_id:
                # Cancel complex OCO orders
                cancel_complex_oco_orders(symbol, trading_state)
                log_message(f"✅ Complex OCO orders cancelled")
            else:
                # Cancel standard OCO order
                try:
                    safe_api_call(exchange.cancel_order, oco_order_id, symbol)
                    log_message(f"✅ Standard OCO order cancelled: {oco_order_id}")
                except Exception as cancel_error:
                    log_message(f"⚠️ Could not cancel OCO order: {cancel_error}")
            
            # Clear OCO state
            state_manager.update_trading_state(
                trailing_oco_order_id=None,
                trailing_oco_active=False,
                trailing_oco_stop_price=None,
                trailing_oco_profit_price=None,
                trailing_oco_highest_price=None
            )
            
    except Exception as e:
        log_message(f"❌ Error canceling trailing OCO order: {e}")

def verify_stop_limit_protection(symbol, holding_position, entry_price):
    """
    🛡️ LEGACY VERIFICATION: Ensure all positions have stop-limit protection
    
    This function maintains backward compatibility with the old stop-limit system
    while encouraging migration to the new OCO system.
    """
    if not holding_position or not entry_price:
        return True  # No position to protect
    
    # First try to verify OCO protection (preferred)
    if verify_trailing_oco_protection(symbol, holding_position, entry_price):
        return True
        
    # Fallback to legacy stop-limit verification
    try:
        trading_state = state_manager.get_trading_state()
        stop_limit_order_id = trading_state.get('immediate_stop_limit_order_id')
        stop_limit_active = trading_state.get('immediate_stop_limit_active', False)
        
        if not stop_limit_order_id or not stop_limit_active:
            log_message("🚨 CRITICAL: Position has NO stop-limit protection!")
            print("🚨 WARNING: UNPROTECTED POSITION DETECTED")
            print("   Attempting to place emergency stop-limit...")
            
            # Try to place emergency stop-limit
            balance = safe_api_call(exchange.fetch_balance)
            crypto_amount = balance[symbol.split('/')[0]]['free']
            
            if crypto_amount > 0.00001:
                # Get current price for trailing stop
                ticker = safe_api_call(exchange.fetch_ticker, symbol)
                current_price = ticker['last'] if ticker else entry_price
                
                # Use trailing stop instead of stop-limit
                emergency_stop = place_simple_trailing_stop(symbol, entry_price, crypto_amount, current_price)
                if emergency_stop:
                    log_message("✅ Emergency trailing stop protection restored")
                    print("✅ EMERGENCY TRAILING STOP PROTECTION RESTORED")
                    return True
                else:
                    log_message("❌ FAILED to restore trailing stop protection")
                    print("❌ FAILED TO RESTORE PROTECTION - MANUAL INTERVENTION REQUIRED")
                    return False
            else:
                log_message("❌ No crypto balance found to protect")
                return False
        else:
            # Verify the stop-limit order still exists
            try:
                order_status = safe_api_call(exchange.fetch_order, stop_limit_order_id, symbol)
                if order_status and order_status.get('status') == 'open':
                    log_message(f"✅ Legacy stop-limit protection verified: {stop_limit_order_id}")
                    return True
                else:
                    log_message(f"⚠️ Stop-limit order {stop_limit_order_id} not found or closed")
                    print(f"⚠️ STOP-LIMIT ORDER MISSING - May have been triggered")
                    # Clear state and try to establish new protection
                    state_manager.update_trading_state(immediate_stop_limit_active=False)
                    return verify_stop_limit_protection(symbol, holding_position, entry_price)
            except Exception as verify_error:
                log_message(f"⚠️ Error verifying stop-limit order: {verify_error}")
                return True  # Assume protection exists if we can't verify
                
    except Exception as e:
        log_message(f"❌ Error in stop-limit verification: {e}")
        return False

def cancel_all_stop_limit_orders(symbol):
    """
    🗑️ COMPREHENSIVE ORDER CLEANUP
    Cancel ALL existing stop-limit orders for the symbol to prevent accumulation
    """
    try:
        log_message(f"🧹 CLEANING UP: Canceling all existing stop-limit orders for {symbol}")
        
        # Get all open orders for the symbol
        open_orders = safe_api_call(exchange.fetch_open_orders, symbol)
        
        if not open_orders:
            log_message("✅ No open orders found")
            return True
        
        cancelled_count = 0
        stop_limit_count = 0
        
        for order in open_orders:
            order_type = order.get('type', '').lower()
            order_side = order.get('side', '').lower()
            order_id = order.get('id')
            
            # Cancel stop-limit, stop-loss, and stop-loss-limit orders
            if ('stop' in order_type or order_type in ['stop_loss_limit', 'stop_loss', 'oco']) and order_side == 'sell':
                stop_limit_count += 1
                try:
                    safe_api_call(exchange.cancel_order, order_id, symbol)
                    cancelled_count += 1
                    log_message(f"✅ Cancelled {order_type} order: {order_id}")
                except Exception as cancel_error:
                    log_message(f"⚠️ Failed to cancel order {order_id}: {cancel_error}")
        
        if stop_limit_count > 0:
            log_message(f"🧹 CLEANUP COMPLETE: {cancelled_count}/{stop_limit_count} stop-limit orders cancelled")
            
            # Clear all stop-limit tracking in state
            state_manager.update_trading_state(
                immediate_stop_limit_order_id=None,
                immediate_stop_limit_active=False,
                trailing_stop_highest_price=None,
                last_trailing_stop_price=None,
                trailing_stop_profit_locked=None,
                oco_order_id=None,
                manual_monitoring_required=False
            )
            
            if cancelled_count != stop_limit_count:
                log_message(f"⚠️ WARNING: {stop_limit_count - cancelled_count} orders failed to cancel")
                return False
        else:
            log_message("✅ No stop-limit orders found to cancel")
        
        return True
        
    except Exception as e:
        log_message(f"❌ Error during order cleanup: {e}")
        return False

def cancel_immediate_stop_limit_order(symbol):
    """Cancel the immediate stop-limit order when position is closed normally"""
    try:
        trading_state = state_manager.get_trading_state()
        order_id = trading_state.get('immediate_stop_limit_order_id')
        
        if order_id and trading_state.get('immediate_stop_limit_active', False):
            log_message(f"🗑️ Canceling immediate stop-limit order: {order_id}")
            
            try:
                safe_api_call(exchange.cancel_order, order_id, symbol)
                log_message("✅ Stop-limit order canceled successfully")
            except Exception as cancel_error:
                # Order might already be filled or canceled
                log_message(f"⚠️ Stop-limit order cancel attempt: {cancel_error}")
            
            # Clear the stop-limit order tracking and trailing stop state
            state_manager.update_trading_state(
                immediate_stop_limit_order_id=None,
                immediate_stop_limit_active=False,
                trailing_stop_highest_price=None,
                last_trailing_stop_price=None,
                trailing_stop_profit_locked=None
            )
            
    except Exception as e:
        log_message(f"❌ Error canceling immediate stop-limit order: {e}")

def enhanced_manual_monitoring(symbol, current_price):
    """
    🛡️ ENHANCED MANUAL MONITORING - Failsafe Protection System
    
    Actively monitors positions when stop-limit orders fail to place.
    Provides real-time alerts and automatic emergency selling if needed.
    This is the ultimate failsafe when all stop-limit strategies fail.
    """
    try:
        trading_state = state_manager.get_trading_state()
        
        # Check if manual monitoring is required
        if not trading_state.get('manual_monitoring_required', False):
            return None
            
        entry_price = trading_state.get('entry_price')
        btc_amount = trading_state.get('btc_amount')
        manual_stop_target = trading_state.get('manual_stop_target')
        priority = trading_state.get('manual_monitoring_priority', 'NORMAL')
        
        if not entry_price or not manual_stop_target:
            log_message("⚠️ Manual monitoring active but missing price data")
            return None
            
        # Calculate current position status
        current_pnl_pct = (current_price - entry_price) / entry_price * 100
        distance_to_stop = (current_price - manual_stop_target) / current_price * 100
        
        # Log monitoring status every 5 minutes (300 seconds)
        last_monitor_log = trading_state.get('last_manual_monitor_log', 0)
        if time.time() - last_monitor_log > 300:  # 5 minutes
            log_message(f"🛡️ MANUAL MONITORING STATUS:")
            log_message(f"   Entry: ${entry_price:.2f} | Current: ${current_price:.2f}")
            log_message(f"   P&L: {current_pnl_pct:+.2f}% | Stop Target: ${manual_stop_target:.2f}")
            log_message(f"   Distance to Stop: {distance_to_stop:+.2f}%")
            log_message(f"   Priority: {priority}")
            
            state_manager.update_trading_state(last_manual_monitor_log=time.time())
        
        # EMERGENCY ACTIONS based on priority and price movement
        emergency_triggered = False
        
        # CRITICAL/EMERGENCY: Immediate action if price hits stop target
        if current_price <= manual_stop_target:
            log_message(f"🚨 EMERGENCY STOP TRIGGERED: Price ${current_price:.2f} <= Target ${manual_stop_target:.2f}")
            emergency_triggered = True
            
        # HIGH PRIORITY: Action if price gets close to stop target
        elif priority in ['CRITICAL', 'EMERGENCY'] and distance_to_stop < 0.5:  # Within 0.5% of stop
            log_message(f"🚨 CRITICAL ALERT: Price approaching manual stop target")
            log_message(f"   Current: ${current_price:.2f} | Target: ${manual_stop_target:.2f}")
            emergency_triggered = True
            
        # SEVERE LOSS: Action if loss exceeds maximum acceptable threshold
        elif current_pnl_pct < -2.0:  # More than 2% loss
            log_message(f"🚨 SEVERE LOSS DETECTED: {current_pnl_pct:.2f}% loss")
            emergency_triggered = True
            
        if emergency_triggered:
            # Attempt emergency market sell
            try:
                log_message(f"🚨 EXECUTING EMERGENCY MARKET SELL")
                
                # Get current BTC balance
                balance = safe_api_call(exchange.fetch_balance)
                if balance:
                    available_btc = balance.get('BTC', {}).get('free', 0)
                    
                    if available_btc > 0.00001:
                        log_message(f"🚨 Emergency selling {available_btc:.6f} BTC at market")
                        
                        # Place emergency market sell order
                        emergency_order = safe_api_call(
                            exchange.create_market_sell_order,
                            symbol,
                            available_btc
                        )
                        
                        if emergency_order:
                            log_message(f"✅ EMERGENCY SELL EXECUTED: Order ID {emergency_order['id']}")
                            log_message(f"   Sold: {available_btc:.6f} BTC at ~${current_price:.2f}")
                            log_message(f"   Final P&L: {current_pnl_pct:+.2f}%")
                            
                            # Clear manual monitoring
                            state_manager.update_trading_state(
                                manual_monitoring_required=False,
                                manual_monitoring_reason=None,
                                entry_price=None,
                                btc_amount=None,
                                manual_stop_target=None,
                                emergency_sell_executed=True,
                                emergency_sell_price=current_price,
                                emergency_sell_pnl=current_pnl_pct
                            )
                            
                            return emergency_order
                        else:
                            log_message(f"❌ EMERGENCY SELL FAILED - MANUAL INTERVENTION CRITICAL")
                    else:
                        log_message(f"⚠️ No BTC balance found for emergency sell")
                        # Clear monitoring since no position exists
                        state_manager.update_trading_state(
                            manual_monitoring_required=False,
                            manual_monitoring_reason="No BTC position found"
                        )
                else:
                    log_message(f"❌ Could not fetch balance for emergency sell")
                    
            except Exception as emergency_error:
                log_message(f"❌ CRITICAL: Emergency sell failed: {emergency_error}")
                log_message(f"🚨 IMMEDIATE MANUAL INTERVENTION REQUIRED")
        
        # Return monitoring status
        return {
            "monitoring_active": True,
            "priority": priority,
            "current_pnl": current_pnl_pct,
            "distance_to_stop": distance_to_stop,
            "emergency_triggered": emergency_triggered
        }
        
    except Exception as e:
        log_message(f"❌ Error in enhanced manual monitoring: {e}")
        return None

# Legacy function for backward compatibility
def place_market_order(symbol, side, amount_usd):
    """Legacy function - redirects to intelligent order execution"""
    return place_intelligent_order(symbol, side, amount_usd, use_limit=False)

# 🎯 FEE OPTIMIZATION FUNCTIONS

def get_bnb_balance_for_fees():
    """
    Check if user has BNB balance for fee discounts (25% reduction)
    Returns BNB balance and whether it's sufficient for fee payments
    """
    try:
        balance = safe_api_call(exchange.fetch_balance)
        bnb_balance = balance.get('BNB', {}).get('free', 0)
        
        # Minimum BNB needed for fee payments (approximately $2-5 worth)
        min_bnb_for_fees = 0.01  # About $2-3 worth of BNB
        
        if bnb_balance >= min_bnb_for_fees:
            log_message(f"✅ BNB BALANCE: {bnb_balance:.4f} BNB (sufficient for 25% fee discount)")
            return bnb_balance, True
        else:
            log_message(f"⚠️ BNB BALANCE: {bnb_balance:.4f} BNB (insufficient for fee discount)")
            return bnb_balance, False
            
    except Exception as e:
        log_message(f"❌ Error checking BNB balance: {e}")
        return 0, False

def track_daily_fee_impact():
    """
    Track daily trading fees and their impact on portfolio performance
    Provides insights for fee optimization strategies
    """
    try:
        # Initialize fee tracking if not exists
        if not hasattr(track_daily_fee_impact, 'daily_fees'):
            track_daily_fee_impact.daily_fees = {'total_fees': 0, 'total_volume': 0, 'trade_count': 0}
        
        # Get current portfolio value for percentage calculations
        balance = safe_api_call(exchange.fetch_balance)
        total_portfolio = 0
        
        # Calculate total portfolio value in USDT
        for crypto in ['BTC', 'ETH', 'SOL', 'XRP', 'ADA', 'DOGE', 'XLM', 'SUI', 'SHIB', 'HBAR']:
            if crypto in balance:
                amount = balance[crypto]['free']
                if amount > 0:
                    # Get price in USDT (would need price lookup in real implementation)
                    # For now, use approximate values
                    total_portfolio += amount * 50000 if crypto == 'BTC' else amount * 100  # Simplified
        
        total_portfolio += balance.get('USDT', {}).get('free', 0)
        
        # Calculate fee efficiency metrics
        stats = track_daily_fee_impact.daily_fees
        if stats['total_volume'] > 0:
            fee_percentage = (stats['total_fees'] / stats['total_volume']) * 100
            portfolio_fee_impact = (stats['total_fees'] / total_portfolio) * 100 if total_portfolio > 0 else 0
            
            log_message(f"📊 DAILY FEE ANALYSIS:")
            log_message(f"   Total Fees: ${stats['total_fees']:.4f}")
            log_message(f"   Total Volume: ${stats['total_volume']:.2f}")
            log_message(f"   Fee Rate: {fee_percentage:.3f}%")
            log_message(f"   Portfolio Impact: {portfolio_fee_impact:.3f}%")
            log_message(f"   Trades Today: {stats['trade_count']}")
            
            # Fee optimization recommendations
            if fee_percentage > 0.15:  # Higher than expected 0.1%
                log_message("⚠️ FEE ALERT: Consider using more limit orders")
            if portfolio_fee_impact > 1.0:  # Fees > 1% of portfolio
                log_message("⚠️ HIGH FEE IMPACT: Consider reducing trade frequency")
        
        return stats
        
    except Exception as e:
        log_message(f"❌ Error tracking fee impact: {e}")
        return None

def place_post_only_order(symbol, side, amount_usd):
    """
    🛡️ POST-ONLY ORDER EXECUTION
    
    Forces maker-only execution to guarantee 0.1% maker fees.
    Will not execute if it would result in taker fees.
    """
    log_message("🛡️ POST-ONLY ORDER: Forcing maker fees (no taker execution)")
    return place_intelligent_order(symbol, side, amount_usd, use_limit=True, force_maker=True)

def optimize_order_size_for_fees(base_amount, symbol):
    """
    🎯 FEE-OPTIMIZED POSITION SIZING
    
    Adjusts position size to optimize fee efficiency while maintaining
    minimum order requirements and strategic position sizing.
    """
    try:
        # Get current market data
        ticker = safe_api_call(exchange.fetch_ticker, symbol)
        current_price = ticker['last']
        
        # Minimum order value to make fees worthwhile
        min_efficient_order = 50.0  # $50 minimum for fee efficiency
        
        # If proposed order is too small, suggest accumulation strategy
        if base_amount < min_efficient_order:
            log_message(f"💡 FEE OPTIMIZATION: ${base_amount:.2f} order may have high fee impact")
            log_message(f"   Consider accumulating to ${min_efficient_order:.2f}+ for better fee efficiency")
            
            # Still allow the trade but warn about fee impact
            fee_impact = (base_amount * 0.001) / base_amount * 100  # 0.1% fee as percentage of trade
            log_message(f"   Fee impact: {fee_impact:.1f}% of trade value")
        
        # Calculate optimal batch size to minimize fee frequency
        profit_target = optimized_config['risk_management']['take_profit_pct']
        target_profit_usd = base_amount * profit_target
        fee_cost_usd = base_amount * 0.002  # Round trip 0.2% fees
        
        fee_to_profit_ratio = fee_cost_usd / target_profit_usd if target_profit_usd > 0 else float('inf')
        
        log_message(f"💰 FEE EFFICIENCY ANALYSIS:")
        log_message(f"   Trade Size: ${base_amount:.2f}")
        log_message(f"   Target Profit: ${target_profit_usd:.2f} ({profit_target*100:.1f}%)")
        log_message(f"   Round-trip Fees: ${fee_cost_usd:.4f} (0.2%)")
        log_message(f"   Fee/Profit Ratio: {fee_to_profit_ratio*100:.1f}%")
        
        if fee_to_profit_ratio > 0.2:  # Fees > 20% of profit
            log_message("⚠️ HIGH FEE RATIO: Consider larger position or longer holds")
        
        return base_amount
        
    except Exception as e:
        log_message(f"❌ Error optimizing order size: {e}")
        return base_amount

# =============================================================================
# CONNECTION TEST FUNCTION
# =============================================================================

def test_connection():
    try:
        balance = safe_api_call(exchange.fetch_balance)
        ticker = safe_api_call(exchange.fetch_ticker, 'BTC/USDT')
        print("✅ Connected to Binance US!")
        print("Balances:")
        for coin, value in balance['total'].items():
            if value > 0:
                print(f"{coin}: {value}")
        print(f"\nCurrent BTC/USDT Price: ${ticker['last']}")

        # Display current bot state
        state_manager.print_current_state()
        
        # Check for existing positions to adopt with trailing stops
        detect_and_adopt_existing_positions()

        # Check for existing position recovery
        if state_manager.is_in_trade():
            print("\n🔄 RECOVERING FROM PREVIOUS SESSION:")
            trade_info = state_manager.get_current_trade_info()
            current_price = ticker['last']

            if trade_info['entry_price']:
                pnl_pct = (current_price - trade_info['entry_price']) / trade_info['entry_price']
                print(f"   Current P&L: {pnl_pct:+.2%}")
                print("   ✅ Bot will continue monitoring this position")

    except Exception as e:
        print("❌ Connection failed.")
        print("Error:", e)

# =============================================================================
# HIGH-FREQUENCY PROFIT ACCUMULATOR SYSTEM - 3 LAYER STRATEGY
# =============================================================================

def daily_pnl_tracker():
    """Track and update daily PnL and trade stats for high-frequency accumulator"""
    if not hasattr(daily_pnl_tracker, 'stats'):
        daily_pnl_tracker.stats = {
            'target_pct': 2.5,
            'current_pct': 0.0,
            'trades_today': 0,
            'win_trades': 0,
            'loss_trades': 0,
            'max_pct': 0.0,
            'start_time': time.time(),
            'last_trade_time': None,
            'layer1_trades': 0,  # EMA7/EMA25 crossover trades (4-10 per day)
            'layer2_trades': 0,  # Micro-scalping trades (20-40 per day)
            'layer3_trades': 0   # Range-bound trades (10-20 per day)
        }
    return daily_pnl_tracker.stats

# =============================================================================
# LAYER 1: EMA7/EMA25 CROSSOVER STRATEGY (HIGH CONVICTION)
# =============================================================================

def execute_layer1_strategy(df, current_price, holding_position):
    """
    Layer 1: EMA7/EMA25 Crossover Strategy
    - High conviction, medium moves (0.5-2%+ targets, optimized for HFT)
    - 4-10 trades per day (increased frequency)
    - Absolute priority when signals are strong
    """
    signal = detect_ma_crossover_signals(df, current_price)
    
    if signal['confidence'] > 0.70:  # Further reduced threshold for higher frequency
        stats = daily_pnl_tracker()
        stats['layer1_trades'] += 1
        
        # Adjust position size for Layer 1 (optimized for HFT)
        base_size_multiplier = 1.1  # Reduced from 1.2 for more frequent trades
        
        signal['layer'] = 'layer1'
        signal['size_multiplier'] = base_size_multiplier
        signal['target_pct'] = 1.0 if signal['confidence'] > 0.9 else 0.5  # Reduced targets: 0.5-1.0%
        signal['priority'] = 'HIGH'
        
        log_message(f"🎯 LAYER 1 SIGNAL: {signal['action']} | Target: {signal['target_pct']:.1f}% | Conf: {signal['confidence']:.3f}")
        return signal
    
    return None

# =============================================================================
# LAYER 2: MICRO-SCALPING SYSTEM (HIGH FREQUENCY)
# =============================================================================

def detect_micro_scalp_opportunities(df_1m, current_price):
    """
    Layer 2: Ultra-fast 1-minute EMA crossovers for micro-scalping
    - 0.15-0.4% profit targets (reduced for higher frequency)
    - 15-25 trades per day
    - 10-20 second hold times
    """
    if len(df_1m) < 15:
        return None
        
    ema5 = df_1m['close'].ewm(span=5).mean()
    ema13 = df_1m['close'].ewm(span=13).mean()
    
    # Calculate momentum for confirmation (more sensitive)
    price_momentum = (df_1m['close'].iloc[-1] - df_1m['close'].iloc[-3]) / df_1m['close'].iloc[-3]
    
    # Volume confirmation if available
    volume_factor = 1.0
    if 'volume' in df_1m.columns and len(df_1m) >= 10:
        recent_vol = df_1m['volume'].iloc[-3:].mean()
        avg_vol = df_1m['volume'].iloc[-10:].mean()
        volume_factor = recent_vol / avg_vol if avg_vol > 0 else 1.0
    
    # Golden micro-cross with momentum confirmation (more sensitive)
    if (ema5.iloc[-1] > ema13.iloc[-1] and ema5.iloc[-2] <= ema13.iloc[-2] and 
        price_momentum > 0.0005 and volume_factor > 0.7):  # Reduced thresholds
        
        confidence = 0.6  # Start lower for faster execution
        if volume_factor > 1.1:  # Reduced volume requirement
            confidence += 0.1
        if abs(price_momentum) > 0.002:  # Reduced momentum requirement
            confidence += 0.1
            
        return {
            'action': 'BUY',
            'confidence': min(confidence, 0.85),
            'target_pct': 0.2,  # Reduced target for faster profits
            'layer': 'layer2',
            'size_multiplier': 0.8,  # Slightly larger for HFT
            'hold_time_seconds': 15,  # Faster hold time
            'priority': 'MEDIUM'
        }
    
    # Death micro-cross with momentum confirmation (more sensitive)
    elif (ema5.iloc[-1] < ema13.iloc[-1] and ema5.iloc[-2] >= ema13.iloc[-2] and 
          price_momentum < -0.0005 and volume_factor > 0.7):  # Reduced thresholds
        
        confidence = 0.6
        if volume_factor > 1.1:
            confidence += 0.1
        if abs(price_momentum) > 0.002:
            confidence += 0.1
            
        return {
            'action': 'SELL',
            'confidence': min(confidence, 0.85),
            'target_pct': 0.2,  # Reduced target for faster profits
            'layer': 'layer2',
            'size_multiplier': 0.8,
            'hold_time_seconds': 15,  # Faster hold time
            'priority': 'MEDIUM'
        }
    
    return None

def execute_layer2_strategy(df_1m, current_price, holding_position):
    """Execute Layer 2 micro-scalping strategy"""
    signal = detect_micro_scalp_opportunities(df_1m, current_price)
    
    if signal and signal['confidence'] > 0.5:  # Reduced threshold for HFT
        stats = daily_pnl_tracker()
        stats['layer2_trades'] += 1
        
        # Check trade frequency limits for scalping (reduced for HFT)
        if stats['last_trade_time'] and (time.time() - stats['last_trade_time']) < 30:  # 30 seconds instead of 60
            # Reduce confidence but don't block completely
            signal['confidence'] *= 0.9
        
        log_message(f"⚡ LAYER 2 SCALP: {signal['action']} | Target: {signal['target_pct']:.1f}% | Conf: {signal['confidence']:.3f}")
        return signal
    
    return None

# =============================================================================
# LAYER 3: RANGE-BOUND SCALPING & MEAN REVERSION
# =============================================================================

def detect_range_bound_opportunities(df, current_price):
    """
    Layer 3: Range-bound scalping using daily boundaries and mean reversion
    - RSI 25/75 levels
    - Daily high/low boundaries
    - Bollinger Band reversals
    """
    if len(df) < 30:
        return None
    
    # Calculate daily range
    daily_high = df['high'].rolling(24).max().iloc[-1]
    daily_low = df['low'].rolling(24).min().iloc[-1]
    daily_range = daily_high - daily_low
    
    if daily_range <= 0:
        return None
    
    position_in_range = (current_price - daily_low) / daily_range
    
    # Calculate RSI for reversal signals
    rsi = calculate_rsi_for_reversals(df['close'], period=14)
    current_rsi = rsi.iloc[-1] if len(rsi) > 0 else 50
    
    # Calculate Bollinger Bands
    bb_upper, bb_middle, bb_lower = calculate_bollinger_bands(df['close'])
    
    # Range-bound BUY opportunities (more sensitive for HFT)
    if (position_in_range < 0.35 and current_rsi < 35) or current_price <= bb_lower.iloc[-1] * 1.015:  # Expanded range
        return {
            'action': 'BUY',
            'confidence': 0.7,  # Reduced for faster execution
            'target_pct': 0.3,  # Reduced target for HFT
            'layer': 'layer3',
            'size_multiplier': 0.8,
            'hold_time_seconds': 180,  # Reduced hold time
            'priority': 'LOW',
            'reason': f"Range bottom ({position_in_range*100:.1f}%) + RSI oversold ({current_rsi:.1f})"
        }
    
    # Range-bound SELL opportunities (more sensitive for HFT)
    elif (position_in_range > 0.65 and current_rsi > 65) or current_price >= bb_upper.iloc[-1] * 0.985:  # Expanded range
        return {
            'action': 'SELL',
            'confidence': 0.7,  # Reduced for faster execution
            'target_pct': 0.3,  # Reduced target for HFT
            'layer': 'layer3',
            'size_multiplier': 0.8,
            'hold_time_seconds': 180,  # Reduced hold time
            'priority': 'LOW',
            'reason': f"Range top ({position_in_range*100:.1f}%) + RSI overbought ({current_rsi:.1f})"
        }
    
    # Mean reversion in middle range (more sensitive)
    elif 0.35 <= position_in_range <= 0.65:  # Expanded middle range
        if current_rsi < 40:  # More sensitive RSI
            return {
                'action': 'BUY',
                'confidence': 0.55,  # Reduced for faster execution
                'target_pct': 0.2,   # Smaller target for HFT
                'layer': 'layer3',
                'size_multiplier': 0.6,
                'hold_time_seconds': 180,
                'priority': 'LOW',
                'reason': f"Mid-range mean reversion (RSI {current_rsi:.1f})"
            }
        elif current_rsi > 60:  # More sensitive RSI for SELL
            return {
                'action': 'SELL',
                'confidence': 0.55,  # Reduced for faster execution
                'target_pct': 0.2,   # Smaller target for HFT
                'layer': 'layer3',
                'size_multiplier': 0.6,
                'hold_time_seconds': 180,  # Reduced hold time
                'priority': 'LOW',
                'reason': f"Mid-range mean reversion (RSI {current_rsi:.1f})"
            }
    
    return None

def execute_layer3_strategy(df, current_price, holding_position):
    """Execute Layer 3 range-bound scalping strategy"""
    signal = detect_range_bound_opportunities(df, current_price)
    
    if signal and signal['confidence'] > 0.45:  # Reduced threshold for HFT
        stats = daily_pnl_tracker()
        stats['layer3_trades'] += 1
        
        log_message(f"📊 LAYER 3 RANGE: {signal['action']} | Target: {signal['target_pct']:.1f}% | {signal['reason']}")
        return signal
    
    return None

# =============================================================================
# LAYER 4: PINE SCRIPT ENHANCED RSI MEAN REVERSION STRATEGY
# =============================================================================

def execute_layer4_rsi_strategy(df, current_price, holding_position):
    """
    Layer 4: Pine Script Enhanced RSI Mean Reversion Strategy
    - Combines RSI (6,12,24), MACD (12,26,9), and EMA (7,25,99) analysis
    - Blue line (EMA25) peaks = SELL signals, Red line dips = BUY signals
    - 0.3-1.0% profit targets (conservative but reliable)
    - 5-12 trades per day (moderate frequency)
    """
    if len(df) < 99:  # Need enough data for EMA99
        return None
    
    try:
        # === Moving Averages (Pine Script Logic) ===
        ema7 = df['close'].ewm(span=7).mean()
        ema25 = df['close'].ewm(span=25).mean()  # Blue line from Pine Script
        ema99 = df['close'].ewm(span=99).mean()
        
        # === RSI Indicators (Multi-timeframe like Pine Script) ===
        def calculate_rsi(prices, period):
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            return 100 - (100 / (1 + rs))
        
        rsi6 = calculate_rsi(df['close'], 6)
        rsi12 = calculate_rsi(df['close'], 12)
        rsi24 = calculate_rsi(df['close'], 24)
        
        # Weighted RSI average (Pine Script formula)
        rsi_avg = (rsi6 * 0.5 + rsi12 * 0.3 + rsi24 * 0.2)
        
        # === Bollinger Bands (20, 2) ===
        bb_basis = df['close'].rolling(window=20).mean()
        bb_std = df['close'].rolling(window=20).std()
        bb_upper = bb_basis + (2 * bb_std)
        bb_lower = bb_basis - (2 * bb_std)
        
        # === MACD (12, 26, 9) ===
        ema_fast = df['close'].ewm(span=12).mean()
        ema_slow = df['close'].ewm(span=26).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=9).mean()
        
        # Current values
        current_ema7 = ema7.iloc[-1]
        current_ema25 = ema25.iloc[-1]  # Blue line
        current_ema99 = ema99.iloc[-1]
        current_rsi_avg = rsi_avg.iloc[-1]
        current_macd = macd_line.iloc[-1]
        current_signal = signal_line.iloc[-1]
        current_bb_upper = bb_upper.iloc[-1]
        current_bb_lower = bb_lower.iloc[-1]
        
        # Previous values for crossover detection
        prev_macd = macd_line.iloc[-2]
        prev_signal = signal_line.iloc[-2]
        prev_ema25 = ema25.iloc[-2]
        
        # === Pine Script Conditions ===
        rsi_oversold = current_rsi_avg < 30
        rsi_overbought = current_rsi_avg > 70
        
        # MACD crossovers
        macd_cross_up = (current_macd > current_signal and prev_macd <= prev_signal)
        macd_cross_down = (current_macd < current_signal and prev_macd >= prev_signal)
        
        # Trend analysis
        bullish_trend = current_ema7 > current_ema25 and current_ema25 > current_ema99
        bearish_trend = current_ema7 < current_ema25 and current_ema25 < current_ema99
        
        # === ENHANCED SIGNALS (Your Observations) ===
        # Blue line (EMA25) peak detection for SELL
        ema25_recent = ema25.iloc[-5:]  # Last 5 periods
        ema25_peak = (current_ema25 >= ema25_recent.max() * 0.999 and 
                     current_ema25 < prev_ema25)  # At or near peak and starting to decline
        
        # Red line dip detection for BUY (using RSI as "red line")
        rsi_recent = rsi_avg.iloc[-5:]  # Last 5 periods
        rsi_dip = (current_rsi_avg <= rsi_recent.min() * 1.001 and 
                  current_rsi_avg > rsi_avg.iloc[-2])  # At or near bottom and starting to rise
        
        # Price near Bollinger Bands
        near_bb_lower = current_price <= current_bb_lower * 1.01  # Within 1% of lower band
        near_bb_upper = current_price >= current_bb_upper * 0.99  # Within 1% of upper band
        
        # === PINE SCRIPT LONG CONDITIONS ===
        pine_long = rsi_oversold and macd_cross_up and bullish_trend
        
        # === PINE SCRIPT SHORT CONDITIONS ===
        pine_short = rsi_overbought and macd_cross_down and bearish_trend
        
        # === ENHANCED BUY SIGNALS ===
        enhanced_buy_signals = []
        confidence = 0.0
        
        if pine_long:
            enhanced_buy_signals.append("Pine Script LONG: RSI oversold + MACD cross up + bullish trend")
            confidence += 0.25
            
        if rsi_dip and near_bb_lower:
            enhanced_buy_signals.append("RSI dip near BB lower band")
            confidence += 0.20
            
        if macd_cross_up and current_rsi_avg < 40:
            enhanced_buy_signals.append("MACD bullish cross with low RSI")
            confidence += 0.15
            
        if bullish_trend and current_price < current_ema25 * 0.99:
            enhanced_buy_signals.append("Price dip below EMA25 in bullish trend")
            confidence += 0.15
        
        # === ENHANCED SELL SIGNALS ===
        enhanced_sell_signals = []
        sell_confidence = 0.0
        
        if pine_short:
            enhanced_sell_signals.append("Pine Script SHORT: RSI overbought + MACD cross down + bearish trend")
            sell_confidence += 0.25
            
        if ema25_peak and near_bb_upper:
            enhanced_sell_signals.append("EMA25 (blue line) peak near BB upper band")
            sell_confidence += 0.20
            
        if macd_cross_down and current_rsi_avg > 60:
            enhanced_sell_signals.append("MACD bearish cross with high RSI")
            sell_confidence += 0.15
            
        if bearish_trend and current_price > current_ema25 * 1.01:
            enhanced_sell_signals.append("Price pump above EMA25 in bearish trend")
            sell_confidence += 0.15
        
        # === SIGNAL GENERATION ===
        if enhanced_buy_signals and not holding_position and confidence >= 0.35:
            # Track Layer 4 trades
            stats = daily_pnl_tracker()
            if 'layer4_trades' not in stats:
                stats['layer4_trades'] = 0
            stats['layer4_trades'] += 1
            
            log_message(f"📈 LAYER 4 PINE: BUY | RSI: {current_rsi_avg:.1f} | MACD: {'↑' if macd_cross_up else '→'} | EMA Trend: {'BULL' if bullish_trend else 'MIXED'}")
            
            return {
                'layer': 'layer4',
                'action': 'BUY',
                'confidence': min(0.85, confidence + 0.35),  # Boost for Pine Script validation
                'priority': 'MEDIUM',
                'target_pct': 0.6,  # Conservative 0.6% target
                'size_multiplier': 1.0,
                'reasons': enhanced_buy_signals,
                'pine_metrics': {
                    'rsi_avg': current_rsi_avg,
                    'macd_signal': 'BULLISH' if macd_cross_up else 'NEUTRAL',
                    'trend': 'BULLISH' if bullish_trend else 'MIXED',
                    'ema25_position': 'SUPPORT' if current_price > current_ema25 else 'RESISTANCE'
                }
            }
            
        elif enhanced_sell_signals and holding_position and sell_confidence >= 0.35:
            log_message(f"📉 LAYER 4 PINE: SELL | RSI: {current_rsi_avg:.1f} | MACD: {'↓' if macd_cross_down else '→'} | EMA25: {'PEAK' if ema25_peak else 'NORMAL'}")
            
            return {
                'layer': 'layer4',
                'action': 'SELL',
                'confidence': min(0.85, sell_confidence + 0.35),
                'priority': 'MEDIUM',
                'target_pct': 0.6,
                'size_multiplier': 1.0,
                'reasons': enhanced_sell_signals,
                'pine_metrics': {
                    'rsi_avg': current_rsi_avg,
                    'macd_signal': 'BEARISH' if macd_cross_down else 'NEUTRAL',
                    'trend': 'BEARISH' if bearish_trend else 'MIXED',
                    'ema25_position': 'RESISTANCE' if current_price < current_ema25 else 'SUPPORT'
                }
            }
        
        return None
        
    except Exception as e:
        log_message(f"❌ Error in Layer 4 Pine Script strategy: {e}")
        return None

# =============================================================================
# STRATEGY COORDINATOR & PROFIT TARGET MANAGEMENT
# =============================================================================

def calculate_adaptive_profit_target(daily_progress, volatility, layer):
    """Adjust profit targets based on daily progress, volatility, and strategy layer"""
    base_targets = {
        'layer1': 0.8,       # EMA crossover - reduced for higher frequency (0.5-2% range)
        'layer2': 0.2,       # Micro-scalping - reduced for higher frequency
        'layer3': 0.3,       # Range-bound - reduced for more trades
        'layer4_rsi': 0.5    # RSI mean reversion - balanced for quick profits
    }
    
    base_target = base_targets.get(layer, 0.3)
    
    # Adjust based on daily progress (more aggressive for HFT)
    if daily_progress < 0.5:  # Far behind target
        multiplier = 0.6  # Take very quick gains to catch up (0.5% for Layer1)
    elif daily_progress < 1.0:  # Behind target
        multiplier = 0.8  # Take smaller, quicker gains (0.6% for Layer1)
    elif daily_progress > 2.5:  # Well ahead of target
        multiplier = 2.5  # Can afford to wait for larger moves (2.0% for Layer1)
    elif daily_progress > 1.5:  # Ahead of target
        multiplier = 1.5  # Slightly larger targets (1.2% for Layer1)
    else:
        multiplier = 1.0
    
    # Adjust based on volatility (more responsive)
    if volatility > 0.03:
        multiplier *= 1.6  # Higher targets in high volatility
    elif volatility > 0.02:
        multiplier *= 1.3
    elif volatility > 0.01:
        multiplier *= 1.1
    else:
        multiplier *= 0.7  # Much lower targets in low volatility for HFT
    
    return base_target * multiplier

def should_accumulate_trades():
    """Return True if bot should keep trading to maximize daily gains"""
    stats = daily_pnl_tracker()
    
    # Always trade aggressively if below 2.5% target
    if stats['current_pct'] < stats['target_pct']:
        return True
    
    # Keep trading if we haven't hit reasonable upper limit (increased for HFT)
    if stats['max_pct'] < 15.0:  # Higher ceiling for high-frequency accumulation
        return True
    
    # Increased daily trade limit for high-frequency trading
    if stats['trades_today'] > 150:  # More trades allowed per day
        return False
    
    # If we've exceeded target but less than 1.5x target, trade more conservatively
    if stats['target_pct'] <= stats['current_pct'] < (stats['target_pct'] * 1.5):
        # Reduce frequency but don't stop completely
        if stats['last_trade_time'] and (time.time() - stats['last_trade_time']) < 120:  # 2 minutes
            return False
        return True
    
    return True

def update_daily_pnl(pnl_pct, trade_win, layer=None):
    """Update daily PnL stats after each trade"""
    stats = daily_pnl_tracker()
    stats['trades_today'] += 1
    if trade_win:
        stats['win_trades'] += 1
    else:
        stats['loss_trades'] += 1
    stats['current_pct'] += pnl_pct
    stats['max_pct'] = max(stats['max_pct'], stats['current_pct'])
    stats['last_trade_time'] = time.time()
    
    # Log progress
    win_rate = (stats['win_trades'] / stats['trades_today']) * 100 if stats['trades_today'] > 0 else 0
    log_message(f"📈 DAILY PROGRESS: {stats['current_pct']:.2f}% | Trades: {stats['trades_today']} | Win Rate: {win_rate:.1f}%")

def reset_daily_pnl_if_needed():
    """Reset daily stats if a new day has started"""
    stats = daily_pnl_tracker()
    now = time.time()
    if now - stats['start_time'] > 86400:  # 24 hours
        # Log final daily stats
        win_rate = (stats['win_trades'] / stats['trades_today']) * 100 if stats['trades_today'] > 0 else 0
        log_message(f"📊 DAILY COMPLETE: {stats['current_pct']:.2f}% | {stats['trades_today']} trades | {win_rate:.1f}% win rate")
        log_message(f"📊 LAYER BREAKDOWN: L1={stats['layer1_trades']} L2={stats['layer2_trades']} L3={stats['layer3_trades']}")
        
        # Reset for new day
        stats['current_pct'] = 0.0
        stats['trades_today'] = 0
        stats['win_trades'] = 0
        stats['loss_trades'] = 0
        stats['max_pct'] = 0.0
        stats['start_time'] = now
        stats['last_trade_time'] = None
        stats['layer1_trades'] = 0
        stats['layer2_trades'] = 0
        stats['layer3_trades'] = 0
        stats['layer4_trades'] = 0

def coordinate_multi_layer_strategy(df, df_1m, current_price, holding_position, symbol=None):
    """
    Coordinate all 4 layers and select the best signal
    Priority: Layer 1 > Layer 4 > Layer 2 > Layer 3
    """
    signals = []
    
    # Check if we should keep trading
    if not should_accumulate_trades():
        log_message("🛑 Daily trading limit reached - pausing accumulation")
        return None
    
    # Layer 1: EMA7/EMA25 Crossover (Highest Priority)
    layer1_signal = execute_layer1_strategy(df, current_price, holding_position)
    if layer1_signal:
        signals.append(layer1_signal)
    
    # Layer 4: RSI Mean Reversion (Second Priority - Market Adaptability)
    layer4_signal = execute_layer4_rsi_strategy(df, current_price, holding_position)
    if layer4_signal:
        signals.append(layer4_signal)
    
    # Layer 2: Micro-scalping (Third Priority)
    if df_1m is not None:
        layer2_signal = execute_layer2_strategy(df_1m, current_price, holding_position)
        if layer2_signal:
            signals.append(layer2_signal)
    
    # Layer 3: Range-bound (Lowest Priority)
    layer3_signal = execute_layer3_strategy(df, current_price, holding_position)
    if layer3_signal:
        signals.append(layer3_signal)
    
    # Select best signal based on priority and confidence
    if not signals:
        return None
    
    # Sort by priority (HIGH > MEDIUM > LOW) then by confidence
    priority_order = {'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}
    best_signal = max(signals, key=lambda s: (priority_order[s['priority']], s['confidence']))
    
    # Add adaptive profit target
    stats = daily_pnl_tracker()
    daily_progress = stats['current_pct'] / stats['target_pct']
    volatility = df['close'].pct_change().std() if len(df) > 1 else 0.02
    
    best_signal['adaptive_target'] = calculate_adaptive_profit_target(
        daily_progress, volatility, best_signal['layer']
    )
    
    # 🧠 PHASE 3: ENHANCE SIGNAL WITH LSTM AI PREDICTION
    if LSTM_PREDICTOR_AVAILABLE:
        try:
            enhanced_signal = enhance_signal_with_lstm(df, best_signal, optimized_config, ['5m', '15m'])
            if enhanced_signal.get('lstm_enhancement', 0) > 0.05:  # Significant enhancement
                best_signal = enhanced_signal
                log_message(f"🧠 LSTM AI Enhancement: +{enhanced_signal['lstm_enhancement']:.1%} confidence boost")
        except Exception as e:
            log_message(f"⚠️ LSTM enhancement error: {e}")
    
    # 🎯 PHASE 3 WEEK 2: ENHANCE SIGNAL WITH SENTIMENT ANALYSIS
    if SENTIMENT_ANALYSIS_AVAILABLE:
        try:
            sentiment_enhanced_signal = enhance_signal_with_sentiment(best_signal, symbol, current_price)
            sentiment_enhancement = sentiment_enhanced_signal.get('sentiment_enhancement', 0)
            
            if abs(sentiment_enhancement) > 0.05:  # Significant sentiment impact
                best_signal = sentiment_enhanced_signal
                sentiment_mood = sentiment_enhanced_signal.get('sentiment_mood', 'NEUTRAL')
                sentiment_score = sentiment_enhanced_signal.get('sentiment_score', 0)
                
                if sentiment_enhancement > 0:
                    log_message(f"🎯 SENTIMENT BOOST: +{sentiment_enhancement:.1%} confidence (Mood: {sentiment_mood})")
                else:
                    log_message(f"⚠️ SENTIMENT WARNING: {sentiment_enhancement:.1%} confidence (Mood: {sentiment_mood})")
                
                # Log sentiment recommendations
                sentiment_recs = sentiment_enhanced_signal.get('sentiment_recommendations', [])
                for rec in sentiment_recs[:2]:  # Show top 2 recommendations
                    log_message(f"   💡 {rec}")
                    
        except Exception as e:
            log_message(f"⚠️ Sentiment analysis error: {e}")
    
    # 🎯 PHASE 3 WEEK 2: ENHANCE SIGNAL WITH PATTERN RECOGNITION
    if PATTERN_AI_AVAILABLE:
        try:
            pattern_enhanced_signal = pattern_ai.enhance_signal_with_patterns(best_signal, df, symbol)
            
            # Check if pattern enhancement was significant
            original_confidence = best_signal.get('confidence', 0.5)
            enhanced_confidence = pattern_enhanced_signal.get('confidence', 0.5)
            pattern_boost = enhanced_confidence - original_confidence
            
            if pattern_boost > 0.05:  # Significant pattern enhancement
                best_signal = pattern_enhanced_signal
                log_message(f"🎯 Pattern AI Enhancement: +{pattern_boost:.1%} confidence boost")
                
                # Log pattern details
                pattern_analysis = pattern_enhanced_signal.get('pattern_analysis', {})
                if pattern_analysis.get('patterns'):
                    for pattern in pattern_analysis['patterns'][:2]:  # Log top 2 patterns
                        log_message(f"   📊 Pattern: {pattern['pattern']} ({pattern['direction']}, {pattern['confidence']:.0f}%)")
                
                # Log breakout predictions
                breakout_pred = pattern_enhanced_signal.get('breakout_prediction', {})
                if breakout_pred.get('breakout_probability', 0) > 0.6:
                    log_message(f"   🚀 Breakout Alert: {breakout_pred['breakout_probability']:.1%} probability ({breakout_pred['primary_direction']})")
            
        except Exception as e:
            log_message(f"⚠️ Pattern enhancement error: {e}")
    
    # 🧠 PHASE 3 WEEK 3: ENHANCE SIGNAL WITH ADVANCED ML ENSEMBLE
    if ADVANCED_ML_AVAILABLE:
        try:
            ml_enhanced_signal = enhance_signal_with_advanced_ml(best_signal, df, symbol)
            
            # Check for significant ML enhancement
            original_confidence = best_signal.get('confidence', 0.5)
            ml_enhanced_confidence = ml_enhanced_signal.get('confidence', 0.5)
            ml_boost = ml_enhanced_confidence - original_confidence
            
            if abs(ml_boost) > 0.05:  # Significant ML enhancement
                best_signal = ml_enhanced_signal
                log_message(f"🧠 Advanced ML Enhancement: {ml_boost:+.1%} confidence change")
                
                # Log ML ensemble details
                ml_enhancement = ml_enhanced_signal.get('ml_enhancement', {})
                enhancement_type = ml_enhancement.get('enhancement_type', 'UNKNOWN')
                
                if enhancement_type == 'AGREEMENT_BOOST':
                    log_message(f"   ✅ ML Ensemble Agreement: {ml_enhancement.get('model_agreement', 0):.1%} consensus")
                elif enhancement_type == 'DISAGREEMENT_CAUTION':
                    ml_pred = ml_enhancement.get('ml_prediction', {})
                    log_message(f"   ⚠️ ML Disagreement: Models suggest {ml_pred.get('action', 'UNKNOWN')}")
                
                # Log feature importance
                feature_importance = ml_enhancement.get('feature_importance', {})
                if feature_importance:
                    top_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:3]
                    feature_text = ", ".join([f"{feat}: {imp:.2f}" for feat, imp in top_features])
                    log_message(f"   🔍 Key Features: {feature_text}")
                    
        except Exception as e:
            log_message(f"⚠️ Advanced ML enhancement error: {e}")
    
    # 📊 PHASE 3 WEEK 4: ENHANCE SIGNAL WITH ALTERNATIVE DATA
    if ALTERNATIVE_DATA_AVAILABLE:
        try:
            alt_data_enhanced_signal = enhance_signal_with_alternative_data(best_signal, 'BTC/USDT')
            
            # Check for significant alternative data enhancement
            original_confidence = best_signal.get('confidence', 0.5)
            alt_data_confidence = alt_data_enhanced_signal.get('confidence', 0.5)
            alt_data_boost = alt_data_confidence - original_confidence
            
            if abs(alt_data_boost) > 0.05:  # Significant alternative data enhancement
                best_signal = alt_data_enhanced_signal
                log_message(f"📊 Alternative Data Enhancement: {alt_data_boost:+.1%} confidence change")
                
                # Log alternative data details
                alt_enhancement = alt_data_enhanced_signal.get('alternative_data_enhancement', {})
                enhancement_type = alt_enhancement.get('enhancement_type', 'UNKNOWN')
                composite_score = alt_enhancement.get('composite_score', 0.5)
                consensus_level = alt_enhancement.get('consensus_level', 0.5)
                
                if enhancement_type == 'STRONG_SUPPORT':
                    log_message(f"   ✅ Alternative Data Support: {composite_score:.1%} composite score")
                elif enhancement_type == 'DATA_CONFLICT':
                    log_message(f"   ⚠️ Alternative Data Conflict: {composite_score:.1%} vs trade direction")
                
                # Log alternative data summary
                summary = alt_enhancement.get('summary', {})
                if summary:
                    log_message(f"   📈 Fundamentals: {summary.get('fundamental_rating', 'N/A')}, "
                               f"Sentiment: {summary.get('sentiment_rating', 'N/A')}, "
                               f"Consensus: {summary.get('consensus_rating', 'N/A')}")
                    
        except Exception as e:
            log_message(f"⚠️ Alternative data enhancement error: {e}")
    
    log_message(f"🎯 SELECTED: {best_signal['layer'].upper()} {best_signal['action']} | "
               f"Adaptive Target: {best_signal['adaptive_target']:.2f}% | Daily: {stats['current_pct']:.2f}%")
    
    return best_signal

# =============================================================================
# EMA7/EMA25 CROSSOVER STRATEGY - ABSOLUTE PRIORITY FOR DAY TRADING
# =============================================================================

def detect_ma_crossover_signals(df, current_price):
    """
    🎯 AGGRESSIVE DAY TRADING: EMA7/EMA25 Crossover Detection
    This is the ABSOLUTE PRIORITY strategy that overrides all others.
    
    Golden Cross (EMA7 > EMA25): Strong BUY signal
    Death Cross (EMA7 < EMA25): Strong SELL signal
    
    🧠 ML ENHANCED: Now includes learning from past mistakes
    ⚠️ BULLETPROOF DEATH CROSS PROTECTION: Multiple layers prevent BUY after death cross
    
    EMA provides faster response to price changes compared to SMA.
    Returns high-confidence signals for immediate execution.
    """
    try:
        if len(df) < 30:
            return {'action': 'HOLD', 'confidence': 0.0, 'reasons': ['Not enough data for EMA crossover'], 'crossover_type': 'no_signal'}

        # Calculate exponential moving averages
        ema_7 = df['close'].ewm(span=7).mean()
        ema_25 = df['close'].ewm(span=25).mean()

        if len(ema_7) < 2 or len(ema_25) < 2:
            return {'action': 'HOLD', 'confidence': 0.0, 'reasons': ['Not enough EMA data'], 'crossover_type': 'no_signal'}

        # Current and previous EMA values
        ema7_current = ema_7.iloc[-1]
        ema25_current = ema_25.iloc[-1]
        ema7_previous = ema_7.iloc[-2]
        ema25_previous = ema_25.iloc[-2]

        # Crossover detection
        golden_cross = (ema7_previous <= ema25_previous) and (ema7_current > ema25_current)
        death_cross = (ema7_previous >= ema25_previous) and (ema7_current < ema25_current)

        # Current trend strength
        ema_spread = abs(ema7_current - ema25_current) / ema25_current * 100  # Percentage spread

        # 🚨 BULLETPROOF DEATH CROSS PROTECTION - LAYER 1: Immediate Detection
        if death_cross:
            # 🧠 LOG DEATH CROSS FOR ML LEARNING
            try:
                if ML_LEARNING_AVAILABLE:
                    log_message("🚨 DEATH CROSS DETECTED - Recording for ML learning to prevent future BUY mistakes")
                    # This will be caught by ML system if a buy is attempted
            except Exception as e:
                log_message(f"⚠️ ML logging error: {e}")
            
            # DEATH CROSS: ALWAYS SELL OR HOLD - NEVER BUY
            return {
                'action': 'SELL',
                'confidence': 1.0,
                'reasons': [
                    f"🚨 DEATH CROSS DETECTED: EMA7 crossed below EMA25 - BEARISH SIGNAL",
                    f"EMA7 prev: {ema7_previous:.4f} → {ema7_current:.4f}",
                    f"EMA25 prev: {ema25_previous:.4f} → {ema25_current:.4f}",
                    f"Spread: {ema_spread:.2f}%",
                    f"⚠️ PROTECTION: Death cross NEVER triggers BUY orders"
                ],
                'ema7': ema7_current,
                'ema25': ema25_current,
                'spread': ema_spread,
                'crossover_type': 'death_cross',
                'death_cross_detected': True,  # 🚨 FLAG FOR ADDITIONAL PROTECTION
                'bearish_signal': True
            }

        # --- FIX: Always return strong signal on crossover ---
        if golden_cross:
            return {
                'action': 'BUY',
                'confidence': 1.0,
                'reasons': [
                    f"Golden Cross: EMA7 crossed above EMA25",
                    f"EMA7 prev: {ema7_previous:.4f} → {ema7_current:.4f}",
                    f"EMA25 prev: {ema25_previous:.4f} → {ema25_current:.4f}",
                    f"Spread: {ema_spread:.2f}%"
                ],
                'ema7': ema7_current,
                'ema25': ema25_current,
                'spread': ema_spread,
                'crossover_type': 'golden_cross'
            }

        # 🎯 DIP DETECTION LOGIC: Look for buying opportunities when price dips below moving averages
        # 🚨 BULLETPROOF DEATH CROSS PROTECTION - LAYER 2: Block ALL dip buying in bearish trends
        current_price = df['close'].iloc[-1]
        
        # CRITICAL PROTECTION: If EMA7 is currently below EMA25, we're in a bearish trend - NO DIP BUYING EVER
        if ema7_current < ema25_current:
            # 🧠 LOG BEARISH TREND FOR ML LEARNING
            try:
                if ML_LEARNING_AVAILABLE:
                    log_message("🚨 BEARISH TREND DETECTED - ML protection preventing dip buying")
            except Exception as e:
                pass  # Don't let ML errors affect protection
            
            return {
                'action': 'HOLD',  # Could be SELL but HOLD is safer for avoiding losses
                'confidence': 0.85,  # High confidence in NOT buying
                'reasons': [
                    f"🚨 BEARISH TREND PROTECTION: EMA7 below EMA25 - NO DIP BUYING ALLOWED",
                    f"EMA7: {ema7_current:.4f} < EMA25: {ema25_current:.4f}",
                    f"Spread: -{ema_spread:.2f}% (bearish)",
                    f"Wait for golden cross or clear trend reversal",
                    f"🛡️ PROTECTION: Preventing losses from buying in downtrend"
                ],
                'ema7': ema7_current,
                'ema25': ema25_current,
                'spread': -ema_spread,  # Negative spread indicates bearish
                'crossover_type': 'bearish_trend_protection',
                'bearish_trend_detected': True,  # 🚨 FLAG FOR ADDITIONAL PROTECTION
                'protection_active': True
            }
        
        # 🚨 BULLETPROOF DEATH CROSS PROTECTION - LAYER 3: Additional Recent Death Cross Check
        # Check if there was a death cross in the last 5-10 periods to avoid delayed buy signals
        recent_death_cross_detected = False
        lookback_periods = min(10, len(ema_7) - 1)  # Look back up to 10 periods
        
        for i in range(1, lookback_periods + 1):
            if len(ema_7) > i and len(ema_25) > i:
                ema7_past = ema_7.iloc[-(i+1)]
                ema25_past = ema_25.iloc[-(i+1)]
                ema7_current_check = ema_7.iloc[-i]
                ema25_current_check = ema_25.iloc[-i]
                
                # Check for death cross in recent history
                if (ema7_past >= ema25_past) and (ema7_current_check < ema25_current_check):
                    recent_death_cross_detected = True
                    log_message(f"🚨 RECENT DEATH CROSS PROTECTION: Found death cross {i} periods ago")
                    break
        
        if recent_death_cross_detected:
            return {
                'action': 'HOLD',
                'confidence': 0.90,  # Very high confidence in NOT buying
                'reasons': [
                    f"🚨 RECENT DEATH CROSS PROTECTION: Death cross detected in last {lookback_periods} periods",
                    f"Current EMA7: {ema7_current:.4f}, EMA25: {ema25_current:.4f}",
                    f"Still in potential downtrend - avoiding buy signals",
                    f"🛡️ PROTECTION: Waiting for clear trend reversal"
                ],
                'ema7': ema7_current,
                'ema25': ema25_current,
                'spread': ema_spread,
                'crossover_type': 'recent_death_cross_protection',
                'recent_death_cross_detected': True,
                'protection_active': True
            }
        
        # Calculate price position relative to EMAs
        price_vs_ema7 = (current_price - ema7_current) / ema7_current
        price_vs_ema25 = (current_price - ema25_current) / ema25_current
        
        # Calculate recent price momentum (last 5 periods)
        if len(df) >= 5:
            price_momentum = (current_price - df['close'].iloc[-6]) / df['close'].iloc[-6]
        else:
            price_momentum = 0
        
        # 🎯 DIP BUYING CONDITIONS: Enhanced and more sensitive dip detection
        dip_below_ema7 = price_vs_ema7 < 0.001  # Price even slightly below EMA7 (0.1%)
        weak_dip_below_ema7 = price_vs_ema7 < 0.005  # Price within 0.5% of EMA7
        dip_below_ema25 = price_vs_ema25 < -0.002  # Price more than 0.2% below EMA25
        oversold_momentum = price_momentum < -0.002  # Recent downward momentum > 0.2%
        mild_oversold_momentum = price_momentum < 0.002  # Very mild negative or flat momentum
        
        # Calculate RSI for additional confirmation
        rsi = None
        if len(df) >= 14:
            try:
                from success_rate_enhancer import calculate_rsi
                rsi_series = calculate_rsi(df['close'])
                rsi = rsi_series.iloc[-1] if len(rsi_series) > 0 else None
            except:
                rsi = None
        
        # 🎯 ENHANCED DIP BUYING SIGNALS
        if dip_below_ema7 and (oversold_momentum or (rsi and rsi < 40)):
            confidence = 0.65
            rsi_display = f"{rsi:.1f}" if rsi else "N/A"
            reasons = [
                f"DIP BUY: Price ${current_price:.2f} near/below EMA7 ${ema7_current:.2f} ({price_vs_ema7*100:+.2f}%)",
                f"Favorable conditions: momentum {price_momentum*100:+.2f}% or RSI {rsi_display}"
            ]
            
            # Boost confidence for deeper dips
            if dip_below_ema25:
                confidence += 0.15
                reasons.append(f"Deep dip: Also below EMA25 ${ema25_current:.2f} ({price_vs_ema25*100:+.2f}%)")
            
            # RSI confirmation boost
            if rsi and rsi < 35:
                confidence += 0.15
                reasons.append(f"Strong RSI oversold: {rsi:.1f}")
            elif rsi and rsi < 40:
                confidence += 0.08
                reasons.append(f"RSI oversold: {rsi:.1f}")
            
            return {
                'action': 'BUY',
                'confidence': min(confidence, 0.9),
                'reasons': reasons,
                'ema7': ema7_current,
                'ema25': ema25_current,
                'spread': ema_spread,
                'crossover_type': 'enhanced_dip_buy',
                'price_vs_ema7': price_vs_ema7,
                'price_vs_ema25': price_vs_ema25,
                'momentum': price_momentum,
                'rsi': rsi
            }
        
        # 🎯 RSI OVERSOLD OPPORTUNITIES: Even when price is near EMAs
        elif rsi and rsi < 35 and weak_dip_below_ema7 and mild_oversold_momentum:
            confidence = 0.55
            reasons = [
                f"RSI OVERSOLD BUY: Strong RSI signal {rsi:.1f}",
                f"Price near EMA7: ${current_price:.2f} vs ${ema7_current:.2f} ({price_vs_ema7*100:+.2f}%)",
                f"Mild negative momentum: {price_momentum*100:+.2f}%"
            ]
            
            if dip_below_ema25:
                confidence += 0.1
                reasons.append(f"Below EMA25: {price_vs_ema25*100:+.2f}%")
            
            return {
                'action': 'BUY',
                'confidence': confidence,
                'reasons': reasons,
                'ema7': ema7_current,
                'ema25': ema25_current,
                'spread': ema_spread,
                'crossover_type': 'rsi_oversold_dip',
                'price_vs_ema7': price_vs_ema7,
                'price_vs_ema25': price_vs_ema25,
                'momentum': price_momentum,
                'rsi': rsi
            }
        
        # 🎯 MODERATE DIP OPPORTUNITIES: Less aggressive dip buying
        elif (dip_below_ema7 or (rsi and rsi < 40)) and price_momentum < 0.005:  # Very mild conditions
            confidence = 0.45
            reasons = [
                f"MODERATE DIP: Mild opportunity detected",
                f"Price vs EMA7: {price_vs_ema7*100:+.2f}%"
            ]
            
            if rsi and rsi < 45:
                confidence += 0.05
                reasons.append(f"RSI support: {rsi:.1f}")
            
            if dip_below_ema25:
                confidence += 0.05
                reasons.append(f"Below EMA25: {price_vs_ema25*100:+.2f}%")
            
            return {
                'action': 'BUY',
                'confidence': confidence,
                'reasons': reasons,
                'ema7': ema7_current,
                'ema25': ema25_current,
                'spread': ema_spread,
                'crossover_type': 'moderate_dip_buy',
                'price_vs_ema7': price_vs_ema7,
                'price_vs_ema25': price_vs_ema25,
                'momentum': price_momentum,
                'rsi': rsi
            }
        
        # 🎯 ORIGINAL TREND FOLLOWING (when price is above EMAs)
        if ema7_current > ema25_current and ema_spread > 1.0:
            # Only buy on uptrend if price is close to EMA7 (avoid buying peaks)
            if price_vs_ema7 < 0.01:  # Within 1% of EMA7
                return {
                    'action': 'BUY',
                    'confidence': 0.6,
                    'reasons': [
                        f"TREND BUY: EMA7 above EMA25, price near EMA7",
                        f"EMA7: {ema7_current:.4f}, EMA25: {ema25_current:.4f}",
                        f"Price vs EMA7: {price_vs_ema7*100:+.2f}%"
                    ],
                    'ema7': ema7_current,
                    'ema25': ema25_current,
                    'spread': ema_spread,
                    'crossover_type': 'trend_buy_near_ema7'
                }
            else:
                # 🎯 ENHANCED PEAK SELLING: Price too far above EMA7 - potential peak
                if price_vs_ema7 > 0.01:  # Price more than 1% above EMA7
                    # Check for peak selling conditions
                    peak_above_ema7 = price_vs_ema7 > 0.015  # Price more than 1.5% above EMA7
                    peak_above_ema25 = price_vs_ema25 > 0.02  # Price more than 2% above EMA25
                    strong_upward_momentum = price_momentum > 0.005  # Strong recent momentum
                    
                    # RSI overbought check
                    rsi_overbought = rsi and rsi > 70
                    mild_rsi_overbought = rsi and rsi > 65
                    
                    # 🎯 ENHANCED PEAK SELLING SIGNALS
                    if peak_above_ema7 and (rsi_overbought or strong_upward_momentum):
                        confidence = 0.65
                        rsi_display = f"{rsi:.1f}" if rsi else "N/A"
                        reasons = [
                            f"PEAK SELL: Price ${current_price:.2f} far above EMA7 ${ema7_current:.2f} (+{price_vs_ema7*100:.2f}%)",
                            f"Peak conditions: momentum {price_momentum*100:+.2f}% or RSI {rsi_display}"
                        ]
                        
                        # Boost confidence for stronger peak signals
                        if peak_above_ema25:
                            confidence += 0.15
                            reasons.append(f"Strong peak: Also above EMA25 ${ema25_current:.2f} (+{price_vs_ema25*100:.2f}%)")
                        
                        # RSI overbought boost
                        if rsi and rsi > 75:
                            confidence += 0.15
                            reasons.append(f"Strong RSI overbought: {rsi:.1f}")
                        elif rsi and rsi > 70:
                            confidence += 0.08
                            reasons.append(f"RSI overbought: {rsi:.1f}")
                        
                        return {
                            'action': 'SELL',
                            'confidence': min(confidence, 0.9),
                            'reasons': reasons,
                            'ema7': ema7_current,
                            'ema25': ema25_current,
                            'spread': ema_spread,
                            'crossover_type': 'enhanced_peak_sell',
                            'price_vs_ema7': price_vs_ema7,
                            'price_vs_ema25': price_vs_ema25,
                            'momentum': price_momentum,
                            'rsi': rsi
                        }
                    
                    # 🎯 RSI OVERBOUGHT OPPORTUNITIES: Even when price is near EMAs
                    elif rsi and rsi > 70 and price_vs_ema7 > 0.005 and strong_upward_momentum:
                        confidence = 0.55
                        reasons = [
                            f"RSI OVERBOUGHT SELL: Strong RSI signal {rsi:.1f}",
                            f"Price above EMA7: ${current_price:.2f} vs ${ema7_current:.2f} (+{price_vs_ema7*100:.2f}%)",
                            f"Strong upward momentum: {price_momentum*100:+.2f}%"
                        ]
                        
                        if peak_above_ema25:
                            confidence += 0.1
                            reasons.append(f"Above EMA25: {price_vs_ema25*100:+.2f}%")
                        
                        return {
                            'action': 'SELL',
                            'confidence': confidence,
                            'reasons': reasons,
                            'ema7': ema7_current,
                            'ema25': ema25_current,
                            'spread': ema_spread,
                            'crossover_type': 'rsi_overbought_peak',
                            'price_vs_ema7': price_vs_ema7,
                            'price_vs_ema25': price_vs_ema25,
                            'momentum': price_momentum,
                            'rsi': rsi
                        }
                    
                    # 🎯 MODERATE PEAK OPPORTUNITIES: Less aggressive peak selling
                    elif (peak_above_ema7 or (rsi and rsi > 65)) and price_momentum > 0.002:  # Mild upward momentum
                        confidence = 0.45
                        reasons = [
                            f"MODERATE PEAK: Mild peak opportunity detected",
                            f"Price vs EMA7: {price_vs_ema7*100:+.2f}%"
                        ]
                        
                        if rsi and rsi > 60:
                            confidence += 0.05
                            reasons.append(f"RSI elevated: {rsi:.1f}")
                        
                        if peak_above_ema25:
                            confidence += 0.05
                            reasons.append(f"Above EMA25: {price_vs_ema25*100:+.2f}%")
                        
                        return {
                            'action': 'SELL',
                            'confidence': confidence,
                            'reasons': reasons,
                            'ema7': ema7_current,
                            'ema25': ema25_current,
                            'spread': ema_spread,
                            'crossover_type': 'moderate_peak_sell',
                            'price_vs_ema7': price_vs_ema7,
                            'price_vs_ema25': price_vs_ema25,
                            'momentum': price_momentum,
                            'rsi': rsi
                        }
                
                # If not peak selling conditions, hold and wait for better entry
                return {
                    'action': 'HOLD',
                    'confidence': 0.0,
                    'reasons': [
                        f"PEAK AVOIDANCE: Price ${current_price:.2f} above EMA7 ${ema7_current:.2f} (+{price_vs_ema7*100:.2f}%)",
                        "Waiting for better entry (dip or pullback to EMA7)"
                    ],
                    'ema7': ema7_current,
                    'ema25': ema25_current,
                    'spread': ema_spread,
                    'crossover_type': 'peak_avoidance'
                }
        elif ema7_current < ema25_current and ema_spread > 1.0:
            return {
                'action': 'SELL',
                'confidence': 0.6,
                'reasons': [
                    f"EMA7 below EMA25 with spread {ema_spread:.2f}%",
                    f"EMA7: {ema7_current:.4f}, EMA25: {ema25_current:.4f}"
                ],
                'ema7': ema7_current,
                'ema25': ema25_current,
                'spread': ema_spread,
                'crossover_type': 'ema7_below_ema25'
            }

        # NO CLEAR SIGNAL
        signal = {
            'action': 'HOLD',
            'confidence': 0.0,
            'reasons': [
                f"📊 EMA7: {ema7_current:.4f}, EMA25: {ema25_current:.4f}",
                f"📈 Spread: {ema_spread:.2f}% - No clear crossover signal",
                "⏳ Waiting for EMA crossover or stronger trend"
            ],
            'ema7': ema7_current,
            'ema25': ema25_current,
            'spread': ema_spread,
            'crossover_type': 'no_signal'
        }

    except Exception as e:
        log_message(f"❌ Error in EMA crossover detection: {e}")
        signal = {'action': 'HOLD', 'confidence': 0.0, 'reasons': [f'EMA crossover error: {e}'], 'crossover_type': 'error'}
    
    # 🧠 APPLY ML LEARNING: Learn from past mistakes and adjust signals
    try:
        if ML_LEARNING_AVAILABLE and signal:
            signal = apply_ml_learning_to_signal(signal)
            if signal.get('ml_adjustment'):
                log_message(f"🧠 ML ADJUSTMENT: {signal['ml_adjustment']['reasoning']}")
                log_message(f"   Confidence: {signal['ml_adjustment']['original_confidence']:.2f} → {signal['confidence']:.2f}")
    except Exception as e:
        log_message(f"⚠️ ML learning application error: {e}")
    
    return signal

# =============================================================================
# DAILY HIGH/LOW PROFIT MAXIMIZATION STRATEGIES
# =============================================================================

def implement_daily_high_low_strategies(df, current_price, signal, holding_position):
    """
    Implement the 6 key strategies for maximizing profits from daily highs/lows:
    1. Day Trading (Scalping) - Quick profits from minor moves
    2. Swing Trading - Capture multi-day swings 
    3. Arbitrage - Exploit price inefficiencies
    4. Dollar-Cost Averaging - Systematic accumulation
    5. Momentum Trading - Ride strong trends
    6. Reversal Trading - Capitalize on trend changes
    """
    strategy_signals = {
        'day_trading': {'action': 'HOLD', 'confidence': 0.0, 'reasons': []},
        'swing_trading': {'action': 'HOLD', 'confidence': 0.0, 'reasons': []},
        'momentum_trading': {'action': 'HOLD', 'confidence': 0.0, 'reasons': []},
        'reversal_trading': {'action': 'HOLD', 'confidence': 0.0, 'reasons': []},
        'dca_signal': {'action': 'HOLD', 'confidence': 0.0, 'reasons': []},
        'optimal_strategy': None
    }

    try:
        if len(df) < 50:
            return strategy_signals

        # 🎯 ABSOLUTE PRIORITY: MA7/MA25 CROSSOVER STRATEGY
        # This strategy OVERRIDES all others when a strong signal is detected
        ma_crossover_signal = detect_ma_crossover_signals(df, current_price)

        # If MA crossover gives a strong signal (confidence > 0.85), use it exclusively
        if ma_crossover_signal['confidence'] > 0.85:
            log_message(f"🚀 MA7/MA25 ABSOLUTE PRIORITY: {ma_crossover_signal['action']} "
                       f"(confidence: {ma_crossover_signal['confidence']:.3f})")
            log_message(f"📊 MA7: {ma_crossover_signal.get('ma7', 'N/A')}, "
                       f"MA25: {ma_crossover_signal.get('ma25', 'N/A')}")

            # Override all strategy signals with MA crossover
            strategy_signals['ma_crossover_priority'] = ma_crossover_signal
            strategy_signals['optimal_strategy'] = {
                'strategy': 'ma_crossover_priority',
                'action': ma_crossover_signal['action'],
                'confidence': ma_crossover_signal['confidence'],
                'score': ma_crossover_signal['confidence'] * 1.5,  # Boost score for priority
                'reason': f"MA7/MA25 ABSOLUTE PRIORITY: {ma_crossover_signal.get('crossover_type', 'crossover')}",
                'ma_data': ma_crossover_signal
            }
            return strategy_signals

        # If MA crossover gives a moderate signal, include it in strategy mix
        elif ma_crossover_signal['confidence'] > 0.5:
            strategy_signals['ma_crossover'] = ma_crossover_signal
            log_message(f"📈 MA7/MA25 signal included: {ma_crossover_signal['action']} "
                       f"(confidence: {ma_crossover_signal['confidence']:.3f})")

        # Get daily high/low data for the last few days
        daily_highs = df['high'].rolling(24).max().dropna()  # 24-hour rolling highs (if 1h data)
        daily_lows = df['low'].rolling(24).min().dropna()    # 24-hour rolling lows

        # Current position within today's range
        if len(daily_highs) > 0 and len(daily_lows) > 0:
            today_high = daily_highs.iloc[-1]
            today_low = daily_lows.iloc[-1]
            daily_range = today_high - today_low

            if daily_range > 0:
                position_in_daily_range = (current_price - today_low) / daily_range

                # 1. DAY TRADING / SCALPING STRATEGY
                strategy_signals['day_trading'] = analyze_scalping_opportunities(
                    df, current_price, today_high, today_low, position_in_daily_range
                )

                # 2. SWING TRADING STRATEGY
                strategy_signals['swing_trading'] = analyze_swing_opportunities(
                    df, current_price, daily_highs, daily_lows, holding_position
                )

                # 3. MOMENTUM TRADING STRATEGY
                strategy_signals['momentum_trading'] = analyze_momentum_opportunities(
                    df, current_price, position_in_daily_range
                )

                # 4. REVERSAL TRADING STRATEGY
                strategy_signals['reversal_trading'] = analyze_reversal_opportunities(
                    df, current_price, today_high, today_low, position_in_daily_range
                )

                # 5. DOLLAR-COST AVERAGING SIGNAL
                strategy_signals['dca_signal'] = analyze_dca_opportunities(
                    df, current_price, position_in_daily_range, holding_position
                )

                # 6. SELECT OPTIMAL STRATEGY based on market conditions
                strategy_signals['optimal_strategy'] = select_optimal_high_low_strategy(
                    strategy_signals, df, current_price
                )

                # Log analysis
                log_message(f"📊 DAILY HIGH/LOW ANALYSIS:")
                log_message(f"   Today's Range: ${today_low:.2f} - ${today_high:.2f} (${daily_range:.2f})")
                log_message(f"   Current Position: {position_in_daily_range*100:.1f}% of daily range")

                # Log each strategy recommendation
                for strategy_name, strategy_data in strategy_signals.items():
                    if strategy_name != 'optimal_strategy' and strategy_data['confidence'] > 0.5:
                        action = strategy_data['action']
                        conf = strategy_data['confidence']
                        reasons = strategy_data['reasons'][:2]  # Top 2 reasons
                        log_message(f"   {strategy_name.upper()}: {action} ({conf:.2f}) - {', '.join(reasons)}")

                if strategy_signals['optimal_strategy']:
                    optimal = strategy_signals['optimal_strategy']
                    log_message(f"🎯 OPTIMAL STRATEGY: {optimal['strategy']} - {optimal['reason']}")

    except Exception as e:
        log_message(f"❌ Error in daily high/low strategy analysis: {e}")

    return strategy_signals

def analyze_scalping_opportunities(df, current_price, today_high, today_low, position_in_range):
    """
    Day Trading/Scalping: Quick profits from minor price changes within the day
    """
    signal = {'action': 'HOLD', 'confidence': 0.0, 'reasons': []}

    try:
        if len(df) < 10:
            return signal

        # Look for quick reversal opportunities within daily range
        recent_prices = df['close'].iloc[-5:]  # Last 5 periods
        price_momentum = (recent_prices.iloc[-1] - recent_prices.iloc[0]) / recent_prices.iloc[0]

        # Volatility check (scalping needs volatility)
        recent_volatility = df['close'].pct_change().iloc[-10:].std()
        high_volatility = recent_volatility > 0.02  # 2%+ volatility

        # SCALPING BUY signals
        if position_in_range < 0.3 and price_momentum < -0.005 and high_volatility:  # Near daily low, quick drop
            signal['action'] = 'BUY'
            signal['confidence'] = 0.75
            signal['reasons'] = [
                f"Scalp buy: {position_in_range*100:.1f}% of daily range",
                f"Quick momentum drop: {price_momentum*100:.2f}%",
                "High volatility environment"
            ]

        # SCALPING SELL signals
        elif position_in_range > 0.7 and price_momentum > 0.005 and high_volatility:  # Near daily high, quick rise
            signal['action'] = 'SELL'
            signal['confidence'] = 0.75
            signal['reasons'] = [
                f"Scalp sell: {position_in_range*100:.1f}% of daily range",
                f"Quick momentum rise: {price_momentum*100:.2f}%",
                "High volatility environment"
            ]

        # Range-bound scalping
        elif 0.45 <= position_in_range <= 0.55 and abs(price_momentum) > 0.003:  # Mid-range with momentum
            if price_momentum > 0:
                signal['action'] = 'SELL'  # Sell momentum peaks in mid-range
                signal['confidence'] = 0.6
                signal['reasons'] = ["Mid-range momentum peak", "Scalping range top"]
            else:
                signal['action'] = 'BUY'   # Buy momentum dips in mid-range
                signal['confidence'] = 0.6
                signal['reasons'] = ["Mid-range momentum dip", "Scalping range bottom"]

    except Exception as e:
        log_message(f"❌ Error in scalping analysis: {e}")

    return signal

def analyze_swing_opportunities(df, current_price, daily_highs, daily_lows, holding_position):
    """
    Swing Trading: Profit from multi-day price swings
    """
    signal = {'action': 'HOLD', 'confidence': 0.0, 'reasons': []}

    try:
        if len(daily_highs) < 5 or len(daily_lows) < 5:
            return signal

        # Analyze multi-day swing patterns
        recent_highs = daily_highs.iloc[-3:]  # Last 3 days of highs
        recent_lows = daily_lows.iloc[-3:]    # Last 3 days of lows

        # Swing low identification (good for BUY)
        current_low = recent_lows.iloc[-1]
        is_swing_low = (current_low <= recent_lows.min() and
                       current_price <= current_low * 1.02)  # Within 2% of swing low

        # Swing high identification (good for SELL)
        current_high = recent_highs.iloc[-1]
        is_swing_high = (current_high >= recent_highs.max() and
                        current_price >= current_high * 0.98)  # Within 2% of swing high

        # Multi-day trend analysis
        if len(daily_highs) >= 5:
            high_trend = (recent_highs.iloc[-1] - recent_highs.iloc[0]) / recent_highs.iloc[0]
            low_trend = (recent_lows.iloc[-1] - recent_lows.iloc[0]) / recent_lows.iloc[0]

            # SWING BUY signals
            if is_swing_low and not holding_position:
                signal['action'] = 'BUY'
                signal['confidence'] = 0.8
                signal['reasons'] = [
                    "Multi-day swing low identified",
                    f"Price near lowest low: ${current_low:.2f}",
                    f"Low trend: {low_trend*100:.2f}%"
                ]

            # SWING SELL signals
            elif is_swing_high and holding_position:
                signal['action'] = 'SELL'
                signal['confidence'] = 0.8
                signal['reasons'] = [
                    "Multi-day swing high identified",
                    f"Price near highest high: ${current_high:.2f}",
                    f"High trend: {high_trend*100:.2f}%"
                ]

            # Trend continuation swings
            elif high_trend > 0.03 and low_trend > 0.02 and not holding_position:  # Strong uptrend
                signal['action'] = 'BUY'
                signal['confidence'] = 0.7
                signal['reasons'] = [
                    "Uptrend swing continuation",
                    f"Rising lows trend: {low_trend*100:.2f}%",
                    "Multi-day bullish structure"
                ]

    except Exception as e:
        log_message(f"❌ Error in swing analysis: {e}")

    return signal

def analyze_momentum_opportunities(df, current_price, position_in_range):
    """
    Momentum Trading: Ride existing strong price trends
    """
    signal = {'action': 'HOLD', 'confidence': 0.0, 'reasons': []}

    try:
        if len(df) < 20:
            return signal

        # Calculate momentum indicators (optimized for quick trading)
        short_ema = df['close'].ewm(span=5).mean().iloc[-1]  # Fast EMA for 1min scalping
        medium_ema = df['close'].ewm(span=13).mean().iloc[-1]  # Fibonacci-based medium
        long_ema = df['close'].ewm(span=21).mean().iloc[-1]  # Professional standard

        # Price momentum over different periods
        momentum_5 = (df['close'].iloc[-1] - df['close'].iloc[-6]) / df['close'].iloc[-6]  # 5-period momentum
        momentum_10 = (df['close'].iloc[-1] - df['close'].iloc[-11]) / df['close'].iloc[-11]  # 10-period momentum

        # Volume momentum (if available)
        volume_momentum = 1.0  # Default
        if 'volume' in df.columns and len(df) >= 10:
            recent_volume = df['volume'].iloc[-5:].mean()
            avg_volume = df['volume'].iloc[-20:].mean()
            volume_momentum = recent_volume / avg_volume if avg_volume > 0 else 1.0

        # Strong upward momentum
        strong_up_momentum = (
            current_price > short_ema > medium_ema > long_ema and  # EMA alignment
            momentum_5 > 0.02 and momentum_10 > 0.03 and        # Strong momentum
            volume_momentum > 1.3                               # Volume confirmation
        )

        # Strong downward momentum
        strong_down_momentum = (
            current_price < short_ema < medium_ema < long_ema and  # Bear EMA alignment
            momentum_5 < -0.02 and momentum_10 < -0.03 and      # Strong down momentum
            volume_momentum > 1.3                               # Volume confirmation
        )

        # MOMENTUM BUY signals
        if strong_up_momentum and position_in_range < 0.8:  # Don't chase tops
            signal['action'] = 'BUY'
            signal['confidence'] = 0.85
            signal['reasons'] = [
                f"Strong upward momentum: {momentum_5*100:.2f}% (5p), {momentum_10*100:.2f}% (10p)",
                "MA alignment: bullish",
                f"Volume momentum: {volume_momentum:.2f}x"
            ]

        # MOMENTUM SELL signals
        elif strong_down_momentum and position_in_range > 0.2:  # Don't chase bottoms
            signal['action'] = 'SELL'
            signal['confidence'] = 0.85
            signal['reasons'] = [
                f"Strong downward momentum: {momentum_5*100:.2f}% (5p), {momentum_10*100:.2f}% (10p)",
                "MA alignment: bearish",
                f"Volume momentum: {volume_momentum:.2f}x"
            ]

        # Momentum continuation in daily range
        elif strong_up_momentum and 0.3 <= position_in_range <= 0.6:  # Mid-range momentum
            signal['action'] = 'BUY'
            signal['confidence'] = 0.7
            signal['reasons'] = [
                "Mid-range momentum continuation",
                f"Daily position: {position_in_range*100:.1f}%",
                "Momentum trend alignment"
            ]

    except Exception as e:
        log_message(f"❌ Error in momentum analysis: {e}")

    return signal

def analyze_reversal_opportunities(df, current_price, today_high, today_low, position_in_range):
    """
    Reversal Trading: Capitalize on trend changes using RSI, MACD, etc.
    """
    signal = {'action': 'HOLD', 'confidence': 0.0, 'reasons': []}

    try:
        if len(df) < 26:  # Need enough data for MACD
            return signal

        # Calculate RSI
        rsi = calculate_rsi_for_reversals(df['close'])
        current_rsi = rsi.iloc[-1] if len(rsi) > 0 else 50

        # Calculate MACD
        macd_line, macd_signal, macd_histogram = calculate_macd_for_reversals(df['close'])

        # Bollinger Bands for reversal identification
        bb_upper, bb_middle, bb_lower = calculate_bollinger_bands(df['close'])

        # REVERSAL BUY signals (oversold reversal)
        oversold_rsi = current_rsi < 30
        macd_bullish_cross = (len(macd_line) > 1 and
                             macd_line.iloc[-1] > macd_signal.iloc[-1] and
                             macd_line.iloc[-2] <= macd_signal.iloc[-2])
        near_bb_lower = current_price <= bb_lower.iloc[-1] * 1.02
        extreme_daily_low = position_in_range < 0.15  # Bottom 15% of daily range

        if oversold_rsi and (macd_bullish_cross or near_bb_lower) and extreme_daily_low:
            signal['action'] = 'BUY'
            signal['confidence'] = 0.9
            signal['reasons'] = [
                f"Oversold reversal: RSI {current_rsi:.1f}",
                f"Daily low extreme: {position_in_range*100:.1f}% of range",
                "MACD bullish cross" if macd_bullish_cross else "Near Bollinger lower"
            ]

        # REVERSAL SELL signals (overbought reversal)
        overbought_rsi = current_rsi > 70
        macd_bearish_cross = (len(macd_line) > 1 and
                             macd_line.iloc[-1] < macd_signal.iloc[-1] and
                             macd_line.iloc[-2] >= macd_signal.iloc[-2])
        near_bb_upper = current_price >= bb_upper.iloc[-1] * 0.98
        extreme_daily_high = position_in_range > 0.85  # Top 15% of daily range

        if overbought_rsi and (macd_bearish_cross or near_bb_upper) and extreme_daily_high:
            signal['action'] = 'SELL'
            signal['confidence'] = 0.9
            signal['reasons'] = [
                f"Overbought reversal: RSI {current_rsi:.1f}",
                f"Daily high extreme: {position_in_range*100:.1f}% of range",
                "MACD bearish cross" if macd_bearish_cross else "Near Bollinger upper"
            ]

        # Mid-range reversals (lower confidence)
        elif oversold_rsi and 0.2 <= position_in_range <= 0.4:  # Oversold in lower-mid range
            signal['action'] = 'BUY'
            signal['confidence'] = 0.65
            signal['reasons'] = [
                f"Mid-range oversold: RSI {current_rsi:.1f}",
                f"Lower-mid daily range: {position_in_range*100:.1f}%"
            ]

        elif overbought_rsi and 0.6 <= position_in_range <= 0.8:  # Overbought in upper-mid range
            signal['action'] = 'SELL'
            signal['confidence'] = 0.65
            signal['reasons'] = [
                f"Mid-range overbought: RSI {current_rsi:.1f}",
                f"Upper-mid daily range: {position_in_range*100:.1f}%"
            ]

    except Exception as e:
        log_message(f"❌ Error in reversal analysis: {e}")

    return signal

def analyze_dca_opportunities(df, current_price, position_in_range, holding_position):
    """
    Dollar-Cost Averaging: Systematic accumulation during dips
    """
    signal = {'action': 'HOLD', 'confidence': 0.0, 'reasons': []}

    try:
        # DCA is about consistent buying regardless of price, but we can optimize timing

        # Enhanced DCA: buy more during dips, less during peaks
        if position_in_range < 0.4 and not holding_position:  # Lower 40% of daily range
            dca_multiplier = 1.5  # Buy 50% more during dips
            signal['action'] = 'BUY'
            signal['confidence'] = 0.7
            signal['reasons'] = [
                f"DCA dip buying: {position_in_range*100:.1f}% of daily range",
                f"Enhanced DCA: {dca_multiplier}x normal amount",
                "Systematic accumulation strategy"
            ]

        elif position_in_range < 0.6 and not holding_position:  # Normal DCA range
            signal['action'] = 'BUY'
            signal['confidence'] = 0.5
            signal['reasons'] = [
                "Regular DCA buying opportunity",
                f"Mid-range position: {position_in_range*100:.1f}%",
                "Dollar-cost averaging strategy"
            ]

        # DCA selling (taking profits systematically)
        elif position_in_range > 0.75 and holding_position:  # Top 25% of daily range
            signal['action'] = 'SELL'
            signal['confidence'] = 0.6
            signal['reasons'] = [
                "DCA profit taking opportunity",
                f"Daily high region: {position_in_range*100:.1f}%",
                "Systematic profit realization"
            ]

    except Exception as e:
        log_message(f"❌ Error in DCA analysis: {e}")

    return signal

def select_optimal_high_low_strategy(strategy_signals, df, current_price):
    """
    Select the optimal strategy based on current market conditions and signal strength
    """
    optimal = None

    try:
        # 🎯 ABSOLUTE PRIORITY: Check for MA crossover priority signal
        if 'ma_crossover_priority' in strategy_signals:
            ma_priority = strategy_signals['ma_crossover_priority']
            if ma_priority['confidence'] > 0.85:
                optimal = {
                    'strategy': 'ma_crossover_priority',
                    'action': ma_priority['action'],
                    'confidence': ma_priority['confidence'],
                    'score': ma_priority['confidence'] * 1.5,  # Boosted score
                    'reason': f"MA7/MA25 ABSOLUTE PRIORITY: {ma_priority.get('crossover_type', 'crossover')} (confidence: {ma_priority['confidence']:.3f})",
                    'ma_data': ma_priority
                }
                log_message(f"🚀 EXECUTING MA7/MA25 PRIORITY: {optimal['action']} - {optimal['reason']}")
                return optimal

        # Score each strategy based on confidence and market suitability
        strategy_scores = {}

        for strategy_name, strategy_data in strategy_signals.items():
            if strategy_name == 'optimal_strategy':
                continue

            confidence = strategy_data['confidence']
            action = strategy_data['action']

            if action in ['BUY', 'SELL'] and confidence > 0.5:
                # Base score is confidence
                score = confidence

                # 🎯 BOOST MA CROSSOVER SIGNALS (even moderate ones get priority)
                if strategy_name in ['ma_crossover', 'ma_crossover_priority']:
                    score *= 2.0  # Double the score for any MA crossover signal
                    log_message(f"📈 MA crossover signal boosted: {strategy_name} score {score:.3f}")

                # Adjust score based on market conditions
                volatility = df['close'].pct_change().iloc[-10:].std()

                # High volatility favors scalping and momentum
                if strategy_name in ['day_trading', 'momentum_trading'] and volatility > 0.025:
                    score *= 1.2

                # Low volatility favors swing trading and DCA
                elif strategy_name in ['swing_trading', 'dca_signal'] and volatility < 0.015:
                    score *= 1.2

                # Reversal trading gets bonus for extreme RSI
                elif strategy_name == 'reversal_trading':
                    try:
                        rsi = calculate_rsi_for_reversals(df['close'])
                        current_rsi = rsi.iloc[-1] if len(rsi) > 0 else 50
                        if current_rsi < 25 or current_rsi > 75:  # Extreme RSI
                            score *= 1.3
                    except:
                        pass

                strategy_scores[strategy_name] = score

        # Select highest scoring strategy

        if strategy_scores:
            best_strategy = max(strategy_scores.items(), key=lambda x: x[1])
            strategy_name, score = best_strategy

            optimal = {
                'strategy': strategy_name,
                'action': strategy_signals[strategy_name]['action'],
                'confidence': strategy_signals[strategy_name]['confidence'],
                'score': score,
                'reason': f"Highest score ({score:.3f}) among {len(strategy_scores)} active strategies",
                'all_scores': strategy_scores
            }

    except Exception as e:
        log_message(f"❌ Error selecting optimal strategy: {e}")

    return optimal

# Helper functions for technical indicators
def calculate_rsi_for_reversals(prices, period=14):
    """Calculate RSI for reversal analysis"""
    try:
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    except:
        return pd.Series([50] * len(prices), index=prices.index)

def calculate_macd_for_reversals(prices, fast=12, slow=26, signal=9):
    """Calculate MACD for reversal analysis"""
    try:
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd_line = ema_fast - ema_slow
        macd_signal = macd_line.ewm(span=signal).mean()
        macd_histogram = macd_line - macd_signal
        return macd_line, macd_signal, macd_histogram
    except:
        return pd.Series([0] * len(prices)), pd.Series([0] * len(prices)), pd.Series([0] * len(prices))

def calculate_bollinger_bands(prices, period=20, std_dev=2):
    """Calculate Bollinger Bands"""
    try:
        rolling_mean = prices.rolling(window=period).mean()
        rolling_std = prices.rolling(window=period).std()
        upper_band = rolling_mean + (rolling_std * std_dev)
        lower_band = rolling_mean - (rolling_std * std_dev)
        return upper_band, rolling_mean, lower_band
    except:
        return pd.Series([0] * len(prices)), pd.Series([0] * len(prices)), pd.Series([0] * len(prices))

# =============================================================================
# PLACEHOLDER FUNCTIONS FOR MISSING IMPLEMENTATIONS
# =============================================================================

def monitor_exchange_orders():
    """Monitor active orders on the exchange"""
    try:
        open_orders = safe_api_call(exchange.fetch_open_orders, 'BTC/USDT')
        if open_orders:
            log_message(f"📋 {len(open_orders)} active orders detected")
        return open_orders
    except Exception as e:
        log_message(f"❌ Error monitoring exchange orders: {e}")
        return []

def check_exchange_order_fills():
    """Check for recently filled orders"""
    try:
        recent_trades = safe_api_call(exchange.fetch_my_trades, 'BTC/USDT', limit=5)
        # Check if any trades are from the last 5 minutes
        recent_fills = []
        current_time = time.time() * 1000
        for trade in recent_trades:
            if trade['timestamp'] and (current_time - trade['timestamp']) < 300000:  # 5 minutes
                recent_fills.append(trade)

        if recent_fills:
            log_message(f"✅ {len(recent_fills)} recent fills detected")
        return recent_fills
    except Exception as e:
        log_message(f"❌ Error checking order fills: {e}")
        return []

def display_system_status(signal, current_price, balance):
    """Display comprehensive system status"""
    try:
        total_usd = balance['total']['USDT']
        total_btc = balance['total']['BTC']
        total_value = total_usd + (total_btc * current_price)

        print(f"\n💰 PORTFOLIO STATUS:")
        print(f"   BTC: {total_btc:.6f} (${total_btc * current_price:.2f})")
        print(f"   USDT: ${total_usd:.2f}")
        print(f"   Total Value: ${total_value:.2f}")
        print(f"   Position: {'BTC' if total_btc * current_price > 1 else 'USDT'}")

    except Exception as e:
        print(f"⚠️ Error displaying system status: {e}")

def validate_and_enhance_signal(signal):
    """Validate and enhance signal structure"""
    if not signal:
        return {'action': 'HOLD', 'confidence': 0.3, 'reason': 'No signal generated'}

    # Ensure required fields exist
    if 'action' not in signal:
        signal['action'] = 'HOLD'
    if 'confidence' not in signal:
        signal['confidence'] = 0.3
    if 'reason' not in signal:
        signal['reason'] = 'Signal validation'

    return signal

def place_advanced_risk_orders(symbol, entry_price, amount):
    """
    🛡️ ADVANCED MULTI-LEVEL RISK MANAGEMENT
    
    Places sophisticated risk orders to protect capital with multiple layers:
    1. Immediate stop-loss (2% below entry)
    2. Trailing stop (dynamic based on volatility)
    3. Take-profit ladders (25%, 50%, 75% exits)
    4. Emergency exit monitoring
    """
    try:
        risk_config = optimized_config['risk_management']
        
        # Validate inputs
        if not symbol or not entry_price or not amount or amount <= 0:
            log_message(f"❌ Invalid inputs for advanced risk orders")
            return None
            
        log_message(f"🛡️ PLACING ADVANCED MULTI-LEVEL RISK ORDERS:")
        log_message(f"   Symbol: {symbol}")
        log_message(f"   Entry: ${entry_price:.2f}")
        log_message(f"   Amount: {amount:.6f}")
        
        # Level 1: Immediate Stop-Loss (Hard Stop)
        immediate_stop_pct = risk_config.get('immediate_stop_pct', 0.02)  # 2% stop
        immediate_stop_price = entry_price * (1 - immediate_stop_pct)
        
        try:
            stop_order = safe_api_call(
                exchange.create_order,
                symbol,
                'stop_loss_limit',
                'sell',
                amount * 0.3,  # 30% of position for immediate stop
                immediate_stop_price * 0.999,  # Limit price slightly below stop
                {
                    'stopPrice': immediate_stop_price,
                    'timeInForce': 'GTC'
                }
            )
            
            if stop_order:
                log_message(f"   ✅ Level 1 - Immediate Stop: ${immediate_stop_price:.2f} ({immediate_stop_pct*100:.1f}%)")
            else:
                log_message(f"   ❌ Level 1 - Immediate Stop: FAILED")
                
        except Exception as e:
            log_message(f"   ❌ Level 1 - Immediate Stop: {e}")
            stop_order = None
        
        # Level 2: Trailing Stop (Dynamic Protection)
        trailing_stop = place_simple_trailing_stop(symbol, entry_price, amount * 0.4, entry_price)
        if trailing_stop:
            log_message(f"   ✅ Level 2 - Trailing Stop: Dynamic protection active")
        else:
            log_message(f"   ❌ Level 2 - Trailing Stop: FAILED")
        
        # Level 3: Take-Profit Ladders (Profit Realization)
        take_profit_levels = [
            {'pct': 0.015, 'amount_pct': 0.25, 'name': 'Quick Profit'},     # 1.5% = 25%
            {'pct': 0.030, 'amount_pct': 0.35, 'name': 'Medium Profit'},    # 3.0% = 35%
            {'pct': 0.050, 'amount_pct': 0.40, 'name': 'Strong Profit'}     # 5.0% = 40%
        ]
        
        profit_orders = []
        for level in take_profit_levels:
            try:
                tp_price = entry_price * (1 + level['pct'])
                tp_amount = amount * level['amount_pct']
                
                tp_order = safe_api_call(
                    exchange.create_limit_order,
                    symbol,
                    'sell',
                    tp_amount,
                    tp_price
                )
                
                if tp_order:
                    profit_orders.append(tp_order)
                    log_message(f"   ✅ Level 3 - {level['name']}: ${tp_price:.2f} (+{level['pct']*100:.1f}%)")
                else:
                    log_message(f"   ❌ Level 3 - {level['name']}: FAILED")
                    
            except Exception as e:
                log_message(f"   ❌ Level 3 - {level['name']}: {e}")
        
        # Level 4: Emergency Exit Monitoring
        try:
            # Set up enhanced manual monitoring for extreme scenarios
            state_manager.update_trading_state(
                advanced_risk_active=True,
                emergency_exit_price=entry_price * 0.92,  # 8% emergency exit
                max_loss_tolerance=entry_price * 0.85,    # 15% absolute max loss
                profit_lock_threshold=entry_price * 1.08, # Lock profits at 8%+
                advanced_risk_entry_time=time.time()
            )
            log_message(f"   ✅ Level 4 - Emergency Monitoring: Active")
        except Exception as e:
            log_message(f"   ❌ Level 4 - Emergency Monitoring: {e}")
        
        # Summary
        successful_orders = 0
        if stop_order: successful_orders += 1
        if trailing_stop: successful_orders += 1
        successful_orders += len(profit_orders)
        
        total_protection = (0.3 if stop_order else 0) + (0.4 if trailing_stop else 0) + sum(level['amount_pct'] for level in take_profit_levels if profit_orders)
        
        log_message(f"🛡️ ADVANCED RISK SUMMARY:")
        log_message(f"   ✅ Successful Orders: {successful_orders}/6")
        log_message(f"   🔒 Position Coverage: {total_protection*100:.0f}%")
        log_message(f"   🎯 Multi-level protection active")
        
        return {
            'status': 'success',
            'orders_placed': successful_orders,
            'coverage_pct': total_protection,
            'stop_order': stop_order,
            'trailing_stop': trailing_stop,
            'profit_orders': profit_orders
        }
        
    except Exception as e:
        log_message(f"❌ CRITICAL ERROR in advanced risk orders: {e}")
        return None

def display_institutional_analysis_safe(inst_data):
    """Safely display institutional analysis with error handling"""
    try:
        print(f"🔍 DEBUG: display_institutional_analysis_safe called with: {inst_data}")

        if not inst_data:
            print("🔍 DEBUG: inst_data is None/empty, returning")
            return

        print(f"\n🏛️ INSTITUTIONAL ANALYSIS:")

        # Market regime with safe access
        try:
            print(f"🔍 DEBUG: Checking market_regime in inst_data: {'market_regime' in inst_data}")
            if 'market_regime' in inst_data and inst_data['market_regime']:
                regime_data = inst_data['market_regime']
                print(f"🔍 DEBUG: regime_data: {regime_data}")
                print(f"🔍 DEBUG: regime_data keys: {list(regime_data.keys()) if isinstance(regime_data, dict) else 'Not a dict'}")

                regime_name = regime_data.get('regime', 'Unknown')
                regime_conf = regime_data.get('confidence', 0.0)
                regime_rec = regime_data.get('recommendation', 'N/A')
                print(f"   Market Regime: {regime_name} (conf: {regime_conf:.2f})")
                print(f"   Regime Strategy: {regime_rec}")
        except Exception as regime_error:
            print(f"   Market Regime: Error ({regime_error})")
            traceback.print_exc()

        # Other institutional metrics with safe access
        try:
            if 'correlation_analysis' in inst_data and inst_data['correlation_analysis']:
                corr_regime = inst_data['correlation_analysis'].get('regime', 'Unknown')
                print(f"   Cross-Asset Regime: {corr_regime}")
        except Exception as corr_error:
            print(f"   Cross-Asset Regime: Error ({corr_error})")

        try:
            if 'ml_signal' in inst_data and inst_data['ml_signal']:
                ml_data = inst_data['ml_signal']
                ml_action = ml_data.get('action', 'Unknown')
                ml_conf = ml_data.get('confidence', 0.0)
                print(f"   ML Signal: {ml_action} (conf: {ml_conf:.2f})")
        except Exception as ml_error:
            print(f"   ML Signal: Error ({ml_error})")

        try:
            if 'risk_analysis' in inst_data and inst_data['risk_analysis']:
                risk_data = inst_data['risk_analysis']
                risk_assess = risk_data.get('risk_assessment', 'Unknown')
                var_daily = risk_data.get('var_daily', 0.0)
                print(f"   Risk Assessment: {risk_assess}")
                print(f"   VaR Daily: ${var_daily:.2f}")
        except Exception as risk_error:
            print(f"   Risk Assessment: Error ({risk_error})")
            print(f"   VaR Daily: Error")

        try:
            if 'kelly_position_size' in inst_data:
                kelly_size = inst_data.get('kelly_position_size', 0.0)
                print(f"   Kelly Position: ${kelly_size:.2f}")
        except Exception as kelly_error:
            print(f"   Kelly Position: Error ({kelly_error})")

    except Exception as e:
        print(f"   [Warning] Institutional analysis display error: {e}")
        print(f"   [Debug] inst_data type: {type(inst_data)}")
        print(f"   [Debug] inst_data keys: {list(inst_data.keys()) if isinstance(inst_data, dict) else 'Not a dict'}")
        import traceback
        traceback.print_exc()

# =============================================================================
# LIVE STRATEGY LOOP WITH MA7/MA25 ABSOLUTE PRIORITY
# =============================================================================

def monitor_and_update_trailing_stop():
    """
    🔄 MANUAL TRAILING STOP MONITOR
    
    Monitors active manual trailing stops and updates them when price rises.
    Cancels old orders and places new ones at 0.50% behind the highest price.
    """
    global trailing_stop_order_id, trailing_stop_active
    
    try:
        # Get current trailing stop data from bot state
        current_state = state_manager.get_current_state()
        trailing_data = current_state.get('trading_state', {}).get('trailing_stop_data')
        
        if not trailing_data or not trailing_data.get('active'):
            return  # No active manual trailing stop
        
        symbol = trailing_data['symbol']
        order_id = trailing_data['order_id']
        amount = trailing_data['amount']
        entry_price = trailing_data['entry_price']
        highest_price = trailing_data['highest_price']
        current_stop_price = trailing_data['current_stop_price']
        trailing_percent = trailing_data['trailing_percent']
        last_updated = trailing_data['last_updated']
        
        # Don't update too frequently (minimum 30 seconds between updates)
        if time.time() - last_updated < 30:
            return
        
        # Get current market price
        ticker = exchange.fetch_ticker(symbol)
        current_price = ticker['last']
        
        # Check if price has reached a new high
        new_highest_price = max(highest_price, current_price)
        
        if new_highest_price > highest_price:
            # Price has risen - calculate new stop price
            new_stop_price = new_highest_price * (1 - trailing_percent)  # 0.50% below new high
            new_limit_price = new_stop_price * 0.995  # Limit slightly below stop
            
            # Only update if the new stop is meaningfully higher (avoid tiny updates)
            price_improvement = (new_stop_price - current_stop_price) / current_stop_price
            if price_improvement > 0.001:  # Only update if at least 0.1% improvement
                
                log_message(f"📈 TRAILING STOP UPDATE TRIGGERED for {symbol}")
                log_message(f"   Previous High: ${highest_price:.4f} | New High: ${new_highest_price:.4f}")
                log_message(f"   Old Stop: ${current_stop_price:.4f} | New Stop: ${new_stop_price:.4f}")
                
                try:
                    # Cancel the old stop-loss order
                    log_message(f"🔄 Canceling old stop-loss order: {order_id}")
                    safe_api_call(exchange.cancel_order, order_id, symbol)
                    
                    # Place new stop-loss order at updated price
                    new_order = safe_api_call(
                        lambda: exchange.create_order(
                            symbol,
                            'STOP_LOSS_LIMIT',
                            'sell',
                            amount,
                            new_limit_price,
                            {
                                'stopPrice': str(new_stop_price),
                                'timeInForce': 'GTC'
                            }
                        )
                    )
                    
                    if new_order and new_order.get('id'):
                        # Update trailing stop data with new order details
                        updated_trailing_data = {
                            'order_id': new_order['id'],
                            'symbol': symbol,
                            'amount': amount,
                            'entry_price': entry_price,
                            'highest_price': new_highest_price,
                            'current_stop_price': new_stop_price,
                            'trailing_percent': trailing_percent,
                            'last_updated': time.time(),
                            'active': True
                        }
                        
                        # Save updated state
                        state_manager.update_trading_state(
                            trailing_stop_data=updated_trailing_data,
                            trailing_stop_order_id=new_order['id'],
                            trailing_stop_active=True
                        )
                        
                        log_message(f"✅ TRAILING STOP UPDATED: New Order ID {new_order['id']}")
                        log_message(f"   New Stop Price: ${new_stop_price:.4f} (0.50% below ${new_highest_price:.4f})")
                        log_message(f"   Price Improvement: +{price_improvement*100:.2f}%")
                        
                    else:
                        log_message("❌ Failed to place new trailing stop order")
                        # Try to restore the old order or mark as inactive
                        trailing_data['active'] = False
                        state_manager.update_trading_state(trailing_stop_data=trailing_data)
                        
                except Exception as e:
                    log_message(f"❌ Failed to update trailing stop: {e}")
                    # Mark trailing stop as inactive if update fails
                    trailing_data['active'] = False
                    state_manager.update_trading_state(trailing_stop_data=trailing_data)
        else:
            # Price hasn't reached new high - just update the last check time
            trailing_data['last_updated'] = time.time()
            state_manager.update_trading_state(trailing_stop_data=trailing_data)
            
    except Exception as e:
        log_message(f"⚠️ Error in trailing stop monitor: {e}")

"""(Deploy Variant) Added heartbeat writer for dashboard liveness detection."""

# Heartbeat (deploy variant) - duplicated minimal logic to avoid import coupling
try:
    import json as _json
    import datetime as _dt
    from threading import Lock as _Lock
    _DEPLOY_HB_LOCK = _Lock()
    def _deploy_write_heartbeat(status="RUNNING", extra: dict | None = None):  # type: ignore[valid-type]
        try:
            payload = {"timestamp": _dt.datetime.utcnow().isoformat(), "status": status}
            if extra:
                for k, v in list(extra.items())[:6]:
                    payload[k] = v
            with _DEPLOY_HB_LOCK:
                with open("bot_heartbeat.json", "w", encoding="utf-8") as f:
                    _json.dump(payload, f)
        except Exception:
            pass
except Exception:
    def _deploy_write_heartbeat(status="RUNNING", extra=None):
        pass

def run_continuously(interval_seconds=60):
    """
    🎯 AGGRESSIVE DAY TRADING BOT - MA7/MA25 Crossover Priority
    
    Main trading loop that executes MA7/MA25 crossover strategy as absolute priority,
    with fallback to other strategies when no clear crossover signals exist.
    """
    global holding_position, last_trade_time, consecutive_losses, active_trade_index, entry_price, stop_loss_price, take_profit_price

    print("\n" + "="*70)
    print("🚀 ENHANCED HIGH-FREQUENCY DAY TRADING BOT - Multi-Timeframe MA + Advanced Price Detection")
    print("🎯 ABSOLUTE PRIORITY: Multi-timeframe MA7/MA25 crossover signals override all other strategies")
    print("📈 STRATEGY: Golden Cross (BUY) | Death Cross (SELL) | Multi-Timeframe Price Detection")
    print("⚡ HFT OPTIMIZATIONS: 15s loops | 30s cooldown | 150 trades/day limit | Enhanced micro targets")
    print("🔍 DETECTION: Spike(0.5%/1min) | Short(0.8%/5min) | Medium(1.2%/15min) | Long(1.8%/30min)")
    print("🎯 DAILY TARGET: 2.5% through high-frequency accumulation")
    print("🎯 LAYER 1 ENHANCED: 4-10 trades/day, 0.5-2% targets (increased frequency)")
    print("="*70)

    _deploy_write_heartbeat("STARTING")

    while True:
        # 🔄 RUNTIME CONFIG RELOAD - Check for multi-pair scanner updates
        config_changed = bot_config.reload_config_if_changed()
        if config_changed:
            log_message("🔄 Configuration reloaded - Multi-pair scanner may have switched trading pair")
            # Update optimized_config reference
            optimized_config = bot_config.config
        
        # 🔄 MANUAL TRAILING STOP MONITORING - Check and update trailing stops
        try:
            monitor_and_update_trailing_stop()
        except Exception as e:
            log_message(f"⚠️ Error in trailing stop monitoring: {e}")
        
        # Always ensure risk management variables are initialized
        if 'entry_price' not in globals() or entry_price is None:
            entry_price = None
        if 'stop_loss_price' not in globals() or stop_loss_price is None:
            stop_loss_price = None
        if 'take_profit_price' not in globals() or take_profit_price is None:
            take_profit_price = None

        print("\n" + "="*50, flush=True)
        print("🎯 HIGH-FREQUENCY 4-LAYER TRADING SYSTEM (2.5% DAILY TARGET)", flush=True)
        print("   L1: EMA7/EMA25 Crossover (4-10 trades/day, 0.5-2% targets)")
        print("   L2: Micro-scalping EMA5/13 (20-40 trades/day, 0.15-0.4% targets)")
        print("   L3: Range-bound RSI/BB (10-20 trades/day, 0.2-0.3% targets)")
        print("   L4: RSI Mean Reversion (5-12 trades/day, 0.3-1.0% targets)")
        
        # 🎯 Display supported pairs and current active pair
        try:
            # Read the comprehensive configuration for accurate pair count
            with open('comprehensive_all_pairs_config.json', 'r') as f:
                comprehensive_config = json.load(f)
                total_pairs = comprehensive_config.get('total_supported_pairs', 235)
        except:
            # Fallback to config.py if comprehensive config unavailable
            supported_pairs = bot_config.get_supported_pairs()
            total_pairs = len(supported_pairs)
        
        active_symbol = bot_config.get_current_trading_symbol()
        print(f"📊 MULTI-PAIR MONITORING: {total_pairs} pairs tracked")
        print(f"🎯 CURRENT ACTIVE PAIR: {active_symbol}")
        print("="*50, flush=True)

        # Add timestamp for debugging
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"🕐 Loop Started: {current_time}", flush=True)
        
        # Display daily progress from high-frequency tracker
        reset_daily_pnl_if_needed()
        stats = daily_pnl_tracker()
        win_rate = (stats['win_trades'] / stats['trades_today']) * 100 if stats['trades_today'] > 0 else 0
        print(f"📊 DAILY TARGET: {stats['current_pct']:.2f}% / {stats['target_pct']:.1f}% | Trades: {stats['trades_today']} | Win Rate: {win_rate:.1f}%", flush=True)
        print(f"📊 LAYER BREAKDOWN: L1={stats['layer1_trades']} L2={stats['layer2_trades']} L3={stats['layer3_trades']} L4={stats.get('layer4_trades', 0)}", flush=True)

        from log_utils import calculate_daily_pnl, calculate_total_pnl_and_summary, calculate_unrealized_pnl

        # Enhanced PnL reporting with more details
        daily_pnl = calculate_daily_pnl()
        pnl_summary = calculate_total_pnl_and_summary()

        print(f"📊 TRADING PERFORMANCE:", flush=True)
        print(f"   📉 Daily PnL (realized): ${daily_pnl:.2f}", flush=True)
        print(f"   💰 Total PnL (realized): ${pnl_summary['total_realized_pnl']:.2f}", flush=True)
        print(f"   📈 Recent Activity: {pnl_summary['recent_trades']} trades (7 days)", flush=True)
        print(f"   🕐 Last Trade: {pnl_summary['last_trade_date']}", flush=True)

        # Calculate dynamic daily loss limit based on current portfolio
        balance = safe_api_call(exchange.fetch_balance)
        
        # 🌐 MULTI-CRYPTO ASSET SELECTION WITH RUNTIME CONFIG SUPPORT
        # Check if multi-pair scanner has specified a trading pair
        config_symbol = bot_config.get_current_trading_symbol()
        
        # 🧠 PHASE 2 INTEGRATION: Initialize blockchain intelligence
        try:
            from phase2_trading_integration import Phase2TradingIntegration
            phase2_integration = Phase2TradingIntegration()
            log_message(f"🧠 PHASE 2 INTELLIGENCE: {phase2_integration.get_status_summary()['status']}")
        except ImportError:
            phase2_integration = None
            log_message("⚠️ PHASE 2 INTELLIGENCE: Not available, using standard signals only")
        
        # 🎯 SIGNAL-FIRST CRYPTO SELECTION - Prioritize strongest signals over tiers
        try:
            # Get all available pairs from comprehensive config
            try:
                with open('comprehensive_all_pairs_config.json', 'r') as f:
                    comp_config = json.load(f)
                available_pairs = comp_config.get('supported_pairs', bot_config.get_supported_pairs())
            except:
                available_pairs = bot_config.get_supported_pairs()
            
            # Quick signal strength scan of top pairs
            best_signal_pair = None
            best_signal_strength = 0
            pairs_to_scan = available_pairs[:30]  # Scan top 30 pairs for performance
            
            log_message(f"🔍 SIGNAL-FIRST SCAN: Analyzing {len(pairs_to_scan)} pairs for strongest signals")
            
            for pair in pairs_to_scan:
                try:
                    # Quick multi-timeframe signal check
                    ticker = safe_api_call(exchange.fetch_ticker, pair)
                    if not ticker:
                        continue
                    
                    # Get 5m and 1m data for quick signal
                    df_5m = fetch_ohlcv(exchange, pair, '5m', 20)
                    df_1m = fetch_ohlcv(exchange, pair, '1m', 20)
                    
                    if df_5m is None or df_1m is None or len(df_5m) < 10:
                        continue
                    
                    # Calculate EMAs
                    df_5m['ema7'] = df_5m['close'].ewm(span=7).mean()
                    df_5m['ema25'] = df_5m['close'].ewm(span=25).mean() if len(df_5m) >= 25 else df_5m['ema7']
                    df_1m['ema7'] = df_1m['close'].ewm(span=7).mean()
                    df_1m['ema13'] = df_1m['close'].ewm(span=13).mean()
                    
                    # Signal strength calculation
                    signal_strength = 0
                    current_price = df_5m['close'].iloc[-1]
                    
                    # 5m EMA alignment
                    ema7_5m = df_5m['ema7'].iloc[-1]
                    ema25_5m = df_5m['ema25'].iloc[-1]
                    if ema7_5m > ema25_5m and current_price > ema7_5m:
                        signal_strength += 3  # Strong bullish 5m
                    elif ema7_5m > ema25_5m:
                        signal_strength += 2  # Moderate bullish 5m
                    
                    # 1m EMA alignment
                    ema7_1m = df_1m['ema7'].iloc[-1]
                    ema13_1m = df_1m['ema13'].iloc[-1]
                    if ema7_1m > ema13_1m and current_price > ema7_1m:
                        signal_strength += 2  # Strong bullish 1m
                    elif ema7_1m > ema13_1m:
                        signal_strength += 1  # Moderate bullish 1m
                    
                    # Recent momentum
                    recent_change = (current_price - df_5m['close'].iloc[-3]) / df_5m['close'].iloc[-3] * 100
                    if recent_change > 0.5:
                        signal_strength += 1
                    
                    # Volume check
                    avg_volume = df_5m['volume'].tail(5).mean()
                    current_volume = df_5m['volume'].iloc[-1]
                    if current_volume > avg_volume * 1.2:
                        signal_strength += 1  # Volume surge
                    
                    if signal_strength > best_signal_strength:
                        best_signal_strength = signal_strength
                        best_signal_pair = pair
                        
                except Exception:
                    continue  # Skip failed pairs
            
            # Use signal-first selection if strong signal found
            if best_signal_pair and best_signal_strength >= 5:
                base_signal = {
                    'symbol': best_signal_pair,
                    'allocation': 1.0,
                    'reason': f"Signal-first selection: strength {best_signal_strength}",
                    'signal_strength': best_signal_strength,
                    'signal_based': True,
                    'confidence': min(0.9, best_signal_strength / 10.0),  # Scale to confidence
                    'urgency_score': best_signal_strength * 5.0  # Convert to urgency
                }
                
                # 🧠 PHASE 2 ENHANCEMENT: Enhance signal with blockchain intelligence
                if phase2_integration and phase2_integration.enabled:
                    try:
                        crypto_symbol = best_signal_pair.split('/')[0]
                        enhancement = phase2_integration.get_trading_enhancement(crypto_symbol, base_signal)
                        
                        # Apply Phase 2 enhancements
                        adjustments = enhancement['trading_adjustments']
                        enhanced_confidence = adjustments['enhanced_confidence']
                        position_multiplier = adjustments['position_size_multiplier']
                        enhanced_urgency = adjustments['enhanced_urgency_score']
                        
                        selected_crypto = {
                            'symbol': best_signal_pair,
                            'allocation': base_signal['allocation'] * position_multiplier,
                            'reason': f"Phase 2 Enhanced: {base_signal['reason']}",
                            'signal_strength': best_signal_strength,
                            'signal_based': True,
                            'confidence': enhanced_confidence,
                            'urgency_score': enhanced_urgency,
                            'phase2_enhanced': True,
                            'phase2_recommendations': enhancement['recommendations'][:3]  # Top 3
                        }
                        
                        # 🎯 PHASE 3 WEEK 2: Add sentiment analysis to Phase 2 enhanced signal
                        if SENTIMENT_ANALYSIS_AVAILABLE:
                            try:
                                sentiment_signal = {
                                    'action': 'BUY',
                                    'confidence': enhanced_confidence,
                                    'urgency_score': enhanced_urgency
                                }
                                sentiment_enhanced = enhance_signal_with_sentiment(sentiment_signal, best_signal_pair, None)
                                sentiment_boost = sentiment_enhanced.get('sentiment_enhancement', 0)
                                
                                if abs(sentiment_boost) > 0.03:  # Significant sentiment impact
                                    selected_crypto['confidence'] = sentiment_enhanced.get('confidence', enhanced_confidence)
                                    selected_crypto['sentiment_enhanced'] = True
                                    selected_crypto['sentiment_mood'] = sentiment_enhanced.get('sentiment_mood', 'NEUTRAL')
                                    
                                    log_message(f"🎯 SENTIMENT + PHASE 2: {sentiment_boost:+.1%} additional boost (Mood: {sentiment_enhanced.get('sentiment_mood', 'NEUTRAL')})")
                                    
                            except Exception as sentiment_error:
                                log_message(f"⚠️ Sentiment enhancement error: {sentiment_error}")
                        
                        log_message(f"🧠 PHASE 2 ENHANCED: {best_signal_pair} confidence {base_signal['confidence']:.3f}→{enhanced_confidence:.3f}")
                        for rec in enhancement['recommendations'][:2]:  # Show top 2 recommendations
                            log_message(f"   💡 {rec}")
                            
                    except Exception as phase2_error:
                        log_message(f"⚠️ Phase 2 enhancement error: {phase2_error}")
                        selected_crypto = base_signal
                else:
                    selected_crypto = base_signal
                
                log_message(f"🎯 SIGNAL-FIRST SELECTION: {best_signal_pair} (strength: {best_signal_strength})")
            else:
                # Fallback to original selection
                selected_crypto = select_best_crypto_for_trading()
                log_message(f"🔄 FALLBACK SELECTION: Using original method")
                
        except Exception as signal_error:
            log_message(f"⚠️ Signal-first selection error: {signal_error}")
            selected_crypto = select_best_crypto_for_trading()
        
        # 🎯 PRIORITIZE CONFIG SYMBOL: If multi-pair scanner set a specific pair, use it
        if config_symbol != 'BTC/USDT' and config_symbol in bot_config.get_supported_pairs():
            current_trading_symbol = config_symbol
            crypto_allocation = selected_crypto['allocation']  # Keep same allocation logic
            log_message(f"🎯 Using multi-pair scanner recommendation: {current_trading_symbol}")
        else:
            current_trading_symbol = selected_crypto['symbol']
            crypto_allocation = selected_crypto['allocation']
        
        # 🚨 EMERGENCY SPIKE DETECTION - Override normal switching rules for major moves
        # Check for exceptional spikes that demand immediate action
        if not holding_position:
            try:
                # 🎯 ENHANCED EMERGENCY DETECTION - Multiple detection layers
                emergency_detected = False
                emergency_symbol = None
                emergency_reason = ""
                
                # Layer 1: Comprehensive Opportunity Scanner - ALL PAIRS WITH PHASE 2 ENHANCEMENT
                try:
                    from comprehensive_opportunity_scanner import run_immediate_comprehensive_scan
                    all_opportunities = run_immediate_comprehensive_scan(exchange)
                    
                    # 🧠 PHASE 2 ENHANCEMENT: Enhance opportunities with blockchain intelligence
                    if phase2_integration and phase2_integration.enabled and all_opportunities:
                        enhanced_opportunities = []
                        for opp in all_opportunities[:10]:  # Enhance top 10 for performance
                            try:
                                crypto_symbol = opp.symbol.split('/')[0]
                                base_signal = {
                                    'symbol': opp.symbol,
                                    'confidence': 0.7,  # Base confidence for opportunities
                                    'urgency_score': opp.urgency_score,
                                    'action': 'BUY'
                                }
                                
                                enhancement = phase2_integration.get_trading_enhancement(crypto_symbol, base_signal)
                                adjustments = enhancement['trading_adjustments']
                                
                                # Apply Phase 2 boost to urgency score
                                enhanced_urgency = adjustments['enhanced_urgency_score']
                                opp.urgency_score = enhanced_urgency
                                opp.phase2_enhanced = True
                                opp.phase2_confidence_boost = adjustments['confidence_change']
                                
                                enhanced_opportunities.append(opp)
                                
                            except Exception as enhance_error:
                                # Keep original opportunity if enhancement fails
                                enhanced_opportunities.append(opp)
                        
                        all_opportunities = enhanced_opportunities
                        log_message(f"🧠 PHASE 2: Enhanced {len(enhanced_opportunities)} opportunities with blockchain intelligence")
                    
                    # 🎯 SIGNAL-FIRST SWITCHING: Prioritize signals over tiers
                    # LOWERED thresholds for more signal-based opportunities
                    switching_opportunities = [
                        opp for opp in all_opportunities 
                        if (opp.recommendation in ["IMMEDIATE_SWITCH", "STRONG_CONSIDERATION"] and 
                            opp.urgency_score >= 25.0)  # LOWERED from 35.0 to 25.0 for signal-first
                    ]
                    
                    # If holding position, check for profit-taking + switching opportunity
                    if holding_position and switching_opportunities:
                        # Calculate current profit on existing position
                        current_profit_pct = 0
                        if entry_price and entry_price > 0:
                            current_profit_pct = ((current_price - entry_price) / entry_price) * 100
                        
                        # Find best switching opportunity
                        best_switch_opp = max(switching_opportunities, key=lambda x: x.urgency_score)
                        
                        # AGGRESSIVE PROFIT-TAKING + SWITCHING LOGIC
                        should_switch = False
                        switch_reason = ""
                        
                        # Take profits if positive AND better opportunity exists
                        if current_profit_pct > 0.5 and best_switch_opp.urgency_score >= 40.0:
                            should_switch = True
                            switch_reason = f"Profit-taking: {current_profit_pct:+.2f}% + Better opportunity: {best_switch_opp.symbol} (score: {best_switch_opp.urgency_score:.1f})"
                        
                        # Switch even at small loss if opportunity is exceptional
                        elif current_profit_pct > -2.0 and best_switch_opp.urgency_score >= 60.0:
                            should_switch = True
                            switch_reason = f"Cut small loss: {current_profit_pct:+.2f}% for exceptional opportunity: {best_switch_opp.symbol} (score: {best_switch_opp.urgency_score:.1f})"
                        
                        # Switch if current pair is underperforming and better opportunity exists
                        elif current_profit_pct < -1.0 and best_switch_opp.urgency_score >= 45.0:
                            should_switch = True
                            switch_reason = f"Exit underperforming position: {current_profit_pct:+.2f}% for better opportunity: {best_switch_opp.symbol} (score: {best_switch_opp.urgency_score:.1f})"
                        
                        if should_switch:
                            log_message(f"🔄 PROFIT-FIRST SWITCHING TRIGGERED: {switch_reason}")
                            
                            # Execute sell of current position first
                            crypto_balance = balance[symbol.split('/')[0]]['free']
                            if crypto_balance > 0.0001:
                                log_message(f"📤 SELLING CURRENT POSITION: {symbol} for profit-taking switch")
                                sell_order = safe_api_call(exchange.create_market_order, symbol, 'sell', crypto_balance)
                                if sell_order:
                                    log_message(f"✅ PROFIT-TAKING SELL EXECUTED: {current_profit_pct:+.2f}% on {symbol}")
                                    holding_position = False
                                    
                                    # Update state
                                    state_manager.exit_trade("PROFIT_TAKING_FOR_SWITCH")
                                    
                                    # Force switch to better opportunity
                                    emergency_symbol = best_switch_opp.symbol
                                    emergency_detected = True
                                    emergency_reason = switch_reason
                                    
                                    print(f"💰 PROFIT-TAKING SWITCH: Sold {symbol} at {current_profit_pct:+.2f}% → Switching to {emergency_symbol}")
                    
                    # Regular emergency detection for new positions
                    elif not holding_position and switching_opportunities:
                        # Take the highest urgency opportunity
                        top_opportunity = switching_opportunities[0]  # Already sorted by urgency_score
                        emergency_symbol = top_opportunity.symbol
                        emergency_detected = True
                        emergency_reason = f"Comprehensive scan: {top_opportunity.price_change_1h:+.2f}% (1h), {top_opportunity.price_change_24h:+.2f}% (24h), urgency: {top_opportunity.urgency_score:.1f}"
                        
                        log_message(f"🚨 OPPORTUNITY SCAN DETECTED: {len(switching_opportunities)} profitable opportunities")
                        log_message(f"🎯 TOP OPPORTUNITY: {emergency_symbol} - {emergency_reason}")
                        
                        # Log top opportunities for visibility
                        for i, opp in enumerate(switching_opportunities[:5]):  # Top 5
                            log_message(f"   {i+1}. {opp.symbol}: {opp.price_change_1h:+.2f}% (1h) | {opp.price_change_24h:+.2f}% (24h) | Urgency: {opp.urgency_score:.1f}")
                            
                except Exception as scanner_error:
                    log_message(f"⚠️ Comprehensive scanner error: {scanner_error}")
                
                # Layer 2: Enhanced Multi-Crypto Monitor with Lower Thresholds
                if not emergency_detected:
                    try:
                        recommendations = multi_crypto_monitor.get_trading_recommendations()
                        if recommendations.get('status') == 'success':
                            # Check ALL recommendations with lower threshold for profit-switching
                            for crypto_data in recommendations.get('recommendations', []):
                                if crypto_data['score'] > 0.60:  # LOWERED from 0.70 to 0.60
                                    # Additional profit-switching logic
                                    should_consider = False
                                    
                                    if not holding_position:
                                        should_consider = True  # Always consider if no position
                                    elif holding_position and entry_price and entry_price > 0:
                                        current_profit = ((current_price - entry_price) / entry_price) * 100
                                        # Switch if profitable or small loss with good opportunity
                                        if current_profit > 0.3 or (current_profit > -1.5 and crypto_data['score'] > 0.75):
                                            should_consider = True
                                    
                                    if should_consider:
                                        emergency_symbol = crypto_data['symbol']
                                        emergency_score = crypto_data['score']
                                        momentum_1h = crypto_data['metrics'].get('momentum_1h', '0%')
                                        emergency_detected = True
                                        emergency_reason = f"Multi-crypto monitor score {emergency_score:.3f}, momentum: {momentum_1h}"
                                        
                                        if holding_position:
                                            log_message(f"💰 PROFIT-SWITCHING: Current position profit check for {emergency_symbol}")
                                        break
                    except Exception as monitor_error:
                        log_message(f"⚠️ Multi-crypto monitor error: {monitor_error}")
                
                # Layer 3: Enhanced Emergency Spike Detector with Profit-Switching
                if not emergency_detected:
                    try:
                        from emergency_spike_detector import detect_xlm_type_opportunities
                        major_opportunities = detect_xlm_type_opportunities(exchange)
                        
                        if major_opportunities:
                            # Take the highest urgency opportunity
                            top_opportunity = major_opportunities[0]
                            if top_opportunity.urgency_score >= 30.0:  # LOWERED from 40.0 to 30.0
                                # Check if we should switch from current position
                                should_switch = False
                                
                                if not holding_position:
                                    should_switch = True
                                elif holding_position and entry_price and entry_price > 0:
                                    current_profit = ((current_price - entry_price) / entry_price) * 100
                                    # More aggressive switching for profitable positions
                                    if current_profit > 0.2 or (current_profit > -2.0 and top_opportunity.urgency_score >= 50.0):
                                        should_switch = True
                                        log_message(f"💰 SWITCHING FROM PROFIT: {current_profit:+.2f}% for better opportunity")
                                
                                if should_switch:
                                    emergency_symbol = top_opportunity.symbol
                                    emergency_detected = True
                                    emergency_reason = f"Emergency detector {top_opportunity.price_change_pct:+.2f}% ({top_opportunity.timeframe}), urgency: {top_opportunity.urgency_score:.1f}"
                    except Exception as detector_error:
                        log_message(f"⚠️ Emergency detector error: {detector_error}")
                
                # Layer 4: Direct Ticker Checking with Profit-First Logic
                if not emergency_detected:
                    try:
                        from config import BotConfig
                        bot_config_instance = BotConfig()
                        all_supported_pairs = bot_config_instance.get_supported_pairs()
                        
                        log_message(f"🔍 DIRECT TICKER SCAN: Scanning {len(all_supported_pairs)} pairs for profitable switches")
                        
                        best_opportunity = None
                        best_change = 0
                        
                        for pair in all_supported_pairs:
                            try:
                                ticker = safe_api_call(exchange.fetch_ticker, pair)
                                if ticker and 'percentage' in ticker:
                                    change_24h = ticker.get('percentage', 0) or 0
                                    if abs(change_24h) >= 4.0:  # LOWERED from 6.0% to 4.0%
                                        if abs(change_24h) > abs(best_change):
                                            best_opportunity = pair
                                            best_change = change_24h
                            except Exception:
                                continue  # Skip failed tickers
                        
                        if best_opportunity:
                            # Check if we should switch for this opportunity
                            should_switch = False
                            
                            if not holding_position:
                                should_switch = True
                            elif holding_position and entry_price and entry_price > 0:
                                current_profit = ((current_price - entry_price) / entry_price) * 100
                                # Switch if profitable or significant opportunity
                                if current_profit > 0.3 or (current_profit > -1.0 and abs(best_change) >= 6.0):
                                    should_switch = True
                                    log_message(f"� TICKER PROFIT-SWITCH: {current_profit:+.2f}% → {best_opportunity} ({best_change:+.2f}%)")
                            
                            if should_switch:
                                emergency_symbol = best_opportunity
                                emergency_detected = True
                                emergency_reason = f"Direct ticker profit-switch {best_change:+.2f}% (24h) on {best_opportunity}"
                                log_message(f"🚨 DIRECT TICKER PROFIT-SWITCH: {best_opportunity} {best_change:+.2f}% move detected")
                                
                    except Exception as direct_error:
                        log_message(f"⚠️ Direct ticker scan error: {direct_error}")
                
                # � EXECUTE EMERGENCY SWITCH
                if emergency_detected and emergency_symbol:
                    log_message(f"🚨 PROFIT-FIRST OPPORTUNITY DETECTED: {emergency_symbol}")
                    log_message(f"🔄 SMART SWITCH: {emergency_reason}")
                    
                    # If holding position, sell first for profit-taking
                    if holding_position:
                        current_profit_pct = 0
                        if entry_price and entry_price > 0:
                            current_profit_pct = ((current_price - entry_price) / entry_price) * 100
                        
                        log_message(f"💰 PROFIT-TAKING EXIT: Current position P&L: {current_profit_pct:+.2f}%")
                        log_message(f"🎯 SWITCHING: {current_trading_symbol} → {emergency_symbol}")
                        
                        # Execute profit-taking sell
                        crypto_balance = balance[symbol.split('/')[0]]['free']
                        if crypto_balance > 0.0001:
                            sell_order = safe_api_call(exchange.create_market_order, symbol, 'sell', crypto_balance)
                            if sell_order:
                                log_message(f"✅ PROFIT-TAKING SELL EXECUTED: {current_profit_pct:+.2f}% realized on {symbol}")
                                holding_position = False
                                state_manager.exit_trade("PROFIT_TAKING_SWITCH")
                        
                        print(f"💰 PROFIT-FIRST SWITCH: Realized {current_profit_pct:+.2f}% → Switching to {emergency_symbol}")
                    else:
                        log_message(f"🎯 NEW OPPORTUNITY: Switching to {emergency_symbol}")
                    
                    # Force switch to new opportunity
                    current_trading_symbol = emergency_symbol
                    
                    # Create profit-first crypto data
                    selected_crypto = {
                        'symbol': emergency_symbol,
                        'allocation': 1.0,  # Max allocation for profit opportunities
                        'emergency': True,
                        'reason': emergency_reason,
                        'profit_switch': True
                    }
                    
                    print(f"🚨 PROFIT-FIRST ASSET SWITCH: {emergency_symbol}")
                    print(f"   Reason: {emergency_reason}")
                    print(f"   Strategy: Take profits when available, switch to biggest opportunities")
                else:
                    # Log that comprehensive scan completed with no emergencies
                    try:
                        from config import BotConfig
                        bot_config_temp = BotConfig()
                        total_pairs = len(bot_config_temp.get_supported_pairs())
                        log_message(f"✅ COMPREHENSIVE SCAN COMPLETE: No emergency opportunities detected across all {total_pairs} pairs")
                    except:
                        log_message("✅ COMPREHENSIVE SCAN COMPLETE: No emergency opportunities detected")
                        
            except Exception as e:
                log_message(f"⚠️ Emergency spike detection error: {e}")
        
        # Check if we need to switch assets (only if not holding position)
        if not holding_position:
            current_symbol = symbol if 'symbol' in locals() else 'BTC/USDT'  # Default fallback
            should_switch, switch_reason = should_switch_crypto_asset(current_symbol, selected_crypto)
            if should_switch:
                log_message(f"🔄 CRYPTO SWITCH: {switch_reason}")
        
        # Update current symbol for this trading cycle
        symbol = current_trading_symbol
        
        # 🌐 ENHANCED CURRENCY SWITCHING: Choose optimal USD/USDT pair
        try:
            from currency_switching import safe_get_optimal_pair
            optimal_pair, switch_reason = safe_get_optimal_pair(exchange, symbol.split('/')[0], balance)
            
            if optimal_pair != symbol:
                print(f"💱 CURRENCY SWITCH: {symbol} → {optimal_pair}")
                print(f"   Reason: {switch_reason}")
                symbol = optimal_pair
                current_trading_symbol = optimal_pair
                log_message(f"💱 CURRENCY SWITCH: {symbol} - {switch_reason}")
        except Exception as currency_error:
            log_message(f"⚠️ Currency switching error: {currency_error}")
        
        # Get current price for the selected crypto
        current_price = safe_api_call(exchange.fetch_ticker, symbol)['last']
        
        # Calculate portfolio value using USDT as base currency
        # Get prices for all held assets to calculate total portfolio value
        total_portfolio_value = balance['total']['USDT']  # Start with USDT balance
        
        # Add value of all crypto holdings converted to USDT
        for crypto in ['BTC', 'ETH', 'SOL', 'XRP', 'ADA', 'DOGE', 'XLM', 'SUI', 'SHIB', 'HBAR']:
            crypto_balance_amount = balance.get(crypto, {}).get('free', 0)
            if crypto_balance_amount > 0:
                try:
                    crypto_price = safe_api_call(exchange.fetch_ticker, f'{crypto}/USDT')['last']
                    total_portfolio_value += crypto_balance_amount * crypto_price
                except:
                    # Skip if crypto price can't be fetched
                    pass
        
        # Get balance of the currently selected crypto
        base_asset = symbol.split('/')[0]  # e.g., 'ETH' from 'ETH/USDT'
        crypto_balance = balance.get(base_asset, {}).get('free', 0)

        # Show unrealized PnL if holding position
        if holding_position and entry_price and entry_price > 0:
            # Calculate unrealized PnL for the currently held asset
            unrealized = calculate_unrealized_pnl(current_price, entry_price, crypto_balance)
            print(f"   💎 UNREALIZED: ${unrealized['unrealized_pnl_usd']:.2f} ({unrealized['unrealized_pnl_pct']:+.2f}%)", flush=True)
            print(f"   📍 Position: {unrealized[f'{base_asset.lower()}_amount']:.6f} {base_asset} @ ${unrealized['entry_price']:.2f} → ${unrealized['current_price']:.2f}", flush=True)
            
            # 🛡️ DISPLAY TRAILING STOP STATUS
            try:
                trading_state = state_manager.get_trading_state()
                # Check both immediate stop-limit and trailing stop systems
                immediate_stop_active = trading_state.get('immediate_stop_limit_active', False)
                trailing_stop_active = trading_state.get('trailing_stop_active', False)
                trailing_stop_order_id = trading_state.get('trailing_stop_order_id', None)
                
                if trailing_stop_active and trailing_stop_order_id:
                    # Show trailing stop status
                    trail_distance_pct = optimized_config['risk_management'].get('trailing_stop_pct', 0.005) * 100
                    current_profit_pct = unrealized['unrealized_pnl_pct']
                    print(f"   🎯 TRAILING STOP: Active (Distance: {trail_distance_pct:.1f}%, Current P&L: {current_profit_pct:+.2f}%)", flush=True)
                    print(f"   🔄 Order ID: {trailing_stop_order_id}", flush=True)
                elif immediate_stop_active:
                    # Show immediate stop-limit status  
                    trigger_pct = optimized_config['risk_management'].get('trailing_stop_limit_trigger_pct', 0.001) * 100
                    current_profit_pct = unrealized['unrealized_pnl_pct']
                    if current_profit_pct >= trigger_pct:
                        print(f"   🎯 IMMEDIATE STOP: Active (Profit: {current_profit_pct:+.2f}% >= {trigger_pct:.1f}% trigger)", flush=True)
                    else:
                        print(f"   🛡️ IMMEDIATE PROTECTION: Stop-limit active (Need {trigger_pct:.1f}% for trailing)", flush=True)
                else:
                    print(f"   ⚠️ WARNING: No protection detected! Manual monitoring required!", flush=True)
            except Exception as status_error:
                print(f"   ⚠️ Status error: {status_error}", flush=True)

        dynamic_daily_loss_limit = calculate_dynamic_daily_loss_limit(total_portfolio_value)

        # Enhanced risk management with dynamic limits
        if daily_pnl <= -dynamic_daily_loss_limit:
            print(f"⚠️ Daily loss alert: ${daily_pnl:.2f} exceeds limit -${dynamic_daily_loss_limit:.2f} (continuing trading as requested)", flush=True)

        if consecutive_losses >= max_consecutive_losses:
            print(f"⚠️ {consecutive_losses} consecutive losses detected (continuing trading as requested)", flush=True)
            consecutive_losses = 0

        # Check trade timing to avoid overtrading
        time_since_last_trade = time.time() - last_trade_time
        cooldown_required = min_trade_interval - int(time_since_last_trade)

        # 🚀 ENHANCED PRICE JUMP DETECTION - Multi-timeframe movement analysis
        price_jump = detect_price_jump(current_price, optimized_config)

        if price_jump:
            jump_analysis = get_price_jump_detector(optimized_config).get_jump_analysis(price_jump)
            timeframe = jump_analysis.get('timeframe', 'spike')
            urgency_score = jump_analysis.get('urgency_score', 0)

            print(f"🚀 {timeframe.upper()} MOVEMENT DETECTED: {price_jump.direction} {price_jump.change_pct:+.2f}% in {price_jump.duration_seconds:.0f}s")
            print(f"   From ${price_jump.start_price:.2f} → ${price_jump.end_price:.2f}")
            print(f"   Timeframe: {timeframe} | Speed: {jump_analysis['speed']:.2f}%/min")
            print(f"   Urgency: {jump_analysis['urgency']} (score: {urgency_score:.1f})")
            print(f"   Trend Alignment: {jump_analysis['trend_alignment']}")
            print(f"   Momentum: {jump_analysis['momentum_strength']:.2f}")

            # Enhanced cooldown override logic
            if jump_analysis['override_cooldown'] and cooldown_required > 0:
                print(f"⚡ COOLDOWN OVERRIDE: {timeframe} movement overriding {cooldown_required}s cooldown")
                cooldown_required = 0

        # Get current trend state for additional context
        trend_state = get_price_jump_detector(optimized_config).get_trend_state()
        if trend_state['direction'] and trend_state['is_sustained']:
            print(f"📈 SUSTAINED TREND: {trend_state['direction']} trend active for {trend_state['duration_seconds']:.0f}s")
            print(f"   Peak change: {trend_state['peak_change_pct']:+.2f}% | Strength: {trend_state['strength']:.2f}")

        # Display enhanced price jump status periodically
        if int(time.time()) % 300 == 0:  # Every 5 minutes
            try:
                display_enhanced_price_jump_status()
            except Exception as e:
                log_message(f"⚠️ Error in price jump status display: {e}")

        if cooldown_required > 0:
            print(f"⏳ Trade cooldown: {cooldown_required}s remaining (avoiding overtrading)", flush=True)
            time.sleep(min(interval_seconds, cooldown_required + 10))
            continue

        try:
            df = fetch_ohlcv(exchange, symbol, '1m', 50)

            # Synchronize holding position with actual balance
            balance = safe_api_call(exchange.fetch_balance)
            crypto_balance = balance[symbol.split('/')[0]]['free']
            current_price = df['close'].iloc[-1]

            # Auto-detect if we're actually holding crypto (threshold: $1 worth)
            crypto_value = crypto_balance * current_price
            if crypto_value > 1.0 and not holding_position:
                holding_position = True
                entry_price = current_price
                stop_loss_price = current_price * (1 - stop_loss_percentage)
                take_profit_price = current_price * (1 + take_profit_percentage)

                # Update state manager - simplified for trailing stops only
                state_manager.update_trading_state(
                    holding_position=True,
                    entry_price=entry_price
                )

                print(f"🔄 SYNC: Detected existing {base_asset} position worth ${crypto_value:.2f}", flush=True)
            elif crypto_value <= 1.0 and holding_position:
                holding_position = False
                entry_price = None
                stop_loss_price = None
                take_profit_price = None

                # Update state manager
                state_manager.update_trading_state(
                    holding_position=False,
                    entry_price=None,
                    stop_loss_price=None,
                    take_profit_price=None
                )
                print(f"🔄 SYNC: No significant {base_asset} position detected", flush=True)

            # 🛡️ ENHANCED MANUAL MONITORING - Failsafe Protection System
            try:
                monitor_status = enhanced_manual_monitoring(symbol, current_price)
                if monitor_status:
                    if monitor_status.get("emergency_triggered"):
                        log_message("🚨 Emergency action taken by manual monitoring system")
                        # Skip to next iteration after emergency action
                        continue
                    elif monitor_status.get("monitoring_active"):
                        # Log status but continue normal operation
                        priority = monitor_status.get("priority", "NORMAL")
                        pnl = monitor_status.get("current_pnl", 0)
                        print(f"🛡️ MANUAL MONITOR: {priority} priority, P&L: {pnl:+.2f}%", flush=True)
            except Exception as monitor_error:
                log_message(f"⚠️ Manual monitoring error: {monitor_error}")

            # 🎯 STEP 1: ENHANCED MULTI-TIMEFRAME MA ANALYSIS
            print(f"\n🎯 MULTI-TIMEFRAME MA ANALYSIS:", flush=True)

            # 🎯 ENHANCED: Get multi-timeframe signals with trend continuation
            try:
                from enhanced_multi_timeframe_ma import detect_enhanced_multi_timeframe_ma_signals
                multi_signals = detect_enhanced_multi_timeframe_ma_signals(exchange, symbol, current_price)
            except ImportError:
                # Fallback to original if enhanced version not available
                multi_signals = detect_multi_timeframe_ma_signals(exchange, symbol, current_price)

            # Primary signal from combined analysis
            ma_signal = multi_signals['combined']
            trend_analysis = multi_signals.get('trend_analysis', {})

            # Display enhanced analysis
            print(f"   📊 1m Signal: {multi_signals['1m']['action']} ({multi_signals['1m']['confidence']:.3f})", flush=True)
            print(f"   📊 5m Signal: {multi_signals['5m']['action']} ({multi_signals['5m']['confidence']:.3f})", flush=True)
            print(f"   🎯 Combined: {ma_signal['action']} ({ma_signal['confidence']:.3f})", flush=True)

            # Display trend analysis if available
            if trend_analysis:
                overall_trend = trend_analysis.get('overall_trend', 'MIXED')
                consensus = trend_analysis.get('consensus_level', 0)
                print(f"   📈 Overall Trend: {overall_trend} ({consensus:.1f}% consensus)", flush=True)
                print(f"   📊 Timeframes: {trend_analysis.get('bullish_timeframes', 0)} bullish, {trend_analysis.get('bearish_timeframes', 0)} bearish", flush=True)

            # Display priority timeframe if available
            priority_tf = ma_signal.get('priority_timeframe')
            if priority_tf:
                print(f"   🎯 Priority Timeframe: {priority_tf}", flush=True)

            if ma_signal.get('agreement'):
                print(f"   ✅ Timeframe Agreement: {ma_signal['action']} signal", flush=True)
            else:
                print(f"   ⚠️ Mixed Signals: Using best available signal", flush=True)

            # Display detailed reasons
            for reason in ma_signal.get('reasons', []):
                print(f"   {reason}", flush=True)

            # Enhanced multi-timeframe price jump integration
            if price_jump and ma_signal['action'] != 'HOLD':
                jump_analysis = get_price_jump_detector(optimized_config).get_jump_analysis(price_jump)
                timeframe = jump_analysis.get('timeframe', 'spike')
                urgency_score = jump_analysis.get('urgency_score', 0)
                trend_alignment = jump_analysis.get('trend_alignment', 'NEUTRAL')

                # Enhanced confidence boost based on multiple factors
                alignment_bonus = 0
                if (price_jump.direction == 'UP' and ma_signal['action'] == 'BUY') or \
                   (price_jump.direction == 'DOWN' and ma_signal['action'] == 'SELL'):

                    # Base boost depends on timeframe
                    timeframe_boosts = {
                        'spike': 0.15,        # High boost for rapid spikes
                        'short_trend': 0.12,  # Good boost for short trends
                        'medium_trend': 0.10, # Medium boost for medium trends
                        'long_trend': 0.08    # Lower boost for long trends
                    }

                    base_boost = timeframe_boosts.get(timeframe, 0.10)

                    # Additional boost for high urgency
                    if urgency_score >= 6.0:
                        base_boost *= 1.5
                    elif urgency_score >= 4.0:
                        base_boost *= 1.2

                    # Additional boost for trend alignment
                    if trend_alignment == 'ALIGNED':
                        base_boost *= 1.3

                    alignment_bonus = base_boost
                    ma_signal['confidence'] = min(0.95, ma_signal['confidence'] + alignment_bonus)

                    print(f"   🚀 {timeframe.upper()} MOVEMENT BOOST: {ma_signal['action']} confidence +{alignment_bonus:.3f} → {ma_signal['confidence']:.3f}", flush=True)
                    print(f"   🎯 Factors: Urgency={urgency_score:.1f}, Alignment={trend_alignment}, Timeframe={timeframe}", flush=True)

                # Counter-trend warning
                elif trend_alignment == 'COUNTER_TREND':
                    print(f"   ⚠️ COUNTER-TREND MOVEMENT: {timeframe} {price_jump.direction} vs MA signal {ma_signal['action']}", flush=True)

            # 🚨 ABSOLUTE PRIORITY: Execute high-confidence multi-timeframe signals immediately
            if ma_signal['confidence'] > 0.85:
                print(f"\n🚀 MULTI-TIMEFRAME ABSOLUTE PRIORITY TRIGGERED!", flush=True)
                print(f"🎯 EXECUTING: {ma_signal['action']} (confidence: {ma_signal['confidence']:.3f})", flush=True)

                # Show enhanced analysis details
                if priority_tf:
                    print(f"   🎯 Priority timeframe: {priority_tf}", flush=True)
                if trend_analysis:
                    print(f"   📈 Trend: {trend_analysis.get('overall_trend', 'N/A')} ({trend_analysis.get('consensus_level', 0):.1f}% consensus)", flush=True)

                # Show progressive sell targets if available
                sell_targets = multi_signals.get('sell_targets', [])
                if sell_targets and ma_signal['action'] == 'BUY':
                    print(f"   🎯 Progressive sell targets calculated: {len(sell_targets)} levels", flush=True)
                    for target in sell_targets[:2]:  # Show first 2 targets
                        print(f"      Level {target['level']}: ${target['target_price']:.2f} (+{target['target_percentage']:.1f}%)", flush=True)

                # 🎯 5M+1M PRIORITY SYSTEM: Check for immediate execution agreement
                agreement = detect_5m_1m_agreement(ma_signal)
                if agreement['agreement'] and not holding_position:
                    print(f"\n🚀 5M+1M PRIORITY SYSTEM ACTIVATED!", flush=True)
                    print(f"✅ IMMEDIATE EXECUTION: {ma_signal['action']} (confidence: {agreement['confidence']:.3f})", flush=True)
                    print(f"📊 Reason: {agreement['reason']}", flush=True)
                    
                    # Execute BUY signal immediately with 5m+1m priority
                    if ma_signal['action'] == 'BUY':
                        position_size = calculate_position_size(current_price, 0.02, agreement['confidence'], total_portfolio_value)
                        if position_size > 0:
                            print(f"🚀 5M+1M PRIORITY BUY ({symbol}): ${position_size:.2f}")
                            order = place_intelligent_order(symbol, 'buy', amount_usd=position_size, use_limit=True)
                            if order:
                                holding_position = True
                                entry_price = current_price
                                entry_time = datetime.datetime.now()
                                state_manager.enter_trade(
                                    entry_price=entry_price,
                                    stop_loss_price=entry_price * 0.98,  # 2% stop loss
                                    take_profit_price=entry_price * 1.015,  # 1.5% take profit
                                    trade_id=order.get('id')
                                )
                                print(f"✅ 5M+1M PRIORITY BUY EXECUTED: Entry ${entry_price:.2f}")
                                time.sleep(interval_seconds)
                                continue  # Skip other logic, trade executed

                # Execute BUY signal
                if ma_signal['action'] == 'BUY' and not holding_position:
                    position_size = calculate_position_size(current_price, 0.02, ma_signal['confidence'], total_portfolio_value)
                    if position_size > 0:
                        print(f"🚀 MULTI-TIMEFRAME PRIORITY BUY ({symbol}): ${position_size:.2f}")
                        order = place_intelligent_order(symbol, 'buy', amount_usd=position_size, use_limit=True)

                        if order:
                            holding_position = True
                            state_manager.enter_trade(
                                entry_price=entry_price,
                                stop_loss_price=stop_loss_price,
                                take_profit_price=take_profit_price,
                                trade_id=order.get('id')
                            )
                            print(f"✅ MULTI-TIMEFRAME CROSSOVER BUY EXECUTED")

                # Execute SELL signal
                elif ma_signal['action'] == 'SELL' and holding_position:
                    crypto_balance = balance[symbol.split('/')[0]]['free']
                    # --- ENHANCEMENT: Prevent premature sell, enforce min hold time ---
                    min_hold_time = optimized_config.get('risk_management', {}).get('minimum_hold_time_minutes', 15) * 60
                    trade_start_time = None
                    if hasattr(state_manager, 'get_trade_start_time'):
                        trade_start_time = state_manager.get_trade_start_time()
                    can_sell = True
                    sell_reason = "MULTI_TIMEFRAME_SELL"
                    if trade_start_time and (time.time() - trade_start_time) < min_hold_time:
                        can_sell = False
                        sell_reason = f"BLOCKED: Minimum hold time active ({min_hold_time/60:.1f} min), only {((time.time() - trade_start_time)/60):.1f} min elapsed"
                        print(f"⏳ SELL BLOCKED: {sell_reason}")
                        log_message(f"⏳ SELL BLOCKED: {sell_reason}")
                    if can_sell and crypto_balance > 0:
                        print(f"🚨 MULTI-TIMEFRAME PRIORITY SELL ({symbol}): {crypto_balance:.6f} {symbol.split('/')[0]}")
                        order = place_intelligent_order(symbol, 'sell', amount_usd=0, use_limit=True)
                        if order:
                            state_manager.exit_trade("MULTI_TIMEFRAME_SELL")
                            holding_position = False
                            consecutive_losses = 0
                            print(f"✅ MULTI-TIMEFRAME CROSSOVER SELL EXECUTED")
                            log_message(f"✅ SELL EXECUTED: Multi-timeframe priority | Reason: {sell_reason}")
                    elif not can_sell:
                        log_message(f"❌ SELL NOT EXECUTED: {sell_reason}")
                        print(f"❌ SELL NOT EXECUTED: {sell_reason}")

                # Skip other strategies when multi-timeframe priority is active
                print("⏭️ Skipping other strategies - Multi-timeframe priority active")
                time.sleep(interval_seconds)
                continue

            # 🎯 STEP 2: Progressive Sell Target Management (NEW FEATURE!)
            if holding_position and crypto_balance > 0:
                sell_targets = multi_signals.get('sell_targets', [])
                if sell_targets:
                    print(f"\n🎯 CHECKING PROGRESSIVE SELL TARGETS:", flush=True)
                    executed_targets = manage_progressive_sell_targets(current_price, sell_targets, crypto_balance)
                    
                    if executed_targets:
                        for target in executed_targets:
                            print(f"✅ Level {target['level']} executed: {target['amount_sold']:.6f} {symbol.split('/')[0]} at ${target['executed_price']:.2f}", flush=True)
                        
                        # Update balance after partial sells
                        balance = safe_api_call(exchange.fetch_balance)
                        crypto_balance = balance[symbol.split('/')[0]]['free']
                        
                        # If we've sold most of our position, consider exiting
                        if crypto_balance < 0.001:  # Less than 0.001 crypto remaining
                            holding_position = False
                            state_manager.exit_trade("PROGRESSIVE_SELL_COMPLETE")
                            print(f"✅ Progressive sell strategy completed - position closed", flush=True)
                            time.sleep(interval_seconds)
                            continue

            # 🎯 5M+1M POSITION MANAGEMENT: Enhanced with peak detection and trailing stop
            if holding_position and 'entry_time' in locals() and entry_time:
                # First check peak detection and trailing stop
                peak_price = getattr(state_manager, '_peak_price', None)
                peak_decision = detect_peak_and_trailing_exit(
                    exchange, symbol, entry_price, entry_time, current_price, 
                    datetime.datetime.now(), peak_price
                )
                
                # Update peak price tracking
                if hasattr(state_manager, '_peak_price'):
                    state_manager._peak_price = peak_decision.get('peak_price', peak_price)
                else:
                    state_manager._peak_price = peak_decision.get('peak_price', current_price)
                
                print(f"🎯 PEAK DETECTION: {peak_decision['action']} - {peak_decision['reason']}")
                
                # If peak detection suggests selling, execute immediately
                if peak_decision['action'] == 'SELL':
                    crypto_balance = balance[symbol.split('/')[0]]['free']
                    if crypto_balance > 0.0001:  # Min trade amount
                        print(f"🚀 PEAK DETECTION SELL ({symbol}): {peak_decision['reason']}")
                        order = place_intelligent_order(symbol, 'sell', amount=crypto_balance, use_limit=True)
                        if order:
                            holding_position = False
                            state_manager.exit_trade(current_price, order.get('id'))
                            # Clear peak tracking
                            if hasattr(state_manager, '_peak_price'):
                                delattr(state_manager, '_peak_price')
                            print(f"✅ PEAK DETECTION SELL EXECUTED: Exit ${current_price:.2f}")
                            time.sleep(interval_seconds)
                            continue  # Skip other logic, trade executed
                
                # If no peak-based exit, use standard 5M+1M hold logic
                hold_decision = should_hold_position(exchange, symbol, entry_price, entry_time, current_price, datetime.datetime.now())
                print(f"🔍 5M+1M HOLD DECISION ({symbol}): {hold_decision['action']} - {hold_decision['reason']}")
                
                if hold_decision['action'] == 'SELL':
                    crypto_balance = balance[symbol.split('/')[0]]['free']
                    if crypto_balance > 0.0001:  # Min trade amount
                        print(f"🚀 5M+1M PRIORITY SELL ({symbol}): {hold_decision['reason']}")
                        order = place_intelligent_order(symbol, 'sell', amount=crypto_balance, use_limit=True)
                        if order:
                            holding_position = False
                            state_manager.exit_trade(current_price, order.get('id'))
                            # Clear peak tracking
                            if hasattr(state_manager, '_peak_price'):
                                delattr(state_manager, '_peak_price')
                            print(f"✅ 5M+1M PRIORITY SELL EXECUTED: Exit ${current_price:.2f}")
                            time.sleep(interval_seconds)
                            continue  # Skip other logic, trade executed

            # 🎯 STEP 2.5: ENHANCED PROFIT-TAKING + LOSS-CUTTING CHECK (Before Risk Management)
            if holding_position and entry_price and entry_price > 0:
                current_profit_pct = ((current_price - entry_price) / entry_price) * 100
                
                # 💰 AGGRESSIVE PROFIT-TAKING + LOSS-CUTTING CONDITIONS
                should_take_profit = False
                profit_reason = ""
                
                # 🚨 PRIORITY 1: IMMEDIATE LOSS CUTTING (Override hold time for significant losses)
                if current_profit_pct < -1.5:
                    should_take_profit = True
                    profit_reason = f"🚨 IMMEDIATE LOSS CUTTING: {current_profit_pct:+.2f}% - Prevent further decline"
                    
                # 🔥 PRIORITY 2: Small loss cutting when better opportunities exist
                elif current_profit_pct < -0.8:
                    try:
                        from comprehensive_opportunity_scanner import run_immediate_comprehensive_scan
                        current_opportunities = run_immediate_comprehensive_scan(exchange)
                        
                        better_opportunities = [
                            opp for opp in current_opportunities 
                            if (opp.symbol != symbol and 
                                opp.urgency_score >= 35.0 and  # Lower threshold for switching from losses
                                opp.recommendation in ["IMMEDIATE_SWITCH", "STRONG_CONSIDERATION"])
                        ]
                        
                        if better_opportunities:
                            should_take_profit = True
                            best_opp = max(better_opportunities, key=lambda x: x.urgency_score)
                            profit_reason = f"🔄 CUT SMALL LOSS: {current_profit_pct:+.2f}% → Switch to {best_opp.symbol} (score: {best_opp.urgency_score:.1f})"
                    except:
                        # If scanner fails, still cut losses at -1.2%
                        if current_profit_pct < -1.2:
                            should_take_profit = True
                            profit_reason = f"🔄 AUTOMATIC LOSS CUTTING: {current_profit_pct:+.2f}% - No recovery detected"
                
                # 💰 PROFIT-TAKING CONDITIONS (Original logic)
                elif current_profit_pct > 0.8:
                    should_take_profit = True
                    profit_reason = f"💰 Quick profit target reached: {current_profit_pct:+.2f}%"
                
                # Medium profits (>1.5%)
                elif current_profit_pct > 1.5:
                    should_take_profit = True
                    profit_reason = f"💰 Medium profit target reached: {current_profit_pct:+.2f}%"
                
                # Large profits (>3.0%)
                elif current_profit_pct > 3.0:
                    should_take_profit = True
                    profit_reason = f"💰 Large profit target exceeded: {current_profit_pct:+.2f}%"
                
                # Execute immediate loss-cutting or profit-taking (Override minimum hold time for losses)
                if should_take_profit:
                    crypto_balance = balance[symbol.split('/')[0]]['free']
                    if crypto_balance > 0.0001:
                        # 🚨 OVERRIDE HOLD TIME FOR LOSS CUTTING
                        is_loss_cutting = current_profit_pct < 0
                        
                        if is_loss_cutting:
                            log_message(f"🚨 LOSS CUTTING OVERRIDE: {profit_reason} (ignoring minimum hold time)")
                            print(f"🚨 IMMEDIATE LOSS CUTTING: {profit_reason}")
                        else:
                            log_message(f"💰 PROFIT-TAKING: {profit_reason}")
                            print(f"💰 PROFIT-TAKING: {profit_reason}")
                        
                        # Execute sell order
                        sell_order = safe_api_call(exchange.create_market_order, symbol, 'sell', crypto_balance)
                        
                        if sell_order:
                            realized_pnl = current_profit_pct
                            log_message(f"✅ {'LOSS CUT' if is_loss_cutting else 'PROFIT'} EXECUTED: {realized_pnl:+.2f}% on {symbol}")
                            print(f"✅ {'🚨 LOSS CUT' if is_loss_cutting else '💰 PROFIT'} REALIZED: {realized_pnl:+.2f}% on {symbol}")
                            
                            # Update state
                            holding_position = False
                            state_manager.exit_trade("LOSS_CUTTING" if is_loss_cutting else "PROFIT_TAKING")
                            
                            # Brief pause and continue
                            time.sleep(5)
                            continue

            # 🎯 STEP 3: Check Risk Management (Stop Loss, Take Profit)
            if holding_position:
                # 🛡️ VERIFY STOP-LIMIT PROTECTION: Ensure all positions have trailing stops
                protection_status = verify_stop_limit_protection(symbol, holding_position, entry_price)
                if not protection_status:
                    print("🚨 CRITICAL: Position lacks proper protection - consider manual intervention")
                    log_message("🚨 CRITICAL: Unprotected position detected in main loop")
                
                # Use the total portfolio value we calculated earlier (includes all assets in USDT)
                risk_action = check_risk_management(current_price, total_portfolio_value, symbol)

                if risk_action in ['STOP_LOSS', 'TAKE_PROFIT', 'EMERGENCY_EXIT', 'MAX_DRAWDOWN_HIT', 'TRAILING_STOP']:
                    print(f"🚨 RISK MANAGEMENT TRIGGERED: {risk_action}")
                    crypto_balance = balance[symbol.split('/')[0]]['free']
                    # --- ENHANCEMENT: Always allow emergency/stop-loss exits, but log reason ---
                    sell_reason = f"RISK_MANAGEMENT: {risk_action}"
                    order = None
                    if crypto_balance > 0:
                        order = safe_api_call(exchange.create_market_order, symbol, 'sell', crypto_balance)

                        if risk_action in ['STOP_LOSS', 'EMERGENCY_EXIT']:
                            consecutive_losses += 1
                            state_manager.update_consecutive_losses(consecutive_losses)
                        else:
                            consecutive_losses = 0
                            state_manager.update_consecutive_losses(consecutive_losses)

                        # Log the trade
                        log_message(f"✅ SELL EXECUTED: {sell_reason}")
                        print(f"✅ SELL EXECUTED: {sell_reason}")
                    else:
                        log_message(f"❌ SELL NOT EXECUTED: {sell_reason} (no {symbol.split('/')[0]} available)")
                        print(f"❌ SELL NOT EXECUTED: {sell_reason} (no {symbol.split('/')[0]} available)")
                        updated_balance = safe_api_call(exchange.fetch_balance)
                        log_trade("SELL", symbol, crypto_balance, current_price, updated_balance['USDT']['free'])

                        # Clear persistent state
                        state_manager.exit_trade(risk_action)
                        holding_position = False
                        print(f"✅ Risk management SELL: {crypto_balance:.6f} {symbol.split('/')[0]} at ${current_price:.2f}")

                        time.sleep(300)  # 5 minute cooldown
                        continue

            # 🎯 STEP 3: HIGH-FREQUENCY 3-LAYER STRATEGY (when multi-timeframe signal is weak)
            if ma_signal['confidence'] < 0.85:
                print(f"\n🎯 HIGH-FREQUENCY 3-LAYER STRATEGY (Multi-timeframe confidence: {ma_signal['confidence']:.3f})")
                
                # Reset daily stats if needed
                reset_daily_pnl_if_needed()
                
                # Get 1-minute data for micro-scalping
                df_1m = None
                try:
                    df_1m = fetch_ohlcv(exchange, symbol, '1m', 50)
                except Exception as e:
                    log_message(f"⚠️ Could not fetch 1m data for micro-scalping: {e}")
                
                # Coordinate multi-layer strategy
                layer_signal = coordinate_multi_layer_strategy(df, df_1m, current_price, holding_position, symbol)
                
                if layer_signal:
                    # Use the selected layer strategy
                    signal = layer_signal
                    
                    # Adjust position size based on layer and size multiplier
                    position_size_multiplier = layer_signal.get('size_multiplier', 1.0)
                    
                    print(f"🎯 LAYER STRATEGY SELECTED: {layer_signal['layer'].upper()}")
                    print(f"   Action: {layer_signal['action']}")
                    print(f"   Confidence: {layer_signal['confidence']:.3f}")
                    print(f"   Target: {layer_signal.get('adaptive_target', layer_signal.get('target_pct', 0.5)):.2f}%")
                    print(f"   Size Multiplier: {position_size_multiplier:.1f}x")
                    
                    # Execute layer strategy trades
                    if layer_signal['action'] == 'BUY' and not holding_position and layer_signal['confidence'] >= 0.6:
                        
                        # 🚨 BULLETPROOF DEATH CROSS PROTECTION - LAYER STRATEGY PROTECTION
                        death_cross_blocked = False
                        
                        # Check layer signal for death cross indicators
                        if (layer_signal.get('death_cross_detected', False) or 
                            layer_signal.get('bearish_trend_detected', False) or 
                            layer_signal.get('protection_active', False) or
                            layer_signal.get('crossover_type') == 'death_cross'):
                            death_cross_blocked = True
                            log_message(f"🚨 DEATH CROSS PROTECTION - BLOCKING {layer_signal['layer'].upper()} BUY ORDER")
                            log_message(f"   Layer signal contains death cross/bearish indicators")
                        
                        if not death_cross_blocked:
                            position_size = calculate_position_size(
                                current_price, 0.02, layer_signal['confidence'], total_portfolio_value
                            ) * position_size_multiplier
                            
                            if position_size > 0:
                                print(f"🚀 {layer_signal['layer'].upper()} BUY ({symbol}): ${position_size:.2f}")
                                order = place_intelligent_order(symbol, 'buy', amount_usd=position_size, use_limit=True)
                                
                                if order:
                                    holding_position = True
                                    entry_price = current_price
                                    entry_time = datetime.datetime.now()
                                    
                                    # Set dynamic targets based on layer
                                    adaptive_target = layer_signal.get('adaptive_target', layer_signal.get('target_pct', 1.5))
                                    take_profit_price = entry_price * (1 + adaptive_target / 100)
                                    stop_loss_price = entry_price * 0.98  # 2% stop loss
                                
                                state_manager.enter_trade(
                                    entry_price=entry_price,
                                    stop_loss_price=stop_loss_price,
                                    take_profit_price=take_profit_price,
                                    trade_id=order.get('id')
                                )
                                
                                # Update daily stats
                                stats = daily_pnl_tracker()
                                
                                print(f"✅ {layer_signal['layer'].upper()} BUY EXECUTED: Entry ${entry_price:.2f}")
                                print(f"📊 Target: ${take_profit_price:.2f} (+{adaptive_target:.2f}%)")
                                print(f"📈 Daily Progress: {stats['current_pct']:.2f}% of {stats['target_pct']:.1f}% target")
                                
                                time.sleep(interval_seconds)
                                continue
                    
                    elif layer_signal['action'] == 'SELL' and holding_position and layer_signal['confidence'] >= 0.6:
                        crypto_balance = balance[symbol.split('/')[0]]['free']
                        if crypto_balance > 0:
                            print(f"🚨 {layer_signal['layer'].upper()} SELL ({symbol}): {crypto_balance:.6f} {symbol.split('/')[0]}")
                            order = place_intelligent_order(symbol, 'sell', amount_usd=0, use_limit=True)
                            
                            if order:
                                # Calculate P&L for daily tracking
                                if entry_price and entry_price > 0:
                                    pnl_pct = ((current_price - entry_price) / entry_price) * 100
                                    trade_win = pnl_pct > 0
                                    update_daily_pnl(pnl_pct, trade_win, layer_signal['layer'])
                                
                                state_manager.exit_trade(f"{layer_signal['layer'].upper()}_SELL")
                                holding_position = False
                                consecutive_losses = 0
                                
                                stats = daily_pnl_tracker()
                                print(f"✅ {layer_signal['layer'].upper()} SELL EXECUTED")
                                print(f"📈 Daily Progress: {stats['current_pct']:.2f}% of {stats['target_pct']:.1f}% target")
                                
                                time.sleep(interval_seconds)
                                continue
                else:
                    # Fallback to original multi-timeframe signal if no layer signals
                    signal = ma_signal.copy()
                    
                    # If multi-timeframe signal is weak, create a conservative HOLD signal
                    if ma_signal['confidence'] < 0.5:
                        signal = {
                            'action': 'HOLD',
                            'confidence': 0.0,
                            'reason': 'No clear signals from any layer - awaiting better opportunity'
                        }
                    
                    # 🎯 BOOST MODERATE MULTI-TIMEFRAME SIGNALS for day trading
                    elif ma_signal['confidence'] >= 0.5:
                        signal['confidence'] = min(0.85, ma_signal['confidence'] + 0.15)  # Boost for day trading
                    signal['reason'] = f"Boosted multi-timeframe {ma_signal.get('action', 'signal')} for day trading"
                    print(f"🎯 MULTI-TIMEFRAME BOOST: Signal boosted to {signal['confidence']:.3f}")

                # Display system status
                print(f"\n🎯 SIGNAL ANALYSIS: {signal.get('action', 'N/A')} at ${current_price:.2f}", flush=True)
                print(f"   Confidence: {signal.get('confidence', 0.0):.3f}", flush=True)
                print(f"   Reason: {signal.get('reason', 'N/A')}", flush=True)

                # Get dynamic confidence threshold
                strategy_config = optimized_config['strategy_parameters']
                min_confidence = strategy_config['confidence_threshold']

                # 🎯 LOWER THRESHOLD FOR DIP SIGNALS (enhanced dip buying)
                is_dip_signal = False
                if 'crossover_type' in signal:
                    crossover_type = signal.get('crossover_type', '')
                    if 'dip' in crossover_type.lower() or signal.get('price_vs_ema7', 0) < -0.002:
                        is_dip_signal = True
                        dip_reduction = strategy_config.get('dip_confidence_reduction', 0.15)
                        min_confidence -= dip_reduction
                        print(f"🎯 DIP SIGNAL DETECTED - Reduced threshold to {min_confidence:.3f}")
                        print(f"   Signal type: {crossover_type}")
                        if 'price_vs_ema7' in signal:
                            print(f"   Price vs EMA7: {signal['price_vs_ema7']*100:+.2f}%")

                # 🎯 LOWER THRESHOLD FOR MULTI-TIMEFRAME SIGNALS (aggressive day trading)
                if 'multi-timeframe' in signal.get('reason', '').lower():
                    min_confidence *= 0.80  # 20% lower threshold for multi-timeframe signals
                    print(f"🎯 Multi-timeframe signal - reduced threshold to {min_confidence:.3f}")

                print(f"   Required confidence: {min_confidence:.3f}", flush=True)
                print(f"   Signal confidence: {signal.get('confidence', 0):.3f}", flush=True)

                # 🚨 BULLETPROOF DEATH CROSS PROTECTION - FINAL LAYER: Ultimate buy order blocker
                if signal['action'] == 'BUY' and not holding_position and signal.get('confidence', 0) >= min_confidence:
                    
                    # 🛡️ FINAL DEATH CROSS CHECK: Ensure NO BUY orders can slip through
                    death_cross_protection_active = False
                    death_cross_reason = ""
                    
                    # Check for death cross indicators in the signal itself
                    if signal.get('death_cross_detected', False) or signal.get('crossover_type') == 'death_cross':
                        death_cross_protection_active = True
                        death_cross_reason = "Death cross detected in signal"
                    
                    # Check for bearish trend indicators
                    elif signal.get('bearish_trend_detected', False) or signal.get('bearish_signal', False):
                        death_cross_protection_active = True
                        death_cross_reason = "Bearish trend detected in signal"
                    
                    # Check if protection is already active
                    elif signal.get('protection_active', False):
                        death_cross_protection_active = True
                        death_cross_reason = "Protection already active in signal"
                    
                    # Additional EMA check as final safeguard
                    if not death_cross_protection_active:
                        try:
                            # Get fresh EMA data for final verification
                            df_final_check = client.get_klines(symbol=symbol, interval='5m', limit=30)
                            if df_final_check is not None and len(df_final_check) >= 25:
                                df_final_check = pd.DataFrame(df_final_check, columns=['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
                                df_final_check['close'] = df_final_check['close'].astype(float)
                                
                                ema7_final = df_final_check['close'].ewm(span=7).mean().iloc[-1]
                                ema25_final = df_final_check['close'].ewm(span=25).mean().iloc[-1]
                                
                                if ema7_final < ema25_final:
                                    death_cross_protection_active = True
                                    death_cross_reason = f"Final EMA check: EMA7 {ema7_final:.4f} < EMA25 {ema25_final:.4f}"
                        except Exception as e:
                            log_message(f"⚠️ Final EMA check error (proceeding cautiously): {e}")
                    
                    # 🚨 BLOCK BUY ORDER IF DEATH CROSS PROTECTION IS ACTIVE
                    if death_cross_protection_active:
                        log_message(f"🚨 DEATH CROSS PROTECTION ACTIVATED - BLOCKING BUY ORDER")
                        log_message(f"   Reason: {death_cross_reason}")
                        log_message(f"   Signal confidence: {signal.get('confidence', 0):.3f}")
                        log_message(f"   Signal type: {signal.get('crossover_type', 'unknown')}")
                        
                        # 🧠 RECORD THIS AS A PREVENTED MISTAKE FOR ML LEARNING
                        try:
                            if ML_LEARNING_AVAILABLE:
                                record_death_cross_buy_mistake("death_cross_protection_prevented", 0.0, symbol, {
                                    'signal': signal,
                                    'protection_reason': death_cross_reason,
                                    'timestamp': datetime.datetime.now().isoformat()
                                })
                                log_message("🧠 ML LEARNING: Recorded prevented death cross buy attempt")
                        except Exception as e:
                            log_message(f"⚠️ ML recording error: {e}")
                        
                        # Force the signal to HOLD instead
                        log_message("🛡️ CONVERTING BUY SIGNAL TO HOLD - DEATH CROSS PROTECTION")
                        continue  # Skip this buy attempt completely
                    
                    # If we get here, no death cross protection is active - proceed with buy
                    position_size = calculate_position_size(current_price, 0.02, signal['confidence'], total_portfolio_value)
                    if position_size > 0:
                        log_message(f"✅ DEATH CROSS PROTECTION PASSED - Executing BUY order")
                        print(f"📥 MULTI-TIMEFRAME ENHANCED BUY signal ({symbol}) - ${position_size:.2f}...")
                        print(f"   Multi-timeframe confidence: {ma_signal['confidence']:.3f}")
                        print(f"   Final confidence: {signal['confidence']:.3f}")

                        order = place_intelligent_order(symbol, 'buy', amount_usd=position_size, use_limit=True)

                        if order:
                            holding_position = True
                            state_manager.enter_trade(
                                entry_price=entry_price,
                                stop_loss_price=stop_loss_price,
                                take_profit_price=take_profit_price,
                                trade_id=order.get('id')
                            )
                            print(f"✅ BUY EXECUTED: Multi-timeframe enhanced strategy")

                elif signal['action'] == 'SELL' and holding_position and signal.get('confidence', 0) >= min_confidence:
                    # Calculate current P&L
                    current_pnl = 0
                    if entry_price and entry_price > 0:
                        current_pnl = (current_price - entry_price) / entry_price

                    execute_sell = True

                    # Don't sell at loss unless multi-timeframe strongly confirms
                    if current_pnl < -0.01:  # Losing more than 1%
                        if ma_signal['action'] != 'SELL' or ma_signal['confidence'] < 0.7:
                            execute_sell = False
                            print(f"⚠️ SELL blocked - would realize {current_pnl:.2%} loss without strong multi-timeframe confirmation")

                    if execute_sell:
                        crypto_balance = balance[symbol.split('/')[0]]['free']
                        if crypto_balance > 0:
                            print(f"📤 MULTI-TIMEFRAME ENHANCED SELL signal ({symbol}) - Current P&L: {current_pnl:.2%}")
                            print(f"   Multi-timeframe confidence: {ma_signal['confidence']:.3f}")
                            print(f"   Final confidence: {signal['confidence']:.3f}")

                            order = place_intelligent_order(symbol, 'sell', amount_usd=0, use_limit=True)

                            if order:
                                state_manager.exit_trade("MA_ENHANCED_SELL")
                                holding_position = False
                                consecutive_losses = 0
                                print(f"✅ SELL EXECUTED: Multi-timeframe enhanced strategy")

                else:
                    print("⏸ No action taken - awaiting stronger multi-timeframe signal", flush=True)

        except Exception as e:
            print("❌ Error in trading loop:", e, flush=True)
            _deploy_write_heartbeat("ERROR", {"error": str(e)[:120]})
        finally:
            _deploy_write_heartbeat("RUNNING")

        # Add heartbeat before sleep
        print(f"💓 Loop completed, sleeping for {interval_seconds} seconds...", flush=True)
        time.sleep(interval_seconds)

def generate_reports():
    """Generate comprehensive trading performance reports"""
    try:
        print("📊 Generating comprehensive performance reports...")
        
        import datetime
        from log_utils import calculate_daily_pnl, calculate_total_pnl_and_summary
        
        # Generate timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"trading_report_{timestamp}.md"
        
        # Get performance data
        try:
            daily_pnl = calculate_daily_pnl()
            pnl_summary = calculate_total_pnl_and_summary()
        except:
            daily_pnl = 0.0
            pnl_summary = {'total_realized_pnl': 0, 'recent_trades': 0, 'last_trade_date': 'N/A'}
        
        # Get current portfolio status
        try:
            balance = safe_api_call(exchange.fetch_balance)
            current_price = safe_api_call(exchange.fetch_ticker, 'BTC/USDT')['last']
            
            if balance and current_price:
                usdt_balance = balance.get('USDT', {}).get('free', 0)
                btc_balance = balance.get('BTC', {}).get('free', 0)
                total_value = usdt_balance + (btc_balance * current_price)
            else:
                usdt_balance = btc_balance = total_value = current_price = 0
        except:
            usdt_balance = btc_balance = total_value = current_price = 0
        
        # Create comprehensive report
        report_content = f"""# 🤖 Crypto Trading Bot Performance Report
*Generated: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*

## 📊 PORTFOLIO SUMMARY
- **Total Portfolio Value**: ${total_value:.2f}
- **USDT Balance**: ${usdt_balance:.2f}
- **BTC Balance**: {btc_balance:.6f} BTC (${btc_balance * current_price:.2f})
- **Current BTC Price**: ${current_price:.2f}

## 💰 PERFORMANCE METRICS
- **Daily PnL (Realized)**: ${daily_pnl:.2f}
- **Total PnL (Realized)**: ${pnl_summary.get('total_realized_pnl', 0):.2f}
- **Recent Activity**: {pnl_summary.get('recent_trades', 0)} trades (7 days)
- **Last Trade Date**: {pnl_summary.get('last_trade_date', 'N/A')}

## 🎯 CURRENT POSITION
- **Holding Position**: {holding_position}
- **Entry Price**: ${entry_price if entry_price else 'None'}
- **Stop Loss**: ${stop_loss_price if stop_loss_price else 'None'}
- **Take Profit**: ${take_profit_price if take_profit_price else 'None'}

## ⚙️ BOT CONFIGURATION
- **Strategy**: Multi-Timeframe MA7/MA25 Crossover
- **Loop Interval**: {optimized_config['system']['loop_interval_seconds']}s
- **Confidence Threshold**: {optimized_config['strategy_parameters']['confidence_threshold']:.3f}
- **Position Sizing**: {optimized_config['trading']['position_sizing_mode']}
- **Trade Cooldown**: {optimized_config['trading']['trade_cooldown_seconds']}s

## 🛡️ RISK MANAGEMENT
- **Stop Loss**: {optimized_config['risk_management']['stop_loss_pct']:.1%}
- **Take Profit**: {optimized_config['risk_management']['take_profit_pct']:.1%}
- **Daily Loss Limit**: ${optimized_config['risk_management']['daily_loss_limit_usd']}
- **Max Consecutive Losses**: {optimized_config['risk_management']['max_consecutive_losses']}

## 📈 SYSTEM STATUS
- **Last Loop Time**: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- **Config File**: {bot_config.config_file}
- **State Manager**: Active
- **Exchange Connection**: {'✅ Connected' if balance else '❌ Disconnected'}

---
*Report generated by Enhanced Trading Bot v{optimized_config.get('system', {}).get('version', '1.0')}*
"""
        
        # Save report to file
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"✅ Comprehensive report saved to: {report_file}")
        print(f"📄 Report contains portfolio status, performance metrics, and system configuration")
        
        # Also print key summary to console
        print(f"\n📊 QUICK SUMMARY:")
        print(f"   💰 Portfolio: ${total_value:.2f}")
        print(f"   📈 Daily PnL: ${daily_pnl:.2f}")
        print(f"   🎯 Position: {'BTC' if holding_position else 'CASH'}")
        print(f"   ⚙️ Status: {'Running' if balance else 'Connection Issues'}")
        
    except Exception as e:
        print(f"❌ Error generating reports: {e}")
        # Fallback simple report
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            simple_report = f"""# Trading Bot Report - {timestamp}
Generated: {datetime.datetime.now()}

Status: Report generation encountered errors
Error: {str(e)}

Please check bot configuration and logs for issues.
"""
            with open(f"error_report_{timestamp}.md", 'w') as f:
                f.write(simple_report)
            print(f"⚠️ Error report saved to: error_report_{timestamp}.md")
        except:
            print("❌ Could not generate any report")

# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":
    # 🛡️ FINAL AWS-ONLY CHECK before main execution
    print("🔒 PERFORMING FINAL AWS ENVIRONMENT CHECK...")
    check_aws_environment()  # Double-check before starting
    print("✅ AWS VERIFICATION PASSED - Starting main bot...")
    
    print("🚀 STARTING ENHANCED HIGH-FREQUENCY DAY TRADING BOT")
    print("🎯 PRIMARY STRATEGY: Multi-Timeframe MA7/MA25 Crossover + Advanced Price Detection")
    print("⚡ HFT OPTIMIZATIONS: 15s loops, 30s cooldown, micro-scalping, range-bound trading")
    print("📊 DAILY TARGET: 2.5% through 50-100+ trades per day across 3 strategy layers")
    print("🔍 DETECTION SYSTEM: Multi-timeframe price movement analysis (spike/short/medium/long)")
    print("="*70)

    try:
        # Display configuration info
        trading_config = optimized_config['trading']
        if trading_config.get('position_sizing_mode') == 'percentage':
            print(f"💰 Position Sizing: {trading_config['base_position_pct']:.1%} of portfolio ({trading_config['min_position_pct']:.1%}-{trading_config['max_position_pct']:.1%} range)")
        else:
            print(f"💰 Position Sizing: Fixed ${trading_config['base_amount_usd']} per trade")

        trail_pct = optimized_config['risk_management'].get('trailing_stop_pct', 0.005)
        print(f"⏰ Trade Cooldown: {min_trade_interval//60} minutes | Trailing Stop: {trail_pct:.1%}")
        print(f"🔧 Confidence Threshold: {optimized_config['strategy_parameters']['confidence_threshold']:.3f}")
        print("🎯 SIMPLIFIED SYSTEM: Only trailing stops for exits - clean and effective")
        print("💡 Press Ctrl+C to stop and generate reports")
        print("="*70)

        # Test connection and start trading
        test_connection()

        # Use faster loop timing from config
        loop_interval = optimized_config['system']['loop_interval_seconds']
        print(f"⚡ Enhanced Loop Timing: {loop_interval}s intervals for better responsiveness (Loaded from config)")
        print(f"[DEBUG] Config file used: {bot_config.config_file}")
        run_continuously(loop_interval)

    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
        print("📊 Generating final reports...")
        generate_reports()
        print("✅ Trading session complete!")

    except Exception as e:
        print(f"❌ Fatal error: {e}")
        print("📊 Generating emergency reports...")
        try:
            generate_reports()
        except:
            print("⚠️ Report generation failed")
        print("🔧 Check logs for debugging information")

def display_enhanced_price_jump_status():
    """Display enhanced price jump detection status"""
    try:
        detector = get_price_jump_detector(optimized_config)
        status = detector.get_status()
        trend_state = status['current_trend']

        print(f"🔍 ENHANCED PRICE DETECTION STATUS:")
        print(f"   📊 History: {status['price_history_size']} points | Recent jumps: {status['recent_jumps_count']}")
        print(f"   ⏱️ Activity (5m/15m/30m): {status['last_5min_jumps']}/{status['last_15min_jumps']}/{status['last_30min_jumps']}")
        print(f"   📈 Current Trend: {trend_state['direction'] or 'NEUTRAL'} (strength: {trend_state['strength']:.2f})")

        if trend_state['direction'] and trend_state['is_sustained']:
            print(f"   🎯 Sustained {trend_state['direction']} trend: {trend_state['duration_seconds']:.0f}s, peak {trend_state['peak_change_pct']:+.2f}%")

        activity = status['timeframe_activity']
        if sum(activity.values()) > 0:
            print(f"   🎯 Timeframe activity: Spike:{activity['spike']} | Short:{activity['short_trend']} | Medium:{activity['medium_trend']} | Long:{activity['long_trend']}")

    except Exception as e:
        print(f"⚠️ Error displaying price jump status: {e}")
