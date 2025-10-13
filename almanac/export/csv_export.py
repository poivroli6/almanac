"""
CSV Export Functions

Extract data from Plotly figures and export to CSV format.
"""

import pandas as pd
import io
import zipfile
from typing import Dict, Optional, List
import plotly.graph_objects as go


def extract_chart_data(figure: go.Figure) -> pd.DataFrame:
    """
    Extract data from a Plotly figure into a pandas DataFrame.
    
    Args:
        figure: Plotly Figure object or dict
        
    Returns:
        DataFrame with all trace data from the figure
    """
    if figure is None:
        return pd.DataFrame()
    
    # Convert dict to Figure if needed (Dash serializes figures as dicts)
    if isinstance(figure, dict):
        figure = go.Figure(figure)
    
    if not hasattr(figure, 'data'):
        return pd.DataFrame()
    
    data_dict = {}
    
    # Extract x-axis values (should be same for all traces)
    x_values = None
    x_label = 'X'
    
    # Get x-axis label from layout
    if hasattr(figure, 'layout') and figure.layout.xaxis and figure.layout.xaxis.title:
        x_label = figure.layout.xaxis.title.text or 'X'
    
    # Extract each trace
    for i, trace in enumerate(figure.data):
        if not hasattr(trace, 'x') or not hasattr(trace, 'y'):
            continue
            
        # Set x-values on first trace
        if x_values is None and trace.x is not None:
            x_values = list(trace.x)
            data_dict[x_label] = x_values
        
        # Add y-values with trace name as column header
        trace_name = trace.name if hasattr(trace, 'name') and trace.name else f'Series {i+1}'
        
        # Convert y data to list
        y_values = list(trace.y) if trace.y is not None else []
        
        # Handle length mismatch
        if x_values and len(y_values) != len(x_values):
            # Pad with None or truncate
            if len(y_values) < len(x_values):
                y_values.extend([None] * (len(x_values) - len(y_values)))
            else:
                y_values = y_values[:len(x_values)]
        
        data_dict[trace_name] = y_values
    
    # Create DataFrame
    if not data_dict:
        return pd.DataFrame()
    
    df = pd.DataFrame(data_dict)
    return df


def export_figure_to_csv(figure: go.Figure, filename: str = "chart_data.csv") -> str:
    """
    Export a Plotly figure's data to CSV format.
    
    Args:
        figure: Plotly Figure object
        filename: Name for the CSV file
        
    Returns:
        CSV string data
    """
    df = extract_chart_data(figure)
    
    if df.empty:
        return ""
    
    # Convert to CSV string
    csv_string = df.to_csv(index=False)
    return csv_string


def export_multiple_figures_to_csv(figures: Dict[str, go.Figure]) -> Dict[str, str]:
    """
    Export multiple figures to CSV format.
    
    Args:
        figures: Dictionary mapping chart names to Figure objects
        
    Returns:
        Dictionary mapping chart names to CSV strings
    """
    csv_data = {}
    
    for chart_name, figure in figures.items():
        csv_string = export_figure_to_csv(figure, f"{chart_name}.csv")
        if csv_string:
            csv_data[chart_name] = csv_string
    
    return csv_data


def export_all_figures_to_zip(figures: Dict[str, go.Figure]) -> bytes:
    """
    Export all figures to a ZIP archive containing CSV files.
    
    Args:
        figures: Dictionary mapping chart names to Figure objects
        
    Returns:
        ZIP file as bytes
    """
    # Create in-memory ZIP file
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for chart_name, figure in figures.items():
            csv_string = export_figure_to_csv(figure)
            
            if csv_string:
                # Clean filename
                safe_name = chart_name.replace(' ', '_').replace('/', '_')
                filename = f"{safe_name}.csv"
                
                # Add to ZIP
                zip_file.writestr(filename, csv_string)
    
    zip_buffer.seek(0)
    return zip_buffer.getvalue()


def create_csv_download_data(figure: go.Figure, chart_title: str = "chart") -> Dict[str, str]:
    """
    Create data URI for CSV download button.
    
    Args:
        figure: Plotly Figure object
        chart_title: Title to use in filename
        
    Returns:
        Dictionary with 'content' (CSV string) and 'filename'
    """
    csv_string = export_figure_to_csv(figure)
    
    # Create safe filename
    safe_title = chart_title.replace(' ', '_').replace('/', '_').lower()
    filename = f"{safe_title}.csv"
    
    return {
        'content': csv_string,
        'filename': filename
    }


def dataframe_to_csv_download(df: pd.DataFrame, filename: str = "data.csv") -> Dict[str, str]:
    """
    Convert a DataFrame to CSV download data.
    
    Args:
        df: pandas DataFrame
        filename: Desired filename
        
    Returns:
        Dictionary with 'content' (CSV string) and 'filename'
    """
    csv_string = df.to_csv(index=False)
    
    return {
        'content': csv_string,
        'filename': filename
    }

