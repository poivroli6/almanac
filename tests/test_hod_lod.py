"""
Tests for HOD/LOD Detection

Tests high-of-day and low-of-day analysis functions.
"""

import pytest
import pandas as pd
from almanac.features.hod_lod import (
    detect_hod_lod,
    compute_survival_curves,
    compute_trend_test,
)


def test_detect_hod_lod(sample_minute_data):
    """Test HOD/LOD detection."""
    result = detect_hod_lod(sample_minute_data)
    
    # Should return a dataframe
    assert isinstance(result, pd.DataFrame)
    
    # Should have expected columns
    assert 'date' in result.columns
    assert 'hod_time' in result.columns
    assert 'lod_time' in result.columns
    assert 'hod_price' in result.columns
    assert 'lod_price' in result.columns
    
    # Should have one row per unique date
    sample_minute_data['date'] = sample_minute_data['time'].dt.date
    expected_days = sample_minute_data['date'].nunique()
    assert len(result) == expected_days
    
    # HOD price should be >= LOD price
    assert (result['hod_price'] >= result['lod_price']).all()


def test_compute_survival_curves(sample_hod_lod_data):
    """Test survival curve computation."""
    # Add required columns
    df = sample_hod_lod_data.copy()
    df['hod_minutes_since_midnight'] = df['hod_time'].dt.hour * 60 + df['hod_time'].dt.minute
    df['lod_minutes_since_midnight'] = df['lod_time'].dt.hour * 60 + df['lod_time'].dt.minute
    
    hod_surv, lod_surv = compute_survival_curves(df)
    
    # Should return dataframes
    assert isinstance(hod_surv, pd.DataFrame)
    assert isinstance(lod_surv, pd.DataFrame)
    
    # Should have required columns
    assert 'minutes' in hod_surv.columns
    assert 'probability' in hod_surv.columns
    
    # Probabilities should be between 0 and 1
    assert (hod_surv['probability'] >= 0).all()
    assert (hod_surv['probability'] <= 1).all()
    
    # Probabilities should be monotonically increasing
    assert (hod_surv['probability'].diff().dropna() >= 0).all()


def test_compute_trend_test_increasing():
    """Test trend detection on increasing series."""
    # Create clearly increasing series
    series = pd.Series(range(50))
    
    result = compute_trend_test(series)
    
    # Should detect increasing trend
    assert 'trend' in result
    assert 'p_value' in result
    assert 'slope' in result
    
    if result['trend'] != 'scipy_not_installed':
        assert result['trend'] == 'increasing'
        assert result['slope'] > 0


def test_compute_trend_test_no_trend():
    """Test trend detection on random series."""
    import numpy as np
    np.random.seed(42)
    series = pd.Series(np.random.randn(50))
    
    result = compute_trend_test(series)
    
    # Should not detect significant trend
    if result['trend'] != 'scipy_not_installed':
        assert result['trend'] in ['no_trend', 'increasing', 'decreasing']


def test_detect_hod_lod_empty():
    """Test HOD/LOD detection with empty dataframe."""
    empty_df = pd.DataFrame(columns=['time', 'high', 'low'])
    
    with pytest.raises(Exception):
        detect_hod_lod(empty_df)

