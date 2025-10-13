"""
High of Day / Low of Day Analysis

Functions for detecting and analyzing HOD/LOD timing patterns.
"""

import pandas as pd
import numpy as np
from typing import Tuple


def detect_hod_lod(df: pd.DataFrame) -> pd.DataFrame:
    """
    Detect the time of High of Day (HOD) and Low of Day (LOD) for each trading day.
    
    Args:
        df: DataFrame with columns: time, high, low
        
    Returns:
        DataFrame with columns: date, hod_time, lod_time, hod_price, lod_price
    """
    df = df.copy()
    df['date'] = df['time'].dt.date
    
    # Find HOD and LOD for each day
    hod = df.loc[df.groupby('date')['high'].idxmax()][['date', 'time', 'high']]
    hod.columns = ['date', 'hod_time', 'hod_price']
    
    lod = df.loc[df.groupby('date')['low'].idxmin()][['date', 'time', 'low']]
    lod.columns = ['date', 'lod_time', 'lod_price']
    
    # Merge HOD and LOD
    result = hod.merge(lod, on='date')
    
    # Add time-of-day fields
    result['hod_hour'] = result['hod_time'].dt.hour
    result['hod_minute'] = result['hod_time'].dt.minute
    result['lod_hour'] = result['lod_time'].dt.hour
    result['lod_minute'] = result['lod_time'].dt.minute
    
    # Calculate minutes since midnight
    result['hod_minutes_since_midnight'] = result['hod_hour'] * 60 + result['hod_minute']
    result['lod_minutes_since_midnight'] = result['lod_hour'] * 60 + result['lod_minute']
    
    return result


def compute_survival_curves(hod_lod_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Compute survival curves: "Probability that HOD/LOD has already occurred by time T".
    
    Args:
        hod_lod_df: DataFrame from detect_hod_lod()
        
    Returns:
        Tuple of (hod_survival, lod_survival) DataFrames with columns: minutes, probability
    """
    # HOD survival curve
    hod_minutes = hod_lod_df['hod_minutes_since_midnight'].sort_values()
    hod_survival = pd.DataFrame({
        'minutes': hod_minutes.unique(),
        'probability': [
            (hod_minutes <= m).sum() / len(hod_minutes)
            for m in hod_minutes.unique()
        ]
    })
    
    # LOD survival curve
    lod_minutes = hod_lod_df['lod_minutes_since_midnight'].sort_values()
    lod_survival = pd.DataFrame({
        'minutes': lod_minutes.unique(),
        'probability': [
            (lod_minutes <= m).sum() / len(lod_minutes)
            for m in lod_minutes.unique()
        ]
    })
    
    return hod_survival, lod_survival


def compute_hod_lod_heatmap(hod_lod_df: pd.DataFrame, by: str = 'weekday') -> pd.DataFrame:
    """
    Create a heatmap matrix of HOD/LOD frequency by time and another dimension.
    
    Args:
        hod_lod_df: DataFrame from detect_hod_lod()
        by: Dimension to group by ('weekday', 'month', 'hour')
        
    Returns:
        Pivot table with time bins on one axis and grouping dimension on the other
    """
    df = hod_lod_df.copy()
    
    # Add grouping dimension
    if by == 'weekday':
        df['group'] = pd.to_datetime(df['date']).dt.day_name()
    elif by == 'month':
        df['group'] = pd.to_datetime(df['date']).dt.month_name()
    elif by == 'hour':
        df['group'] = df['hod_hour']
    else:
        raise ValueError(f"Unknown grouping dimension: {by}")
    
    # Create time bins (e.g., 15-minute intervals)
    df['hod_time_bin'] = (df['hod_minutes_since_midnight'] // 15) * 15
    df['lod_time_bin'] = (df['lod_minutes_since_midnight'] // 15) * 15
    
    # Create frequency tables
    hod_freq = df.groupby(['group', 'hod_time_bin']).size().reset_index(name='count')
    hod_pivot = hod_freq.pivot(index='group', columns='hod_time_bin', values='count').fillna(0)
    
    lod_freq = df.groupby(['group', 'lod_time_bin']).size().reset_index(name='count')
    lod_pivot = lod_freq.pivot(index='group', columns='lod_time_bin', values='count').fillna(0)
    
    return hod_pivot, lod_pivot


def compute_rolling_median_time(
    hod_lod_df: pd.DataFrame,
    metric: str = 'hod',
    window: int = 63
) -> pd.DataFrame:
    """
    Compute rolling median HOD or LOD time with confidence intervals.
    
    Args:
        hod_lod_df: DataFrame from detect_hod_lod()
        metric: 'hod' or 'lod'
        window: Rolling window size in days
        
    Returns:
        DataFrame with columns: date, rolling_median, ci_low, ci_high
    """
    df = hod_lod_df.copy()
    df['date_ts'] = pd.to_datetime(df['date'])
    df = df.sort_values('date_ts')
    
    col = f'{metric}_minutes_since_midnight'
    
    # Compute rolling statistics
    rolling = df[col].rolling(window=window, min_periods=10)
    
    result = pd.DataFrame({
        'date': df['date'],
        'rolling_median': rolling.median(),
        'rolling_mean': rolling.mean(),
        'rolling_std': rolling.std(),
    })
    
    # Approximate confidence intervals (mean ± 1.96 * std/sqrt(n))
    result['ci_low'] = result['rolling_mean'] - 1.96 * result['rolling_std'] / np.sqrt(window)
    result['ci_high'] = result['rolling_mean'] + 1.96 * result['rolling_std'] / np.sqrt(window)
    
    return result


def compute_trend_test(series: pd.Series) -> dict:
    """
    Perform Mann-Kendall trend test on a time series.
    
    Args:
        series: Time series (e.g., HOD times over days)
        
    Returns:
        Dictionary with trend, p_value, slope
    """
    try:
        from scipy import stats
        
        # Remove NaNs
        clean_series = series.dropna()
        n = len(clean_series)
        
        if n < 10:
            return {'trend': 'insufficient_data', 'p_value': None, 'slope': None}
        
        # Mann-Kendall test
        s = 0
        for i in range(n - 1):
            for j in range(i + 1, n):
                s += np.sign(clean_series.iloc[j] - clean_series.iloc[i])
        
        # Variance
        var_s = n * (n - 1) * (2 * n + 5) / 18
        
        # Z-score
        if s > 0:
            z = (s - 1) / np.sqrt(var_s)
        elif s < 0:
            z = (s + 1) / np.sqrt(var_s)
        else:
            z = 0
        
        # P-value (two-tailed)
        p_value = 2 * (1 - stats.norm.cdf(abs(z)))
        
        # Trend direction
        if p_value < 0.05:
            trend = 'increasing' if s > 0 else 'decreasing'
        else:
            trend = 'no_trend'
        
        # Theil-Sen slope estimate
        slopes = []
        for i in range(n - 1):
            for j in range(i + 1, n):
                slopes.append((clean_series.iloc[j] - clean_series.iloc[i]) / (j - i))
        
        slope = np.median(slopes) if slopes else 0
        
        return {
            'trend': trend,
            'p_value': float(p_value),
            'slope': float(slope),
            'z_score': float(z)
        }
    
    except ImportError:
        return {
            'trend': 'scipy_not_installed',
            'p_value': None,
            'slope': None
        }

