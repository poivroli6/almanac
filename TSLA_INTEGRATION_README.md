# TSLA Integration with Almanac Futures

This document describes the integration of Tesla (TSLA) stock data into the Almanac Futures application using the Alpaca API.

## Overview

The TSLA integration extends the existing futures data analysis capabilities to include stock data, specifically Tesla stock. This integration maintains the same data format and analysis features while handling the different trading hours and data source requirements for stocks.

## Features

- **Real-time TSLA data** via Alpaca API
- **Local caching** to reduce API calls and improve performance
- **Trading hours awareness** (9:30 AM - 4:00 PM ET)
- **Data validation** with comprehensive quality checks
- **Seamless integration** with existing analysis features
- **Error handling** with graceful fallbacks

## Installation

### Prerequisites

1. **Alpaca API Account**: Sign up at [https://alpaca.markets/](https://alpaca.markets/)
2. **API Credentials**: Get your API key and secret key from the Alpaca dashboard

### Setup

1. **Install Dependencies**:
   ```bash
   pip install alpaca-py>=0.20.0
   ```

2. **Set Environment Variables**:
   ```bash
   # For paper trading (recommended for testing)
   export ALPACA_API_KEY="your_api_key_here"
   export ALPACA_SECRET_KEY="your_secret_key_here"
   export ALPACA_BASE_URL="https://paper-api.alpaca.markets"
   
   # For live trading (use with caution)
   export ALPACA_BASE_URL="https://api.alpaca.markets"
   ```

3. **Verify Installation**:
   ```bash
   python -c "from almanac.data_sources.alpaca_loader import get_alpaca_client; print('Alpaca client:', get_alpaca_client())"
   ```

## Usage

### Basic Usage

```python
from almanac.data_sources import load_minute_data

# Load TSLA data for a specific date range
df = load_minute_data('TSLA', '2024-01-15', '2024-01-15')
print(f"Loaded {len(df)} TSLA records")
```

### Advanced Usage

```python
from almanac.data_sources.alpaca_loader import (
    load_tsla_minute_data,
    validate_tsla_data,
    get_tsla_trading_hours,
    is_tsla_trading_time
)

# Load with custom parameters
df = load_tsla_minute_data(
    start_date='2024-01-15',
    end_date='2024-01-15',
    use_cache=True,
    save_cache=True
)

# Validate data quality
if validate_tsla_data(df):
    print("Data validation passed")
else:
    print("Data validation failed")

# Check trading hours
hours = get_tsla_trading_hours()
print(f"TSLA trades: {hours['start_time']} - {hours['end_time']} {hours['timezone']}")

# Check if current time is trading time
from datetime import datetime
now = datetime.now()
if is_tsla_trading_time(now):
    print("TSLA is currently trading")
```

## Data Format

TSLA data follows the same format as existing futures data:

| Column | Type | Description |
|--------|------|-------------|
| time | datetime | Timestamp (ET timezone) |
| open | float | Opening price |
| high | float | High price |
| low | float | Low price |
| close | float | Closing price |
| volume | int | Volume |

### Sample Data

```
time,open,high,low,close,volume
2024-01-15 09:30:00,250.00,250.50,249.80,250.50,1000
2024-01-15 09:31:00,250.50,251.00,250.20,251.00,1200
2024-01-15 09:32:00,251.00,251.20,250.80,250.80,800
```

## Trading Hours

TSLA follows regular market hours:

- **Exchange**: NYSE
- **Trading Hours**: 9:30 AM - 4:00 PM ET
- **Timezone**: US/Eastern
- **Trading Days**: Monday - Friday (excluding holidays)

### Holiday Handling

The system automatically handles:
- Weekends (Saturday/Sunday)
- Market holidays (New Year's Day, MLK Day, Presidents Day, Good Friday, Memorial Day, Independence Day, Labor Day, Thanksgiving, Christmas)
- Early close days (Black Friday, day before Independence Day)

## Caching

### Local Cache

TSLA data is automatically cached locally in the `1min/TSLA.txt` file to:
- Reduce API calls and rate limit issues
- Improve application performance
- Provide offline access to previously loaded data

### Cache Management

```python
# Force refresh from API (bypass cache)
df = load_tsla_minute_data('2024-01-15', '2024-01-15', use_cache=False)

# Load from cache only
df = load_tsla_minute_data('2024-01-15', '2024-01-15', use_cache=True, save_cache=False)
```

## Error Handling

The integration includes comprehensive error handling:

### API Errors
- **Rate Limiting**: Automatic retry with exponential backoff
- **Authentication**: Clear error messages for invalid credentials
- **Network Issues**: Graceful fallback to cached data when available

### Data Validation
- **Price Validation**: Ensures positive prices
- **OHLC Relationships**: Validates high >= open,close and low <= open,close
- **Volume Validation**: Ensures non-negative volume
- **Trading Hours**: Filters data to trading hours only

### Example Error Handling

```python
try:
    df = load_minute_data('TSLA', '2024-01-15', '2024-01-15')
except ValueError as e:
    if "API credentials" in str(e):
        print("Please check your Alpaca API credentials")
    elif "no data found" in str(e):
        print("No TSLA data available for the specified date range")
    else:
        print(f"Error loading TSLA data: {e}")
```

## Integration Points

### UI Components

TSLA appears in the product dropdown alongside existing futures:
- **Label**: "TSLA (Tesla Stock)"
- **Value**: "TSLA"
- **Position**: Added to the end of the dropdown list

### Analysis Features

All existing analysis features work with TSLA data:
- **Statistical Analysis**: Mean, median, standard deviation
- **Risk Metrics**: VaR, max drawdown, Sharpe ratio
- **Time-based Analysis**: Hourly performance, day-of-week patterns
- **Volume Analysis**: Volume patterns and correlations
- **Export Functions**: CSV export, chart export

### Data Sources

The minute loader automatically routes TSLA requests to the Alpaca API:
```python
# This automatically uses Alpaca API for TSLA
df = load_minute_data('TSLA', start_date, end_date)

# This uses file-based loading for futures
df = load_minute_data('ES', start_date, end_date)
```

## Performance Considerations

### API Rate Limits
- **Alpaca Limit**: 200 requests per minute
- **Mitigation**: Local caching reduces API calls
- **Best Practice**: Load data in reasonable chunks (e.g., 1-7 days at a time)

### Memory Usage
- **Data Size**: ~390 records per trading day (6.5 hours × 60 minutes)
- **Caching**: Data is stored in efficient CSV format
- **Cleanup**: Old cache files can be manually removed if needed

### Network Optimization
- **Compression**: Alpaca API uses gzip compression
- **Connection Pooling**: Automatic connection reuse
- **Timeout Handling**: 30-second timeout with retries

## Troubleshooting

### Common Issues

1. **"Alpaca API client not available"**
   - Check environment variables are set correctly
   - Verify API credentials are valid
   - Ensure alpaca-py is installed

2. **"No TSLA data found"**
   - Check if the date range includes trading days
   - Verify the date is not a holiday
   - Ensure API credentials have data access

3. **"Data validation failed"**
   - Check for data quality issues
   - Verify trading hours filtering
   - Review OHLC relationships

### Debug Mode

Enable debug logging to troubleshoot issues:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Now run your TSLA operations
df = load_minute_data('TSLA', '2024-01-15', '2024-01-15')
```

### Support

For issues related to:
- **Alpaca API**: Contact Alpaca support
- **TSLA Integration**: Check the application logs
- **Data Quality**: Review validation messages

## Future Enhancements

Potential improvements for future versions:

1. **Additional Stocks**: Support for other stocks (AAPL, MSFT, etc.)
2. **Real-time Updates**: WebSocket integration for live data
3. **Extended Hours**: Pre-market and after-hours data
4. **Options Data**: Support for options chains
5. **Fundamental Data**: Earnings, dividends, splits

## Security Notes

- **API Keys**: Never commit API keys to version control
- **Environment Variables**: Use secure environment variable management
- **Paper Trading**: Use paper trading for development and testing
- **Rate Limiting**: Respect API rate limits to avoid account suspension

## License

This integration follows the same license as the main Almanac Futures application.
