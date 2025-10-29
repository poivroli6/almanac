"""
Tests for Performance Optimization Module

Tests caching, query optimization, memory management, and monitoring functionality.
"""

import pytest
import pandas as pd
import time
from unittest.mock import patch, MagicMock, Mock
from datetime import datetime, timedelta

from almanac.performance.cache_enhancer import EnhancedCache, create_cache_key_for_query
from almanac.performance.query_optimizer import QueryOptimizer, QueryStats
from almanac.performance.memory_manager import MemoryProfiler, DataStreamer, MemoryOptimizer
from almanac.performance.monitoring import PerformanceMonitor, HealthStatus
from almanac.performance.production_config import ConfigManager, Environment, ErrorHandler, HealthChecker


class TestEnhancedCache:
    """Test enhanced caching functionality."""
    
    def test_cache_key_generation(self):
        """Test cache key generation."""
        key1 = create_cache_key_for_query("SELECT * FROM test", {"param1": "value1"})
        key2 = create_cache_key_for_query("SELECT * FROM test", {"param1": "value1"})
        key3 = create_cache_key_for_query("SELECT * FROM test", {"param1": "value2"})
        
        # Same parameters should generate same key
        assert key1 == key2
        # Different parameters should generate different keys
        assert key1 != key3
    
    @patch('almanac.performance.cache_enhancer.REDIS_AVAILABLE', False)
    def test_filesystem_cache_fallback(self):
        """Test filesystem cache when Redis is not available."""
        from flask import Flask
        
        app = Flask(__name__)
        app.config['TESTING'] = True
        
        cache = EnhancedCache()
        cache.init_app(app)
        
        # Test basic operations
        test_data = pd.DataFrame({'test': [1, 2, 3]})
        
        cache.set('test_key', test_data)
        retrieved = cache.get('test_key')
        
        assert retrieved is not None
        pd.testing.assert_frame_equal(retrieved, test_data)
        
        # Test deletion
        cache.delete('test_key')
        assert cache.get('test_key') is None
    
    def test_query_result_caching(self):
        """Test database query result caching."""
        from flask import Flask
        
        app = Flask(__name__)
        app.config['TESTING'] = True
        
        cache = EnhancedCache()
        cache.init_app(app)
        
        test_df = pd.DataFrame({'col1': [1, 2, 3], 'col2': ['a', 'b', 'c']})
        
        # Cache query result
        success = cache.cache_query_result('test_query_hash', test_df)
        assert success
        
        # Retrieve cached result
        cached_result = cache.get_cached_query_result('test_query_hash')
        assert cached_result is not None
        pd.testing.assert_frame_equal(cached_result, test_df)
    
    def test_computation_result_caching(self):
        """Test computation result caching."""
        from flask import Flask
        
        app = Flask(__name__)
        app.config['TESTING'] = True
        
        cache = EnhancedCache()
        cache.init_app(app)
        
        test_result = {'result': 42, 'data': [1, 2, 3]}
        
        # Cache computation result
        success = cache.cache_computation_result('test_computation', {'param1': 'value1'}, test_result)
        assert success
        
        # Retrieve cached result
        cached_result = cache.get_cached_computation_result('test_computation', {'param1': 'value1'})
        assert cached_result == test_result


