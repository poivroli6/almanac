"""
Weekly Statistical Computations

Functions for computing weekly-level statistics and day-of-week analysis.
"""

import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any


def compute_weekly_stats(df: pd.DataFrame, trim_pct: float = 5.0) -> Tuple[pd.Series, pd.Series, pd.Series, pd.Series, pd.Series, pd.Series, pd.Series, pd.Series, pd.Series, pd.Series]:
    """
    Compute weekly statistics from daily data aggregated by week.
    
    Args:
        df: DataFrame with columns: time, open, high, low, close
        trim_pct: Percentage to trim from top/bottom (0-50)
        
    Returns:
        Tuple of (avg_pct_change, trimmed_pct_change, med_pct_change, mode_pct_change, 
                 var_pct_change, avg_range, trimmed_range, med_range, mode_range, var_range)
        Each is a Series indexed by weekday (Monday-Sunday)
    """
    df = df.copy()
    
    # Ensure we have date column
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
    elif 'time' in df.columns:
        df['date'] = pd.to_datetime(df['time'])
    
    # Add weekday
    df['weekday'] = df['date'].dt.day_name()
    df['weekday_num'] = df['date'].dt.dayofweek
    
    # Calculate daily metrics
    df['pct_chg'] = (df['close'] - df['open']) / df['open']
    df['rng'] = df['high'] - df['low']
    
    # Group by weekday
    grp = df.groupby('weekday')
    
    # Calculate all 4 measures for percentage change
    avg_pct_chg = grp['pct_chg'].mean()
    med_pct_chg = grp['pct_chg'].median()
    
    # Optimized statistics calculation
    def calculate_all_stats(x, trim_pct):
        if len(x) < 10:
            return x.mean(), x.mean(), x.median(), x.mode().iloc[0] if len(x.mode()) > 0 else x.median()
        
        trim_low = trim_pct / 100.0
        trim_high = 1.0 - trim_low
        
        # Calculate quantiles once
        q_low, q_high = x.quantile([trim_low, trim_high])
        
        # Trimmed mean: average of values between trim percentiles
        trimmed_mean = (q_low + q_high) / 2
        
        # Mode: most frequent value
        mode_val = x.mode().iloc[0] if len(x.mode()) > 0 else x.median()
        
        return x.mean(), trimmed_mean, x.median(), mode_val
    
    # Calculate all stats in one pass per group
    stats_results = grp['pct_chg'].apply(lambda x: calculate_all_stats(x, trim_pct))
    
    # Extract results efficiently
    trimmed_pct_chg = stats_results.apply(lambda x: x[1])
    mode_pct_chg = stats_results.apply(lambda x: x[3])
    
    var_pct_chg = grp['pct_chg'].var()
    
    # Calculate all 4 measures for range
    avg_range = grp['rng'].mean()
    med_range = grp['rng'].median()
    
    # Calculate range stats in one pass
    range_stats_results = grp['rng'].apply(lambda x: calculate_all_stats(x, trim_pct))
    trimmed_range = range_stats_results.apply(lambda x: x[1])
    mode_range = range_stats_results.apply(lambda x: x[3])
    
    var_range = grp['rng'].var()
    
    # Ensure consistent weekday order (Monday to Sunday)
    weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    def reorder_series(series):
        return series.reindex(weekday_order, fill_value=0)
    
    return (reorder_series(avg_pct_chg), reorder_series(trimmed_pct_chg), reorder_series(med_pct_chg), 
            reorder_series(mode_pct_chg), reorder_series(var_pct_chg), reorder_series(avg_range), 
            reorder_series(trimmed_range), reorder_series(med_range), reorder_series(mode_range), 
            reorder_series(var_range))


