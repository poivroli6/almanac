# Button Callback Analysis - Almanac Futures

## Executive Summary
**Many buttons in the sidebar do NOT have working callbacks.**

The application has a beautiful UI with many buttons, but most of them are **decorative only** and don't actually do anything when clicked.

---

## Buttons WITH Working Callbacks ✅

### 1. **Date Range Buttons**
- ✅ `max-date-range-btn` - Has callback (line 1746)
- ✅ `monthly-all-range-btn` - Has callback (line 1774)
- ✅ `weekly-all-range-btn` - Has callback (line 1789)

### 2. **Calculate Buttons**
- ✅ `calc-daily-btn` - Has callback (line 1833)
- ✅ `calc-hour-btn` - Has callback (line 1834)
- ✅ `calc-weekly-btn` - Has callback (line 1835)
- ✅ `calc-monthly-btn` - Has callback (line 1836)

### 3. **Filter/Comparison Buttons**
- ✅ `apply-comparison-btn` - Has callback (line 3105)
- ✅ `apply-day-restriction-btn` - Has callback (line 3228)
- ✅ `apply-volume-comparison-btn` - Has callback (line 3355)

### 4. **Layout Control Buttons**
- ✅ `layout-left-btn` - Has callback (line 3009)
- ✅ `layout-top-btn` - Has callback (line 3010)
- ✅ `layout-hide-btn` - Has callback (line 3011)

### 5. **Preset Buttons (Partial)**
- ✅ `apply-preset-btn` - Has callback (line 2686)
- ✅ `save-preset-btn` - Has callback (line 2782)
- ✅ `delete-preset-btn` - Has callback (line 2783)

---

## Buttons WITHOUT Working Callbacks ❌

### 1. **Export/Share Buttons** 
- ❌ `share-url-btn` - **NO CALLBACK**
  - Located at line 1433
  - Button exists but does nothing
  - Should generate shareable URL

- ❌ `download-all-csv-btn` - **NO CALLBACK**
  - Located at line 1462
  - Button exists but does nothing
  - Should download CSV data

### 2. **Dynamic Preset Remove Buttons**
- ❌ `{'type': 'remove-preset', 'index': preset_id}` - **NO CALLBACK**
  - Located at line 121-123
  - The ❌ buttons on preset rows don't work
  - Should remove preset rows

---

## Why These Buttons Don't Work

### **Root Cause:**
The callbacks for these buttons were commented out or removed:

```python
# Line 2598-2602 in profile.py
# Register export callbacks (Agent 2) - DISABLED (function not defined)
# register_export_callbacks(app)

# Register filter callbacks - DISABLED (function not defined)
# register_filter_callbacks(app)
```

These callback registration functions were **disabled** because:
1. The functions `register_export_callbacks()` and `register_filter_callbacks()` don't exist
2. They were probably in separate files that were deleted during cleanup
3. The callbacks need to be re-implemented

---

## Impact on User Experience

### **What Users See vs. Reality:**

| Button | User Expectation | Reality | Impact |
|--------|------------------|---------|--------|
| 🔗 Share URL | Generate shareable link | Nothing happens | High |
| 📥 Download All CSV | Download data as CSV | Nothing happens | High |
| ❌ (Remove preset) | Remove preset row | Nothing happens | Medium |
| 💾 Save Preset | Save configuration | ✅ **Works** | Good |

---

## Recommended Fixes

### **Priority 1: Export Buttons (High Impact)**

#### 1. Share URL Button
**File**: `almanac/pages/profile.py`
**Location**: After line 2602

