"""
Data Filtering Functions

Functions for applying conditional filters to intraday data based on various criteria.
"""

import pandas as pd
from typing import Optional, List
from ..data_sources.calendar import get_previous_trading_day
from ..data_sources.economic_events import is_economic_event_date


def trim_extremes(df: pd.DataFrame, lower_quantile: float = 0.05, upper_quantile: float = 0.95) -> pd.DataFrame:
    """
    Remove extreme values from the dataset based on quantiles.
    
    Args:
        df: DataFrame with 'pct_chg' and 'rng' columns
        lower_quantile: Lower quantile threshold (default 0.05 = bottom 5%)
        upper_quantile: Upper quantile threshold (default 0.95 = top 5%)
        
    Returns:
        Filtered DataFrame with extremes removed
    """
    if 'pct_chg' not in df.columns or 'rng' not in df.columns:
        return df
    
    low_pc, high_pc = df['pct_chg'].quantile([lower_quantile, upper_quantile])
    low_r, high_r = df['rng'].quantile([lower_quantile, upper_quantile])
    
    trimmed = df[
        df['pct_chg'].between(low_pc, high_pc) & 
        df['rng'].between(low_r, high_r)
    ]
    
    return trimmed if not trimmed.empty else df


def apply_filters(
    minute_df: pd.DataFrame,
    daily_df: pd.DataFrame,
    filters: List[str],
    vol_threshold: Optional[float] = None,
    pct_threshold: Optional[float] = None
) -> pd.DataFrame:
    """
    Apply multiple conditional filters to minute data based on daily conditions.
    
    Args:
        minute_df: Minute-level OHLCV data
        daily_df: Daily OHLCV data with derived fields
        filters: List of filter names to apply
        vol_threshold: Relative volume threshold (e.g., 1.5 = 150% of average)
        pct_threshold: Percentage change threshold (e.g., 1.0 = 1%)
        
    Returns:
        Filtered minute DataFrame
        
    Available filters:
        - 'monday', 'tuesday', 'wednesday', 'thursday', 'friday': Day of week
        - 'prev_pos': Previous day closed higher
        - 'prev_neg': Previous day closed lower
        - 'prev_pct_pos': Previous day % change >= pct_threshold
        - 'prev_pct_neg': Previous day % change <= -pct_threshold
        - 'relvol_gt': Previous day relative volume > vol_threshold
        - 'relvol_lt': Previous day relative volume < vol_threshold
        - 'trim_extremes': Remove top/bottom 5% of returns and ranges
        - 'cpi_day': CPI release day
        - 'fomc_day': FOMC meeting day
        - 'nfp_day': Non-Farm Payrolls day
        - 'ppi_day': Producer Price Index day
        - 'retail_sales_day': Retail Sales release day
        - 'gdp_day': GDP release day
        - 'pce_day': PCE release day
        - 'major_event_day': Any major economic event day
    """
    # print(f"[DEBUG apply_filters] Input: {len(minute_df)} rows, filters={filters}")
    
    # Handle None or empty filters
    if filters is None:
        filters = []
    
    df = minute_df.copy()
    df['date'] = df['time'].dt.date
    
    # Add previous date using proper trading calendar
    df['prev_date'] = df['date'].apply(lambda d: get_previous_trading_day(d))
    
    # Prepare daily data with previous day metrics
    daily_df = _prepare_daily_with_prev(daily_df)
    
    # Merge minute data with previous day information
    prev_cols = ['date', 'p_open', 'p_close', 'p_volume', 'p_volume_sma_10', 'p_return_pct']
    df = df.merge(
        daily_df[prev_cols],
        left_on='prev_date',
        right_on='date',
        how='left',
        suffixes=('', '_daily')
    )
    
    # Drop rows without previous day data
    df = df.dropna(subset=['p_open'])
    
    # Apply weekday filters
    weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
    selected_days = [f for f in filters if f in weekdays]
    
    if selected_days and set(selected_days) != set(weekdays):
        df = df[df['time'].dt.day_name().str.lower().isin(selected_days)]
    
    # Apply economic event filters
    economic_event_filters = {
        'cpi_day': 'CPI',
        'fomc_day': 'FOMC',
        'nfp_day': 'NFP',
        'ppi_day': 'PPI',
        'retail_sales_day': 'RETAIL_SALES',
        'gdp_day': 'GDP',
        'pce_day': 'PCE'
    }
    
    for filter_name, event_type in economic_event_filters.items():
        if filter_name in filters:
            df = df[df['date'].apply(lambda d: is_economic_event_date(d, event_type))]
    
    # Apply major event day filter (any economic event)
    if 'major_event_day' in filters:
        from ..data_sources.economic_events import get_all_major_event_dates
        major_dates = get_all_major_event_dates()
        df = df[df['date'].apply(lambda d: d.strftime('%Y-%m-%d') in major_dates)]
    
    # Apply previous-day direction filters
    if 'prev_pos' in filters:
        df = df[df['p_close'] > df['p_open']]
    
    if 'prev_neg' in filters:
        df = df[df['p_close'] < df['p_open']]
    
    # Apply previous-day percentage change filters
    if 'prev_pct_pos' in filters and pct_threshold is not None:
        df = df[df['p_return_pct'] >= pct_threshold]
    
    if 'prev_pct_neg' in filters and pct_threshold is not None:
        df = df[df['p_return_pct'] <= -pct_threshold]
    
    # Apply relative volume filters
    df['p_relvol'] = df['p_volume'] / df['p_volume_sma_10']
    
    if 'relvol_gt' in filters and vol_threshold is not None:
        df = df[df['p_relvol'] > vol_threshold]
    
    if 'relvol_lt' in filters and vol_threshold is not None:
        df = df[df['p_relvol'] < vol_threshold]
    
    # Apply extreme trimming if requested
    if 'trim_extremes' in filters:
        df['pct_chg'] = (df['close'] - df['open']) / df['open']
        df['rng'] = df['high'] - df['low']
        df = trim_extremes(df)
    
    # print(f"[DEBUG apply_filters] Output: {len(df)} rows")
    return df


