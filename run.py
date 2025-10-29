"""
Almanac Futures - Application Launcher

Simple entry point to run the Dash application.

Usage:
    python run.py
    
    # Or with custom settings:
    python run.py --port 8086 --debug
"""

import argparse
import logging
import os
from datetime import datetime
from almanac.app import run_server
from almanac.config import get_config


def setup_logging():
    """
    Set up logging configuration with both console and file output.
    Creates logs directory if it doesn't exist.
    """
    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(os.path.dirname(__file__), 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    
    # Generate log filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_filename = os.path.join(logs_dir, f'almanac_{timestamp}.log')
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler()  # Console output
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f"Logging initialized. Log file: {log_filename}")
    return logger


def main():
    # Set up logging first
    logger = setup_logging()
    
    cfg = get_config()
    
    parser = argparse.ArgumentParser(description='Almanac Futures Application')
    parser.add_argument('--host', default=cfg.host, help=f'Host address (default: {cfg.host})')
    parser.add_argument('--port', type=int, default=cfg.port, help=f'Port number (default: {cfg.port})')
    parser.add_argument('--no-debug', dest='debug', action='store_false', help='Disable debug mode')
    parser.set_defaults(debug=cfg.debug)
    
    args = parser.parse_args()
    
    # Log startup information
    logger.info(f"Starting Almanac Futures on http://{args.host}:{args.port}")
    logger.info(f"Debug mode: {'ON' if args.debug else 'OFF'}")
    
    # Keep console output for user interaction
    print(f"Starting Almanac Futures on http://{args.host}:{args.port}")
    print(f"Debug mode: {'ON' if args.debug else 'OFF'}")
    print("\nPress Ctrl+C to stop the server.")
    
    try:
        run_server(host=args.host, port=args.port, debug=args.debug)
    except KeyboardInterrupt:
        logger.info("Server stopped by user (Ctrl+C)")
        print("\nServer stopped.")
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        raise


if __name__ == '__main__':
    main()

