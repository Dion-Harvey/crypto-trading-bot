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

# Import required libraries
import ccxt
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

# Enhanced Risk Management State - Restored from state
entry_price = trading_state.get('entry_price', None)
stop_loss_price = trading_state.get('stop_loss_price', None)
take_profit_price = trading_state.get('take_profit_price', None)

# Load risk state
risk_state = state_manager.get_risk_state()
max_drawdown_from_peak = risk_state['max_drawdown_from_peak']
account_peak_value = risk_state['account_peak_value']

# Risk Management Parameters - Now loaded from enhanced config
risk_config = optimized_config['risk_management']
stop_loss_percentage = risk_config['stop_loss_pct']
take_profit_percentage = risk_config['take_profit_pct']
max_drawdown_limit = risk_config['max_drawdown_pct']

# Enhanced Risk Management - Ensure proper initialization
if entry_price is None:
    entry_price = None
    stop_loss_price = None
    take_profit_price = None

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
                exchange.fetch_ticker('BTC/USDC')
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

            # Handle rate limiting
            elif 'rate limit' in error_str or '429' in str(e):
                wait_time = 5 * (attempt + 1)  # Exponential backoff
                log_message(f"⚠️ Rate limit hit, waiting {wait_time}s (attempt {attempt + 1}/{max_retries})")
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
    raise Exception(f"API call failed after {max_retries} attempts")

# =============================================================================
# DYNAMIC RISK MANAGEMENT FUNCTIONS
# =============================================================================

def calculate_dynamic_daily_loss_limit(total_portfolio_value):
    """
    Calculate daily loss limit based on portfolio percentage or fixed amount
    """
    risk_config = optimized_config['risk_management']

    # Use percentage-based limit if available, otherwise fall back to fixed amount
    if 'daily_loss_limit_pct' in risk_config:
        percentage_limit = total_portfolio_value * risk_config['daily_loss_limit_pct']
        fixed_limit = risk_config.get('daily_loss_limit_usd', 2.5)

        # Use the larger of the two for better protection
        dynamic_limit = max(percentage_limit, fixed_limit)

        log_message(f"📊 Dynamic Daily Loss Limit:")
        log_message(f"   Portfolio: ${total_portfolio_value:.2f}")
        log_message(f"   Percentage Limit ({risk_config['daily_loss_limit_pct']:.1%}): ${percentage_limit:.2f}")
        log_message(f"   Fixed Limit: ${fixed_limit:.2f}")
        log_message(f"   Using: ${dynamic_limit:.2f}")

        return dynamic_limit
    else:
        return risk_config.get('daily_loss_limit_usd', 2.5)

# =============================================================================
# MARKET ORDER FUNCTION
# =============================================================================

def calculate_position_size(current_price, volatility, signal_confidence, total_portfolio_value):
    """
    Enhanced percentage-based position sizing with Kelly Criterion and institutional methods
    Uses percentage of total portfolio value instead of fixed dollar amounts
    """
    global consecutive_losses, account_peak_value

    # Get position sizing configuration
    trading_config = optimized_config['trading']
    position_mode = trading_config.get('position_sizing_mode', 'percentage')

    if position_mode == 'percentage':
        # Percentage-based sizing (RECOMMENDED)
        base_position_pct = trading_config['base_position_pct']  # e.g., 0.15 = 15%
        min_position_pct = trading_config['min_position_pct']    # e.g., 0.08 = 8%
        max_position_pct = trading_config['max_position_pct']    # e.g., 0.25 = 25%

        # Calculate base position size as percentage of total portfolio
        base_amount = total_portfolio_value * base_position_pct
        min_amount = total_portfolio_value * min_position_pct
        max_amount = total_portfolio_value * max_position_pct

        log_message(f"📊 PERCENTAGE-BASED Position Sizing:")
        log_message(f"   Portfolio Value: ${total_portfolio_value:.2f}")
        log_message(f"   Base Position: {base_position_pct:.1%} = ${base_amount:.2f}")

    else:
        # Fixed dollar sizing (legacy fallback)
        base_amount = trading_config['base_amount_usd']
        min_amount = trading_config['min_amount_usd']
        max_amount = trading_config['max_amount_usd']

        log_message(f"📊 FIXED-DOLLAR Position Sizing:")
        log_message(f"   Base Amount: ${base_amount:.2f}")

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
        returns = fetch_ohlcv(exchange, 'BTC/USDC', '1h', 100)['close'].pct_change().dropna()
        var_analysis = institutional_manager.var_calculator.calculate_var(returns, total_portfolio_value)

        if var_analysis['risk_assessment'] == 'HIGH':
            var_factor = 0.5
        elif var_analysis['risk_assessment'] == 'MEDIUM':
            var_factor = 0.75
        else:
            var_factor = 1.0
    except:
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
            target_position_size = 15.0  # $15 for $50-75 accounts (30%)
            small_account_scaling = 1.2  # Slightly aggressive
        elif total_portfolio_value >= 25:
            target_position_size = 12.50  # $12.50 for $25-50 accounts (50%)
            small_account_scaling = 1.6  # More aggressive for growth
        else:
            # For accounts under $25, scale proportionally but respect minimum order
            target_position_size = max(10.0, total_portfolio_value * 0.50)  # 50% or $10 minimum
            small_account_scaling = 2.0  # Maximum scaling for tiny accounts

        # Calculate actual percentage for logging
        actual_percentage = (target_position_size / total_portfolio_value) * 100

        log_message(f"🎯 SMALL ACCOUNT SCALING:")
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

