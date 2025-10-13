"""
Reusable UI Components

Accordion sections, preset controls, and other UI building blocks.
"""

from dash import dcc, html
import dash_bootstrap_components as dbc


def create_accordion_section(section_id, title, children, is_open=True, icon=None):
    """
    Create a collapsible accordion section for the sidebar.
    
    Args:
        section_id: Unique identifier for the accordion section
        title: Section header text
        children: List of Dash components to display in the section
        is_open: Whether the section starts open (default: True)
        icon: Optional emoji/icon to display before title
    
    Returns:
        Dash HTML component representing an accordion section
    """
    header_content = [
        html.Span(icon, style={'marginRight': '8px', 'fontSize': '16px'}) if icon else None,
        html.Span(title, style={'fontWeight': 'bold', 'fontSize': '15px'}),
        html.Span(
            '▼' if is_open else '▶',
            id=f'{section_id}-icon',
            style={
                'marginLeft': 'auto',
                'fontSize': '12px',
                'transition': 'transform 0.2s ease'
            }
        )
    ]
    
    return html.Div([
        # Header (clickable)
        html.Div(
            [c for c in header_content if c is not None],
            id=f'{section_id}-header',
            style={
                'display': 'flex',
                'alignItems': 'center',
                'padding': '12px 15px',
                'backgroundColor': '#e9ecef',
                'borderRadius': '5px',
                'cursor': 'pointer',
                'marginBottom': '5px',
                'userSelect': 'none',
                'transition': 'background-color 0.2s ease'
            },
            className='accordion-header'
        ),
        
        # Content (collapsible)
        html.Div(
            children,
            id=f'{section_id}-content',
            style={
                'display': 'block' if is_open else 'none',
                'padding': '10px 5px',
                'marginBottom': '15px',
                'transition': 'max-height 0.3s ease-out'
            }
        )
    ], style={'marginBottom': '10px'})


def create_preset_controls():
    """
    Create preset save/load controls.
    
    Returns:
        Dash HTML component with preset management UI
    """
    return html.Div([
        html.Label("Presets", style={'fontWeight': 'bold', 'marginBottom': '10px'}),
        
        # Preset dropdown
        html.Div([
            dcc.Dropdown(
                id='preset-dropdown',
                options=[],
                placeholder='Select a saved preset...',
                style={'flex': '1', 'marginRight': '5px'}
            ),
            html.Button(
                '🗑️',
                id='delete-preset-btn',
                title='Delete selected preset',
                style={
                    'padding': '5px 10px',
                    'backgroundColor': '#dc3545',
                    'color': 'white',
                    'border': 'none',
                    'borderRadius': '4px',
                    'cursor': 'pointer',
                    'fontSize': '14px'
                }
            )
        ], style={'display': 'flex', 'marginBottom': '10px', 'alignItems': 'center'}),
        
        # Save preset controls
        html.Div([
            dcc.Input(
                id='preset-name-input',
                type='text',
                placeholder='New preset name...',
                style={
                    'flex': '1',
                    'marginRight': '5px',
                    'padding': '5px 10px',
                    'borderRadius': '4px',
                    'border': '1px solid #ced4da'
                }
            ),
            html.Button(
                '💾',
                id='save-preset-btn',
                title='Save current settings as preset (Ctrl+S)',
                style={
                    'padding': '5px 10px',
                    'backgroundColor': '#28a745',
                    'color': 'white',
                    'border': 'none',
                    'borderRadius': '4px',
                    'cursor': 'pointer',
                    'fontSize': '14px'
                }
            )
        ], style={'display': 'flex', 'marginBottom': '10px'}),
        
        # Status message
        html.Div(
            id='preset-status-message',
            style={
                'fontSize': '12px',
                'padding': '5px',
                'borderRadius': '3px',
                'marginTop': '5px',
                'display': 'none'
            }
        ),
        
        # Hidden store for presets
        dcc.Store(id='presets-store', storage_type='local', data={})
    ], style={'marginBottom': '20px'})


def create_export_button():
    """
    Create export button for charts and data.
    
    Returns:
        Dash HTML component with export button
    """
    return html.Button(
        '📊 Export Data',
        id='export-data-btn',
        title='Export all data to CSV (Ctrl+E)',
        style={
            'width': '100%',
            'padding': '8px',
            'backgroundColor': '#17a2b8',
            'color': 'white',
            'border': 'none',
            'borderRadius': '4px',
            'cursor': 'pointer',
            'fontWeight': 'bold',
            'marginBottom': '10px'
        }
    )


