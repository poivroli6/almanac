"""
V2 Almanac Futures - Layout Components
Clean, simple layout matching the original design
"""

from dash import dcc, html
from datetime import datetime
import pytz

# Available products (from 1min folder)
PRODUCTS = [
    {'label': 'ES - E-mini S&P 500', 'value': 'ES'},
    {'label': 'NQ - E-mini Nasdaq', 'value': 'NQ'},
    {'label': 'YM - E-mini Dow', 'value': 'YM'},
    {'label': 'GC - Gold', 'value': 'GC'},
    {'label': 'SI - Silver', 'value': 'SI'},
    {'label': 'CL - Crude Oil', 'value': 'CL'},
    {'label': 'NG - Natural Gas', 'value': 'NG'},
    {'label': 'BTCUSD - Bitcoin', 'value': 'BTCUSD'},
    {'label': 'TSLA - Tesla', 'value': 'TSLA'},
    {'label': 'EU - Euro FX', 'value': 'EU'},
    {'label': 'JY - Japanese Yen', 'value': 'JY'},
    {'label': 'AD - Australian Dollar', 'value': 'AD'},
    {'label': 'BP - British Pound', 'value': 'BP'},
    {'label': 'CD - Canadian Dollar', 'value': 'CD'},
    {'label': 'SF - Swiss Franc', 'value': 'SF'},
    {'label': 'HG - Copper', 'value': 'HG'},
    {'label': 'PA - Palladium', 'value': 'PA'},
    {'label': 'PL - Platinum', 'value': 'PL'},
    {'label': 'C - Corn', 'value': 'C'},
    {'label': 'W - Wheat', 'value': 'W'},
    {'label': 'S - Soybeans', 'value': 'S'},
    {'label': 'RP - Rice', 'value': 'RP'},
    {'label': 'TY - 10-Year T-Note', 'value': 'TY'},
    {'label': 'US - 30-Year T-Bond', 'value': 'US'},
    {'label': 'FV - 5-Year T-Note', 'value': 'FV'},
    {'label': 'TU - 2-Year T-Note', 'value': 'TU'},
]

MONTHS = [
    {'label': 'January', 'value': 1},
    {'label': 'February', 'value': 2},
    {'label': 'March', 'value': 3},
    {'label': 'April', 'value': 4},
    {'label': 'May', 'value': 5},
    {'label': 'June', 'value': 6},
    {'label': 'July', 'value': 7},
    {'label': 'August', 'value': 8},
    {'label': 'September', 'value': 9},
    {'label': 'October', 'value': 10},
    {'label': 'November', 'value': 11},
    {'label': 'December', 'value': 12},
]

WEEKDAYS = [
    {'label': '📅 Monday', 'value': 0},
    {'label': '📅 Tuesday', 'value': 1},
    {'label': '📅 Wednesday', 'value': 2},
    {'label': '📅 Thursday', 'value': 3},
    {'label': '📅 Friday', 'value': 4},
]

COMPARISON_OPERATORS = [
    {'label': '< (Less Than)', 'value': 'less_than'},
    {'label': '> (Greater Than)', 'value': 'greater_than'},
    {'label': '≤ (Less Than or Equal)', 'value': 'less_equal'},
    {'label': '≥ (Greater Than or Equal)', 'value': 'greater_equal'},
]


def create_header():
    """Create the header section with current time."""
    est = pytz.timezone('US/Eastern')
    current_time = datetime.now(est).strftime('%H:%M:%S')
    
    return html.Div([
        html.H1([
            html.Span('📊 ', style={'fontSize': '0.9em'}),
            'Almanac Futures'
        ], style={'margin': '0', 'fontSize': '1.5em', 'color': '#2c3e50'}),
        html.Div([
            html.Span('🕒 ', style={'fontSize': '0.9em'}),
            html.Span('Current Time (EST): ', style={'fontWeight': 'bold'}),
            html.Span(current_time, id='current-time')
        ], style={'fontSize': '0.9em', 'color': '#7f8c8d', 'marginTop': '5px'}),
        # Interval for updating time
        dcc.Interval(id='time-interval', interval=1000, n_intervals=0)
    ], style={
        'backgroundColor': '#ecf0f1',
        'padding': '20px',
        'borderRadius': '8px',
        'marginBottom': '20px'
    })


