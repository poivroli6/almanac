# Alpaca API Configuration Guide

## Current Status
✅ **API Key**: `PKVCN0OOHSY4ZP35SUCB` (configured)
❌ **Secret Key**: Missing (needed for TSLA data)

## How to Get Your Alpaca Secret Key

1. **Log into Alpaca**: Go to https://alpaca.markets/
2. **Navigate to API Keys**: 
   - Go to your account dashboard
   - Look for "API Keys" or "Developer" section
3. **Copy Your Secret Key**: It should look similar to your API key but longer
4. **Update Configuration**: Replace `YOUR_SECRET_KEY_HERE` in the code

## Configuration Options

### Option 1: Update the Code Directly
Edit `almanac/data_sources/alpaca_loader.py` line 30:
```python
ALPACA_SECRET_KEY = os.getenv('ALPACA_SECRET_KEY', 'YOUR_ACTUAL_SECRET_KEY')
```

### Option 2: Set Environment Variables
Set these environment variables in your system:
```bash
set ALPACA_API_KEY=PKVCN0OOHSY4ZP35SUCB
set ALPACA_SECRET_KEY=your_actual_secret_key_here
```

### Option 3: Create .env File
Create a `.env` file in your project root:
```
ALPACA_API_KEY=PKVCN0OOHSY4ZP35SUCB
ALPACA_SECRET_KEY=your_actual_secret_key_here
```

## Alternative: Use Yahoo Finance for TSLA

If you don't have the Alpaca secret key, we can modify TSLA to use Yahoo Finance instead:

1. **Pros**: No API credentials needed, free
2. **Cons**: Less real-time data, different data source
3. **Implementation**: Would require modifying the minute_loader.py

## Current Data Sources

- ✅ **BTCUSD**: Working with Yahoo Finance API
- ⚠️ **TSLA**: Waiting for Alpaca secret key
- ✅ **ES, NQ, etc.**: Working with local files

## Next Steps

1. **Get your Alpaca secret key** from your account
2. **Update the configuration** using one of the methods above
3. **Test TSLA data loading** to confirm it works

Once you provide the secret key, TSLA will work just like BTCUSD!
