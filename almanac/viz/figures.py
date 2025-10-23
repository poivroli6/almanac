"""
Figure Factory Functions

Reusable functions for creating consistent Plotly charts.
"""

import plotly.graph_objects as go
import pandas as pd
from typing import Optional, List


def make_line_chart(
    x: pd.Series | list,
    y: pd.Series | list,
    title: str,
    xaxis_title: str = "Time",
    yaxis_title: str = "Value",
    show_markers: bool = True,
    confidence_bands: Optional[tuple] = None,
    mean_data: Optional[pd.Series | list] = None,
    trimmed_mean_data: Optional[pd.Series | list] = None,
    median_data: Optional[pd.Series | list] = None,
    mode_data: Optional[pd.Series | list] = None,
    trim_pct: float = 5.0,
    selected_measures: Optional[list] = None
) -> go.Figure:
    """
    Create a line chart with multiple statistical measures.
    
    Args:
        x: X-axis values
        y: Y-axis values (primary series)
        title: Chart title
        xaxis_title: X-axis label
        yaxis_title: Y-axis label
        show_markers: Whether to show markers on the line
        confidence_bands: Optional tuple of (lower_bound, upper_bound) series
        mean_data: Mean data (if different from y)
        trimmed_mean_data: Trimmed mean data
        median_data: Median data
        mode_data: Mode data
        trim_pct: Trim percentage for display
        selected_measures: List of measures to display ['mean', 'trimmed_mean', 'median', 'mode']
        
    Returns:
        Plotly Figure
    """
    # Default to showing all measures if none specified
    if selected_measures is None:
        selected_measures = ['mean', 'trimmed_mean', 'median', 'mode']
    
    # Convert to numpy arrays for consistent handling
    x_vals = x.values if hasattr(x, 'values') else x
    y_vals = y.values if hasattr(y, 'values') else y
    
    mode = 'lines+markers' if show_markers else 'lines'
    
    fig = go.Figure()
    
    # Add confidence bands if provided
    if confidence_bands is not None:
        lower, upper = confidence_bands
        fig.add_trace(go.Scatter(
            x=x_vals,
            y=upper,
            mode='lines',
            line=dict(width=0),
            showlegend=False,
            hoverinfo='skip'
        ))
        fig.add_trace(go.Scatter(
            x=x_vals,
            y=lower,
            mode='lines',
            line=dict(width=0),
            fillcolor='rgba(68, 68, 68, 0.2)',
            fill='tonexty',
            showlegend=False,
            hoverinfo='skip'
        ))
    
    # Define colors and styles for each measure
    measure_styles = {
        'mean': {'color': '#1f77b4', 'width': 2, 'dash': 'solid', 'name': 'Mean'},
        'trimmed_mean': {'color': '#ff7f0e', 'width': 2, 'dash': 'dash', 'name': f'Trimmed Mean ({trim_pct:.0f}%)'},
        'median': {'color': '#2ca02c', 'width': 2, 'dash': 'dot', 'name': 'Median'},
        'mode': {'color': '#d62728', 'width': 2, 'dash': 'dashdot', 'name': 'Mode'}
    }
    
    # Add traces for selected measures
    if 'mean' in selected_measures:
        # Use mean_data if provided, otherwise use y_data
        mean_vals = mean_data.values if mean_data is not None and hasattr(mean_data, 'values') else y_vals
        if mean_data is not None and not hasattr(mean_data, 'values'):
            mean_vals = mean_data
        elif mean_data is not None:
            mean_vals = mean_data.values
        
        fig.add_trace(go.Scatter(
            x=x_vals,
            y=mean_vals,
            mode=mode,
            name=measure_styles['mean']['name'],
            line=dict(
                color=measure_styles['mean']['color'],
                width=measure_styles['mean']['width'],
                dash=measure_styles['mean']['dash']
            )
        ))
    
    if 'trimmed_mean' in selected_measures and trimmed_mean_data is not None:
        trimmed_mean_vals = trimmed_mean_data.values if hasattr(trimmed_mean_data, 'values') else trimmed_mean_data
        fig.add_trace(go.Scatter(
            x=x_vals,
            y=trimmed_mean_vals,
            mode=mode,
            name=measure_styles['trimmed_mean']['name'],
            line=dict(
                color=measure_styles['trimmed_mean']['color'],
                width=measure_styles['trimmed_mean']['width'],
                dash=measure_styles['trimmed_mean']['dash']
            )
        ))
    
    if 'median' in selected_measures and median_data is not None:
        median_vals = median_data.values if hasattr(median_data, 'values') else median_data
        fig.add_trace(go.Scatter(
            x=x_vals,
            y=median_vals,
            mode=mode,
            name=measure_styles['median']['name'],
            line=dict(
                color=measure_styles['median']['color'],
                width=measure_styles['median']['width'],
                dash=measure_styles['median']['dash']
            )
        ))
    
    if 'mode' in selected_measures and mode_data is not None:
        mode_vals = mode_data.values if hasattr(mode_data, 'values') else mode_data
        fig.add_trace(go.Scatter(
            x=x_vals,
            y=mode_vals,
            mode=mode,
            name=measure_styles['mode']['name'],
            line=dict(
                color=measure_styles['mode']['color'],
                width=measure_styles['mode']['width'],
                dash=measure_styles['mode']['dash']
            )
        ))
    
    fig.update_layout(
        title=title,
        xaxis_title=xaxis_title,
        yaxis_title=yaxis_title,
        margin=dict(l=40, r=20, t=50, b=40),
        hovermode='x unified',
        template='plotly_white'
    )
    
    return fig