def create_product_section():
    """Create product and time selection section."""
    return html.Div([
        html.H3([
            html.Span('📈 ', style={'fontSize': '0.9em'}),
            'Product & Time of Interest'
        ], style={'fontSize': '1.1em', 'color': '#2c3e50', 'marginBottom': '10px'}),
        
        html.Label('Studied Product', style={'fontWeight': 'bold', 'marginBottom': '5px'}),
        dcc.Dropdown(
            id='product-dropdown',
            options=PRODUCTS,
            value='ES',
            clearable=False,
            style={'marginBottom': '15px'}
        ),
        
        html.Div([
            html.Span('📅 ', style={'fontSize': '0.9em'}),
            html.Span('Date Range Controls', style={'fontWeight': 'bold'})
        ], style={'marginBottom': '10px'}),
        
        html.Button(
            [html.Span('📊 '), 'Max Date Range'],
            id='max-date-range-btn',
            n_clicks=0,
            style={
                'width': '100%',
                'padding': '10px',
                'backgroundColor': '#27ae60',
                'color': 'white',
                'border': 'none',
                'borderRadius': '5px',
                'cursor': 'pointer',
                'fontWeight': 'bold',
                'marginBottom': '10px'
            }
        ),
        
        html.Div([
            html.Div([
                html.Label('Start Date', style={'fontSize': '0.9em', 'marginBottom': '5px'}),
                dcc.DatePickerSingle(
                    id='start-date',
                    date='2010-01-01',
                    display_format='YYYY-MM-DD',
                    style={'width': '100%'}
                )
            ], style={'marginBottom': '10px'}),
            
            html.Div([
                html.Label('End Date', style={'fontSize': '0.9em', 'marginBottom': '5px'}),
                dcc.DatePickerSingle(
                    id='end-date',
                    date='2025-04-08',
                    display_format='YYYY-MM-DD',
                    style={'width': '100%'}
                )
            ])
        ])
    ], style={
        'backgroundColor': '#ecf0f1',
        'padding': '15px',
        'borderRadius': '8px',
        'marginBottom': '20px'
    })


def create_statistical_section():
    """Create statistical visuals configuration section."""
    return html.Div([
        html.H3([
            html.Span('📊 ', style={'fontSize': '0.9em'}),
            'Statistical Visuals'
        ], style={'fontSize': '1.1em', 'color': '#2c3e50', 'marginBottom': '10px'}),
        
        html.Label('Mean Trim %', style={'fontWeight': 'bold', 'marginBottom': '5px'}),
        dcc.Input(
            id='median-percent',
            type='number',
            value=5,
            min=0,
            max=100,
            style={'width': '100%', 'padding': '8px', 'marginBottom': '10px'}
        ),
        html.Div('Percentage to trim from extremes for trimmed mean calculations (0-50%)', 
                 style={'fontSize': '0.8em', 'color': '#7f8c8d', 'marginBottom': '15px'}),
        
        html.Label('Display Measures', style={'fontWeight': 'bold', 'marginBottom': '10px'}),
        dcc.Checklist(
            id='display-measures',
            options=[
                {'label': ' Trimmed Mean', 'value': 'trimmed_mean'},
                {'label': ' Mean', 'value': 'mean'},
                {'label': ' Median', 'value': 'median'},
                {'label': ' Mode', 'value': 'mode'}
            ],
            value=['trimmed_mean', 'mean', 'median', 'mode'],
            style={'marginBottom': '10px'}
        )
    ], style={
        'backgroundColor': '#ecf0f1',
        'padding': '15px',
        'borderRadius': '8px',
        'marginBottom': '20px'
    })


