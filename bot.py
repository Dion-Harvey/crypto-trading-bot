# =============================================================================
# CRYPTO TRADING BOT - Main Entry Point
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

    # Combine Kelly sizing with all risk factors
    institutional_size = (kelly_size * volatility_factor * confidence_factor *
                         loss_factor * drawdown_factor * time_factor * var_factor * size_adjustment)

    # Apply bounds based on position sizing mode
    final_size = max(min_amount, min(max_amount, institutional_size))

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

def place_intelligent_order(symbol, side, amount_usd, use_limit=True, timeout_seconds=20):
    """
    Intelligent order execution with limit orders and market order fallback
    Reduces slippage while ensuring fills
    """
    global last_trade_time, consecutive_losses, entry_price, stop_loss_price, take_profit_price

    try:
        # Check if we have sufficient balance before placing order
        balance = safe_api_call(exchange.fetch_balance)

        # Get current market data
        orderbook = safe_api_call(exchange.fetch_order_book, symbol)
        ticker = safe_api_call(exchange.fetch_ticker, symbol)
        market_price = ticker['last']

        # Binance minimum order requirements
        MIN_NOTIONAL_VALUE = 10.0  # Minimum $10 USD equivalent
        MIN_BTC_AMOUNT = 0.00001   # Minimum 0.00001 BTC

        if side.upper() == 'BUY':
            available_usd = balance['USDC']['free']
            if available_usd < amount_usd:
                print(f"❌ Insufficient USDC balance: ${available_usd:.2f} < ${amount_usd:.2f}")
                return None

            # Use best bid for limit buy (slightly below market)
            limit_price = orderbook['bids'][0][0] if orderbook['bids'] else market_price * 0.999
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
                print(f"   💡 Current balance: {available_btc:.6f} BTC (~${available_btc * market_price:.2f})")
                return None

            # Check minimum notional value
            notional_value = amount * market_price
            if notional_value < MIN_NOTIONAL_VALUE:
                print(f"❌ SELL order value too small: ${notional_value:.2f} < ${MIN_NOTIONAL_VALUE:.2f} minimum")
                print(f"   BTC amount: {amount:.6f}, Price: ${market_price:.2f}")
                return None

            # Use best ask for limit sell (slightly above market)
            limit_price = orderbook['asks'][0][0] if orderbook['asks'] else market_price * 1.001

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
# LIVE STRATEGY LOOP
# =============================================================================

