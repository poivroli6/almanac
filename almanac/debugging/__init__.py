"""
Comprehensive Debugging System for Almanac Futures

This module provides extensive debugging capabilities to prevent callback errors,
schema mismatches, and other common issues in Dash applications.
"""

import json
import time
import logging
import traceback
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional
from functools import wraps
import os

logger = logging.getLogger(__name__)


class CallbackMonitor:
    """Real-time monitoring of callback performance and errors."""
    
    def __init__(self):
        self.callback_stats = {}
        self.error_count = {}
        self.performance_history = []
        self.schema_registry = {}
    
    def log_callback_start(self, callback_name: str, inputs: List[Any]):
        """Log the start of a callback execution."""
        self.callback_stats[callback_name] = {
            'start_time': time.time(),
            'inputs': inputs,
            'status': 'running',
            'execution_count': self.callback_stats.get(callback_name, {}).get('execution_count', 0) + 1
        }
        logger.info(f"[START] Starting callback: {callback_name}")
        print(f"🔄 CALLBACK STARTED: {callback_name}")  # Visible terminal output
    
    def log_callback_end(self, callback_name: str, success: bool = True, outputs: Optional[List[Any]] = None, error: Optional[Exception] = None):
        """Log the end of a callback execution."""
        if callback_name in self.callback_stats:
            stats = self.callback_stats[callback_name]
            stats['end_time'] = time.time()
            stats['duration'] = stats['end_time'] - stats['start_time']
            stats['status'] = 'success' if success else 'error'
            stats['output_count'] = len(outputs) if outputs else 0
            
            if success:
                logger.info(f"[SUCCESS] Callback {callback_name} completed in {stats['duration']:.3f}s")
                print(f"✅ CALLBACK SUCCESS: {callback_name} completed in {stats['duration']:.3f}s")  # Visible terminal output
            else:
                logger.error(f"[ERROR] Callback {callback_name} failed after {stats['duration']:.3f}s")
                print(f"❌ CALLBACK ERROR: {callback_name} failed after {stats['duration']:.3f}s")  # Visible terminal output
                self.error_count[callback_name] = self.error_count.get(callback_name, 0) + 1
                if error:
                    stats['last_error'] = str(error)
                    stats['error_type'] = type(error).__name__
            
            # Store performance data
            self.performance_history.append({
                'callback_name': callback_name,
                'duration': stats['duration'],
                'success': success,
                'timestamp': datetime.now().isoformat(),
                'output_count': stats['output_count']
            })
    
    def get_callback_stats(self) -> Dict[str, Any]:
        """Get comprehensive callback statistics."""
        return {
            'callbacks': self.callback_stats,
            'error_counts': self.error_count,
            'performance_summary': self._get_performance_summary(),
            'schema_registry': self.schema_registry
        }
    
    def _get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary statistics."""
        if not self.performance_history:
            return {}
        
        recent_calls = self.performance_history[-100:]  # Last 100 calls
        
        avg_duration = sum(call['duration'] for call in recent_calls) / len(recent_calls)
        success_rate = sum(1 for call in recent_calls if call['success']) / len(recent_calls)
        
        return {
            'average_duration': avg_duration,
            'success_rate': success_rate,
            'total_calls': len(self.performance_history),
            'recent_calls': len(recent_calls)
        }


class CallbackValidator:
    """Validates callback schemas and return values."""
    
    def __init__(self, monitor: CallbackMonitor):
        self.monitor = monitor
        self.validation_errors = []
    
    def validate_callback_outputs(self, outputs: List[Any], return_values: List[Any], callback_name: str) -> bool:
        """Validate that callback outputs match return values."""
        expected_count = len(outputs)
        actual_count = len(return_values)
        
        if expected_count != actual_count:
            error_msg = f"CALLBACK SCHEMA MISMATCH in {callback_name}"
            error_details = {
                'callback_name': callback_name,
                'expected_count': expected_count,
                'actual_count': actual_count,
                'outputs': [str(o) for o in outputs],
                'return_types': [type(v).__name__ for v in return_values],
                'timestamp': datetime.now().isoformat()
            }
            
            logger.error(f"[SCHEMA_ERROR] {error_msg}")
            logger.error(f"   Expected: {expected_count} outputs")
            logger.error(f"   Received: {actual_count} values")
            logger.error(f"   Outputs: {error_details['outputs']}")
            logger.error(f"   Return types: {error_details['return_types']}")
            print(f"🚨 SCHEMA MISMATCH: {callback_name} - Expected {expected_count}, got {actual_count}")  # Visible terminal output
            
            self.validation_errors.append(error_details)
            return False
        
        logger.info(f"[VALIDATED] Callback {callback_name} schema validated: {actual_count} outputs")
        print(f"✅ SCHEMA VALID: {callback_name} - {actual_count} outputs")  # Visible terminal output
        return True
    
    def register_callback_schema(self, callback_name: str, outputs: List[Any], inputs: List[Any], states: List[Any] = None):
        """Register a callback schema for validation."""
        self.monitor.schema_registry[callback_name] = {
            'outputs': [str(o) for o in outputs],
            'inputs': [str(i) for i in inputs],
            'states': [str(s) for s in states] if states else [],
            'output_count': len(outputs),
            'input_count': len(inputs),
            'state_count': len(states) if states else 0,
            'registered_at': datetime.now().isoformat()
        }
        logger.info(f"[REGISTERED] Schema for {callback_name}: {len(outputs)} outputs, {len(inputs)} inputs")
    
    def get_validation_report(self) -> Dict[str, Any]:
        """Get a comprehensive validation report."""
        return {
            'validation_errors': self.validation_errors,
            'registered_schemas': len(self.monitor.schema_registry),
            'error_count': len(self.validation_errors),
            'last_error': self.validation_errors[-1] if self.validation_errors else None
        }


class DebugErrorHandler:
    """Enhanced error handling with comprehensive context."""
    
    def __init__(self, monitor: CallbackMonitor):
        self.monitor = monitor
        self.error_history = []
    
    def safe_callback_wrapper(self, callback_func):
        """Wrapper that adds comprehensive error handling to callbacks."""
        @wraps(callback_func)
        def wrapper(*args, **kwargs):
            callback_name = callback_func.__name__
            
            try:
                # Log callback start
                self.monitor.log_callback_start(callback_name, args)
                
                # Execute callback
                result = callback_func(*args, **kwargs)
                
                # Log successful completion
                self.monitor.log_callback_end(callback_name, success=True, outputs=result)
                
                logger.info(f"✅ Callback {callback_name} completed successfully")
                return result
                
            except Exception as e:
                # Log error with full context
                error_context = {
                    'callback_name': callback_name,
                    'error': str(e),
                    'error_type': type(e).__name__,
                    'args': [str(arg)[:100] for arg in args],  # Truncate long args
                    'kwargs': {k: str(v)[:100] for k, v in kwargs.items()},
                    'traceback': traceback.format_exc(),
                    'timestamp': datetime.now().isoformat()
                }
                
                self.error_history.append(error_context)
                self.monitor.log_callback_end(callback_name, success=False, error=e)
                
                logger.error(f"❌ Callback {callback_name} failed:")
                logger.error(f"   Error: {str(e)}")
                logger.error(f"   Type: {type(e).__name__}")
                logger.error(f"   Args count: {len(args)}")
                logger.error(f"   Kwargs: {list(kwargs.keys())}")
                
                # Return safe fallback values
                return self._get_safe_fallback_values(callback_name)
        
        return wrapper
    
    def _get_safe_fallback_values(self, callback_name: str) -> List[Any]:
        """Get safe fallback values for failed callbacks."""
        # This would need to be customized based on your specific callback schemas
        # For now, return a generic error message
        return [f"Error in {callback_name}: Callback failed"]


class SchemaDocumenter:
    """Generates comprehensive documentation of callback schemas."""
    
    def __init__(self, monitor: CallbackMonitor):
        self.monitor = monitor
    
    def document_callback_schema(self, app) -> Dict[str, Any]:
        """Generate documentation of all callback schemas."""
        schema_doc = {
            'generated_at': datetime.now().isoformat(),
            'app_name': getattr(app, 'name', 'Unknown'),
            'callbacks': {}
        }
        
        try:
            for callback_id, callback_info in app.callback_map.items():
                callback_name = callback_info['callback'].__name__
                outputs = callback_info.get('outputs', [])
                inputs = callback_info.get('inputs', [])
                states = callback_info.get('state', [])
                
                schema_doc['callbacks'][callback_name] = {
                    'callback_id': callback_id,
                    'outputs': [str(o) for o in outputs],
                    'inputs': [str(i) for i in inputs],
                    'states': [str(s) for s in states],
                    'output_count': len(outputs),
                    'input_count': len(inputs),
                    'state_count': len(states),
                    'total_parameters': len(outputs) + len(inputs) + len(states)
                }
            
            logger.info(f"[DOCUMENTED] {len(schema_doc['callbacks'])} callback schemas")
            
        except Exception as e:
            logger.error(f"[ERROR] Error documenting schemas: {e}")
            schema_doc['error'] = str(e)
        
        return schema_doc
    
    def save_schema_documentation(self, app, filename: str = 'callback_schemas.json'):
        """Save schema documentation to file."""
        schema_doc = self.document_callback_schema(app)
        
        try:
            with open(filename, 'w') as f:
                json.dump(schema_doc, f, indent=2)
            logger.info(f"[SAVED] Schema documentation saved to {filename}")
        except Exception as e:
            logger.error(f"[ERROR] Error saving schema documentation: {e}")


class HealthChecker:
    """Comprehensive health check system."""
    
    def __init__(self, monitor: CallbackMonitor, validator: CallbackValidator):
        self.monitor = monitor
        self.validator = validator
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status."""
        stats = self.monitor.get_callback_stats()
        validation_report = self.validator.get_validation_report()
        
        health_status = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'healthy',
            'callbacks': {
                'total_registered': len(self.monitor.schema_registry),
                'active_callbacks': len(self.monitor.callback_stats),
                'error_count': sum(self.monitor.error_count.values()),
                'success_rate': self._calculate_success_rate()
            },
            'validation': validation_report,
            'performance': stats.get('performance_summary', {}),
            'environment': {
                'debug_mode': os.getenv('FLASK_ENV') == 'development',
                'python_version': os.sys.version,
                'working_directory': os.getcwd()
            }
        }
        
        # Determine overall health
        if validation_report['error_count'] > 0:
            health_status['overall_status'] = 'degraded'
        if sum(self.monitor.error_count.values()) > 10:
            health_status['overall_status'] = 'unhealthy'
        
        return health_status
    
    def _calculate_success_rate(self) -> float:
        """Calculate overall success rate."""
        if not self.monitor.performance_history:
            return 1.0
        
        recent_calls = self.monitor.performance_history[-50:]  # Last 50 calls
        successful_calls = sum(1 for call in recent_calls if call['success'])
        return successful_calls / len(recent_calls) if recent_calls else 1.0