def create_filters_section():
    """Create filters and conditions section."""
    return html.Div([
        html.H3([
            html.Span('🔍 ', style={'fontSize': '0.9em'}),
            'Filters & Conditions'
        ], style={'fontSize': '1.1em', 'color': '#2c3e50', 'marginBottom': '15px'}),
        
        html.Div([
            html.Label('📅 Day of Interest', style={'fontWeight': 'bold', 'marginBottom': '5px'}),
            dcc.Dropdown(
                id='day-of-interest',
                options=[{'label': 'Same Day', 'value': 'same_day'}] + 
                        [{'label': f'T+{i}', 'value': f't+{i}'} for i in range(1, 6)],
                value='same_day',
                clearable=False,
                style={'marginBottom': '10px'}
            ),
            dcc.Checklist(
                id='focus-trading-day',
                options=[{'label': ' Focus analysis on a specific trading day', 'value': 'focus'}],
                value=[],
                style={'fontSize': '0.9em', 'marginBottom': '15px'}
            )
        ]),
        
        html.Div([
            html.Label('🎯 Filter Presets', style={'fontWeight': 'bold', 'marginBottom': '5px'}),
            dcc.Dropdown(
                id='filter-presets',
                options=[
                    {'label': 'None', 'value': 'none'},
                    {'label': 'Preset 1', 'value': 'preset1'},
                    {'label': 'Preset 2', 'value': 'preset2'},
                ],
                value='none',
                placeholder='Select a preset...',
                clearable=True
            )
        ])
    ], style={
        'backgroundColor': '#ecf0f1',
        'padding': '15px',
        'borderRadius': '8px',
        'marginBottom': '20px'
    })


def create_yearly_section():
    """Create yearly analysis section."""
    return html.Div([
        html.H3([
            html.Span('📅 ', style={'fontSize': '0.9em'}),
            'YEARLY ANALYSIS'
        ], style={'fontSize': '1.1em', 'color': '#2c3e50', 'marginBottom': '5px'}),
        html.Div('💡 Analyze seasonal patterns and yearly trends',
                 style={'fontSize': '0.85em', 'color': '#7f8c8d', 'marginBottom': '15px'}),
        
        html.Div([
            html.Label('📅 Month-Year Range', style={'fontWeight': 'bold', 'marginBottom': '5px'}),
            html.Div('💡 Select the month/year range for yearly analysis',
                     style={'fontSize': '0.8em', 'color': '#7f8c8d', 'marginBottom': '10px'}),
            
            html.Div([
                html.Div([
                    html.Label('From', style={'fontSize': '0.9em', 'marginBottom': '5px'}),
                    dcc.Dropdown(
                        id='yearly-from-month',
                        options=MONTHS,
                        value=1,
                        clearable=False,
                        style={'marginBottom': '5px'}
                    ),
                    dcc.Dropdown(
                        id='yearly-from-year',
                        options=[{'label': str(y), 'value': y} for y in range(2010, 2026)],
                        value=2025,
                        clearable=False
                    )
                ], style={'marginBottom': '10px'}),
                
                html.Div([
                    html.Label('To', style={'fontSize': '0.9em', 'marginBottom': '5px'}),
                    dcc.Dropdown(
                        id='yearly-to-month',
                        options=MONTHS,
                        value=12,
                        clearable=False,
                        style={'marginBottom': '5px'}
                    ),
                    dcc.Dropdown(
                        id='yearly-to-year',
                        options=[{'label': str(y), 'value': y} for y in range(2010, 2026)],
                        value=2025,
                        clearable=False
                    )
                ])
            ])
        ], style={'marginBottom': '10px'}),
        
        html.Button(
            [html.Span('📊 '), 'All Available Range'],
            id='yearly-all-range-btn',
            n_clicks=0,
            style={
                'width': '100%',
                'padding': '10px',
                'backgroundColor': '#27ae60',
                'color': 'white',
                'border': 'none',
                'borderRadius': '5px',
                'cursor': 'pointer',
                'fontWeight': 'bold',
                'marginBottom': '10px'
            }
        ),
        
        html.Button(
            [html.Span('📅 '), 'Calculate Yearly'],
            id='calculate-yearly-btn',
            n_clicks=0,
            style={
                'width': '100%',
                'padding': '12px',
                'backgroundColor': '#9b59b6',
                'color': 'white',
                'border': 'none',
                'borderRadius': '5px',
                'cursor': 'pointer',
                'fontWeight': 'bold',
                'fontSize': '1.1em'
            }
        )
    ], style={
        'backgroundColor': '#ecf0f1',
        'padding': '15px',
        'borderRadius': '8px',
        'marginBottom': '20px'
    })