def make_heatmap(
    data: pd.DataFrame,
    title: str,
    xaxis_title: str = "Time",
    yaxis_title: str = "Group",
    colorscale: str = "Viridis"
) -> go.Figure:
    """
    Create a heatmap from a pivot table or matrix.
    
    Args:
        data: DataFrame where index = y-axis, columns = x-axis
        title: Chart title
        xaxis_title: X-axis label
        yaxis_title: Y-axis label
        colorscale: Plotly colorscale name
        
    Returns:
        Plotly Figure
    """
    fig = go.Figure(data=go.Heatmap(
        z=data.values,
        x=data.columns,
        y=data.index,
        colorscale=colorscale,
        hoverongaps=False,
        hovertemplate='%{y}<br>%{x}<br>Count: %{z}<extra></extra>'
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title=xaxis_title,
        yaxis_title=yaxis_title,
        margin=dict(l=100, r=20, t=50, b=80),
        template='plotly_white'
    )
    
    return fig


def make_survival_curve(
    x: pd.Series | list,
    y: pd.Series | list,
    title: str,
    xaxis_title: str = "Minutes Since Midnight",
    yaxis_title: str = "Cumulative Probability"
) -> go.Figure:
    """
    Create a survival curve (step function).
    
    Args:
        x: Time values
        y: Cumulative probability values (0 to 1)
        title: Chart title
        xaxis_title: X-axis label
        yaxis_title: Y-axis label
        
    Returns:
        Plotly Figure
    """
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=x,
        y=y,
        mode='lines',
        line=dict(shape='hv', color='#2ca02c', width=2),
        fill='tozeroy',
        fillcolor='rgba(44, 160, 44, 0.2)',
        name='Probability'
    ))
    
    # Add reference lines for key percentiles
    if len(y) > 0:
        for percentile, label in [(0.25, '25%'), (0.5, '50%'), (0.75, '75%')]:
            if y.max() >= percentile:
                # Find x value where y crosses percentile
                idx = (y >= percentile).argmax() if hasattr(y, 'argmax') else 0
                x_val = x.iloc[idx] if hasattr(x, 'iloc') else x[idx]
                
                fig.add_hline(
                    y=percentile,
                    line_dash="dash",
                    line_color="gray",
                    opacity=0.5,
                    annotation_text=label,
                    annotation_position="right"
                )
    
    fig.update_layout(
        title=title,
        xaxis_title=xaxis_title,
        yaxis_title=yaxis_title,
        yaxis=dict(range=[0, 1.05]),
        margin=dict(l=40, r=20, t=50, b=40),
        hovermode='x unified',
        template='plotly_white'
    )
    
    return fig


