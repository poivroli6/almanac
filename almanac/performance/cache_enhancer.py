"""
Enhanced Caching System

Provides Redis support, query result caching, and intelligent cache invalidation.
"""

import os
import hashlib
import pickle
from typing import Any, Optional, Dict, Union
from datetime import datetime, timedelta
import pandas as pd

# Try to import Redis, fallback to filesystem if not available
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from flask_caching import Cache


class EnhancedCache:
    """
    Enhanced caching system with Redis support and intelligent invalidation.
    """
    
    def __init__(self, app=None, config=None):
        self.app = app
        self.redis_client = None
        self.filesystem_cache = None
        self.config = config or {}
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize the enhanced cache with the Flask app."""
        self.app = app
        
        # Configure Redis if available
        if REDIS_AVAILABLE and self.config.get('USE_REDIS', False):
            try:
                self.redis_client = redis.Redis(
                    host=self.config.get('REDIS_HOST', 'localhost'),
                    port=self.config.get('REDIS_PORT', 6379),
                    db=self.config.get('REDIS_DB', 0),
                    password=self.config.get('REDIS_PASSWORD'),
                    decode_responses=False,  # We'll handle serialization ourselves
                    socket_connect_timeout=5,
                    socket_timeout=5
                )
                # Test connection
                self.redis_client.ping()
                app.logger.info("Redis cache initialized successfully")
            except Exception as e:
                app.logger.warning(f"Redis connection failed, falling back to filesystem: {e}")
                self.redis_client = None
        
        # Initialize filesystem cache as fallback
        cache_config = {
            'CACHE_TYPE': 'filesystem',
            'CACHE_DIR': os.path.join(app.root_path, '..', '.cache'),
            'CACHE_DEFAULT_TIMEOUT': self.config.get('CACHE_TIMEOUT', 3600),
            'CACHE_THRESHOLD': self.config.get('CACHE_THRESHOLD', 1000)
        }
        
        self.filesystem_cache = Cache()
        self.filesystem_cache.init_app(app, config=cache_config)
    
    def _generate_cache_key(self, prefix: str, **kwargs) -> str:
        """Generate a consistent cache key from parameters."""
        # Sort kwargs for consistent key generation
        sorted_kwargs = sorted(kwargs.items())
        key_string = f"{prefix}:{sorted_kwargs}"
        
        # Create hash for shorter keys
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _serialize_data(self, data: Any) -> bytes:
        """Serialize data for storage."""
        return pickle.dumps(data)
    
    def _deserialize_data(self, data: bytes) -> Any:
        """Deserialize data from storage."""
        return pickle.loads(data)
    
    def get(self, key: str) -> Optional[Any]:
        """Get data from cache."""
        if self.redis_client:
            try:
                data = self.redis_client.get(key)
                if data:
                    return self._deserialize_data(data)
            except Exception:
                # Fallback to filesystem cache
                pass
        
        # Use filesystem cache
        return self.filesystem_cache.get(key)
    
    def set(self, key: str, value: Any, timeout: Optional[int] = None) -> bool:
        """Set data in cache."""
        timeout = timeout or self.config.get('CACHE_TIMEOUT', 3600)
        
        if self.redis_client:
            try:
                serialized_data = self._serialize_data(value)
                return self.redis_client.setex(key, timeout, serialized_data)
            except Exception:
                # Fallback to filesystem cache
                pass
        
        # Use filesystem cache
        self.filesystem_cache.set(key, value, timeout=timeout)
        return True
    
    def delete(self, key: str) -> bool:
        """Delete data from cache."""
        success = True
        
        if self.redis_client:
            try:
                self.redis_client.delete(key)
            except Exception:
                success = False
        
        # Also delete from filesystem cache
        try:
            self.filesystem_cache.delete(key)
        except Exception:
            success = False
        
        return success
    
    def clear(self) -> bool:
        """Clear all cached data."""
        success = True
        
        if self.redis_client:
            try:
                self.redis_client.flushdb()
            except Exception:
                success = False
        
        # Also clear filesystem cache
        try:
            self.filesystem_cache.clear()
        except Exception:
            success = False
        
        return success
    
    def cache_query_result(self, query_hash: str, result: pd.DataFrame, 
                          timeout: Optional[int] = None) -> bool:
        """Cache a database query result."""
        cache_key = f"query:{query_hash}"
        return self.set(cache_key, result, timeout)
    
    def get_cached_query_result(self, query_hash: str) -> Optional[pd.DataFrame]:
        """Retrieve a cached database query result."""
        cache_key = f"query:{query_hash}"
        return self.get(cache_key)
    
    def cache_computation_result(self, computation_type: str, params: Dict, 
                               result: Any, timeout: Optional[int] = None) -> bool:
        """Cache a computation result."""
        cache_key = self._generate_cache_key(f"compute:{computation_type}", **params)
        return self.set(cache_key, result, timeout)
    
    def get_cached_computation_result(self, computation_type: str, 
                                    params: Dict) -> Optional[Any]:
        """Retrieve a cached computation result."""
        cache_key = self._generate_cache_key(f"compute:{computation_type}", **params)
        return self.get(cache_key)
    
    def invalidate_by_pattern(self, pattern: str) -> int:
        """Invalidate cache entries matching a pattern."""
        count = 0
        
        if self.redis_client:
            try:
                keys = self.redis_client.keys(pattern)
                if keys:
                    count += self.redis_client.delete(*keys)
            except Exception:
                pass
        
        # Note: Filesystem cache doesn't support pattern deletion easily
        # This would require implementing a custom solution
        
        return count
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        stats = {
            'redis_available': self.redis_client is not None,
            'cache_type': 'redis' if self.redis_client else 'filesystem'
        }
        
        if self.redis_client:
            try:
                info = self.redis_client.info()
                stats.update({
                    'redis_connected_clients': info.get('connected_clients', 0),
                    'redis_used_memory': info.get('used_memory_human', 'N/A'),
                    'redis_keyspace_hits': info.get('keyspace_hits', 0),
                    'redis_keyspace_misses': info.get('keyspace_misses', 0),
                })
                
                # Calculate hit rate
                hits = info.get('keyspace_hits', 0)
                misses = info.get('keyspace_misses', 0)
                total = hits + misses
                stats['redis_hit_rate'] = (hits / total * 100) if total > 0 else 0
                
            except Exception:
                stats['redis_error'] = True
        
        return stats


def create_cache_key_for_query(sql: str, params: Dict) -> str:
    """Create a cache key for a database query."""
    # Normalize SQL (remove extra whitespace, sort parameters)
    normalized_sql = ' '.join(sql.split())
    sorted_params = sorted(params.items()) if params else []
    
    key_string = f"{normalized_sql}:{sorted_params}"
    return hashlib.md5(key_string.encode()).hexdigest()


def create_cache_key_for_computation(func_name: str, args: tuple, kwargs: dict) -> str:
    """Create a cache key for a computation."""
    # Convert args to dict for consistent key generation
    params = {f"arg_{i}": arg for i, arg in enumerate(args)}
    params.update(kwargs)
    
    return hashlib.md5(f"{func_name}:{sorted(params.items())}".encode()).hexdigest()
