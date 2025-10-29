"""
Statistical Computations

Functions for computing hourly and minute-level statistics on intraday data.
"""

import pandas as pd
import numpy as np
from typing import Tuple


def compute_hourly_stats(df: pd.DataFrame, trim_pct: float = 5.0) -> Tuple[pd.Series, pd.Series, pd.Series, pd.Series, pd.Series, pd.Series, pd.Series, pd.Series, pd.Series, pd.Series, pd.Series, pd.Series]:
    """
    Compute hourly statistics from minute data.
    
    Args:
        df: DataFrame with columns: time, open, high, low, close
        trim_pct: Percentage to trim from top/bottom (0-50)
        
    Returns:
        Tuple of (avg_pct_change, trimmed_pct_change, med_pct_change, mode_pct_change, outlier_pct_change,
                 var_pct_change, avg_range, trimmed_range, med_range, mode_range, outlier_range, var_range)
        Each is a Series indexed by hour (0-23)
    """
    df = df.copy()
    
    # Calculate metrics
    df['pct_chg'] = (df['close'] - df['open']) / df['open']
    df['rng'] = df['high'] - df['low']
    
    # Group by hour
    grp = df.groupby(df['time'].dt.hour)
    
    # Calculate all 5 measures for percentage change
    avg_pct_chg = grp['pct_chg'].mean()
    med_pct_chg = grp['pct_chg'].median()
    
    # Optimized statistics calculation with mode and outlier
    def calculate_all_stats(x, trim_pct):
        if len(x) < 10:
            return x.mean(), x.mean(), x.median(), x.mode().iloc[0] if len(x.mode()) > 0 else x.median(), x.mean()
        
        trim_low = trim_pct / 100.0
        trim_high = 1.0 - trim_low
        
        # Calculate quantiles once
        q_low, q_high = x.quantile([trim_low, trim_high])
        
        # Trimmed mean: mean of values between trim percentiles (excluding extremes)
        trimmed_values = x[(x >= q_low) & (x <= q_high)]
        trimmed_mean = trimmed_values.mean() if len(trimmed_values) > 0 else x.mean()
        
        # Mode: most frequent value
        mode_val = x.mode().iloc[0] if len(x.mode()) > 0 else x.median()
        
        # Outlier: average of top and bottom percentiles
        outlier_mean = (q_low + q_high) / 2
        
        return x.mean(), trimmed_mean, x.median(), mode_val, outlier_mean
    
    # Calculate all stats in one pass per group
    stats_results = grp['pct_chg'].apply(lambda x: calculate_all_stats(x, trim_pct))
    
    # Extract results efficiently
    trimmed_pct_chg = stats_results.apply(lambda x: x[1])
    mode_pct_chg = stats_results.apply(lambda x: x[3])
    outlier_pct_chg = stats_results.apply(lambda x: x[4])
    
    var_pct_chg = grp['pct_chg'].var()
    
    # Calculate all 5 measures for range
    avg_range = grp['rng'].mean()
    med_range = grp['rng'].median()
    
    # Calculate range stats in one pass
    range_stats_results = grp['rng'].apply(lambda x: calculate_all_stats(x, trim_pct))
    trimmed_range = range_stats_results.apply(lambda x: x[1])
    mode_range = range_stats_results.apply(lambda x: x[3])
    outlier_range = range_stats_results.apply(lambda x: x[4])
    
    var_range = grp['rng'].var()
    
    return (avg_pct_chg, trimmed_pct_chg, med_pct_chg, mode_pct_chg, outlier_pct_chg,
            var_pct_chg, avg_range, trimmed_range, med_range, mode_range, outlier_range, var_range)


