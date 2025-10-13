# Almanac Futures v2.0 - Intraday Pattern Analysis

## Overview
This application analyzes historical intraday patterns in futures contracts to identify repeatable behaviors based on previous day conditions and time-of-day statistics.

**Version 2.0** features a complete architectural refactoring with modular structure, improved data validation, caching, and comprehensive test coverage.

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Application
```bash
python run.py
```

Or with custom settings:
```bash
python run.py --port 8086 --no-debug
```

The application will be available at: `http://127.0.0.1:8085`

### 3. Run Tests
```bash
pytest tests/
```

---

## Features

### Core Analysis
- **Hourly Statistics**: Average and variance of returns and ranges by hour
- **Minute Statistics**: Drill-down analysis for specific hours
- **Conditional Filtering**: Previous day metrics, weekday selection, volume filters
- **HOD/LOD Detection**: High-of-day and low-of-day timing analysis
- **Time Comparisons**: Filter based on price relationships at specific times

### Data Quality
- ✅ Trading calendar with holiday handling
- ✅ Data validation (nulls, duplicates, OHLC relationships)
- ✅ Extreme outlier detection and trimming
- ✅ Missing data gap reporting

### Performance
- ✅ Flask-caching for fast repeated queries
- ✅ Database connection pooling
- ✅ Efficient filtering pipeline

### Testing
- ✅ Comprehensive pytest suite
- ✅ Mock fixtures for database-free testing
- ✅ Edge case coverage

---

## Architecture

The application follows a clean, modular architecture:

```
almanac/
├── data_sources/    # Database loaders with validation
├── features/        # Statistical computations & filtering
├── viz/             # Plotly figure factory functions
└── pages/           # Dash UI layouts & callbacks
```

**See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed documentation.**

---

## Usage Guide

### Product Selection
Choose from:
- **ES**: E-mini S&P 500
- **NQ**: E-mini Nasdaq 100
- **GC**: Gold Futures

### Date Range
Select start and end dates for the analysis period.

### Filters

#### Previous Day Conditions
- **Close > Open / Close < Open**: Filter by previous day direction
- **%∆ Thresholds**: Set percentage change requirements (e.g., "previous day up >1%")
- **Relative Volume**: Filter by volume relative to 10-day average

#### Weekday Selection
Analyze specific days of the week (e.g., "only Tuesdays")

#### Time Comparisons
Compare prices at two specific times to filter for intraday patterns
- Example: "Days when 9:45 price > 10:15 price"

#### Extreme Trimming
Exclude the top and bottom 5% of returns and ranges to focus on typical behavior

### Output Charts

**Hourly Statistics:**
1. Average % Change by hour
2. Variance of % Change by hour
3. Average Range by hour
4. Variance of Range by hour

**Minute Statistics (for selected hour):**
5. Average % Change by minute
6. Variance of % Change by minute
7. Average Range by minute
8. Variance of Range by minute

**Summary Panel:**
- Date range metrics (open, close, change)
- Total days and green/red day distribution
- Filtered data statistics
- Scaled variance metrics

---

## Database Requirements

### Connection
The application connects to the RESEARCH database on SQL Server.

**Ensure you have:**
- ODBC Driver 17 for SQL Server installed
- Proper database access credentials
- Network access to the database server

### Required Indexes (for performance)
```sql
CREATE INDEX idx_raw_time_product 
  ON RawIntradayData(contract_id, interval, time);

CREATE INDEX idx_daily_product 
  ON DailyData(contract_id, time);
```

### Tables Used
- `dbo.RawIntradayData`: 1-minute OHLCV data
- `dbo.DailyData`: Daily OHLCV data

---

## Development

### Running Tests
```bash
# Run all tests
pytest tests/

# Verbose output
pytest tests/ -v

# With coverage report
pytest tests/ --cov=almanac --cov-report=html
```

### Code Formatting
```bash
# Format code
black almanac/

# Check linting
flake8 almanac/
```

### Project Structure
```
Almanac Futures/
├── almanac/              # Main package
│   ├── data_sources/     # Data loading & validation
│   ├── features/         # Statistics & filtering
│   ├── viz/              # Visualization
│   └── pages/            # UI components
├── tests/                # Test suite
├── .cache/               # Caching directory (auto-created)
├── run.py                # Application launcher
├── requirements.txt      # Python dependencies
├── pytest.ini            # Test configuration
├── ARCHITECTURE.md       # Detailed architecture docs
└── README.md             # This file
```

---

## Troubleshooting

### "No data found" Error
- **Check:** Product code spelling (ES, NQ, GC)
- **Check:** Date range has available data
- **Check:** Database connection and permissions

### Slow Performance
- **Solution:** Add database indexes (see above)
- **Solution:** Reduce date range (<3 months for minute data)
- **Solution:** Clear cache: delete `.cache/` directory

### Test Failures
- **Missing scipy:** Some statistical tests require `scipy`
- **Database mocks:** Integration tests use mocks by default

---

## Roadmap

### Phase 1 (Current - v2.0)
- ✅ Modular architecture
- ✅ Data validation & quality checks
- ✅ Trading calendar integration
- ✅ Flask-caching
- ✅ Comprehensive test suite

### Phase 2 (Next)
- [ ] HOD/LOD survival curves and heatmaps
- [ ] Export functionality (CSV, PNG)
- [ ] Shareable URLs with query parameters
- [ ] Preset save/load

### Phase 3 (Future)
- [ ] Cross-asset correlation analysis
- [ ] Event calendar integration (CPI, NFP, FOMC)
- [ ] Strategy sandbox (simple backtests)
- [ ] ML classification (day archetype prediction)

**See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed roadmap.**

---

## Contributing

1. Write tests for new features
2. Follow PEP 8 style guidelines
3. Update documentation
4. Run test suite before committing

---

## License

**Version:** 2.0.0  
**Author:** Trading Research Team  
**License:** Internal Use Only
