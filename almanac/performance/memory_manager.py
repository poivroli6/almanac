"""
Memory Management and Data Streaming

Provides memory profiling, data streaming for large datasets, and garbage collection optimization.
"""

import gc
import psutil
import logging
import tracemalloc
from typing import Iterator, Optional, Dict, Any, List, Tuple
from contextlib import contextmanager
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from dataclasses import dataclass


@dataclass
class MemoryStats:
    """Memory usage statistics."""
    timestamp: datetime
    process_memory_mb: float
    system_memory_mb: float
    memory_percent: float
    peak_memory_mb: float
    gc_objects: int
    gc_collections: Tuple[int, int, int]  # gen0, gen1, gen2


class MemoryProfiler:
    """Memory profiler for monitoring application memory usage."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.memory_stats: List[MemoryStats] = []
        self.peak_memory = 0.0
        self.tracemalloc_enabled = False
        
        # Memory thresholds (MB)
        self.warning_threshold = 1024  # 1GB
        self.critical_threshold = 2048  # 2GB
        
        # GC tuning
        self.gc_thresholds = {
            0: 700,   # gen0
            1: 10,    # gen1  
            2: 10     # gen2
        }
    
    def start_tracing(self):
        """Start memory tracing."""
        if not self.tracemalloc_enabled:
            tracemalloc.start()
            self.tracemalloc_enabled = True
            self.logger.info("Memory tracing started")
    
    def stop_tracing(self):
        """Stop memory tracing."""
        if self.tracemalloc_enabled:
            tracemalloc.stop()
            self.tracemalloc_enabled = False
            self.logger.info("Memory tracing stopped")
    
    def get_memory_stats(self) -> MemoryStats:
        """Get current memory statistics."""
        process = psutil.Process()
        memory_info = process.memory_info()
        
        # Convert to MB
        process_memory_mb = memory_info.rss / 1024 / 1024
        system_memory_mb = psutil.virtual_memory().total / 1024 / 1024
        memory_percent = process.memory_percent()
        
        # Update peak memory
        if process_memory_mb > self.peak_memory:
            self.peak_memory = process_memory_mb
        
        # GC statistics
        gc_stats = gc.get_stats()
        gc_collections = (gc_stats[0]['collections'], gc_stats[1]['collections'], gc_stats[2]['collections'])
        
        stats = MemoryStats(
            timestamp=datetime.now(),
            process_memory_mb=process_memory_mb,
            system_memory_mb=system_memory_mb,
            memory_percent=memory_percent,
            peak_memory_mb=self.peak_memory,
            gc_objects=len(gc.get_objects()),
            gc_collections=gc_collections
        )
        
        self.memory_stats.append(stats)
        
        # Check thresholds
        if process_memory_mb > self.critical_threshold:
            self.logger.critical(f"Critical memory usage: {process_memory_mb:.1f}MB")
        elif process_memory_mb > self.warning_threshold:
            self.logger.warning(f"High memory usage: {process_memory_mb:.1f}MB")
        
        return stats
    
    def optimize_gc(self):
        """Optimize garbage collection settings."""
        gc.set_threshold(*self.gc_thresholds.values())
        self.logger.info(f"GC thresholds set to: {self.gc_thresholds}")
    
    def force_gc(self):
        """Force garbage collection."""
        collected = gc.collect()
        self.logger.debug(f"Garbage collection freed {collected} objects")
        return collected
    
    def get_memory_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get memory usage summary for the last N hours."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_stats = [s for s in self.memory_stats if s.timestamp >= cutoff_time]
        
        if not recent_stats:
            return {'message': 'No memory statistics available'}
        
        memory_values = [s.process_memory_mb for s in recent_stats]
        
        return {
            'current_memory_mb': recent_stats[-1].process_memory_mb if recent_stats else 0,
            'peak_memory_mb': max(memory_values),
            'avg_memory_mb': sum(memory_values) / len(memory_values),
            'memory_growth_mb': memory_values[-1] - memory_values[0] if len(memory_values) > 1 else 0,
            'gc_objects': recent_stats[-1].gc_objects if recent_stats else 0,
            'sample_count': len(recent_stats)
        }
    
    @contextmanager
    def monitor_memory(self, operation_name: str):
        """Context manager for monitoring memory usage during an operation."""
        self.start_tracing()
        start_stats = self.get_memory_stats()
        start_memory = start_stats.process_memory_mb
        
        self.logger.info(f"Starting memory monitoring for: {operation_name}")
        
        try:
            yield
        finally:
            end_stats = self.get_memory_stats()
            end_memory = end_stats.process_memory_mb
            memory_diff = end_memory - start_memory
            
            self.logger.info(
                f"Memory monitoring completed for {operation_name}: "
                f"{memory_diff:+.1f}MB (start: {start_memory:.1f}MB, end: {end_memory:.1f}MB)"
            )
            
            if memory_diff > 100:  # More than 100MB increase
                self.logger.warning(f"Significant memory increase during {operation_name}: {memory_diff:.1f}MB")


class DataStreamer:
    """Data streaming for large datasets to reduce memory usage."""
    
    def __init__(self, chunk_size: int = 10000):
        self.chunk_size = chunk_size
        self.logger = logging.getLogger(__name__)
    
    def stream_minute_data(self, product: str, start_date: str, end_date: str,
                          query_optimizer=None) -> Iterator[pd.DataFrame]:
        """
        Stream minute data in chunks to reduce memory usage.
        
        Args:
            product: Product symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            query_optimizer: QueryOptimizer instance
            
        Yields:
            DataFrames containing chunks of minute data
        """
        if not query_optimizer:
            from .query_optimizer import get_query_optimizer
            query_optimizer = get_query_optimizer()
        
        # Calculate date range for chunking
        start_dt = pd.to_datetime(start_date)
        end_dt = pd.to_datetime(end_date)
        
        # Stream by month to avoid huge queries
        current_date = start_dt
        while current_date <= end_dt:
            chunk_end = min(current_date + timedelta(days=30), end_dt)
            
            sql = query_optimizer.optimize_minute_data_query(
                product, current_date.strftime('%Y-%m-%d'), 
                chunk_end.strftime('%Y-%m-%d')
            )
            
            params = {
                'product': product,
                'start_date': current_date.strftime('%Y-%m-%d'),
                'end_date': chunk_end.strftime('%Y-%m-%d'),
                'interval': 1
            }
            
            try:
                chunk_data = query_optimizer.execute_query(sql, params)
                
                if not chunk_data.empty:
                    self.logger.debug(f"Streamed chunk: {len(chunk_data)} rows for {current_date.date()}")
                    yield chunk_data
                
                # Force garbage collection after each chunk
                gc.collect()
                
            except Exception as e:
                self.logger.error(f"Error streaming chunk for {current_date.date()}: {e}")
                continue
            
            current_date = chunk_end + timedelta(days=1)
    
    def stream_daily_data(self, product: str, start_date: str, end_date: str,
                         query_optimizer=None) -> Iterator[pd.DataFrame]:
        """
        Stream daily data in chunks.
        
        Args:
            product: Product symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            query_optimizer: QueryOptimizer instance
            
        Yields:
            DataFrames containing chunks of daily data
        """
        if not query_optimizer:
            from .query_optimizer import get_query_optimizer
            query_optimizer = get_query_optimizer()
        
        # For daily data, we can use larger chunks (1 year)
        start_dt = pd.to_datetime(start_date)
        end_dt = pd.to_datetime(end_date)
        
        current_date = start_dt
        while current_date <= end_dt:
            chunk_end = min(current_date + timedelta(days=365), end_dt)
            
            sql = query_optimizer.optimize_daily_data_query(
                product, current_date.strftime('%Y-%m-%d'), 
                chunk_end.strftime('%Y-%m-%d')
            )
            
            params = {
                'product': product,
                'start_date': current_date.strftime('%Y-%m-%d'),
                'end_date': chunk_end.strftime('%Y-%m-%d')
            }
            
            try:
                chunk_data = query_optimizer.execute_query(sql, params)
                
                if not chunk_data.empty:
                    self.logger.debug(f"Streamed daily chunk: {len(chunk_data)} rows for {current_date.year}")
                    yield chunk_data
                
                gc.collect()
                
            except Exception as e:
                self.logger.error(f"Error streaming daily chunk for {current_date.year}: {e}")
                continue
            
            current_date = chunk_end + timedelta(days=1)
    
    def process_large_dataset(self, data_stream: Iterator[pd.DataFrame], 
                            processor_func, **kwargs) -> pd.DataFrame:
        """
        Process a large dataset in streaming fashion.
        
        Args:
            data_stream: Iterator of DataFrames
            processor_func: Function to process each chunk
            **kwargs: Additional arguments for processor function
            
        Returns:
            Combined results from all chunks
        """
        results = []
        
        for chunk in data_stream:
            try:
                # Process chunk
                processed_chunk = processor_func(chunk, **kwargs)
                results.append(processed_chunk)
                
                # Log progress
                self.logger.debug(f"Processed chunk: {len(chunk)} rows")
                
                # Force cleanup
                del chunk
                gc.collect()
                
            except Exception as e:
                self.logger.error(f"Error processing chunk: {e}")
                continue
        
        if results:
            # Combine results
            combined = pd.concat(results, ignore_index=True)
            self.logger.info(f"Combined {len(results)} chunks into {len(combined)} rows")
            return combined
        else:
            self.logger.warning("No data processed")
            return pd.DataFrame()


class MemoryOptimizer:
    """Memory optimization utilities."""
    
    @staticmethod
    def optimize_dataframe_memory(df: pd.DataFrame) -> pd.DataFrame:
        """
        Optimize DataFrame memory usage by downcasting numeric types.
        
        Args:
            df: Input DataFrame
            
        Returns:
            Memory-optimized DataFrame
        """
        original_memory = df.memory_usage(deep=True).sum() / 1024**2
        
        # Downcast integers
        for col in df.select_dtypes(include=['int64']).columns:
            df[col] = pd.to_numeric(df[col], downcast='integer')
        
        # Downcast floats
        for col in df.select_dtypes(include=['float64']).columns:
            df[col] = pd.to_numeric(df[col], downcast='float')
        
        # Optimize datetime columns
        for col in df.select_dtypes(include=['datetime64[ns]']).columns:
            df[col] = pd.to_datetime(df[col], infer_datetime_format=True)
        
        # Optimize categorical columns
        for col in df.select_dtypes(include=['object']).columns:
            if df[col].nunique() / len(df) < 0.5:  # Less than 50% unique values
                df[col] = df[col].astype('category')
        
        optimized_memory = df.memory_usage(deep=True).sum() / 1024**2
        reduction = (original_memory - optimized_memory) / original_memory * 100
        
        logging.getLogger(__name__).info(
            f"Memory optimization: {original_memory:.1f}MB -> {optimized_memory:.1f}MB "
            f"({reduction:.1f}% reduction)"
        )
        
        return df
    
    @staticmethod
    def cleanup_large_objects(*objects):
        """Clean up large objects and force garbage collection."""
        for obj in objects:
            if obj is not None:
                del obj
        
        collected = gc.collect()
        logging.getLogger(__name__).debug(f"Cleaned up {len(objects)} objects, freed {collected} items")


# Global instances
_memory_profiler = None
_data_streamer = None


def get_memory_profiler() -> MemoryProfiler:
    """Get the global memory profiler instance."""
    global _memory_profiler
    if _memory_profiler is None:
        _memory_profiler = MemoryProfiler()
    return _memory_profiler


def get_data_streamer() -> DataStreamer:
    """Get the global data streamer instance."""
    global _data_streamer
    if _data_streamer is None:
        _data_streamer = DataStreamer()
    return _data_streamer
