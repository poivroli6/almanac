"""
Yahoo Finance Data Loader

Loads cryptocurrency data from Yahoo Finance API with caching and error handling.
"""

import pandas as pd
import yfinance as yf
from pathlib import Path
from typing import Optional, Union
from datetime import datetime, timedelta
import pytz
import logging
import os
import json

logger = logging.getLogger(__name__)

# Base directory for data files
DATA_DIR = Path(__file__).parent.parent.parent
CACHE_DIR = DATA_DIR / "cache"
CACHE_DIR.mkdir(exist_ok=True)

# Timezone handling
UTC = pytz.UTC
ET = pytz.timezone('US/Eastern')

# Yahoo Finance symbol mapping
SYMBOL_MAP = {
    'BTCUSD': 'BTC-USD',
    'ETHUSD': 'ETH-USD',
    'ADAUSD': 'ADA-USD',
    'SOLUSD': 'SOL-USD',
    'DOGEUSD': 'DOGE-USD',
    'TSLA': 'TSLA',  # Add TSLA to Yahoo Finance mapping
}


def load_btcusd_minute_data(
    start_date: Union[str, datetime],
    end_date: Union[str, datetime],
    use_cache: bool = True,
    validate: bool = True
) -> pd.DataFrame:
    """
    Load BTCUSD 1-minute data from Yahoo Finance API.
    
    Args:
        start_date: Start date (YYYY-MM-DD or datetime)
        end_date: End date (YYYY-MM-DD or datetime)
        use_cache: Whether to use cached data if available
        validate: Whether to run data quality checks
        
    Returns:
        DataFrame with columns: time, open, high, low, close, volume
        
    Raises:
        ValueError: If no data found or validation fails
        Exception: If API request fails
    """
    # Convert dates to datetime
    if isinstance(start_date, str):
        start_date = pd.Timestamp(start_date)
    if isinstance(end_date, str):
        end_date = pd.Timestamp(end_date)
    
    # Ensure dates are timezone-aware (UTC)
    if start_date.tzinfo is None:
        start_date = UTC.localize(start_date)
    if end_date.tzinfo is None:
        end_date = UTC.localize(end_date)
    
    # Check cache first
    cache_file = CACHE_DIR / f"BTCUSD_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv"
    
    if use_cache and cache_file.exists():
        try:
            logger.info(f"Loading BTCUSD data from cache: {cache_file}")
            df = pd.read_csv(cache_file, parse_dates=['time'])
            df['time'] = pd.to_datetime(df['time'], utc=True)
            
            # Filter by date range (cache might have more data)
            df = df[(df['time'] >= start_date) & (df['time'] <= end_date)]
            
            if not df.empty:
                logger.info(f"Loaded {len(df):,} cached BTCUSD bars from {df['time'].min()} to {df['time'].max()}")
                return df
        except Exception as e:
            logger.warning(f"Failed to load from cache: {e}")
    
    # Load from Yahoo Finance API
    logger.info(f"Loading BTCUSD data from Yahoo Finance API: {start_date} to {end_date}")
    
    try:
        # Create ticker object
        ticker = yf.Ticker('BTC-USD')
        
        # Download data with 1-minute intervals
        # Note: Yahoo Finance has limitations on historical minute data
        # For crypto, we can get up to 7 days of minute data
        data = ticker.history(
            start=start_date,
            end=end_date,
            interval='1m',
            auto_adjust=False,
            prepost=True  # Include pre/post market data (24/7 for crypto)
        )
        
        if data.empty:
            raise ValueError(f"No BTCUSD data found between {start_date} and {end_date}")
        
        # Convert to our standard format
        df = _convert_yfinance_to_standard_format(data)
        
        # Convert UTC to ET for consistency with futures data
        df['time'] = df['time'].dt.tz_convert(ET)
        
        # Cache the data
        if use_cache:
            try:
                cache_df = df.copy()
                cache_df['time'] = cache_df['time'].dt.tz_convert(UTC)
                cache_df.to_csv(cache_file, index=False)
                logger.info(f"Cached BTCUSD data to: {cache_file}")
            except Exception as e:
                logger.warning(f"Failed to cache data: {e}")
        
        if validate:
            df = _validate_crypto_data(df, 'BTCUSD', start_date, end_date)
        
        logger.info(f"Loaded {len(df):,} BTCUSD bars from {df['time'].min()} to {df['time'].max()}")
        
        return df
        
    except Exception as e:
        logger.error(f"Failed to load BTCUSD data from Yahoo Finance: {e}")
        
        # Try to load from cache as fallback
        if cache_file.exists():
            logger.info("Attempting to load from cache as fallback")
            try:
                df = pd.read_csv(cache_file, parse_dates=['time'])
                df['time'] = pd.to_datetime(df['time'], utc=True).dt.tz_convert(ET)
                df = df[(df['time'] >= start_date) & (df['time'] <= end_date)]
                
                if not df.empty:
                    logger.info(f"Loaded {len(df):,} BTCUSD bars from cache fallback")
                    return df
            except Exception as cache_e:
                logger.error(f"Cache fallback also failed: {cache_e}")
        
        raise Exception(f"Failed to load BTCUSD data: {e}")


