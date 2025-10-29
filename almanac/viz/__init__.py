"""
Visualization Module

Figure factory functions for consistent chart generation.
"""

from .figures import (
    make_line_chart,
    make_heatmap,
    make_survival_curve,
    make_violin_plot,
    make_multi_year_line_chart,
)

__all__ = [
    'make_line_chart',
    'make_heatmap',
    'make_survival_curve',
    'make_violin_plot',
    'make_multi_year_line_chart',
]

