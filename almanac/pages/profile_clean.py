"""
Profile Page - Clean Version

Main analysis page showing hourly/minute statistics with filtering capabilities.
"""

from dash import dcc, html, Input, Output, State
import dash.dependencies
import pandas as pd
import math

from ..data_sources import load_minute_data, load_daily_data
from ..features import (
    compute_hourly_stats,
    compute_minute_stats,
    apply_filters,
    apply_time_filters,
    apply_quick_filter,
    apply_custom_filter,
    combine_filters,
    get_filtered_minute_data,
    calculate_sample_stats,
    calculate_individual_filter_stats,
    create_filter_description,
    validate_filter_config,
)
from ..features.hod_lod import (
    detect_hod_lod,
    compute_survival_curves,
    compute_hod_lod_heatmap,
    compute_rolling_median_time,
    compute_trend_test,
)
from ..viz import make_line_chart, make_heatmap, make_survival_curve
from ..export import (
    export_figure_to_csv,
    get_png_download_config,
    generate_shareable_url,
    get_current_page_url
)
import base64

# UI Components (Agent 3 additions)
from ..ui.components import (
    create_accordion_section,
    create_preset_controls,
    create_mobile_responsive_styles,
    create_help_modal,
    create_export_button
)
from ..ui.presets import PresetManager
from ..ui.keyboard import (
    create_keyboard_listener,
    register_help_modal_callbacks
)


def create_preset_row(preset_id, preset_name, day_count, logic_operator="AND"):
    """
    Create a dynamic preset row with X button, day count, dates, and AND/OR selector.
    """
    return html.Div([
        html.Div([
            # Left side: Preset name and day count
            html.Div([
                html.Span(f"📊 {preset_name}", style={'fontWeight': 'bold', 'marginRight': '10px'}),
                html.Span(f"({day_count} days)", style={'fontSize': '11px', 'color': '#666', 'marginRight': '10px'}),
            ], style={'flex': '1'}),
            
            # Center: AND/OR selector
            html.Div([
                html.Label("Logic:", style={'fontSize': '10px', 'marginRight': '5px', 'color': '#666'}),
                dcc.Dropdown(
                    id={'type': 'preset-logic', 'index': preset_id},
                    options=[
                        {'label': 'AND', 'value': 'AND'},
                        {'label': 'OR', 'value': 'OR'}
                    ],
                    value=logic_operator,
                    clearable=False,
                    style={'width': '60px', 'fontSize': '10px'},
                    className='preset-logic-dropdown'
                )
            ], style={'marginRight': '10px'}),
            
            # Right side: X button to remove
            html.Button(
                "❌",
                id={'type': 'remove-preset', 'index': preset_id},
                style={
                    'padding': '2px 6px',
                    'fontSize': '10px',
                    'backgroundColor': '#e74c3c',
                    'color': 'white',
                    'border': 'none',
                    'borderRadius': '3px',
                    'cursor': 'pointer',
                    'minWidth': '20px'
                },
                title="Remove this preset"
            )
        ], style={
            'display': 'flex',
            'alignItems': 'center',
            'padding': '8px 12px',
            'backgroundColor': '#e8f4f8',
            'border': '1px solid #3498db',
            'borderRadius': '5px',
            'marginBottom': '8px'
        })
    ], id={'type': 'preset-row', 'index': preset_id})