def load_crypto_minute_data(
    symbol: str,
    start_date: Union[str, datetime],
    end_date: Union[str, datetime],
    use_cache: bool = True,
    validate: bool = True
) -> pd.DataFrame:
    """
    Load cryptocurrency minute data from Yahoo Finance API.
    
    Args:
        symbol: Cryptocurrency symbol (e.g., 'BTCUSD', 'ETHUSD')
        start_date: Start date (YYYY-MM-DD or datetime)
        end_date: End date (YYYY-MM-DD or datetime)
        use_cache: Whether to use cached data if available
        validate: Whether to run data quality checks
        
    Returns:
        DataFrame with columns: time, open, high, low, close, volume
    """
    if symbol not in SYMBOL_MAP:
        raise ValueError(f"Unsupported cryptocurrency symbol: {symbol}. Supported: {list(SYMBOL_MAP.keys())}")
    
    yf_symbol = SYMBOL_MAP[symbol]
    
    # Convert dates to datetime
    if isinstance(start_date, str):
        start_date = pd.Timestamp(start_date)
    if isinstance(end_date, str):
        end_date = pd.Timestamp(end_date)
    
    # Ensure dates are timezone-aware (UTC)
    if start_date.tzinfo is None:
        start_date = UTC.localize(start_date)
    if end_date.tzinfo is None:
        end_date = UTC.localize(end_date)
    
    # Check cache first
    cache_file = CACHE_DIR / f"{symbol}_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv"
    
    if use_cache and cache_file.exists():
        try:
            logger.info(f"Loading {symbol} data from cache: {cache_file}")
            df = pd.read_csv(cache_file, parse_dates=['time'])
            df['time'] = pd.to_datetime(df['time'], utc=True)
            
            # Filter by date range
            df = df[(df['time'] >= start_date) & (df['time'] <= end_date)]
            
            if not df.empty:
                logger.info(f"Loaded {len(df):,} cached {symbol} bars from {df['time'].min()} to {df['time'].max()}")
                return df
        except Exception as e:
            logger.warning(f"Failed to load from cache: {e}")
    
    # Load from Yahoo Finance API
    logger.info(f"Loading {symbol} data from Yahoo Finance API: {start_date} to {end_date}")
    
    try:
        # Create ticker object
        ticker = yf.Ticker(yf_symbol)
        
        # Yahoo Finance limitation: Only 8 days of 1-minute data per request
        # We need to make multiple requests for longer periods
        all_dataframes = []
        current_start = start_date
        
        while current_start < end_date:
            # Calculate end date for this chunk (8 days max)
            chunk_end = min(current_start + timedelta(days=7), end_date)
            
            logger.info(f"Loading {symbol} chunk: {current_start.date()} to {chunk_end.date()}")
            
            # Download data with 1-minute intervals for this chunk
            data = ticker.history(
                start=current_start,
                end=chunk_end,
                interval='1m',
                auto_adjust=False,
                prepost=True  # Include pre/post market data (24/7 for crypto)
            )
            
            if not data.empty:
                # Convert to our standard format
                chunk_df = _convert_yfinance_to_standard_format(data)
                all_dataframes.append(chunk_df)
                logger.info(f"Loaded {len(chunk_df):,} bars for chunk {current_start.date()} to {chunk_end.date()}")
            else:
                logger.warning(f"No data for chunk {current_start.date()} to {chunk_end.date()}")
            
            # Move to next chunk
            current_start = chunk_end
            
            # Small delay to respect rate limits
            import time
            time.sleep(0.1)
        
        if not all_dataframes:
            raise ValueError(f"No {symbol} data found between {start_date} and {end_date}")
        
        # Combine all chunks
        df = pd.concat(all_dataframes, ignore_index=True)
        df = df.sort_values('time').reset_index(drop=True)
        
        # Remove duplicates that might occur at chunk boundaries
        df = df.drop_duplicates(subset=['time'], keep='first')
        
        # Convert UTC to ET for consistency with futures data
        df['time'] = df['time'].dt.tz_convert(ET)
        
        # Cache the data
        if use_cache:
            try:
                cache_df = df.copy()
                cache_df['time'] = cache_df['time'].dt.tz_convert(UTC)
                cache_df.to_csv(cache_file, index=False)
                logger.info(f"Cached {symbol} data to: {cache_file}")
            except Exception as e:
                logger.warning(f"Failed to cache data: {e}")
        
        if validate:
            df = _validate_crypto_data(df, symbol, start_date, end_date)
        
        logger.info(f"Loaded {len(df):,} {symbol} bars from {df['time'].min()} to {df['time'].max()}")
        
        return df
        
    except Exception as e:
        logger.error(f"Failed to load {symbol} data from Yahoo Finance: {e}")
        
        # Try to load from cache as fallback
        if cache_file.exists():
            logger.info("Attempting to load from cache as fallback")
            try:
                df = pd.read_csv(cache_file, parse_dates=['time'])
                df['time'] = pd.to_datetime(df['time'], utc=True).dt.tz_convert(ET)
                df = df[(df['time'] >= start_date) & (df['time'] <= end_date)]
                
                if not df.empty:
                    logger.info(f"Loaded {len(df):,} {symbol} bars from cache fallback")
                    return df
            except Exception as cache_e:
                logger.error(f"Cache fallback also failed: {cache_e}")
        
        raise Exception(f"Failed to load {symbol} data: {e}")