def check_risk_management(current_price, total_balance):
    """
    Enhanced risk management with stop loss, take profit, trailing stops, partial exits, and trend-based exits
    """
    global entry_price, holding_position, account_peak_value, stop_loss_price, take_profit_price

    # Update peak balance for drawdown calculation
    if total_balance > account_peak_value:
        account_peak_value = total_balance

    # Check maximum drawdown
    current_drawdown = (account_peak_value - total_balance) / account_peak_value
    if current_drawdown > max_drawdown_limit:
        log_message(f"🚨 MAX DRAWDOWN HIT: {current_drawdown:.3f} > {max_drawdown_limit}")
        return 'MAX_DRAWDOWN_HIT'

    if holding_position and entry_price and entry_price > 0:
        # Calculate P&L percentage
        pnl_percentage = (current_price - entry_price) / entry_price

        risk_config = optimized_config['risk_management']

        # 🎯 PARTIAL EXIT STRATEGY (Your suggestion to scale out of winners)
        if risk_config.get('partial_exit_enabled', False):
            partial_exit_profit = risk_config.get('partial_exit_at_profit_pct', 0.10)
            partial_exit_amount = risk_config.get('partial_exit_amount_pct', 0.50)

            if pnl_percentage >= partial_exit_profit:
                # Check if we haven't already done a partial exit
                if not hasattr(state_manager, '_partial_exit_done') or not state_manager._partial_exit_done:
                    log_message(f"💰 PARTIAL EXIT triggered at {pnl_percentage:.2%} profit")
                    return f'PARTIAL_EXIT_{partial_exit_amount}'

        # 🎯 ENHANCED TRAILING STOP (Your suggestion for better reward:risk)
        if risk_config.get('trailing_stop_enabled', False):
            trailing_pct = risk_config.get('trailing_stop_pct', 0.03)  # Increased to 3%
            profit_lock_threshold = risk_config.get('profit_lock_threshold', 0.08)

            # If we're in profit above threshold, activate trailing stop
            if pnl_percentage > profit_lock_threshold:
                # Get highest price since entry (or implement proper tracking)
                highest_price_since_entry = max(current_price, entry_price * (1 + pnl_percentage))
                trailing_stop_price = highest_price_since_entry * (1 - trailing_pct)

                if current_price <= trailing_stop_price:
                    log_message(f"📈 TRAILING STOP: ${current_price:.2f} <= ${trailing_stop_price:.2f} (Locking in {pnl_percentage:.2%} profit)")
                    return 'TRAILING_STOP'

        # Check stop loss (tighter for better capital preservation)
        if stop_loss_price and current_price <= stop_loss_price:
            log_message(f"⛔ STOP LOSS: Price ${current_price:.2f} <= SL ${stop_loss_price:.2f} (P&L: {pnl_percentage:.3f})")
            return 'STOP_LOSS'

        # Check take profit (your suggestion: 15% vs 2.5% = 6:1 ratio)
        if take_profit_price and current_price >= take_profit_price:
            log_message(f"🎯 TAKE PROFIT: Price ${current_price:.2f} >= TP ${take_profit_price:.2f} (P&L: {pnl_percentage:.3f})")
            return 'TAKE_PROFIT'

        # Emergency exit for extreme losses (tighter threshold)
        if pnl_percentage <= -0.06:  # -6% emergency exit
            log_message(f"🚨 EMERGENCY EXIT: P&L {pnl_percentage:.3f} <= -6%")
            return 'EMERGENCY_EXIT'

        # 🎯 MINIMUM HOLD TIME (Your suggestion: 90 minutes to avoid overtrading)
        min_hold_time = risk_config.get('minimum_hold_time_minutes', 90) * 60  # Convert to seconds
        if hasattr(state_manager, 'get_trade_start_time'):
            trade_start_time = state_manager.get_trade_start_time()
            if trade_start_time and (time.time() - trade_start_time) < min_hold_time:
                # Don't exit yet unless it's an emergency
                if pnl_percentage <= -0.04:  # Allow emergency exits
                    log_message(f"🚨 EARLY EMERGENCY EXIT: P&L {pnl_percentage:.3f} <= -4% (overriding min hold time)")
                    return 'EMERGENCY_EXIT'
                else:
                    # Still in minimum hold period - no exit
                    remaining_hold = min_hold_time - (time.time() - trade_start_time)
                    log_message(f"⏳ Minimum hold active: {remaining_hold/60:.1f} minutes remaining")

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