def make_violin_plot(
    data: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str,
    xaxis_title: str = "Group",
    yaxis_title: str = "Value"
) -> go.Figure:
    """
    Create a violin plot for comparing distributions across groups.
    
    Args:
        data: DataFrame with data
        x_col: Column name for grouping (x-axis)
        y_col: Column name for values (y-axis)
        title: Chart title
        xaxis_title: X-axis label
        yaxis_title: Y-axis label
        
    Returns:
        Plotly Figure
    """
    fig = go.Figure()
    
    groups = data[x_col].unique()
    
    for group in groups:
        group_data = data[data[x_col] == group][y_col]
        
        fig.add_trace(go.Violin(
            y=group_data,
            name=str(group),
            box_visible=True,
            meanline_visible=True
        ))
    
    fig.update_layout(
        title=title,
        xaxis_title=xaxis_title,
        yaxis_title=yaxis_title,
        margin=dict(l=40, r=20, t=50, b=40),
        template='plotly_white',
        showlegend=True
    )
    
    return fig


def make_box_plot(
    data: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str,
    xaxis_title: str = "Group",
    yaxis_title: str = "Value"
) -> go.Figure:
    """
    Create a box plot for comparing distributions across groups.
    
    Args:
        data: DataFrame with data
        x_col: Column name for grouping (x-axis)
        y_col: Column name for values (y-axis)
        title: Chart title
        xaxis_title: X-axis label
        yaxis_title: Y-axis label
        
    Returns:
        Plotly Figure
    """
    fig = go.Figure()
    
    groups = data[x_col].unique()
    
    for group in groups:
        group_data = data[data[x_col] == group][y_col]
        
        fig.add_trace(go.Box(
            y=group_data,
            name=str(group),
            boxmean='sd'
        ))
    
    fig.update_layout(
        title=title,
        xaxis_title=xaxis_title,
        yaxis_title=yaxis_title,
        margin=dict(l=40, r=20, t=50, b=40),
        template='plotly_white',
        showlegend=True
    )
    
    return fig


