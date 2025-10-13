"""
Almanac Futures - Application Launcher

Simple entry point to run the Dash application.

Usage:
    python run.py
    
    # Or with custom settings:
    python run.py --port 8086 --debug
"""

import argparse
from almanac.app import run_server


def main():
    parser = argparse.ArgumentParser(description='Almanac Futures Application')
    parser.add_argument('--host', default='127.0.0.1', help='Host address (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=8085, help='Port number (default: 8085)')
    parser.add_argument('--no-debug', dest='debug', action='store_false', help='Disable debug mode')
    parser.set_defaults(debug=True)
    
    args = parser.parse_args()
    
    print(f"Starting Almanac Futures on http://{args.host}:{args.port}")
    print(f"Debug mode: {'ON' if args.debug else 'OFF'}")
    print("\nPress Ctrl+C to stop the server.")
    
    run_server(host=args.host, port=args.port, debug=args.debug)


if __name__ == '__main__':
    main()