def run_continuously(interval_seconds=60):

    global holding_position, last_trade_time, consecutive_losses, active_trade_index, entry_price, stop_loss_price, take_profit_price

    while True:
        # Always ensure risk management variables are initialized
        if 'entry_price' not in globals() or entry_price is None:
            entry_price = None
        if 'stop_loss_price' not in globals() or stop_loss_price is None:
            stop_loss_price = None
        if 'take_profit_price' not in globals() or take_profit_price is None:
            take_profit_price = None

        print("\n" + "="*50)
        print("RUNNING TRADING STRATEGY LOOP")
        print("="*50)

        from log_utils import calculate_daily_pnl

        daily_pnl = calculate_daily_pnl()
        print(f"📉 Daily PnL: ${daily_pnl:.2f}")

        # Calculate dynamic daily loss limit based on current portfolio
        balance = safe_api_call(exchange.fetch_balance)
        current_price = safe_api_call(exchange.fetch_ticker, 'BTC/USDC')['last']
        total_portfolio_value = balance['total']['USDC'] + (balance['total']['BTC'] * current_price)

        dynamic_daily_loss_limit = calculate_dynamic_daily_loss_limit(total_portfolio_value)

        # Enhanced risk management with dynamic limits (logging only)
        if daily_pnl <= -dynamic_daily_loss_limit:
            print(f"⚠️ Daily loss alert: ${daily_pnl:.2f} exceeds limit -${dynamic_daily_loss_limit:.2f} (continuing trading as requested)")

        if consecutive_losses >= max_consecutive_losses:
            print(f"⚠️ {consecutive_losses} consecutive losses detected (continuing trading as requested)")
            # Reset consecutive losses to avoid spam alerts
            consecutive_losses = 0

        # Check trade timing to avoid overtrading
        time_since_last_trade = time.time() - last_trade_time
        if time_since_last_trade < min_trade_interval:
            remaining_time = min_trade_interval - int(time_since_last_trade)
            print(f"⏳ Trade cooldown: {remaining_time}s remaining (avoiding overtrading)")
            time.sleep(min(interval_seconds, remaining_time + 10))
            continue

        try:
            df = fetch_ohlcv(exchange, 'BTC/USDC', '1m', 50)

            # Monitor exchange-side orders with safe API calls
            open_orders = monitor_exchange_orders()
            recent_fills = check_exchange_order_fills()

            # Synchronize holding position with actual balance
            balance = safe_api_call(exchange.fetch_balance)
            btc_balance = balance['BTC']['free']
            current_price = df['close'].iloc[-1]

            # Auto-detect if we're actually holding BTC (threshold: $1 worth)
            btc_value = btc_balance * current_price
            if btc_value > 1.0 and not holding_position:
                holding_position = True
                entry_price = current_price  # Estimate current price as entry
                stop_loss_price = current_price * (1 - stop_loss_percentage)
                take_profit_price = current_price * (1 + take_profit_percentage)
                print(f"🔄 SYNC: Detected existing BTC position worth ${btc_value:.2f}")
                print(f"🛡️ Risk Levels Set: Entry=${current_price:.2f}, SL=${stop_loss_price:.2f}, TP=${take_profit_price:.2f}")
            elif btc_value <= 1.0 and holding_position:
                holding_position = False
                entry_price = None
                stop_loss_price = None
                take_profit_price = None
                print(f"🔄 SYNC: No significant BTC position detected")

            # Initialize strategy ensemble with institutional-grade analysis
            base_strategy = MultiStrategyOptimized()
            enhanced_strategy = EnhancedMultiStrategy()
            hybrid_strategy = AdvancedHybridStrategy()

            # Get signals from all strategy systems
            base_signal = base_strategy.get_consensus_signal(df)
            enhanced_signal = enhanced_strategy.get_enhanced_consensus_signal(df)
            adaptive_signal = hybrid_strategy.get_adaptive_signal(df)

            # Get institutional-grade signal analysis
            total_balance = balance['total']['USDC'] + (balance['total']['BTC'] * current_price)
            institutional_signal = institutional_manager.get_institutional_signal(
                df, portfolio_value=total_balance, base_position_size=optimized_config['trading']['base_amount_usd']
            )

            # Intelligent signal fusion with institutional overlay
            signal = fuse_strategy_signals(base_signal, enhanced_signal, adaptive_signal, df, institutional_signal)

            # 🎯 NEW: ADVANCED SIGNAL QUALITY ANALYSIS
            if signal and signal.get('action') in ['BUY', 'SELL']:
                quality_analysis = success_enhancer.analyze_signal_quality(df, signal, current_price)

                # Enhance signal with quality analysis
                signal['quality_analysis'] = quality_analysis
                signal['enhanced_confidence'] = quality_analysis['enhanced_confidence']
                signal['quality_score'] = quality_analysis['overall_quality_score']

                # Log quality analysis
                log_message(f"🔍 SIGNAL QUALITY ANALYSIS:")
                log_message(f"   Overall Quality Score: {quality_analysis['overall_quality_score']:.3f}")
                log_message(f"   Enhanced Confidence: {quality_analysis['enhanced_confidence']:.3f}")
                for factor, score in quality_analysis['quality_factors'].items():
                    log_message(f"   {factor.replace('_', ' ').title()}: {score:.3f}")

                # Display recommendations
                for rec in quality_analysis['recommendations']:
                    log_message(f"   {rec}")

            # Display comprehensive system status
            display_system_status(signal, current_price, balance)

            # Get dynamic confidence threshold from config
            strategy_config = optimized_config['strategy_parameters']
            base_min_confidence = strategy_config['confidence_threshold']

            # Check risk management (stop loss, take profit, max drawdown)

            if holding_position:
                total_balance = balance['total']['USDC'] + (balance['total']['BTC'] * current_price)

                risk_action = check_risk_management(current_price, total_balance)

                if risk_action in ['STOP_LOSS', 'TAKE_PROFIT', 'EMERGENCY_EXIT', 'MAX_DRAWDOWN_HIT', 'TRAILING_STOP']:
                    print(f"🚨 RISK MANAGEMENT TRIGGERED: {risk_action}")

                    # Execute exit trade
                    btc_amount = balance['BTC']['free']
                    if btc_amount > 0:
                        order = safe_api_call(exchange.create_market_order, 'BTC/USDC', 'sell', btc_amount)

                        # Update consecutive losses for stop loss
                        if risk_action in ['STOP_LOSS', 'EMERGENCY_EXIT']:
                            consecutive_losses += 1
                            state_manager.update_consecutive_losses(consecutive_losses)
                            log_message(f"📉 Consecutive losses: {consecutive_losses}")

                            # Update Kelly Criterion with loss result
                            if entry_price is not None and entry_price > 0:
                                pnl_pct = (current_price - entry_price) / entry_price
                                institutional_manager.add_trade_result(pnl_pct)
                        else:
                            consecutive_losses = 0  # Reset on profitable exit
                            state_manager.update_consecutive_losses(consecutive_losses)

                            # Update Kelly Criterion with win result
                            if entry_price is not None and entry_price > 0:
                                pnl_pct = (current_price - entry_price) / entry_price
                                institutional_manager.add_trade_result(pnl_pct)

                        # Log the trade
                        updated_balance = safe_api_call(exchange.fetch_balance)
                        log_trade("SELL", "BTC/USDC", btc_amount, current_price, updated_balance['USDC']['free'])

                        # Update performance tracking
                        if active_trade_index is not None:
                            performance_tracker.update_trade_outcome(active_trade_index, None, current_price, risk_action)
                            active_trade_index = None

                        # Clear persistent state
                        state_manager.exit_trade(risk_action)
                        holding_position = False
                        print(f"✅ Risk management SELL: {btc_amount:.6f} BTC at ${current_price:.2f}")

                        # Take a break after risk management exit
                        time.sleep(300)  # 5 minute cooldown
                        continue

                # 🎯 PARTIAL EXIT HANDLING (Your suggestion to scale out of winners)
                elif risk_action and risk_action.startswith('PARTIAL_EXIT_'):
                    partial_amount_pct = float(risk_action.split('_')[-1]) / 100
                    btc_amount = balance['BTC']['free']
                    partial_btc_amount = btc_amount * partial_amount_pct

                    if partial_btc_amount > 0.00001:  # Minimum BTC amount
                        print(f"💰 PARTIAL EXIT: Selling {partial_amount_pct:.0%} of position")
                        order = safe_api_call(exchange.create_market_order, 'BTC/USDC', 'sell', partial_btc_amount)

                        # Log partial exit
                        updated_balance = safe_api_call(exchange.fetch_balance)
                        log_trade(f"PARTIAL_SELL_{partial_amount_pct:.0%}", "BTC/USDC", partial_btc_amount, current_price, updated_balance['USDC']['free'])

                        # Mark partial exit as done
                        state_manager._partial_exit_done = True

                        # Adjust stop loss to break-even for remaining position
                        stop_loss_price = entry_price * 1.005  # Slight profit to cover fees
                        log_message(f"🛡️ Adjusted stop loss to break-even: ${stop_loss_price:.2f}")

                        print(f"✅ Partial exit: {partial_btc_amount:.6f} BTC at ${current_price:.2f}")
                        print(f"💎 Holding remaining {btc_amount - partial_btc_amount:.6f} BTC with break-even stop")


            try:
                print(f"\n🎯 INSTITUTIONAL MULTI-STRATEGY SIGNAL: {signal.get('action', 'N/A')} at ${current_price:.2f}")
                print(f"   Overall Confidence: {signal.get('confidence', 0.0):.3f}")
                print(f"   Primary Reason: {signal.get('reason', 'N/A')}")

                # Show institutional analysis details
                if 'institutional_analysis' in signal:
                    inst = signal['institutional_analysis']
                    try:
                        display_institutional_analysis_safe(inst)
                    except Exception as inst_display_error:
                        print(f"   [Error] Institutional analysis display failed: {inst_display_error}")
                        traceback.print_exc()

                # Show fusion details
                if 'fusion_info' in signal:
                    fusion = signal['fusion_info']
                    try:
                        print(f"\n🧠 Strategy Selection: {fusion.get('selection_reason', 'N/A')}")
                        print(f"   🎚️ Adaptive Mode: {fusion.get('adaptive_mode', 'N/A')}")
                        print(f"   📊 Market Volatility: {fusion.get('market_volatility', 0.0):.4f}")
                        print(f"   🗳️ All Strategy Votes:")
                        for name, vote_info in fusion.get('all_signals', {}).items():
                            print(f"      {name}: {vote_info.get('action', 'N/A')} ({vote_info.get('confidence', 0.0):.2f})")
                    except Exception as fusion_error:
                        print(f"   [Error] Fusion info display failed: {fusion_error}")
                        traceback.print_exc()

                # Show vote counts if available
                if 'vote_count' in signal:
                    try:
                        votes = signal['vote_count']
                        print(f"   Votes: BUY={votes.get('BUY', 0)}, SELL={votes.get('SELL', 0)}, HOLD={votes.get('HOLD', 0)}")
                    except Exception as vote_error:
                        print(f"   [Error] Vote count display failed: {vote_error}")

                # Show individual strategy signals if available
                if 'individual_signals' in signal and signal['individual_signals']:
                    try:
                        print(f"   📋 Individual Strategy Details:")
                        for strategy_name, individual in signal['individual_signals'].items():
                            print(f"      {strategy_name}: {individual.get('action', 'N/A')} ({individual.get('confidence', 0.0):.2f}) - {individual.get('reason', 'N/A')}")
                    except Exception as indiv_error:
                        print(f"   [Error] Individual signals display failed: {indiv_error}")

                # Show market conditions if available
                if 'market_conditions' in signal:
                    try:
                        mc = signal['market_conditions']
                        print(f"\n📈 MARKET CONDITIONS:")
                        print(f"   Volatility: {mc.get('volatility', 0.0):.3f} ({'HIGH' if mc.get('is_high_volatility', False) else 'NORMAL'})")
                        print(f"   Momentum: {mc.get('momentum', 0.0):.3f} ({mc.get('momentum', 0.0)*100:.1f}%)")
                        print(f"   5min Change: {mc.get('price_change_5min', 0.0):.4f} ({mc.get('price_change_5min', 0.0)*100:.2f}%)")
                        if mc.get('strong_uptrend', False):
                            print("   🔥 STRONG UPTREND detected - Peak selling opportunity!")
                        elif mc.get('strong_downtrend', False):
                            print("   💎 STRONG DOWNTREND detected - Dip buying opportunity!")
                    except Exception as mc_error:
                        print(f"   [Error] Market conditions display failed: {mc_error}")

            except Exception as display_block_error:
                print(f"❌ Error in trading loop display block: {display_block_error}")
                traceback.print_exc()

            # Enhanced confidence thresholds with quality analysis
            base_min_confidence = strategy_config['confidence_threshold']

            # 🎯 QUALITY-BASED CONFIDENCE ADJUSTMENT
            if 'quality_analysis' in signal:
                quality_score = signal['quality_analysis']['overall_quality_score']
                if quality_score >= 0.8:
                    # Exceptional quality - lower threshold for high-quality signals
                    min_confidence = base_min_confidence * 0.85
                    log_message(f"🎯 High-quality signal detected - lowering confidence threshold to {min_confidence:.3f}")
                elif quality_score < 0.6:
                    # Poor quality - raise threshold significantly
                    min_confidence = base_min_confidence * 1.5
                    log_message(f"⚠️ Low-quality signal detected - raising confidence threshold to {min_confidence:.3f}")
                else:
                    min_confidence = base_min_confidence

                # Use enhanced confidence instead of raw confidence
                signal_confidence_to_use = signal.get('enhanced_confidence', signal.get('confidence', 0.0))
            else:
                min_confidence = base_min_confidence
                signal_confidence_to_use = signal.get('confidence', 0.0)

            # Adjust threshold based on market conditions
            if 'market_conditions' in signal:
                mc = signal['market_conditions']
                # Lower threshold for high-confidence dip/peak trades
                if (signal['action'] == 'BUY' and mc.get('strong_downtrend', False)) or \
                   (signal['action'] == 'SELL' and mc.get('strong_uptrend', False)):
                    min_confidence = min_confidence * 0.9  # Only 10% lower for extreme conditions
                elif mc.get('is_high_volatility', False):
                    min_confidence = min_confidence * 1.3  # 30% higher in high volatility

            print(f"   Required confidence: {min_confidence:.3f}")
            print(f"   Signal confidence: {signal_confidence_to_use:.3f}")

            if signal['action'] == 'BUY' and not holding_position and signal_confidence_to_use >= min_confidence:
                # Check trend filter to avoid contrarian trades in strong trends
                trend_filtered = is_strong_trend(df, signal)
                if trend_filtered:
                    print("⚠️ BUY signal filtered out due to strong trend detection")
                # 🛡️ NEW: Anti-whipsaw protection
                elif not check_anti_whipsaw_protection(signal, current_price, df):
                    print("⚠️ BUY signal filtered out due to anti-whipsaw protection")
                else:
                    # Enhanced BUY signal validation with SUCCESS RATE OPTIMIZATION
                    buy_votes = signal.get('vote_count', {}).get('BUY', 1)
                    signal_confidence = signal_confidence_to_use  # Use quality-enhanced confidence

                    # 🎯 QUALITY GATE - Only proceed with high-quality signals
                    quality_gate_passed = True
                    if 'quality_analysis' in signal:
                        quality_filters = signal['quality_analysis']['filters_passed']
                        if not quality_filters.get('minimum_quality', False):
                            quality_gate_passed = False
                            print("❌ BUY signal rejected: Failed minimum quality gate")
                            print(f"   Quality score: {signal.get('quality_score', 0):.3f} (minimum: 0.60)")

                    # 🎯 MA TREND ALIGNMENT FILTER (Your suggestion: EMA 7 > EMA 25 > EMA 99)
                    ma_trend_confirmed = True
                    market_config = optimized_config.get('market_filters', {})
                    if market_config.get('ma_trend_filter_enabled', True):
                        if len(df) >= 99:
                            ema_7 = df['close'].ewm(span=7).mean().iloc[-1]
                            ema_25 = df['close'].ewm(span=25).mean().iloc[-1]
                            ema_99 = df['close'].ewm(span=99).mean().iloc[-1]

                            if signal['action'] == 'BUY':
                                ma_trend_confirmed = ema_7 > ema_25 > ema_99
                                if not ma_trend_confirmed:
                                    log_message(f"❌ MA Trend Filter: EMA7({ema_7:.2f}) > EMA25({ema_25:.2f}) > EMA99({ema_99:.2f}) not aligned for BUY")

                    # 🎯 RSI RANGE FILTER (Your suggestion: avoid RSI 40-60 choppy range)
                    rsi_range_ok = True
                    if market_config.get('rsi_range_filter', {}).get('enabled', False):
                        rsi_avoid_min = market_config['rsi_range_filter']['avoid_range_min']
                        rsi_avoid_max = market_config['rsi_range_filter']['avoid_range_max']

                        # Calculate current RSI
                        if len(df) >= 14:
                            from success_rate_enhancer import calculate_rsi
                            current_rsi = calculate_rsi(df['close']).iloc[-1]

                            if rsi_avoid_min <= current_rsi <= rsi_avoid_max:
                                rsi_range_ok = False
                                log_message(f"❌ RSI Range Filter: RSI({current_rsi:.1f}) in choppy range {rsi_avoid_min}-{rsi_avoid_max}")

                    if not quality_gate_passed:
                        continue  # Skip this signal entirely

                    if not ma_trend_confirmed:
                        print("❌ BUY signal rejected: MA trend alignment required")
                        continue

                    if not rsi_range_ok:
                        print("❌ BUY signal rejected: RSI in choppy range - avoiding whipsaws")
                        continue

                    # Extract RSI values for additional context
                    rsi_values = []
                    for individual in signal.get('individual_signals', []):
                        if 'RSI' in individual.get('reason', ''):
                            reason = individual['reason']
                            if 'RSI' in reason:
                                rsi_match = re.search(r'RSI.*?(\d+\.\d+)', reason)
                                if rsi_match:
                                    rsi_values.append(float(rsi_match.group(1)))

                    # Volume confirmation (critical for quality trades)
                    volume_confirmed = False
                    if 'volume' in df.columns and len(df) >= 20:
                        recent_volume = df['volume'].iloc[-5:].mean()
                        avg_volume = df['volume'].iloc[-20:].mean()
                        volume_confirmed = recent_volume > avg_volume * 1.4

                    # Multi-timeframe trend confirmation
                    trend_confirmed = False
                    if len(df) >= 50:
                        ma_short = df['close'].rolling(7).mean().iloc[-1]
                        ma_medium = df['close'].rolling(21).mean().iloc[-1]
                        ma_long = df['close'].rolling(50).mean().iloc[-1]
                        trend_confirmed = ma_short > ma_medium and current_price > ma_short

                    # Price action confirmation (not in immediate resistance)
                    price_action_good = True
                    if len(df) >= 20:
                        recent_high = df['high'].iloc[-10:].max()
                        price_action_good = current_price < recent_high * 0.98  # Not near recent highs

                    # IMPROVED BUY criteria - ALL must be met for higher quality:
                    high_confidence = signal_confidence >= 0.65  # Raised threshold
                    strong_consensus = buy_votes >= 4  # Need stronger agreement
                    good_rsi = any(rsi < 35 for rsi in rsi_values) if rsi_values else signal_confidence > 0.7
                    institutional_backed = 'institutional_analysis' in signal and signal.get('risk_score', 'HIGH') != 'HIGH'

                    # Support/resistance or dip-buying signals
                    support_signal = any('support' in individual.get('reason', '').lower()
                                       for individual in signal.get('individual_signals', {}).values())

                    # Quality gate: ALL core conditions must be met
                    core_quality = high_confidence and (strong_consensus or institutional_backed)
                    additional_confirmation = (good_rsi or support_signal) and volume_confirmed and trend_confirmed and price_action_good

                    execute_buy = core_quality and additional_confirmation

                    if not execute_buy:
                        print(f"⚠️ BUY signal filtered for quality: conf={signal_confidence:.3f}, votes={buy_votes}, vol_conf={volume_confirmed}, trend_conf={trend_confirmed}")
                        print(f"   RSI favorable: {good_rsi}, Price action: {price_action_good}, Support: {support_signal}")
                        print(f"   Core quality: {core_quality}, Additional confirmation: {additional_confirmation}")
                    else:
                        # Calculate dynamic position size with institutional methods
                        volatility = signal.get('market_conditions', {}).get('volatility', 0.02)
                        total_balance = balance['total']['USDC'] + (balance['total']['BTC'] * current_price)

                        # Use institutional position sizing if available
                        if 'institutional_analysis' in signal:
                            inst_analysis = signal['institutional_analysis']
                            kelly_size = inst_analysis.get('kelly_position_size', 0)
                            if kelly_size > 0:
                                # Ensure institutional Kelly size meets minimum
                                position_size = max(10, min(25, kelly_size))  # $10 minimum, $25 max
                                log_message(f"💼 Using institutional Kelly position size: ${position_size:.2f}")
                            else:
                                position_size = calculate_position_size(
                                    current_price,
                                    volatility,
                                    signal['confidence'],
                                    total_balance
                                )
                        else:
                            position_size = calculate_position_size(
                                current_price,
                                volatility,
                                signal['confidence'],
                                total_balance
                            )

                        # Check if position size is valid (0 means skip trade)
                        if position_size <= 0:
                            print(f"⚠️ Position size too small (${position_size:.2f}), skipping trade")
                            continue

                        # Record trade signal for performance tracking
                        trade_index = performance_tracker.record_trade_signal(signal, signal.get('market_conditions', {}))

                        print(f"📥 INSTITUTIONAL Multi-strategy BUY signal - ${position_size:.2f} of BTC...")
                        print(f"   ✅ Quality checks: High conf={high_confidence}, Strong consensus={strong_consensus}, Oversold conditions met")

                        # Show institutional context if available
                        if 'institutional_analysis' in signal:
                            inst = signal['institutional_analysis']
                            regime_name = inst.get('market_regime', {}).get('regime', 'Unknown')
                            ml_conf = inst.get('ml_signal', {}).get('confidence', 0.0)
                            var_daily = inst.get('risk_analysis', {}).get('var_daily', 0.0)
                            print(f"   🏛️ Regime: {regime_name}, Risk: {signal.get('risk_score', 'UNKNOWN')}")
                            print(f"   📊 ML Confidence: {ml_conf:.2f}, VaR: ${var_daily:.2f}")

                        order = place_intelligent_order('BTC/USDC', 'buy', amount_usd=position_size, use_limit=True)
                        if order:
                            holding_position = True
                            active_trade_index = trade_index
                            performance_tracker.update_trade_outcome(trade_index, current_price)

                            # Place advanced risk management orders (entry_price is set in place_intelligent_order)
                            risk_order = place_advanced_risk_orders('BTC/USDC', entry_price, order.get('amount', 0))

                            # Save trade state persistently
                            state_manager.enter_trade(
                                entry_price=entry_price,
                                stop_loss_price=stop_loss_price,
                                take_profit_price=take_profit_price,
                                trade_id=order.get('id'),
                                active_trade_index=trade_index
                            )

            elif signal['action'] == 'SELL' and holding_position and signal_confidence_to_use >= min_confidence:
                # Enhanced SELL signal validation with profit optimization
                sell_votes = signal.get('vote_count', {}).get('SELL', 1)
                signal_confidence = signal.get('confidence', 0.0)

                # Calculate current profit/loss
                current_pnl = 0
                if entry_price and entry_price > 0:
                    current_pnl = (current_price - entry_price) / entry_price

                # Don't sell at small losses unless technical conditions are very bearish
                if current_pnl < -0.01:  # If losing more than 1%
                    # Need very strong bearish signal to sell at a loss
                    if signal_confidence < 0.75 or sell_votes < 4:
                        print(f"⚠️ SELL signal rejected: Would realize loss of {current_pnl:.2%} without strong confirmation")
                        print("⏸ No action taken.")
                        continue

                # Check for momentum continuation (don't sell in strong uptrends)
                momentum_check = True
                if len(df) >= 10:
                    recent_momentum = (df['close'].iloc[-1] - df['close'].iloc[-5]) / df['close'].iloc[-5]
                    if recent_momentum > 0.02:  # Strong recent uptrend
                        momentum_check = False
                        print("⚠️ SELL signal filtered - strong momentum continuation detected")

                # Volume confirmation for sell signals
                volume_confirmed = True
                if 'volume' in df.columns and len(df) >= 20:
                    recent_volume = df['volume'].iloc[-3:].mean()
                    avg_volume = df['volume'].iloc[-20:].mean()
                    volume_confirmed = recent_volume > avg_volume * 1.2

                # RSI overbought confirmation
                rsi_overbought = False
                for individual in signal.get('individual_signals', {}).values():
                    if 'RSI' in individual.get('reason', ''):
                        reason = individual['reason']
                        rsi_match = re.search(r'RSI.*?(\d+\.\d+)', reason)
                        if rsi_match and float(rsi_match.group(1)) > 70:
                            rsi_overbought = True

                # Profit-taking logic
                profit_taking = current_pnl > 0.05  # Take profits if up 5%+

                # Check trend filter to avoid selling in strong uptrends (let profits run)
                trend_filtered = is_strong_trend(df, signal)

                if trend_filtered and not profit_taking:
                    print("⚠️ SELL signal filtered out - letting profits run in strong uptrend")
                elif not momentum_check:
                    pass  # Already printed message above
                elif signal_confidence >= 0.65 and (volume_confirmed or rsi_overbought or profit_taking):
                    print(f"📤 Enhanced SELL signal - Current P&L: {current_pnl:.2%}")
                    balance = safe_api_call(exchange.fetch_balance)
                    btc_amount = balance['BTC']['free']
                    if btc_amount > 0:
                        ticker = safe_api_call(exchange.fetch_ticker, 'BTC/USDC')
                        price = ticker['last']
                        order = place_intelligent_order('BTC/USDC', 'sell', amount_usd=0, use_limit=True)

                        # Only continue if order was successfully placed
                        if order is not None:
                            # Clear persistent state
                            state_manager.exit_trade("STRATEGY_SELL")
                            holding_position = False

                            # Reset consecutive losses on successful trade
                            consecutive_losses = 0
                            state_manager.update_consecutive_losses(consecutive_losses)

                            # Update Kelly Criterion with successful trade result
                            if entry_price and entry_price > 0:
                                pnl_pct = (current_price - entry_price) / entry_price
                                institutional_manager.add_trade_result(pnl_pct)

                            # Update performance tracking
                            if active_trade_index is not None:
                                performance_tracker.update_trade_outcome(active_trade_index, None, current_price)
                                active_trade_index = None

                            print(f"✅ SOLD {btc_amount:.6f} BTC at ${price:.2f}")
                            print(f"📝 Trade logged to trade_log.csv")
                        else:
                            print("⚠️ SELL order skipped due to insufficient amount or minimum order requirements")
                            print("💡 Tip: The bot will continue to monitor for BUY opportunities to accumulate more BTC")
                    else:
                        print("⚠️ No BTC balance available to sell")
                else:
                    print("⚠️ SELL signal quality check failed - holding position")

            else:
                print("⏸ No action taken.")

        except Exception as e:
            print("❌ Error in trading loop:", e)

        time.sleep(interval_seconds)

