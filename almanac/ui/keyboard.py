"""
Keyboard Shortcut Handlers

Client-side JavaScript for keyboard shortcuts.
"""

from dash import html, Input, Output, State, clientside_callback


# JavaScript code for keyboard event handling
KEYBOARD_SHORTCUTS_JS = """
function() {
    // Add keyboard event listener
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + S: Save preset
        if ((e.ctrlKey || e.metaKey) && e.key === 's') {
            e.preventDefault();
            const saveBtn = document.getElementById('save-preset-btn');
            if (saveBtn) saveBtn.click();
        }
        
        // Ctrl/Cmd + E: Export data
        if ((e.ctrlKey || e.metaKey) && e.key === 'e') {
            e.preventDefault();
            const exportBtn = document.getElementById('export-data-btn');
            if (exportBtn) exportBtn.click();
        }
        
        // Ctrl/Cmd + Enter: Calculate
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            e.preventDefault();
            const calcBtn = document.getElementById('calc-btn');
            if (calcBtn) calcBtn.click();
        }
        
        // F1: Show help
        if (e.key === 'F1') {
            e.preventDefault();
            const helpBtn = document.getElementById('help-modal-btn');
            if (helpBtn) helpBtn.click();
        }
        
        // Escape: Close help modal
        if (e.key === 'Escape') {
            const helpOverlay = document.getElementById('help-modal-overlay');
            if (helpOverlay && helpOverlay.style.display !== 'none') {
                const closeBtn = document.getElementById('close-help-modal-btn');
                if (closeBtn) closeBtn.click();
            }
        }
    });
    
    return window.dash_clientside.no_update;
}
"""


# JavaScript code for accordion toggle
ACCORDION_TOGGLE_JS = """
function(n_clicks, current_display) {
    if (!n_clicks) {
        return window.dash_clientside.no_update;
    }
    
    // Toggle display
    return current_display === 'none' ? 'block' : 'none';
}
"""


# JavaScript code for accordion icon rotation
ACCORDION_ICON_JS = """
function(n_clicks, current_icon) {
    if (!n_clicks) {
        return window.dash_clientside.no_update;
    }
    
    // Toggle icon
    return current_icon === '▼' ? '▶' : '▼';
}
"""


def register_keyboard_shortcuts(app):
    """
    Register keyboard shortcut handlers with the Dash app.
    
    Args:
        app: Dash application instance
    """
    # Register clientside callback for keyboard events
    # This runs in the browser for instant response
    clientside_callback(
        KEYBOARD_SHORTCUTS_JS,
        Output('keyboard-listener', 'data'),
        Input('keyboard-listener', 'data')
    )


def create_keyboard_listener():
    """
    Create a hidden component that listens for keyboard events.
    
    Returns:
        dcc.Store component for keyboard event handling
    """
    from dash import dcc
    return dcc.Store(id='keyboard-listener', data=0)


def register_accordion_callbacks(app, section_ids: list):
    """
    Register accordion toggle callbacks for each section.
    
    Args:
        app: Dash application instance
        section_ids: List of accordion section IDs
    """
    for section_id in section_ids:
        # Toggle content visibility
        clientside_callback(
            ACCORDION_TOGGLE_JS,
            Output(f'{section_id}-content', 'style'),
            Input(f'{section_id}-header', 'n_clicks'),
            State(f'{section_id}-content', 'style'),
            prevent_initial_call=True
        )
        
        # Toggle icon
        clientside_callback(
            ACCORDION_ICON_JS,
            Output(f'{section_id}-icon', 'children'),
            Input(f'{section_id}-header', 'n_clicks'),
            State(f'{section_id}-icon', 'children'),
            prevent_initial_call=True
        )


def register_help_modal_callbacks(app):
    """
    Register callbacks for help modal toggle.
    
    Args:
        app: Dash application instance
    """
    @app.callback(
        Output('help-modal-overlay', 'style'),
        [Input('help-modal-btn', 'n_clicks'),
         Input('close-help-modal-btn', 'n_clicks')],
        State('help-modal-overlay', 'style'),
        prevent_initial_call=True
    )
    def toggle_help_modal(open_clicks, close_clicks, current_style):
        """Toggle help modal visibility."""
        from dash import callback_context
        
        if not callback_context.triggered:
            return current_style
        
        trigger_id = callback_context.triggered[0]['prop_id'].split('.')[0]
        
        if trigger_id == 'help-modal-btn':
            return {'display': 'block'}
        elif trigger_id == 'close-help-modal-btn':
            return {'display': 'none'}
        
        return current_style