def create_weekly_section():
    """Create weekly analysis section."""
    return html.Div([
        html.H3([
            html.Span('📊 ', style={'fontSize': '0.9em'}),
            'WEEKLY ANALYSIS'
        ], style={'fontSize': '1.1em', 'color': '#2c3e50', 'marginBottom': '5px'}),
        html.Div('💡 Analyze week-to-week performance patterns',
                 style={'fontSize': '0.85em', 'color': '#7f8c8d', 'marginBottom': '15px'}),
        
        html.Div([
            html.Label('📅 Month-Year Range', style={'fontWeight': 'bold', 'marginBottom': '5px'}),
            html.Div('💡 Select the month/year range for weekly analysis',
                     style={'fontSize': '0.8em', 'color': '#7f8c8d', 'marginBottom': '10px'}),
            
            html.Div([
                html.Div([
                    html.Label('From', style={'fontSize': '0.9em', 'marginBottom': '5px'}),
                    dcc.Dropdown(
                        id='weekly-from-month',
                        options=MONTHS,
                        value=1,
                        clearable=False,
                        style={'marginBottom': '5px'}
                    ),
                    dcc.Dropdown(
                        id='weekly-from-year',
                        options=[{'label': str(y), 'value': y} for y in range(2010, 2026)],
                        value=2025,
                        clearable=False
                    )
                ], style={'marginBottom': '10px'}),
                
                html.Div([
                    html.Label('To', style={'fontSize': '0.9em', 'marginBottom': '5px'}),
                    dcc.Dropdown(
                        id='weekly-to-month',
                        options=MONTHS,
                        value=12,
                        clearable=False,
                        style={'marginBottom': '5px'}
                    ),
                    dcc.Dropdown(
                        id='weekly-to-year',
                        options=[{'label': str(y), 'value': y} for y in range(2010, 2026)],
                        value=2025,
                        clearable=False
                    )
                ])
            ])
        ], style={'marginBottom': '10px'}),
        
        html.Button(
            [html.Span('📊 '), 'All Available Range'],
            id='weekly-all-range-btn',
            n_clicks=0,
            style={
                'width': '100%',
                'padding': '10px',
                'backgroundColor': '#27ae60',
                'color': 'white',
                'border': 'none',
                'borderRadius': '5px',
                'cursor': 'pointer',
                'fontWeight': 'bold',
                'marginBottom': '10px'
            }
        ),
        
        html.Button(
            [html.Span('📊 '), 'Calculate Weekly'],
            id='calculate-weekly-btn',
            n_clicks=0,
            style={
                'width': '100%',
                'padding': '12px',
                'backgroundColor': '#17a2b8',
                'color': 'white',
                'border': 'none',
                'borderRadius': '5px',
                'cursor': 'pointer',
                'fontWeight': 'bold',
                'fontSize': '1.1em'
            }
        )
    ], style={
        'backgroundColor': '#ecf0f1',
        'padding': '15px',
        'borderRadius': '8px',
        'marginBottom': '20px'
    })


