"""
Minute Data Loader

Loads and validates 1-minute intraday data from files or database.
"""

import pandas as pd
from typing import Optional
from datetime import datetime
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Base directory for data files
DATA_DIR = Path(__file__).parent.parent.parent

try:
    from sqlalchemy import text
    HAS_SQLALCHEMY = True
except ImportError:
    HAS_SQLALCHEMY = False

from .file_loader import load_minute_data_from_file
from .yfinance_loader import is_crypto_symbol, load_crypto_minute_data


def load_minute_data(
    product: str,
    start_date: str | datetime,
    end_date: str | datetime,
    interval: str = "1min",
    validate: bool = True,
    use_files: bool = True
) -> pd.DataFrame:
    """
    Load minute-level intraday data from files or database.
    
    Tries file-based loading first, falls back to database if files not available.
    For TSLA, uses Alpaca API with caching.
    For cryptocurrencies, uses Yahoo Finance API with caching.
    
    Args:
        product: Contract ID (e.g., 'ES', 'NQ', 'GC', 'TSLA', 'BTCUSD')
        start_date: Start date (YYYY-MM-DD or datetime)
        end_date: End date (YYYY-MM-DD or datetime)
        interval: Time interval (default '1min')
        validate: Whether to run data quality checks
        use_files: Whether to try loading from files first (default True)
        
    Returns:
        DataFrame with columns: time, open, high, low, close, volume
        
    Raises:
        ValueError: If no data found or validation fails
    """
    # Handle TSLA data via cached files or Alpaca API
    if product == 'TSLA':
        try:
            # First try to load from cached file
            if use_files:
                try:
                    return load_minute_data_from_file(product, start_date, end_date, validate)
                except Exception as e:
                    logger.warning(f"Failed to load TSLA minute from cache: {e}")
            
            # If no cached data, try Alpaca API
            try:
                from .alpaca_loader import load_tsla_minute_data, validate_tsla_data
                df = load_tsla_minute_data(start_date, end_date, use_cache=False, save_cache=True)
                if validate:
                    if not validate_tsla_data(df):
                        raise ValueError("TSLA data validation failed")
                return df
            except ImportError:
                raise ValueError("TSLA data requires alpaca-py. Install with: pip install alpaca-py>=0.20.0")
            except Exception as e:
                raise ValueError(f"Failed to load TSLA data: {e}")
            
        except Exception as e:
            raise ValueError(f"Failed to load TSLA data: {e}")
    
    # Handle cryptocurrency data via Yahoo Finance API
    if is_crypto_symbol(product):
        # Check if local file exists first (for cached data)
        file_path = DATA_DIR / "1min" / f"{product}.txt"
        if file_path.exists():
            try:
                logger.info(f"Loading {product} from cached file: {file_path}")
                return load_minute_data_from_file(product, start_date, end_date, validate)
            except Exception as e:
                logger.warning(f"Failed to load {product} from cache, using API: {e}")
        
        # Fallback to API if no cached file
        try:
            df = load_crypto_minute_data(product, start_date, end_date, validate=validate)
            return df
        except Exception as e:
            raise ValueError(f"Failed to load {product} data: {e}")
    
    # Try file-based loading first for other products
    if use_files:
        try:
            return load_minute_data_from_file(product, start_date, end_date, validate)
        except Exception as e:
            print(f"File loading failed, trying database: {e}")
    
    # Fallback to database
    if not HAS_SQLALCHEMY:
        raise ImportError(
            "SQLAlchemy is required for database fallback. "
            "Install it with: pip install sqlalchemy pyodbc"
        )
    
    from .db_config import get_engine
    engine = get_engine()
    
    # Convert dates to strings if needed
    if isinstance(start_date, datetime):
        start_date = start_date.strftime("%Y-%m-%d")
    if isinstance(end_date, datetime):
        end_date = end_date.strftime("%Y-%m-%d")
    
    sql = text("""
        SELECT [time], [open], [high], [low], [close], [volume]
        FROM dbo.RawIntradayData
        WHERE contract_id = :prod
          AND interval = :interval
          AND [time] BETWEEN :start AND :end
        ORDER BY [time]
    """)
    
    df = pd.read_sql(
        sql,
        engine,
        params={
            'prod': product,
            'interval': interval,
            'start': f"{start_date} 00:00:00",
            'end': f"{end_date} 23:59:59"
        },
        parse_dates=['time']
    )
    
    if df.empty:
        raise ValueError(
            f"No minute data found for {product} between {start_date} and {end_date}"
        )
    
    if validate:
        df = _validate_minute_data(df, product, start_date, end_date)
    
    return df


def _validate_minute_data(
    df: pd.DataFrame,
    product: str,
    start_date: str,
    end_date: str
) -> pd.DataFrame:
    """
    Run data quality checks on minute data.
    
    Args:
        df: Raw dataframe from database
        product: Product code
        start_date: Start date string
        end_date: End date string
        
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
    
    # Check time gaps (expect 1-minute intervals within sessions)
    df = df.sort_values('time')
    time_diffs = df['time'].diff()
    
    # Report gaps > 5 minutes (likely session breaks, which are OK)
    large_gaps = time_diffs[time_diffs > pd.Timedelta(minutes=5)]
    if len(large_gaps) > 100:  # Excessive gaps might indicate problems
        issues.append(
            f"Found {len(large_gaps)} time gaps >5min (might indicate missing data)"
        )
    
    # Log issues but don't fail unless critical
    if issues:
        print(f"Data quality warnings for {product} ({start_date} to {end_date}):")
        for issue in issues:
            print(f"  - {issue}")
    
    return df


def get_minute_data_summary(
    product: str,
    start_date: str,
    end_date: str
) -> dict:
    """
    Get summary statistics about available minute data without loading it all.
    
    Args:
        product: Contract ID
        start_date: Start date
        end_date: End date
        
    Returns:
        Dictionary with summary stats
    """
    engine = get_engine()
    
    sql = text("""
        SELECT 
            COUNT(*) as row_count,
            MIN([time]) as first_timestamp,
            MAX([time]) as last_timestamp,
            COUNT(DISTINCT CAST([time] AS DATE)) as distinct_days
        FROM dbo.RawIntradayData
        WHERE contract_id = :prod
          AND interval = '1min'
          AND [time] BETWEEN :start AND :end
    """)
    
    result = pd.read_sql(
        sql,
        engine,
        params={
            'prod': product,
            'start': f"{start_date} 00:00:00",
            'end': f"{end_date} 23:59:59"
        }
    )
    
    return result.iloc[0].to_dict() if not result.empty else {}

