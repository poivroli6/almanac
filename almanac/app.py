"""
Main Dash Application

Entry point for the Almanac Futures application with caching and modular structure.
"""

import dash
from dash import dcc, html
from flask_caching import Cache
import os

# Initialize Dash app
app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    title="Almanac Futures - Intraday Analysis"
)

# Configure Flask-Caching
cache_config = {
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': os.path.join(os.path.dirname(__file__), '..', '.cache'),
    'CACHE_DEFAULT_TIMEOUT': 3600,  # 1 hour
    'CACHE_THRESHOLD': 500  # Maximum number of items
}

cache = Cache()
cache.init_app(app.server, config=cache_config)

# Import and register page callbacks
from .pages.profile import create_profile_layout, register_profile_callbacks

# Create layout
app.layout = create_profile_layout()

# Register callbacks
register_profile_callbacks(app, cache)


def run_server(host='127.0.0.1', port=8085, debug=True):
    """
    Run the Dash application server.
    
    Args:
        host: Host address
        port: Port number
        debug: Whether to run in debug mode
    """
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    run_server()