class DebuggingSystem:
    """Main debugging system that coordinates all components."""
    
    def __init__(self):
        self.monitor = CallbackMonitor()
        self.validator = CallbackValidator(self.monitor)
        self.error_handler = DebugErrorHandler(self.monitor)
        self.documenter = SchemaDocumenter(self.monitor)
        self.health_checker = HealthChecker(self.monitor, self.validator)
        
        # Setup enhanced logging
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup enhanced logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('debug.log')
            ]
        )
        
        # Add debug-specific logger
        debug_logger = logging.getLogger('debug')
        debug_logger.setLevel(logging.DEBUG)
    
    def setup_app_debugging(self, app):
        """Setup comprehensive debugging for a Dash app."""
        logger.info("[SETUP] Setting up comprehensive debugging system")
        
        # Add request logging
        from flask import request
        @app.server.before_request
        def log_request():
            logger.info(f"[REQUEST] {request.method} {request.path}")
            if request.path.startswith('/_dash-update-component'):
                print(f"🔄 BUTTON PRESSED: Processing callback request")  # Visible terminal output
        
        # Override callback registration
        self._override_callback_registration(app)
        
        # Generate initial schema documentation
        self.documenter.save_schema_documentation(app)
        
        logger.info("[COMPLETE] Debugging system setup complete")
    
    def _override_callback_registration(self, app):
        """Override Dash callback registration to add debugging."""
        original_callback = app.callback
        
        def debug_callback(outputs, inputs=None, state=None, **kwargs):
            callback_name = kwargs.get('name', 'unnamed')
            
            logger.info(f"[REGISTER] Registering callback: {callback_name}")
            logger.info(f"   Outputs: {len(outputs)}")
            logger.info(f"   Inputs: {len(inputs) if inputs else 0}")
            logger.info(f"   State: {len(state) if state else 0}")
            
            # Register schema
            self.validator.register_callback_schema(callback_name, outputs, inputs or [], state or [])
            
            # Wrap the callback function
            def wrapper(func):
                # Apply error handling wrapper
                wrapped_func = self.error_handler.safe_callback_wrapper(func)
                
                # Add validation wrapper
                @wraps(wrapped_func)
                def validation_wrapper(*args, **kwargs):
                    result = wrapped_func(*args, **kwargs)
                    
                    # Validate outputs
                    if not self.validator.validate_callback_outputs(outputs, result, callback_name):
                        logger.error(f"[VALIDATION_ERROR] Schema validation failed for {callback_name}")
                    
                    return result
                
                return validation_wrapper
            
            return original_callback(outputs, inputs, state, **kwargs)
        
        app.callback = debug_callback
    
    def get_debug_report(self) -> Dict[str, Any]:
        """Get comprehensive debug report."""
        return {
            'health_status': self.health_checker.get_health_status(),
            'callback_stats': self.monitor.get_callback_stats(),
            'validation_report': self.validator.get_validation_report(),
            'system_info': {
                'timestamp': datetime.now().isoformat(),
                'debug_system_version': '1.0.0',
                'components_active': [
                    'CallbackMonitor',
                    'CallbackValidator', 
                    'DebugErrorHandler',
                    'SchemaDocumenter',
                    'HealthChecker'
                ]
            }
        }


# Global debugging system instance
debug_system = DebuggingSystem()


def get_debug_system() -> DebuggingSystem:
    """Get the global debugging system instance."""
    return debug_system


def setup_debugging(app):
    """Quick setup function for debugging."""
    debug_system.setup_app_debugging(app)
    return debug_system


# Lightweight decorator to validate callback output counts
def validate_output_count(expected_count: int):
    """
    Decorator that validates a Dash callback returns the expected number of outputs.

    Args:
        expected_count: Number of outputs the callback is expected to return
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            # Normalize result to a list-like for counting
            if isinstance(result, (list, tuple)):
                values = list(result)
            elif result is None:
                values = []
            else:
                values = [result]

            actual_count = len(values)
            if actual_count != expected_count:
                logger.error("[OUTPUT_VALIDATION] Mismatch in %s: expected %d, got %d", func.__name__, expected_count, actual_count)
                logger.error("[OUTPUT_VALIDATION] Returned types: %s", [type(v).__name__ for v in values])
                raise ValueError(f"Callback {func.__name__} returned {actual_count} outputs, expected {expected_count}")

            return result

        return wrapper
    return decorator