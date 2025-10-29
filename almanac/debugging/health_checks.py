"""
Health Check Endpoints for Almanac Futures

Provides comprehensive health monitoring and debugging endpoints.
"""

from flask import Blueprint, jsonify, request
from datetime import datetime
import logging
import os
import sys
import traceback

logger = logging.getLogger(__name__)

# Create blueprint for debug endpoints
debug_bp = Blueprint('debug', __name__, url_prefix='/debug')


@debug_bp.route('/health')
def debug_health():
    """Comprehensive health check endpoint."""
    try:
        from ..debugging import get_debug_system
        
        debug_system = get_debug_system()
        health_status = debug_system.get_debug_report()
        
        return jsonify({
            'status': 'success',
            'data': health_status,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@debug_bp.route('/callbacks')
def debug_callbacks():
    """Get detailed callback information."""
    try:
        from ..debugging import get_debug_system
        
        debug_system = get_debug_system()
        callback_stats = debug_system.monitor.get_callback_stats()
        
        return jsonify({
            'status': 'success',
            'data': callback_stats,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Callback debug failed: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@debug_bp.route('/validation')
def debug_validation():
    """Get validation report."""
    try:
        from ..debugging import get_debug_system
        
        debug_system = get_debug_system()
        validation_report = debug_system.validator.get_validation_report()
        
        return jsonify({
            'status': 'success',
            'data': validation_report,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Validation debug failed: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@debug_bp.route('/performance')
def debug_performance():
    """Get performance metrics."""
    try:
        from ..debugging import get_debug_system
        
        debug_system = get_debug_system()
        performance_data = debug_system.monitor.performance_history[-100:]  # Last 100 calls
        
        return jsonify({
            'status': 'success',
            'data': {
                'recent_calls': performance_data,
                'summary': debug_system.monitor._get_performance_summary()
            },
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Performance debug failed: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@debug_bp.route('/errors')
def debug_errors():
    """Get recent error history."""
    try:
        from ..debugging import get_debug_system
        
        debug_system = get_debug_system()
        error_history = debug_system.error_handler.error_history[-50:]  # Last 50 errors
        
        return jsonify({
            'status': 'success',
            'data': {
                'recent_errors': error_history,
                'error_count': len(error_history),
                'callback_error_counts': debug_system.monitor.error_count
            },
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error debug failed: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@debug_bp.route('/system')
def debug_system_info():
    """Get system information."""
    try:
        import psutil
        
        system_info = {
            'python_version': sys.version,
            'platform': sys.platform,
            'working_directory': os.getcwd(),
            'environment': dict(os.environ),
            'memory_usage': psutil.virtual_memory()._asdict(),
            'cpu_usage': psutil.cpu_percent(interval=1),
            'disk_usage': psutil.disk_usage('/')._asdict(),
            'process_info': {
                'pid': os.getpid(),
                'memory_percent': psutil.Process().memory_percent(),
                'cpu_percent': psutil.Process().cpu_percent()
            }
        }
        
        return jsonify({
            'status': 'success',
            'data': system_info,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"System debug failed: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@debug_bp.route('/test-callback/<callback_name>')
def test_callback(callback_name):
    """Test a specific callback with mock data."""
    try:
        from ..debugging import get_debug_system
        
        debug_system = get_debug_system()
        
        # This would need to be implemented based on your specific callback schemas
        # For now, return a placeholder response
        return jsonify({
            'status': 'success',
            'message': f'Callback {callback_name} test endpoint created',
            'note': 'Implementation needed for specific callback testing',
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Callback test failed: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@debug_bp.route('/clear-errors')
def clear_errors():
    """Clear error history (for testing)."""
    try:
        from ..debugging import get_debug_system
        
        debug_system = get_debug_system()
        debug_system.error_handler.error_history.clear()
        debug_system.monitor.error_count.clear()
        
        return jsonify({
            'status': 'success',
            'message': 'Error history cleared',
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Clear errors failed: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@debug_bp.route('/export-logs')
def export_logs():
    """Export debug logs."""
    try:
        import json
        
        from ..debugging import get_debug_system
        
        debug_system = get_debug_system()
        debug_report = debug_system.get_debug_report()
        
        # Save to file
        filename = f"debug_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(debug_report, f, indent=2)
        
        return jsonify({
            'status': 'success',
            'message': f'Debug logs exported to {filename}',
            'filename': filename,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Export logs failed: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


def register_debug_endpoints(app):
    """Register all debug endpoints with the Flask app."""
    app.register_blueprint(debug_bp)
    logger.info("[REGISTERED] Debug endpoints registered")
    
    # Add a simple status endpoint at root level
    @app.route('/status')
    def simple_status():
        """Simple status check."""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'debug_endpoints': [
                '/debug/health',
                '/debug/callbacks', 
                '/debug/validation',
                '/debug/performance',
                '/debug/errors',
                '/debug/system'
            ]
        })
