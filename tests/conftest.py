"""
Pytest Configuration and Fixtures

Provides reusable test data and fixtures for all tests.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


@pytest.fixture
def sample_minute_data():
    """
    Create sample minute-level OHLCV data for testing.
    
    Returns 2 days of data with 60 minutes per day.
    """
    dates = pd.date_range('2025-01-02 09:00', periods=120, freq='1min')
    
    np.random.seed(42)
    opens = 100 + np.random.randn(120) * 0.5
    
    df = pd.DataFrame({
        'time': dates,
        'open': opens,
        'high': opens + np.abs(np.random.randn(120) * 0.3),
        'low': opens - np.abs(np.random.randn(120) * 0.3),
        'close': opens + np.random.randn(120) * 0.4,
        'volume': np.random.randint(1000, 10000, 120)
    })
    
    # Ensure OHLC relationships are valid
    df['high'] = df[['open', 'high', 'low', 'close']].max(axis=1)
    df['low'] = df[['open', 'high', 'low', 'close']].min(axis=1)
    
    return df


@pytest.fixture
def sample_daily_data():
    """
    Create sample daily OHLCV data for testing.
    
    Returns 30 days of data.
    """
    dates = pd.date_range('2025-01-01', periods=30, freq='D')
    
    np.random.seed(42)
    opens = 100 + np.random.randn(30) * 2
    
    df = pd.DataFrame({
        'time': dates,
        'date': [d.date() for d in dates],
        'open': opens,
        'high': opens + np.abs(np.random.randn(30)),
        'low': opens - np.abs(np.random.randn(30)),
        'close': opens + np.random.randn(30) * 1.5,
        'volume': np.random.randint(100000, 500000, 30)
    })
    
    # Ensure OHLC relationships are valid
    df['high'] = df[['open', 'high', 'low', 'close']].max(axis=1)
    df['low'] = df[['open', 'high', 'low', 'close']].min(axis=1)
    
    # Add derived fields
    df['is_green'] = df['close'] > df['open']
    df['day_return_pct'] = ((df['close'] - df['open']) / df['open']) * 100
    df['volume_sma_10'] = df['volume'].rolling(10, min_periods=1).mean()
    df['weekday'] = df['date'].apply(lambda d: pd.Timestamp(d).day_name())
    
    return df


@pytest.fixture
def sample_hod_lod_data():
    """
    Create sample HOD/LOD detection data.
    """
    dates = pd.date_range('2025-01-01', periods=10, freq='D')
    
    df = pd.DataFrame({
        'date': [d.date() for d in dates],
        'hod_time': [
            pd.Timestamp(f'{d.date()} {np.random.randint(9, 15)}:{np.random.randint(0, 59)}:00')
            for d in dates
        ],
        'lod_time': [
            pd.Timestamp(f'{d.date()} {np.random.randint(9, 15)}:{np.random.randint(0, 59)}:00')
            for d in dates
        ],
        'hod_price': 100 + np.random.randn(10) * 2,
        'lod_price': 98 + np.random.randn(10) * 2,
    })
    
    return df


@pytest.fixture
def empty_dataframe():
    """Create an empty DataFrame with expected columns."""
    return pd.DataFrame(columns=['time', 'open', 'high', 'low', 'close', 'volume'])

