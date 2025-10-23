"""
Monthly Data Loader

Loads and processes monthly OHLCV data by aggregating daily data.
"""

import pandas as pd
import numpy as np
from typing import Optional
from datetime import datetime
from .daily_loader import load_daily_data


def load_monthly_data(
    product: str,
    start_date: str | datetime,
    end_date: str | datetime,
    add_derived_fields: bool = True
) -> pd.DataFrame:
    """
    Load monthly OHLCV data by aggregating daily data.
    
    Args:
        product: Contract ID (e.g., 'ES', 'NQ', 'GC')
        start_date: Start date (YYYY-MM-DD or datetime)
        end_date: End date (YYYY-MM-DD or datetime)
        add_derived_fields: Whether to add derived fields (month, year, etc.)
        
    Returns:
        DataFrame with columns: time, open, high, low, close, volume, month, year, month_name
        
    Raises:
        ValueError: If no data found
    """
    # Load daily data first
    daily_df = load_daily_data(product, start_date, end_date, add_derived_fields=True)
    
    if daily_df.empty:
        raise ValueError(f"No daily data found for {product} between {start_date} and {end_date}")
    
    # Convert to datetime if needed
    if not pd.api.types.is_datetime64_any_dtype(daily_df['time']):
        daily_df['time'] = pd.to_datetime(daily_df['time'])
    
    # Add month and year columns
    daily_df['month'] = daily_df['time'].dt.month
    daily_df['year'] = daily_df['time'].dt.year
    daily_df['month_name'] = daily_df['time'].dt.month_name()
    daily_df['year_month'] = daily_df['time'].dt.to_period('M')
    
    # Group by month and aggregate
    monthly_data = []
    
    for (year, month), group in daily_df.groupby(['year', 'month']):
        if group.empty:
            continue
            
        # Monthly OHLCV aggregation
        month_open = group.iloc[0]['open']  # First day's open
        month_close = group.iloc[-1]['close']  # Last day's close
        month_high = group['high'].max()  # Highest high
        month_low = group['low'].min()  # Lowest low
        month_volume = group['volume'].sum()  # Total volume
        
        # Calculate monthly metrics
        month_return = (month_close - month_open) / month_open if month_open != 0 else 0
        month_range = month_high - month_low
        month_range_pct = month_range / month_open if month_open != 0 else 0
        
        # Calculate volatility (standard deviation of daily returns)
        daily_returns = group['close'].pct_change().dropna()
        month_volatility = daily_returns.std() if len(daily_returns) > 1 else 0
        
        # Count trading days
        trading_days = len(group)
        
        # Create monthly record
        monthly_record = {
            'time': pd.Timestamp(year=year, month=month, day=1),  # First day of month
            'open': month_open,
            'high': month_high,
            'low': month_low,
            'close': month_close,
            'volume': month_volume,
            'month': month,
            'year': year,
            'month_name': group.iloc[0]['month_name'],
            'year_month': group.iloc[0]['year_month'],
            'return_pct': month_return,
            'range': month_range,
            'range_pct': month_range_pct,
            'volatility': month_volatility,
            'trading_days': trading_days
        }
        
        monthly_data.append(monthly_record)
    
    # Create DataFrame
    monthly_df = pd.DataFrame(monthly_data)
    
    if monthly_df.empty:
        raise ValueError(f"No monthly data could be created for {product} between {start_date} and {end_date}")
    
    # Sort by time
    monthly_df = monthly_df.sort_values('time').reset_index(drop=True)
    
    # Add additional derived fields if requested
    if add_derived_fields:
        # Add month abbreviation
        monthly_df['month_abbr'] = monthly_df['time'].dt.strftime('%b')
        
        # Add quarter
        monthly_df['quarter'] = monthly_df['time'].dt.quarter
        
        # Add season
        def get_season(month):
            if month in [12, 1, 2]:
                return 'Winter'
            elif month in [3, 4, 5]:
                return 'Spring'
            elif month in [6, 7, 8]:
                return 'Summer'
            else:
                return 'Fall'
        
        monthly_df['season'] = monthly_df['month'].apply(get_season)
        
        # Add performance ranking within year
        monthly_df['year_rank'] = monthly_df.groupby('year')['return_pct'].rank(ascending=False)
        
        # Add rolling statistics
        monthly_df['return_ma_3'] = monthly_df['return_pct'].rolling(window=3, min_periods=1).mean()
        monthly_df['return_ma_6'] = monthly_df['return_pct'].rolling(window=6, min_periods=1).mean()
        monthly_df['return_ma_12'] = monthly_df['return_pct'].rolling(window=12, min_periods=1).mean()
        
        # Add volatility ranking
        monthly_df['volatility_rank'] = monthly_df.groupby('year')['volatility'].rank(ascending=False)
    
    return monthly_df


def get_monthly_performance_summary(monthly_df: pd.DataFrame) -> dict:
    """
    Get summary statistics for monthly performance analysis.
    
    Args:
        monthly_df: DataFrame from load_monthly_data()
        
    Returns:
        Dictionary with performance metrics by month
    """
    if monthly_df.empty:
        return {}
    
    # Group by month and calculate statistics
    monthly_stats = monthly_df.groupby('month').agg({
        'return_pct': ['mean', 'median', 'std', 'min', 'max', 'count'],
        'range_pct': ['mean', 'median', 'std'],
        'volatility': ['mean', 'median', 'std'],
        'volume': ['mean', 'median', 'sum']
    }).round(4)
    
    # Flatten column names
    monthly_stats.columns = ['_'.join(col).strip() for col in monthly_stats.columns]
    
    # Add month names
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    monthly_stats['month_name'] = [month_names[i-1] for i in monthly_stats.index]
    
    # Calculate win rate (positive returns)
    win_rates = monthly_df.groupby('month')['return_pct'].apply(
        lambda x: (x > 0).sum() / len(x) * 100
    )
    monthly_stats['win_rate'] = win_rates.round(2)
    
    # Calculate best and worst months
    best_month = monthly_stats['return_pct_mean'].idxmax()
    worst_month = monthly_stats['return_pct_mean'].idxmin()
    
    return {
        'monthly_stats': monthly_stats,
        'best_month': best_month,
        'worst_month': worst_month,
        'best_month_name': month_names[best_month-1],
        'worst_month_name': month_names[worst_month-1],
        'total_months': len(monthly_df),
        'avg_monthly_return': monthly_df['return_pct'].mean(),
        'total_return': monthly_df['return_pct'].sum()
    }