# =============================================================================
# REPORTING FUNCTIONS
# =============================================================================

def generate_reports():
    """Generate comprehensive trading reports - updates existing files"""
    print("\n" + "="*60)
    print("📊 UPDATING COMPREHENSIVE TRADING REPORTS")
    print("="*60)

    # Generate performance report
    perf_report = generate_performance_report()

    # Generate trade analysis
    analysis_report = generate_trade_analysis()

    # Generate strategy performance analytics
    performance_tracker.print_performance_summary()

    print("\n✅ Report update complete!")
    print("📁 Check performance_report.csv and trade_analysis.csv for updated data.")
    return perf_report, analysis_report

# =============================================================================
# STRATEGY FUSION FUNCTION
# =============================================================================

def fuse_strategy_signals(base_signal, enhanced_signal, adaptive_signal, df, institutional_signal=None):
    """
    Intelligent fusion of signals from multiple strategy systems including institutional analysis
    Chooses the best signal based on market conditions, confidence levels, and institutional factors
    """
    log_message("🧠 INSTITUTIONAL STRATEGY FUSION - Analyzing all signal sources:")

    signals = [
        ('Base Strategy', base_signal),
        ('Enhanced Strategy', enhanced_signal),
        ('Adaptive Strategy', adaptive_signal)
    ]

    if institutional_signal:
        signals.append(('Institutional ML', institutional_signal))

    # Log all signals for transparency
    for name, sig in signals:
        action = sig.get('action', 'UNKNOWN')
        conf = sig.get('confidence', 0.0)
        reason = sig.get('reason', 'No reason')
        log_message(f"   {name}: {action} (conf: {conf:.3f}) - {reason}")

    # Market condition analysis for signal selection
    current_price = df['close'].iloc[-1]
    volatility = df['close'].pct_change().rolling(20).std().iloc[-1]

    # Get regime information from adaptive strategy
    adaptive_mode = adaptive_signal.get('mode', 'neutral')

    # Get institutional regime analysis if available
    institutional_regime = None
    if institutional_signal and 'institutional_analysis' in institutional_signal:
        inst_analysis = institutional_signal['institutional_analysis']
        market_regime_data = inst_analysis.get('market_regime')
        if market_regime_data and isinstance(market_regime_data, dict):
            institutional_regime = market_regime_data.get('regime', 'Unknown')
        else:
            institutional_regime = 'Unknown'

    log_message(f"🔍 Market Context: Price=${current_price:.2f}, Vol={volatility:.4f}")
    log_message(f"   Adaptive Mode: {adaptive_mode}, Institutional Regime: {institutional_regime}")

    # Strategy selection logic enhanced with institutional analysis
    selected_signal = None
    selection_reason = ""

    # 1. Institutional signal takes priority if high confidence and regime-aligned
    if (institutional_signal and institutional_signal.get('confidence', 0) > 0.7 and
        institutional_signal.get('risk_score') != 'HIGH'):
        selected_signal = institutional_signal
        selection_reason = f"High-confidence institutional signal (regime: {institutional_regime})"

    # 2. High confidence adaptive signal in trending markets
    elif (adaptive_signal.get('confidence', 0) > 0.6 and
          adaptive_mode in ['trend_following', 'mean_reversion']):
        selected_signal = adaptive_signal
        selection_reason = f"High-confidence adaptive signal in {adaptive_mode} mode"

    # 3. Enhanced strategy in normal market conditions
    elif enhanced_signal.get('confidence', 0) > 0.5 and volatility < 0.03:
        selected_signal = enhanced_signal
        selection_reason = "Enhanced strategy for stable market conditions"

    # 4. Base strategy as reliable fallback
    elif base_signal.get('confidence', 0) > 0.45:
        selected_signal = base_signal
        selection_reason = "Base strategy as reliable fallback"

    # 5. Consensus voting if no clear winner
    else:
        # Count votes from all strategies
        buy_votes = sum(1 for _, sig in signals if sig.get('action') == 'BUY')
        sell_votes = sum(1 for _, sig in signals if sig.get('action') == 'SELL')

        if buy_votes >= 2:
            # Use the highest confidence BUY signal
            buy_signals = [(name, sig) for name, sig in signals if sig.get('action') == 'BUY']
            selected_signal = max(buy_signals, key=lambda x: x[1].get('confidence', 0))[1]
            selection_reason = f"Consensus BUY ({buy_votes}/{len(signals)} strategies agree)"
        elif sell_votes >= 2:
            # Use the highest confidence SELL signal
            sell_signals = [(name, sig) for name, sig in signals if sig.get('action') == 'SELL']
            selected_signal = max(sell_signals, key=lambda x: x[1].get('confidence', 0))[1]
            selection_reason = f"Consensus SELL ({sell_votes}/{len(signals)} strategies agree)"
        else:
            # Default to HOLD with enhanced structure
            selected_signal = {
                'action': 'HOLD',
                'confidence': 0.3,
                'reason': 'No clear consensus among strategies',
                'vote_count': {'BUY': buy_votes, 'SELL': sell_votes, 'HOLD': len(signals) - buy_votes - sell_votes},
                'individual_signals': {}
            }
            selection_reason = "No consensus - defaulting to HOLD"

    # Enhance selected signal with fusion metadata and institutional analysis
    if selected_signal:
        # Ensure vote_count exists in the signal
        if 'vote_count' not in selected_signal:
            buy_votes = sum(1 for _, sig in signals if sig.get('action') == 'BUY')
            sell_votes = sum(1 for _, sig in signals if sig.get('action') == 'SELL')
            hold_votes = sum(1 for _, sig in signals if sig.get('action') == 'HOLD')
            selected_signal['vote_count'] = {'BUY': buy_votes, 'SELL': sell_votes, 'HOLD': hold_votes}

        # Add fusion metadata
        selected_signal['fusion_info'] = {
            'selection_reason': selection_reason,
            'adaptive_mode': adaptive_mode,
            'all_signals': {name: {'action': sig.get('action'), 'confidence': sig.get('confidence', 0)}
                           for name, sig in signals},
            'market_volatility': volatility,
            'institutional_regime': institutional_regime
        }

        # Inherit institutional analysis if available
        if institutional_signal and 'institutional_analysis' in institutional_signal:
            selected_signal['institutional_analysis'] = institutional_signal['institutional_analysis']
            selected_signal['risk_score'] = institutional_signal.get('risk_score', 'MEDIUM')

        # Apply institutional risk overlay
        if institutional_signal:
            risk_score = institutional_signal.get('risk_score', 'MEDIUM')
            if risk_score == 'HIGH':
                selected_signal['confidence'] *= 0.7  # Reduce confidence in high-risk environment
                selected_signal['reason'] += ' | Risk-adjusted for high VaR environment'

    log_message(f"📊 INSTITUTIONAL FUSION RESULT: {selected_signal.get('action')} - {selection_reason}")

    # Validate and enhance the final signal
    selected_signal = validate_and_enhance_signal(selected_signal)

    return selected_signal

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
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":
    try:
        print("🚀 Starting INSTITUTIONAL-GRADE BTC Trading Bot...")
        print("🏛️ Features: Hedge Fund Strategies, Machine Learning, Kelly Criterion, VaR Risk Management")
        print("📊 Strategies: Enhanced RSI, Bollinger Bands, Mean Reversion, VWAP + ML Ensemble")
        print("🧠 Institutional: Market Regime Detection, Cross-Asset Correlation, Kelly Sizing")
        print("⚖️ Risk Management: Value-at-Risk, Hurst Exponent, Statistical Arbitrage Signals")
        print("💡 NEW: Percentage-Based Position Sizing for Scalable Growth")

        # Display configuration info
        trading_config = optimized_config['trading']
        if trading_config.get('position_sizing_mode') == 'percentage':
            print(f"💰 Position Sizing: {trading_config['base_position_pct']:.1%} of portfolio ({trading_config['min_position_pct']:.1%}-{trading_config['max_position_pct']:.1%} range)")
        else:
            print(f"💰 Position Sizing: Fixed ${trading_config['base_amount_usd']} per trade")

        print(f"⏰ Trade Cooldown: {min_trade_interval//60} minutes | Stop Loss: {stop_loss_percentage:.1%} | Take Profit: {take_profit_percentage:.1%}")
        print(f"🔧 Confidence Threshold: {optimized_config['strategy_parameters']['confidence_threshold']:.3f} | Institutional Auto-Optimization: ENABLED")
        print("💡 Press Ctrl+C to stop and generate reports")
        print("="*70)

        # Test connection and start trading
        test_connection()
        run_continuously()

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
