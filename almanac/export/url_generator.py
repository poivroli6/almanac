"""
URL Generator Functions

Generate shareable URLs with encoded query parameters for preserving dashboard state.
"""

import json
import base64
from typing import Dict, List, Optional, Any
from urllib.parse import urlencode, parse_qs, urlparse, urlunparse
import zlib


def encode_filter_state(
    product: str,
    start_date: str,
    end_date: str,
    filters: Optional[List[str]] = None,
    minute_hour: Optional[int] = None,
    vol_threshold: Optional[float] = None,
    pct_threshold: Optional[float] = None,
    trim_percentage: Optional[float] = None,
    stat_measures: Optional[List[str]] = None,
    intermarket_product: Optional[str] = None,
    timeA_hour: Optional[int] = None,
    timeA_minute: Optional[int] = None,
    timeB_hour: Optional[int] = None,
    timeB_minute: Optional[int] = None
) -> str:
    """
    Encode filter state into a compressed base64 string.
    
    Args:
        product: Studied product symbol
        start_date: Start date string (YYYY-MM-DD)
        end_date: End date string (YYYY-MM-DD)
        filters: List of active filter values
        minute_hour: Selected minute hour
        vol_threshold: Volume threshold value
        pct_threshold: Percentage threshold value
        trim_percentage: Trim percentage value
        stat_measures: List of selected statistical measures
        intermarket_product: Intermarket product symbol
        timeA_hour: Time A hour
        timeA_minute: Time A minute
        timeB_hour: Time B hour
        timeB_minute: Time B minute
        
    Returns:
        Base64-encoded compressed JSON string
    """
    state = {
        'product': product,
        'start_date': start_date,
        'end_date': end_date
    }
    
    # Add optional parameters only if they have values
    if filters:
        state['filters'] = filters
    if minute_hour is not None:
        state['minute_hour'] = minute_hour
    if vol_threshold is not None:
        state['vol_threshold'] = vol_threshold
    if pct_threshold is not None:
        state['pct_threshold'] = pct_threshold
    if trim_percentage is not None:
        state['trim_percentage'] = trim_percentage
    if stat_measures:
        state['stat_measures'] = stat_measures
    if intermarket_product:
        state['intermarket_product'] = intermarket_product
    if timeA_hour is not None:
        state['timeA_hour'] = timeA_hour
    if timeA_minute is not None:
        state['timeA_minute'] = timeA_minute
    if timeB_hour is not None:
        state['timeB_hour'] = timeB_hour
    if timeB_minute is not None:
        state['timeB_minute'] = timeB_minute
    
    # Convert to JSON
    json_str = json.dumps(state, separators=(',', ':'))  # Compact JSON
    
    # Compress with zlib
    compressed = zlib.compress(json_str.encode('utf-8'))
    
    # Encode to base64 (URL-safe)
    encoded = base64.urlsafe_b64encode(compressed).decode('ascii')
    
    return encoded


def decode_filter_state(encoded_state: str) -> Dict[str, Any]:
    """
    Decode a compressed base64 filter state string.
    
    Args:
        encoded_state: Base64-encoded compressed JSON string
        
    Returns:
        Dictionary with filter state parameters
    """
    try:
        # Decode from base64
        compressed = base64.urlsafe_b64decode(encoded_state.encode('ascii'))
        
        # Decompress
        json_str = zlib.decompress(compressed).decode('utf-8')
        
        # Parse JSON
        state = json.loads(json_str)
        
        return state
    except Exception as e:
        print(f"Error decoding filter state: {e}")
        return {}


def generate_shareable_url(
    base_url: str,
    product: str,
    start_date: str,
    end_date: str,
    **kwargs
) -> str:
    """
    Generate a shareable URL with all current filter settings.
    
    Args:
        base_url: Base URL of the application (e.g., 'http://localhost:8085')
        product: Studied product symbol
        start_date: Start date string
        end_date: End date string
        **kwargs: Additional filter parameters
        
    Returns:
        Complete shareable URL
    """
    # Encode state
    encoded = encode_filter_state(
        product=product,
        start_date=start_date,
        end_date=end_date,
        **kwargs
    )
    
    # Build URL with state parameter
    params = {'state': encoded}
    query_string = urlencode(params)
    
    # Combine base URL and query string
    if base_url.endswith('/'):
        base_url = base_url[:-1]
    
    url = f"{base_url}?{query_string}"
    
    return url


