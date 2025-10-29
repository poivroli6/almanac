# Weekly Analysis Feature

## Overview

The Weekly Analysis feature provides day-of-week performance insights for futures contracts, helping you identify which days of the week perform best for your trading strategy.

## Features

### 1. Weekly Statistics Graphs

The application now includes a **Weekly Statistics** section with the following graphs:

- **Weekly Avg % Change by Day**: Shows the average percentage change for each day of the week (Monday-Friday)
- **Weekly Var % Change by Day**: Displays variance in percentage changes by day of week
- **Weekly Avg Range by Day**: Shows the average price range for each day of the week
- **Weekly Var Range by Day**: Displays variance in price ranges by day of week

### 2. Day-of-Week Performance Analysis

Additional analysis graphs include:

- **Day-of-Week Performance Analysis**: Identifies the best performing day of the week
- **Day-of-Week Volatility**: Shows which days are most volatile

## How It Works

### Data Processing

1. **Daily Data Aggregation**: The system loads daily OHLC (Open, High, Low, Close) data for the selected product and date range
2. **Day-of-Week Grouping**: Data is grouped by day of the week (Monday through Sunday)
3. **Statistical Computation**: For each day of the week, the system calculates:
   - Mean, Trimmed Mean, Median, and Mode for percentage changes
   - Mean, Trimmed Mean, Median, and Mode for price ranges
   - Variance for both metrics

### Performance Metrics

The analysis identifies:
- **Best Performing Day**: The day with the highest average percentage change
- **Worst Performing Day**: The day with the lowest average percentage change
- **Most Volatile Day**: The day with the highest standard deviation in percentage changes
- **Least Volatile Day**: The day with the lowest standard deviation in percentage changes

## Usage

### Viewing Weekly Statistics

1. Open the Almanac Futures application
2. Select your product (e.g., ES, NQ, GC) from the dropdown
3. Set your desired date range
4. Click "Calculate Daily" button
5. Scroll down to the "Weekly Statistics" section to view the graphs

### Interpreting the Results

- **Positive % Change**: Days where the average close is higher than the average open
- **Negative % Change**: Days where the average close is lower than the average open
- **Higher Range**: Days with larger price movements (High - Low)
- **Higher Variance**: Days with more inconsistent performance

## Technical Implementation

### New Modules

1. **`almanac/data_sources/weekly_loader.py`**
   - `load_weekly_data()`: Loads and aggregates daily data into weekly format
   - `get_weekly_day_performance_stats()`: Analyzes day-of-week performance

2. **`almanac/features/weekly_stats.py`**
   - `compute_weekly_stats()`: Computes weekly statistics by day of week
   - `compute_weekly_day_performance()`: Analyzes performance metrics by day
   - `compute_weekly_volatility_analysis()`: Analyzes volatility patterns by day

### Integration

The weekly analysis is integrated into the main profile page (`almanac/pages/profile.py`) and appears between the Minute Statistics and Monthly Statistics sections.

## Example Output

```
Day-of-Week Performance Analysis:

Best performing day: Wednesday
Best performance: 0.002790 (0.28%)

Worst performing day: Friday  
Worst performance: -0.004819 (-0.48%)

Weekly Statistics by Day:
  weekday  pct_chg_mean  pct_chg_std
Wednesday      0.002790     0.007197
   Monday      0.001679     0.013033
  Tuesday     -0.003510     0.008701
 Thursday     -0.004350     0.009291
   Friday     -0.004819     0.019084
```

## Use Cases

1. **Day-of-Week Bias**: Identify if certain days consistently perform better or worse
2. **Strategy Optimization**: Adjust trading strategies based on day-of-week patterns
3. **Risk Management**: Avoid trading on high-volatility days if risk-averse
4. **Pattern Recognition**: Discover weekly seasonality patterns in your markets

## Notes

- Saturday and Sunday typically show zero values as most futures markets are closed
- The analysis requires sufficient data points (at least 10 days per day-of-week category) for reliable results
- Results are subject to market conditions and historical patterns may not predict future performance
- Always combine with other analysis tools and risk management practices

## Future Enhancements

Potential future improvements:
- Week-of-month analysis (first week vs. last week performance)
- Day-before-holiday pattern analysis
- Intraday day-of-week patterns (combining with hourly analysis)
- Statistical significance testing for day-of-week effects

