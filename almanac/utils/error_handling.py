"""
Error Handling Utilities

Provides comprehensive error handling for the Almanac Futures application.
"""

import logging
import traceback
from typing import Optional, Dict, Any, Callable
from functools import wraps
import pandas as pd
from dash import html

logger = logging.getLogger(__name__)


class AlmanacError(Exception):
    """Base exception for Almanac Futures application."""
    
    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}


class DataLoadError(AlmanacError):
    """Exception raised when data loading fails."""
    pass


class FilterError(AlmanacError):
    """Exception raised when filter application fails."""
    pass


class CalculationError(AlmanacError):
    """Exception raised when calculations fail."""
    pass


class ValidationError(AlmanacError):
    """Exception raised when input validation fails."""
    pass


def handle_data_loading_error(func: Callable) -> Callable:
    """
    Decorator to handle data loading errors.
    
    Args:
        func: Function to wrap
        
    Returns:
        Wrapped function with error handling
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Data loading error in {func.__name__}: {e}")
            logger.error(traceback.format_exc())
            raise DataLoadError(
                f"Failed to load data in {func.__name__}: {str(e)}",
                error_code="DATA_LOAD_ERROR",
                details={"function": func.__name__, "original_error": str(e)}
            )
    return wrapper


def handle_calculation_error(func: Callable) -> Callable:
    """
    Decorator to handle calculation errors.
    
    Args:
        func: Function to wrap
        
    Returns:
        Wrapped function with error handling
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Calculation error in {func.__name__}: {e}")
            logger.error(traceback.format_exc())
            raise CalculationError(
                f"Failed to perform calculation in {func.__name__}: {str(e)}",
                error_code="CALCULATION_ERROR",
                details={"function": func.__name__, "original_error": str(e)}
            )
    return wrapper


def handle_filter_error(func: Callable) -> Callable:
    """
    Decorator to handle filter application errors.
    
    Args:
        func: Function to wrap
        
    Returns:
        Wrapped function with error handling
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Filter error in {func.__name__}: {e}")
            logger.error(traceback.format_exc())
            raise FilterError(
                f"Failed to apply filters in {func.__name__}: {str(e)}",
                error_code="FILTER_ERROR",
                details={"function": func.__name__, "original_error": str(e)}
            )
    return wrapper


def create_error_message(error: Exception, context: Optional[str] = None) -> html.Div:
    """
    Create a user-friendly error message component.
    
    Args:
        error: Exception that occurred
        context: Additional context about where the error occurred
        
    Returns:
        html.Div: Error message component
    """
    error_type = type(error).__name__
    error_message = str(error)
    
    # Create user-friendly message based on error type
    if isinstance(error, DataLoadError):
        user_message = "Unable to load data. Please check your connection and try again."
    elif isinstance(error, FilterError):
        user_message = "Error applying filters. Please check your filter settings."
    elif isinstance(error, CalculationError):
        user_message = "Error performing calculations. Please try again."
    elif isinstance(error, ValidationError):
        user_message = "Invalid input parameters. Please check your settings."
    else:
        user_message = "An unexpected error occurred. Please try again."
    
    # Create error component
    error_component = html.Div([
        html.Div([
            html.H4("⚠️ Error", style={'color': '#dc3545', 'marginBottom': '10px'}),
            html.P(user_message, style={'marginBottom': '10px'}),
            html.Details([
                html.Summary("Technical Details", style={'cursor': 'pointer', 'color': '#6c757d'}),
                html.Pre(f"{error_type}: {error_message}", style={
                    'fontSize': '12px',
                    'backgroundColor': '#f8f9fa',
                    'padding': '10px',
                    'borderRadius': '4px',
                    'marginTop': '10px',
                    'overflow': 'auto'
                })
            ])
        ], style={
            'padding': '20px',
            'backgroundColor': '#f8d7da',
            'border': '1px solid #f5c6cb',
            'borderRadius': '5px',
            'color': '#721c24'
        })
    ])
    
    if context:
        logger.info(f"Error context: {context}")
    
    return error_component


def create_empty_chart(title: str = "No Data", message: str = "No data available") -> Dict[str, Any]:
    """
    Create an empty chart configuration for error states.
    
    Args:
        title: Chart title
        message: Error message
        
    Returns:
        Dict: Empty chart configuration
    """
    return {
        'data': [],
        'layout': {
            'title': title,
            'xaxis': {'title': ''},
            'yaxis': {'title': ''},
            'annotations': [{
                'text': message,
                'x': 0.5,
                'y': 0.5,
                'xref': 'paper',
                'yref': 'paper',
                'showarrow': False,
                'font': {'size': 16, 'color': '#6c757d'}
            }]
        }
    }


def safe_execute(func: Callable, *args, default_return=None, error_message: str = "Operation failed", **kwargs):
    """
    Safely execute a function with error handling.
    
    Args:
        func: Function to execute
        *args: Function arguments
        default_return: Value to return if function fails
        error_message: Error message to log
        **kwargs: Function keyword arguments
        
    Returns:
        Function result or default_return if error occurs
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.error(f"{error_message}: {e}")
        logger.error(traceback.format_exc())
        return default_return


