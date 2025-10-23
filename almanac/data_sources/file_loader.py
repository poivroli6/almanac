"""
File-Based Data Loader

Loads data directly from text files (1min/ and daily/ folders).
"""

import pandas as pd
from pathlib import Path
from typing import Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


# Base directory for data files
DATA_DIR = Path(__file__).parent.parent.parent


def load_minute_data_from_file(
    product: str,
    start_date: str | datetime,
    end_date: str | datetime,
    validate: bool = True
) -> pd.DataFrame:
    """
    Load minute-level data from text files.
    
    File format: Date,Time,Open,High,Low,Close,Volume
    Example: 09/27/2009,18:00,1042.25,1043.25,1042.25,1043,1354
    
    Args:
        product: Contract ID (e.g., 'ES', 'NQ', 'GC')
        start_date: Start date (YYYY-MM-DD or datetime)
        end_date: End date (YYYY-MM-DD or datetime)
        validate: Whether to run data quality checks
        
    Returns:
        DataFrame with columns: time, open, high, low, close, volume
        
    Raises:
        ValueError: If file not found or no data in range
    """
    # Convert dates to datetime
    if isinstance(start_date, str):
        start_date = pd.Timestamp(start_date)
    if isinstance(end_date, str):
        end_date = pd.Timestamp(end_date)
    
    # Construct file path
    file_path = DATA_DIR / "1min" / f"{product}.txt"
    
    if not file_path.exists():
        raise ValueError(f"Data file not found: {file_path}")
    
    # Read CSV
    df = pd.read_csv(
        file_path,
        names=['date', 'time_str', 'open', 'high', 'low', 'close', 'volume'],
        parse_dates=False  # We'll handle dates manually
    )
    
    # Combine date and time into datetime
    df['time'] = pd.to_datetime(df['date'] + ' ' + df['time_str'], format='%m/%d/%Y %H:%M')
    
    # Filter by date range
    df = df[(df['time'] >= start_date) & (df['time'] <= end_date)]
    
    if df.empty:
        raise ValueError(
            f"No minute data found for {product} between {start_date} and {end_date}"
        )
    
    # Select and order columns
    df = df[['time', 'open', 'high', 'low', 'close', 'volume']].copy()
    
    # Sort by time
    df = df.sort_values('time').reset_index(drop=True)
    
    if validate:
        print(f"Loaded {len(df):,} minute bars for {product} from {df['time'].min()} to {df['time'].max()}")
    
    return df


def load_daily_data_from_file(
    product: str,
    start_date: str | datetime,
    end_date: str | datetime,
    add_derived_fields: bool = True
) -> pd.DataFrame:
    """
    Load daily OHLCV data from text files.
    
    File format: Date,Open,High,Low,Close,Volume
    Example: 09/09/1997,933.75,941.25,932.75,934,0
    
    Args:
        product: Contract ID (e.g., 'ES', 'NQ', 'GC')
        start_date: Start date (YYYY-MM-DD or datetime)
        end_date: End date (YYYY-MM-DD or datetime)
        add_derived_fields: Whether to add derived fields
        
    Returns:
        DataFrame with columns: date, open, high, low, close, volume
        
    Raises:
        ValueError: If file not found or no data in range
    """
    # Convert dates to datetime
    if isinstance(start_date, str):
        start_date = pd.Timestamp(start_date)
    if isinstance(end_date, str):
        end_date = pd.Timestamp(end_date)
    
    # Construct file path
    file_path = DATA_DIR / "daily" / f"{product}_daily.txt"
    
    if not file_path.exists():
        raise ValueError(f"Data file not found: {file_path}")
    
    # Read CSV
    df = pd.read_csv(
        file_path,
        names=['date_str', 'open', 'high', 'low', 'close', 'volume'],
        parse_dates=False
    )
    
    # Parse dates
    df['time'] = pd.to_datetime(df['date_str'], format='%m/%d/%Y')
    df['date'] = df['time'].dt.date
    
    # Filter by date range
    df = df[(df['time'] >= start_date) & (df['time'] <= end_date)]
    
    if df.empty:
        raise ValueError(
            f"No daily data found for {product} between {start_date} and {end_date}"
        )
    
    # Select columns
    df = df[['date', 'time', 'open', 'high', 'low', 'close', 'volume']].copy()
    
    # Sort by date
    df = df.sort_values('date').reset_index(drop=True)
    
    if add_derived_fields:
        df = _add_derived_fields_file(df)
    
    print(f"Loaded {len(df):,} daily bars for {product} from {df['date'].min()} to {df['date'].max()}")
    
    return df


def _add_derived_fields_file(df: pd.DataFrame) -> pd.DataFrame:
    """Add commonly used derived fields to daily data."""
    df = df.copy()
    
    # Direction
    df['is_green'] = df['close'] > df['open']
    df['is_red'] = df['close'] < df['open']
    
    # Returns
    df['day_return'] = (df['close'] - df['open']) / df['open']
    df['day_return_pct'] = df['day_return'] * 100
    
    # Range
    df['range'] = df['high'] - df['low']
    df['range_pct'] = (df['range'] / df['open']) * 100
    
    # Rolling volumes
    df['volume_sma_10'] = df['volume'].rolling(10, min_periods=1).mean()
    df['volume_sma_20'] = df['volume'].rolling(20, min_periods=1).mean()
    df['relative_volume'] = df['volume'] / df['volume_sma_10']
    
    # Rolling price metrics
    df['atr_14'] = df['range'].rolling(14, min_periods=1).mean()
    
    # Weekday
    df['weekday'] = df['date'].apply(lambda d: pd.Timestamp(d).day_name())
    df['weekday_num'] = df['date'].apply(lambda d: pd.Timestamp(d).weekday())
    
    return df


def get_available_products() -> list[str]:
    """Get list of available products from 1min folder."""
    min_dir = DATA_DIR / "1min"
    if not min_dir.exists():
        return []
    
    products = [f.stem for f in min_dir.glob("*.txt")]
    return sorted(products)


def save_minute_data_to_file(
    df: pd.DataFrame,
    product: str,
    file_path: Optional[Path] = None
) -> Path:
    """
    Save minute data to a text file in the standard format.
    
    Args:
        df: DataFrame with columns: time, open, high, low, close, volume
        product: Product symbol (e.g., 'ES', 'BTCUSD')
        file_path: Optional custom file path
        
    Returns:
        Path to the saved file
    """
    if file_path is None:
        file_path = DATA_DIR / "1min" / f"{product}.txt"
    
    # Ensure directory exists
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Convert DataFrame to the standard format
    df_save = df.copy()
    
    # Format time as MM/DD/YYYY HH:MM
    df_save['date'] = df_save['time'].dt.strftime('%m/%d/%Y')
    df_save['time_str'] = df_save['time'].dt.strftime('%H:%M')
    
    # Select and order columns for output
    output_df = df_save[['date', 'time_str', 'open', 'high', 'low', 'close', 'volume']].copy()
    
    # Save to CSV without header
    output_df.to_csv(file_path, index=False, header=False)
    
    return file_path