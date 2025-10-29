#!/usr/bin/env python3
"""
TSLA Cache Setup Script

Quick setup script to initialize TSLA data caching.
"""

import os
import sys
import subprocess

def check_requirements():
    """Check if required packages are installed."""
    print("Checking requirements...")
    
    try:
        import alpaca
        print("✓ alpaca-py is installed")
        return True
    except ImportError:
        print("✗ alpaca-py is not installed")
        print("Install with: pip install alpaca-py>=0.20.0")
        return False

def check_credentials():
    """Check if API credentials are configured."""
    print("\nChecking API credentials...")
    
    api_key = os.getenv('ALPACA_API_KEY')
    secret_key = os.getenv('ALPACA_SECRET_KEY')
    
    if api_key and secret_key:
        print(f"✓ API Key: {api_key[:8]}...")
        print(f"✓ Secret Key: {secret_key[:8]}...")
        return True
    else:
        print("✗ API credentials not configured")
        print("Set environment variables:")
        print("  ALPACA_API_KEY=your_api_key")
        print("  ALPACA_SECRET_KEY=your_secret_key")
        return False

def setup_cache():
    """Set up the cache system."""
    print("\nSetting up TSLA cache...")
    
    try:
        # Run the cache manager
        result = subprocess.run([sys.executable, 'cache_tsla_data.py'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ TSLA cache setup successful!")
            print(result.stdout)
            return True
        else:
            print("✗ Cache setup failed:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"✗ Cache setup failed: {e}")
        return False

def check_cache_status():
    """Check the cache status."""
    print("\nChecking cache status...")
    
    try:
        result = subprocess.run([sys.executable, 'cache_tsla_data.py', '--status'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("Cache Status:")
            print(result.stdout)
            return True
        else:
            print("Failed to check cache status")
            return False
            
    except Exception as e:
        print(f"Failed to check cache status: {e}")
        return False

def main():
    """Main setup function."""
    print("TSLA Cache Setup")
    print("=" * 20)
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Setup failed: Missing requirements")
        return False
    
    # Check credentials
    if not check_credentials():
        print("\n❌ Setup failed: Missing API credentials")
        return False
    
    # Setup cache
    if not setup_cache():
        print("\n❌ Setup failed: Cache setup error")
        return False
    
    # Check status
    check_cache_status()
    
    print("\n🎉 TSLA cache setup complete!")
    print("\nNext steps:")
    print("1. TSLA data is now cached locally")
    print("2. You can use TSLA in the application")
    print("3. Run 'python cache_tsla_data.py' daily for fresh data")
    print("4. Check status with 'python cache_tsla_data.py --status'")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