def validate_dataframe_safe(df: pd.DataFrame, name: str = "DataFrame") -> bool:
    """
    Safely validate a DataFrame.
    
    Args:
        df: DataFrame to validate
        name: Name for logging
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        if not isinstance(df, pd.DataFrame):
            logger.warning(f"{name} is not a DataFrame")
            return False
        
        if df.empty:
            logger.warning(f"{name} is empty")
            return False
        
        return True
    except Exception as e:
        logger.error(f"Error validating {name}: {e}")
        return False


def handle_callback_error(error: Exception, callback_name: str) -> tuple:
    """
    Handle callback errors and return appropriate fallback values.
    
    Args:
        error: Exception that occurred
        callback_name: Name of the callback for logging
        
    Returns:
        tuple: Fallback values for callback outputs
    """
    logger.error(f"Callback error in {callback_name}: {error}")
    logger.error(traceback.format_exc())
    
    # Create error message component
    error_msg = create_error_message(error, f"Callback: {callback_name}")
    
    # Create empty chart
    empty_chart = create_empty_chart("Error", "Unable to generate chart")
    
    # Return fallback values (adjust based on your callback outputs)
    return (
        empty_chart,  # h-avg
        empty_chart,  # h-var
        empty_chart,  # h-range
        empty_chart,  # h-var-range
        empty_chart,  # m-avg
        empty_chart,  # m-var
        empty_chart,  # m-range
        empty_chart,  # m-var-range
        error_msg,    # summary-box
        html.Div("Error occurred"),  # hod-lod-kpi-cards
        empty_chart,  # hod-survival
        empty_chart,  # lod-survival
        empty_chart,  # hod-heatmap
        empty_chart,  # lod-heatmap
        empty_chart,  # hod-rolling
        empty_chart,  # lod-rolling
        "0 cases",    # total-cases-display
        {'display': 'none'},  # hourly-container
        {'display': 'none'},  # minute-container
        {'display': 'none'}   # hod-lod-container
    )


class ErrorHandler:
    """
    Centralized error handler for the application.
    """
    
    def __init__(self):
        self.error_count = 0
        self.error_history = []
    
    def handle_error(self, error: Exception, context: str = None):
        """
        Handle an error and update error tracking.
        
        Args:
            error: Exception that occurred
            context: Context where error occurred
        """
        self.error_count += 1
        error_info = {
            'timestamp': pd.Timestamp.now(),
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context,
            'traceback': traceback.format_exc()
        }
        self.error_history.append(error_info)
        
        logger.error(f"Error #{self.error_count}: {error}")
        if context:
            logger.error(f"Context: {context}")
    
    def get_error_summary(self) -> Dict[str, Any]:
        """
        Get summary of errors that have occurred.
        
        Returns:
            Dict: Error summary information
        """
        if not self.error_history:
            return {'total_errors': 0, 'recent_errors': []}
        
        recent_errors = self.error_history[-5:]  # Last 5 errors
        
        return {
            'total_errors': self.error_count,
            'recent_errors': recent_errors,
            'error_types': list(set(e['error_type'] for e in self.error_history))
        }


# Global error handler instance
error_handler = ErrorHandler()
