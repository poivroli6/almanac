"""
Filter Components for Profile Page

Contains functions for creating filter-related UI components.
"""

from dash import dcc, html
import logging

logger = logging.getLogger(__name__)


def create_filter_controls():
    """
    Create filter control components.
    
    Returns:
        html.Div: Dash component containing filter controls
    """
    return html.Div([
        html.Label("Filters:", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
        dcc.Checklist(
            id='filters',
            options=[
                {'label': 'High Volume Days', 'value': 'high_volume'},
                {'label': 'Low Volume Days', 'value': 'low_volume'},
                {'label': 'Gap Up Days', 'value': 'gap_up'},
                {'label': 'Gap Down Days', 'value': 'gap_down'},
                {'label': 'Time A > Time B', 'value': 'timeA_gt_timeB'},
                {'label': 'Time A < Time B', 'value': 'timeA_lt_timeB'},
            ],
            value=[],
            style={'marginBottom': '15px'}
        )
    ])


def create_threshold_controls():
    """
    Create threshold control components.
    
    Returns:
        html.Div: Dash component containing threshold controls
    """
    return html.Div([
        html.Label("Volume Threshold (%):", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
        dcc.Input(
            id='vol-threshold',
            type='number',
            value=150,
            min=0,
            max=1000,
            step=10,
            style={'width': '100%', 'marginBottom': '15px'}
        ),
        html.Label("Price Change Threshold (%):", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
        dcc.Input(
            id='pct-threshold',
            type='number',
            value=0.5,
            min=0,
            max=10,
            step=0.1,
            style={'width': '100%', 'marginBottom': '15px'}
        )
    ])


def create_product_dropdown():
    """
    Create product selection dropdown.
    
    Returns:
        dcc.Dropdown: Dash component for product selection
    """
    return dcc.Dropdown(
        id='product-dropdown',
        options=[
            {'label': 'ES (E-mini S&P 500)', 'value': 'ES'},
            {'label': 'NQ (E-mini NASDAQ)', 'value': 'NQ'},
            {'label': 'YM (E-mini Dow)', 'value': 'YM'},
            {'label': 'RTY (E-mini Russell)', 'value': 'RTY'},
            {'label': 'CL (Crude Oil)', 'value': 'CL'},
            {'label': 'GC (Gold)', 'value': 'GC'},
            {'label': 'SI (Silver)', 'value': 'SI'},
            {'label': 'NG (Natural Gas)', 'value': 'NG'},
            {'label': 'ZB (30-Year Bond)', 'value': 'ZB'},
            {'label': 'ZN (10-Year Note)', 'value': 'ZN'},
            {'label': 'ZF (5-Year Note)', 'value': 'ZF'},
            {'label': 'ZT (2-Year Note)', 'value': 'ZT'},
            {'label': 'EUR/USD', 'value': 'EURUSD'},
            {'label': 'GBP/USD', 'value': 'GBPUSD'},
            {'label': 'USD/JPY', 'value': 'USDJPY'},
            {'label': 'AUD/USD', 'value': 'AUDUSD'},
            {'label': 'USD/CAD', 'value': 'USDCAD'},
            {'label': 'NZD/USD', 'value': 'NZDUSD'},
            {'label': 'USD/CHF', 'value': 'USDCHF'},
            {'label': 'TSLA (Tesla Stock)', 'value': 'TSLA'},
            {'label': 'BTC/USD (Bitcoin)', 'value': 'BTCUSD'},
        ],
        value='ES',
        clearable=False,
        style={'marginBottom': '15px'}
    )


def create_date_range_controls():
    """
    Create date range control components.
    
    Returns:
        html.Div: Dash component containing date range controls
    """
    return html.Div([
        html.Label("Date Range:", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
        html.Div([
            dcc.DatePickerSingle(
                id='filter-start-date',
                placeholder="Start Date",
                style={'marginRight': '10px', 'width': '45%'}
            ),
            dcc.DatePickerSingle(
                id='filter-end-date',
                placeholder="End Date",
                style={'width': '45%'}
            )
        ], style={'display': 'flex', 'marginBottom': '10px'}),
        html.Button(
            "Max Range",
            id='max-date-range-btn',
            style={
                'width': '100%',
                'padding': '5px',
                'backgroundColor': '#007bff',
                'color': 'white',
                'border': 'none',
                'borderRadius': '3px',
                'cursor': 'pointer'
            }
        )
    ], style={'marginBottom': '20px'})


def create_calculate_button():
    """
    Create the main calculate button with progress bar.
    
    Returns:
        html.Div: Dash component containing the calculate button and progress bar
    """
    return html.Div([
        html.Button(
            "Calculate",
            id='calc-btn',
            style={
                'width': '100%',
                'padding': '10px',
                'backgroundColor': '#28a745',
                'color': 'white',
                'border': 'none',
                'borderRadius': '5px',
                'cursor': 'pointer',
                'fontSize': '16px',
                'fontWeight': 'bold',
                'transition': 'all 0.3s ease'
            }
        ),
        # Progress bar container
        html.Div(
            id='progress-container',
            style={'display': 'none', 'marginTop': '8px'},
            children=[
                # Progress bar background
                html.Div(
                    style={
                        'width': '100%',
                        'height': '4px',
                        'backgroundColor': '#e9ecef',
                        'borderRadius': '2px',
                        'overflow': 'hidden'
                    },
                    children=[
                        # Progress bar fill
                        html.Div(
                            id='progress-bar',
                            style={
                                'width': '0%',
                                'height': '100%',
                                'backgroundColor': '#007bff',
                                'borderRadius': '2px',
                                'transition': 'width 0.3s ease',
                                'background': 'linear-gradient(90deg, #007bff 0%, #0056b3 100%)'
                            }
                        )
                    ]
                ),
                # Progress text
                html.Div(
                    id='progress-text',
                    style={
                        'textAlign': 'center',
                        'marginTop': '4px',
                        'fontSize': '12px',
                        'color': '#666',
                        'fontWeight': '500'
                    },
                    children="Processing..."
                )
            ]
        )
    ])
