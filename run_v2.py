"""
Simple launcher for V2 Almanac Futures
"""

if __name__ == '__main__':
    from v2almanac_app import run_server
    
    print("=" * 60)
    print("🚀 ALMANAC FUTURES V2 - CLEAN RESTART")
    print("=" * 60)
    print("📍 Starting on: http://127.0.0.1:8086")
    print("🔧 This is a simplified version with UI only")
    print("=" * 60)
    print("\nPress Ctrl+C to stop the server.")
    print("=" * 60)
    
    run_server(host='127.0.0.1', port=8086, debug=True)