def make_scatter(
    x: pd.Series | list,
    y: pd.Series | list,
    title: str,
    xaxis_title: str = "X",
    yaxis_title: str = "Y",
    color: Optional[pd.Series | list] = None,
    size: Optional[pd.Series | list] = None
) -> go.Figure:
    """
    Create a scatter plot.
    
    Args:
        x: X-axis values
        y: Y-axis values
        title: Chart title
        xaxis_title: X-axis label
        yaxis_title: Y-axis label
        color: Optional values for color mapping
        size: Optional values for size mapping
        
    Returns:
        Plotly Figure
    """
    marker_dict = {}
    
    if color is not None:
        marker_dict['color'] = color
        marker_dict['colorscale'] = 'Viridis'
        marker_dict['showscale'] = True
    
    if size is not None:
        marker_dict['size'] = size
        marker_dict['sizemode'] = 'diameter'
        marker_dict['sizeref'] = 2
    
    fig = go.Figure(data=go.Scatter(
        x=x,
        y=y,
        mode='markers',
        marker=marker_dict if marker_dict else None
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title=xaxis_title,
        yaxis_title=yaxis_title,
        margin=dict(l=40, r=20, t=50, b=40),
        hovermode='closest',
        template='plotly_white'
    )
    
    return fig


def make_multi_year_line_chart(
    yearly_stats: dict,
    title: str,
    xaxis_title: str = "Month",
    yaxis_title: str = "Value",
    stat_type: str = "avg_pct_chg",
    show_markers: bool = True,
    show_statistical_lines: bool = True
) -> go.Figure:
    """
    Create a multi-year line chart showing each year as a different colored line,
    plus statistical summary lines (Mean, Median, Mode) across all years.
    
    Args:
        yearly_stats: Dictionary with year as key and DataFrame as value
        title: Chart title
        xaxis_title: X-axis label
        yaxis_title: Y-axis label
        stat_type: Which statistic to plot ('avg_pct_chg', 'trimmed_pct_chg', 'med_pct_chg', 'mode_pct_chg', 'var_pct_chg', 'avg_range', 'trimmed_range', 'med_range', 'mode_range', 'var_range')
        show_markers: Whether to show markers on the lines
        show_statistical_lines: Whether to show Mean, Median, Mode lines
        
    Returns:
        Plotly Figure with multiple colored lines for each year plus statistical lines
    """
    fig = go.Figure()
    
    # Define colors for different years
    year_colors = [
        '#1f77b4',  # blue
        '#ff7f0e',  # orange
        '#2ca02c',  # green
        '#d62728',  # red
        '#9467bd',  # purple
        '#8c564b',  # brown
        '#e377c2',  # pink
        '#7f7f7f',  # gray
        '#bcbd22',  # olive
        '#17becf'   # cyan
    ]
    
    # Define colors and styles for statistical lines
    stat_colors = {
        'mean': '#000000',      # black, solid
        'median': '#FF0000',    # red, dashed
        'mode': '#00AA00'       # green, dotted
    }
    
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    # Collect all data for statistical calculations
    all_data_by_month = {i: [] for i in range(12)}  # 0-11 for Jan-Dec
    
    # Add a line for each year
    for i, (year, year_df) in enumerate(yearly_stats.items()):
        color = year_colors[i % len(year_colors)]
        
        # Get the data for this year
        y_values = year_df[stat_type].values
        
        # Store data for statistical calculations
        for month_idx, value in enumerate(y_values):
            all_data_by_month[month_idx].append(value)
        
        fig.add_trace(go.Scatter(
            x=month_names,
            y=y_values,
            mode='lines+markers' if show_markers else 'lines',
            name=f'{year}',
            line=dict(color=color, width=2),
            marker=dict(size=6, color=color),
            hovertemplate=f'<b>{year}</b><br>' +
                         f'Month: %{{x}}<br>' +
                         f'{stat_type.replace("_", " ").title()}: %{{y:.4f}}<br>' +
                         '<extra></extra>'
        ))
    
    # Add statistical lines if requested
    if show_statistical_lines and len(yearly_stats) > 1:
        import numpy as np
        
        # Calculate Mean, Median, Mode for each month
        mean_values = []
        median_values = []
        mode_values = []
        
        for month_idx in range(12):
            month_data = all_data_by_month[month_idx]
            if month_data:
                mean_values.append(np.mean(month_data))
                median_values.append(np.median(month_data))
                # For mode, use the most frequent value (simplified)
                mode_values.append(max(set(month_data), key=month_data.count))
            else:
                mean_values.append(0)
                median_values.append(0)
                mode_values.append(0)
        
        # Add Mean line
        fig.add_trace(go.Scatter(
            x=month_names,
            y=mean_values,
            mode='lines',
            name='Mean',
            line=dict(color=stat_colors['mean'], width=3, dash='solid'),
            hovertemplate='<b>Mean</b><br>' +
                         'Month: %{x}<br>' +
                         'Mean: %{y:.4f}<br>' +
                         '<extra></extra>'
        ))
        
        # Add Median line
        fig.add_trace(go.Scatter(
            x=month_names,
            y=median_values,
            mode='lines',
            name='Median',
            line=dict(color=stat_colors['median'], width=3, dash='dash'),
            hovertemplate='<b>Median</b><br>' +
                         'Month: %{x}<br>' +
                         'Median: %{y:.4f}<br>' +
                         '<extra></extra>'
        ))
        
        # Add Mode line
        fig.add_trace(go.Scatter(
            x=month_names,
            y=mode_values,
            mode='lines',
            name='Mode',
            line=dict(color=stat_colors['mode'], width=3, dash='dot'),
            hovertemplate='<b>Mode</b><br>' +
                         'Month: %{x}<br>' +
                         'Mode: %{y:.4f}<br>' +
                         '<extra></extra>'
        ))
    
    fig.update_layout(
        title=title,
        xaxis_title=xaxis_title,
        yaxis_title=yaxis_title,
        margin=dict(l=40, r=20, t=50, b=40),
        hovermode='closest',
        template='plotly_white',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig
