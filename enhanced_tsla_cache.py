#!/usr/bin/env python3
"""
Enhanced TSLA Data Loader

Combines multiple data sources to get comprehensive TSLA data:
- Yahoo Finance: Extensive historical daily data (years of data)
- Alpaca: Recent minute data (last 6-7 weeks)
- Smart merging to avoid duplicates
"""

import os
import sys
import pandas as pd
from datetime import datetime, timedelta, date
import logging
import json

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Cache configuration
CACHE_DIR = os.path.join(os.path.dirname(__file__), '1min')
DAILY_CACHE_DIR = os.path.join(os.path.dirname(__file__), 'daily')
CACHE_METADATA_FILE = os.path.join(CACHE_DIR, 'tsla_enhanced_cache_metadata.json')

def get_yfinance_daily_data(start_date, end_date):
    """Get TSLA daily data from Yahoo Finance."""
    try:
        import yfinance as yf
        
        logger.info(f"Fetching TSLA daily data from Yahoo Finance: {start_date} to {end_date}")
        
        # Download TSLA data
        tsla = yf.Ticker("TSLA")
        hist = tsla.history(start=start_date, end=end_date)
        
        if hist.empty:
            logger.warning("No data received from Yahoo Finance")
            return pd.DataFrame()
        
        # Convert to our standard format
        df = hist.reset_index()
        df = df.rename(columns={
            'Date': 'time',
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume'
        })
        
        # Ensure time column is datetime
        df['time'] = pd.to_datetime(df['time'])
        
        # Select only the columns we need
        df = df[['time', 'open', 'high', 'low', 'close', 'volume']]
        
        logger.info(f"Retrieved {len(df)} daily records from Yahoo Finance")
        return df
        
    except ImportError:
        logger.error("yfinance not installed. Install with: pip install yfinance")
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"Failed to fetch Yahoo Finance data: {e}")
        return pd.DataFrame()

def get_alpaca_minute_data(start_date, end_date):
    """Get TSLA minute data from Alpaca API."""
    try:
        from almanac.data_sources.alpaca_loader import load_tsla_minute_data
        
        logger.info(f"Fetching TSLA minute data from Alpaca: {start_date} to {end_date}")
        
        df = load_tsla_minute_data(start_date, end_date, use_cache=False, save_cache=False)
        
        if df.empty:
            logger.warning("No data received from Alpaca")
            return pd.DataFrame()
        
        logger.info(f"Retrieved {len(df)} minute records from Alpaca")
        return df
        
    except Exception as e:
        logger.error(f"Failed to fetch Alpaca data: {e}")
        return pd.DataFrame()

def convert_minute_to_daily(minute_df):
    """Convert minute data to daily OHLCV format."""
    if minute_df.empty:
        return pd.DataFrame()
    
    # Ensure time column is datetime
    minute_df = minute_df.copy()
    minute_df['time'] = pd.to_datetime(minute_df['time'])
    
    # Group by date and aggregate
    daily_df = minute_df.groupby(minute_df['time'].dt.date).agg({
        'open': 'first',    # First price of the day
        'high': 'max',      # Highest price of the day
        'low': 'min',       # Lowest price of the day
        'close': 'last',    # Last price of the day
        'volume': 'sum'     # Total volume for the day
    }).reset_index()
    
    # Rename date column to time for consistency
    daily_df = daily_df.rename(columns={'time': 'time'})
    
    # Convert date back to datetime
    daily_df['time'] = pd.to_datetime(daily_df['time'])
    
    # Ensure proper column order
    daily_df = daily_df[['time', 'open', 'high', 'low', 'close', 'volume']]
    
    return daily_df

def merge_daily_data(yfinance_df, alpaca_daily_df):
    """Merge daily data from multiple sources, avoiding duplicates."""
    if yfinance_df.empty and alpaca_daily_df.empty:
        return pd.DataFrame()
    
    if yfinance_df.empty:
        return alpaca_daily_df
    
    if alpaca_daily_df.empty:
        return yfinance_df
    
    # Ensure both dataframes have timezone-naive datetime columns
    yfinance_df = yfinance_df.copy()
    alpaca_daily_df = alpaca_daily_df.copy()
    
    # Convert to timezone-naive if needed
    if yfinance_df['time'].dt.tz is not None:
        yfinance_df['time'] = yfinance_df['time'].dt.tz_localize(None)
    
    if alpaca_daily_df['time'].dt.tz is not None:
        alpaca_daily_df['time'] = alpaca_daily_df['time'].dt.tz_localize(None)
    
    # Combine dataframes
    combined_df = pd.concat([yfinance_df, alpaca_daily_df], ignore_index=True)
    
    # Remove duplicates based on date
    combined_df = combined_df.drop_duplicates(subset=['time'], keep='last')
    
    # Sort by date
    combined_df = combined_df.sort_values('time').reset_index(drop=True)
    
    logger.info(f"Merged daily data: {len(combined_df)} unique records")
    return combined_df

def save_minute_data(minute_df):
    """Save minute data to TSLA.txt file."""
    if minute_df.empty:
        return
    
    # Ensure cache directory exists
    os.makedirs(CACHE_DIR, exist_ok=True)
    
    tsla_file = os.path.join(CACHE_DIR, 'TSLA.txt')
    
    try:
        # Convert to the same format as existing data files
        df_save = minute_df.copy()
        
        # Format datetime for file output (MM/DD/YYYY,HH:MM format)
        df_save['date'] = df_save['time'].dt.strftime('%m/%d/%Y')
        df_save['time'] = df_save['time'].dt.strftime('%H:%M')
        
        # Reorder columns to match existing format
        df_save = df_save[['date', 'time', 'open', 'high', 'low', 'close', 'volume']]
        
        # Save to file (overwrite existing)
        df_save.to_csv(tsla_file, header=False, index=False)
        
        logger.info(f"Saved {len(minute_df)} minute records to {tsla_file}")
        
    except Exception as e:
        logger.error(f"Failed to save minute data: {e}")
        raise

def save_daily_data(daily_df):
    """Save daily data to TSLA_daily.txt file."""
    if daily_df.empty:
        return
    
    # Ensure cache directory exists
    os.makedirs(DAILY_CACHE_DIR, exist_ok=True)
    
    tsla_daily_file = os.path.join(DAILY_CACHE_DIR, 'TSLA_daily.txt')
    
    try:
        # Convert to the same format as existing daily data files
        df_save = daily_df.copy()
        
        # Format datetime for file output (MM/DD/YYYY format)
        df_save['date'] = df_save['time'].dt.strftime('%m/%d/%Y')
        df_save['time'] = '00:00'  # Daily data typically has 00:00 time
        
        # Reorder columns to match existing format
        df_save = df_save[['date', 'time', 'open', 'high', 'low', 'close', 'volume']]
        
        # Save to file (overwrite existing)
        df_save.to_csv(tsla_daily_file, header=False, index=False)
        
        logger.info(f"Saved {len(daily_df)} daily records to {tsla_daily_file}")
        
    except Exception as e:
        logger.error(f"Failed to save daily data: {e}")
        raise

def update_cache_metadata(minute_records, daily_records, last_date, sources):
    """Update cache metadata."""
    metadata = {
        'last_update': datetime.now().isoformat(),
        'last_date': last_date.isoformat() if isinstance(last_date, date) else last_date,
        'minute_records': minute_records,
        'daily_records': daily_records,
        'sources': sources,
        'enhanced': True
    }
    
    try:
        with open(CACHE_METADATA_FILE, 'w') as f:
            json.dump(metadata, f, indent=2)
        logger.info(f"Updated enhanced cache metadata: {minute_records} minute records, {daily_records} daily records")
    except Exception as e:
        logger.error(f"Failed to update cache metadata: {e}")

