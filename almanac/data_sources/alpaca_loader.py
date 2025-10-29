"""
Alpaca API Data Loader

Loads stock data from Alpaca API with caching and error handling.
Supports TSLA and other stocks with 1-minute bar data.
"""

import pandas as pd
import os
import logging
from datetime import datetime, timedelta, date
from typing import Optional, Dict, Any
import pytz

try:
    from alpaca.data.historical import StockHistoricalDataClient
    from alpaca.data.requests import StockBarsRequest
    from alpaca.data.timeframe import TimeFrame
    from alpaca.common.exceptions import APIError
    HAS_ALPACA = True
except ImportError:
    HAS_ALPACA = False

# from .file_loader import save_minute_data_to_file  # Function doesn't exist

logger = logging.getLogger(__name__)

# Alpaca API Configuration
ALPACA_API_KEY = os.getenv('ALPACA_API_KEY', 'PKVCN0OOHSY4ZP35SUCB')
ALPACA_SECRET_KEY = os.getenv('ALPACA_SECRET_KEY', 'FgHoVnAAYvRwjfGPzr7HbimScDWTrGaTzcBpKS8gCJ7L')
ALPACA_BASE_URL = os.getenv('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets/v2')

# Cache directory for TSLA data
CACHE_DIR = os.path.join(os.path.dirname(__file__), '..', '..', '1min')
TSLA_CACHE_FILE = os.path.join(CACHE_DIR, 'TSLA.txt')

# TSLA trading hours (9:30 AM - 4:00 PM ET)
TSLA_TRADING_START = 9.5  # 9:30 AM in decimal hours
TSLA_TRADING_END = 16.0   # 4:00 PM in decimal hours
ET_TIMEZONE = pytz.timezone('US/Eastern')


def get_alpaca_client() -> Optional[Any]:
    """
    Initialize and return Alpaca API client.
    
    Returns:
        Alpaca client instance or None if not configured
    """
    if not HAS_ALPACA:
        logger.warning("alpaca-py not installed. Install with: pip install alpaca-py>=0.20.0")
        return None
    
    if not ALPACA_API_KEY or not ALPACA_SECRET_KEY:
        logger.warning("Alpaca API credentials not configured. Set ALPACA_API_KEY and ALPACA_SECRET_KEY environment variables.")
        return None
    
    try:
        client = StockHistoricalDataClient(
            api_key=ALPACA_API_KEY,
            secret_key=ALPACA_SECRET_KEY
        )
        return client
    except Exception as e:
        logger.error(f"Failed to initialize Alpaca client: {e}")
        return None


def convert_alpaca_to_standard_format(bars_data: Any) -> pd.DataFrame:
    """
    Convert Alpaca bars data to standard format matching existing futures data.
    
    Args:
        bars_data: Alpaca bars response data
        
    Returns:
        DataFrame with columns: time, open, high, low, close, volume
    """
    if not bars_data or not hasattr(bars_data, 'df'):
        return pd.DataFrame()
    
    df = bars_data.df.copy()
    
    # Reset index to get timestamp as column
    df = df.reset_index()
    
    # Rename columns to match standard format
    df = df.rename(columns={
        'timestamp': 'time',
        'open': 'open',
        'high': 'high', 
        'low': 'low',
        'close': 'close',
        'volume': 'volume'
    })
    
    # Convert timestamp to ET timezone
    if 'time' in df.columns:
        df['time'] = df['time'].dt.tz_convert(ET_TIMEZONE)
    
    # Filter to trading hours only (9:30 AM - 4:00 PM ET)
    if 'time' in df.columns:
        df['hour'] = df['time'].dt.hour + df['time'].dt.minute / 60.0
        df = df[(df['hour'] >= TSLA_TRADING_START) & (df['hour'] <= TSLA_TRADING_END)]
        df = df.drop('hour', axis=1)
    
    # Ensure proper column order
    expected_columns = ['time', 'open', 'high', 'low', 'close', 'volume']
    df = df[expected_columns]
    
    return df