class TestQueryOptimizer:
    """Test query optimization functionality."""
    
    def test_query_stats_creation(self):
        """Test QueryStats creation."""
        stats = QueryStats(
            sql="SELECT * FROM test",
            params={"param1": "value1"},
            execution_time=1.5,
            row_count=100,
            timestamp=datetime.now()
        )
        
        assert stats.sql == "SELECT * FROM test"
        assert stats.execution_time == 1.5
        assert stats.row_count == 100
    
    def test_query_classification(self):
        """Test query classification."""
        optimizer = QueryOptimizer()
        
        assert optimizer._classify_query("SELECT * FROM RawIntradayData") == "minute_data_select"
        assert optimizer._classify_query("SELECT * FROM DailyData") == "daily_data_select"
        assert optimizer._classify_query("INSERT INTO test") == "insert"
        assert optimizer._classify_query("UPDATE test SET") == "update"
        assert optimizer._classify_query("DELETE FROM test") == "delete"
    
    def test_optimized_query_generation(self):
        """Test optimized query generation."""
        optimizer = QueryOptimizer()
        
        # Test minute data query
        sql = optimizer.optimize_minute_data_query('ES', '2025-01-01', '2025-01-02')
        assert 'RawIntradayData' in sql
        assert ':product' in sql
        assert ':start_date' in sql
        assert ':end_date' in sql
        
        # Test daily data query
        sql = optimizer.optimize_daily_data_query('ES', '2025-01-01', '2025-01-02')
        assert 'DailyData' in sql
        assert ':product' in sql
    
    def test_performance_stats(self):
        """Test query performance statistics."""
        optimizer = QueryOptimizer()
        
        # Add some test stats
        optimizer.query_stats = [
            QueryStats(
                sql="SELECT * FROM test1",
                params={},
                execution_time=0.5,
                row_count=50,
                timestamp=datetime.now() - timedelta(hours=1),
                cache_hit=False
            ),
            QueryStats(
                sql="SELECT * FROM test2",
                params={},
                execution_time=2.0,
                row_count=100,
                timestamp=datetime.now() - timedelta(minutes=30),
                cache_hit=True
            )
        ]
        
        stats = optimizer.get_query_performance_stats(hours=2)
        
        assert stats['total_queries'] == 2
        assert stats['avg_execution_time'] == 1.25
        assert stats['cache_hit_rate'] == 50.0
        assert stats['slow_queries'] == 1
    
    def test_slow_queries_detection(self):
        """Test slow query detection."""
        optimizer = QueryOptimizer()
        
        # Add test stats with slow queries
        optimizer.query_stats = [
            QueryStats(
                sql="SELECT * FROM slow_table",
                params={},
                execution_time=5.0,
                row_count=1000,
                timestamp=datetime.now(),
                cache_hit=False
            ),
            QueryStats(
                sql="SELECT * FROM fast_table",
                params={},
                execution_time=0.1,
                row_count=10,
                timestamp=datetime.now(),
                cache_hit=True
            )
        ]
        
        slow_queries = optimizer.get_slow_queries(limit=5)
        
        assert len(slow_queries) == 1
        assert slow_queries[0]['execution_time'] == 5.0
        assert 'slow_table' in slow_queries[0]['sql']


class TestMemoryProfiler:
    """Test memory profiling functionality."""
    
    def test_memory_stats_creation(self):
        """Test memory statistics creation."""
        with patch('psutil.Process') as mock_process, \
             patch('psutil.virtual_memory') as mock_virtual_memory:
            
            # Mock memory info
            mock_memory_info = Mock()
            mock_memory_info.rss = 100 * 1024 * 1024  # 100MB
            mock_process.return_value.memory_info.return_value = mock_memory_info
            mock_process.return_value.memory_percent.return_value = 10.0
            
            mock_virtual_memory.return_value.total = 8 * 1024 * 1024 * 1024  # 8GB
            
            profiler = MemoryProfiler()
            stats = profiler.get_memory_stats()
            
            assert stats.process_memory_mb == 100.0
            assert stats.memory_percent == 10.0
            assert isinstance(stats.timestamp, datetime)
    
    def test_memory_summary(self):
        """Test memory usage summary."""
        profiler = MemoryProfiler()
        
        # Add some test stats
        profiler.memory_stats = [
            Mock(process_memory_mb=100.0, gc_objects=1000),
            Mock(process_memory_mb=150.0, gc_objects=1200),
            Mock(process_memory_mb=200.0, gc_objects=1500)
        ]
        
        summary = profiler.get_memory_summary(hours=1)
        
        assert summary['current_memory_mb'] == 200.0
        assert summary['peak_memory_mb'] == 200.0
        assert summary['avg_memory_mb'] == 150.0
        assert summary['memory_growth_mb'] == 100.0
    
    def test_gc_optimization(self):
        """Test garbage collection optimization."""
        profiler = MemoryProfiler()
        
        with patch('gc.set_threshold') as mock_set_threshold:
            profiler.optimize_gc()
            mock_set_threshold.assert_called_once_with(700, 10, 10)
    
    def test_memory_monitoring_context(self):
        """Test memory monitoring context manager."""
        profiler = MemoryProfiler()
        
        with patch.object(profiler, 'get_memory_stats') as mock_get_stats:
            mock_get_stats.side_effect = [
                Mock(process_memory_mb=100.0),
                Mock(process_memory_mb=150.0)
            ]
            
            with profiler.monitor_memory("test_operation"):
                pass  # Simulate operation
            
            assert mock_get_stats.call_count == 2


