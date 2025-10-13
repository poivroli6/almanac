"""
Visualization Module

Figure factory functions for consistent chart generation.
"""

from .figures import (
    make_line_chart,
    make_heatmap,
    make_survival_curve,
    make_violin_plot,
)

__all__ = [
    'make_line_chart',
    'make_heatmap',
    'make_survival_curve',
    'make_violin_plot',
]

