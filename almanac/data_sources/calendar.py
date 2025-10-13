"""
Trading Calendar Utilities

Handles trading days, holidays, and session times using exchange calendars.
"""

import pandas as pd
from datetime import date, datetime
from typing import Optional
import warnings

# Try to import pandas_market_calendars, fallback to BDay if not available
try:
    import pandas_market_calendars as mcal
    HAS_MARKET_CALENDARS = True
except ImportError:
    HAS_MARKET_CALENDARS = False
    warnings.warn(
        "pandas_market_calendars not installed. Using BDay approximation. "
        "Install with: pip install pandas-market-calendars",
        ImportWarning
    )


def get_exchange_calendar(exchange: str = "CME"):
    """
    Get trading calendar for specified exchange.
    
    Args:
        exchange: Exchange code (CME, CBOT, NYSE, etc.)
        
    Returns:
        Market calendar instance or None if not available
    """
    if not HAS_MARKET_CALENDARS:
        return None
    
    try:
        return mcal.get_calendar(exchange)
    except Exception:
        # Fallback to CME if specific exchange not found
        return mcal.get_calendar("CME")


def get_previous_trading_day(
    current_date: date | str | pd.Timestamp,
    exchange: str = "CME"
) -> date:
    """
    Get the previous trading day, accounting for holidays and weekends.
    
    Args:
        current_date: Reference date
        exchange: Exchange to use for trading calendar
        
    Returns:
        Previous trading day as date object
    """
    if isinstance(current_date, str):
        current_date = pd.Timestamp(current_date).date()
    elif isinstance(current_date, pd.Timestamp):
        current_date = current_date.date()
    
    if HAS_MARKET_CALENDARS:
        try:
            cal = get_exchange_calendar(exchange)
            # Get valid trading days up to current_date
            schedule = cal.valid_days(
                start_date=pd.Timestamp(current_date) - pd.Timedelta(days=10),
                end_date=pd.Timestamp(current_date)
            )
            
            # Find the previous trading day
            valid_dates = schedule[schedule < pd.Timestamp(current_date)]
            if len(valid_dates) > 0:
                return valid_dates[-1].date()
        except Exception:
            pass
    
    # Fallback: Use business day approximation
    prev = pd.Timestamp(current_date) - pd.tseries.offsets.BDay(1)
    return prev.date()


def is_trading_day(check_date: date | str | pd.Timestamp, exchange: str = "CME") -> bool:
    """
    Check if a given date is a trading day.
    
    Args:
        check_date: Date to check
        exchange: Exchange to use for trading calendar
        
    Returns:
        True if trading day, False otherwise
    """
    if isinstance(check_date, str):
        check_date = pd.Timestamp(check_date)
    elif isinstance(check_date, date):
        check_date = pd.Timestamp(check_date)
    
    if HAS_MARKET_CALENDARS:
        try:
            cal = get_exchange_calendar(exchange)
            schedule = cal.valid_days(start_date=check_date, end_date=check_date)
            return len(schedule) > 0
        except Exception:
            pass
    
    # Fallback: Check if weekday
    return check_date.weekday() < 5


def get_trading_days(
    start_date: date | str | pd.Timestamp,
    end_date: date | str | pd.Timestamp,
    exchange: str = "CME"
) -> pd.DatetimeIndex:
    """
    Get all trading days in a date range.
    
    Args:
        start_date: Start date (inclusive)
        end_date: End date (inclusive)
        exchange: Exchange to use for trading calendar
        
    Returns:
        DatetimeIndex of trading days
    """
    if isinstance(start_date, str):
        start_date = pd.Timestamp(start_date)
    if isinstance(end_date, str):
        end_date = pd.Timestamp(end_date)
    
    if HAS_MARKET_CALENDARS:
        try:
            cal = get_exchange_calendar(exchange)
            return cal.valid_days(start_date=start_date, end_date=end_date)
        except Exception:
            pass
    
    # Fallback: Use business days
    return pd.bdate_range(start=start_date, end=end_date)