def create_daily_section():
    """Create daily analysis section."""
    return html.Div([
        html.H3([
            html.Span('📅 ', style={'fontSize': '0.9em'}),
            'DAILY ANALYSIS'
        ], style={'fontSize': '1.1em', 'color': '#2c3e50', 'marginBottom': '5px'}),
        html.Div('💡 Examine hourly statistics and OPEN-LONG',
                 style={'fontSize': '0.85em', 'color': '#7f8c8d', 'marginBottom': '15px'}),
        
        html.Div([
            html.Label('📅 Weekday Filters (applies to T-0)', 
                       style={'fontWeight': 'bold', 'marginBottom': '5px'}),
            html.Div('💡 Filter by day of the week for the current trading day',
                     style={'fontSize': '0.8em', 'color': '#7f8c8d', 'marginBottom': '10px'}),
            
            dcc.Checklist(
                id='weekday-filters',
                options=WEEKDAYS,
                value=[],
                style={'marginBottom': '10px'}
            ),
            
            html.Button(
                'Apply Day Restriction',
                id='apply-day-restriction-btn',
                n_clicks=0,
                style={
                    'width': '100%',
                    'padding': '10px',
                    'backgroundColor': '#3498db',
                    'color': 'white',
                    'border': 'none',
                    'borderRadius': '5px',
                    'cursor': 'pointer',
                    'fontWeight': 'bold',
                    'marginBottom': '10px'
                }
            )
        ], style={'marginBottom': '10px'}),
        
        html.Button(
            [html.Span('📅 '), 'Calculate Daily'],
            id='calculate-daily-btn',
            n_clicks=0,
            style={
                'width': '100%',
                'padding': '12px',
                'backgroundColor': '#007bff',
                'color': 'white',
                'border': 'none',
                'borderRadius': '5px',
                'cursor': 'pointer',
                'fontWeight': 'bold',
                'fontSize': '1.1em'
            }
        )
    ], style={
        'backgroundColor': '#ecf0f1',
        'padding': '15px',
        'borderRadius': '8px',
        'marginBottom': '20px'
    })


def create_hourly_section():
    """Create hourly analysis section."""
    return html.Div([
        html.H3([
            html.Span('🕐 ', style={'fontSize': '0.9em'}),
            'HOURLY ANALYSIS'
        ], style={'fontSize': '1.1em', 'color': '#2c3e50', 'marginBottom': '5px'}),
        html.Div('💡 Analyze minute-level statistics for specific hour',
                 style={'fontSize': '0.85em', 'color': '#7f8c8d', 'marginBottom': '15px'}),
        
        html.Div([
            html.Label('🕒 Minute Hour', style={'fontWeight': 'bold', 'marginBottom': '5px'}),
            html.Div('💡 Select the hour to analyze for minute-level statistics',
                     style={'fontSize': '0.8em', 'color': '#7f8c8d', 'marginBottom': '10px'}),
            
            dcc.Dropdown(
                id='minute-hour',
                options=[{'label': f'{h:02d}:00', 'value': h} for h in range(24)],
                value=20,
                clearable=False,
                style={'marginBottom': '10px'}
            )
        ]),
        
        html.Button(
            [html.Span('🕐 '), 'Calculate an Hour'],
            id='calculate-hourly-btn',
            n_clicks=0,
            style={
                'width': '100%',
                'padding': '12px',
                'backgroundColor': '#28a745',
                'color': 'white',
                'border': 'none',
                'borderRadius': '5px',
                'cursor': 'pointer',
                'fontWeight': 'bold',
                'fontSize': '1.1em'
            }
        )
    ], style={
        'backgroundColor': '#ecf0f1',
        'padding': '15px',
        'borderRadius': '8px',
        'marginBottom': '20px'
    })


