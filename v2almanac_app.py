"""
V2 Almanac Futures - Clean Restart
Main application file

A simplified, streamlined version built from scratch with:
- Clean architecture
- Minimal complexity
- Easy to debug
- Modern Dash practices
"""

import dash
from dash import Dash, html, dcc
import logging
from datetime import datetime

# Setup basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Dash app
app = Dash(
    __name__,
    suppress_callback_exceptions=True,
    title="Almanac Futures V2"
)

# Import layout
from v2almanac_layout import create_layout

# Create the app layout
app.layout = create_layout()

# Import and register callbacks
from v2almanac_callbacks import register_callbacks
register_callbacks(app)

def run_server(host='127.0.0.1', port=8086, debug=True):
    """Run the application server."""
    logger.info(f"🚀 Starting Almanac Futures V2")
    logger.info(f"📍 Running on: http://{host}:{port}")
    logger.info(f"🔧 Debug mode: {'ON' if debug else 'OFF'}")
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    run_server()

