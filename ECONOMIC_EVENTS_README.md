# Economic Events Filter Feature

## Overview

The Almanac application now includes filters for major economic events, allowing you to analyze market behavior on days when important economic data is released.

## Available Economic Event Filters

### 1. **CPI Release Day** 💰
- **Filter ID**: `cpi_day`
- **Description**: Consumer Price Index release days - a key inflation indicator
- **Frequency**: Monthly (typically mid-month)
- **Market Impact**: High volatility expected

### 2. **FOMC Meeting Day** 🏦
- **Filter ID**: `fomc_day`
- **Description**: Federal Open Market Committee meeting decision announcement days
- **Frequency**: 8 times per year
- **Market Impact**: Very high volatility, major policy decisions

### 3. **Non-Farm Payrolls (NFP) Day** 👔
- **Filter ID**: `nfp_day`
- **Description**: Employment situation report (Jobs Report)
- **Frequency**: Monthly (first Friday of the month, typically)
- **Market Impact**: Very high volatility, labor market health indicator

### 4. **Producer Price Index (PPI) Day** 🏭
- **Filter ID**: `ppi_day`
- **Description**: Producer Price Index release days - wholesale inflation
- **Frequency**: Monthly (typically day after CPI)
- **Market Impact**: Moderate to high volatility

### 5. **Retail Sales Day** 🛒
- **Filter ID**: `retail_sales_day`
- **Description**: Retail sales report - consumer spending indicator
- **Frequency**: Monthly (mid-month)
- **Market Impact**: Moderate volatility

### 6. **GDP Release Day** 📊
- **Filter ID**: `gdp_day`
- **Description**: Gross Domestic Product reports (advance, preliminary, final)
- **Frequency**: Quarterly (3 releases per quarter)
- **Market Impact**: Moderate volatility

### 7. **PCE Inflation Day** 💵
- **Filter ID**: `pce_day`
- **Description**: Personal Consumption Expenditures - Fed's preferred inflation gauge
- **Frequency**: Monthly (end of month)
- **Market Impact**: High volatility

### 8. **Any Major Economic Event** ⚡
- **Filter ID**: `major_event_day`
- **Description**: Any day with any of the above economic events
- **Use Case**: Analyze all high-impact data release days together

## How to Use

1. **In the Sidebar**: Navigate to the "🔍 Custom Filter Options" section
2. **Select Events**: Check the economic event filters you want to analyze
3. **Combine Filters**: Use multiple filters together (e.g., CPI days + FOMC days)
4. **Logic Operator**: Choose AND/OR to combine with other filters

## Example Use Cases

### Example 1: FOMC Day Behavior
```
Filters: FOMC Meeting Day
Product: ES (E-mini S&P 500)
Analysis: See how the S&P 500 behaves on Federal Reserve decision days
```

### Example 2: NFP + Previous Day Bearish
```
Filters: 
- Non-Farm Payrolls (NFP) Day
- Prev-Day: Close < Open (Bearish)
Logic: AND
Analysis: How does the market behave on jobs report days when the previous day was bearish
```

### Example 3: All Major Events
```
Filters: Any Major Economic Event
Product: GC (Gold)
Analysis: Gold behavior on all major economic data release days
```

### Example 4: CPI Days with High Volume
```
Filters:
- CPI Release Day
- Prev-Day: High Relative Volume
Threshold: 1.5x
Logic: AND
Analysis: Analyze CPI days that follow high volume days
```

## Data Coverage

The economic events calendar includes data for:
- **2023**: Full year coverage
- **2024**: Full year coverage
- **2025**: Scheduled dates (subject to actual release schedules)

## Technical Details

### Files Modified/Created
1. **`almanac/data_sources/economic_events.py`** - New module with economic calendar data
2. **`almanac/features/filters.py`** - Updated to handle economic event filters
3. **`almanac/pages/profile.py`** - UI updated with new filter options

### Data Structure
Economic events are stored as sets of date strings in `YYYY-MM-DD` format:
```python
ECONOMIC_EVENTS = {
    'CPI': {'2024-01-11', '2024-02-13', ...},
    'FOMC': {'2024-01-31', '2024-03-20', ...},
    # etc.
}
```

## Maintenance Notes

### Updating Economic Calendars
To add new dates or years, edit `almanac/data_sources/economic_events.py`:

```python
ECONOMIC_EVENTS = {
    'CPI': {
        # Add new dates in 'YYYY-MM-DD' format
        '2026-01-14',
        '2026-02-11',
        # etc.
    }
}
```

### Data Sources
Economic event dates should be sourced from:
- Federal Reserve official calendar (FOMC)
- Bureau of Labor Statistics schedule (CPI, PPI, NFP)
- Bureau of Economic Analysis schedule (GDP, PCE)
- Census Bureau schedule (Retail Sales)

### Future Enhancements
Potential improvements:
1. **API Integration**: Connect to real-time economic calendar APIs
2. **Event Importance**: Add weight/importance levels to events
3. **Release Time**: Include exact release times (typically 8:30 AM ET)
4. **Historical Impact**: Store typical volatility metrics for each event
5. **International Events**: Add ECB, BOJ, BOE decisions
6. **More Events**: Add ISM PMI, Housing Data, Consumer Confidence, etc.

## Troubleshooting

### No Data Returned
- Check if the selected date range includes economic event dates
- Verify the product has data for those specific dates
- Use "Any Major Economic Event" to test if any events match

### Unexpected Results
- Economic calendars can change - releases can be rescheduled
- Some events have multiple releases per period (GDP: advance, preliminary, final)
- Check that the correct event type is selected

## API Reference

### Function: `is_economic_event_date()`
```python
from almanac.data_sources.economic_events import is_economic_event_date

# Check if a date is a CPI release day
is_cpi = is_economic_event_date('2024-01-11', 'CPI')  # Returns True
```

### Function: `get_events_on_date()`
```python
from almanac.data_sources.economic_events import get_events_on_date

# Get all events on a specific date
events = get_events_on_date('2024-01-31')  # Returns ['FOMC']
```

## Contact

For questions or suggestions about economic event filters, please refer to the main README.md or contact the development team.

---

**Last Updated**: October 2024
**Version**: 1.0

