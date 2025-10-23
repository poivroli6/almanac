# Almanac Futures - Architecture Documentation

## Overview

Almanac Futures is a modular Dash application for analyzing historical intraday patterns in futures contracts. The v2.0 refactoring introduces a clean separation of concerns with proper data validation, caching, and testability.

---

## Directory Structure

```
Almanac Futures/
├── almanac/                    # Main package
│   ├── __init__.py
│   ├── app.py                  # Application entry point
│   ├── data_sources/           # Data loading & validation
│   │   ├── __init__.py
│   │   ├── db_config.py        # Database connection management
│   │   ├── minute_loader.py    # Minute-level data loading
│   │   ├── daily_loader.py     # Daily OHLCV loading
│   │   └── calendar.py         # Trading calendar utilities
│   ├── features/               # Feature engineering & statistics
│   │   ├── __init__.py
│   │   ├── stats.py            # Statistical computations
│   │   ├── filters.py          # Conditional filtering
│   │   └── hod_lod.py          # HOD/LOD detection & analysis
│   ├── viz/                    # Visualization
│   │   ├── __init__.py
│   │   └── figures.py          # Plotly figure factory functions
│   └── pages/                  # Dash page layouts
│       ├── __init__.py
│       └── profile.py          # Main profile/analysis page
├── tests/                      # Test suite
│   ├── __init__.py
│   ├── conftest.py             # Pytest fixtures
│   ├── test_data_sources.py
│   ├── test_features.py
│   ├── test_filters.py
│   └── test_hod_lod.py
├── .cache/                     # Flask-caching storage (auto-created)
├── Almanac_main.py             # Legacy script (kept for reference)
├── requirements.txt
└── README.md
```

---

## Module Responsibilities

### **data_sources/** - Data Access Layer

**Purpose:** Isolate all database interactions and data loading logic.

#### `db_config.py`
- Manages SQLAlchemy engine with connection pooling
- Singleton pattern for engine instance
- Pool pre-ping and recycling for reliability

#### `minute_loader.py`
- Loads 1-minute intraday data from `RawIntradayData` table
- Data validation: nulls, duplicates, OHLC relationships, price sanity checks
- Summary statistics without loading full data

#### `daily_loader.py`
- Loads daily OHLCV from `DailyData` table
- Auto-computes derived fields: returns, ranges, volume SMAs, weekday
- Summary statistics

#### `calendar.py`
- Trading calendar utilities using `pandas-market-calendars`
- Handles holidays, weekends, half-days
- Replaces naive `BDay()` with exchange-aware logic
- Fallback to business days if library not installed

**Key Design Decisions:**
- Pure functions: no side effects
- Typed return values (DataFrames with known schemas)
- Validation is optional but enabled by default
- Warnings for data quality issues (non-blocking)

---

### **features/** - Feature Engineering & Statistics

**Purpose:** Business logic for statistical computations and data transformations.

#### `stats.py`
- `compute_hourly_stats()`: Aggregates minute data by hour
- `compute_minute_stats()`: Aggregates by minute within a specific hour
- `compute_intraday_vol_curve()`: Rolling volatility patterns
- `compute_rolling_metrics()`: Generic rolling statistics

#### `filters.py`
- `apply_filters()`: Multi-condition filtering based on previous day metrics
  - Weekday selection
  - Previous day direction (green/red)
  - Previous day % change thresholds
  - Relative volume conditions
  - Extreme trimming (top/bottom 5%)
- `apply_time_filters()`: Price comparison at specific times
- `_prepare_daily_with_prev()`: Joins previous day metrics using trading calendar

#### `hod_lod.py`
- `detect_hod_lod()`: Finds HOD/LOD time and price for each day
- `compute_survival_curves()`: CDF of "HOD/LOD already occurred by time T"
- `compute_hod_lod_heatmap()`: Frequency heatmaps by weekday/month/time
- `compute_rolling_median_time()`: Trend analysis with confidence intervals
- `compute_trend_test()`: Mann-Kendall test + Theil-Sen slope

