"""
Health Check and Monitoring Utilities

Provides health check endpoints and monitoring capabilities for the Almanac Futures application.
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import pandas as pd
from functools import wraps

# Try to import psutil, but don't fail if it's not available
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    psutil = None

logger = logging.getLogger(__name__)


class HealthChecker:
    """
    Health checker for monitoring application status.
    """
    
    def __init__(self):
        self.start_time = datetime.now()
        self.request_count = 0
        self.error_count = 0
        self.last_check = datetime.now()
    
    def check_system_resources(self) -> Dict[str, Any]:
        """
        Check system resource usage.
        
        Returns:
            Dict: System resource information
        """
        if not HAS_PSUTIL:
            return {
                'cpu_percent': 'N/A (psutil not available)',
                'memory': {
                    'total': 'N/A',
                    'available': 'N/A',
                    'percent': 'N/A',
                    'used': 'N/A'
                },
                'disk': {
                    'total': 'N/A',
                    'used': 'N/A',
                    'free': 'N/A',
                    'percent': 'N/A'
                },
                'note': 'psutil not installed - install with: pip install psutil'
            }
        
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'cpu_percent': cpu_percent,
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'percent': memory.percent,
                    'used': memory.used
                },
                'disk': {
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free,
                    'percent': (disk.used / disk.total) * 100
                }
            }
        except Exception as e:
            logger.error(f"Error checking system resources: {e}")
            return {'error': str(e)}
    
    def check_data_sources(self) -> Dict[str, Any]:
        """
        Check data source availability.
        
        Returns:
            Dict: Data source status
        """
        try:
            # This would check actual data sources in a real implementation
            return {
                'database': 'healthy',
                'file_system': 'healthy',
                'external_apis': 'healthy'
            }
        except Exception as e:
            logger.error(f"Error checking data sources: {e}")
            return {'error': str(e)}
    
    def get_uptime(self) -> str:
        """
        Get application uptime.
        
        Returns:
            str: Formatted uptime
        """
        uptime = datetime.now() - self.start_time
        return str(uptime).split('.')[0]  # Remove microseconds
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Get overall health status.
        
        Returns:
            Dict: Complete health status
        """
        system_resources = self.check_system_resources()
        data_sources = self.check_data_sources()
        
        # Determine overall health
        overall_health = 'healthy'
        if 'error' in system_resources or 'error' in data_sources:
            overall_health = 'degraded'
        
        # Only check resource limits if psutil is available
        if HAS_PSUTIL and isinstance(system_resources.get('cpu_percent'), (int, float)):
            if system_resources.get('cpu_percent', 0) > 90:
                overall_health = 'degraded'
            
            if system_resources.get('memory', {}).get('percent', 0) > 90:
                overall_health = 'degraded'
        
        return {
            'status': overall_health,
            'timestamp': datetime.now().isoformat(),
            'uptime': self.get_uptime(),
            'request_count': self.request_count,
            'error_count': self.error_count,
            'system_resources': system_resources,
            'data_sources': data_sources
        }
    
    def increment_request_count(self):
        """Increment request counter."""
        self.request_count += 1
    
    def increment_error_count(self):
        """Increment error counter."""
        self.error_count += 1


class PerformanceMonitor:
    """
    Performance monitor for tracking application performance.
    """
    
    def __init__(self):
        self.metrics = []
        self.max_metrics = 1000  # Keep last 1000 metrics
    
    def record_metric(self, operation: str, duration: float, success: bool = True, **kwargs):
        """
        Record a performance metric.
        
        Args:
            operation: Name of the operation
            duration: Duration in seconds
            success: Whether the operation was successful
            **kwargs: Additional metric data
        """
        metric = {
            'timestamp': datetime.now(),
            'operation': operation,
            'duration': duration,
            'success': success,
            **kwargs
        }
        
        self.metrics.append(metric)
        
        # Keep only the last max_metrics
        if len(self.metrics) > self.max_metrics:
            self.metrics = self.metrics[-self.max_metrics:]
    
    def get_performance_summary(self, operation: Optional[str] = None, 
                               time_window: Optional[timedelta] = None) -> Dict[str, Any]:
        """
        Get performance summary.
        
        Args:
            operation: Filter by operation name
            time_window: Filter by time window
            
        Returns:
            Dict: Performance summary
        """
        metrics = self.metrics
        
        # Filter by operation if specified
        if operation:
            metrics = [m for m in metrics if m['operation'] == operation]
        
        # Filter by time window if specified
        if time_window:
            cutoff_time = datetime.now() - time_window
            metrics = [m for m in metrics if m['timestamp'] >= cutoff_time]
        
        if not metrics:
            return {'total_operations': 0}
        
        durations = [m['duration'] for m in metrics]
        successes = [m['success'] for m in metrics]
        
        return {
            'total_operations': len(metrics),
            'success_rate': sum(successes) / len(successes),
            'avg_duration': sum(durations) / len(durations),
            'min_duration': min(durations),
            'max_duration': max(durations),
            'operations': list(set(m['operation'] for m in metrics))
        }


