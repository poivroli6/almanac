"""
Tests for Data Sources Module

Tests data loading functions (using mocks to avoid database dependency).
"""

import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from almanac.data_sources.calendar import is_trading_day, get_previous_trading_day


def test_is_trading_day_weekday():
    """Test that weekdays are recognized as trading days."""
    # Monday, Jan 6, 2025
    date = pd.Timestamp('2025-01-06')
    
    # Without market calendars, should recognize weekday
    result = is_trading_day(date)
    assert result is True


def test_is_trading_day_weekend():
    """Test that weekends are not trading days."""
    # Saturday, Jan 4, 2025
    date = pd.Timestamp('2025-01-04')
    
    result = is_trading_day(date)
    assert result is False


def test_get_previous_trading_day_simple():
    """Test getting previous trading day."""
    # Tuesday, Jan 7, 2025 -> should return Monday, Jan 6
    current = pd.Timestamp('2025-01-07')
    
    prev = get_previous_trading_day(current)
    
    # Should be one business day earlier
    assert prev < current.date()


def test_get_previous_trading_day_after_weekend():
    """Test getting previous trading day after weekend."""
    # Monday, Jan 6, 2025 -> should return Friday, Jan 3
    current = pd.Timestamp('2025-01-06')
    
    prev = get_previous_trading_day(current)
    
    # Should be Friday (3 days back)
    assert prev == pd.Timestamp('2025-01-03').date()


@patch('almanac.data_sources.db_config.get_engine')
@patch('pandas.read_sql')
def test_load_minute_data_mock(mock_read_sql, mock_get_engine):
    """Test minute data loading with mock database."""
    from almanac.data_sources.minute_loader import load_minute_data
    
    # Setup mock
    mock_engine = MagicMock()
    mock_get_engine.return_value = mock_engine
    
    # Mock data
    mock_df = pd.DataFrame({
        'time': pd.date_range('2025-01-01 09:00', periods=60, freq='1min'),
        'open': [100] * 60,
        'high': [101] * 60,
        'low': [99] * 60,
        'close': [100.5] * 60,
        'volume': [1000] * 60
    })
    mock_read_sql.return_value = mock_df
    
    # Call function
    result = load_minute_data('GC', '2025-01-01', '2025-01-01', validate=False)
    
    # Verify
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 60
    assert mock_read_sql.called


@patch('almanac.data_sources.db_config.get_engine')
@patch('pandas.read_sql')
def test_load_daily_data_mock(mock_read_sql, mock_get_engine):
    """Test daily data loading with mock database."""
    from almanac.data_sources.daily_loader import load_daily_data
    
    # Setup mock
    mock_engine = MagicMock()
    mock_get_engine.return_value = mock_engine
    
    # Mock data
    mock_df = pd.DataFrame({
        'time': pd.date_range('2025-01-01', periods=10, freq='D'),
        'open': [100] * 10,
        'high': [102] * 10,
        'low': [98] * 10,
        'close': [101] * 10,
        'volume': [100000] * 10
    })
    mock_read_sql.return_value = mock_df
    
    # Call function
    result = load_daily_data('GC', '2025-01-01', '2025-01-10', add_derived_fields=False)
    
    # Verify
    assert isinstance(result, pd.DataFrame)
    # The mock returns 10 rows but the function filters to trading days, so expect fewer
    assert len(result) <= 10
    assert len(result) > 0  # Should have some data
    assert 'date' in result.columns