def compute_minute_stats(
    df: pd.DataFrame,
    hour: int,
    trim_pct: float = 5.0
) -> Tuple[pd.Series, pd.Series, pd.Series, pd.Series, pd.Series, pd.Series, pd.Series, pd.Series, pd.Series, pd.Series, pd.Series, pd.Series]:
    """
    Compute minute-level statistics for a specific hour.
    
    Args:
        df: DataFrame with columns: time, open, high, low, close
        hour: Hour to analyze (0-23)
        trim_pct: Percentage to trim from top/bottom (0-50)
        
    Returns:
        Tuple of (avg_pct_change, trimmed_pct_change, med_pct_change, mode_pct_change, outlier_pct_change,
                 var_pct_change, avg_range, trimmed_range, med_range, mode_range, outlier_range, var_range)
        Each is a Series indexed by minute (0-59)
    """
    # Filter to specific hour
    df_hour = df[df['time'].dt.hour == hour].copy()
    
    if df_hour.empty:
        # Return empty series if no data
        empty = pd.Series(dtype=float)
        return empty, empty, empty, empty, empty, empty, empty, empty, empty, empty, empty, empty
    
    # Calculate metrics
    df_hour['pct_chg'] = (df_hour['close'] - df_hour['open']) / df_hour['open']
    df_hour['rng'] = df_hour['high'] - df_hour['low']
    
    # Group by minute
    grp = df_hour.groupby(df_hour['time'].dt.minute)
    
    # Calculate all 5 measures for percentage change
    avg_pct_chg = grp['pct_chg'].mean()
    med_pct_chg = grp['pct_chg'].median()
    
    # Optimized statistics calculation with mode and outlier
    def calculate_all_stats(x, trim_pct):
        if len(x) < 10:
            return x.mean(), x.mean(), x.median(), x.mode().iloc[0] if len(x.mode()) > 0 else x.median(), x.mean()
        
        trim_low = trim_pct / 100.0
        trim_high = 1.0 - trim_low
        
        # Calculate quantiles once
        q_low, q_high = x.quantile([trim_low, trim_high])
        
        # Trimmed mean: mean of values between trim percentiles (excluding extremes)
        trimmed_values = x[(x >= q_low) & (x <= q_high)]
        trimmed_mean = trimmed_values.mean() if len(trimmed_values) > 0 else x.mean()
        
        # Mode: most frequent value
        mode_val = x.mode().iloc[0] if len(x.mode()) > 0 else x.median()
        
        # Outlier: average of top and bottom percentiles
        outlier_mean = (q_low + q_high) / 2
        
        return x.mean(), trimmed_mean, x.median(), mode_val, outlier_mean
    
    # Calculate all stats in one pass per group
    stats_results = grp['pct_chg'].apply(lambda x: calculate_all_stats(x, trim_pct))
    
    # Extract results efficiently
    trimmed_pct_chg = stats_results.apply(lambda x: x[1])
    mode_pct_chg = stats_results.apply(lambda x: x[3])
    outlier_pct_chg = stats_results.apply(lambda x: x[4])
    
    var_pct_chg = grp['pct_chg'].var()
    
    # Calculate all 5 measures for range
    avg_range = grp['rng'].mean()
    med_range = grp['rng'].median()
    
    # Calculate range stats in one pass
    range_stats_results = grp['rng'].apply(lambda x: calculate_all_stats(x, trim_pct))
    trimmed_range = range_stats_results.apply(lambda x: x[1])
    mode_range = range_stats_results.apply(lambda x: x[3])
    outlier_range = range_stats_results.apply(lambda x: x[4])
    
    var_range = grp['rng'].var()
    
    return (avg_pct_chg, trimmed_pct_chg, med_pct_chg, mode_pct_chg, outlier_pct_chg,
            var_pct_chg, avg_range, trimmed_range, med_range, mode_range, outlier_range, var_range)


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