def monitor_performance(operation_name: str):
    """
    Decorator to monitor function performance.
    
    Args:
        operation_name: Name of the operation for monitoring
        
    Returns:
        Decorated function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                logger.error(f"Error in {operation_name}: {e}")
                raise
            finally:
                duration = time.time() - start_time
                performance_monitor.record_metric(operation_name, duration, success)
        
        return wrapper
    return decorator


def monitor_callback_timing(callback_name: str = None):
    """
    Decorator specifically for monitoring Dash callback performance with enhanced error context.
    
    Args:
        callback_name: Name of the callback for monitoring (defaults to function name)
        
    Returns:
        Decorated function with timing logs and comprehensive error handling
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            name = callback_name or func.__name__
            start_time = time.time()
            
            # Log callback start with context
            logger.info(f"[CALLBACK START] {name}")
            logger.debug(f"[CALLBACK CONTEXT] Args count: {len(args)}, Kwargs: {list(kwargs.keys())}")
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Log successful completion with timing
                logger.info(f"[CALLBACK COMPLETE] {name} - {duration:.3f}s")
                
                # Record performance metric
                performance_monitor.record_metric(f"callback_{name}", duration, True)
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                
                # Enhanced error logging with full context
                logger.error(f"[CALLBACK ERROR] {name} - {duration:.3f}s")
                logger.error(f"[ERROR TYPE] {type(e).__name__}: {str(e)}")
                
                # Log function arguments (safely)
                try:
                    args_str = ", ".join([str(arg)[:100] + "..." if len(str(arg)) > 100 else str(arg) for arg in args])
                    logger.error(f"[ERROR ARGS] {args_str}")
                except:
                    logger.error(f"[ERROR ARGS] Unable to serialize arguments")
                
                # Log kwargs (safely)
                try:
                    kwargs_str = ", ".join([f"{k}={str(v)[:100]}{'...' if len(str(v)) > 100 else ''}" for k, v in kwargs.items()])
                    logger.error(f"[ERROR KWARGS] {kwargs_str}")
                except:
                    logger.error(f"[ERROR KWARGS] Unable to serialize keyword arguments")
                
                # Log full stack trace
                import traceback
                logger.error(f"[ERROR STACK TRACE]\n{traceback.format_exc()}")
                
                # Log error context for debugging
                logger.error(f"[ERROR CONTEXT] Function: {func.__name__}, Module: {func.__module__}")
                
                # Record performance metric as failed with error details
                performance_monitor.record_metric(
                    f"callback_{name}", 
                    duration, 
                    False, 
                    error_type=type(e).__name__,
                    error_message=str(e),
                    error_args_count=len(args),
                    error_kwargs_count=len(kwargs)
                )
                
                raise
        
        return wrapper
    return decorator


def create_health_check_endpoint(app):
    """
    Create health check endpoint for the Dash app.
    
    Args:
        app: Dash app instance
    """
    @app.server.route('/health')
    def health_check():
        """Health check endpoint."""
        health_status = health_checker.get_health_status()
        
        if health_status['status'] == 'healthy':
            return {'status': 'healthy', 'data': health_status}, 200
        else:
            return {'status': 'degraded', 'data': health_status}, 503


def create_metrics_endpoint(app):
    """
    Create metrics endpoint for the Dash app.
    
    Args:
        app: Dash app instance
    """
    @app.server.route('/metrics')
    def metrics():
        """Metrics endpoint."""
        performance_summary = performance_monitor.get_performance_summary()
        health_status = health_checker.get_health_status()
        
        return {
            'performance': performance_summary,
            'health': health_status,
            'timestamp': datetime.now().isoformat()
        }


def graceful_degradation(func):
    """
    Decorator for graceful degradation when errors occur.
    
    Args:
        func: Function to wrap
        
    Returns:
        Decorated function with graceful degradation
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.warning(f"Graceful degradation triggered in {func.__name__}: {e}")
            
            # Return fallback values based on function name
            if 'load_data' in func.__name__:
                # Return empty DataFrame for data loading functions
                return pd.DataFrame()
            elif 'calculate' in func.__name__:
                # Return None for calculation functions
                return None
            else:
                # Return empty string for other functions
                return ""
    
    return wrapper


def rate_limit(max_requests: int = 100, time_window: int = 60):
    """
    Decorator for rate limiting.
    
    Args:
        max_requests: Maximum requests allowed
        time_window: Time window in seconds
        
    Returns:
        Decorated function with rate limiting
    """
    requests = []
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            
            # Remove old requests outside the time window
            requests[:] = [req_time for req_time in requests if now - req_time < time_window]
            
            if len(requests) >= max_requests:
                logger.warning(f"Rate limit exceeded for {func.__name__}")
                raise Exception("Rate limit exceeded")
            
            requests.append(now)
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def timeout(seconds: int):
    """
    Decorator for function timeout.
    
    Args:
        seconds: Timeout in seconds
        
    Returns:
        Decorated function with timeout
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            import signal
            
            def timeout_handler(signum, frame):
                raise TimeoutError(f"Function {func.__name__} timed out after {seconds} seconds")
            
            # Set the signal handler
            old_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(seconds)
            
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                # Restore the old signal handler
                signal.signal(signal.SIGALRM, old_handler)
                signal.alarm(0)
        
        return wrapper
    return decorator


# Global instances
health_checker = HealthChecker()
performance_monitor = PerformanceMonitor()