def create_scenarios_section():
    """Create active scenarios display."""
    return html.Div([
        html.H3([
            html.Span('📊 ', style={'fontSize': '0.9em'}),
            'Active Scenarios'
        ], style={'fontSize': '1.1em', 'color': '#2c3e50', 'marginBottom': '10px'}),
        
        html.Div([
            html.Span('📊 ', style={'fontSize': '0.9em'}),
            html.Span('All Instances', style={'fontWeight': 'bold'}),
            html.Span(' 3520 cases', style={'color': '#7f8c8d', 'marginLeft': '10px'})
        ])
    ], style={
        'backgroundColor': '#ecf0f1',
        'padding': '15px',
        'borderRadius': '8px',
        'marginBottom': '20px'
    })


def create_presets_section():
    """Create save/load presets section."""
    return html.Div([
        html.H3([
            html.Span('💾 ', style={'fontSize': '0.9em'}),
            'Save/Load Presets'
        ], style={'fontSize': '1.1em', 'color': '#2c3e50', 'marginBottom': '10px'}),
        
        dcc.Input(
            id='preset-name-input',
            type='text',
            placeholder='Enter preset name...',
            style={
                'width': '100%',
                'padding': '8px',
                'marginBottom': '10px',
                'border': '1px solid #bdc3c7',
                'borderRadius': '5px'
            }
        ),
        
        html.Button(
            [html.Span('💾 '), 'Save'],
            id='save-preset-btn',
            n_clicks=0,
            style={
                'width': '100%',
                'padding': '10px',
                'backgroundColor': '#27ae60',
                'color': 'white',
                'border': 'none',
                'borderRadius': '5px',
                'cursor': 'pointer',
                'fontWeight': 'bold'
            }
        )
    ], style={
        'backgroundColor': '#ecf0f1',
        'padding': '15px',
        'borderRadius': '8px',
        'marginBottom': '20px'
    })


def create_price_comparison_section():
    """Create price comparison builder."""
    return html.Div([
        html.H3([
            html.Span('🔧 ', style={'fontSize': '0.9em'}),
            'Price Comparison Builder'
        ], style={'fontSize': '1.1em', 'color': '#2c3e50', 'marginBottom': '5px'}),
        html.Div('💡 Compare price values across different days and times',
                 style={'fontSize': '0.85em', 'color': '#7f8c8d', 'marginBottom': '15px'}),
        
        # Left Side
        html.Div([
            html.Label('Left Side', style={'fontWeight': 'bold', 'marginBottom': '10px'}),
            html.Div([
                html.Button('Hig', id='price-left-hig-btn', n_clicks=0, 
                           style={'padding': '8px 15px', 'marginRight': '5px', 'marginBottom': '5px',
                                  'backgroundColor': '#ecf0f1', 'border': '1px solid #bdc3c7',
                                  'borderRadius': '5px', 'cursor': 'pointer'}),
                html.Button('T-1', id='price-left-t1-btn', n_clicks=0,
                           style={'padding': '8px 15px', 'marginBottom': '5px',
                                  'backgroundColor': '#ecf0f1', 'border': '1px solid #bdc3c7',
                                  'borderRadius': '5px', 'cursor': 'pointer'})
            ], style={'marginBottom': '10px'})
        ]),
        
        # Operator
        html.Div([
            html.Label('Operator', style={'fontWeight': 'bold', 'marginBottom': '5px'}),
            dcc.Dropdown(
                id='price-operator',
                options=COMPARISON_OPERATORS,
                value='less_than',
                clearable=False,
                style={'marginBottom': '10px'}
            )
        ]),
        
        # Threshold
        html.Div([
            html.Label('Threshold (%)', style={'fontWeight': 'bold', 'marginBottom': '5px'}),
            dcc.Input(
                id='price-threshold',
                type='number',
                value=2,
                min=0,
                style={'width': '100%', 'padding': '8px', 'marginBottom': '10px'}
            )
        ]),
        
        # Right Side
        html.Div([
            html.Label('Right Side', style={'fontWeight': 'bold', 'marginBottom': '10px'}),
            html.Div([
                html.Button('Op', id='price-right-op-btn', n_clicks=0,
                           style={'padding': '8px 15px', 'marginRight': '5px', 'marginBottom': '5px',
                                  'backgroundColor': '#ecf0f1', 'border': '1px solid #bdc3c7',
                                  'borderRadius': '5px', 'cursor': 'pointer'}),
                html.Button('T-3', id='price-right-t3-btn', n_clicks=0,
                           style={'padding': '8px 15px', 'marginBottom': '5px',
                                  'backgroundColor': '#ecf0f1', 'border': '1px solid #bdc3c7',
                                  'borderRadius': '5px', 'cursor': 'pointer'})
            ])
        ]),
        
        html.Button(
            [html.Span('✓ '), 'Apply Comparison'],
            id='apply-price-comparison-btn',
            n_clicks=0,
            style={
                'width': '100%',
                'padding': '12px',
                'backgroundColor': '#27ae60',
                'color': 'white',
                'border': 'none',
                'borderRadius': '5px',
                'cursor': 'pointer',
                'fontWeight': 'bold',
                'fontSize': '1.05em',
                'marginTop': '10px'
            }
        )
    ], style={
        'backgroundColor': '#e8f5e9',
        'padding': '15px',
        'borderRadius': '8px',
        'marginBottom': '20px'
    })


