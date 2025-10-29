"""
Simple Dash Application

Entry point for the Almanac Futures application without complex production infrastructure.
"""

import dash
from dash import dcc, html
import os

# Initialize Dash app
app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    title="Almanac Futures - Intraday Analysis"
)

# Import and register page callbacks
from .pages.profile import create_profile_layout, register_profile_callbacks

# Create layout
app.layout = create_profile_layout()

# Simple caching setup (after app is created)
try:
    from flask_caching import Cache
    cache = Cache(app.server, config={
        'CACHE_TYPE': 'simple',
        'CACHE_DEFAULT_TIMEOUT': 300
    })
except ImportError:
    # Fallback if flask-caching not available
    class SimpleCache:
        def memoize(self, timeout=None):
            def decorator(func):
                return func
            return decorator
    cache = SimpleCache()

# Register callbacks
register_profile_callbacks(app, cache)

# Setup logging (simple version)
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("Almanac Futures started in simple mode")


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
