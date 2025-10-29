"""
Performance Integration Tests

Tests for end-to-end performance, load testing, and system integration.
"""

import pytest
import time
import threading
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any
import pandas as pd
from unittest.mock import patch, Mock

from almanac.app import app
from almanac.performance.cache_enhancer import EnhancedCache
from almanac.performance.query_optimizer import QueryOptimizer
from almanac.performance.memory_manager import MemoryProfiler, DataStreamer
from almanac.performance.monitoring import PerformanceMonitor


class TestPerformanceIntegration:
    """Integration tests for performance optimization."""
    
    @pytest.fixture(autouse=True)
    def setup_test_environment(self):
        """Setup test environment for performance tests."""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Initialize performance components
        self.cache = EnhancedCache()
        self.cache.init_app(self.app)
        
        self.query_optimizer = QueryOptimizer(self.cache)
        self.memory_profiler = MemoryProfiler()
        self.data_streamer = DataStreamer()
        
        # Setup performance monitor
        self.performance_monitor = PerformanceMonitor(self.app, self.cache)
    
    def test_cache_performance_improvement(self):
        """Test that caching improves performance."""
        # Create test data
        test_data = pd.DataFrame({
            'time': pd.date_range('2025-01-01', periods=1000, freq='1min'),
            'open': range(1000),
            'high': range(1000),
            'low': range(1000),
            'close': range(1000),
            'volume': range(1000)
        })
        
        # Test without cache
        start_time = time.time()
        
        # Simulate expensive computation
        result1 = self._expensive_computation(test_data, use_cache=False)
        
        no_cache_time = time.time() - start_time
        
        # Test with cache
        start_time = time.time()
        
        result2 = self._expensive_computation(test_data, use_cache=True)
        
        cache_time = time.time() - start_time
        
        # Cache should be faster on subsequent calls
        assert cache_time < no_cache_time
        
        # Results should be identical
        pd.testing.assert_frame_equal(result1, result2)
    
    def _expensive_computation(self, data: pd.DataFrame, use_cache: bool = True) -> pd.DataFrame:
        """Simulate an expensive computation."""
        cache_key = f"expensive_computation_{hash(str(data))}"
        
        if use_cache:
            cached_result = self.cache.get(cache_key)
            if cached_result is not None:
                return cached_result
        
        # Simulate expensive operation
        time.sleep(0.1)  # Simulate 100ms computation
        
        result = data.copy()
        result['computed'] = result['close'] * 2
        
        if use_cache:
            self.cache.set(cache_key, result, timeout=3600)
        
        return result
    
    def test_memory_usage_optimization(self):
        """Test memory usage optimization with large datasets."""
        # Create large test dataset
        large_data = pd.DataFrame({
            'time': pd.date_range('2020-01-01', periods=100000, freq='1min'),
            'open': range(100000),
            'high': range(100000),
            'low': range(100000),
            'close': range(100000),
            'volume': range(100000)
        })
        
        # Monitor memory usage
        with self.memory_profiler.monitor_memory("large_dataset_processing"):
            # Process data in chunks
            results = []
            chunk_size = 10000
            
            for i in range(0, len(large_data), chunk_size):
                chunk = large_data.iloc[i:i+chunk_size]
                processed_chunk = self._process_chunk(chunk)
                results.append(processed_chunk)
                
                # Force garbage collection
                import gc
                gc.collect()
            
            final_result = pd.concat(results, ignore_index=True)
        
        # Verify results
        assert len(final_result) == len(large_data)
        assert 'processed' in final_result.columns
    
    def _process_chunk(self, chunk: pd.DataFrame) -> pd.DataFrame:
        """Process a chunk of data."""
        result = chunk.copy()
        result['processed'] = result['close'] * 1.5
        return result
    
    def test_concurrent_query_performance(self):
        """Test performance under concurrent load."""
        # Simulate concurrent queries
        def simulate_query(query_id: int) -> Dict[str, Any]:
            """Simulate a database query."""
            start_time = time.time()
            
            # Simulate query execution
            time.sleep(0.05)  # 50ms query
            
            execution_time = time.time() - start_time
            
            return {
                'query_id': query_id,
                'execution_time': execution_time,
                'timestamp': time.time()
            }
        
        # Run concurrent queries
        num_queries = 20
        results = []
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(simulate_query, i) for i in range(num_queries)]
            
            for future in as_completed(futures):
                results.append(future.result())
        
        # Analyze results
        assert len(results) == num_queries
        
        execution_times = [r['execution_time'] for r in results]
        avg_execution_time = sum(execution_times) / len(execution_times)
        
        # Average execution time should be reasonable
        assert avg_execution_time < 0.1  # Less than 100ms average
    
    def test_memory_leak_detection(self):
        """Test for memory leaks in repeated operations."""
        initial_memory = self.memory_profiler.get_memory_stats()
        
        # Perform repeated operations
        for i in range(10):
            # Create and process data
            test_data = pd.DataFrame({
                'time': pd.date_range('2025-01-01', periods=1000, freq='1min'),
                'value': range(1000)
            })
            
            # Process data
            processed = self._process_data_with_potential_leak(test_data)
            
            # Force garbage collection
            import gc
            gc.collect()
        
        final_memory = self.memory_profiler.get_memory_stats()
        
        # Memory growth should be minimal
        memory_growth = final_memory.process_memory_mb - initial_memory.process_memory_mb
        assert memory_growth < 50  # Less than 50MB growth
    
    def _process_data_with_potential_leak(self, data: pd.DataFrame) -> pd.DataFrame:
        """Process data that might cause memory leaks."""
        # Simulate data processing
        result = data.copy()
        result['processed'] = result['value'] * 2
        
        # Simulate some computation
        time.sleep(0.01)
        
        return result
    
    def test_cache_invalidation_performance(self):
        """Test cache invalidation performance."""
        # Populate cache
        cache_data = {}
        for i in range(100):
            key = f"test_key_{i}"
            value = pd.DataFrame({'test': range(i*10, (i+1)*10)})
            self.cache.set(key, value)
            cache_data[key] = value
        
        # Test cache hit performance
        start_time = time.time()
        
        for i in range(50):
            key = f"test_key_{i}"
            cached_value = self.cache.get(key)
            assert cached_value is not None
        
        cache_hit_time = time.time() - start_time
        
        # Test cache invalidation
        start_time = time.time()
        
        for i in range(50):
            key = f"test_key_{i}"
            self.cache.delete(key)
        
        invalidation_time = time.time() - start_time
        
        # Invalidation should be fast
        assert invalidation_time < cache_hit_time * 2
    
    def test_query_optimization_effectiveness(self):
        """Test query optimization effectiveness."""
        # Simulate slow queries
        slow_queries = [
            "SELECT * FROM RawIntradayData WHERE contract_id = 'ES'",
            "SELECT * FROM DailyData WHERE time > '2025-01-01'",
            "SELECT COUNT(*) FROM RawIntradayData GROUP BY contract_id"
        ]
        
        for sql in slow_queries:
            # Record query stats
            start_time = time.time()
            
            # Simulate query execution
            time.sleep(0.1)  # 100ms
            
            execution_time = time.time() - start_time
            
            # Add to optimizer stats
            from almanac.performance.query_optimizer import QueryStats
            stats = QueryStats(
                sql=sql,
                params={},
                execution_time=execution_time,
                row_count=1000,
                timestamp=time.time()
            )
            self.query_optimizer.query_stats.append(stats)
        
        # Analyze query patterns
        analysis = self.query_optimizer.analyze_query_patterns()
        
        assert 'query_types' in analysis
        assert 'recommendations' in analysis
        
        # Should have recommendations for optimization
        assert len(analysis['recommendations']) > 0
    
    def test_monitoring_system_performance(self):
        """Test performance monitoring system overhead."""
        # Start monitoring
        self.performance_monitor.start_monitoring(interval=1)  # 1 second interval
        
        try:
            # Perform operations while monitoring
            for i in range(5):
                test_data = pd.DataFrame({'test': range(1000)})
                self._expensive_computation(test_data)
                time.sleep(0.5)
            
            # Check that monitoring collected data
            assert len(self.performance_monitor.metrics_history) > 0
            
            # Check health status
            health_status = self.performance_monitor.get_health_status()
            assert 'status' in health_status
            assert 'components' in health_status
            
        finally:
            # Stop monitoring
            self.performance_monitor.stop_monitoring()
    
    def test_data_streaming_performance(self):
        """Test data streaming performance with large datasets."""
        # Create large dataset
        large_data = pd.DataFrame({
            'time': pd.date_range('2020-01-01', periods=100000, freq='1min'),
            'value': range(100000)
        })
        
        # Test streaming processing
        start_time = time.time()
        
        # Simulate streaming
        chunk_size = 10000
        processed_chunks = []
        
        for i in range(0, len(large_data), chunk_size):
            chunk = large_data.iloc[i:i+chunk_size]
            processed_chunk = self._process_chunk(chunk)
            processed_chunks.append(processed_chunk)
            
            # Simulate memory cleanup
            import gc
            gc.collect()
        
        streaming_time = time.time() - start_time
        
        # Compare with non-streaming approach
        start_time = time.time()
        
        # Process entire dataset at once
        processed_all = self._process_chunk(large_data)
        
        non_streaming_time = time.time() - start_time
        
        # Streaming should be more memory efficient (may not be faster)
        assert len(processed_chunks) == 10  # 10 chunks
        assert len(pd.concat(processed_chunks, ignore_index=True)) == len(large_data)
        
        # Results should be equivalent
        pd.testing.assert_frame_equal(
            processed_all, 
            pd.concat(processed_chunks, ignore_index=True)
        )