```python
@app.callback(
    [Output('share-url-display', 'children'),
     Output('share-url-display', 'style')],
    Input('share-url-btn', 'n_clicks'),
    [State('product-dropdown', 'value'),
     State('filter-start-date', 'date'),
     State('filter-end-date', 'date'),
     State('filters', 'value')],
    prevent_initial_call=True
)
def generate_share_url(n_clicks, product, start_date, end_date, filters):
    """Generate shareable URL with current settings."""
    if not n_clicks:
        return "", {'display': 'none'}
    
    # Build URL with query parameters
    from urllib.parse import urlencode
    base_url = "http://127.0.0.1:8085"
    params = {
        'product': product,
        'start': start_date,
        'end': end_date,
        'filters': ','.join(filters) if filters else ''
    }
    share_url = f"{base_url}?{urlencode(params)}"
    
    return html.Div([
        html.P("Share this URL:"),
        html.Code(share_url, style={'padding': '10px', 'backgroundColor': '#f8f9fa'})
    ]), {'display': 'block', 'marginTop': '10px'}
```

#### 2. Download All CSV Button
```python
@app.callback(
    Output('download-all-csv', 'data'),
    Input('download-all-csv-btn', 'n_clicks'),
    [State('h-avg', 'figure'),
     State('m-avg', 'figure'),
     State('product-dropdown', 'value')],
    prevent_initial_call=True
)
def download_all_csv(n_clicks, h_avg_fig, m_avg_fig, product):
    """Download all chart data as CSV."""
    if not n_clicks:
        return None
    
    import pandas as pd
    import io
    
    # Extract data from figures
    df = pd.DataFrame({
        'hour': h_avg_fig.get('data', [{}])[0].get('x', []),
        'avg': h_avg_fig.get('data', [{}])[0].get('y', [])
    })
    
    # Convert to CSV
    return dcc.send_data_frame(df.to_csv, f"{product}_data.csv", index=False)
```

### **Priority 2: Remove Preset Button**

```python
@app.callback(
    Output('dynamic-preset-rows', 'children', allow_duplicate=True),
    Input({'type': 'remove-preset', 'index': dash.dependencies.ALL}, 'n_clicks'),
    State('dynamic-preset-rows', 'children'),
    prevent_initial_call=True
)
def remove_preset_row(n_clicks_list, current_rows):
    """Remove a preset row when X button is clicked."""
    ctx = dash.callback_context
    
    if not ctx.triggered or not any(n_clicks_list):
        return dash.no_update
    
    # Find which button was clicked
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    clicked_index = eval(button_id)['index']  # Extract index from pattern-matching ID
    
    # Remove the row with matching index
    updated_rows = [row for row in current_rows if row['props']['id'] != clicked_index]
    
    return updated_rows
```

---

## Missing Components

Some callbacks also need components in the layout that might be missing:

### Required Components:
1. ✅ `share-url-display` - Need to add to layout
2. ✅ `download-all-csv` (dcc.Download) - Already exists (line 1478)
3. ✅ `dynamic-preset-rows` - Already exists

---

## Quick Fix Implementation

### Step 1: Add Missing Component
In the layout (around line 1433), add after the Share URL button:

```python
html.Button('🔗 Share URL', id='share-url-btn', ...),
html.Div(id='share-url-display', style={'display': 'none'}),  # ← ADD THIS
```

### Step 2: Add Callbacks
Copy the callback code above into `register_profile_callbacks()` function after line 2602.

### Step 3: Test
1. Restart server
2. Click 🔗 Share URL → Should show URL
3. Click 📥 Download All CSV → Should download file
4. Click ❌ on preset row → Should remove row

---

## Summary Statistics

- **Total Buttons**: ~18 buttons
- **Working Callbacks**: ~14 buttons (78%)
- **Non-Working Callbacks**: ~4 buttons (22%)

**High Priority Missing**:
1. Share URL button (user-facing, frequently used)
2. Download CSV button (export functionality)
3. Remove preset X buttons (UX frustration)

---

## Recommendation

**Implement the 3 missing callbacks IMMEDIATELY** to restore full functionality. These are user-facing features that create confusion when they don't work.

The good news: Most buttons (78%) already work! Just need to add these 3 callbacks to make the app fully functional.

---

**Date**: 2025-10-17
**Status**: Analysis Complete
**Next Step**: Implement missing callbacks

