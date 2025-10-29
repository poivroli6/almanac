"""
Tests for Features Module

Tests statistical computations and feature engineering functions.
"""

import pytest
import pandas as pd
import numpy as np
from almanac.features import (
    compute_hourly_stats,
    compute_minute_stats,
    trim_extremes,
)


def test_compute_hourly_stats(sample_minute_data):
    """Test hourly statistics computation."""
    result = compute_hourly_stats(sample_minute_data)
    
    # Check we get 10 return values
    assert len(result) == 10
    
    avg_pct, trimmed_pct, med_pct, mode_pct, var_pct, avg_rng, trimmed_rng, med_rng, mode_rng, var_rng = result
    
    # Check return types
    assert isinstance(avg_pct, pd.Series)
    assert isinstance(var_pct, pd.Series)
    assert isinstance(avg_rng, pd.Series)
    assert isinstance(var_rng, pd.Series)
    
    # Check that we have hourly data
    assert len(avg_pct) > 0
    
    # Check that values are numeric
    assert not avg_pct.isnull().all()
    assert not avg_rng.isnull().all()


def test_compute_minute_stats(sample_minute_data):
    """Test minute-level statistics for a specific hour."""
    hour = 9
    result = compute_minute_stats(sample_minute_data, hour)
    
    # Check we get 10 return values
    assert len(result) == 10
    
    avg_pct, trimmed_pct, med_pct, mode_pct, var_pct, avg_rng, trimmed_rng, med_rng, mode_rng, var_rng = result
    
    # Check return types
    assert isinstance(avg_pct, pd.Series)
    
    # If data exists for this hour, should have results
    hour_data = sample_minute_data[sample_minute_data['time'].dt.hour == hour]
    if not hour_data.empty:
        assert len(avg_pct) > 0


def test_compute_minute_stats_empty_hour(sample_minute_data):
    """Test minute stats for hour with no data."""
    hour = 23  # No data at this hour in sample
    result = compute_minute_stats(sample_minute_data, hour)
    
    # Check we get 10 return values
    assert len(result) == 10
    
    avg_pct, trimmed_pct, med_pct, mode_pct, var_pct, avg_rng, trimmed_rng, med_rng, mode_rng, var_rng = result
    
    # Should return empty series
    assert len(avg_pct) == 0


def test_trim_extremes(sample_minute_data):
    """Test trimming of extreme values."""
    # Add pct_chg and rng columns
    df = sample_minute_data.copy()
    df['pct_chg'] = (df['close'] - df['open']) / df['open']
    df['rng'] = df['high'] - df['low']
    
    original_len = len(df)
    trimmed = trim_extremes(df)
    
    # Trimmed data should be smaller
    assert len(trimmed) <= original_len
    
    # Should remove roughly 10% (5% from each end) - adjust expectation for small dataset
    assert len(trimmed) >= original_len * 0.80  # More lenient for small test dataset


def test_trim_extremes_without_columns(sample_minute_data):
    """Test that trim_extremes handles missing columns gracefully."""
    # Don't add required columns
    result = trim_extremes(sample_minute_data)
    
    # Should return original dataframe unchanged
    assert len(result) == len(sample_minute_data)


def test_hourly_stats_consistency(sample_minute_data):
    """Test that hourly stats are consistent across multiple calls."""
    stats1 = compute_hourly_stats(sample_minute_data)
    stats2 = compute_hourly_stats(sample_minute_data)
    
    # Results should be identical
    pd.testing.assert_series_equal(stats1[0], stats2[0])  # avg_pct
    pd.testing.assert_series_equal(stats1[2], stats2[2])  # med_pct

