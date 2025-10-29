"""
Features Module

Statistical computations and feature engineering functions.
"""

from .stats import compute_hourly_stats, compute_minute_stats, compute_daily_stats, compute_monthly_stats
from .weekly_stats import compute_weekly_stats, compute_weekly_day_performance, compute_weekly_volatility_analysis
from .monthly_stats import compute_monthly_stats as compute_monthly_stats_module, compute_seasonal_patterns, get_monthly_summary_cards, compute_multi_year_monthly_stats
from .filters import apply_filters, apply_time_filters, trim_extremes
from .hod_lod import (
    detect_hod_lod, 
    compute_survival_curves, 
    compute_hod_lod_heatmap, 
    compute_rolling_median_time, 
    compute_trend_test
)
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
from .advanced_analytics import (
    StatisticalSignificanceTester,
    CorrelationAnalyzer,
    VolatilityAnalyzer,
    RegimeDetector,
    PatternRecognizer,
    RiskMetrics,
    create_analytics_summary
)

__all__ = [
    'compute_hourly_stats',
    'compute_minute_stats',
    'compute_daily_stats',
    'compute_monthly_stats',
    'compute_weekly_stats',
    'compute_weekly_day_performance',
    'compute_weekly_volatility_analysis',
    'compute_monthly_stats_module',
    'compute_seasonal_patterns',
    'get_monthly_summary_cards',
    'compute_multi_year_monthly_stats',
    'apply_filters',
    'apply_time_filters',
    'trim_extremes',
    'detect_hod_lod',
    'compute_survival_curves',
    'compute_hod_lod_heatmap',
    'compute_rolling_median_time',
    'compute_trend_test',
    'apply_quick_filter',
    'apply_custom_filter',
    'combine_filters',
    'get_filtered_minute_data',
    'calculate_sample_stats',
    'calculate_individual_filter_stats',
    'create_filter_description',
    'validate_filter_config',
    'StatisticalSignificanceTester',
    'CorrelationAnalyzer',
    'VolatilityAnalyzer',
    'RegimeDetector',
    'PatternRecognizer',
    'RiskMetrics',
    'create_analytics_summary'
]