def create_volume_comparison_section():
    """Create volume comparison builder."""
    return html.Div([
        html.H3([
            html.Span('📊 ', style={'fontSize': '0.9em'}),
            'Volume Comparison Builder'
        ], style={'fontSize': '1.1em', 'color': '#2c3e50', 'marginBottom': '5px'}),
        html.Div('💡 Compare volume metrics across different sessions and time periods',
                 style={'fontSize': '0.85em', 'color': '#7f8c8d', 'marginBottom': '15px'}),
        
        # Left Side
        html.Div([
            html.Label('Left Side', style={'fontWeight': 'bold', 'marginBottom': '10px'}),
            html.Div([
                html.Button('Ses', id='volume-left-ses-btn', n_clicks=0,
                           style={'padding': '8px 15px', 'marginRight': '5px', 'marginBottom': '5px',
                                  'backgroundColor': '#ecf0f1', 'border': '1px solid #bdc3c7',
                                  'borderRadius': '5px', 'cursor': 'pointer'}),
                html.Button('T-1', id='volume-left-t1-btn', n_clicks=0,
                           style={'padding': '8px 15px', 'marginBottom': '5px',
                                  'backgroundColor': '#ecf0f1', 'border': '1px solid #bdc3c7',
                                  'borderRadius': '5px', 'cursor': 'pointer'})
            ], style={'marginBottom': '10px'})
        ]),
        
        # Operator
        html.Div([
            html.Label('Operator', style={'fontWeight': 'bold', 'marginBottom': '5px'}),
            dcc.Dropdown(
                id='volume-operator',
                options=COMPARISON_OPERATORS,
                value='less_than',
                clearable=False,
                style={'marginBottom': '10px'}
            )
        ]),
        
        # Right Side
        html.Div([
            html.Label('Right Side', style={'fontWeight': 'bold', 'marginBottom': '10px'}),
            html.Div([
                html.Button('Ses', id='volume-right-ses-btn', n_clicks=0,
                           style={'padding': '8px 15px', 'marginRight': '5px', 'marginBottom': '5px',
                                  'backgroundColor': '#ecf0f1', 'border': '1px solid #bdc3c7',
                                  'borderRadius': '5px', 'cursor': 'pointer'}),
                html.Button('T-2', id='volume-right-t2-btn', n_clicks=0,
                           style={'padding': '8px 15px', 'marginBottom': '5px',
                                  'backgroundColor': '#ecf0f1', 'border': '1px solid #bdc3c7',
                                  'borderRadius': '5px', 'cursor': 'pointer'})
            ])
        ]),
        
        # Threshold
        html.Div([
            html.Label('Threshold (%)', style={'fontWeight': 'bold', 'marginBottom': '5px'}),
            dcc.Input(
                id='volume-threshold',
                type='number',
                value=10,
                min=0,
                style={'width': '100%', 'padding': '8px', 'marginBottom': '10px'}
            )
        ]),
        
        html.Button(
            [html.Span('✓ '), 'Apply Volume Comparison'],
            id='apply-volume-comparison-btn',
            n_clicks=0,
            style={
                'width': '100%',
                'padding': '12px',
                'backgroundColor': '#27ae60',
                'color': 'white',
                'border': 'none',
                'borderRadius': '5px',
                'cursor': 'pointer',
                'fontWeight': 'bold',
                'fontSize': '1.05em',
                'marginTop': '10px'
            }
        )
    ], style={
        'backgroundColor': '#fff8e1',
        'padding': '15px',
        'borderRadius': '8px',
        'marginBottom': '20px'
    })


