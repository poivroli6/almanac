"""
Conditional Filtering for Intraday Analysis

This module provides functions to filter data based on custom conditions,
enabling analysis of intraday patterns under specific market conditions.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, date


def apply_quick_filter(daily_data: pd.DataFrame, filter_type: str) -> pd.Series:
    """
    Apply predefined quick filters to daily data.
    
    Args:
        daily_data: DataFrame with columns ['date', 'open', 'high', 'low', 'close', 'volume']
        filter_type: Type of filter to apply
        
    Returns:
        Boolean series indicating which days match the filter
    """
    if filter_type == 'all':
        return pd.Series([True] * len(daily_data), index=daily_data.index)
    
    elif filter_type == 'bull':
        return daily_data['close'] > daily_data['open']
    
    elif filter_type == 'bear':
        return daily_data['close'] < daily_data['open']
    
    elif filter_type == 'high_vol':
        daily_range = (daily_data['high'] - daily_data['low']) / daily_data['open']
        threshold = daily_range.quantile(0.75)
        return daily_range > threshold
    
    elif filter_type == 'low_vol':
        daily_range = (daily_data['high'] - daily_data['low']) / daily_data['open']
        threshold = daily_range.quantile(0.25)
        return daily_range < threshold
    
    elif filter_type == 'gap_up':
        gap = (daily_data['open'] - daily_data['close'].shift(1)) / daily_data['close'].shift(1)
        return gap > 0.005  # 0.5%
    
    elif filter_type == 'gap_down':
        gap = (daily_data['open'] - daily_data['close'].shift(1)) / daily_data['close'].shift(1)
        return gap < -0.005  # -0.5%
    
    else:
        return pd.Series([True] * len(daily_data), index=daily_data.index)


def apply_custom_filter(daily_data: pd.DataFrame, filter_config: Dict[str, Any], 
                       intermarket_data: pd.DataFrame = None, 
                       studied_product: str = None, 
                       intermarket_product: str = None) -> pd.Series:
    """
    Apply custom filter based on configuration.
    
    Args:
        daily_data: DataFrame with OHLCV data for studied product
        filter_config: Dictionary with keys:
            - asset: 'studied', 'intermarket', 'GC', 'ES', 'vix'
            - metric: 'daily_return', 'daily_range', 'gap', 'volume'
            - condition: 'gt', 'lt', 'gte', 'lte', 'eq'
            - value: numeric threshold
        intermarket_data: DataFrame with OHLCV data for intermarket product
        studied_product: Symbol of studied product (e.g., 'ES')
        intermarket_product: Symbol of intermarket product (e.g., 'GC')
            
    Returns:
        Boolean series indicating which days match the filter
    """
    asset = filter_config.get('asset', 'studied')
    metric = filter_config.get('metric', 'daily_return')
    condition = filter_config.get('condition', 'gt')
    value = filter_config.get('value', 0)
    
    # Determine which dataset to use
    if asset == 'studied':
        target_data = daily_data
    elif asset == 'intermarket':
        if intermarket_data is not None and not intermarket_data.empty:
            target_data = intermarket_data
        else:
            # Fallback to studied product if no intermarket data
            target_data = daily_data
    else:
        # For specific assets, we'd need to load their data
        # For now, fallback to studied product
        target_data = daily_data
    
    # Calculate the metric based on the configuration
    if metric == 'daily_return':
        metric_series = (target_data['close'] - target_data['open']) / target_data['open']
    elif metric == 'daily_range':
        metric_series = (target_data['high'] - target_data['low']) / target_data['open']
    elif metric == 'gap':
        metric_series = (target_data['open'] - target_data['close'].shift(1)) / target_data['close'].shift(1)
        metric_series = metric_series.fillna(0)  # First day has no gap
    elif metric == 'volume':
        metric_series = target_data['volume']
    else:
        return pd.Series([True] * len(daily_data), index=daily_data.index)
    
    # Apply the condition to get a boolean series on target_data's index
    if condition == 'gt':
        bool_series = metric_series > value
    elif condition == 'lt':
        bool_series = metric_series < value
    elif condition == 'gte':
        bool_series = metric_series >= value
    elif condition == 'lte':
        bool_series = metric_series <= value
    elif condition == 'eq':
        bool_series = np.abs(metric_series - value) < 1e-6  # Floating point equality
    else:
        bool_series = pd.Series([True] * len(target_data), index=target_data.index)

    # Align the boolean series to the studied daily_data index using the date column
    # This prevents index-length mismatches when mixing intermarket filters
    try:
        target_dates = target_data['date'] if 'date' in target_data.columns else target_data['time'].dt.date
        date_to_bool = pd.Series(bool_series.values, index=target_dates)
        ref_dates = daily_data['date'] if 'date' in daily_data.columns else daily_data['time'].dt.date
        aligned = date_to_bool.reindex(ref_dates).fillna(False)
        aligned.index = daily_data.index
        return aligned.astype(bool)
    except Exception:
        # Fallback: best-effort length match
        if len(bool_series) == len(daily_data):
            return bool_series.astype(bool).reset_index(drop=True)
        # As a safe default, return all False to avoid accidental full passes
        return pd.Series([False] * len(daily_data), index=daily_data.index, dtype=bool)


def combine_filters(filter_results: List[pd.Series], operator: str = 'AND') -> pd.Series:
    """
    Combine multiple filter results using AND or OR logic.
    
    Args:
        filter_results: List of boolean series from different filters
        operator: 'AND' or 'OR'
        
    Returns:
        Combined boolean series
    """
    if not filter_results:
        return pd.Series([True], dtype=bool)
    
    # Normalize and filter out empty series; align dtype and fill NaNs
    valid_results = []
    for s in filter_results:
        if s is None or getattr(s, 'empty', True):
            continue
        s = s.astype(bool).fillna(False)
        valid_results.append(s)
    if not valid_results:
        return pd.Series([False], dtype=bool)
    
    result = valid_results[0].copy()
    for filter_result in valid_results[1:]:
        if operator == 'AND':
            result = result & filter_result
        elif operator == 'OR':
            result = result | filter_result
    
    return result


def get_filtered_minute_data(minute_data: pd.DataFrame, daily_mask: pd.Series, 
                           daily_data: pd.DataFrame) -> pd.DataFrame:
    """
    Filter minute data to only include days that match the daily filter criteria.
    
    Args:
        minute_data: DataFrame with minute-level data
        daily_mask: Boolean series indicating which days to include
        daily_data: DataFrame with daily data (for date matching)
        
    Returns:
        Filtered minute data
    """
    # Get the dates that match the filter
    filtered_dates = daily_data[daily_mask]['date'].values
    
    # Ensure minute_data has a date column
    minute_copy = minute_data.copy()
    if 'time' in minute_copy.columns:
        minute_copy['date_only'] = pd.to_datetime(minute_copy['time']).dt.date
    else:
        return minute_data  # Return original if no time column
    
    # Filter minute data to only include those dates
    filtered_minute = minute_copy[minute_copy['date_only'].isin(filtered_dates)].copy()
    filtered_minute = filtered_minute.drop('date_only', axis=1)
    
    return filtered_minute


def calculate_sample_stats(total_days: int, filtered_days: int) -> Dict[str, Any]:
    """
    Calculate sample statistics for display.
    
    Args:
        total_days: Total number of days in dataset
        filtered_days: Number of days matching filter criteria
        
    Returns:
        Dictionary with sample statistics
    """
    return {
        'total_days': total_days,
        'filtered_days': filtered_days,
        'filter_percentage': (filtered_days / total_days * 100) if total_days > 0 else 0,
        'is_sufficient': filtered_days >= 30  # Minimum sample size
    }


def calculate_individual_filter_stats(daily_data: pd.DataFrame, filter_configs: List[Dict[str, Any]], 
                                     intermarket_data: pd.DataFrame = None) -> List[Dict[str, Any]]:
    """
    Calculate statistics for each individual filter.
    
    Args:
        daily_data: DataFrame with OHLCV data
        filter_configs: List of filter configuration dictionaries
        intermarket_data: DataFrame with intermarket OHLCV data
        
    Returns:
        List of dictionaries with filter stats
    """
    stats_list = []
    
    for i, config in enumerate(filter_configs):
        try:
            # Apply individual filter
            filter_mask = apply_custom_filter(daily_data, config, intermarket_data)
            filtered_days = filter_mask.sum()
            total_days = len(daily_data)
            
            stats = {
                'filter_id': i,
                'description': create_filter_description(config),
                'total_days': total_days,
                'filtered_days': filtered_days,
                'percentage': (filtered_days / total_days * 100) if total_days > 0 else 0,
                'is_sufficient': filtered_days >= 30
            }
            stats_list.append(stats)
            
        except Exception as e:
            stats = {
                'filter_id': i,
                'description': create_filter_description(config),
                'total_days': len(daily_data),
                'filtered_days': 0,
                'percentage': 0,
                'is_sufficient': False,
                'error': str(e)
            }
            stats_list.append(stats)
    
    return stats_list


def create_filter_description(filter_config: Dict[str, Any]) -> str:
    """
    Create a human-readable description of the filter configuration.
    
    Args:
        filter_config: Filter configuration dictionary
        
    Returns:
        String description of the filter
    """
    asset_map = {
        'studied': 'Studied Product',
        'intermarket': 'Intermarket Product',
        'GC': 'Gold (GC)',
        'ES': 'S&P 500 (ES)',
        'NQ': 'Nasdaq (NQ)',
        'YM': 'Dow (YM)',
        'SI': 'Silver (SI)',
        'CL': 'Crude Oil (CL)',
        'NG': 'Natural Gas (NG)',
        'EU': 'Euro (EU)',
        'JY': 'Yen (JY)',
        'TY': '10Y Treasury (TY)',
        'vix': 'VIX'
    }
    
    metric_map = {
        'daily_return': 'Daily Return',
        'daily_range': 'Daily Range',
        'gap': 'Gap',
        'volume': 'Volume'
    }
    
    condition_map = {
        'gt': '>',
        'lt': '<',
        'gte': '>=',
        'lte': '<=',
        'eq': '='
    }
    
    asset = asset_map.get(filter_config.get('asset', 'studied'), 'Studied Product')
    metric = metric_map.get(filter_config.get('metric', 'daily_return'), 'Daily Return')
    condition = condition_map.get(filter_config.get('condition', 'gt'), '>')
    value = filter_config.get('value', 0)
    
    return f"{asset} {metric} {condition} {value:.2%}" if metric != 'volume' else f"{asset} {metric} {condition} {value:,.0f}"


def validate_filter_config(filter_config: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validate a filter configuration.
    
    Args:
        filter_config: Filter configuration to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    required_keys = ['asset', 'metric', 'condition', 'value']
    
    for key in required_keys:
        if key not in filter_config:
            return False, f"Missing required key: {key}"
    
    if filter_config['asset'] not in ['studied', 'GC', 'ES', 'vix']:
        return False, "Invalid asset selection"
    
    if filter_config['metric'] not in ['daily_return', 'daily_range', 'gap', 'volume']:
        return False, "Invalid metric selection"
    
    if filter_config['condition'] not in ['gt', 'lt', 'gte', 'lte', 'eq']:
        return False, "Invalid condition selection"
    
    try:
        float(filter_config['value'])
    except (ValueError, TypeError):
        return False, "Value must be a number"
    
    return True, ""