def _convert_yfinance_to_standard_format(data: pd.DataFrame) -> pd.DataFrame:
    """
    Convert Yahoo Finance data to our standard format.
    
    Args:
        data: Raw Yahoo Finance DataFrame
        
    Returns:
        DataFrame with columns: time, open, high, low, close, volume
    """
    df = data.copy()
    
    # Reset index to get DatetimeIndex as column
    df = df.reset_index()
    
    # Rename columns to match our standard format
    df = df.rename(columns={
        'Datetime': 'time',
        'Open': 'open',
        'High': 'high',
        'Low': 'low',
        'Close': 'close',
        'Volume': 'volume'
    })
    
    # Ensure time column is timezone-aware (UTC)
    if df['time'].dt.tz is None:
        df['time'] = df['time'].dt.tz_localize(UTC)
    
    # Select only the columns we need
    df = df[['time', 'open', 'high', 'low', 'close', 'volume']].copy()
    
    # Remove any rows with NaN values
    df = df.dropna()
    
    # Sort by time
    df = df.sort_values('time').reset_index(drop=True)
    
    return df


def _validate_crypto_data(
    df: pd.DataFrame,
    symbol: str,
    start_date: Union[str, datetime],
    end_date: Union[str, datetime]
) -> pd.DataFrame:
    """
    Run data quality checks on cryptocurrency data.
    
    Args:
        df: Raw dataframe from Yahoo Finance
        symbol: Cryptocurrency symbol
        start_date: Start date
        end_date: End date
        
    Returns:
        Validated (and possibly cleaned) DataFrame
        
    Raises:
        ValueError: If critical validation issues found
    """
    issues = []
    
    # Check for nulls
    null_counts = df.isnull().sum()
    if null_counts.any():
        issues.append(f"Found null values: {null_counts[null_counts > 0].to_dict()}")
    
    # Check for duplicate timestamps
    dupes = df[df['time'].duplicated()]
    if not dupes.empty:
        issues.append(f"Found {len(dupes)} duplicate timestamps")
        df = df.drop_duplicates(subset=['time'], keep='first')
    
    # Check for invalid OHLC relationships
    invalid_ohlc = df[
        (df['high'] < df['low']) |
        (df['high'] < df['open']) |
        (df['high'] < df['close']) |
        (df['low'] > df['open']) |
        (df['low'] > df['close'])
    ]
    if not invalid_ohlc.empty:
        issues.append(f"Found {len(invalid_ohlc)} rows with invalid OHLC relationships")
    
    # Check for negative or zero prices
    price_cols = ['open', 'high', 'low', 'close']
    invalid_prices = df[(df[price_cols] <= 0).any(axis=1)]
    if not invalid_prices.empty:
        issues.append(f"Found {len(invalid_prices)} rows with invalid prices (<=0)")
    
    # Check for negative volume
    invalid_volume = df[df['volume'] < 0]
    if not invalid_volume.empty:
        issues.append(f"Found {len(invalid_volume)} rows with negative volume")
    
    # Check time gaps (crypto trades 24/7, so gaps should be minimal)
    df = df.sort_values('time')
    time_diffs = df['time'].diff()
    
    # Report gaps > 5 minutes (unusual for crypto)
    large_gaps = time_diffs[time_diffs > pd.Timedelta(minutes=5)]
    if len(large_gaps) > 10:  # More than 10 gaps >5min is unusual for crypto
        issues.append(
            f"Found {len(large_gaps)} time gaps >5min (unusual for 24/7 crypto trading)"
        )
    
    # Log issues but don't fail unless critical
    if issues:
        logger.warning(f"Data quality warnings for {symbol} ({start_date} to {end_date}):")
        for issue in issues:
            logger.warning(f"  - {issue}")
    
    return df