def pull_enhanced_tsla_data():
    """Pull comprehensive TSLA data from multiple sources."""
    logger.info("Starting enhanced TSLA data pull...")
    
    # Define date ranges
    end_date = datetime.now().date()
    
    # Yahoo Finance: Get 2 years of historical daily data
    yfinance_start = end_date - timedelta(days=730)  # 2 years
    
    # Alpaca: Get recent minute data (last 2 months)
    alpaca_start = end_date - timedelta(days=60)  # 2 months
    
    sources_used = []
    
    # Get Yahoo Finance daily data
    logger.info("Fetching historical daily data from Yahoo Finance...")
    yfinance_daily = get_yfinance_daily_data(yfinance_start, end_date)
    if not yfinance_daily.empty:
        sources_used.append("Yahoo Finance (Daily)")
    
    # Get Alpaca minute data
    logger.info("Fetching recent minute data from Alpaca...")
    alpaca_minute = get_alpaca_minute_data(alpaca_start, end_date)
    if not alpaca_minute.empty:
        sources_used.append("Alpaca (Minute)")
    
    # Convert Alpaca minute data to daily
    alpaca_daily = pd.DataFrame()
    if not alpaca_minute.empty:
        alpaca_daily = convert_minute_to_daily(alpaca_minute)
    
    # Merge daily data from both sources
    combined_daily = merge_daily_data(yfinance_daily, alpaca_daily)
    
    if combined_daily.empty:
        logger.error("No data retrieved from any source")
        return False
    
    # Save data
    if not alpaca_minute.empty:
        save_minute_data(alpaca_minute)
    
    if not combined_daily.empty:
        save_daily_data(combined_daily)
    
    # Update metadata
    update_cache_metadata(
        len(alpaca_minute), 
        len(combined_daily), 
        end_date, 
        sources_used
    )
    
    logger.info("✅ Enhanced TSLA data successfully cached!")
    logger.info(f"Sources used: {', '.join(sources_used)}")
    logger.info(f"Total daily records: {len(combined_daily)}")
    logger.info(f"Total minute records: {len(alpaca_minute)}")
    
    return True

def check_enhanced_cache_status():
    """Check and display enhanced cache status."""
    if os.path.exists(CACHE_METADATA_FILE):
        try:
            with open(CACHE_METADATA_FILE, 'r') as f:
                metadata = json.load(f)
        except Exception as e:
            logger.error(f"Failed to read cache metadata: {e}")
            metadata = {}
    else:
        metadata = {}
    
    print("Enhanced TSLA Cache Status:")
    print("=" * 35)
    
    if metadata:
        print(f"Last Update: {metadata.get('last_update', 'Unknown')}")
        print(f"Last Date: {metadata.get('last_date', 'Unknown')}")
        print(f"Minute Records: {metadata.get('minute_records', 0)}")
        print(f"Daily Records: {metadata.get('daily_records', 0)}")
        print(f"Sources: {', '.join(metadata.get('sources', []))}")
        print(f"Enhanced: {metadata.get('enhanced', False)}")
        
        # Check if files exist
        tsla_file = os.path.join(CACHE_DIR, 'TSLA.txt')
        tsla_daily_file = os.path.join(DAILY_CACHE_DIR, 'TSLA_daily.txt')
        
        print(f"Minute File Exists: {'Yes' if os.path.exists(tsla_file) else 'No'}")
        print(f"Daily File Exists: {'Yes' if os.path.exists(tsla_daily_file) else 'No'}")
        
        if os.path.exists(tsla_daily_file):
            # Show date range
            try:
                df = pd.read_csv(tsla_daily_file, names=['date', 'time', 'open', 'high', 'low', 'close', 'volume'])
                df['date'] = pd.to_datetime(df['date'])
                print(f"Daily Data Range: {df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}")
            except Exception as e:
                print(f"Could not read date range: {e}")
    else:
        print("No enhanced cache data found")

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Enhanced TSLA Data Cache Manager')
    parser.add_argument('--status', action='store_true', help='Check enhanced cache status')
    parser.add_argument('--pull', action='store_true', help='Pull enhanced TSLA data')
    
    args = parser.parse_args()
    
    if args.status:
        check_enhanced_cache_status()
        return
    
    if args.pull:
        success = pull_enhanced_tsla_data()
        if success:
            print("\n✅ Enhanced TSLA data cache updated successfully!")
            check_enhanced_cache_status()
        else:
            print("\n❌ Failed to update enhanced TSLA data cache")
            sys.exit(1)
    else:
        print("Enhanced TSLA Data Cache Manager")
        print("=" * 35)
        print("Usage:")
        print("  python enhanced_tsla_cache.py --pull    # Pull comprehensive TSLA data")
        print("  python enhanced_tsla_cache.py --status  # Check cache status")
        print("\nThis will combine:")
        print("- Yahoo Finance: 2 years of historical daily data")
        print("- Alpaca: Recent minute data (last 2 months)")

if __name__ == "__main__":
    main()
