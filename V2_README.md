# 🚀 Almanac Futures V2 - Clean Restart

A simplified, streamlined version of Almanac Futures built from scratch with modern best practices.

## 📁 Project Structure

```
v2almanac_app.py          # Main application entry point
v2almanac_layout.py       # Complete UI layout components  
v2almanac_callbacks.py    # Callback handlers (UI interactions)
run_v2.py                 # Simple launcher script
```

## ✨ Features Implemented

### UI Components (All Visual Elements)
- ✅ Real-time clock display (EST timezone)
- ✅ Product selection dropdown (26 products)
- ✅ Date range controls with Max Date Range button
- ✅ Statistical visuals configuration (Mean Trim %, Display Measures)
- ✅ Filters & conditions section
- ✅ Day of interest selector
- ✅ Filter presets dropdown
- ✅ Yearly analysis (month/year range selector)
- ✅ Weekly analysis (month/year range selector)
- ✅ Daily analysis (weekday filters)
- ✅ Hourly analysis (minute hour selector)
- ✅ Active scenarios display
- ✅ Save/Load presets interface
- ✅ Price comparison builder
- ✅ Volume comparison builder
- ✅ Export & share buttons

### Callbacks (Placeholder Responses)
- ✅ Time update (live clock)
- ✅ All button interactions work
- ✅ Calculate buttons show placeholder responses
- ✅ Preset save functionality
- ✅ Export/share placeholder responses

## 🚀 How to Run

### Quick Start
```bash
python run_v2.py
```

Then open your browser to: **http://127.0.0.1:8086**

### Custom Port/Host
```python
from v2almanac_app import run_server
run_server(host='0.0.0.0', port=8080, debug=True)
```

## 🎯 Design Philosophy

### Why This Version?
1. **Simplicity First** - Only 3 files, easy to understand
2. **Clean Architecture** - No complex debugging infrastructure
3. **Easy to Debug** - Clear separation of concerns
4. **Maintainable** - Each section is self-contained
5. **Extensible** - Easy to add new features

### What's Different from V1?
- ❌ No complex caching system
- ❌ No performance monitoring overhead
- ❌ No intricate callback validation
- ❌ No multi-layer abstraction
- ✅ Simple, direct code
- ✅ Easy to trace issues
- ✅ Fast to modify

## 📊 Available Products

The following products are available in the dropdown:
- **Indices**: ES, NQ, YM
- **Metals**: GC, SI, HG, PA, PL
- **Energy**: CL, NG
- **Crypto**: BTCUSD
- **Equities**: TSLA
- **Currencies**: EU, JY, AD, BP, CD, SF
- **Agriculture**: C, W, S, RP
- **Fixed Income**: TY, US, FV, TU

## 🔧 Next Steps - Backend Integration

When you're ready to add backend functionality, here's the recommended approach:

### Phase 1: Data Loading
1. Create `v2almanac_data.py` for data loading functions
2. Implement simple file readers for 1min/*.txt files
3. Add basic data validation

### Phase 2: Calculations
1. Add calculation functions to callbacks
2. Implement yearly/weekly/daily/hourly analysis
3. Keep calculations simple and direct

### Phase 3: Visualizations
1. Add Plotly charts to main content area
2. Implement heatmaps, line charts, etc.
3. Use simple chart configurations

### Phase 4: Advanced Features
1. Implement price/volume comparisons
2. Add filter logic
3. Implement preset save/load
4. Add CSV export functionality

## 💡 Tips for Development

### Adding a New Callback
```python
@app.callback(
    Output('some-output', 'children'),
    Input('some-button', 'n_clicks'),
    State('some-input', 'value'),
    prevent_initial_call=True
)
def handle_something(n_clicks, input_value):
    # Your logic here
    return result
```

### Adding a New UI Section
```python
def create_new_section():
    """Create a new UI section."""
    return html.Div([
        html.H3('Section Title'),
        # Your components here
    ], style={
        'backgroundColor': '#ecf0f1',
        'padding': '15px',
        'borderRadius': '8px',
        'marginBottom': '20px'
    })
```

### Debugging Tips
1. Check browser console for JavaScript errors
2. Look at Flask terminal output for Python errors
3. Use `logger.info()` to trace execution
4. Test callbacks individually

## 🐛 Known Limitations (By Design)

- Backend calculations not implemented yet
- Data loading not connected
- Preset save/load is placeholder
- CSV export is placeholder
- Charts not generated yet

These are intentional - the focus is on getting the UI structure right first!

## 📝 Code Quality

- ✅ No linter errors
- ✅ Clear function names
- ✅ Documented with docstrings
- ✅ Consistent styling
- ✅ Modern Dash practices

## 🎨 Styling Notes

- Uses inline styles for simplicity
- Color scheme matches original design
- Responsive layout with flexbox
- Scrollable sidebar
- Clean, modern appearance

## 🔄 Migration from V1

If you want to port functionality from the old version:

1. **Don't copy-paste complex code** - Rewrite it simply
2. **Start with one feature** - Get it working fully
3. **Test thoroughly** - Make sure it's bulletproof
4. **Document as you go** - Keep code readable
5. **Avoid over-engineering** - Keep it simple!

---

**Built with:** Python 3.x, Dash, Plotly  
**License:** Your choice  
**Version:** 2.0.0 (Clean Restart)

