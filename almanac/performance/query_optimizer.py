"""
Database Query Optimization

Provides query optimization, indexing recommendations, and connection pooling enhancements.
"""

import time
import logging
from typing import Dict, List, Optional, Any, Tuple
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta
import pandas as pd

from ..data_sources.db_config import get_engine
from sqlalchemy import text, create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError


@dataclass
class QueryStats:
    """Statistics for a database query."""
    sql: str
    params: Dict[str, Any]
    execution_time: float
    row_count: int
    timestamp: datetime
    cache_hit: bool = False
    error: Optional[str] = None


class QueryOptimizer:
    """
    Database query optimizer with caching, connection pooling, and performance monitoring.
    """
    
    def __init__(self, cache_manager=None):
        self.cache_manager = cache_manager
        self.query_stats: List[QueryStats] = []
        self.logger = logging.getLogger(__name__)
        
        # Performance thresholds
        self.slow_query_threshold = 1.0  # seconds
        self.cache_timeout = 3600  # 1 hour
        
        # Index recommendations
        self.recommended_indexes = {
            'RawIntradayData': [
                'CREATE INDEX idx_raw_time_product ON RawIntradayData(contract_id, interval, time)',
                'CREATE INDEX idx_raw_time_only ON RawIntradayData(time)',
                'CREATE INDEX idx_raw_contract ON RawIntradayData(contract_id)',
            ],
            'DailyData': [
                'CREATE INDEX idx_daily_product ON DailyData(contract_id, time)',
                'CREATE INDEX idx_daily_time ON DailyData(time)',
                'CREATE INDEX idx_daily_contract ON DailyData(contract_id)',
            ]
        }
    
    def execute_query(self, sql: str, params: Optional[Dict] = None, 
                     use_cache: bool = True, timeout: Optional[int] = None) -> pd.DataFrame:
        """
        Execute a database query with optimization and caching.
        
        Args:
            sql: SQL query string
            params: Query parameters
            use_cache: Whether to use caching
            timeout: Cache timeout in seconds
            
        Returns:
            DataFrame with query results
        """
        params = params or {}
        start_time = time.time()
        
        # Check cache first
        if use_cache and self.cache_manager:
            cache_key = self._create_query_cache_key(sql, params)
            cached_result = self.cache_manager.get_cached_query_result(cache_key)
            
            if cached_result is not None:
                execution_time = time.time() - start_time
                stats = QueryStats(
                    sql=sql,
                    params=params,
                    execution_time=execution_time,
                    row_count=len(cached_result),
                    timestamp=datetime.now(),
                    cache_hit=True
                )
                self.query_stats.append(stats)
                
                self.logger.info(f"Cache hit for query: {execution_time:.3f}s")
                return cached_result
        
        # Execute query
        try:
            with self._get_connection() as conn:
                result = pd.read_sql(sql, conn, params=params)
            
            execution_time = time.time() - start_time
            
            # Cache the result
            if use_cache and self.cache_manager:
                cache_timeout = timeout or self.cache_timeout
                cache_key = self._create_query_cache_key(sql, params)
                self.cache_manager.cache_query_result(cache_key, result, cache_timeout)
            
            # Record statistics
            stats = QueryStats(
                sql=sql,
                params=params,
                execution_time=execution_time,
                row_count=len(result),
                timestamp=datetime.now()
            )
            self.query_stats.append(stats)
            
            # Log slow queries
            if execution_time > self.slow_query_threshold:
                self.logger.warning(
                    f"Slow query detected: {execution_time:.3f}s\n"
                    f"SQL: {sql[:200]}...\n"
                    f"Params: {params}"
                )
            
            self.logger.debug(f"Query executed: {execution_time:.3f}s, {len(result)} rows")
            return result
            
        except SQLAlchemyError as e:
            execution_time = time.time() - start_time
            error_msg = str(e)
            
            stats = QueryStats(
                sql=sql,
                params=params,
                execution_time=execution_time,
                row_count=0,
                timestamp=datetime.now(),
                error=error_msg
            )
            self.query_stats.append(stats)
            
            self.logger.error(f"Query failed: {error_msg}\nSQL: {sql}")
            raise
    
    @contextmanager
    def _get_connection(self):
        """Get a database connection with proper error handling."""
        engine = get_engine()
        conn = None
        try:
            conn = engine.connect()
            yield conn
        finally:
            if conn:
                conn.close()
    
    def _create_query_cache_key(self, sql: str, params: Dict) -> str:
        """Create a cache key for a query."""
        # Normalize SQL
        normalized_sql = ' '.join(sql.strip().split())
        # Sort parameters for consistent keys
        sorted_params = sorted(params.items()) if params else []
        key_string = f"{normalized_sql}:{sorted_params}"
        
        import hashlib
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def optimize_minute_data_query(self, product: str, start_date: str, 
                                 end_date: str, interval: int = 1) -> str:
        """
        Generate an optimized query for minute data.
        
        Args:
            product: Product symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            interval: Minute interval (default: 1)
            
        Returns:
            Optimized SQL query
        """
        # Use parameterized query for better performance
        sql = """
        SELECT 
            time,
            open,
            high,
            low,
            close,
            volume
        FROM RawIntradayData
        WHERE contract_id = :product
          AND interval = :interval
          AND time >= :start_date
          AND time <= :end_date
        ORDER BY time
        """
        
        return sql
    
    def optimize_daily_data_query(self, product: str, start_date: str, 
                                end_date: str) -> str:
        """
        Generate an optimized query for daily data.
        
        Args:
            product: Product symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            Optimized SQL query
        """
        sql = """
        SELECT 
            time,
            open,
            high,
            low,
            close,
            volume
        FROM DailyData
        WHERE contract_id = :product
          AND time >= :start_date
          AND time <= :end_date
        ORDER BY time
        """
        
        return sql
    
    def get_query_performance_stats(self, hours: int = 24) -> Dict[str, Any]:
        """
        Get query performance statistics for the last N hours.
        
        Args:
            hours: Number of hours to analyze
            
        Returns:
            Dictionary with performance statistics
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_stats = [s for s in self.query_stats if s.timestamp >= cutoff_time]
        
        if not recent_stats:
            return {
                'total_queries': 0,
                'avg_execution_time': 0,
                'cache_hit_rate': 0,
                'slow_queries': 0
            }
        
        total_queries = len(recent_stats)
        cache_hits = sum(1 for s in recent_stats if s.cache_hit)
        slow_queries = sum(1 for s in recent_stats if s.execution_time > self.slow_query_threshold)
        
        avg_execution_time = sum(s.execution_time for s in recent_stats) / total_queries
        cache_hit_rate = (cache_hits / total_queries * 100) if total_queries > 0 else 0
        
        return {
            'total_queries': total_queries,
            'avg_execution_time': avg_execution_time,
            'cache_hit_rate': cache_hit_rate,
            'slow_queries': slow_queries,
            'slow_query_rate': (slow_queries / total_queries * 100) if total_queries > 0 else 0
        }
    
    def get_slow_queries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the slowest queries.
        
        Args:
            limit: Maximum number of queries to return
            
        Returns:
            List of slow query dictionaries
        """
        slow_queries = [s for s in self.query_stats if s.execution_time > self.slow_query_threshold]
        slow_queries.sort(key=lambda x: x.execution_time, reverse=True)
        
        return [
            {
                'sql': q.sql[:200] + '...' if len(q.sql) > 200 else q.sql,
                'execution_time': q.execution_time,
                'row_count': q.row_count,
                'timestamp': q.timestamp,
                'params': q.params
            }
            for q in slow_queries[:limit]
        ]
    
    def recommend_indexes(self, table_name: str) -> List[str]:
        """
        Get index recommendations for a table.
        
        Args:
            table_name: Name of the table
            
        Returns:
            List of CREATE INDEX statements
        """
        return self.recommended_indexes.get(table_name, [])
    
    def analyze_query_patterns(self) -> Dict[str, Any]:
        """
        Analyze query patterns to identify optimization opportunities.
        
        Returns:
            Dictionary with analysis results
        """
        if not self.query_stats:
            return {'message': 'No query statistics available'}
        
        # Analyze by query type
        query_types = {}
        for stat in self.query_stats:
            query_type = self._classify_query(stat.sql)
            if query_type not in query_types:
                query_types[query_type] = {
                    'count': 0,
                    'total_time': 0,
                    'avg_time': 0,
                    'cache_hits': 0
                }
            
            query_types[query_type]['count'] += 1
            query_types[query_type]['total_time'] += stat.execution_time
            query_types[query_type]['cache_hits'] += 1 if stat.cache_hit else 0
        
        # Calculate averages
        for query_type in query_types:
            stats = query_types[query_type]
            stats['avg_time'] = stats['total_time'] / stats['count']
            stats['cache_hit_rate'] = (stats['cache_hits'] / stats['count'] * 100)
        
        return {
            'query_types': query_types,
            'total_queries': len(self.query_stats),
            'recommendations': self._generate_recommendations(query_types)
        }
    
    def _classify_query(self, sql: str) -> str:
        """Classify a query by type."""
        sql_lower = sql.lower().strip()
        if sql_lower.startswith('select'):
            if 'rawintradaydata' in sql_lower:
                return 'minute_data_select'
            elif 'dailydata' in sql_lower:
                return 'daily_data_select'
            else:
                return 'other_select'
        elif sql_lower.startswith('insert'):
            return 'insert'
        elif sql_lower.startswith('update'):
            return 'update'
        elif sql_lower.startswith('delete'):
            return 'delete'
        else:
            return 'other'
    
    def _generate_recommendations(self, query_types: Dict) -> List[str]:
        """Generate optimization recommendations based on query analysis."""
        recommendations = []
        
        for query_type, stats in query_types.items():
            if stats['avg_time'] > self.slow_query_threshold:
                recommendations.append(
                    f"Consider optimizing {query_type} queries (avg: {stats['avg_time']:.2f}s)"
                )
            
            if stats['cache_hit_rate'] < 50:
                recommendations.append(
                    f"Low cache hit rate for {query_type} ({stats['cache_hit_rate']:.1f}%) - consider longer cache timeout"
                )
        
        return recommendations
    
    def clear_stats(self):
        """Clear query statistics."""
        self.query_stats.clear()
        self.logger.info("Query statistics cleared")


# Global query optimizer instance
_query_optimizer = None


def get_query_optimizer() -> QueryOptimizer:
    """Get the global query optimizer instance."""
    global _query_optimizer
    if _query_optimizer is None:
        _query_optimizer = QueryOptimizer()
    return _query_optimizer


def init_query_optimizer(cache_manager=None):
    """Initialize the global query optimizer with a cache manager."""
    global _query_optimizer
    _query_optimizer = QueryOptimizer(cache_manager)