def compute_daily_stats(df: pd.DataFrame, trim_pct: float = 5.0) -> Tuple[pd.Series, pd.Series, pd.Series, pd.Series, pd.Series, pd.Series, pd.Series, pd.Series, pd.Series, pd.Series, pd.Series, pd.Series]:
    """
    Compute daily statistics grouped by day of week (Monday-Sunday).
    
    Args:
        df: DataFrame with columns: time, open, high, low, close
        trim_pct: Percentage to trim from top/bottom (0-50)
        
    Returns:
        Tuple of (avg_pct_change, trimmed_pct_change, med_pct_change, mode_pct_change, outlier_pct_change,
                 var_pct_change, avg_range, trimmed_range, med_range, mode_range, outlier_range, var_range)
        Each is a Series indexed by day of week (Monday-Sunday)
    """
    df = df.copy()
    
    # Calculate metrics
    df['pct_chg'] = (df['close'] - df['open']) / df['open']
    df['rng'] = df['high'] - df['low']
    
    # Add day of week (0=Monday, 6=Sunday)
    df['day_of_week'] = df['time'].dt.dayofweek
    
    # Group by day of week
    grp = df.groupby('day_of_week')
    
    # Calculate all 5 measures for percentage change
    avg_pct_chg = grp['pct_chg'].mean()
    med_pct_chg = grp['pct_chg'].median()
    
    # Optimized statistics calculation with mode and outlier
    def calculate_all_stats(x, trim_pct):
        if len(x) < 10:
            return x.mean(), x.mean(), x.median(), x.mode().iloc[0] if len(x.mode()) > 0 else x.median(), x.mean()
        
        trim_low = trim_pct / 100.0
        trim_high = 1.0 - trim_low
        
        # Calculate quantiles once
        q_low, q_high = x.quantile([trim_low, trim_high])
        
        # Trimmed mean: mean of values between trim percentiles (excluding extremes)
        trimmed_values = x[(x >= q_low) & (x <= q_high)]
        trimmed_mean = trimmed_values.mean() if len(trimmed_values) > 0 else x.mean()
        
        # Mode: most frequent value
        mode_val = x.mode().iloc[0] if len(x.mode()) > 0 else x.median()
        
        # Outlier: average of top and bottom percentiles (old incorrect method)
        outlier_mean = (q_low + q_high) / 2
        
        return x.mean(), trimmed_mean, x.median(), mode_val, outlier_mean
    
    # Calculate all stats in one pass per group
    stats_results = grp['pct_chg'].apply(lambda x: calculate_all_stats(x, trim_pct))
    
    # Extract results efficiently
    trimmed_pct_chg = stats_results.apply(lambda x: x[1])
    mode_pct_chg = stats_results.apply(lambda x: x[3])
    outlier_pct_chg = stats_results.apply(lambda x: x[4])
    
    var_pct_chg = grp['pct_chg'].var()
    
    # Calculate all 5 measures for range
    avg_range = grp['rng'].mean()
    med_range = grp['rng'].median()
    
    # Calculate range stats in one pass
    range_stats_results = grp['rng'].apply(lambda x: calculate_all_stats(x, trim_pct))
    trimmed_range = range_stats_results.apply(lambda x: x[1])
    mode_range = range_stats_results.apply(lambda x: x[3])
    outlier_range = range_stats_results.apply(lambda x: x[4])
    
    var_range = grp['rng'].var()
    
    # Create proper day names for index
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    avg_pct_chg.index = [day_names[i] for i in avg_pct_chg.index]
    trimmed_pct_chg.index = [day_names[i] for i in trimmed_pct_chg.index]
    med_pct_chg.index = [day_names[i] for i in med_pct_chg.index]
    mode_pct_chg.index = [day_names[i] for i in mode_pct_chg.index]
    outlier_pct_chg.index = [day_names[i] for i in outlier_pct_chg.index]
    var_pct_chg.index = [day_names[i] for i in var_pct_chg.index]
    avg_range.index = [day_names[i] for i in avg_range.index]
    trimmed_range.index = [day_names[i] for i in trimmed_range.index]
    med_range.index = [day_names[i] for i in med_range.index]
    mode_range.index = [day_names[i] for i in mode_range.index]
    outlier_range.index = [day_names[i] for i in outlier_range.index]
    var_range.index = [day_names[i] for i in var_range.index]
    
    return (avg_pct_chg, trimmed_pct_chg, med_pct_chg, mode_pct_chg, outlier_pct_chg,
            var_pct_chg, avg_range, trimmed_range, med_range, mode_range, outlier_range, var_range)


