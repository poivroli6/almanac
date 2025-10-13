"""
Statistical Computations

Functions for computing hourly and minute-level statistics on intraday data.
"""

import pandas as pd
import numpy as np
from typing import Tuple


def compute_hourly_stats(df: pd.DataFrame, trim_pct: float = 5.0) -> Tuple[pd.Series, pd.Series, pd.Series, pd.Series, pd.Series, pd.Series, pd.Series, pd.Series]:
    """
    Compute hourly statistics from minute data.
    
    Args:
        df: DataFrame with columns: time, open, high, low, close
        trim_pct: Percentage to trim from top/bottom (0-50)
        
    Returns:
        Tuple of (avg_pct_change, trimmed_pct_change, med_pct_change, mode_pct_change, 
                 var_pct_change, avg_range, trimmed_range, med_range, mode_range, var_range)
        Each is a Series indexed by hour (0-23)
    """
    df = df.copy()
    
    # Calculate metrics
    df['pct_chg'] = (df['close'] - df['open']) / df['open']
    df['rng'] = df['high'] - df['low']
    
    # Group by hour
    grp = df.groupby(df['time'].dt.hour)
    
    # Calculate all 4 measures for percentage change
    avg_pct_chg = grp['pct_chg'].mean()
    med_pct_chg = grp['pct_chg'].median()
    
    # Optimized statistics calculation with mode instead of trimmed median
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
    
    return (avg_pct_chg, trimmed_pct_chg, med_pct_chg, mode_pct_chg, 
            var_pct_chg, avg_range, trimmed_range, med_range, mode_range, var_range)


def compute_minute_stats(
    df: pd.DataFrame,
    hour: int,
    trim_pct: float = 5.0
) -> Tuple[pd.Series, pd.Series, pd.Series, pd.Series, pd.Series, pd.Series, pd.Series, pd.Series]:
    """
    Compute minute-level statistics for a specific hour.
    
    Args:
        df: DataFrame with columns: time, open, high, low, close
        hour: Hour to analyze (0-23)
        trim_pct: Percentage to trim from top/bottom (0-50)
        
    Returns:
        Tuple of (avg_pct_change, trimmed_pct_change, med_pct_change, trimmed_med_pct_change,
                 var_pct_change, avg_range, trimmed_range, med_range, mode_range, var_range)
        Each is a Series indexed by minute (0-59)
    """
    # Filter to specific hour
    df_hour = df[df['time'].dt.hour == hour].copy()
    
    if df_hour.empty:
        # Return empty series if no data
        empty = pd.Series(dtype=float)
        return empty, empty, empty, empty, empty, empty, empty, empty, empty, empty
    
    # Calculate metrics
    df_hour['pct_chg'] = (df_hour['close'] - df_hour['open']) / df_hour['open']
    df_hour['rng'] = df_hour['high'] - df_hour['low']
    
    # Group by minute
    grp = df_hour.groupby(df_hour['time'].dt.minute)
    
    # Calculate all 4 measures for percentage change
    avg_pct_chg = grp['pct_chg'].mean()
    med_pct_chg = grp['pct_chg'].median()
    
    # Optimized statistics calculation with mode (same as hourly)
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
    
    return (avg_pct_chg, trimmed_pct_chg, med_pct_chg, mode_pct_chg,
            var_pct_chg, avg_range, trimmed_range, med_range, mode_range, var_range)


def compute_intraday_vol_curve(df: pd.DataFrame, window: str = '5T') -> pd.DataFrame:
    """
    Compute rolling volatility curve throughout the trading day.
    
    Args:
        df: DataFrame with columns: time, open, high, low, close
        window: Rolling window size (e.g., '5T' for 5 minutes)
        
    Returns:
        DataFrame with time, mean_abs_return, iqr_low, iqr_high
    """
    df = df.copy()
    df['returns'] = (df['close'] - df['open']) / df['open']
    df['abs_returns'] = df['returns'].abs()
    
    # Group by time of day (hour:minute)
    df['time_of_day'] = df['time'].dt.time
    
    grouped = df.groupby('time_of_day')['abs_returns'].agg([
        ('mean', 'mean'),
        ('q25', lambda x: x.quantile(0.25)),
        ('q75', lambda x: x.quantile(0.75)),
        ('count', 'count')
    ]).reset_index()
    
    return grouped


def compute_correlation_matrix(
    df: pd.DataFrame,
    features: list[str]
) -> pd.DataFrame:
    """
    Compute correlation matrix for specified features.
    
    Args:
        df: DataFrame containing the features
        features: List of column names to correlate
        
    Returns:
        Correlation matrix DataFrame
    """
    return df[features].corr()


def compute_rolling_metrics(
    series: pd.Series,
    window: int,
    metrics: list[str] = ['mean', 'std', 'min', 'max']
) -> pd.DataFrame:
    """
    Compute rolling statistics for a time series.
    
    Args:
        series: Time series data
        window: Rolling window size (number of periods)
        metrics: List of metrics to compute ('mean', 'std', 'min', 'max', etc.)
        
    Returns:
        DataFrame with computed rolling metrics
    """
    result = pd.DataFrame(index=series.index)
    
    rolling = series.rolling(window=window, min_periods=1)
    
    for metric in metrics:
        if metric == 'mean':
            result[f'rolling_{metric}'] = rolling.mean()
        elif metric == 'std':
            result[f'rolling_{metric}'] = rolling.std()
        elif metric == 'min':
            result[f'rolling_{metric}'] = rolling.min()
        elif metric == 'max':
            result[f'rolling_{metric}'] = rolling.max()
        elif metric == 'median':
            result[f'rolling_{metric}'] = rolling.median()
    
    return result