class TestDataStreamer:
    """Test data streaming functionality."""
    
    def test_dataframe_memory_optimization(self):
        """Test DataFrame memory optimization."""
        # Create a test DataFrame with inefficient types
        df = pd.DataFrame({
            'int_col': pd.Series([1, 2, 3], dtype='int64'),
            'float_col': pd.Series([1.1, 2.2, 3.3], dtype='float64'),
            'str_col': pd.Series(['a', 'b', 'a'], dtype='object')
        })
        
        original_memory = df.memory_usage(deep=True).sum()
        
        optimized_df = MemoryOptimizer.optimize_dataframe_memory(df.copy())
        
        optimized_memory = optimized_df.memory_usage(deep=True).sum()
        
        # Memory should be reduced
        assert optimized_memory <= original_memory
        
        # Data should be preserved
        pd.testing.assert_frame_equal(df, optimized_df, check_dtype=False)
    
    def test_cleanup_large_objects(self):
        """Test cleanup of large objects."""
        with patch('gc.collect') as mock_collect:
            mock_collect.return_value = 10
            
            MemoryOptimizer.cleanup_large_objects(
                pd.DataFrame({'test': [1, 2, 3]}),
                {'test': 'dict'},
                None
            )
            
            mock_collect.assert_called_once()


class TestPerformanceMonitor:
    """Test performance monitoring functionality."""
    
    def test_health_status_creation(self):
        """Test health status creation."""
        status = HealthStatus(
            component='test',
            status='healthy',
            message='Test message',
            timestamp=datetime.now(),
            metrics={'test_metric': 42}
        )
        
        assert status.component == 'test'
        assert status.status == 'healthy'
        assert status.message == 'Test message'
    
    def test_performance_metrics_creation(self):
        """Test performance metrics creation."""
        from almanac.performance.monitoring import PerformanceMetrics
        
        metrics = PerformanceMetrics(
            timestamp=datetime.now(),
            memory_mb=100.0,
            query_count=50,
            avg_query_time=0.5,
            cache_hit_rate=80.0,
            active_connections=5,
            error_count=0
        )
        
        assert metrics.memory_mb == 100.0
        assert metrics.query_count == 50
        assert metrics.avg_query_time == 0.5
        assert metrics.cache_hit_rate == 80.0


class TestConfigManager:
    """Test configuration management."""
    
    def test_environment_detection(self):
        """Test environment detection."""
        with patch.dict('os.environ', {'ALMANAC_ENV': 'production'}):
            config = ConfigManager()
            assert config.environment == Environment.PRODUCTION
        
        with patch.dict('os.environ', {}, clear=True):
            config = ConfigManager()
            assert config.environment == Environment.DEVELOPMENT
    
    def test_config_loading(self):
        """Test configuration loading."""
        config = ConfigManager(Environment.DEVELOPMENT)
        
        # Test basic config values
        assert config.get('debug') == True
        assert config.get('host') == '127.0.0.1'
        
        # Test nested config values
        assert isinstance(config.get('database'), dict)
        assert isinstance(config.get('cache'), dict)
        assert isinstance(config.get('logging'), dict)
    
    def test_environment_specific_config(self):
        """Test environment-specific configuration."""
        dev_config = ConfigManager(Environment.DEVELOPMENT)
        prod_config = ConfigManager(Environment.PRODUCTION)
        
        assert dev_config.get('debug') == True
        assert prod_config.get('debug') == False
        
        assert dev_config.get('host') == '127.0.0.1'
        assert prod_config.get('host') == '0.0.0.0'