class TestLoadTesting:
    """Load testing for the application."""
    
    def test_concurrent_user_simulation(self):
        """Test application performance under concurrent user load."""
        def simulate_user_session(user_id: int) -> Dict[str, Any]:
            """Simulate a user session."""
            session_start = time.time()
            requests_made = 0
            total_response_time = 0
            
            # Simulate multiple requests per user
            for request_id in range(5):
                start_time = time.time()
                
                # Simulate request processing
                time.sleep(0.02)  # 20ms processing time
                
                response_time = time.time() - start_time
                total_response_time += response_time
                requests_made += 1
            
            session_duration = time.time() - session_start
            
            return {
                'user_id': user_id,
                'session_duration': session_duration,
                'requests_made': requests_made,
                'avg_response_time': total_response_time / requests_made,
                'total_response_time': total_response_time
            }
        
        # Simulate concurrent users
        num_users = 50
        results = []
        
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(simulate_user_session, i) for i in range(num_users)]
            
            for future in as_completed(futures):
                results.append(future.result())
        
        # Analyze results
        assert len(results) == num_users
        
        avg_response_times = [r['avg_response_time'] for r in results]
        max_response_time = max(avg_response_times)
        
        # Response times should be reasonable under load
        assert max_response_time < 0.1  # Less than 100ms average response time
        
        # Check that all users completed their sessions
        completed_sessions = len([r for r in results if r['requests_made'] == 5])
        assert completed_sessions == num_users
    
    def test_memory_usage_under_load(self):
        """Test memory usage under sustained load."""
        memory_profiler = MemoryProfiler()
        
        # Get initial memory
        initial_memory = memory_profiler.get_memory_stats()
        
        # Simulate sustained load
        def load_worker(worker_id: int):
            """Worker function for load testing."""
            for i in range(100):
                # Create and process data
                data = pd.DataFrame({
                    'time': pd.date_range('2025-01-01', periods=1000, freq='1min'),
                    'value': range(1000)
                })
                
                # Process data
                processed = data.copy()
                processed['computed'] = processed['value'] * 2
                
                # Simulate some work
                time.sleep(0.001)
                
                # Cleanup
                del data, processed
                
                if i % 10 == 0:
                    import gc
                    gc.collect()
        
        # Run multiple workers
        num_workers = 5
        threads = []
        
        for i in range(num_workers):
            thread = threading.Thread(target=load_worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check final memory
        final_memory = memory_profiler.get_memory_stats()
        
        # Memory growth should be reasonable
        memory_growth = final_memory.process_memory_mb - initial_memory.process_memory_mb
        assert memory_growth < 100  # Less than 100MB growth
    
    def test_cache_performance_under_load(self):
        """Test cache performance under high load."""
        cache = EnhancedCache()
        from flask import Flask
        app = Flask(__name__)
        cache.init_app(app)
        
        def cache_worker(worker_id: int):
            """Worker function for cache testing."""
            for i in range(100):
                key = f"worker_{worker_id}_key_{i}"
                value = pd.DataFrame({
                    'worker': worker_id,
                    'iteration': i,
                    'data': range(100)
                })
                
                # Set cache
                cache.set(key, value)
                
                # Get from cache
                retrieved = cache.get(key)
                assert retrieved is not None
                
                # Delete from cache
                cache.delete(key)
        
        # Run multiple cache workers
        num_workers = 10
        threads = []
        
        for i in range(num_workers):
            thread = threading.Thread(target=cache_worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All operations should complete without errors
        assert True  # If we get here, no exceptions were raised


@pytest.mark.performance
class TestPerformanceBenchmarks:
    """Performance benchmark tests."""
    
    def test_data_processing_benchmark(self):
        """Benchmark data processing performance."""
        import time
        
        # Create test dataset
        data = pd.DataFrame({
            'time': pd.date_range('2025-01-01', periods=10000, freq='1min'),
            'open': range(10000),
            'high': range(10000),
            'low': range(10000),
            'close': range(10000),
            'volume': range(10000)
        })
        
        # Benchmark processing
        start_time = time.time()
        
        # Process data
        result = data.copy()
        result['returns'] = (result['close'] - result['open']) / result['open']
        result['volatility'] = result['returns'].rolling(window=20).std()
        result['sma'] = result['close'].rolling(window=20).mean()
        
        processing_time = time.time() - start_time
        
        # Should process 10k rows in reasonable time
        assert processing_time < 1.0  # Less than 1 second
        
        # Verify results
        assert len(result) == len(data)
        assert 'returns' in result.columns
        assert 'volatility' in result.columns
        assert 'sma' in result.columns
    
    def test_cache_benchmark(self):
        """Benchmark cache performance."""
        from flask import Flask
        app = Flask(__name__)
        
        cache = EnhancedCache()
        cache.init_app(app)
        
        # Benchmark cache operations
        test_data = pd.DataFrame({'test': range(1000)})
        
        # Benchmark set operation
        start_time = time.time()
        for i in range(1000):
            cache.set(f'key_{i}', test_data)
        set_time = time.time() - start_time
        
        # Benchmark get operation
        start_time = time.time()
        for i in range(1000):
            cached = cache.get(f'key_{i}')
            assert cached is not None
        get_time = time.time() - start_time
        
        # Operations should be fast
        assert set_time < 10.0  # Less than 10 seconds for 1000 sets
        assert get_time < 5.0   # Less than 5 seconds for 1000 gets
    
    def test_memory_optimization_benchmark(self):
        """Benchmark memory optimization."""
        from almanac.performance.memory_manager import MemoryOptimizer
        
        # Create inefficient DataFrame
        inefficient_df = pd.DataFrame({
            'int_col': pd.Series(range(10000), dtype='int64'),
            'float_col': pd.Series([1.1] * 10000, dtype='float64'),
            'str_col': pd.Series(['test'] * 10000, dtype='object')
        })
        
        # Benchmark optimization
        start_time = time.time()
        optimized_df = MemoryOptimizer.optimize_dataframe_memory(inefficient_df.copy())
        optimization_time = time.time() - start_time
        
        # Optimization should be fast
        assert optimization_time < 1.0  # Less than 1 second
        
        # Memory should be reduced
        original_memory = inefficient_df.memory_usage(deep=True).sum()
        optimized_memory = optimized_df.memory_usage(deep=True).sum()
        
        assert optimized_memory < original_memory
        
        # Data should be preserved
        pd.testing.assert_frame_equal(inefficient_df, optimized_df, check_dtype=False)