**Key Design Decisions:**
- Stateless functions (no global state)
- Explicit parameters (no hidden dependencies)
- Defensive programming: handle edge cases (empty data, NaNs)
- Return structured data (DataFrames, not bare arrays)

---

### **viz/** - Visualization Layer

**Purpose:** Reusable, consistent chart generation.

#### `figures.py`
- `make_line_chart()`: Line charts with optional confidence bands
- `make_heatmap()`: 2D frequency/correlation matrices
- `make_survival_curve()`: Step functions for CDFs
- `make_violin_plot()`: Distribution comparisons across groups
- `make_box_plot()`: Box plots with mean/std
- `make_scatter()`: Scatter with optional color/size mapping

**Key Design Decisions:**
- Consistent styling: `template='plotly_white'`, unified margins
- Hover templates for rich tooltips
- Reference lines for percentiles (survival curves)
- Configurable but sensible defaults

---

### **pages/** - UI Layer

**Purpose:** Dash layouts and callbacks.

#### `profile.py`
- Layout: Left sidebar (controls) + Right content (charts)
- Callback: Loads data → applies filters → computes stats → generates figures
- Integrated with Flask-Caching for performance
- Error handling with user-friendly messages

**Key Design Decisions:**
- Single callback for all outputs (atomic updates)
- State stored in `dcc.Store` (future: URL params)
- Loading indicators for async operations
- Summary box with key metrics

---

## Data Flow

```
User Input (Product, Dates, Filters)
    ↓
[Callback Triggered]
    ↓
Load Data (data_sources)
    ├─ load_daily_data()    → Daily OHLCV + derived fields
    └─ load_minute_data()   → Minute OHLCV with validation
    ↓
Apply Filters (features)
    ├─ apply_filters()      → Filter by prev-day conditions
    └─ apply_time_filters() → Filter by time comparisons
    ↓
Compute Statistics (features)
    ├─ compute_hourly_stats()
    ├─ compute_minute_stats()
    └─ detect_hod_lod() (optional)
    ↓
Generate Figures (viz)
    └─ make_line_chart() × 8
    ↓
Update UI
```

---

## Caching Strategy

### Flask-Caching Configuration
- **Type:** Filesystem (`.cache/` directory)
- **Timeout:** 3600 seconds (1 hour)
- **Threshold:** 500 items
- **Decorator:** `@cache.memoize(timeout=...)`

### What's Cached
- Main callback results (all 9 outputs)
- Cache key: `hash(product, start, end, minute_hour, filters, thresholds, time_params)`

### Cache Invalidation
- **Time-based:** Auto-expires after 1 hour
- **Manual:** Clear `.cache/` directory or restart app
- **Future:** Add "Clear Cache" button in UI

---

## Data Quality & Validation

### Minute Data Checks
1. **Nulls:** Detect and warn
2. **Duplicates:** Remove, keep first occurrence
3. **OHLC Relationships:** `high >= open, close, low` and `low <= open, close, high`
4. **Price Sanity:** No zero or negative prices
5. **Time Gaps:** Report gaps >5 minutes (potential missing data)

### Daily Data Checks
- Relies on database integrity
- Auto-computes derived fields for consistency
- Rolling metrics use `min_periods=1` to handle short windows

### Trading Calendar
- **Preferred:** `pandas-market-calendars` (CME/CBOT aware)
- **Fallback:** `pd.tseries.offsets.BDay()`
- Handles holidays: New Year's, Christmas, Thanksgiving, etc.
- Handles half-days: Day before Thanksgiving, early closes

---

## Testing Strategy

### Fixtures (`conftest.py`)
- `sample_minute_data`: 2 days × 60 minutes of synthetic OHLCV
- `sample_daily_data`: 30 days of synthetic daily data
- `sample_hod_lod_data`: Pre-computed HOD/LOD times
- `empty_dataframe`: Edge case testing