def load_tsla_minute_data(
    start_date: str | datetime,
    end_date: str | datetime,
    use_cache: bool = True,
    save_cache: bool = True
) -> pd.DataFrame:
    """
    Load TSLA 1-minute data from Alpaca API with caching.
    
    Args:
        start_date: Start date (YYYY-MM-DD or datetime)
        end_date: End date (YYYY-MM-DD or datetime)  
        use_cache: Whether to use cached data if available
        save_cache: Whether to save data to cache file
        
    Returns:
        DataFrame with TSLA minute data in standard format
        
    Raises:
        ValueError: If no data found or API fails
    """
    # Convert string dates to datetime
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    elif hasattr(start_date, 'year') and hasattr(start_date, 'month') and hasattr(start_date, 'day'):
        # Handle date objects
        start_date = datetime.combine(start_date, datetime.min.time())
    
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    elif hasattr(end_date, 'year') and hasattr(end_date, 'month') and hasattr(end_date, 'day'):
        # Handle date objects
        end_date = datetime.combine(end_date, datetime.min.time())
    
    # Ensure dates are timezone-aware (ET)
    if start_date.tzinfo is None:
        start_date = ET_TIMEZONE.localize(start_date)
    if end_date.tzinfo is None:
        end_date = ET_TIMEZONE.localize(end_date)
    
    logger.info(f"Loading TSLA data from {start_date.date()} to {end_date.date()}")
    
    # Try to load from cache first
    if use_cache and os.path.exists(TSLA_CACHE_FILE):
        try:
            cached_df = load_from_cache_file(start_date, end_date)
            if not cached_df.empty:
                logger.info(f"Loaded {len(cached_df)} TSLA records from cache")
                return cached_df
        except Exception as e:
            logger.warning(f"Failed to load from cache: {e}")
    
    # Load from Alpaca API
    client = get_alpaca_client()
    if not client:
        raise ValueError("Alpaca API client not available. Check credentials and installation.")
    
    try:
        # Create request for TSLA bars
        request_params = StockBarsRequest(
            symbol_or_symbols=["TSLA"],
            timeframe=TimeFrame.Minute,
            start=start_date,
            end=end_date,
            adjustment='raw'  # Unadjusted prices
        )
        
        # Fetch data from Alpaca
        bars = client.get_stock_bars(request_params)
        
        # Convert to standard format
        df = convert_alpaca_to_standard_format(bars)
        
        if df.empty:
            raise ValueError(f"No TSLA data found for date range {start_date.date()} to {end_date.date()}")
        
        logger.info(f"Loaded {len(df)} TSLA records from Alpaca API")
        
        # Save to cache if requested
        if save_cache and not df.empty:
            try:
                save_to_cache_file(df)
                logger.info("TSLA data saved to cache")
            except Exception as e:
                logger.warning(f"Failed to save to cache: {e}")
        
        return df
        
    except APIError as e:
        logger.error(f"Alpaca API error: {e}")
        raise ValueError(f"Failed to fetch TSLA data from Alpaca API: {e}")
    except Exception as e:
        logger.error(f"Unexpected error loading TSLA data: {e}")
        raise ValueError(f"Failed to load TSLA data: {e}")


def load_from_cache_file(start_date: datetime, end_date: datetime) -> pd.DataFrame:
    """
    Load TSLA data from cache file for the specified date range.
    
    Args:
        start_date: Start date
        end_date: End date
        
    Returns:
        DataFrame with cached TSLA data
    """
    if not os.path.exists(TSLA_CACHE_FILE):
        return pd.DataFrame()
    
    try:
        # Read cache file
        df = pd.read_csv(TSLA_CACHE_FILE, 
                        names=['date', 'time', 'open', 'high', 'low', 'close', 'volume'],
                        parse_dates=[['date', 'time']])
        
        # Combine date and time columns
        df['datetime'] = pd.to_datetime(df['date_time'])
        df = df.drop(['date_time'], axis=1)
        
        # Filter by date range
        df = df[(df['datetime'] >= start_date) & (df['datetime'] <= end_date)]
        
        # Rename datetime to time for consistency
        df = df.rename(columns={'datetime': 'time'})
        
        return df
        
    except Exception as e:
        logger.error(f"Error reading cache file: {e}")
        return pd.DataFrame()


