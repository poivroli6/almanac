#!/usr/bin/env python3
"""
TSLA Data Cache Manager

This script pulls TSLA data once per day and stores it locally to avoid API rate limits.
It creates both daily and minute data files in the same format as existing futures data.
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
CACHE_METADATA_FILE = os.path.join(CACHE_DIR, 'tsla_cache_metadata.json')

def get_cache_metadata():
    """Get cache metadata to track when data was last updated."""
    if os.path.exists(CACHE_METADATA_FILE):
        try:
            with open(CACHE_METADATA_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to read cache metadata: {e}")
    
    return {
        'last_update': None,
        'last_date': None,
        'minute_records': 0,
        'daily_records': 0
    }

def update_cache_metadata(minute_records, daily_records, last_date):
    """Update cache metadata."""
    metadata = {
        'last_update': datetime.now().isoformat(),
        'last_date': last_date.isoformat() if isinstance(last_date, date) else last_date,
        'minute_records': minute_records,
        'daily_records': daily_records
    }
    
    try:
        with open(CACHE_METADATA_FILE, 'w') as f:
            json.dump(metadata, f, indent=2)
        logger.info(f"Updated cache metadata: {minute_records} minute records, {daily_records} daily records")
    except Exception as e:
        logger.error(f"Failed to update cache metadata: {e}")

def is_cache_fresh():
    """Check if cache is fresh (updated today)."""
    metadata = get_cache_metadata()
    
    if not metadata.get('last_update'):
        return False
    
    try:
        last_update = datetime.fromisoformat(metadata['last_update'])
        today = datetime.now().date()
        return last_update.date() == today
    except Exception:
        return False

def pull_tsla_data_once():
    """Pull TSLA data once and store it locally."""
    logger.info("Starting TSLA data pull...")
    
    # Check if we already have fresh data
    if is_cache_fresh():
        logger.info("Cache is already fresh for today. Skipping API call.")
        return True
    
    try:
        from almanac.data_sources.alpaca_loader import load_tsla_minute_data
        
        # Determine date range - get last 30 days of trading data
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=45)  # Extra days to account for weekends/holidays
        
        logger.info(f"Pulling TSLA data from {start_date} to {end_date}")
        
        # Load minute data
        minute_df = load_tsla_minute_data(start_date, end_date, use_cache=False, save_cache=False)
        
        if minute_df.empty:
            logger.error("No TSLA minute data received from API")
            return False
        
        logger.info(f"Received {len(minute_df)} minute records")
        
        # Convert to daily data
        daily_df = convert_minute_to_daily(minute_df)
        logger.info(f"Generated {len(daily_df)} daily records")
        
        # Save minute data
        save_minute_data(minute_df)
        
        # Save daily data
        save_daily_data(daily_df)
        
        # Update metadata
        update_cache_metadata(len(minute_df), len(daily_df), end_date)
        
        logger.info("✅ TSLA data successfully cached!")
        return True
        
    except Exception as e:
        logger.error(f"Failed to pull TSLA data: {e}")
        return False

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

def check_cache_status():
    """Check and display cache status."""
    metadata = get_cache_metadata()
    
    print("TSLA Cache Status:")
    print("=" * 30)
    
    if metadata.get('last_update'):
        last_update = datetime.fromisoformat(metadata['last_update'])
        print(f"Last Update: {last_update.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Last Date: {metadata.get('last_date', 'Unknown')}")
        print(f"Minute Records: {metadata.get('minute_records', 0)}")
        print(f"Daily Records: {metadata.get('daily_records', 0)}")
        
        is_fresh = is_cache_fresh()
        print(f"Cache Fresh: {'Yes' if is_fresh else 'No'}")
        
        # Check if files exist
        tsla_file = os.path.join(CACHE_DIR, 'TSLA.txt')
        tsla_daily_file = os.path.join(DAILY_CACHE_DIR, 'TSLA_daily.txt')
        
        print(f"Minute File Exists: {'Yes' if os.path.exists(tsla_file) else 'No'}")
        print(f"Daily File Exists: {'Yes' if os.path.exists(tsla_daily_file) else 'No'}")
        
    else:
        print("No cache data found")

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='TSLA Data Cache Manager')
    parser.add_argument('--status', action='store_true', help='Check cache status')
    parser.add_argument('--force', action='store_true', help='Force update even if cache is fresh')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without actually doing it')
    
    args = parser.parse_args()
    
    if args.status:
        check_cache_status()
        return
    
    if args.dry_run:
        print("DRY RUN MODE")
        print("=" * 20)
        print("This would:")
        print("1. Check if cache is fresh")
        print("2. Pull TSLA data from Alpaca API (if needed)")
        print("3. Save minute data to 1min/TSLA.txt")
        print("4. Save daily data to daily/TSLA_daily.txt")
        print("5. Update cache metadata")
        return
    
    # Check if we need to update
    if not args.force and is_cache_fresh():
        logger.info("Cache is already fresh for today. Use --force to update anyway.")
        check_cache_status()
        return
    
    # Pull data
    success = pull_tsla_data_once()
    
    if success:
        print("\n✅ TSLA data cache updated successfully!")
        check_cache_status()
    else:
        print("\n❌ Failed to update TSLA data cache")
        sys.exit(1)

if __name__ == "__main__":
    main()
