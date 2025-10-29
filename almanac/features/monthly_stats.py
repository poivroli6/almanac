"""
Monthly Statistical Computations

Functions for computing monthly statistics and seasonal patterns.
"""

import pandas as pd
import numpy as np
from typing import Tuple, Dict, List
from datetime import datetime


def compute_monthly_stats(monthly_df: pd.DataFrame, trim_pct: float = 5.0) -> Tuple[pd.Series, pd.Series, pd.Series, pd.Series, pd.Series, pd.Series, pd.Series, pd.Series]:
    """
    Compute monthly statistics from monthly data.
    
    Args:
        monthly_df: DataFrame with columns: month, return_pct, range_pct, volatility
        trim_pct: Percentage to trim from top/bottom (0-50)
        
    Returns:
        Tuple of (avg_return, trimmed_return, med_return, mode_return, 
                 var_return, avg_range, trimmed_range, med_range, mode_range, var_range)
        Each is a Series indexed by month (1-12)
    """
    df = monthly_df.copy()
    
    # Ensure we have the required columns
    if 'return_pct' not in df.columns or 'range_pct' not in df.columns:
        raise ValueError("DataFrame must contain 'return_pct' and 'range_pct' columns")
    
    # Group by month
    grp = df.groupby('month')
    
    # Calculate all 4 measures for percentage change
    avg_return = grp['return_pct'].mean()
    med_return = grp['return_pct'].median()
    
    # Calculate trimmed mean and mode for returns
    def calculate_all_stats(x, trim_pct):
        if len(x) < 3:
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
    stats_results = grp['return_pct'].apply(lambda x: calculate_all_stats(x, trim_pct))
    
    # Extract results
    avg_return = pd.Series([result[0] for result in stats_results], index=stats_results.index)
    trimmed_return = pd.Series([result[1] for result in stats_results], index=stats_results.index)
    med_return = pd.Series([result[2] for result in stats_results], index=stats_results.index)
    mode_return = pd.Series([result[3] for result in stats_results], index=stats_results.index)
    
    # Calculate variance
    var_return = grp['return_pct'].var()
    
    # Calculate range statistics
    avg_range = grp['range_pct'].mean()
    med_range = grp['range_pct'].median()
    
    # Calculate trimmed mean and mode for ranges
    range_stats_results = grp['range_pct'].apply(lambda x: calculate_all_stats(x, trim_pct))
    trimmed_range = pd.Series([result[1] for result in range_stats_results], index=range_stats_results.index)
    mode_range = pd.Series([result[3] for result in range_stats_results], index=range_stats_results.index)
    
    # Calculate variance for ranges
    var_range = grp['range_pct'].var()
    
    return (avg_return, trimmed_return, med_return, mode_return, 
            var_return, avg_range, trimmed_range, med_range, mode_range, var_range)


