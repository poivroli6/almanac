# TSLA Data Cache System

This system provides a safe way to pull TSLA data from the Alpaca API only once per day and cache it locally, preventing API rate limit issues and potential account restrictions.

## 🚨 **Important: API Rate Limit Protection**

The Alpaca API has rate limits (200 requests per minute). To avoid getting restricted:
- **Only pull data once per day** using the cache system
- **Never make repeated API calls** from the application
- **Always use cached data** for regular operations

## 📁 **Cache System Overview**

### Files Created:
- `1min/TSLA.txt` - Minute-level data (same format as existing futures)
- `daily/TSLA_daily.txt` - Daily OHLCV data (same format as existing futures)
- `1min/tsla_cache_metadata.json` - Cache metadata and timestamps

### Data Flow:
1. **Cache Manager** pulls data once per day from Alpaca API
2. **Data Loaders** prioritize cached files over API calls
3. **Application** uses cached data for all operations

## 🛠️ **Usage**

### Initial Setup (One-time):
```bash
# Pull TSLA data once and cache it
python cache_tsla_data.py
```

### Check Cache Status:
```bash
# See when data was last updated
python cache_tsla_data.py --status
```

### Force Update (if needed):
```bash
# Force update even if cache is fresh
python cache_tsla_data.py --force
```

### Dry Run (see what would happen):
```bash
# Preview what the script would do
python cache_tsla_data.py --dry-run
```

## 📊 **Data Format**

### Minute Data (`1min/TSLA.txt`):
```
MM/DD/YYYY,HH:MM,Open,High,Low,Close,Volume
01/15/2024,09:30,250.00,250.50,249.80,250.50,1000
01/15/2024,09:31,250.50,251.00,250.20,251.00,1200
```

### Daily Data (`daily/TSLA_daily.txt`):
```
MM/DD/YYYY,00:00,Open,High,Low,Close,Volume
01/15/2024,00:00,250.00,255.00,245.00,252.00,390000
01/16/2024,00:00,252.00,258.00,248.00,256.00,420000
```

## 🔧 **Technical Details**

### Cache Manager (`cache_tsla_data.py`):
- **Smart Caching**: Only pulls data if cache is older than today
- **Data Conversion**: Converts minute data to daily OHLCV format
- **Metadata Tracking**: Tracks when data was last updated
- **Error Handling**: Graceful fallbacks if API fails

### Data Loaders (Updated):
- **Priority Order**: Cached files → API fallback → Error
- **Format Consistency**: Same format as existing futures data
- **Validation**: Data quality checks and validation

### Cache Metadata:
```json
{
  "last_update": "2024-01-15T10:30:00",
  "last_date": "2024-01-15",
  "minute_records": 1000,
  "daily_records": 30
}
```

## 🚀 **Integration with Application**

### Automatic Fallback:
1. **Application requests TSLA data**
2. **Data loader checks for cached files**
3. **If cached data exists**: Load from files
4. **If no cached data**: Show helpful error message
5. **No automatic API calls** (prevents rate limit issues)

### Error Messages:
- `"Data file not found: TSLA.txt"` → Run cache manager
- `"No TSLA data found"` → Check date range or run cache manager
- `"TSLA data requires alpaca-py"` → Install dependencies

## 📅 **Daily Workflow**

### Recommended Daily Routine:
1. **Morning**: Run `python cache_tsla_data.py` to get fresh data
2. **Throughout Day**: Use application normally (uses cached data)
3. **Evening**: Check status with `python cache_tsla_data.py --status`

### Automated Scheduling (Optional):
```bash
# Add to crontab for daily updates at 9 AM
0 9 * * * cd /path/to/almanac && python cache_tsla_data.py
```

## 🔒 **Security & Best Practices**

### API Credentials:
- Store in environment variables (never in code)
- Use paper trading for development
- Monitor API usage in Alpaca dashboard

### Cache Management:
- Cache files are overwritten daily (no accumulation)
- Metadata tracks usage and prevents duplicate calls
- Graceful degradation if API is unavailable

### Error Handling:
- Network failures don't crash the application
- Clear error messages guide users to solutions
- Fallback to demo data if needed

## 🐛 **Troubleshooting**

### Common Issues:

1. **"No cache data found"**
   - Run: `python cache_tsla_data.py`

2. **"Failed to load TSLA data"**
   - Check API credentials
   - Verify internet connection
   - Check Alpaca API status

3. **"Data file not found"**
   - Cache files don't exist
   - Run cache manager to create them

4. **"Cache is already fresh"**
   - Data was updated today
   - Use `--force` if you need to update anyway

### Debug Mode:
```bash
# Enable debug logging
export PYTHONPATH=.
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from cache_tsla_data import pull_tsla_data_once
pull_tsla_data_once()
"
```

## 📈 **Performance Benefits**

### Speed:
- **Cached data loads instantly** (no API delays)
- **No network requests** during analysis
- **Consistent performance** regardless of API status

### Reliability:
- **Works offline** once data is cached
- **No rate limit issues** with cached data
- **Predictable behavior** for users

### Cost Efficiency:
- **Minimal API usage** (once per day)
- **No repeated requests** for same data
- **Reduced bandwidth** usage

## 🔄 **Data Updates**

### When to Update:
- **Daily**: For current trading data
- **After Market Close**: For complete daily data
- **Before Market Open**: For pre-market analysis

### Update Frequency:
- **Maximum**: Once per day
- **Recommended**: Once per day
- **Minimum**: As needed for analysis

## 📋 **Checklist**

### Before Using TSLA Data:
- [ ] API credentials configured
- [ ] Cache manager run at least once
- [ ] Cache status shows fresh data
- [ ] Data files exist in correct locations

### Daily Maintenance:
- [ ] Run cache manager for fresh data
- [ ] Check cache status
- [ ] Verify data files are updated
- [ ] Test application with TSLA data

### Troubleshooting:
- [ ] Check API credentials
- [ ] Verify internet connection
- [ ] Check Alpaca API status
- [ ] Review error messages
- [ ] Check cache metadata

## 🎯 **Summary**

This cache system provides:
- **Safe API usage** (once per day maximum)
- **Fast data access** (cached files)
- **Reliable operation** (offline capability)
- **Easy maintenance** (simple commands)
- **Clear error handling** (helpful messages)

The system ensures you can use TSLA data in your analysis without risking API restrictions or rate limit issues.
