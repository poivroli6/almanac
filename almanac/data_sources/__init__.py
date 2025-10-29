"""
Data Sources Module

Handles all data loading operations with caching and validation.
"""

from .db_config import get_engine
from .minute_loader import load_minute_data
from .daily_loader import load_daily_data
from .weekly_loader import load_weekly_data, get_weekly_day_performance_stats
from .monthly_loader import load_monthly_data
from .calendar import (
    get_exchange_calendar, 
    get_previous_trading_day,
    is_crypto_trading_day,
    get_crypto_trading_days,
    get_previous_crypto_trading_day,
    is_trading_time
)
from .demo_data import generate_demo_minute_data, generate_demo_daily_data
from .yfinance_loader import (
    load_btcusd_minute_data,
    load_crypto_minute_data,
    is_crypto_symbol,
    get_available_crypto_symbols,
    clear_crypto_cache
)
from .alpaca_loader import (
    load_tsla_minute_data,
    validate_tsla_data,
    get_tsla_trading_hours,
    is_tsla_trading_time
)

__all__ = [
    'get_engine',
    'load_minute_data',
    'load_daily_data',
    'load_weekly_data',
    'get_weekly_day_performance_stats',
    'load_monthly_data',
    'get_exchange_calendar',
    'get_previous_trading_day',
    'is_crypto_trading_day',
    'get_crypto_trading_days',
    'get_previous_crypto_trading_day',
    'is_trading_time',
    'generate_demo_minute_data',
    'generate_demo_daily_data',
    'load_btcusd_minute_data',
    'load_crypto_minute_data',
    'is_crypto_symbol',
    'get_available_crypto_symbols',
    'clear_crypto_cache',
    'load_tsla_minute_data',
    'validate_tsla_data',
    'get_tsla_trading_hours',
    'is_tsla_trading_time',
]

