"""
🎯 BINANCE NATIVE TRAILING STOP INTEGRATION
==========================================

This file contains the modified functions to integrate Binance native trailing stops
into the existing bot logic, replacing manual trailing stop management.
"""

def place_enhanced_order_with_native_trailing(symbol, side, amount_usd, use_limit=True):
    """
    Enhanced order placement with Binance native trailing stops
    
    This replaces the existing place_intelligent_order function to automatically
    set up native Binance trailing stops after successful buy orders.
    """
    try:
        # Import the binance native trailing module
        from binance_native_trailing import (
            place_binance_trailing_stop_order,
            place_trailing_stop_on_position
        )
        
        # Get configuration
        config = get_enhanced_config()
        risk_config = config.get('risk_management', {})
        trailing_config = risk_config.get('binance_native_trailing', {})
        
        # Place the initial order using existing logic
        order = place_intelligent_order(symbol, side, amount_usd, use_limit)
        
        if order and side.upper() == 'BUY' and trailing_config.get('enabled', False):
            # Extract order details
            final_price = order.get('average') or order.get('price', 0)
            crypto_purchased = order.get('filled', 0) or order.get('amount', 0)
            
            if crypto_purchased > 0 and final_price > 0:
                log_message(f"🎯 Setting up Binance native trailing stop for position...")
                
                # Calculate when to activate trailing stop
                trailing_percent = trailing_config.get('trailing_percent', 1.5)
                activation_percent = trailing_config.get('activation_percent', 0.5)
                
                # Get current price to check if we should place trailing stop immediately
                ticker = exchange.fetch_ticker(symbol)
                current_price = ticker['last']
                
                # Check if we're already in profit enough to activate trailing
                profit_pct = ((current_price - final_price) / final_price) * 100
                
                if profit_pct >= activation_percent:
                    # Place trailing stop immediately
                    trailing_order = place_binance_trailing_stop_order(
                        exchange=exchange,
                        symbol=symbol,
                        side='sell',
                        amount=crypto_purchased,
                        trailing_percent=trailing_percent,
                        activation_price=current_price
                    )
                    
                    if trailing_order:
                        log_message(f"✅ Binance native trailing stop placed:")
                        log_message(f"   📊 Trailing %: {trailing_percent}%")
                        log_message(f"   🎯 Order ID: {trailing_order['id']}")
                        log_message(f"   💰 Amount: {crypto_purchased:.6f}")
                        
                        # Store trailing stop info in trading state
                        trading_state = get_trading_state()
                        trading_state['binance_trailing_order_id'] = trailing_order['id']
                        trading_state['binance_trailing_percent'] = trailing_percent
                        trading_state['binance_trailing_activation'] = current_price
                        save_trading_state(trading_state)
                        
                        print(f"🎯 BINANCE NATIVE TRAILING STOP ACTIVE")
                        print(f"   📈 Trailing: {trailing_percent}% below highest price")
                        print(f"   🔄 Server-side execution (no bot monitoring needed)")
                        print(f"   ⚡ Better performance than manual trailing")
                        
                    else:
                        log_message("⚠️ Failed to place Binance native trailing stop - falling back to manual")
                        # Fallback to existing OCO/manual trailing logic if enabled
                        if trailing_config.get('emergency_fallback', True):
                            trailing_oco_order = place_trailing_oco_order(symbol, final_price, crypto_purchased, final_price)
                            if trailing_oco_order:
                                log_message("✅ Fallback OCO trailing stop placed")
                else:
                    log_message(f"📊 Position not profitable enough for trailing stop ({profit_pct:.2f}% < {activation_percent}%)")
                    log_message(f"   🔄 Will check for trailing stop activation in monitoring loop")
                    
                    # Store position info for later trailing stop placement
                    trading_state = get_trading_state()
                    trading_state['pending_trailing_stop'] = {
                        'symbol': symbol,
                        'amount': crypto_purchased,
                        'entry_price': final_price,
                        'activation_percent': activation_percent,
                        'trailing_percent': trailing_percent
                    }
                    save_trading_state(trading_state)
            else:
                log_message("❌ No valid position to protect with trailing stop")
        
        return order
        
    except Exception as e:
        log_message(f"❌ Error in enhanced order placement with native trailing: {e}")
        # Fallback to standard order placement
        return place_intelligent_order(symbol, side, amount_usd, use_limit)


def check_and_place_pending_trailing_stops():
    """
    Check if any positions are ready for trailing stop activation
    
    This function runs in the main bot loop to monitor positions that
    haven't reached profit threshold yet for trailing stop activation.
    """
    try:
        from binance_native_trailing import place_binance_trailing_stop_order
        
        trading_state = get_trading_state()
        pending_trailing = trading_state.get('pending_trailing_stop')
        
        if pending_trailing:
            symbol = pending_trailing['symbol']
            amount = pending_trailing['amount']
            entry_price = pending_trailing['entry_price']
            activation_percent = pending_trailing['activation_percent']
            trailing_percent = pending_trailing['trailing_percent']
            
            # Get current price
            ticker = exchange.fetch_ticker(symbol)
            current_price = ticker['last']
            
            # Check if we've reached activation threshold
            profit_pct = ((current_price - entry_price) / entry_price) * 100
            
            if profit_pct >= activation_percent:
                log_message(f"🎯 Position reached {profit_pct:.2f}% profit - activating trailing stop")
                
                # Place the Binance native trailing stop
                trailing_order = place_binance_trailing_stop_order(
                    exchange=exchange,
                    symbol=symbol,
                    side='sell',
                    amount=amount,
                    trailing_percent=trailing_percent,
                    activation_price=current_price
                )
                
                if trailing_order:
                    log_message(f"✅ Delayed Binance native trailing stop activated:")
                    log_message(f"   📊 Trailing %: {trailing_percent}%")
                    log_message(f"   🎯 Order ID: {trailing_order['id']}")
                    log_message(f"   💰 Profit at activation: {profit_pct:.2f}%")
                    
                    # Update trading state
                    trading_state['binance_trailing_order_id'] = trailing_order['id']
                    trading_state['binance_trailing_percent'] = trailing_percent
                    trading_state['binance_trailing_activation'] = current_price
                    del trading_state['pending_trailing_stop']  # Remove pending status
                    save_trading_state(trading_state)
                    
                    print(f"🎯 DELAYED TRAILING STOP NOW ACTIVE")
                    print(f"   ⏰ Activated after {profit_pct:.2f}% profit")
                    print(f"   📈 Trailing: {trailing_percent}% below highest price")
                    
                else:
                    log_message("⚠️ Failed to place delayed trailing stop")
                    
    except Exception as e:
        log_message(f"❌ Error checking pending trailing stops: {e}")


