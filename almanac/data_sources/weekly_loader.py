"""
Weekly Data Loader

Loads and processes weekly OHLCV data from daily data aggregation.
"""

import pandas as pd
from typing import Optional
from datetime import datetime
import numpy as np

from .daily_loader import load_daily_data


def load_weekly_data(
    product: str,
    start_date: str | datetime,
    end_date: str | datetime,
    add_derived_fields: bool = True,
    use_files: bool = True
) -> pd.DataFrame:
    """
    Load weekly OHLCV data by aggregating daily data.
    
    Args:
        product: Contract ID (e.g., 'ES', 'NQ', 'GC')
        start_date: Start date (YYYY-MM-DD or datetime)
        end_date: End date (YYYY-MM-DD or datetime)
        add_derived_fields: Whether to add derived fields
        use_files: Whether to try loading from files first (default True)
        
    Returns:
        DataFrame with columns: week_start, week_end, open, high, low, close, volume, weekday
        
    Raises:
        ValueError: If no data found
    """
    # Load daily data first
    daily_df = load_daily_data(product, start_date, end_date, add_derived_fields, use_files)
    
    if daily_df.empty:
        raise ValueError(f"No daily data found for {product} between {start_date} and {end_date}")
    
    # Convert date to datetime if needed
    if 'date' in daily_df.columns:
        daily_df['date'] = pd.to_datetime(daily_df['date'])
    elif 'time' in daily_df.columns:
        daily_df['date'] = pd.to_datetime(daily_df['time'])
    
    # Add weekday information
    daily_df['weekday'] = daily_df['date'].dt.day_name()
    daily_df['weekday_num'] = daily_df['date'].dt.dayofweek  # Monday=0, Sunday=6
    
    # Create week identifier (Monday as start of week)
    daily_df['week_start'] = daily_df['date'] - pd.to_timedelta(daily_df['date'].dt.dayofweek, unit='D')
    
    # Group by week and aggregate
    weekly_data = []
    
    for week_start, week_group in daily_df.groupby('week_start'):
        if len(week_group) == 0:
            continue
            
        # Sort by date within the week
        week_group = week_group.sort_values('date')
        
        # Weekly OHLCV aggregation
        week_open = week_group.iloc[0]['open']
        week_high = week_group['high'].max()
        week_low = week_group['low'].min()
        week_close = week_group.iloc[-1]['close']
        week_volume = week_group['volume'].sum()
        
        # Get the weekday names in this week
        weekdays = week_group['weekday'].tolist()
        
        # Find the best performing day (highest close-to-open percentage change)
        week_group['pct_change'] = (week_group['close'] - week_group['open']) / week_group['open']
        best_day_idx = week_group['pct_change'].idxmax()
        best_day = week_group.loc[best_day_idx, 'weekday']
        best_pct_change = week_group.loc[best_day_idx, 'pct_change']
        
        # Find the worst performing day
        worst_day_idx = week_group['pct_change'].idxmin()
        worst_day = week_group.loc[worst_day_idx, 'weekday']
        worst_pct_change = week_group.loc[worst_day_idx, 'pct_change']
        
        weekly_data.append({
            'week_start': week_start,
            'week_end': week_group['date'].max(),
            'open': week_open,
            'high': week_high,
            'low': week_low,
            'close': week_close,
            'volume': week_volume,
            'weekdays': ', '.join(weekdays),
            'best_day': best_day,
            'best_pct_change': best_pct_change,
            'worst_day': worst_day,
            'worst_pct_change': worst_pct_change,
            'week_pct_change': (week_close - week_open) / week_open,
            'week_range': week_high - week_low,
            'avg_daily_volume': week_group['volume'].mean(),
            'trading_days': len(week_group)
        })
    
    weekly_df = pd.DataFrame(weekly_data)
    
    if weekly_df.empty:
        raise ValueError(f"No weekly data could be created for {product} between {start_date} and {end_date}")
    
    # Sort by week start date
    weekly_df = weekly_df.sort_values('week_start').reset_index(drop=True)
    
    if add_derived_fields:
        weekly_df = _add_weekly_derived_fields(weekly_df)
    
    print(f"Loaded {len(weekly_df):,} weekly bars for {product} from {weekly_df['week_start'].min().date()} to {weekly_df['week_end'].max().date()}")
    
    return weekly_df


def _add_weekly_derived_fields(df: pd.DataFrame) -> pd.DataFrame:
    """Add commonly used derived fields to weekly data."""
    df = df.copy()
    
    # Rolling averages
    df['vol_ma_4'] = df['volume'].rolling(window=4, min_periods=1).mean()
    df['vol_ma_13'] = df['volume'].rolling(window=13, min_periods=1).mean()
    
    # Relative volume
    df['rel_vol'] = df['volume'] / df['vol_ma_4']
    
    # Weekly range as percentage of open
    df['range_pct'] = df['week_range'] / df['open']
    
    # Volatility (standard deviation of daily changes within week)
    # This would require daily data, so we'll use weekly range as proxy
    df['volatility_proxy'] = df['range_pct']
    
    return df


def get_weekly_day_performance_stats(weekly_df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyze which day of the week performs best based on weekly data.
    
    Args:
        weekly_df: DataFrame with weekly data including best_day and worst_day columns
        
    Returns:
        DataFrame with day-of-week performance statistics
    """
    if weekly_df.empty:
        return pd.DataFrame()
    
    # Count occurrences of each day as best/worst
    best_day_counts = weekly_df['best_day'].value_counts()
    worst_day_counts = weekly_df['worst_day'].value_counts()
    
    # Calculate average performance by day
    day_stats = []
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    for day in days:
        # Count how many times this day was best/worst
        best_count = best_day_counts.get(day, 0)
        worst_count = worst_day_counts.get(day, 0)
        total_weeks = len(weekly_df)
        
        # Calculate percentages
        best_pct = (best_count / total_weeks) * 100 if total_weeks > 0 else 0
        worst_pct = (worst_count / total_weeks) * 100 if total_weeks > 0 else 0
        
        # Calculate average performance when this day was best
        best_performance = weekly_df[weekly_df['best_day'] == day]['best_pct_change'].mean()
        worst_performance = weekly_df[weekly_df['worst_day'] == day]['worst_pct_change'].mean()
        
        day_stats.append({
            'day': day,
            'best_count': best_count,
            'worst_count': worst_count,
            'best_percentage': best_pct,
            'worst_percentage': worst_pct,
            'avg_best_performance': best_performance if not pd.isna(best_performance) else 0,
            'avg_worst_performance': worst_performance if not pd.isna(worst_performance) else 0,
            'net_score': best_pct - worst_pct,  # Positive means more likely to be best than worst
            'total_weeks': total_weeks
        })
    
    result_df = pd.DataFrame(day_stats)
    result_df = result_df.sort_values('net_score', ascending=False)
    
    return result_df