def save_to_cache_file(df: pd.DataFrame) -> None:
    """
    Save TSLA data to cache file in the same format as existing futures data.
    
    Args:
        df: DataFrame with TSLA data
    """
    if df.empty:
        return
    
    try:
        # Ensure cache directory exists
        os.makedirs(CACHE_DIR, exist_ok=True)
        
        # Convert to the same format as existing data files
        df_cache = df.copy()
        
        # Format datetime for file output (MM/DD/YYYY,HH:MM format)
        df_cache['date'] = df_cache['time'].dt.strftime('%m/%d/%Y')
        df_cache['time'] = df_cache['time'].dt.strftime('%H:%M')
        
        # Reorder columns to match existing format
        df_cache = df_cache[['date', 'time', 'open', 'high', 'low', 'close', 'volume']]
        
        # Append to cache file (don't overwrite existing data)
        df_cache.to_csv(TSLA_CACHE_FILE, mode='a', header=False, index=False)
        
    except Exception as e:
        logger.error(f"Error saving to cache file: {e}")
        raise


def validate_tsla_data(df: pd.DataFrame) -> bool:
    """
    Validate TSLA data format and quality.
    
    Args:
        df: DataFrame to validate
        
    Returns:
        True if data is valid, False otherwise
    """
    if df.empty:
        logger.warning("TSLA data is empty")
        return False
    
    required_columns = ['time', 'open', 'high', 'low', 'close', 'volume']
    if not all(col in df.columns for col in required_columns):
        logger.error(f"TSLA data missing required columns. Found: {df.columns.tolist()}")
        return False
    
    # Check for negative prices
    price_columns = ['open', 'high', 'low', 'close']
    for col in price_columns:
        if (df[col] <= 0).any():
            logger.warning(f"TSLA data contains non-positive prices in {col}")
            return False
    
    # Check for negative volume
    if (df['volume'] < 0).any():
        logger.warning("TSLA data contains negative volume")
        return False
    
    # Check OHLC relationships (high should be >= all others, low should be <= all others)
    invalid_ohlc = (
        (df['high'] < df['low']) | 
        (df['high'] < df['open']) | 
        (df['high'] < df['close']) | 
        (df['low'] > df['open']) | 
        (df['low'] > df['close'])
    )
    if invalid_ohlc.any():
        logger.warning("TSLA data contains invalid OHLC relationships")
        return False
    
    logger.info(f"TSLA data validation passed: {len(df)} records")
    return True


def get_tsla_trading_hours() -> Dict[str, Any]:
    """
    Get TSLA trading hours information.
    
    Returns:
        Dictionary with trading hours information
    """
    return {
        'start_time': '09:30',
        'end_time': '16:00',
        'timezone': 'US/Eastern',
        'start_hour': TSLA_TRADING_START,
        'end_hour': TSLA_TRADING_END,
        'description': 'Regular market hours (9:30 AM - 4:00 PM ET)'
    }


def is_tsla_trading_time(dt: datetime) -> bool:
    """
    Check if the given datetime is within TSLA trading hours.
    
    Args:
        dt: Datetime to check
        
    Returns:
        True if within trading hours, False otherwise
    """
    if dt.tzinfo is None:
        dt = ET_TIMEZONE.localize(dt)
    else:
        dt = dt.astimezone(ET_TIMEZONE)
    
    # Check if it's a weekday
    if dt.weekday() >= 5:  # Saturday = 5, Sunday = 6
        return False
    
    # Check if within trading hours
    hour = dt.hour + dt.minute / 60.0
    return TSLA_TRADING_START <= hour <= TSLA_TRADING_END
