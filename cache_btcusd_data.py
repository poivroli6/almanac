#!/usr/bin/env python3
"""
BTCUSD Cache Manager

Downloads and caches BTCUSD data from Yahoo Finance API to local files.
This allows BTCUSD to work like traditional futures data (fast file-based loading).
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from almanac.data_sources.yfinance_loader import load_crypto_minute_data
from almanac.data_sources.file_loader import save_minute_data_to_file

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Cache configuration
CACHE_DIR = Path(__file__).parent
BTCUSD_MINUTE_FILE = CACHE_DIR / "1min" / "BTCUSD.txt"
BTCUSD_DAILY_FILE = CACHE_DIR / "daily" / "BTCUSD_daily.txt"
CACHE_METADATA_FILE = CACHE_DIR / "cache" / "btcusd_cache_metadata.json"

# Ensure cache directory exists
(CACHE_DIR / "cache").mkdir(exist_ok=True)
(CACHE_DIR / "1min").mkdir(exist_ok=True)
(CACHE_DIR / "daily").mkdir(exist_ok=True)


def get_cache_metadata():
    """Get cache metadata if it exists."""
    if CACHE_METADATA_FILE.exists():
        try:
            with open(CACHE_METADATA_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to read cache metadata: {e}")
    return None


def save_cache_metadata(metadata):
    """Save cache metadata."""
    try:
        with open(CACHE_METADATA_FILE, 'w') as f:
            json.dump(metadata, f, indent=2)
        logger.info(f"Cache metadata saved to {CACHE_METADATA_FILE}")
    except Exception as e:
        logger.error(f"Failed to save cache metadata: {e}")


def is_cache_fresh():
    """Check if cache is fresh (less than 24 hours old)."""
    metadata = get_cache_metadata()
    if not metadata:
        return False
    
    last_update = datetime.fromisoformat(metadata.get('last_update', '1970-01-01'))
    return datetime.now() - last_update < timedelta(hours=24)


def download_btcusd_data(days_back=30):
    """Download BTCUSD data from Yahoo Finance API."""
    logger.info(f"Downloading BTCUSD data for last {days_back} days...")
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    
    try:
        # Load minute data from Yahoo Finance
        df_minute = load_crypto_minute_data('BTCUSD', start_date, end_date, validate=True)
        
        if df_minute.empty:
            raise ValueError("No BTCUSD data downloaded")
        
        logger.info(f"Downloaded {len(df_minute):,} minute records")
        logger.info(f"Date range: {df_minute['time'].min()} to {df_minute['time'].max()}")
        
        return df_minute
        
    except Exception as e:
        logger.error(f"Failed to download BTCUSD data: {e}")
        raise


def download_btcusd_daily_data(years_back=5):
    """Download BTCUSD daily data from Yahoo Finance API."""
    logger.info(f"Downloading BTCUSD daily data for last {years_back} years...")
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=years_back * 365)
    
    try:
        import yfinance as yf
        
        # Create ticker object
        ticker = yf.Ticker('BTC-USD')
        
        # Download daily data
        data = ticker.history(
            start=start_date,
            end=end_date,
            interval='1d',  # Daily data
            auto_adjust=False,
            prepost=True
        )
        
        if data.empty:
            raise ValueError("No BTCUSD daily data downloaded")
        
        # Convert to our standard format
        df = data.copy()
        df = df.reset_index()
        
        logger.info(f"Available columns: {list(df.columns)}")
        
        # Rename columns to match our standard format
        df = df.rename(columns={
            'Datetime': 'time',
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume'
        })
        
        # Handle different column names that might exist
        if 'time' not in df.columns and 'Date' in df.columns:
            df = df.rename(columns={'Date': 'time'})
        
        logger.info(f"Columns after rename: {list(df.columns)}")
        
        # Ensure time column is timezone-aware (UTC)
        if df['time'].dt.tz is None:
            df['time'] = df['time'].dt.tz_localize('UTC')
        
        # Convert UTC to ET for consistency
        df['time'] = df['time'].dt.tz_convert('US/Eastern')
        
        # Add date column
        df['date'] = df['time'].dt.date
        
        # Select only the columns we need
        df = df[['date', 'time', 'open', 'high', 'low', 'close', 'volume']].copy()
        
        # Remove any rows with NaN values
        df = df.dropna()
        
        # Sort by date
        df = df.sort_values('date').reset_index(drop=True)
        
        logger.info(f"Downloaded {len(df):,} daily records")
        logger.info(f"Date range: {df['date'].min()} to {df['date'].max()}")
        
        return df
        
    except Exception as e:
        logger.error(f"Failed to download BTCUSD daily data: {e}")
        raise


def save_minute_data(df_minute):
    """Save minute data to file in standard format."""
    logger.info(f"Saving {len(df_minute):,} minute records to {BTCUSD_MINUTE_FILE}")
    
    try:
        # Save to file using the standard format
        save_minute_data_to_file(df_minute, 'BTCUSD', BTCUSD_MINUTE_FILE)
        logger.info(f"Minute data saved successfully")
        
    except Exception as e:
        logger.error(f"Failed to save minute data: {e}")
        raise


def generate_daily_data(df_minute):
    """Generate daily data from minute data."""
    logger.info("Generating daily data from minute data...")
    
    try:
        # Convert to daily OHLCV
        df_minute['date'] = df_minute['time'].dt.date
        
        daily_data = df_minute.groupby('date').agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        }).reset_index()
        
        # Add derived fields
        daily_data['is_green'] = daily_data['close'] > daily_data['open']
        daily_data['is_red'] = daily_data['close'] < daily_data['open']
        daily_data['day_return'] = (daily_data['close'] - daily_data['open']) / daily_data['open']
        daily_data['day_return_pct'] = daily_data['day_return'] * 100
        daily_data['range'] = daily_data['high'] - daily_data['low']
        daily_data['range_pct'] = (daily_data['range'] / daily_data['open']) * 100
        
        logger.info(f"Generated {len(daily_data)} daily records")
        return daily_data
        
    except Exception as e:
        logger.error(f"Failed to generate daily data: {e}")
        raise


def save_daily_data(df_daily):
    """Save daily data to file."""
    logger.info(f"Saving {len(df_daily)} daily records to {BTCUSD_DAILY_FILE}")
    
    try:
        # Format for daily file (Date,Open,High,Low,Close,Volume)
        df_save = df_daily[['date', 'open', 'high', 'low', 'close', 'volume']].copy()
        df_save['date'] = df_save['date'].apply(lambda d: d.strftime('%m/%d/%Y'))
        
        # Save to CSV without header
        df_save.to_csv(BTCUSD_DAILY_FILE, index=False, header=False)
        logger.info(f"Daily data saved successfully")
        
    except Exception as e:
        logger.error(f"Failed to save daily data: {e}")
        raise


def update_cache(force=False):
    """Update BTCUSD cache."""
    if not force and is_cache_fresh():
        logger.info("Cache is fresh, no update needed")
        return
    
    logger.info("Updating BTCUSD cache...")
    
    try:
        # Download minute data (last 30 days)
        df_minute = download_btcusd_data()
        
        # Download daily data (last 5 years)
        df_daily = download_btcusd_daily_data()
        
        # Save minute data
        save_minute_data(df_minute)
        
        # Save daily data
        save_daily_data(df_daily)
        
        # Update metadata
        metadata = {
            'last_update': datetime.now().isoformat(),
            'minute_records': len(df_minute),
            'daily_records': len(df_daily),
            'minute_date_range': {
                'start': df_minute['time'].min().isoformat(),
                'end': df_minute['time'].max().isoformat()
            },
            'daily_date_range': {
                'start': df_daily['date'].min().isoformat(),
                'end': df_daily['date'].max().isoformat()
            },
            'price_range': {
                'min': float(min(df_minute['low'].min(), df_daily['low'].min())),
                'max': float(max(df_minute['high'].max(), df_daily['high'].max()))
            }
        }
        save_cache_metadata(metadata)
        
        logger.info("✅ BTCUSD cache updated successfully!")
        
    except Exception as e:
        logger.error(f"❌ Failed to update BTCUSD cache: {e}")
        raise


def show_cache_status():
    """Show current cache status."""
    metadata = get_cache_metadata()
    
    print("\n" + "="*60)
    print("BTCUSD CACHE STATUS")
    print("="*60)
    
    if not metadata:
        print("❌ No cache metadata found")
        print("💡 Run: python cache_btcusd_data.py --update")
        return
    
    last_update = datetime.fromisoformat(metadata['last_update'])
    is_fresh = datetime.now() - last_update < timedelta(hours=24)
    
    print(f"📅 Last Update: {last_update.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔄 Cache Status: {'✅ Fresh' if is_fresh else '⚠️ Stale'}")
    print(f"📊 Minute Records: {metadata['minute_records']:,}")
    print(f"📈 Daily Records: {metadata['daily_records']:,}")
    
    # Show date ranges
    if 'minute_date_range' in metadata:
        minute_range = metadata['minute_date_range']
        print(f"📅 Minute Range: {minute_range['start'][:10]} to {minute_range['end'][:10]}")
    
    if 'daily_date_range' in metadata:
        daily_range = metadata['daily_date_range']
        print(f"📅 Daily Range: {daily_range['start'][:10]} to {daily_range['end'][:10]}")
    elif 'date_range' in metadata:
        # Legacy format
        date_range = metadata['date_range']
        print(f"📅 Date Range: {date_range['start'][:10]} to {date_range['end'][:10]}")
    
    price_range = metadata['price_range']
    print(f"💰 Price Range: ${price_range['min']:,.2f} - ${price_range['max']:,.2f}")
    
    # Check if files exist
    minute_exists = BTCUSD_MINUTE_FILE.exists()
    daily_exists = BTCUSD_DAILY_FILE.exists()
    
    print(f"\n📁 Files:")
    print(f"   Minute Data: {'✅' if minute_exists else '❌'} {BTCUSD_MINUTE_FILE}")
    print(f"   Daily Data:  {'✅' if daily_exists else '❌'} {BTCUSD_DAILY_FILE}")
    
    if not minute_exists or not daily_exists:
        print("\n💡 Run: python cache_btcusd_data.py --update")


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='BTCUSD Cache Manager')
    parser.add_argument('--update', action='store_true', help='Update cache')
    parser.add_argument('--force', action='store_true', help='Force update even if cache is fresh')
    parser.add_argument('--status', action='store_true', help='Show cache status')
    
    args = parser.parse_args()
    
    if args.status:
        show_cache_status()
    elif args.update:
        update_cache(force=args.force)
    else:
        # Default: show status
        show_cache_status()


if __name__ == "__main__":
    main()