def replace_manual_trailing_logic():
    """
    This function would replace the manual trailing stop logic in assess_risk_action
    with a simple check for Binance native trailing stop status.
    """
    try:
        # Get configuration
        config = get_enhanced_config()
        risk_config = config.get('risk_management', {})
        trailing_config = risk_config.get('binance_native_trailing', {})
        
        # If Binance native trailing is enabled and we have an active order,
        # we don't need to do manual trailing stop checks
        if trailing_config.get('enabled', False):
            trading_state = get_trading_state()
            trailing_order_id = trading_state.get('binance_trailing_order_id')
            
            if trailing_order_id:
                # Check if the trailing stop order is still active
                try:
                    order_status = exchange.fetch_order(trailing_order_id)
                    if order_status['status'] in ['open', 'pending']:
                        # Trailing stop is active, no manual intervention needed
                        return None
                    elif order_status['status'] == 'closed':
                        # Trailing stop was triggered
                        log_message(f"🎯 Binance native trailing stop triggered: {trailing_order_id}")
                        # Clear the trailing stop from state
                        del trading_state['binance_trailing_order_id']
                        save_trading_state(trading_state)
                        return 'TRAILING_STOP_TRIGGERED'
                except:
                    # Order not found, might have been executed
                    log_message(f"⚠️ Trailing stop order {trailing_order_id} not found - may have executed")
        
        # If no native trailing stop or fallback is enabled, use manual logic
        if not trailing_config.get('enabled', False) or trailing_config.get('emergency_fallback', True):
            # Keep existing manual trailing stop logic as fallback
            return None  # Continue with manual logic
        
        return None
        
    except Exception as e:
        log_message(f"❌ Error in trailing stop replacement logic: {e}")
        return None


# Configuration update function
def update_config_for_native_trailing():
    """
    Update the enhanced_config.json to properly configure native trailing stops
    """
    config_updates = {
        "binance_native_trailing": {
            "enabled": True,
            "trailing_percent": 0.5,
            "activation_percent": 0.5,
            "min_notional": 5.0,
            "replace_manual_trailing": True,
            "use_for_all_positions": True,
            "emergency_fallback": True
        }
    }
    
    print("🔧 Configuration for Binance Native Trailing Stops:")
    print(f"   ✅ Enabled: {config_updates['binance_native_trailing']['enabled']}")
    print(f"   📊 Trailing %: {config_updates['binance_native_trailing']['trailing_percent']}%")
    print(f"   🎯 Activation %: {config_updates['binance_native_trailing']['activation_percent']}%")
    print(f"   🔄 Replace Manual: {config_updates['binance_native_trailing']['replace_manual_trailing']}")
    print(f"   🛡️ Emergency Fallback: {config_updates['binance_native_trailing']['emergency_fallback']}")
    
    return config_updates


def update_bot_config(config_dict):
    """
    Update bot configuration with new settings
    
    This function updates the enhanced_config.json file with new configuration
    settings, specifically for Phase 2 intelligence and native trailing stops.
    """
    import json
    import os
    from datetime import datetime
    
    try:
        config_file = 'enhanced_config.json'
        
        # Load existing config
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                current_config = json.load(f)
        else:
            current_config = {}
        
        # Backup current config
        backup_file = f"enhanced_config.json.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        with open(backup_file, 'w') as f:
            json.dump(current_config, f, indent=2)
        
        # Deep merge the new config
        def deep_merge(dict1, dict2):
            result = dict1.copy()
            for key, value in dict2.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = deep_merge(result[key], value)
                else:
                    result[key] = value
            return result
        
        # Merge configs
        updated_config = deep_merge(current_config, config_dict)
        
        # Add update timestamp
        updated_config['last_updated'] = datetime.now().isoformat()
        updated_config['config_version'] = updated_config.get('config_version', '1.0')
        
        # Save updated config
        with open(config_file, 'w') as f:
            json.dump(updated_config, f, indent=2)
        
        print(f"✅ Configuration updated successfully")
        print(f"   📁 Config file: {config_file}")
        print(f"   📋 Backup created: {backup_file}")
        print(f"   🔄 Updated keys: {list(config_dict.keys())}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating bot configuration: {e}")
        return False


if __name__ == "__main__":
    print("🎯 Binance Native Trailing Stop Integration Module")
    print("=" * 50)
    
    config = update_config_for_native_trailing()
    
    print("\n✅ Ready to integrate with main bot:")
    print("1. Replace place_intelligent_order calls with place_enhanced_order_with_native_trailing")
    print("2. Add check_and_place_pending_trailing_stops() to main bot loop")
    print("3. Update assess_risk_action to use replace_manual_trailing_logic()")
    print("4. Deploy binance_native_trailing.py to AWS")
    print("5. Test with small amounts first")