def generate_simple_shareable_url(
    base_url: str,
    product: str,
    start_date: str,
    end_date: str,
    filters: Optional[List[str]] = None
) -> str:
    """
    Generate a simpler shareable URL with basic parameters (uncompressed).
    
    Args:
        base_url: Base URL of the application
        product: Studied product symbol
        start_date: Start date string
        end_date: End date string
        filters: List of filter values
        
    Returns:
        Complete shareable URL with query parameters
    """
    params = {
        'product': product,
        'start': start_date,
        'end': end_date
    }
    
    if filters:
        params['filters'] = ','.join(filters)
    
    query_string = urlencode(params)
    
    if base_url.endswith('/'):
        base_url = base_url[:-1]
    
    url = f"{base_url}?{query_string}"
    
    return url


def parse_url_parameters(url: str) -> Dict[str, Any]:
    """
    Parse URL parameters and decode filter state if present.
    
    Args:
        url: Complete URL or query string
        
    Returns:
        Dictionary with parsed parameters
    """
    # Parse URL
    parsed = urlparse(url)
    query_params = parse_qs(parsed.query)
    
    # Check for encoded state
    if 'state' in query_params:
        encoded_state = query_params['state'][0]
        return decode_filter_state(encoded_state)
    
    # Otherwise, parse simple parameters
    params = {}
    
    if 'product' in query_params:
        params['product'] = query_params['product'][0]
    if 'start' in query_params:
        params['start_date'] = query_params['start'][0]
    if 'end' in query_params:
        params['end_date'] = query_params['end'][0]
    if 'filters' in query_params:
        params['filters'] = query_params['filters'][0].split(',')
    
    return params


def create_preset_url(
    base_url: str,
    preset_name: str,
    preset_config: Dict[str, Any]
) -> str:
    """
    Create a URL from a saved preset configuration.
    
    Args:
        base_url: Base URL of the application
        preset_name: Name of the preset
        preset_config: Preset configuration dictionary
        
    Returns:
        Shareable URL
    """
    return generate_shareable_url(
        base_url=base_url,
        **preset_config
    )


def shorten_url_safe_base64(long_string: str, max_length: int = 2000) -> str:
    """
    Shorten a base64 string if it exceeds max_length by using higher compression.
    
    Args:
        long_string: Long base64 string
        max_length: Maximum allowed length
        
    Returns:
        Shortened string (may be same as input if already short enough)
    """
    if len(long_string) <= max_length:
        return long_string
    
    # Already compressed with zlib, so just truncate and warn
    # In production, you might want to use a URL shortening service
    print(f"Warning: URL is too long ({len(long_string)} chars), consider using fewer filters")
    
    return long_string[:max_length]


def extract_chart_metadata_from_url(url: str) -> Dict[str, str]:
    """
    Extract chart-related metadata from a URL.
    
    Args:
        url: Complete URL
        
    Returns:
        Dictionary with metadata (product, date range, etc.)
    """
    params = parse_url_parameters(url)
    
    metadata = {
        'product': params.get('product', 'Unknown'),
        'start_date': params.get('start_date', 'Unknown'),
        'end_date': params.get('end_date', 'Unknown'),
        'filters_count': len(params.get('filters', [])),
    }
    
    return metadata


def get_current_page_url(hostname: str = 'localhost', port: int = 8085, https: bool = False) -> str:
    """
    Get the current page base URL.
    
    Args:
        hostname: Server hostname
        port: Server port
        https: Whether to use HTTPS
        
    Returns:
        Base URL string
    """
    protocol = 'https' if https else 'http'
    
    if port == 80 and not https:
        return f"{protocol}://{hostname}"
    elif port == 443 and https:
        return f"{protocol}://{hostname}"
    else:
        return f"{protocol}://{hostname}:{port}"


# Preset configurations for common scenarios
PRESET_CONFIGS = {
    'es_current_month': {
        'product': 'ES',
        'start_date': '2025-10-01',
        'end_date': '2025-04-08',
        'filters': ['monday', 'tuesday', 'wednesday', 'thursday', 'friday'],
        'minute_hour': 9,
        'trim_percentage': 5,
        'stat_measures': ['mean', 'median']
    },
    'gc_high_vol': {
        'product': 'GC',
        'start_date': '2025-01-01',
        'end_date': '2025-04-08',
        'filters': ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'relvol_gt'],
        'vol_threshold': 1.5,
        'minute_hour': 8,
        'trim_percentage': 10,
        'stat_measures': ['mean', 'trimmed_mean', 'median']
    },
}


def get_preset_config(preset_name: str) -> Optional[Dict[str, Any]]:
    """
    Get a preset configuration by name.
    
    Args:
        preset_name: Name of the preset
        
    Returns:
        Preset configuration dictionary or None
    """
    return PRESET_CONFIGS.get(preset_name)