def compute_weekly_day_performance(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Compute day-of-week performance analysis from daily data.
    
    Args:
        df: DataFrame with columns: time, open, high, low, close
        
    Returns:
        Dictionary with day-of-week performance statistics
    """
    df = df.copy()
    
    # Ensure we have date column
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
    elif 'time' in df.columns:
        df['date'] = pd.to_datetime(df['time'])
    
    # Add weekday
    df['weekday'] = df['date'].dt.day_name()
    df['weekday_num'] = df['date'].dt.dayofweek
    
    # Calculate daily performance
    df['pct_chg'] = (df['close'] - df['open']) / df['open']
    df['range'] = df['high'] - df['low']
    
    # Group by weekday
    weekday_stats = df.groupby('weekday').agg({
        'pct_chg': ['count', 'mean', 'median', 'std', 'min', 'max'],
        'range': ['mean', 'median', 'std'],
        'volume': ['mean', 'sum']
    }).round(6)
    
    # Flatten column names
    weekday_stats.columns = ['_'.join(col).strip() for col in weekday_stats.columns]
    weekday_stats = weekday_stats.reset_index()
    
    # Calculate additional metrics
    weekday_stats['win_rate'] = df.groupby('weekday')['pct_chg'].apply(lambda x: (x > 0).mean())
    weekday_stats['avg_win'] = df.groupby('weekday').apply(lambda x: x[x['pct_chg'] > 0]['pct_chg'].mean())
    weekday_stats['avg_loss'] = df.groupby('weekday').apply(lambda x: x[x['pct_chg'] < 0]['pct_chg'].mean())
    
    # Calculate Sharpe-like ratio (mean/std)
    weekday_stats['sharpe_ratio'] = weekday_stats['pct_chg_mean'] / weekday_stats['pct_chg_std']
    
    # Sort by average performance
    weekday_stats = weekday_stats.sort_values('pct_chg_mean', ascending=False)
    
    # Find best and worst performing days
    best_day = weekday_stats.iloc[0]['weekday']
    worst_day = weekday_stats.iloc[-1]['weekday']
    
    return {
        'weekday_stats': weekday_stats,
        'best_day': best_day,
        'worst_day': worst_day,
        'best_performance': weekday_stats.iloc[0]['pct_chg_mean'],
        'worst_performance': weekday_stats.iloc[-1]['pct_chg_mean'],
        'total_days': len(df),
        'analysis_period': f"{df['date'].min().date()} to {df['date'].max().date()}"
    }


def compute_weekly_volatility_analysis(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Compute weekly volatility patterns by day of week.
    
    Args:
        df: DataFrame with columns: time, open, high, low, close
        
    Returns:
        Dictionary with volatility analysis by day of week
    """
    df = df.copy()
    
    # Ensure we have date column
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
    elif 'time' in df.columns:
        df['date'] = pd.to_datetime(df['time'])
    
    # Add weekday
    df['weekday'] = df['date'].dt.day_name()
    
    # Calculate daily volatility metrics
    df['pct_chg'] = (df['close'] - df['open']) / df['open']
    df['range'] = df['high'] - df['low']
    df['range_pct'] = df['range'] / df['open']
    df['true_range'] = np.maximum(
        df['high'] - df['low'],
        np.maximum(
            abs(df['high'] - df['close'].shift(1)),
            abs(df['low'] - df['close'].shift(1))
        )
    )
    
    # Group by weekday and calculate volatility metrics
    vol_stats = df.groupby('weekday').agg({
        'pct_chg': ['std', 'var'],
        'range_pct': ['mean', 'std'],
        'true_range': ['mean', 'std'],
        'volume': ['mean', 'std']
    }).round(6)
    
    # Flatten column names
    vol_stats.columns = ['_'.join(col).strip() for col in vol_stats.columns]
    vol_stats = vol_stats.reset_index()
    
    # Calculate additional volatility metrics
    vol_stats['volatility_rank'] = vol_stats['pct_chg_std'].rank(ascending=False)
    vol_stats['range_rank'] = vol_stats['range_pct_mean'].rank(ascending=False)
    
    # Sort by volatility
    vol_stats = vol_stats.sort_values('pct_chg_std', ascending=False)
    
    return {
        'volatility_stats': vol_stats,
        'most_volatile_day': vol_stats.iloc[0]['weekday'],
        'least_volatile_day': vol_stats.iloc[-1]['weekday'],
        'analysis_period': f"{df['date'].min().date()} to {df['date'].max().date()}"
    }
