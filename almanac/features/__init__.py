"""
Features Module

Statistical computations and feature engineering functions.
"""

from .stats import compute_hourly_stats, compute_minute_stats, compute_daily_stats, compute_monthly_stats
from .filters import apply_filters, apply_time_filters, trim_extremes
from .hod_lod import detect_hod_lod, compute_survival_curves
from .conditional_filters import (
    apply_quick_filter, 
    apply_custom_filter, 
    combine_filters,
    get_filtered_minute_data,
    calculate_sample_stats,
    calculate_individual_filter_stats,
    create_filter_description,
    validate_filter_config
)

__all__ = [
    'compute_hourly_stats',
    'compute_minute_stats',
    'compute_daily_stats',
    'compute_monthly_stats',
    'apply_filters',
    'apply_time_filters',
    'trim_extremes',
    'detect_hod_lod',
    'compute_survival_curves',
    'apply_quick_filter',
    'apply_custom_filter',
    'combine_filters',
    'get_filtered_minute_data',
    'calculate_sample_stats',
    'calculate_individual_filter_stats',
    'create_filter_description',
    'validate_filter_config',
]

