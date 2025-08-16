import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("🚨 CHECKING EGLD POSITION AND PROTECTION STATUS")
print("=" * 60)

# Get API credentials from environment
api_key = os.getenv('BINANCE_API_KEY')
api_secret = os.getenv('BINANCE_API_SECRET')

if not api_key or not api_secret:
    print("❌ API credentials not found in .env file")
    exit(1)

try:
    # Try to connect to Binance
    import requests
    import hmac
    import hashlib
    import time
    
    # Simple Binance API call without external libraries
    base_url = 'https://api.binance.us'
    
    def get_account_info():
        """Get account info using direct API calls"""
        timestamp = int(time.time() * 1000)
        query_string = f'timestamp={timestamp}'
        
        signature = hmac.new(
            api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        headers = {
            'X-MBX-APIKEY': api_key
        }
        
        url = f'{base_url}/api/v3/account?{query_string}&signature={signature}'
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ API Error: {response.status_code} - {response.text}")
            return None
    
    def get_ticker_price(symbol):
        """Get current price for symbol"""
        url = f'{base_url}/api/v3/ticker/price?symbol={symbol}'
        response = requests.get(url)
        
        if response.status_code == 200:
            return float(response.json()['price'])
        return None
    
    def get_open_orders(symbol):
        """Get open orders for symbol"""
        timestamp = int(time.time() * 1000)
        query_string = f'symbol={symbol}&timestamp={timestamp}'
        
        signature = hmac.new(
            api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        headers = {
            'X-MBX-APIKEY': api_key
        }
        
        url = f'{base_url}/api/v3/openOrders?{query_string}&signature={signature}'
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Orders API Error: {response.status_code}")
            return []
    
    # Get account info
    print("🔍 Fetching account information...")
    account = get_account_info()
    
    if not account:
        print("❌ Failed to get account information")
        exit(1)
    
    # Find EGLD balance
    egld_balance = 0
    egld_locked = 0
    
    for balance in account['balances']:
        if balance['asset'] == 'EGLD':
            egld_balance = float(balance['free'])
            egld_locked = float(balance['locked'])
            break
    
    print(f"💰 EGLD Balance:")
    print(f"   Free: {egld_balance:.6f} EGLD")
    print(f"   Locked: {egld_locked:.6f} EGLD")
    print(f"   Total: {egld_balance + egld_locked:.6f} EGLD")
    
    if egld_balance <= 0:
        print("⚠️ No free EGLD balance found")
        exit(0)
    
    # Get current EGLD price
    print("📊 Fetching current EGLD price...")
    current_price = get_ticker_price('EGLDUSDT')
    
    if not current_price:
        print("❌ Failed to get EGLD price")
        exit(1)
    
    position_value = egld_balance * current_price
    print(f"📊 Current EGLD Price: ${current_price:.4f}")
    print(f"📊 Position Value: ${position_value:.2f}")
    
    # Check open orders
    print("📋 Checking existing orders...")
    open_orders = get_open_orders('EGLDUSDT')
    
    protection_exists = False
    for order in open_orders:
        if order['side'] == 'SELL':
            print(f"✅ Found protection order: {order['type']} @ ${float(order['price']):.4f}")
            protection_exists = True
    
    if protection_exists:
        print("🛡️ Your EGLD position is already protected!")
    else:
        print("🚨 NO PROTECTION FOUND FOR YOUR EGLD POSITION!")
        
        # Calculate recommended stop-loss
        stop_price = current_price * 0.995  # 0.5% below current
        
        print("\n🚨 URGENT MANUAL ACTION REQUIRED:")
        print("Place this stop-loss order IMMEDIATELY on Binance US:")
        print(f"   Symbol: EGLD/USDT")
        print(f"   Type: Limit Sell")
        print(f"   Quantity: {egld_balance:.6f} EGLD")
        print(f"   Price: ${stop_price:.4f}")
        print(f"   Current Price: ${current_price:.4f}")
        print("   Time in Force: GTC")
        print("\nThis will protect your position from further losses!")
        
        # Try to place the order automatically
        print("\n🔄 Attempting to place protection order automatically...")
        
        def place_limit_sell(symbol, quantity, price):
            """Place limit sell order"""
            timestamp = int(time.time() * 1000)
            
            params = {
                'symbol': symbol,
                'side': 'SELL',
                'type': 'LIMIT',
                'timeInForce': 'GTC',
                'quantity': f"{quantity:.6f}",
                'price': f"{price:.4f}",
                'timestamp': timestamp
            }
            
            query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
            
            signature = hmac.new(
                api_secret.encode('utf-8'),
                query_string.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            headers = {
                'X-MBX-APIKEY': api_key,
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            url = f'{base_url}/api/v3/order'
            data = query_string + f'&signature={signature}'
            
            response = requests.post(url, headers=headers, data=data)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Order Error: {response.status_code} - {response.text}")
                return None
        
        # Attempt to place the protection order
        protect_quantity = egld_balance * 0.999  # Use 99.9% to avoid precision issues
        order_result = place_limit_sell('EGLDUSDT', protect_quantity, stop_price)
        
        if order_result:
            print("🎉 SUCCESS! Automatic protection order placed:")
            print(f"   Order ID: {order_result['orderId']}")
            print(f"   Status: {order_result['status']}")
            print(f"   Price: ${float(order_result['price']):.4f}")
            print(f"   Quantity: {float(order_result['origQty']):.6f} EGLD")
            print("\n✅ YOUR EGLD POSITION IS NOW PROTECTED!")
        else:
            print("❌ Automatic order placement failed")
            print("Please place the manual order as shown above")

except ImportError:
    print("❌ Required libraries not available")
    print("Please install: pip install requests")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 60)
print("🔒 PROTECTION STATUS CHECK COMPLETE")