### Test Coverage
- **Unit Tests:** All feature functions
- **Integration Tests:** End-to-end data loading (mocked)
- **Edge Cases:** Empty data, missing columns, invalid inputs

### Running Tests
```bash
pytest tests/                    # Run all tests
pytest tests/ -v                 # Verbose output
pytest tests/ --cov=almanac      # With coverage report
```

---

## Performance Considerations

### Database Query Optimization
- **Indexes Required:**
  ```sql
  CREATE INDEX idx_raw_time_product 
    ON RawIntradayData(contract_id, interval, time);
  
  CREATE INDEX idx_daily_product 
    ON DailyData(contract_id, time);
  ```
- **Connection Pooling:** Reuses connections (pool_recycle=3600s)
- **Parameter Binding:** Prevents SQL injection, enables query plan caching

### Memory Efficiency
- Avoid loading entire history at once (use date ranges)
- `apply_filters()` reduces data early in pipeline
- Aggregations (groupby) happen on filtered data

### UI Responsiveness
- Single callback reduces round-trips
- Loading indicators prevent user confusion
- Debounced inputs (number fields)

---

## Future Enhancements (Roadmap)

### Immediate (Set 2-3)
1. **Product Profile Page:**
   - KPI cards (ADR, %Green, Median HOD/LOD times)
   - HOD/LOD heatmaps and survival curves
   - Rolling drift analysis

2. **Export Functionality:**
   - CSV export per chart
   - PNG downloads
   - Shareable URLs with query params

3. **UI Polish:**
   - Accordion-style sidebar
   - Preset save/load
   - Keyboard shortcuts

### Medium-Term (Set 4-6)
4. **Extremes Page:**
   - Violin plots by weekday/month
   - Conditional heatmaps
   - Mann-Kendall trend tests

5. **Cross-Asset Lab:**
   - Load secondary products (ETFs, other futures)
   - Lead-lag correlation heatmaps
   - Event study: align on secondary spikes

6. **Event Calendar:**
   - Macro events (CPI, NFP, FOMC)
   - Split analysis: macro vs non-macro days

### Long-Term (Set 7-9)
7. **Strategy Sandbox:**
   - Time-fade strategies
   - Range-completion setups
   - Backtest with MAE/MFE

8. **ML Pipeline:**
   - Binary classification (close > open)
   - Feature engineering (early session metrics)
   - Walk-forward validation
   - SHAP explainability

9. **Scalability:**
   - DuckDB for analytics queries
   - Polars for data transformations
   - FastAPI + React for multi-user

---

## Troubleshooting

### "No data found" Error
- **Check:** Product code spelling (ES, NQ, GC)
- **Check:** Date range (is data available for those dates?)
- **Check:** Database connection (firewall, credentials)

### Slow Performance
- **Check:** Date range (>6 months can be slow)
- **Fix:** Add database indexes
- **Fix:** Reduce time range or use daily-only analysis first

### Cache Issues
- **Symptom:** Stale results after data updates
- **Fix:** Delete `.cache/` directory
- **Alternative:** Restart application

### Test Failures
- **Missing `scipy`:** Trend tests will show "scipy_not_installed"
- **Mock Issues:** Some integration tests require proper mocks
- **Date Alignment:** Test data may have weekends (expected)

---

## Contributing

### Code Style
- Follow PEP 8
- Use type hints where helpful
- Docstrings for all public functions

### Adding Features
1. Write feature function in `features/`
2. Add corresponding tests in `tests/`
3. Add visualization in `viz/` if needed
4. Wire into callback in `pages/`
5. Update this architecture doc

### Pull Request Checklist
- [ ] Tests pass (`pytest tests/`)
- [ ] Code formatted (`black almanac/`)
- [ ] No linter errors (`flake8 almanac/`)
- [ ] Documentation updated

---

## License & Contact

**Version:** 2.0.0  
**Author:** Trading Research Team  
**License:** Internal Use Only

