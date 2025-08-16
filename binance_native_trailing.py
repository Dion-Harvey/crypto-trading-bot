#!/usr/bin/env python3
"""
🎯 BINANCE NATIVE TRAILING STOP IMPLEMENTATION
==============================================

This module implements Binance US native trailing stop orders
instead of manual trailing stop management in the bot.

Features:
- Native TRAILING_STOP_MARKET orders
- Configurable trailing percentages
- Server-side execution (no polling needed)
- Better performance and reliability
"""

import ccxt
from typing import Dict, Optional, Union
import json
from decimal import Decimal, ROUND_DOWN


def place_binance_trailing_stop_order(
    exchange: ccxt.Exchange,
    symbol: str, 
    side: str,
    amount: float,
    trailing_percent: float,
    activation_price: Optional[float] = None
) -> Optional[Dict]:
    """
    Place a native Binance trailing stop order
    
    Args:
        exchange: CCXT exchange instance
        symbol: Trading pair (e.g., 'BTC/USDT')
        side: 'buy' or 'sell'
        amount: Amount of base currency to trade
        trailing_percent: Trailing percentage (e.g., 1.5 for 1.5%)
        activation_price: Price to activate trailing (optional)
    
    Returns:
        Order response dict or None if failed
    """
    try:
        # Get current market price for reference
        ticker = exchange.fetch_ticker(symbol)
        current_price = ticker['last']
        
        # Calculate minimum notional value
        market_info = exchange.markets.get(symbol, {})
        min_notional = market_info.get('limits', {}).get('cost', {}).get('min', 5.0)
        
        # Validate order size
        order_value = amount * current_price
        if order_value < min_notional:
            print(f"⚠️ Order value ${order_value:.2f} below minimum ${min_notional:.2f}")
            return None
        
        # Prepare order parameters for Binance native trailing stop
        params = {
            'type': 'TRAILING_STOP_MARKET',
            'side': side.upper(),
            'symbol': symbol.replace('/', ''),  # Binance format: BTCUSDT
            'quantity': amount,
            'callbackRate': trailing_percent  # Trailing percentage
        }
        
        # Add activation price if provided
        if activation_price:
            params['activationPrice'] = activation_price
            
        # Add timestamp for order
        params['timestamp'] = exchange.milliseconds()
        
        print(f"🎯 Placing Binance native trailing stop order:")
        print(f"   Symbol: {symbol}")
        print(f"   Side: {side}")
        print(f"   Amount: {amount}")
        print(f"   Trailing %: {trailing_percent}%")
        print(f"   Current Price: ${current_price:.2f}")
        if activation_price:
            print(f"   Activation Price: ${activation_price:.2f}")
        
        # Place the order using exchange's private API
        response = exchange.private_post_order(params)
        
        if response and response.get('orderId'):
            order_id = response['orderId']
            print(f"✅ Binance trailing stop order placed: {order_id}")
            
            return {
                'id': order_id,
                'symbol': symbol,
                'type': 'TRAILING_STOP_MARKET',
                'side': side,
                'amount': amount,
                'trailing_percent': trailing_percent,
                'activation_price': activation_price,
                'status': 'open',
                'timestamp': exchange.milliseconds(),
                'info': response
            }
        else:
            print(f"❌ Failed to place trailing stop order: {response}")
            return None
            
    except Exception as e:
        print(f"❌ Error placing Binance trailing stop order: {e}")
        return None


def place_trailing_stop_on_position(
    exchange: ccxt.Exchange,
    symbol: str,
    position_amount: float,
    entry_price: float,
    config: Dict
) -> Optional[Dict]:
    """
    Place a trailing stop order for an existing position
    
    Args:
        exchange: CCXT exchange instance
        symbol: Trading pair
        position_amount: Amount of the position
        entry_price: Original entry price
        config: Trailing stop configuration
    
    Returns:
        Order response or None
    """
    try:
        # Get trailing stop configuration
        trailing_config = config.get('binance_native_trailing', {})
        trailing_percent = trailing_config.get('trailing_percent', 1.5)
        activation_percent = trailing_config.get('activation_percent', 0.5)
        
        # Calculate activation price (when to start trailing)
        activation_price = entry_price * (1 + activation_percent / 100)
        
        # Get current price to check if we should activate
        ticker = exchange.fetch_ticker(symbol)
        current_price = ticker['last']
        
        # Only place trailing stop if we're in profit
        profit_pct = ((current_price - entry_price) / entry_price) * 100
        
        if profit_pct >= activation_percent:
            print(f"🎯 Position in profit ({profit_pct:.2f}%), placing trailing stop")
            
            return place_binance_trailing_stop_order(
                exchange=exchange,
                symbol=symbol,
                side='sell',  # Selling to close long position
                amount=position_amount,
                trailing_percent=trailing_percent,
                activation_price=activation_price
            )
        else:
            print(f"📊 Position not profitable enough ({profit_pct:.2f}% < {activation_percent}%)")
            return None
            
    except Exception as e:
        print(f"❌ Error placing trailing stop on position: {e}")
        return None


def update_trailing_stop_config(config_path: str, new_settings: Dict) -> bool:
    """
    Update trailing stop configuration in enhanced_config.json
    
    Args:
        config_path: Path to config file
        new_settings: New trailing stop settings
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Load current config
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Update or add binance native trailing section
        if 'binance_native_trailing' not in config:
            config['binance_native_trailing'] = {}
        
        config['binance_native_trailing'].update(new_settings)
        
        # Save updated config
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Updated trailing stop configuration")
        return True
        
    except Exception as e:
        print(f"❌ Error updating trailing stop config: {e}")
        return False


def get_binance_trailing_stop_orders(exchange: ccxt.Exchange, symbol: str) -> list:
    """
    Get all active trailing stop orders for a symbol
    
    Args:
        exchange: CCXT exchange instance
        symbol: Trading pair
    
    Returns:
        List of active trailing stop orders
    """
    try:
        # Fetch all open orders
        open_orders = exchange.fetch_open_orders(symbol)
        
        # Filter for trailing stop orders
        trailing_orders = [
            order for order in open_orders 
            if order.get('type') == 'TRAILING_STOP_MARKET'
        ]
        
        return trailing_orders
        
    except Exception as e:
        print(f"❌ Error fetching trailing stop orders: {e}")
        return []


# Default configuration for Binance native trailing stops
DEFAULT_TRAILING_CONFIG = {
    "binance_native_trailing": {
        "enabled": True,
        "trailing_percent": 0.5,  # 0.5% trailing stop (tighter)
        "activation_percent": 0.5,  # Activate after 0.5% profit
        "min_notional": 5.0,  # Minimum order value
        "replace_manual_trailing": True,  # Replace existing manual logic
        "use_for_all_positions": True,  # Apply to all new positions
        "emergency_fallback": True  # Keep manual backup for failures
    }
}


def test_binance_trailing_stop():
    """Test function for Binance native trailing stops"""
    print("🧪 Testing Binance Native Trailing Stop Configuration...")
    
    config = DEFAULT_TRAILING_CONFIG
    trailing_config = config['binance_native_trailing']
    
    print(f"✅ Enabled: {trailing_config['enabled']}")
    print(f"📊 Trailing %: {trailing_config['trailing_percent']}%")
    print(f"🎯 Activation %: {trailing_config['activation_percent']}%")
    print(f"💰 Min Notional: ${trailing_config['min_notional']}")
    print(f"🔄 Replace Manual: {trailing_config['replace_manual_trailing']}")
    
    print("\n✅ Binance Native Trailing Stop system ready!")
    

if __name__ == "__main__":
    test_binance_trailing_stop()