def compute_monthly_stats(df: pd.DataFrame, trim_pct: float = 5.0) -> Tuple[pd.Series, pd.Series, pd.Series, pd.Series, pd.Series, pd.Series, pd.Series, pd.Series, pd.Series, pd.Series, pd.Series, pd.Series]:
    """
    Compute monthly statistics grouped by month (January-December).
    
    Args:
        df: DataFrame with columns: time, open, high, low, close
        trim_pct: Percentage to trim from top/bottom (0-50)
        
    Returns:
        Tuple of (avg_pct_change, trimmed_pct_change, med_pct_change, mode_pct_change, outlier_pct_change,
                 var_pct_change, avg_range, trimmed_range, med_range, mode_range, outlier_range, var_range)
        Each is a Series indexed by month (January-December)
    """
    df = df.copy()
    
    # Calculate metrics
    df['pct_chg'] = (df['close'] - df['open']) / df['open']
    df['rng'] = df['high'] - df['low']
    
    # Add month (1=January, 12=December)
    df['month'] = df['time'].dt.month
    
    # Group by month
    grp = df.groupby('month')
    
    # Calculate all 5 measures for percentage change
    avg_pct_chg = grp['pct_chg'].mean()
    med_pct_chg = grp['pct_chg'].median()
    
    # Optimized statistics calculation with mode and outlier
    def calculate_all_stats(x, trim_pct):
        if len(x) < 10:
            return x.mean(), x.mean(), x.median(), x.mode().iloc[0] if len(x.mode()) > 0 else x.median(), x.mean()
        
        trim_low = trim_pct / 100.0
        trim_high = 1.0 - trim_low
        
        # Calculate quantiles once
        q_low, q_high = x.quantile([trim_low, trim_high])
        
        # Trimmed mean: mean of values between trim percentiles (excluding extremes)
        trimmed_values = x[(x >= q_low) & (x <= q_high)]
        trimmed_mean = trimmed_values.mean() if len(trimmed_values) > 0 else x.mean()
        
        # Mode: most frequent value
        mode_val = x.mode().iloc[0] if len(x.mode()) > 0 else x.median()
        
        # Outlier: average of top and bottom percentiles
        outlier_mean = (q_low + q_high) / 2
        
        return x.mean(), trimmed_mean, x.median(), mode_val, outlier_mean
    
    # Calculate all stats in one pass per group
    stats_results = grp['pct_chg'].apply(lambda x: calculate_all_stats(x, trim_pct))
    
    # Extract results efficiently
    trimmed_pct_chg = stats_results.apply(lambda x: x[1])
    mode_pct_chg = stats_results.apply(lambda x: x[3])
    outlier_pct_chg = stats_results.apply(lambda x: x[4])
    
    var_pct_chg = grp['pct_chg'].var()
    
    # Calculate all 5 measures for range
    avg_range = grp['rng'].mean()
    med_range = grp['rng'].median()
    
    # Calculate range stats in one pass
    range_stats_results = grp['rng'].apply(lambda x: calculate_all_stats(x, trim_pct))
    trimmed_range = range_stats_results.apply(lambda x: x[1])
    mode_range = range_stats_results.apply(lambda x: x[3])
    outlier_range = range_stats_results.apply(lambda x: x[4])
    
    var_range = grp['rng'].var()
    
    # Create proper month names for index
    month_names = ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']
    avg_pct_chg.index = [month_names[i-1] for i in avg_pct_chg.index]
    trimmed_pct_chg.index = [month_names[i-1] for i in trimmed_pct_chg.index]
    med_pct_chg.index = [month_names[i-1] for i in med_pct_chg.index]
    mode_pct_chg.index = [month_names[i-1] for i in mode_pct_chg.index]
    outlier_pct_chg.index = [month_names[i-1] for i in outlier_pct_chg.index]
    var_pct_chg.index = [month_names[i-1] for i in var_pct_chg.index]
    avg_range.index = [month_names[i-1] for i in avg_range.index]
    trimmed_range.index = [month_names[i-1] for i in trimmed_range.index]
    med_range.index = [month_names[i-1] for i in med_range.index]
    mode_range.index = [month_names[i-1] for i in mode_range.index]
    outlier_range.index = [month_names[i-1] for i in outlier_range.index]
    var_range.index = [month_names[i-1] for i in var_range.index]
    
    return (avg_pct_chg, trimmed_pct_chg, med_pct_chg, mode_pct_chg, outlier_pct_chg,
            var_pct_chg, avg_range, trimmed_range, med_range, mode_range, outlier_range, var_range)