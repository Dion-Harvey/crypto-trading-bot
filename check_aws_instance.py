#!/usr/bin/env python3
"""
🔍 AWS Instance Status Checker
Check if your AWS instance is running and accessible
"""

import subprocess
import time

def check_instance_ping():
    """Check if instance responds to ping"""
    print("🔍 CHECKING AWS INSTANCE STATUS")
    print("=" * 40)
    
    aws_ip = "3.135.216.32"
    
    print(f"📡 Pinging {aws_ip}...")
    try:
        # Use ping command (works on Windows)
        result = subprocess.run(
            ['ping', '-n', '4', aws_ip], 
            capture_output=True, 
            text=True, 
            timeout=30
        )
        
        if result.returncode == 0:
            print("✅ Instance responds to ping - Network connectivity OK")
            return True
        else:
            print("❌ Instance does not respond to ping")
            print("⚠️ This could mean:")
            print("   • Instance is stopped/terminated")
            print("   • Security group blocks ICMP")
            print("   • Network routing issues")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Ping timeout - Network or instance issues")
        return False
    except Exception as e:
        print(f"❌ Ping failed: {e}")
        return False

def check_ssh_port():
    """Check if SSH port is accessible"""
    print(f"\n🔌 CHECKING SSH PORT 22")
    print("=" * 30)
    
    aws_ip = "3.135.216.32"
    
    try:
        # Use telnet-like approach with PowerShell
        ps_command = f'Test-NetConnection -ComputerName {aws_ip} -Port 22 -InformationLevel Quiet'
        
        result = subprocess.run(
            ['powershell', '-Command', ps_command],
            capture_output=True,
            text=True,
            timeout=15
        )
        
        if "True" in result.stdout:
            print("✅ Port 22 is accessible - SSH service is likely running")
            return True
        else:
            print("❌ Port 22 is not accessible")
            print("⚠️ This could mean:")
            print("   • SSH service is not running")
            print("   • Security group blocks port 22")
            print("   • Instance firewall blocks SSH")
            return False
            
    except Exception as e:
        print(f"⚠️ Port check failed: {e}")
        return False

def check_key_file():
    """Check SSH key file"""
    print(f"\n🔑 CHECKING SSH KEY FILE")
    print("=" * 30)
    
    key_file = r"C:\Users\miste\Documents\cryptobot-key.pem"
    
    try:
        import os
        if os.path.exists(key_file):
            size = os.path.getsize(key_file)
            print(f"✅ Key file found: {key_file}")
            print(f"📄 File size: {size} bytes")
            
            if size < 100:
                print("⚠️ Key file seems too small - may be corrupted")
                return False
            else:
                print("✅ Key file size looks normal")
                return True
        else:
            print(f"❌ Key file not found: {key_file}")
            print("💡 Make sure the key file is in the correct location")
            return False
            
    except Exception as e:
        print(f"❌ Key file check failed: {e}")
        return False

def suggest_solutions():
    """Suggest solutions based on checks"""
    print(f"\n💡 TROUBLESHOOTING SOLUTIONS")
    print("=" * 35)
    
    print("🔧 Try these solutions in order:")
    print()
    print("1️⃣ **Check AWS Console:**")
    print("   • Go to EC2 Dashboard")
    print("   • Verify instance is 'running'")
    print("   • Check if IP address changed")
    print("   • Restart instance if stopped")
    print()
    print("2️⃣ **Check Security Group:**")
    print("   • Go to Security Groups in AWS")
    print("   • Ensure SSH (port 22) is open")
    print("   • Source: 0.0.0.0/0 or your IP")
    print()
    print("3️⃣ **Try Different Connection:**")
    print("   • Use different network (mobile hotspot)")
    print("   • Check if your ISP blocks AWS")
    print("   • Try from different location")
    print()
    print("4️⃣ **Alternative Access:**")
    print("   • Use AWS Session Manager")
    print("   • Connect via AWS Console")
    print("   • Create new instance if needed")

def main():
    """Run all checks"""
    print("🚀 AWS CONNECTION TROUBLESHOOTER")
    print("=" * 50)
    print(f"🕒 Check Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Run checks
    ping_ok = check_instance_ping()
    port_ok = check_ssh_port()
    key_ok = check_key_file()
    
    # Summary
    print(f"\n📊 DIAGNOSTIC SUMMARY")
    print("=" * 25)
    print(f"📡 Network Ping: {'✅ OK' if ping_ok else '❌ FAILED'}")
    print(f"🔌 SSH Port 22: {'✅ OPEN' if port_ok else '❌ BLOCKED'}")
    print(f"🔑 SSH Key File: {'✅ OK' if key_ok else '❌ ISSUE'}")
    
    if ping_ok and port_ok and key_ok:
        print("\n🎉 ALL CHECKS PASSED!")
        print("🔧 Connection should work - try again:")
        print('   ssh -i "C:\\Users\\miste\\Documents\\cryptobot-key.pem" ubuntu@3.135.216.32')
    else:
        print(f"\n⚠️ ISSUES DETECTED")
        suggest_solutions()

if __name__ == "__main__":
    main()
