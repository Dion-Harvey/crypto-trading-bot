#!/usr/bin/env python3
print("🧪 Testing AWS Bot Configuration...")

try:
    import enhanced_config
    print("✅ enhanced_config imported successfully")
    
    config = enhanced_config.BotConfig()
    print("✅ BotConfig created successfully")
    
    validation = config.validate_config()
    print(f"✅ Config validation: {validation}")
    
    api_config = config.get_api_config()
    api_configured = bool(api_config.get('api_key'))
    print(f"🔑 API configured: {api_configured}")
    
    if api_configured:
        print("🎯 AWS bot is ready to trade!")
    else:
        print("⚠️ Please configure API keys in enhanced_config.json")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