def compute_seasonal_patterns(monthly_df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """
    Compute seasonal patterns and statistics.
    
    Args:
        monthly_df: DataFrame with monthly data
        
    Returns:
        Dictionary with seasonal analysis results
    """
    df = monthly_df.copy()
    
    # Ensure we have season column
    if 'season' not in df.columns:
        def get_season(month):
            if month in [12, 1, 2]:
                return 'Winter'
            elif month in [3, 4, 5]:
                return 'Spring'
            elif month in [6, 7, 8]:
                return 'Summer'
            else:
                return 'Fall'
        df['season'] = df['month'].apply(get_season)
    
    # Seasonal statistics
    seasonal_stats = df.groupby('season').agg({
        'return_pct': ['mean', 'median', 'std', 'min', 'max', 'count'],
        'range_pct': ['mean', 'median', 'std'],
        'volatility': ['mean', 'median', 'std'],
        'volume': ['mean', 'median', 'sum']
    }).round(4)
    
    # Flatten column names
    seasonal_stats.columns = ['_'.join(col).strip() for col in seasonal_stats.columns]
    
    # Monthly performance ranking
    monthly_performance = df.groupby('month').agg({
        'return_pct': ['mean', 'std', 'count'],
        'range_pct': ['mean', 'std'],
        'volatility': ['mean', 'std']
    }).round(4)
    
    monthly_performance.columns = ['_'.join(col).strip() for col in monthly_performance.columns]
    
    # Add month names
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    monthly_performance['month_name'] = [month_names[i-1] for i in monthly_performance.index]
    
    # Calculate win rates
    win_rates = df.groupby('month')['return_pct'].apply(
        lambda x: (x > 0).sum() / len(x) * 100 if len(x) > 0 else 0
    )
    monthly_performance['win_rate'] = win_rates.round(2)
    
    # Best and worst performing months
    best_month = monthly_performance['return_pct_mean'].idxmax()
    worst_month = monthly_performance['return_pct_mean'].idxmin()
    
    # Volatility analysis
    highest_vol_month = monthly_performance['volatility_mean'].idxmax()
    lowest_vol_month = monthly_performance['volatility_mean'].idxmin()
    
    return {
        'seasonal_stats': seasonal_stats,
        'monthly_performance': monthly_performance,
        'best_month': best_month,
        'worst_month': worst_month,
        'highest_vol_month': highest_vol_month,
        'lowest_vol_month': lowest_vol_month,
        'best_month_name': month_names[best_month-1],
        'worst_month_name': month_names[worst_month-1],
        'highest_vol_month_name': month_names[highest_vol_month-1],
        'lowest_vol_month_name': month_names[lowest_vol_month-1]
    }


def compute_monthly_hod_lod_patterns(monthly_df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """
    Compute monthly HOD/LOD patterns for seasonal analysis.
    
    Args:
        monthly_df: DataFrame with monthly data
        
    Returns:
        Dictionary with HOD/LOD seasonal patterns
    """
    df = monthly_df.copy()
    
    # Calculate monthly HOD/LOD timing patterns
    # For monthly data, we'll analyze the distribution of high/low occurrences
    
    # Group by month and analyze high/low patterns
    monthly_patterns = df.groupby('month').agg({
        'high': ['max', 'mean'],
        'low': ['min', 'mean'],
        'range': ['max', 'mean', 'std'],
        'return_pct': ['mean', 'std']
    }).round(4)
    
    monthly_patterns.columns = ['_'.join(col).strip() for col in monthly_patterns.columns]
    
    # Add month names
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    monthly_patterns['month_name'] = [month_names[i-1] for i in monthly_patterns.index]
    
    # Calculate relative performance metrics
    monthly_patterns['high_performance'] = monthly_patterns['high_max'] / monthly_patterns['high_max'].mean()
    monthly_patterns['low_performance'] = monthly_patterns['low_min'] / monthly_patterns['low_min'].mean()
    monthly_patterns['range_performance'] = monthly_patterns['range_mean'] / monthly_patterns['range_mean'].mean()
    
    # Identify months with highest/lowest ranges
    highest_range_month = monthly_patterns['range_mean'].idxmax()
    lowest_range_month = monthly_patterns['range_mean'].idxmin()
    
    # Calculate consistency metrics (lower std = more consistent)
    most_consistent_month = monthly_patterns['return_pct_std'].idxmin()
    most_volatile_month = monthly_patterns['return_pct_std'].idxmax()
    
    return {
        'monthly_patterns': monthly_patterns,
        'highest_range_month': highest_range_month,
        'lowest_range_month': lowest_range_month,
        'most_consistent_month': most_consistent_month,
        'most_volatile_month': most_volatile_month,
        'highest_range_month_name': month_names[highest_range_month-1],
        'lowest_range_month_name': month_names[lowest_range_month-1],
        'most_consistent_month_name': month_names[most_consistent_month-1],
        'most_volatile_month_name': month_names[most_volatile_month-1]
    }


def compute_multi_year_monthly_stats(monthly_df: pd.DataFrame, trim_pct: float = 5.0) -> Dict[str, pd.DataFrame]:
    """
    Compute monthly statistics broken down by year for multi-year line charts.
    
    Args:
        monthly_df: DataFrame with columns: time, Open, High, Low, Close, Volume, Month, Year
        trim_pct: Percentage to trim from top/bottom (0-50)
        
    Returns:
        Dictionary with DataFrames for each year containing monthly stats
    """
    df = monthly_df.copy()
    
    # Calculate metrics
    df['pct_chg'] = (df['close'] - df['open']) / df['open']
    df['rng'] = df['high'] - df['low']
    
    # Group by year and month
    yearly_stats = {}
    
    for year in sorted(df['year'].unique()):
        year_data = df[df['year'] == year].copy()
        
        # Group by month for this year
        grp = year_data.groupby('month')
        
        def calculate_all_stats(x, trim_pct):
            if len(x) < 3:  # Not enough data to trim meaningfully
                return x.mean(), x.mean(), x.median(), x.mode().iloc[0] if not x.mode().empty else x.median()
            
            trim_low = trim_pct / 100.0
            trim_high = 1.0 - trim_low
            
            # Calculate quantiles once
            q_low, q_high = x.quantile([trim_low, trim_high])
            
            # Trimmed mean: average of values between trim percentiles
            trimmed_mean_val = x[(x >= q_low) & (x <= q_high)].mean()
            
            # Mode: most frequent value
            mode_val = x.mode().iloc[0] if not x.mode().empty else x.median()
            
            return x.mean(), trimmed_mean_val, x.median(), mode_val
        
        # Apply custom stats function
        pct_chg_stats = grp['pct_chg'].apply(lambda x: calculate_all_stats(x, trim_pct))
        range_stats = grp['rng'].apply(lambda x: calculate_all_stats(x, trim_pct))
        
        # Extract individual series
        month_avg_pct_chg = pct_chg_stats.apply(lambda x: x[0])
        month_trimmed_pct_chg = pct_chg_stats.apply(lambda x: x[1])
        month_med_pct_chg = pct_chg_stats.apply(lambda x: x[2])
        month_mode_pct_chg = pct_chg_stats.apply(lambda x: x[3])
        month_var_pct_chg = grp['pct_chg'].var()
        
        month_avg_range = range_stats.apply(lambda x: x[0])
        month_trimmed_range = range_stats.apply(lambda x: x[1])
        month_med_range = range_stats.apply(lambda x: x[2])
        month_mode_range = range_stats.apply(lambda x: x[3])
        month_var_range = grp['rng'].var()
        
        # Create DataFrame for this year - use actual months that exist
        months_in_data = sorted(year_data['month'].unique())
        
        # Create a DataFrame with all 12 months, filling missing ones with 0
        all_months = list(range(1, 13))
        year_stats_df = pd.DataFrame({
            'Month': all_months,
            'Year': year,
            'avg_pct_chg': [month_avg_pct_chg.get(month, 0) for month in all_months],
            'trimmed_pct_chg': [month_trimmed_pct_chg.get(month, 0) for month in all_months],
            'med_pct_chg': [month_med_pct_chg.get(month, 0) for month in all_months],
            'mode_pct_chg': [month_mode_pct_chg.get(month, 0) for month in all_months],
            'var_pct_chg': [month_var_pct_chg.get(month, 0) for month in all_months],
            'avg_range': [month_avg_range.get(month, 0) for month in all_months],
            'trimmed_range': [month_trimmed_range.get(month, 0) for month in all_months],
            'med_range': [month_med_range.get(month, 0) for month in all_months],
            'mode_range': [month_mode_range.get(month, 0) for month in all_months],
            'var_range': [month_var_range.get(month, 0) for month in all_months]
        })
        
        yearly_stats[str(year)] = year_stats_df
    
    return yearly_stats


def get_monthly_summary_cards(monthly_df: pd.DataFrame) -> List[Dict]:
    """
    Generate summary cards for monthly analysis.
    
    Args:
        monthly_df: DataFrame with monthly data
        
    Returns:
        List of card dictionaries for display
    """
    if monthly_df.empty:
        return []
    
    # Calculate overall statistics
    total_months = len(monthly_df)
    avg_monthly_return = monthly_df['return_pct'].mean()
    total_return = monthly_df['return_pct'].sum()
    best_month_return = monthly_df['return_pct'].max()
    worst_month_return = monthly_df['return_pct'].min()
    
    # Find best and worst months
    best_month_data = monthly_df.loc[monthly_df['return_pct'].idxmax()]
    worst_month_data = monthly_df.loc[monthly_df['return_pct'].idxmin()]
    
    # Calculate win rate
    win_rate = (monthly_df['return_pct'] > 0).sum() / len(monthly_df) * 100
    
    # Calculate average volatility
    avg_volatility = monthly_df['volatility'].mean()
    
    cards = [
        {
            'title': 'TOTAL MONTHS',
            'value': f"{total_months}",
            'color': '#007bff',
            'bg_color': '#e6f3ff',
            'border_color': '#b3d9ff'
        },
        {
            'title': 'AVG MONTHLY RETURN',
            'value': f"{avg_monthly_return:.2%}",
            'color': '#28a745' if avg_monthly_return >= 0 else '#dc3545',
            'bg_color': '#e6ffe6' if avg_monthly_return >= 0 else '#ffe6e6',
            'border_color': '#99e699' if avg_monthly_return >= 0 else '#ff9999'
        },
        {
            'title': 'TOTAL RETURN',
            'value': f"{total_return:.2%}",
            'color': '#28a745' if total_return >= 0 else '#dc3545',
            'bg_color': '#e6ffe6' if total_return >= 0 else '#ffe6e6',
            'border_color': '#99e699' if total_return >= 0 else '#ff9999'
        },
        {
            'title': 'WIN RATE',
            'value': f"{win_rate:.1f}%",
            'color': '#17a2b8',
            'bg_color': '#e6f8ff',
            'border_color': '#80d4ff'
        },
        {
            'title': 'BEST MONTH',
            'value': f"{best_month_data['month_name']} {best_month_data['year']}",
            'subtitle': f"{best_month_return:.2%}",
            'color': '#28a745',
            'bg_color': '#e6ffe6',
            'border_color': '#99e699'
        },
        {
            'title': 'WORST MONTH',
            'value': f"{worst_month_data['month_name']} {worst_month_data['year']}",
            'subtitle': f"{worst_month_return:.2%}",
            'color': '#dc3545',
            'bg_color': '#ffe6e6',
            'border_color': '#ff9999'
        }
    ]
    
    return cards