def create_export_section():
    """Create export & share section."""
    return html.Div([
        html.H3([
            html.Span('📤 ', style={'fontSize': '0.9em'}),
            'Export & Share'
        ], style={'fontSize': '1.1em', 'color': '#2c3e50', 'marginBottom': '10px'}),
        
        html.Button(
            [html.Span('🔗 '), 'Share URL'],
            id='share-url-btn',
            n_clicks=0,
            style={
                'width': '100%',
                'padding': '12px',
                'backgroundColor': '#27ae60',
                'color': 'white',
                'border': 'none',
                'borderRadius': '5px',
                'cursor': 'pointer',
                'fontWeight': 'bold',
                'marginBottom': '10px'
            }
        ),
        
        html.Button(
            [html.Span('📥 '), 'Download All CSV'],
            id='download-csv-btn',
            n_clicks=0,
            style={
                'width': '100%',
                'padding': '12px',
                'backgroundColor': '#6c757d',
                'color': 'white',
                'border': 'none',
                'borderRadius': '5px',
                'cursor': 'pointer',
                'fontWeight': 'bold',
                'marginBottom': '10px'
            }
        ),
        
        html.Div('💡 Tip: Use the camera icon on charts to download individual images',
                 style={'fontSize': '0.8em', 'color': '#7f8c8d', 'fontStyle': 'italic'})
    ], style={
        'backgroundColor': '#ecf0f1',
        'padding': '15px',
        'borderRadius': '8px',
        'marginBottom': '20px'
    })


def create_sidebar():
    """Create the left sidebar with all controls."""
    return html.Div([
        create_header(),
        create_product_section(),
        create_statistical_section(),
        create_filters_section(),
        create_yearly_section(),
        create_weekly_section(),
        create_daily_section(),
        create_hourly_section(),
        create_scenarios_section(),
        create_presets_section(),
        create_price_comparison_section(),
        create_volume_comparison_section(),
        create_export_section()
    ], style={
        'width': '300px',
        'height': '100vh',
        'overflowY': 'auto',
        'padding': '20px',
        'backgroundColor': '#f8f9fa',
        'borderRight': '2px solid #dee2e6'
    })


def create_main_content():
    """Create the main content area (right side)."""
    return html.Div([
        html.Div([
            html.H2('📊 Analysis Results', style={'color': '#2c3e50', 'marginBottom': '20px'}),
            html.Div(
                'Select a product and calculation type to view results here.',
                id='main-content-placeholder',
                style={
                    'padding': '40px',
                    'textAlign': 'center',
                    'color': '#7f8c8d',
                    'fontSize': '1.1em',
                    'backgroundColor': '#ecf0f1',
                    'borderRadius': '8px'
                }
            )
        ], style={'padding': '30px'})
    ], style={
        'flex': '1',
        'height': '100vh',
        'overflowY': 'auto',
        'backgroundColor': '#ffffff'
    })


def create_layout():
    """Create the complete application layout."""
    return html.Div([
        # Main container with flexbox layout
        html.Div([
            create_sidebar(),
            create_main_content()
        ], style={
            'display': 'flex',
            'height': '100vh',
            'overflow': 'hidden'
        })
    ])