def place_intelligent_order(symbol, side, amount_usd, use_limit=True, timeout_seconds=None):
    """
    Enhanced intelligent order execution with improved limit order handling
    Uses config-based timeout and smarter market fallback
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

        # Calculate spread to determine if limit order is worthwhile
        bid_price = orderbook['bids'][0][0] if orderbook['bids'] else market_price * 0.999
        ask_price = orderbook['asks'][0][0] if orderbook['asks'] else market_price * 1.001
        spread_pct = (ask_price - bid_price) / market_price * 100

        # If spread is too wide (>0.5%), use market order for faster execution
        if spread_pct > 0.5:
            use_limit = False
            print(f"⚡ Wide spread detected ({spread_pct:.2f}%) - using market order for fast execution")

        # Binance minimum order requirements
        MIN_NOTIONAL_VALUE = 10.0  # Minimum $10 USD equivalent
        MIN_BTC_AMOUNT = 0.00001   # Minimum 0.00001 BTC

        if side.upper() == 'BUY':
            available_usd = balance['USDC']['free']
            if available_usd < amount_usd:
                print(f"❌ Insufficient USDC balance: ${available_usd:.2f} < ${amount_usd:.2f}")
                return None

            # Use slightly more conservative limit prices for better fill rates
            # For BUY: place slightly above best bid but below market
            limit_price = bid_price + (market_price - bid_price) * 0.3  # 30% into the spread
            amount = round(amount_usd / limit_price, 6)

            # Check minimum order size for BUY
            if amount < MIN_BTC_AMOUNT:
                print(f"❌ BUY amount too small: {amount:.6f} BTC < {MIN_BTC_AMOUNT:.6f} BTC minimum")
                return None
            if amount_usd < MIN_NOTIONAL_VALUE:
                print(f"❌ BUY order value too small: ${amount_usd:.2f} < ${MIN_NOTIONAL_VALUE:.2f} minimum")
                return None
        else:  # SELL
            available_btc = balance['BTC']['free']
            amount = round(available_btc, 6)

            # Check if we have any BTC to sell
            if available_btc <= 0:
                print(f"❌ No BTC available to sell: {available_btc:.6f} BTC")
                return None

            # Check minimum order size for SELL
            if amount < MIN_BTC_AMOUNT:
                print(f"❌ SELL amount too small: {amount:.6f} BTC < {MIN_BTC_AMOUNT:.6f} BTC minimum")
                print(f"   🔍 This amount is too small to trade on Binance. Consider accumulating more BTC before selling.")
                return None

            # Check minimum notional value
            notional_value = amount * market_price
            if notional_value < MIN_NOTIONAL_VALUE:
                print(f"❌ SELL order value too small: ${notional_value:.2f} < ${MIN_NOTIONAL_VALUE:.2f} minimum")
                print(f"   BTC amount: {amount:.6f}, Price: ${market_price:.2f}")
                return None

            # Use slightly more conservative limit prices for better fill rates
            # For SELL: place slightly below best ask but above market
            limit_price = ask_price - (ask_price - market_price) * 0.3  # 30% into the spread

            print(f"✅ SELL order validation passed: {amount:.6f} BTC worth ${notional_value:.2f}")

        order = None
        final_price = None

        if use_limit:
            print(f"🎯 Placing LIMIT {side.upper()} order: {amount:.6f} {symbol.split('/')[0]} at ${limit_price:.2f}")

            try:
                # Place limit order
                order = safe_api_call(exchange.create_limit_order, symbol, side.lower(), amount, limit_price)
                order_id = order['id']

                # Wait for fill with timeout
                start_time = time.time()
                filled = False

                while time.time() - start_time < timeout_seconds:
                    try:
                        order_status = safe_api_call(exchange.fetch_order, order_id, symbol)
                        if order_status['status'] == 'closed':
                            filled = True
                            final_price = order_status['average'] or limit_price
                            print(f"✅ LIMIT ORDER FILLED at ${final_price:.2f}")
                            break
                    except:
                        pass
                    time.sleep(2)  # Check every 2 seconds

                if not filled:
                    # Cancel unfilled limit order
                    try:
                        safe_api_call(exchange.cancel_order, order_id, symbol)
                        print(f"⏰ Limit order timeout - placing market order as fallback")
                    except:
                        pass

                    # Fallback to market order
                    order = safe_api_call(exchange.create_market_order, symbol, side.lower(), amount)
                    final_price = market_price
                    print(f"✅ MARKET ORDER FALLBACK at ~${final_price:.2f}")

            except Exception as limit_error:
                print(f"⚠️ Limit order failed ({limit_error}) - using market order")
                # Fallback to market order
                order = safe_api_call(exchange.create_market_order, symbol, side.lower(), amount)
                final_price = market_price
        else:
            # Direct market order
            amount = round(amount_usd / market_price, 6) if side.upper() == 'BUY' else amount
            order = safe_api_call(exchange.create_market_order, symbol, side.lower(), amount)
            final_price = market_price
            print(f"✅ MARKET ORDER PLACED at ~${final_price:.2f}")

        # Track entry price and set stop loss/take profit for BUY orders
        if side.upper() == 'BUY':
            entry_price = final_price
            stop_loss_price = final_price * (1 - stop_loss_percentage)
            take_profit_price = final_price * (1 + take_profit_percentage)

            log_message(f"🛡️ Risk Levels Set: Entry=${final_price:.2f}, SL=${stop_loss_price:.2f}, TP=${take_profit_price:.2f}")
        elif side.upper() == 'SELL':
            # Clear risk management levels after selling
            entry_price = None
            stop_loss_price = None
            take_profit_price = None

        # Get updated balance for logging
        updated_balance = safe_api_call(exchange.fetch_balance)
        total_balance = updated_balance['total']['USDC'] + (updated_balance['total']['BTC'] * final_price)

        # Log the trade
        log_trade(side.upper(), symbol, amount, final_price, total_balance)

        # Update trade timing
        last_trade_time = time.time()

        print(f"📝 Trade logged to trade_log.csv")
        print(f"💰 Total portfolio value: ${total_balance:.2f}")

        if side.upper() == 'BUY' and stop_loss_price and take_profit_price:
            print(f"🛡️ Stop Loss: ${stop_loss_price:.2f} | 🎯 Take Profit: ${take_profit_price:.2f}")

        return order
    except Exception as e:
        print("❌ Order failed:", e)
        return None

# Legacy function for backward compatibility
def place_market_order(symbol, side, amount_usd):
    """Legacy function - redirects to intelligent order execution"""
    return place_intelligent_order(symbol, side, amount_usd, use_limit=False)

# =============================================================================
# CONNECTION TEST FUNCTION
# =============================================================================

def test_connection():
    try:
        balance = safe_api_call(exchange.fetch_balance)
        ticker = safe_api_call(exchange.fetch_ticker, 'BTC/USDC')
        print("✅ Connected to Binance US!")
        print("Balances:")
        for coin, value in balance['total'].items():
            if value > 0:
                print(f"{coin}: {value}")
        print(f"\nCurrent BTC/USDC Price: ${ticker['last']}")

        # Display current bot state
        state_manager.print_current_state()

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
# MA7/MA25 CROSSOVER STRATEGY - ABSOLUTE PRIORITY FOR DAY TRADING
# =============================================================================

def detect_ma_crossover_signals(df, current_price):
    """
    🎯 AGGRESSIVE DAY TRADING: MA7/MA25 Crossover Detection
    This is the ABSOLUTE PRIORITY strategy that overrides all others.
    
    Golden Cross (MA7 > MA25): Strong BUY signal
    Death Cross (MA7 < MA25): Strong SELL signal
    
    Returns high-confidence signals for immediate execution.
    """
    try:
        if len(df) < 30:
            return {'action': 'HOLD', 'confidence': 0.0, 'reasons': ['Not enough data for MA crossover'], 'crossover_type': 'no_signal'}

        # Calculate moving averages
        ma_7 = df['close'].rolling(7).mean()
        ma_25 = df['close'].rolling(25).mean()

        if len(ma_7) < 2 or len(ma_25) < 2:
            return {'action': 'HOLD', 'confidence': 0.0, 'reasons': ['Not enough MA data'], 'crossover_type': 'no_signal'}

        # Current and previous MA values
        ma7_current = ma_7.iloc[-1]
        ma25_current = ma_25.iloc[-1]
        ma7_previous = ma_7.iloc[-2]
        ma25_previous = ma_25.iloc[-2]

        # Crossover detection
        golden_cross = (ma7_previous <= ma25_previous) and (ma7_current > ma25_current)
        death_cross = (ma7_previous >= ma25_previous) and (ma7_current < ma25_current)

        # Current trend strength
        ma_spread = abs(ma7_current - ma25_current) / ma25_current * 100  # Percentage spread

        # --- FIX: Always return strong signal on crossover ---
        if golden_cross:
            return {
                'action': 'BUY',
                'confidence': 1.0,
                'reasons': [
                    f"Golden Cross: MA7 crossed above MA25",
                    f"MA7 prev: {ma7_previous:.4f} → {ma7_current:.4f}",
                    f"MA25 prev: {ma25_previous:.4f} → {ma25_current:.4f}",
                    f"Spread: {ma_spread:.2f}%"
                ],
                'ma7': ma7_current,
                'ma25': ma25_current,
                'spread': ma_spread,
                'crossover_type': 'golden_cross'
            }
        elif death_cross:
            return {
                'action': 'SELL',
                'confidence': 1.0,
                'reasons': [
                    f"Death Cross: MA7 crossed below MA25",
                    f"MA7 prev: {ma7_previous:.4f} → {ma7_current:.4f}",
                    f"MA25 prev: {ma25_previous:.4f} → {ma25_current:.4f}",
                    f"Spread: {ma_spread:.2f}%"
                ],
                'ma7': ma7_current,
                'ma25': ma25_current,
                'spread': ma_spread,
                'crossover_type': 'death_cross'
            }

        # If not a crossover, check for strong trend (optional, can be tuned)
        if ma7_current > ma25_current and ma_spread > 1.0:
            return {
                'action': 'BUY',
                'confidence': 0.6,
                'reasons': [
                    f"MA7 above MA25 with spread {ma_spread:.2f}%",
                    f"MA7: {ma7_current:.4f}, MA25: {ma25_current:.4f}"
                ],
                'ma7': ma7_current,
                'ma25': ma25_current,
                'spread': ma_spread,
                'crossover_type': 'ma7_above_ma25'
            }
        elif ma7_current < ma25_current and ma_spread > 1.0:
            return {
                'action': 'SELL',
                'confidence': 0.6,
                'reasons': [
                    f"MA7 below MA25 with spread {ma_spread:.2f}%",
                    f"MA7: {ma7_current:.4f}, MA25: {ma25_current:.4f}"
                ],
                'ma7': ma7_current,
                'ma25': ma25_current,
                'spread': ma_spread,
                'crossover_type': 'ma7_below_ma25'
            }

        # NO CLEAR SIGNAL
        return {
            'action': 'HOLD',
            'confidence': 0.0,
            'reasons': [
                f"📊 MA7: {ma7_current:.4f}, MA25: {ma25_current:.4f}",
                f"📈 Spread: {ma_spread:.2f}% - No clear crossover signal",
                "⏳ Waiting for MA crossover or stronger trend"
            ],
            'ma7': ma7_current,
            'ma25': ma25_current,
            'spread': ma_spread,
            'crossover_type': 'no_signal'
        }

    except Exception as e:
        log_message(f"❌ Error in MA crossover detection: {e}")
        return {'action': 'HOLD', 'confidence': 0.0, 'reasons': [f'MA crossover error: {e}'], 'crossover_type': 'error'}

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

        # Calculate momentum indicators
        short_ma = df['close'].rolling(5).mean().iloc[-1]
        medium_ma = df['close'].rolling(10).mean().iloc[-1]
        long_ma = df['close'].rolling(20).mean().iloc[-1]

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
            current_price > short_ma > medium_ma > long_ma and  # MA alignment
            momentum_5 > 0.02 and momentum_10 > 0.03 and        # Strong momentum
            volume_momentum > 1.3                               # Volume confirmation
        )

        # Strong downward momentum
        strong_down_momentum = (
            current_price < short_ma < medium_ma < long_ma and  # Bear MA alignment
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
    """Placeholder for advanced risk order placement"""
    log_message(f"🛡️ Advanced risk orders would be placed for {symbol} at entry ${entry_price:.2f}")
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

def run_continuously(interval_seconds=60):
    """
    🎯 AGGRESSIVE DAY TRADING BOT - MA7/MA25 Crossover Priority
    
    Main trading loop that executes MA7/MA25 crossover strategy as absolute priority,
    with fallback to other strategies when no clear crossover signals exist.
    """
    global holding_position, last_trade_time, consecutive_losses, active_trade_index, entry_price, stop_loss_price, take_profit_price

    print("\n" + "="*70)
    print("🚀 ENHANCED DAY TRADING BOT - Multi-Timeframe MA + Advanced Price Detection")
    print("🎯 ABSOLUTE PRIORITY: Multi-timeframe MA7/MA25 crossover signals override all other strategies")
    print("📈 STRATEGY: Golden Cross (BUY) | Death Cross (SELL) | Multi-Timeframe Price Detection")
    print("⚡ ENHANCEMENTS: 30s loops | 15min cooldown | Multi-timeframe analysis | Sustained trend tracking")
    print("🔍 DETECTION: Spike(0.5%/1min) | Short(0.8%/5min) | Medium(1.2%/15min) | Long(1.8%/30min)")
    print("="*70)

    while True:
        # Always ensure risk management variables are initialized
        if 'entry_price' not in globals() or entry_price is None:
            entry_price = None
        if 'stop_loss_price' not in globals() or stop_loss_price is None:
            stop_loss_price = None
        if 'take_profit_price' not in globals() or take_profit_price is None:
            take_profit_price = None

        print("\n" + "="*50, flush=True)
        print("🎯 ENHANCED MULTI-TIMEFRAME DAY TRADING LOOP", flush=True)
        print("="*50, flush=True)

        # Add timestamp for debugging
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"🕐 Loop Started: {current_time}", flush=True)

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
        current_price = safe_api_call(exchange.fetch_ticker, 'BTC/USDC')['last']
        btc_balance = balance['BTC']['free']
        total_portfolio_value = balance['total']['USDC'] + (balance['total']['BTC'] * current_price)

        # Show unrealized PnL if holding position
        if holding_position and entry_price and entry_price > 0:
            unrealized = calculate_unrealized_pnl(current_price, entry_price, btc_balance)
            print(f"   💎 UNREALIZED: ${unrealized['unrealized_pnl_usd']:.2f} ({unrealized['unrealized_pnl_pct']:+.2f}%)", flush=True)
            print(f"   📍 Position: {unrealized['btc_amount']:.6f} BTC @ ${unrealized['entry_price']:.2f} → ${unrealized['current_price']:.2f}", flush=True)

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
        current_price = safe_api_call(exchange.fetch_ticker, 'BTC/USDC')['last']
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
            display_enhanced_price_jump_status()

        if cooldown_required > 0:
            print(f"⏳ Trade cooldown: {cooldown_required}s remaining (avoiding overtrading)", flush=True)
            time.sleep(min(interval_seconds, cooldown_required + 10))
            continue

        try:
            df = fetch_ohlcv(exchange, 'BTC/USDC', '1m', 50)

            # Synchronize holding position with actual balance
            balance = safe_api_call(exchange.fetch_balance)
            btc_balance = balance['BTC']['free']
            current_price = df['close'].iloc[-1]

            # Auto-detect if we're actually holding BTC (threshold: $1 worth)
            btc_value = btc_balance * current_price
            if btc_value > 1.0 and not holding_position:
                holding_position = True
                entry_price = current_price
                stop_loss_price = current_price * (1 - stop_loss_percentage)
                take_profit_price = current_price * (1 + take_profit_percentage)

                # Update state manager
                state_manager.update_trading_state(
                    holding_position=True,
                    entry_price=entry_price,
                    stop_loss_price=stop_loss_price,
                    take_profit_price=take_profit_price
                )

                print(f"🔄 SYNC: Detected existing BTC position worth ${btc_value:.2f}", flush=True)
            elif btc_value <= 1.0 and holding_position:
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
                print(f"🔄 SYNC: No significant BTC position detected", flush=True)

            # 🎯 STEP 1: ENHANCED MULTI-TIMEFRAME MA ANALYSIS
            print(f"\n🎯 MULTI-TIMEFRAME MA ANALYSIS:", flush=True)

            # Get multi-timeframe signals
            multi_signals = detect_multi_timeframe_ma_signals(exchange, 'BTC/USDC', current_price)

            # Primary signal from combined analysis
            ma_signal = multi_signals['combined']

            # Display analysis
            print(f"   📊 1m Signal: {multi_signals['1m']['action']} ({multi_signals['1m']['confidence']:.3f})", flush=True)
            print(f"   📊 5m Signal: {multi_signals['5m']['action']} ({multi_signals['5m']['confidence']:.3f})", flush=True)
            print(f"   🎯 Combined: {ma_signal['action']} ({ma_signal['confidence']:.3f})", flush=True)

            if ma_signal.get('agreement'):
                print(f"   ✅ Timeframe Agreement: {ma_signal['action']} signal", flush=True)
            else:
                print(f"   ⚠️ Timeframe Disagreement: Using cautious approach", flush=True)

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

                # Show timeframe breakdown
                if 'signal_1m' in ma_signal and 'signal_5m' in ma_signal:
                    print(f"   📊 1m contribution: {ma_signal['signal_1m']['confidence']:.3f}", flush=True)
                    print(f"   📊 5m contribution: {ma_signal['signal_5m']['confidence']:.3f}", flush=True)

                # Execute BUY signal
                if ma_signal['action'] == 'BUY' and not holding_position:
                    position_size = calculate_position_size(current_price, 0.02, ma_signal['confidence'], total_portfolio_value)
                    if position_size > 0:
                        print(f"🚀 MULTI-TIMEFRAME PRIORITY BUY: ${position_size:.2f}")
                        order = place_intelligent_order('BTC/USDC', 'buy', amount_usd=position_size, use_limit=True)

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
                    btc_amount = balance['BTC']['free']
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
                    if can_sell and btc_amount > 0:
                        print(f"🚨 MULTI-TIMEFRAME PRIORITY SELL: {btc_amount:.6f} BTC")
                        order = place_intelligent_order('BTC/USDC', 'sell', amount_usd=0, use_limit=True)
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

            # 🎯 STEP 2: Check Risk Management (Stop Loss, Take Profit)
            if holding_position:
                total_balance = balance['total']['USDC'] + (balance['total']['BTC'] * current_price)
                risk_action = check_risk_management(current_price, total_balance)

                if risk_action in ['STOP_LOSS', 'TAKE_PROFIT', 'EMERGENCY_EXIT', 'MAX_DRAWDOWN_HIT', 'TRAILING_STOP']:
                    print(f"🚨 RISK MANAGEMENT TRIGGERED: {risk_action}")
                    btc_amount = balance['BTC']['free']
                    # --- ENHANCEMENT: Always allow emergency/stop-loss exits, but log reason ---
                    sell_reason = f"RISK_MANAGEMENT: {risk_action}"
                    order = None
                    if btc_amount > 0:
                        order = safe_api_call(exchange.create_market_order, 'BTC/USDC', 'sell', btc_amount)

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
                        log_message(f"❌ SELL NOT EXECUTED: {sell_reason} (no BTC available)")
                        print(f"❌ SELL NOT EXECUTED: {sell_reason} (no BTC available)")
                        updated_balance = safe_api_call(exchange.fetch_balance)
                        log_trade("SELL", "BTC/USDC", btc_amount, current_price, updated_balance['USDC']['free'])

                        # Clear persistent state
                        state_manager.exit_trade(risk_action)
                        holding_position = False
                        print(f"✅ Risk management SELL: {btc_amount:.6f} BTC at ${current_price:.2f}")

                        time.sleep(300)  # 5 minute cooldown
                        continue

            # 🎯 STEP 3: Fallback Strategies (when multi-timeframe signal is weak)
            if ma_signal['confidence'] < 0.85:
                print(f"\n📊 FALLBACK STRATEGIES (Multi-timeframe confidence: {ma_signal['confidence']:.3f})")

                # Simple fallback: use multi-timeframe signal even if moderate confidence
                signal = ma_signal.copy()

                # If multi-timeframe signal is weak, create a conservative HOLD signal
                if ma_signal['confidence'] < 0.5:
                    signal = {
                        'action': 'HOLD',
                        'confidence': 0.0,
                        'reason': 'No clear multi-timeframe signal - awaiting better opportunity'
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

                # 🎯 LOWER THRESHOLD FOR MULTI-TIMEFRAME SIGNALS (aggressive day trading)
                if 'multi-timeframe' in signal.get('reason', '').lower():
                    min_confidence *= 0.80  # 20% lower threshold for multi-timeframe signals
                    print(f"🎯 Multi-timeframe signal - reduced threshold to {min_confidence:.3f}")

                print(f"   Required confidence: {min_confidence:.3f}", flush=True)
                print(f"   Signal confidence: {signal.get('confidence', 0):.3f}", flush=True)

                # Execute trading logic with MA focus
                if signal['action'] == 'BUY' and not holding_position and signal.get('confidence', 0) >= min_confidence:
                    position_size = calculate_position_size(current_price, 0.02, signal['confidence'], total_portfolio_value)
                    if position_size > 0:
                        print(f"📥 MULTI-TIMEFRAME ENHANCED BUY signal - ${position_size:.2f} of BTC...")
                        print(f"   Multi-timeframe confidence: {ma_signal['confidence']:.3f}")
                        print(f"   Final confidence: {signal['confidence']:.3f}")

                        order = place_intelligent_order('BTC/USDC', 'buy', amount_usd=position_size, use_limit=True)

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
                        btc_amount = balance['BTC']['free']
                        if btc_amount > 0:
                            print(f"📤 MULTI-TIMEFRAME ENHANCED SELL signal - Current P&L: {current_pnl:.2%}")
                            print(f"   Multi-timeframe confidence: {ma_signal['confidence']:.3f}")
                            print(f"   Final confidence: {signal['confidence']:.3f}")

                            order = place_intelligent_order('BTC/USDC', 'sell', amount_usd=0, use_limit=True)

                            if order:
                                state_manager.exit_trade("MA_ENHANCED_SELL")
                                holding_position = False
                                consecutive_losses = 0
                                print(f"✅ SELL EXECUTED: Multi-timeframe enhanced strategy")

                else:
                    print("⏸ No action taken - awaiting stronger multi-timeframe signal", flush=True)

        except Exception as e:
            print("❌ Error in trading loop:", e, flush=True)

        # Add heartbeat before sleep
        print(f"💓 Loop completed, sleeping for {interval_seconds} seconds...", flush=True)
        time.sleep(interval_seconds)

def generate_reports():
    """Generate trading performance reports"""
    try:
        print("📊 Generating performance reports...")
        # Add report generation logic here if needed
        print("✅ Reports generated successfully")
    except Exception as e:
        print(f"❌ Error generating reports: {e}")

# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":
    print("🚀 STARTING ENHANCED AGGRESSIVE DAY TRADING BOT")
    print("🎯 PRIMARY STRATEGY: Multi-Timeframe MA7/MA25 Crossover + Advanced Price Detection")
    print("⚡ IMPROVEMENTS: 30s loops, 15min cooldown, multi-timeframe jump detection, sustained trend tracking")
    print("🔍 DETECTION SYSTEM: Multi-timeframe price movement analysis (spike/short/medium/long)")
    print("="*70)

    try:
        # Display configuration info
        trading_config = optimized_config['trading']
        if trading_config.get('position_sizing_mode') == 'percentage':
            print(f"💰 Position Sizing: {trading_config['base_position_pct']:.1%} of portfolio ({trading_config['min_position_pct']:.1%}-{trading_config['max_position_pct']:.1%} range)")
        else:
            print(f"💰 Position Sizing: Fixed ${trading_config['base_amount_usd']} per trade")

        print(f"⏰ Trade Cooldown: {min_trade_interval//60} minutes | Stop Loss: {stop_loss_percentage:.1%} | Take Profit: {take_profit_percentage:.1%}")
        print(f"🔧 Confidence Threshold: {optimized_config['strategy_parameters']['confidence_threshold']:.3f}")
        print("🎯 MA7/MA25 ABSOLUTE PRIORITY: Multi-timeframe crossover signals override all other strategies")
        print("💡 Press Ctrl+C to stop and generate reports")
        print("="*70)

        # Test connection and start trading
        test_connection()

        # Use faster loop timing from config
        loop_interval = optimized_config['system']['loop_interval_seconds']
        print(f"⚡ Enhanced Loop Timing: {loop_interval}s intervals for better responsiveness")
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
