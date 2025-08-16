#!/usr/bin/env python3
"""
🔍 BINANCE US ORDER TYPE CHECKER
Check what order types are actually supported for ENJ and EGLD
"""

import ccxt
import json

# Load configuration
with open('enhanced_config.json', 'r') as f:
    config = json.load(f)

# Initialize exchange
exchange = ccxt.binanceus({
    'apiKey': config['api_keys']['binance']['api_key'],
    'secret': config['api_keys']['binance']['api_secret'],
    'sandbox': False,
    'enableRateLimit': True,
})

def check_order_types():
    """Check supported order types for specific symbols"""
    try:
        # Load markets to see supported order types
        markets = exchange.load_markets()
        
        symbols = ['ENJ/USDT', 'EGLD/USDT']
        
        for symbol in symbols:
            if symbol in markets:
                market = markets[symbol]
                print(f"\n🎯 {symbol} Order Support:")
                print(f"   Active: {market.get('active', 'N/A')}")
                print(f"   Order Types: {market.get('orders', 'N/A')}")
                print(f"   Type: {market.get('type', 'N/A')}")
                print(f"   Contract Size: {market.get('contractSize', 'N/A')}")
                print(f"   Limits: {market.get('limits', {})}")
                
                # Check specific order type support
                if 'orders' in market and market['orders']:
                    supported_orders = market['orders']
                    print(f"   📊 Supported Orders:")
                    for order_type in supported_orders:
                        print(f"      ✅ {order_type}")
            else:
                print(f"❌ {symbol} not found in markets")
        
        # Check exchange capabilities
        print(f"\n🏢 Exchange Capabilities:")
        print(f"   Has Stop Orders: {exchange.has.get('createStopOrder', False)}")
        print(f"   Has Stop Limit Orders: {exchange.has.get('createStopLimitOrder', False)}")
        print(f"   Has Trailing Stop Orders: {exchange.has.get('createTrailingStopOrder', False)}")
        
        # Check general order types
        print(f"\n📋 General Order Types Available:")
        if hasattr(exchange, 'options') and 'orderTypes' in exchange.options:
            for order_type in exchange.options['orderTypes']:
                print(f"   ✅ {order_type}")
        
    except Exception as e:
        print(f"❌ Error checking order types: {e}")

def test_order_creation():
    """Test different order type formats without actually placing them"""
    print(f"\n🧪 TESTING ORDER FORMATS (DRY RUN):")
    
    test_params = [
        {
            'name': 'STOP_LOSS_LIMIT',
            'type': 'STOP_LOSS_LIMIT',
            'params': {
                'stopPrice': '16.50',
                'timeInForce': 'GTC'
            }
        },
        {
            'name': 'STOP_LOSS',
            'type': 'STOP_LOSS',
            'params': {
                'stopPrice': '16.50',
                'timeInForce': 'GTC'
            }
        },
        {
            'name': 'TRAILING_STOP_MARKET with stopLoss',
            'type': 'TRAILING_STOP_MARKET',
            'params': {
                'callbackRate': '0.5',
                'timeInForce': 'GTC',
                'stopLoss': True  # Required parameter!
            }
        }
    ]
    
    for test in test_params:
        print(f"\n   🔍 Testing {test['name']}:")
        print(f"      Type: {test['type']}")
        print(f"      Params: {test['params']}")
        print(f"      Status: Format prepared (not executed)")

if __name__ == "__main__":
    print("🔍 BINANCE US ORDER TYPE ANALYSIS")
    print("=" * 50)
    
    check_order_types()
    test_order_creation()
    
    print(f"\n✅ Analysis complete - check results above")
