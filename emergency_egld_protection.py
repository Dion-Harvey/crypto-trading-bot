#!/usr/bin/env python3
"""
🚨 EMERGENCY EGLD POSITION PROTECTION
Places immediate stop-loss protection for EGLD/USDT position
"""
import os
import sys
from dotenv import load_dotenv
from binance.client import Client
from decimal import Decimal, ROUND_DOWN
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def get_binance_client():
    """Initialize Binance client"""
    load_dotenv()
    api_key = os.getenv('BINANCE_API_KEY')
    api_secret = os.getenv('BINANCE_API_SECRET')
    
    if not api_key or not api_secret:
        logger.error("❌ Binance API credentials not found in .env file")
        return None
    
    try:
        client = Client(api_key, api_secret, testnet=False)
        # Test connection
        client.ping()
        logger.info("✅ Connected to Binance US")
        return client
    except Exception as e:
        logger.error(f"❌ Failed to connect to Binance: {e}")
        return None

def get_position_info(client, symbol='EGLDUSDT'):
    """Get current EGLD position and price"""
    try:
        # Get account balance
        account = client.get_account()
        egld_balance = 0
        
        for asset in account['balances']:
            if asset['asset'] == 'EGLD':
                free_balance = float(asset['free'])
                locked_balance = float(asset['locked'])
                egld_balance = free_balance + locked_balance
                logger.info(f"💰 EGLD Balance: {egld_balance:.6f} (Free: {free_balance:.6f}, Locked: {locked_balance:.6f})")
                break
        
        if egld_balance <= 0:
            logger.warning("⚠️ No EGLD position found")
            return None, None, None
        
        # Get current price
        ticker = client.get_symbol_ticker(symbol=symbol)
        current_price = float(ticker['price'])
        logger.info(f"📊 Current EGLD Price: ${current_price:.4f}")
        
        # Check existing orders
        open_orders = client.get_open_orders(symbol=symbol)
        logger.info(f"📋 Existing open orders: {len(open_orders)}")
        
        for order in open_orders:
            logger.info(f"  📄 {order['side']} {order['type']} - Price: ${float(order['price']):.4f}, Qty: {float(order['origQty']):.6f}")
        
        return egld_balance, current_price, open_orders
        
    except Exception as e:
        logger.error(f"❌ Error getting position info: {e}")
        return None, None, None

def place_stop_loss_protection(client, symbol, quantity, current_price, stop_loss_pct=0.5):
    """Place stop-loss order for EGLD position"""
    try:
        # Calculate stop price (0.5% below current price)
        stop_price = current_price * (1 - stop_loss_pct / 100)
        limit_price = stop_price * 0.995  # Slightly below stop price
        
        logger.info(f"🎯 Stop Loss Setup:")
        logger.info(f"   Current Price: ${current_price:.4f}")
        logger.info(f"   Stop Price: ${stop_price:.4f} (-{stop_loss_pct}%)")
        logger.info(f"   Limit Price: ${limit_price:.4f}")
        logger.info(f"   Quantity: {quantity:.6f} EGLD")
        
        # Get symbol info for precision
        info = client.get_symbol_info(symbol)
        price_filter = next(f for f in info['filters'] if f['filterType'] == 'PRICE_FILTER')
        lot_size_filter = next(f for f in info['filters'] if f['filterType'] == 'LOT_SIZE')
        
        # Round to proper precision
        price_precision = len(price_filter['tickSize'].rstrip('0').split('.')[-1]) if '.' in price_filter['tickSize'] else 0
        qty_precision = len(lot_size_filter['stepSize'].rstrip('0').split('.')[-1]) if '.' in lot_size_filter['stepSize'] else 0
        
        stop_price_rounded = round(stop_price, price_precision)
        limit_price_rounded = round(limit_price, price_precision)
        quantity_rounded = round(quantity, qty_precision)
        
        logger.info(f"🔧 Rounded values:")
        logger.info(f"   Stop Price: ${stop_price_rounded}")
        logger.info(f"   Limit Price: ${limit_price_rounded}")
        logger.info(f"   Quantity: {quantity_rounded}")
        
        # Place STOP_LOSS_LIMIT order
        order = client.order_limit_sell(
            symbol=symbol,
            quantity=quantity_rounded,
            price=str(limit_price_rounded),
            timeInForce='GTC'
        )
        
        logger.info(f"✅ EMERGENCY STOP LOSS PLACED!")
        logger.info(f"   Order ID: {order['orderId']}")
        logger.info(f"   Symbol: {order['symbol']}")
        logger.info(f"   Side: {order['side']}")
        logger.info(f"   Type: {order['type']}")
        logger.info(f"   Price: ${float(order['price']):.4f}")
        logger.info(f"   Quantity: {float(order['origQty']):.6f}")
        
        return order
        
    except Exception as e:
        logger.error(f"❌ Failed to place stop loss: {e}")
        
        # Try regular limit sell order as backup
        try:
            logger.info("🔄 Attempting backup limit order...")
            backup_price = current_price * 0.995  # 0.5% below current
            backup_price_rounded = round(backup_price, price_precision)
            
            order = client.order_limit_sell(
                symbol=symbol,
                quantity=quantity_rounded,
                price=str(backup_price_rounded),
                timeInForce='GTC'
            )
            
            logger.info(f"✅ BACKUP LIMIT ORDER PLACED!")
            logger.info(f"   Order ID: {order['orderId']}")
            logger.info(f"   Price: ${float(order['price']):.4f}")
            return order
            
        except Exception as backup_e:
            logger.error(f"❌ Backup order also failed: {backup_e}")
            return None

def main():
    """Main protection function"""
    logger.info("🚨 EMERGENCY EGLD PROTECTION SCRIPT")
    logger.info("=" * 50)
    
    # Get Binance client
    client = get_binance_client()
    if not client:
        return False
    
    # Get position info
    balance, current_price, open_orders = get_position_info(client)
    if not balance or balance <= 0:
        logger.warning("⚠️ No EGLD position to protect")
        return False
    
    # Check if stop loss already exists
    existing_stop_loss = False
    for order in open_orders:
        if order['side'] == 'SELL' and order['type'] in ['STOP_LOSS_LIMIT', 'LIMIT']:
            existing_stop_loss = True
            logger.info(f"✅ Existing protection found: {order['type']} @ ${float(order['price']):.4f}")
            break
    
    if existing_stop_loss:
        logger.info("🛡️ Position already protected - no action needed")
        return True
    
    # Place emergency protection
    logger.info("🚨 NO PROTECTION FOUND - PLACING EMERGENCY STOP LOSS")
    
    # Use 99% of free balance to account for any locked amounts
    account = client.get_account()
    free_egld = 0
    for asset in account['balances']:
        if asset['asset'] == 'EGLD':
            free_egld = float(asset['free'])
            break
    
    if free_egld > 0:
        # Use slightly less than free balance to avoid precision issues
        protect_quantity = free_egld * 0.999
        order = place_stop_loss_protection(client, 'EGLDUSDT', protect_quantity, current_price)
        
        if order:
            logger.info("🎉 EMERGENCY PROTECTION SUCCESSFUL!")
            return True
        else:
            logger.error("❌ FAILED TO PLACE PROTECTION - MANUAL INTERVENTION REQUIRED")
            return False
    else:
        logger.warning("⚠️ No free EGLD balance available for protection")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ EGLD POSITION PROTECTION COMPLETE")
    else:
        print("\n❌ FAILED TO PROTECT EGLD POSITION")
        sys.exit(1)