def create_sidebar_content():
    """Create accordion-based sidebar content with collapsible sections."""
    
    # Enhanced filter options with better organization and descriptions
    filter_options = [
        # Previous Day Performance
        {'label': '📈 Prev-Day: Close > Open (Bullish)', 'value': 'prev_pos'},
        {'label': '📉 Prev-Day: Close < Open (Bearish)', 'value': 'prev_neg'},
        {'label': '🚀 Prev-Day: %∆ ≥ Threshold (Strong Move Up)', 'value': 'prev_pct_pos'},
        {'label': '💥 Prev-Day: %∆ ≤ -Threshold (Strong Move Down)', 'value': 'prev_pct_neg'},
        
        # Previous Day Range & Volume
        {'label': '📊 Prev-Day: High Relative Volume (≥ Threshold)', 'value': 'relvol_gt'},
        {'label': '📉 Prev-Day: Low Relative Volume (≤ Threshold)', 'value': 'relvol_lt'},
        
        # Time-based Conditions
        {'label': '⏰ Time A > Time B (Custom Time Comparison)', 'value': 'timeA_gt_timeB'},
        {'label': '⏰ Time A < Time B (Custom Time Comparison)', 'value': 'timeA_lt_timeB'},
        
        # Data Quality
        {'label': '✂️ Exclude Top/Bottom 5% (Trim Extremes)', 'value': 'trim_extremes'},
        
        # Weekday Filters
        {'label': '📅 Monday', 'value': 'monday'},
        {'label': '📅 Tuesday', 'value': 'tuesday'},
        {'label': '📅 Wednesday', 'value': 'wednesday'},
        {'label': '📅 Thursday', 'value': 'thursday'},
        {'label': '📅 Friday', 'value': 'friday'},
    ]
    
    # Complete product options list
    product_options = [
        # Equities
        {'label': '─── EQUITIES ───', 'value': '', 'disabled': True},
        {'label': 'ES - E-mini S&P 500', 'value': 'ES'},
        {'label': 'NQ - E-mini Nasdaq', 'value': 'NQ'},
        {'label': 'YM - E-mini Dow', 'value': 'YM'},
        
        # Metals
        {'label': '─── METALS ───', 'value': '', 'disabled': True},
        {'label': 'GC - Gold', 'value': 'GC'},
        {'label': 'SI - Silver', 'value': 'SI'},
        {'label': 'HG - Copper', 'value': 'HG'},
        {'label': 'PA - Palladium', 'value': 'PA'},
        {'label': 'PL - Platinum', 'value': 'PL'},
        
        # Energies
        {'label': '─── ENERGIES ───', 'value': '', 'disabled': True},
        {'label': 'CL - Crude Oil', 'value': 'CL'},
        {'label': 'NG - Natural Gas', 'value': 'NG'},
        {'label': 'RP - Refined Products', 'value': 'RP'},
        
        # Currencies
        {'label': '─── CURRENCIES ───', 'value': '', 'disabled': True},
        {'label': 'EU - Euro FX', 'value': 'EU'},
        {'label': 'JY - Japanese Yen', 'value': 'JY'},
        {'label': 'BP - British Pound', 'value': 'BP'},
        {'label': 'CD - Canadian Dollar', 'value': 'CD'},
        {'label': 'AD - Australian Dollar', 'value': 'AD'},
        {'label': 'SF - Swiss Franc', 'value': 'SF'},
        
        # Treasuries
        {'label': '─── TREASURIES ───', 'value': '', 'disabled': True},
        {'label': 'TY - 10-Year Treasury', 'value': 'TY'},
        {'label': 'FV - 5-Year Treasury', 'value': 'FV'},
        {'label': 'TU - 2-Year Treasury', 'value': 'TU'},
        {'label': 'US - 30-Year Treasury', 'value': 'US'},
        
        # Agriculturals
        {'label': '─── AGRICULTURALS ───', 'value': '', 'disabled': True},
        {'label': 'C - Corn', 'value': 'C'},
        {'label': 'S - Soybeans', 'value': 'S'},
        {'label': 'W - Wheat', 'value': 'W'},
    ]
    
    sidebar_content = [
        html.H2("📊 Almanac Futures", style={'marginBottom': '20px', 'fontSize': '20px'}),
        
        # Product & Time of Interest Section
        create_accordion_section(
            'product-time-section',
            'Product & Time of Interest',
            [
                html.Label("Studied Product", style={'fontWeight': 'bold'}),
                dcc.Dropdown(
                    id='product-dropdown',
                    options=product_options,
                    value='ES',
                    clearable=False,
                    style={'marginBottom': '20px'}
                ),
                
                html.Label("Minute Hour", style={'fontWeight': 'bold'}),
                dcc.Dropdown(
                    id='minute-hour',
                    options=[{'label': f'{h}:00', 'value': h} for h in range(0, 24) if h not in (5, 6)],
                    value=9,
                    clearable=False,
                    style={'marginBottom': '20px'}
                )
            ],
            is_open=True,
            icon='📈'
        ),
        
        # Statistical Visuals Section
        create_accordion_section(
            'statistical-section',
            'Statistical Visuals',
            [
                html.Label("Median %", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                dcc.Input(
                    id='median-percentage',
                    type='number',
                    value=5.0,
                    min=0,
                    max=50,
                    step=0.1,
                    style={'width': '100%', 'marginBottom': '15px'},
                    placeholder='Enter percentage (0-50%)'
                ),
                html.Small("Percentage for median calculations (0-50%)", style={'color': '#666', 'fontSize': '11px', 'display': 'block', 'marginBottom': '15px'}),
                
                html.Label("Display Measures", style={'fontWeight': 'bold', 'marginBottom': '10px'}),
                dcc.Checklist(
                    id='stat-measures',
                    options=[
                        {'label': 'Mean', 'value': 'mean'},
                        {'label': 'Trimmed Mean', 'value': 'trimmed_mean'},
                        {'label': 'Median', 'value': 'median'},
                        {'label': 'Mode', 'value': 'mode'}
                    ],
                    value=['mean', 'trimmed_mean', 'median', 'mode'],
                    style={'marginBottom': '20px'}
                ),
            ],
            is_open=True,
            icon='📊'
        ),
        
        # Filters Section
        create_accordion_section(
            'filters-section',
            'Filters & Conditions',
            [
                html.Div(id='sample-size-display', style={
                    'backgroundColor': '#f8f9fa', 
                    'padding': '10px', 
                    'borderRadius': '5px',
                    'marginTop': '15px',
                    'marginBottom': '15px'
                }),
                
                html.Hr(style={'margin': '15px 0'}),
                
                # Filter Presets Section - Redesigned
                html.Div([
                    html.Label("🎯 Filter Presets", style={'fontWeight': 'bold', 'marginBottom': '8px', 'color': '#2c3e50'}),
                     html.Button(
                         "Apply Scenario",
                         id='apply-preset-btn',
                         style={
                             'width': '100%',
                             'padding': '8px',
                             'marginBottom': '8px',
                             'backgroundColor': '#3498db',
                             'color': 'white',
                             'border': 'none',
                             'borderRadius': '4px',
                             'cursor': 'pointer',
                             'fontSize': '12px',
                             'fontWeight': 'bold'
                         }
                     ),
                    dcc.Dropdown(
                        id='filter-presets-dropdown',
                        placeholder="Select a preset...",
                        value=None,  # Default to None as requested
                        options=[
                            {'label': '📈 Bullish Days (Close > Open)', 'value': 'bullish'},
                            {'label': '📉 Bearish Days (Close < Open)', 'value': 'bearish'},
                            {'label': '🚀 Strong Moves (%∆ ≥ Threshold)', 'value': 'strong_moves'},
                            {'label': '📊 High Volume Days', 'value': 'high_volume'},
                            {'label': '📅 Weekdays Only', 'value': 'weekdays'},
                            {'label': '🔄 All Conditions (No Filters)', 'value': 'all'},
                        ],
                        style={'marginBottom': '15px', 'fontSize': '12px'},
                        clearable=True
                    )
                ]),
                
                # Date Range Controls Section
                html.Label("📅 Date Range Controls", style={'fontWeight': 'bold', 'marginBottom': '10px', 'color': '#2c3e50'}),
                html.Div([
                    html.Button(
                        "📊 Max Date Range",
                        id='max-date-range-btn',
                        style={
                            'width': '100%',
                            'padding': '8px',
                            'marginBottom': '10px',
                            'backgroundColor': '#27ae60',
                            'color': 'white',
                            'border': 'none',
                            'borderRadius': '4px',
                            'cursor': 'pointer',
                            'fontSize': '12px',
                            'fontWeight': 'bold'
                        },
                        title="Set date range to first and last available dates for selected product"
                    )
                ]),
                
                html.Div([
                    html.Div([
                        html.Label("Start Date", style={'fontSize': '11px', 'marginBottom': '5px', 'color': '#666'}),
                        dcc.DatePickerSingle(
                            id='filter-start-date',
                            display_format='YYYY-MM-DD',
                            placeholder='Select start date...',
                            style={'fontSize': '11px'}
                        )
                    ], style={'width': '48%', 'display': 'inline-block', 'marginRight': '4%'}),
                    
                    html.Div([
                        html.Label("End Date", style={'fontSize': '11px', 'marginBottom': '5px', 'color': '#666'}),
                        dcc.DatePickerSingle(
                            id='filter-end-date',
                            display_format='YYYY-MM-DD',
                            placeholder='Select end date...',
                            style={'fontSize': '11px'}
                        )
                    ], style={'width': '48%', 'display': 'inline-block'})
                ], style={'marginBottom': '15px'}),
                
                html.Label("🔍 Custom Filter Options", style={'fontWeight': 'bold', 'marginBottom': '10px', 'color': '#2c3e50'}),
                html.Small("💡 Tip: Select multiple filters to narrow down your analysis", 
                          style={'color': '#666', 'fontSize': '10px', 'marginBottom': '8px', 'display': 'block'}),
                dcc.Checklist(
                    id='filters',
                    options=filter_options,
                    value=[],  # Start with no filters selected - let user choose
                    style={'marginBottom': '15px'},
                    inputStyle={'marginRight': '8px'},
                    labelStyle={'fontSize': '11px', 'lineHeight': '1.3', 'marginBottom': '4px'}
                ),
                
                html.Label("⚙️ Filter Thresholds", style={'fontWeight': 'bold', 'marginBottom': '10px', 'color': '#2c3e50'}),
                
                html.Div([
                    html.Label("📊 Relative Volume Multiplier", style={'fontSize': '11px', 'marginBottom': '2px'}),
                    dcc.Input(
                        id='vol-threshold', 
                        type='number', 
                        placeholder='e.g., 1.5 (50% above average)', 
                        style={'width': '100%', 'marginBottom': '8px', 'fontSize': '11px'},
                        debounce=True
                    )
                ]),
                
                html.Div([
                    html.Label("📈 %∆ Threshold", style={'fontSize': '11px', 'marginBottom': '2px'}),
                    dcc.Input(
                        id='pct-threshold', 
                        type='number', 
                        placeholder='e.g., 1.0 (1% move)', 
                        style={'width': '100%', 'marginBottom': '8px', 'fontSize': '11px'},
                        debounce=True
                    )
                ]),
                
                html.Hr(style={'margin': '15px 0'}),
                
                html.Label("Time A", style={'fontWeight': 'bold'}),
                html.Div([
                    dcc.Dropdown(id='timeA-hour', options=[{'label': h, 'value': h} for h in range(0, 24) if h not in (5, 6)], placeholder='Hour'),
                    dcc.Dropdown(id='timeA-minute', options=[{'label': m, 'value': m} for m in range(0, 60)], placeholder='Min')
                ], style={'display': 'flex', 'gap': '10px', 'marginBottom': '10px'}),
                
                html.Label("Time B", style={'fontWeight': 'bold'}),
                html.Div([
                    dcc.Dropdown(id='timeB-hour', options=[{'label': h, 'value': h} for h in range(0, 24) if h not in (5, 6)], placeholder='Hour'),
                    dcc.Dropdown(id='timeB-minute', options=[{'label': m, 'value': m} for m in range(0, 60)], placeholder='Min')
                ], style={'display': 'flex', 'gap': '10px', 'marginBottom': '10px'})
            ],
            is_open=True,
            icon='🔧'
        ),
        
        # Action Buttons
        html.Hr(style={'margin': '20px 0'}),
        
        html.Button(
            '🚀 Calculate',
            id='calc-btn',
            n_clicks=0,
            title='Run analysis (Ctrl+Enter)',
            style={
                'width': '100%',
                'padding': '12px',
                'fontWeight': 'bold',
                'backgroundColor': '#007bff',
                'color': 'white',
                'border': 'none',
                'borderRadius': '4px',
                'cursor': 'pointer',
                'marginBottom': '10px',
                'fontSize': '14px'
            }
        ),
        
        create_export_button(),
        
        # Summary box
        html.Div(
            id='summary-box',
            style={
                'marginTop': '15px',
                'padding': '12px',
                'border': '1px solid #ccc',
                'borderRadius': '5px',
                'backgroundColor': '#ffffff',
                'fontSize': '13px',
                'lineHeight': '1.5'
            }
        )
    ]
    
    return sidebar_content


def create_profile_layout():
    """Create the main profile page layout with accordion-based sidebar."""
    
    layout = html.Div([
        # Responsive CSS styles
        create_mobile_responsive_styles(),
        
        # Keyboard listener
        create_keyboard_listener(),
        
        # Help modal
        create_help_modal(),
        
        # State storage
        dcc.Store(id='query-spec', storage_type='session'),
        dcc.Store(id='custom-filters-store', data=[], storage_type='session'),
        dcc.Store(id='dynamic-filters-store', data=[], storage_type='session'),
        
        # Left sidebar (controls) - NEW ACCORDION STRUCTURE
        html.Div(
            className='sidebar',
            style={
                'position': 'fixed',
                'width': '20%',
                'height': '100vh',
                'overflow': 'auto',
                'padding': '20px',
                'borderRight': '1px solid #ccc',
                'backgroundColor': '#f8f9fa'
            },
            children=create_sidebar_content()
        ),
        
        # Right content area (charts)
        html.Div(
            className='content-area',
            style={'marginLeft': '22%', 'padding': '20px'},
            children=[
                dcc.Loading(
                    id='loading-graphs',
                    type='default',
                    children=[
                        html.H3("Hourly Statistics"),
                        dcc.Graph(id='h-avg', config=get_png_download_config('hourly_avg_change')),
                        dcc.Graph(id='h-var', config=get_png_download_config('hourly_var_change')),
                        dcc.Graph(id='h-range', config=get_png_download_config('hourly_avg_range')),
                        dcc.Graph(id='h-var-range', config=get_png_download_config('hourly_var_range')),
                        
                        html.H3("Minute Statistics"),
                        dcc.Graph(id='m-avg', config=get_png_download_config('minute_avg_change')),
                        dcc.Graph(id='m-var', config=get_png_download_config('minute_var_change')),
                        dcc.Graph(id='m-range', config=get_png_download_config('minute_avg_range')),
                        dcc.Graph(id='m-var-range', config=get_png_download_config('minute_var_range')),
                        
                        html.Hr(style={'margin': '40px 0'}),
                        
                        html.H3("HOD/LOD Analysis"),
                        html.Div(id='hod-lod-kpi-cards', style={
                            'display': 'grid',
                            'gridTemplateColumns': 'repeat(auto-fit, minmax(200px, 1fr))',
                            'gap': '15px',
                            'marginBottom': '30px'
                        }),
                        
                        html.H4("Survival Curves (Probability HOD/LOD occurred by time T)"),
                        html.Div([
                            html.Div([dcc.Graph(id='hod-survival')], style={'width': '49%', 'display': 'inline-block'}),
                            html.Div([dcc.Graph(id='lod-survival')], style={'width': '49%', 'display': 'inline-block', 'marginLeft': '2%'})
                        ]),
                        
                        html.H4("HOD/LOD Frequency Heatmaps (by Weekday)"),
                        html.Div([
                            html.Div([dcc.Graph(id='hod-heatmap')], style={'width': '49%', 'display': 'inline-block'}),
                            html.Div([dcc.Graph(id='lod-heatmap')], style={'width': '49%', 'display': 'inline-block', 'marginLeft': '2%'})
                        ]),
                        
                        html.H4("Rolling Median Time (63-day window)"),
                        html.Div([
                            html.Div([dcc.Graph(id='hod-rolling')], style={'width': '49%', 'display': 'inline-block'}),
                            html.Div([dcc.Graph(id='lod-rolling')], style={'width': '49%', 'display': 'inline-block', 'marginLeft': '2%'})
                        ]),
                    ]
                )
            ]
        )
    ])
    
    return layout


def register_profile_callbacks(app, cache):
    """Register all callbacks for the profile page."""
    
    # TEMPORARY FIX: Simplified callback to get app working
    @app.callback(
        [
            Output('h-avg', 'figure'),
            Output('h-var', 'figure'),
            Output('h-range', 'figure'),
            Output('h-var-range', 'figure'),
            Output('m-avg', 'figure'),
            Output('m-var', 'figure'),
            Output('m-range', 'figure'),
            Output('m-var-range', 'figure'),
            Output('summary-box', 'children'),
            Output('hod-lod-kpi-cards', 'children'),
            Output('hod-survival', 'figure'),
            Output('lod-survival', 'figure'),
            Output('hod-heatmap', 'figure'),
            Output('lod-heatmap', 'figure'),
            Output('hod-rolling', 'figure'),
            Output('lod-rolling', 'figure'),
        ],
        Input('calc-btn', 'n_clicks'),
        [
            State('product-dropdown', 'value'),
            State('filter-start-date', 'date'),
            State('filter-end-date', 'date'),
            State('minute-hour', 'value'),
            State('filters', 'value'),
            State('vol-threshold', 'value'),
            State('pct-threshold', 'value'),
            State('median-percentage', 'value'),
            State('stat-measures', 'value'),
            State('timeA-hour', 'value'),
            State('timeA-minute', 'value'),
            State('timeB-hour', 'value'),
            State('timeB-minute', 'value'),
        ]
    )
    @cache.memoize(timeout=300)  # Reduced timeout to 5 minutes
    def update_graphs_simple(n, prod, start, end, mh, filters, vol_thr, pct_thr, median_pct, selected_measures, tA_h, tA_m, tB_h, tB_m):
        """Main callback to update all charts and summary."""
        print(f"\n[DEBUG] Callback triggered: n_clicks={n}")
        print(f"[DEBUG] Parameters: prod={prod}, start={start}, end={end}, mh={mh}")
        print(f"[DEBUG] filters={filters}, vol_thr={vol_thr}, pct_thr={pct_thr}")
        print(f"[DEBUG] median_pct={median_pct}, selected_measures={selected_measures}")
        
        # Initialize HOD/LOD variables
        empty_fig = make_line_chart([], [], "No Data", "", "")
        empty_kpi = html.Div("Initializing...")
        hod_survival_fig = lod_survival_fig = empty_fig
        hod_heatmap_fig = lod_heatmap_fig = empty_fig
        hod_rolling_fig = lod_rolling_fig = empty_fig
        
        try:
            debug_msgs = []
            # Try loading from database first
            try:
                daily = load_daily_data(prod, start, end)
                minute = load_minute_data(prod, start, end)
                debug_msgs.append(f"Loaded daily={len(daily)} rows, minute={len(minute)} rows")
                
                # Intermarket data loading disabled in simplified version
                intermarket_daily = None
                        
            except Exception as db_error:
                # Fallback to demo data if database unavailable
                print(f"Database unavailable, using demo data: {db_error}")
                from ..data_sources import generate_demo_daily_data, generate_demo_minute_data
                daily = generate_demo_daily_data(prod, start, end)
                minute = generate_demo_minute_data(prod, start, end)
                intermarket_daily = None
            
            # Check if we have data
            if daily.empty or minute.empty:
                error_msg = html.Div([
                    html.B("Error:", style={'color': 'red'}),
                    html.Br(),
                    f"No data found for {prod} between {start} and {end}"
                ])
                empty_fig = make_line_chart([], [], "No Data", "", "")
                empty_kpi = html.Div("No data available")
                return (empty_fig,) * 8 + (error_msg, empty_kpi) + (empty_fig,) * 6
            
            # Apply filtering
            filtered_minute = minute
            
            # Apply additional filters
            try:
                pre_rows = len(filtered_minute)
                filtered_minute = apply_filters(filtered_minute, daily, filters, vol_thr, pct_thr)
                debug_msgs.append(f"After base filters [{','.join(filters or [])}]: {pre_rows} -> {len(filtered_minute)} rows")
            except Exception as filter_error:
                import traceback
                traceback.print_exc()
                raise
            
            # Apply time filters if specified
            if filters and any(f in filters for f in ['timeA_gt_timeB', 'timeA_lt_timeB']):
                try:
                    before_time = len(filtered_minute)
                    filtered_minute = apply_time_filters(
                        filtered_minute, filters, tA_h, tA_m, tB_h, tB_m
                    )
                    debug_msgs.append(f"After time filters: {before_time} -> {len(filtered_minute)} rows")
                except Exception as time_error:
                    import traceback
                    traceback.print_exc()
                    raise
            
            # Compute statistics (now includes all 4 measures)
            try:
                # Set default values
                trim_pct = median_pct or 5.0
                selected_measures = selected_measures or ['mean', 'trimmed_mean', 'median', 'mode']
                
                # Compute hourly stats with all 4 measures
                hc, hcm, hmed, hmode, hv, hr, hrm, hmed_r, hmode_r, hvr = compute_hourly_stats(filtered_minute, trim_pct)
                
                # Compute minute stats with all 4 measures
                mc, mcm, mmed, mmode, mv, mr, mrm, mmed_r, mmode_r, mvr = compute_minute_stats(filtered_minute, mh, trim_pct)
            except Exception as stats_error:
                import traceback
                traceback.print_exc()
                raise
            
            # Scale variance for display
            sh, _ = _scale_variance(hv.mean())
            sm, _ = _scale_variance(mv.mean())
            
            # Compute HOD/LOD analysis - TEMPORARILY DISABLED FOR DEBUGGING
            print(f"[HOD/LOD] Analysis temporarily disabled for debugging...")
            
            # Use empty figures for HOD/LOD while debugging
            empty_fig = make_line_chart([], [], "HOD/LOD Disabled", "", "")
            empty_kpi = html.Div([
                html.B("HOD/LOD Analysis", style={'marginBottom': '10px'}),
                html.Br(),
                html.Div("Temporarily disabled for debugging", 
                        style={'color': '#666', 'fontSize': '14px'})
            ])
            hod_survival_fig = lod_survival_fig = empty_fig
            hod_heatmap_fig = lod_heatmap_fig = empty_fig
            hod_rolling_fig = lod_rolling_fig = empty_fig
            
            # Generate summary
            summary = _generate_summary(
                daily, filtered_minute, hc, hv, hr, hvr, mc, mv, mr, mvr, sh, sm
            )
            # Append debug information at the bottom of the summary
            if debug_msgs:
                summary = summary + [html.Hr(), html.B("Debug"), html.Br()] + [html.Div(m) for m in debug_msgs]
            
            # Create figures with all 4 statistical measures
            return (
                make_line_chart(hc.index, hc, "Hourly Avg % Change", "Hour", "Pct", 
                              mean_data=hc, trimmed_mean_data=hcm, median_data=hmed, mode_data=hmode,
                              trim_pct=median_pct, selected_measures=selected_measures),
                make_line_chart(hv.index, hv, "Hourly Var % Change", "Hour", "Var"),
                make_line_chart(hr.index, hr, "Hourly Avg Range", "Hour", "Price", 
                              mean_data=hr, trimmed_mean_data=hrm, median_data=hmed_r, mode_data=hmode_r,
                              trim_pct=median_pct, selected_measures=selected_measures),
                make_line_chart(hvr.index, hvr, "Hourly Var Range", "Hour", "Var"),
                make_line_chart(mc.index, mc, f"Min Avg %∆ @ {mh}:00", "Minute", "Pct", 
                              mean_data=mc, trimmed_mean_data=mcm, median_data=mmed, mode_data=mmode,
                              trim_pct=median_pct, selected_measures=selected_measures),
                make_line_chart(mv.index, mv, f"Min Var %∆ @ {mh}:00", "Minute", "Var"),
                make_line_chart(mr.index, mr, f"Min Avg Range @ {mh}:00", "Minute", "Price", 
                              mean_data=mr, trimmed_mean_data=mrm, median_data=mmed_r, mode_data=mmode_r,
                              trim_pct=median_pct, selected_measures=selected_measures),
                make_line_chart(mvr.index, mvr, f"Min Var Range @ {mh}:00", "Minute", "Var"),
                summary,
                empty_kpi,  # HOD/LOD KPI cards
                hod_survival_fig,
                lod_survival_fig,
                hod_heatmap_fig,
                lod_heatmap_fig,
                hod_rolling_fig,
                lod_rolling_fig
            )
            
            print(f"[DEBUG] Callback completed successfully!")
            
        except Exception as e:
            print(f"\n{'='*60}")
            print(f"EXCEPTION IN update_graphs CALLBACK:")
            print(f"{'='*60}")
            import traceback
            traceback.print_exc()
            print(f"{'='*60}\n")
            
            error_msg = html.Div([
                html.B("Error:", style={'color': 'red'}),
                html.Br(),
                html.Pre(str(e), style={'whiteSpace': 'pre-wrap', 'fontSize': '11px'}),
                html.Br(),
                html.B("Type:", style={'fontSize': '10px'}),
                html.Div(str(type(e).__name__), style={'fontSize': '10px'}),
            ])
            empty_fig = make_line_chart([], [], "No Data", "", "")
            empty_kpi = html.Div("Error occurred")
            return (empty_fig,) * 8 + (error_msg, empty_kpi) + (empty_fig,) * 6


def _scale_variance(v):
    """Scale variance for better display."""
    if v is None or v <= 0 or math.isnan(v):
        return 0.0, 0
    exp = -math.floor(math.log10(v)) + 1
    return v * (10 ** exp), exp


def _generate_summary(daily, filtered_minute, hc, hv, hr, hvr, mc, mv, mr, mvr, sh, sm):
    """Generate summary statistics box."""
    
    total_days = len(daily)
    green_days = (daily['close'] > daily['open']).sum()
    red_days = (daily['close'] < daily['open']).sum()
    
    op = daily['open'].iloc[0]
    cl = daily['close'].iloc[-1]
    chg = (cl - op) / op * 100
    
    # Count filtered data
    filtered_days = filtered_minute['date'].nunique() if 'date' in filtered_minute.columns else 0
    
    summary = [
        html.B("Date Range Summary"), html.Br(),
        f"Open: {op:.2f}", html.Br(),
        f"Close: {cl:.2f}", html.Br(),
        f"Change: {chg:.2f}%", html.Br(),
        f"Total Days: {total_days}", html.Br(),
        f"Green Days: {green_days} ({green_days/total_days*100:.2f}%)", html.Br(),
        f"Red Days: {red_days} ({red_days/total_days*100:.2f}%)", html.Br(),
        html.Br(),
        
        html.B("Filtered Data"), html.Br(),
        f"Days After Filters: {filtered_days}", html.Br(),
        f"Data Remaining: {filtered_days/total_days*100:.2f}%", html.Br(),
        html.Br(),
        
        html.B("Mean Variances (scaled)"), html.Br(),
        f"Hourly %∆ Var: {sh:.1f}", html.Br(),
        f"Hourly Range Var: {hvr.mean():.6f}", html.Br(),
        f"Minute %∆ Var: {sm:.1f}", html.Br(),
        f"Minute Range Var: {mvr.mean():.6f}", html.Br(),
    ]
    
    return summary
