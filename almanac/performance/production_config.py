"""
Production Configuration Management

Provides environment-based configuration, error handling, logging, and health checks.
"""

import os
import logging
import json
from typing import Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

from flask import Flask, request, jsonify, Response
import structlog


class Environment(Enum):
    """Application environments."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


@dataclass
class DatabaseConfig:
    """Database configuration."""
    host: str
    port: int
    database: str
    username: Optional[str] = None
    password: Optional[str] = None
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 3600


@dataclass
class CacheConfig:
    """Cache configuration."""
    type: str = "filesystem"  # filesystem, redis, memcached
    host: Optional[str] = None
    port: Optional[int] = None
    password: Optional[str] = None
    timeout: int = 3600
    threshold: int = 1000


@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: str = "INFO"
    format: str = "json"  # json, text
    file_path: Optional[str] = None
    max_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5


@dataclass
class PerformanceConfig:
    """Performance configuration."""
    memory_warning_threshold: int = 1024  # MB
    memory_critical_threshold: int = 2048  # MB
    query_timeout: int = 30  # seconds
    cache_timeout: int = 3600  # seconds
    monitoring_interval: int = 30  # seconds


class ConfigManager:
    """Manages application configuration for different environments."""
    
    def __init__(self, environment: Environment = None):
        self.environment = environment or self._detect_environment()
        self.config = self._load_config()
        
        # Initialize structured logging
        self._setup_logging()
    
    def _detect_environment(self) -> Environment:
        """Detect the current environment."""
        env_str = os.getenv('ALMANAC_ENV', 'development').lower()
        
        try:
            return Environment(env_str)
        except ValueError:
            return Environment.DEVELOPMENT
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration for the current environment."""
        base_config = {
            'environment': self.environment.value,
            'debug': False,
            'host': '127.0.0.1',
            'port': 8085,
            'database': self._load_database_config(),
            'cache': self._load_cache_config(),
            'logging': self._load_logging_config(),
            'performance': self._load_performance_config(),
        }
        
        # Environment-specific overrides
        if self.environment == Environment.PRODUCTION:
            base_config.update({
                'debug': False,
                'host': '0.0.0.0',
                'port': int(os.getenv('PORT', 8085)),
            })
        elif self.environment == Environment.STAGING:
            base_config.update({
                'debug': False,
                'host': '0.0.0.0',
            })
        else:  # DEVELOPMENT
            base_config.update({
                'debug': True,
                'host': '127.0.0.1',
            })
        
        return base_config
    
    def _load_database_config(self) -> Dict[str, Any]:
        """Load database configuration."""
        return {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', 1433)),
            'database': os.getenv('DB_NAME', 'HistoricalData'),
            'username': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'pool_size': int(os.getenv('DB_POOL_SIZE', 10)),
            'max_overflow': int(os.getenv('DB_MAX_OVERFLOW', 20)),
            'pool_timeout': int(os.getenv('DB_POOL_TIMEOUT', 30)),
            'pool_recycle': int(os.getenv('DB_POOL_RECYCLE', 3600)),
        }
    
    def _load_cache_config(self) -> Dict[str, Any]:
        """Load cache configuration."""
        return {
            'type': os.getenv('CACHE_TYPE', 'filesystem'),
            'host': os.getenv('REDIS_HOST'),
            'port': int(os.getenv('REDIS_PORT', 6379)) if os.getenv('REDIS_PORT') else None,
            'password': os.getenv('REDIS_PASSWORD'),
            'timeout': int(os.getenv('CACHE_TIMEOUT', 3600)),
            'threshold': int(os.getenv('CACHE_THRESHOLD', 1000)),
        }
    
    def _load_logging_config(self) -> Dict[str, Any]:
        """Load logging configuration."""
        return {
            'level': os.getenv('LOG_LEVEL', 'INFO'),
            'format': os.getenv('LOG_FORMAT', 'json'),
            'file_path': os.getenv('LOG_FILE_PATH'),
            'max_size': int(os.getenv('LOG_MAX_SIZE', 10 * 1024 * 1024)),
            'backup_count': int(os.getenv('LOG_BACKUP_COUNT', 5)),
        }
    
    def _load_performance_config(self) -> Dict[str, Any]:
        """Load performance configuration."""
        return {
            'memory_warning_threshold': int(os.getenv('MEMORY_WARNING_MB', 1024)),
            'memory_critical_threshold': int(os.getenv('MEMORY_CRITICAL_MB', 2048)),
            'query_timeout': int(os.getenv('QUERY_TIMEOUT', 30)),
            'cache_timeout': int(os.getenv('CACHE_TIMEOUT', 3600)),
            'monitoring_interval': int(os.getenv('MONITORING_INTERVAL', 30)),
        }
    
    def _setup_logging(self):
        """Setup structured logging."""
        log_config = self.config['logging']
        
        # Configure structlog
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer() if log_config['format'] == 'json' 
                else structlog.dev.ConsoleRenderer(),
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
        
        # Configure Python logging
        logging.basicConfig(
            level=getattr(logging, log_config['level'].upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Add file handler if specified
        if log_config['file_path']:
            from logging.handlers import RotatingFileHandler
            
            file_handler = RotatingFileHandler(
                log_config['file_path'],
                maxBytes=log_config['max_size'],
                backupCount=log_config['backup_count']
            )
            
            logger = logging.getLogger()
            logger.addHandler(file_handler)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return self.config.copy()


class ErrorHandler:
    """Centralized error handling for the application."""
    
    def __init__(self, app: Flask, config: ConfigManager):
        self.app = app
        self.config = config
        self.logger = structlog.get_logger()
        
        # Register error handlers
        self._register_error_handlers()
    
    def _register_error_handlers(self):
        """Register Flask error handlers."""
        
        @self.app.errorhandler(400)
        def bad_request(error):
            return self._create_error_response(
                'Bad Request',
                400,
                'The request could not be understood by the server.',
                str(error)
            )
        
        @self.app.errorhandler(404)
        def not_found(error):
            return self._create_error_response(
                'Not Found',
                404,
                'The requested resource was not found.',
                str(error)
            )
        
        @self.app.errorhandler(500)
        def internal_error(error):
            self.logger.error(
                "Internal server error",
                error=str(error),
                request_url=request.url,
                request_method=request.method
            )
            
            return self._create_error_response(
                'Internal Server Error',
                500,
                'An internal server error occurred.',
                str(error) if self.config.get('debug', False) else 'Internal server error'
            )
        
        @self.app.errorhandler(Exception)
        def handle_exception(error):
            self.logger.error(
                "Unhandled exception",
                error=str(error),
                request_url=request.url,
                request_method=request.method,
                exc_info=True
            )
            
            return self._create_error_response(
                'Internal Server Error',
                500,
                'An unexpected error occurred.',
                str(error) if self.config.get('debug', False) else 'Internal server error'
            )
    
    def _create_error_response(self, title: str, status_code: int, 
                             message: str, details: str = None) -> Response:
        """Create a standardized error response."""
        error_data = {
            'error': {
                'title': title,
                'status': status_code,
                'message': message,
                'timestamp': datetime.now().isoformat(),
                'path': request.path if request else None
            }
        }
        
        if details and self.config.get('debug', False):
            error_data['error']['details'] = details
        
        response = jsonify(error_data)
        response.status_code = status_code
        return response


class HealthChecker:
    """System health checking and monitoring."""
    
    def __init__(self, config: ConfigManager):
        self.config = config
        self.logger = structlog.get_logger()
        
        # Health check results cache
        self._health_cache = {}
        self._cache_timeout = 30  # seconds
    
    def check_database_health(self) -> Dict[str, Any]:
        """Check database connectivity and performance."""
        try:
            from ..data_sources.db_config import get_engine
            
            engine = get_engine()
            
            # Test connection
            with engine.connect() as conn:
                result = conn.execute("SELECT 1 as test").fetchone()
                
                if result and result[0] == 1:
                    return {
                        'status': 'healthy',
                        'message': 'Database connection successful',
                        'response_time': 0.1  # Would measure actual response time
                    }
                else:
                    return {
                        'status': 'unhealthy',
                        'message': 'Database query returned unexpected result'
                    }
                    
        except Exception as e:
            return {
                'status': 'unhealthy',
                'message': f'Database connection failed: {str(e)}'
            }
    
    def check_cache_health(self) -> Dict[str, Any]:
        """Check cache system health."""
        try:
            from ..performance.cache_enhancer import get_cache_manager
            
            cache_manager = get_cache_manager()
            if not cache_manager:
                return {
                    'status': 'warning',
                    'message': 'Cache manager not available'
                }
            
            # Test cache operations
            test_key = 'health_check_test'
            test_value = {'test': True, 'timestamp': datetime.now().isoformat()}
            
            # Set and get test
            cache_manager.set(test_key, test_value, timeout=10)
            retrieved = cache_manager.get(test_key)
            
            if retrieved == test_value:
                cache_manager.delete(test_key)
                return {
                    'status': 'healthy',
                    'message': 'Cache operations successful'
                }
            else:
                return {
                    'status': 'unhealthy',
                    'message': 'Cache read/write test failed'
                }
                
        except Exception as e:
            return {
                'status': 'unhealthy',
                'message': f'Cache health check failed: {str(e)}'
            }
    
    def check_memory_health(self) -> Dict[str, Any]:
        """Check system memory health."""
        try:
            import psutil
            
            process = psutil.Process()
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024
            
            warning_threshold = self.config.get('performance.memory_warning_threshold', 1024)
            critical_threshold = self.config.get('performance.memory_critical_threshold', 2048)
            
            if memory_mb > critical_threshold:
                status = 'critical'
                message = f'Memory usage critical: {memory_mb:.1f}MB'
            elif memory_mb > warning_threshold:
                status = 'warning'
                message = f'Memory usage high: {memory_mb:.1f}MB'
            else:
                status = 'healthy'
                message = f'Memory usage normal: {memory_mb:.1f}MB'
            
            return {
                'status': status,
                'message': message,
                'memory_mb': memory_mb
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'message': f'Memory health check failed: {str(e)}'
            }
    
    def get_overall_health(self) -> Dict[str, Any]:
        """Get overall system health status."""
        checks = {
            'database': self.check_database_health(),
            'cache': self.check_cache_health(),
            'memory': self.check_memory_health(),
        }
        
        # Determine overall status
        statuses = [check['status'] for check in checks.values()]
        
        if 'critical' in statuses or 'unhealthy' in statuses:
            overall_status = 'critical'
        elif 'warning' in statuses:
            overall_status = 'warning'
        else:
            overall_status = 'healthy'
        
        return {
            'status': overall_status,
            'timestamp': datetime.now().isoformat(),
            'checks': checks
        }


def setup_production_infrastructure(app: Flask, environment: Environment = None) -> Dict[str, Any]:
    """
    Setup production infrastructure for the Flask application.
    
    Args:
        app: Flask application instance
        environment: Application environment
        
    Returns:
        Dictionary with initialized components
    """
    # Initialize configuration
    config_manager = ConfigManager(environment)
    
    # Setup error handling
    error_handler = ErrorHandler(app, config_manager)
    
    # Setup health checking
    health_checker = HealthChecker(config_manager)
    
    # Register health check endpoint
    @app.route('/health')
    def health_check():
        """Health check endpoint."""
        return jsonify(health_checker.get_overall_health())
    
    # Register configuration endpoint (for debugging)
    @app.route('/config')
    def get_config():
        """Get application configuration (debug only)."""
        if not config_manager.get('debug', False):
            return jsonify({'error': 'Configuration endpoint not available in production'}), 403
        
        return jsonify(config_manager.to_dict())
    
    return {
        'config': config_manager,
        'error_handler': error_handler,
        'health_checker': health_checker
    }