def create_mobile_responsive_styles():
    """
    Create CSS styles for mobile responsiveness.
    
    Returns:
        HTML style component with responsive CSS
    """
    css_content = """
    /* Mobile Responsiveness */
    @media (max-width: 768px) {
        .sidebar {
            position: relative !important;
            width: 100% !important;
            height: auto !important;
            border-right: none !important;
            border-bottom: 1px solid #ccc !important;
        }
        
        .content-area {
            margin-left: 0 !important;
            padding: 10px !important;
        }
        
        .accordion-header {
            font-size: 13px !important;
        }
    }
    
    /* Tablet Responsiveness */
    @media (min-width: 769px) and (max-width: 1024px) {
        .sidebar {
            width: 25% !important;
        }
        
        .content-area {
            margin-left: 27% !important;
        }
    }
    
    /* Accordion Hover Effects */
    .accordion-header:hover {
        background-color: #dee2e6 !important;
    }
    
    /* Dark Mode Weekend Styles */
    .weekend-day {
        background-color: #2c3e50 !important;
        color: #ecf0f1 !important;
    }
    
    /* Smooth Transitions */
    .accordion-content {
        overflow: hidden;
        transition: max-height 0.3s ease-out;
    }
    
    /* Preset Controls */
    .preset-success {
        background-color: #d4edda !important;
        color: #155724 !important;
        border: 1px solid #c3e6cb !important;
    }
    
    .preset-error {
        background-color: #f8d7da !important;
        color: #721c24 !important;
        border: 1px solid #f5c6cb !important;
    }
    
    /* Keyboard Shortcut Hints */
    .shortcut-hint {
        font-size: 11px;
        color: #6c757d;
        font-style: italic;
    }
    """
    
    # Note: Dash doesn't support html.Style()
    # CSS would need to be injected via external_stylesheets or inline styles
    # For now, return empty div to prevent crash
    return html.Div(style={'display': 'none'})


def create_help_modal():
    """
    Create a help modal with keyboard shortcuts and usage tips.
    
    Returns:
        Dash HTML component with help modal
    """
    return html.Div([
        # Help button
        html.Button(
            '❓',
            id='help-modal-btn',
            title='Show keyboard shortcuts and help (F1)',
            style={
                'position': 'fixed',
                'bottom': '20px',
                'right': '20px',
                'width': '50px',
                'height': '50px',
                'borderRadius': '50%',
                'backgroundColor': '#007bff',
                'color': 'white',
                'border': 'none',
                'fontSize': '20px',
                'cursor': 'pointer',
                'boxShadow': '0 2px 10px rgba(0,0,0,0.2)',
                'zIndex': '1000'
            }
        ),
        
        # Modal overlay
        html.Div(
            id='help-modal-overlay',
            style={'display': 'none'},
            children=[
                html.Div(
                    style={
                        'position': 'fixed',
                        'top': '0',
                        'left': '0',
                        'right': '0',
                        'bottom': '0',
                        'backgroundColor': 'rgba(0,0,0,0.5)',
                        'zIndex': '1001',
                        'display': 'flex',
                        'justifyContent': 'center',
                        'alignItems': 'center'
                    },
                    children=[
                        html.Div(
                            style={
                                'backgroundColor': 'white',
                                'padding': '30px',
                                'borderRadius': '10px',
                                'maxWidth': '600px',
                                'maxHeight': '80vh',
                                'overflow': 'auto',
                                'boxShadow': '0 4px 20px rgba(0,0,0,0.3)'
                            },
                            children=[
                                html.H3('⌨️ Keyboard Shortcuts', style={'marginBottom': '20px'}),
                                
                                html.Table([
                                    html.Tr([
                                        html.Td(html.Code('Ctrl + S'), style={'padding': '5px 10px'}),
                                        html.Td('Save current settings as preset', style={'padding': '5px 10px'})
                                    ]),
                                    html.Tr([
                                        html.Td(html.Code('Ctrl + E'), style={'padding': '5px 10px'}),
                                        html.Td('Export data to CSV', style={'padding': '5px 10px'})
                                    ]),
                                    html.Tr([
                                        html.Td(html.Code('Ctrl + Enter'), style={'padding': '5px 10px'}),
                                        html.Td('Run calculation', style={'padding': '5px 10px'})
                                    ]),
                                    html.Tr([
                                        html.Td(html.Code('F1'), style={'padding': '5px 10px'}),
                                        html.Td('Show this help dialog', style={'padding': '5px 10px'})
                                    ]),
                                    html.Tr([
                                        html.Td(html.Code('Esc'), style={'padding': '5px 10px'}),
                                        html.Td('Close help dialog', style={'padding': '5px 10px'})
                                    ])
                                ], style={'width': '100%', 'marginBottom': '20px'}),
                                
                                html.Hr(),
                                
                                html.H4('📘 Quick Tips', style={'marginTop': '20px', 'marginBottom': '10px'}),
                                html.Ul([
                                    html.Li('Click on section headers to collapse/expand them'),
                                    html.Li('Save frequently used filter combinations as presets'),
                                    html.Li('Use the trim percentage to exclude outliers'),
                                    html.Li('Combine multiple filters with AND/OR logic'),
                                ]),
                                
                                html.Button(
                                    'Close',
                                    id='close-help-modal-btn',
                                    style={
                                        'marginTop': '20px',
                                        'padding': '10px 20px',
                                        'backgroundColor': '#007bff',
                                        'color': 'white',
                                        'border': 'none',
                                        'borderRadius': '4px',
                                        'cursor': 'pointer',
                                        'width': '100%'
                                    }
                                )
                            ]
                        )
                    ]
                )
            ]
        )
    ])

