"""
PNG Export Functions

Handle PNG downloads for Plotly charts using built-in modebar functionality.
"""

from typing import Dict, Optional, List
import plotly.graph_objects as go


def get_png_download_config(
    filename: str = "chart",
    width: int = 1200,
    height: int = 600,
    scale: int = 2
) -> Dict:
    """
    Get Plotly config dictionary to enable PNG download with custom settings.
    
    Args:
        filename: Default filename for download (without extension)
        width: Image width in pixels
        height: Image height in pixels
        scale: Scale factor for image resolution (2 = retina)
        
    Returns:
        Dictionary to pass to dcc.Graph's config parameter
    """
    config = {
        'toImageButtonOptions': {
            'format': 'png',  # Can also be 'svg', 'jpeg', 'webp'
            'filename': filename,
            'height': height,
            'width': width,
            'scale': scale  # Multiply width/height for higher resolution
        },
        'displayModeBar': True,
        'modeBarButtonsToAdd': ['downloadImage'],
        'modeBarButtonsToRemove': [],
        'displaylogo': False
    }
    
    return config


def get_enhanced_config(
    filename: str = "chart",
    include_download: bool = True,
    include_zoom: bool = True,
    include_pan: bool = True,
    include_select: bool = False
) -> Dict:
    """
    Get enhanced Plotly config with customizable modebar buttons.
    
    Args:
        filename: Default filename for download
        include_download: Show download button
        include_zoom: Show zoom buttons
        include_pan: Show pan button
        include_select: Show selection tools
        
    Returns:
        Dictionary to pass to dcc.Graph's config parameter
    """
    config = {
        'toImageButtonOptions': {
            'format': 'png',
            'filename': filename,
            'height': 600,
            'width': 1200,
            'scale': 2
        },
        'displayModeBar': True,
        'displaylogo': False
    }
    
    # Build buttons to remove list
    buttons_to_remove = []
    
    if not include_zoom:
        buttons_to_remove.extend(['zoomIn2d', 'zoomOut2d', 'autoScale2d'])
    
    if not include_pan:
        buttons_to_remove.append('pan2d')
    
    if not include_select:
        buttons_to_remove.extend(['select2d', 'lasso2d'])
    
    config['modeBarButtonsToRemove'] = buttons_to_remove
    
    return config


def create_download_button(chart_id: str, button_text: str = "Download PNG") -> Dict:
    """
    Create a custom download button configuration.
    
    Note: This is for reference. Plotly's built-in modebar button is recommended.
    
    Args:
        chart_id: ID of the chart to download
        button_text: Text to display on button
        
    Returns:
        Dictionary with button configuration
    """
    return {
        'id': f'download-btn-{chart_id}',
        'text': button_text,
        'chart_id': chart_id
    }


def get_export_formats() -> List[str]:
    """
    Get list of supported export formats.
    
    Returns:
        List of format strings
    """
    return ['png', 'svg', 'jpeg', 'webp']


def get_config_for_format(
    export_format: str = 'png',
    filename: str = 'chart',
    width: int = 1200,
    height: int = 600
) -> Dict:
    """
    Get Plotly config for a specific export format.
    
    Args:
        export_format: One of 'png', 'svg', 'jpeg', 'webp'
        filename: Default filename (without extension)
        width: Image width in pixels
        height: Image height in pixels
        
    Returns:
        Dictionary to pass to dcc.Graph's config parameter
    """
    if export_format not in get_export_formats():
        export_format = 'png'
    
    config = {
        'toImageButtonOptions': {
            'format': export_format,
            'filename': filename,
            'height': height,
            'width': width,
            'scale': 2 if export_format == 'png' else 1
        },
        'displayModeBar': True,
        'displaylogo': False
    }
    
    return config


def enhance_figure_for_export(figure: go.Figure, title: Optional[str] = None) -> go.Figure:
    """
    Enhance a figure's layout for better export quality.
    
    Args:
        figure: Plotly Figure object
        title: Optional title to set/override
        
    Returns:
        Enhanced Figure object
    """
    if figure is None:
        return figure
    
    # Update layout for better export
    updates = {
        'font': {'size': 12},
        'margin': {'l': 60, 'r': 40, 't': 60, 'b': 60},
    }
    
    if title:
        updates['title'] = {
            'text': title,
            'font': {'size': 16, 'color': '#2c3e50'}
        }
    
    figure.update_layout(**updates)
    
    return figure


# Common configurations for different use cases
CONFIGS = {
    'default': get_png_download_config(),
    'high_res': get_png_download_config(width=1920, height=1080, scale=3),
    'print': get_png_download_config(width=2400, height=1200, scale=2),
    'presentation': get_png_download_config(width=1920, height=1080, scale=2),
    'minimal': {
        'displayModeBar': True,
        'displaylogo': False,
        'modeBarButtonsToRemove': ['pan2d', 'select2d', 'lasso2d', 'resetScale2d']
    }
}


def get_preset_config(preset: str = 'default') -> Dict:
    """
    Get a preset configuration.
    
    Args:
        preset: One of 'default', 'high_res', 'print', 'presentation', 'minimal'
        
    Returns:
        Configuration dictionary
    """
    return CONFIGS.get(preset, CONFIGS['default'])