def get_crypto_data_summary(
    symbol: str,
    start_date: Union[str, datetime],
    end_date: Union[str, datetime]
) -> dict:
    """
    Get summary statistics about available crypto data without loading it all.
    
    Args:
        symbol: Cryptocurrency symbol
        start_date: Start date
        end_date: End date
        
    Returns:
        Dictionary with summary stats
    """
    try:
        # Try to load a small sample to get summary info
        sample_end = min(
            pd.Timestamp(end_date),
            pd.Timestamp(start_date) + timedelta(days=1)
        )
        
        df = load_crypto_minute_data(symbol, start_date, sample_end, use_cache=True, validate=False)
        
        return {
            'row_count': len(df),
            'first_timestamp': df['time'].min(),
            'last_timestamp': df['time'].max(),
            'distinct_days': df['time'].dt.date.nunique(),
            'avg_volume': df['volume'].mean(),
            'price_range': {
                'min': df[['open', 'high', 'low', 'close']].min().min(),
                'max': df[['open', 'high', 'low', 'close']].max().max()
            }
        }
    except Exception as e:
        logger.error(f"Failed to get summary for {symbol}: {e}")
        return {}


def clear_crypto_cache(symbol: Optional[str] = None):
    """
    Clear cached cryptocurrency data.
    
    Args:
        symbol: Specific symbol to clear cache for, or None to clear all crypto cache
    """
    if symbol:
        pattern = f"{symbol}_*.csv"
    else:
        pattern = "*_*.csv"  # All cached files
    
    cache_files = list(CACHE_DIR.glob(pattern))
    
    for cache_file in cache_files:
        try:
            cache_file.unlink()
            logger.info(f"Cleared cache file: {cache_file}")
        except Exception as e:
            logger.error(f"Failed to clear cache file {cache_file}: {e}")
    
    logger.info(f"Cleared {len(cache_files)} cache files")


def is_crypto_symbol(symbol: str) -> bool:
    """
    Check if a symbol is a cryptocurrency.
    
    Args:
        symbol: Symbol to check
        
    Returns:
        True if symbol is a cryptocurrency
    """
    return symbol.upper() in SYMBOL_MAP


def get_available_crypto_symbols() -> list[str]:
    """
    Get list of available cryptocurrency symbols.
    
    Returns:
        List of cryptocurrency symbols
    """
    return list(SYMBOL_MAP.keys())