class TestHealthChecker:
    """Test health checking functionality."""
    
    def test_memory_health_check(self):
        """Test memory health checking."""
        config = ConfigManager(Environment.DEVELOPMENT)
        health_checker = HealthChecker(config)
        
        with patch('psutil.Process') as mock_process:
            # Mock low memory usage
            mock_memory_info = Mock()
            mock_memory_info.rss = 500 * 1024 * 1024  # 500MB
            mock_process.return_value.memory_info.return_value = mock_memory_info
            
            result = health_checker.check_memory_health()
            
            assert result['status'] == 'healthy'
            assert 'Memory usage normal' in result['message']
            assert result['memory_mb'] == 500.0
    
    def test_database_health_check(self):
        """Test database health checking."""
        config = ConfigManager(Environment.DEVELOPMENT)
        health_checker = HealthChecker(config)
        
        with patch('almanac.performance.production_config.get_engine') as mock_get_engine:
            # Mock successful database connection
            mock_engine = Mock()
            mock_conn = Mock()
            mock_result = Mock()
            mock_result.__getitem__ = Mock(return_value=1)
            mock_conn.execute.return_value.fetchone.return_value = mock_result
            
            mock_engine.connect.return_value.__enter__.return_value = mock_conn
            mock_get_engine.return_value = mock_engine
            
            result = health_checker.check_database_health()
            
            assert result['status'] == 'healthy'
            assert 'Database connection successful' in result['message']
    
    def test_overall_health_status(self):
        """Test overall health status determination."""
        config = ConfigManager(Environment.DEVELOPMENT)
        health_checker = HealthChecker(config)
        
        with patch.object(health_checker, 'check_memory_health') as mock_memory, \
             patch.object(health_checker, 'check_database_health') as mock_db, \
             patch.object(health_checker, 'check_cache_health') as mock_cache:
            
            mock_memory.return_value = {'status': 'healthy'}
            mock_db.return_value = {'status': 'healthy'}
            mock_cache.return_value = {'status': 'healthy'}
            
            result = health_checker.get_overall_health()
            
            assert result['status'] == 'healthy'
            assert len(result['checks']) == 3


class TestIntegration:
    """Integration tests for performance modules."""
    
    def test_cache_and_query_optimizer_integration(self):
        """Test integration between cache and query optimizer."""
        from flask import Flask
        
        app = Flask(__name__)
        app.config['TESTING'] = True
        
        # Setup cache
        cache = EnhancedCache()
        cache.init_app(app)
        
        # Setup query optimizer with cache
        optimizer = QueryOptimizer(cache)
        
        # Test query result caching
        test_df = pd.DataFrame({'test': [1, 2, 3]})
        
        # Mock the actual query execution
        with patch.object(optimizer, '_get_connection') as mock_conn:
            mock_conn.return_value.__enter__.return_value = Mock()
            
            # This would normally execute a query, but we'll mock the result
            cache.cache_query_result('test_query', test_df)
            
            # Verify cache integration
            cached_result = cache.get_cached_query_result('test_query')
            assert cached_result is not None
            pd.testing.assert_frame_equal(cached_result, test_df)
    
    def test_memory_profiler_and_monitor_integration(self):
        """Test integration between memory profiler and performance monitor."""
        from flask import Flask
        
        app = Flask(__name__)
        app.config['TESTING'] = True
        
        # Setup components
        cache = EnhancedCache()
        cache.init_app(app)
        
        monitor = PerformanceMonitor(app, cache)
        
        # Mock memory profiler
        with patch('almanac.performance.monitoring.get_memory_profiler') as mock_profiler:
            mock_stats = Mock()
            mock_stats.process_memory_mb = 100.0
            mock_profiler.return_value.get_memory_stats.return_value = mock_stats
            
            # Test metrics collection
            monitor._collect_metrics()
            
            assert len(monitor.metrics_history) == 1
            assert monitor.metrics_history[0].memory_mb == 100.0