def _prepare_daily_with_prev(daily_df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare daily data with previous day metrics.
    
    Args:
        daily_df: Daily OHLCV DataFrame
        
    Returns:
        DataFrame with previous day columns prefixed with 'p_'
    """
    df = daily_df.copy()
    
    # Ensure we have required computed fields
    if 'volume_sma_10' not in df.columns:
        df['volume_sma_10'] = df['volume'].rolling(10, min_periods=1).mean()
    
    if 'day_return_pct' not in df.columns:
        df['day_return_pct'] = ((df['close'] - df['open']) / df['open']) * 100
    
    # Get previous day using proper trading calendar
    df['prev_date'] = df['date'].apply(lambda d: get_previous_trading_day(d))
    
    # Create a mapping from date to metrics
    date_index = df.set_index('date')
    
    # Map previous day metrics
    df['p_open'] = df['prev_date'].map(date_index['open'])
    df['p_close'] = df['prev_date'].map(date_index['close'])
    df['p_volume'] = df['prev_date'].map(date_index['volume'])
    df['p_volume_sma_10'] = df['prev_date'].map(date_index['volume_sma_10'])
    df['p_return_pct'] = df['prev_date'].map(date_index['day_return_pct'])
    
    return df


def apply_time_filters(
    df: pd.DataFrame,
    filters: List[str],
    time_a_hour: Optional[int] = None,
    time_a_minute: Optional[int] = None,
    time_b_hour: Optional[int] = None,
    time_b_minute: Optional[int] = None
) -> pd.DataFrame:
    """
    Apply time-based comparison filters (e.g., price at time A vs time B).
    
    Args:
        df: Minute-level DataFrame
        filters: List of filters ('timeA_gt_timeB', 'timeA_lt_timeB')
        time_a_hour: Hour for time A
        time_a_minute: Minute for time A
        time_b_hour: Hour for time B
        time_b_minute: Minute for time B
        
    Returns:
        Filtered DataFrame
    """
    if not any(f in filters for f in ['timeA_gt_timeB', 'timeA_lt_timeB']):
        return df
    
    if any(x is None for x in [time_a_hour, time_a_minute, time_b_hour, time_b_minute]):
        return df
    
    df = df.copy()
    df['date'] = df['time'].dt.date
    
    # Extract prices at specified times
    price_a = df[
        (df['time'].dt.hour == time_a_hour) & 
        (df['time'].dt.minute == time_a_minute)
    ].set_index('date')['close'].rename('price_a')
    
    price_b = df[
        (df['time'].dt.hour == time_b_hour) & 
        (df['time'].dt.minute == time_b_minute)
    ].set_index('date')['close'].rename('price_b')
    
    # Merge prices with main dataframe
    df = df.merge(price_a, left_on='date', right_index=True, how='left')
    df = df.merge(price_b, left_on='date', right_index=True, how='left')
    
    # Apply filters
    if 'timeA_gt_timeB' in filters:
        df = df[df['price_a'] > df['price_b']]
    
    if 'timeA_lt_timeB' in filters:
        df = df[df['price_a'] < df['price_b']]
    
    return df

