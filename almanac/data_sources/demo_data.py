"""
Demo Data Generator

Provides synthetic data for testing without database connection.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def generate_demo_minute_data(product: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Generate synthetic minute data for demo purposes.
    
    Args:
        product: Contract ID (ES, NQ, GC)
        start_date: Start date
        end_date: End date
        
    Returns:
        DataFrame with minute OHLCV data
    """
    # Generate dates (weekdays only)
    dates = pd.bdate_range(start=start_date, end=end_date, freq='B')
    
    # Generate minute timestamps for trading hours (9:30 AM - 4:00 PM)
    all_data = []
    
    # Base price by product
    base_prices = {'ES': 4500, 'NQ': 15000, 'GC': 2000}
    base_price = base_prices.get(product, 100)
    
    np.random.seed(42)
    
    for date in dates:
        # Generate trading hours (9:30 - 16:00)
        times = pd.date_range(
            start=f"{date.date()} 09:30:00",
            end=f"{date.date()} 16:00:00",
            freq='1min'
        )
        
        # Random walk for the day
        n_minutes = len(times)
        returns = np.random.randn(n_minutes) * 0.0001
        price_series = base_price * (1 + returns).cumprod()
        
        for i, time in enumerate(times):
            price = price_series[i]
            volatility = np.abs(np.random.randn()) * price * 0.0005
            
            open_price = price
            close_price = price + np.random.randn() * volatility
            high_price = max(open_price, close_price) + abs(np.random.randn()) * volatility
            low_price = min(open_price, close_price) - abs(np.random.randn()) * volatility
            volume = int(np.random.randint(1000, 10000))
            
            all_data.append({
                'time': time,
                'open': open_price,
                'high': high_price,
                'low': low_price,
                'close': close_price,
                'volume': volume
            })
    
    df = pd.DataFrame(all_data)
    return df


def generate_demo_daily_data(product: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Generate synthetic daily data for demo purposes.
    
    Args:
        product: Contract ID (ES, NQ, GC)
        start_date: Start date
        end_date: End date
        
    Returns:
        DataFrame with daily OHLCV data
    """
    dates = pd.bdate_range(start=start_date, end=end_date, freq='B')
    
    # Base price by product
    base_prices = {'ES': 4500, 'NQ': 15000, 'GC': 2000}
    base_price = base_prices.get(product, 100)
    
    np.random.seed(42)
    
    # Generate daily data
    n_days = len(dates)
    returns = np.random.randn(n_days) * 0.01
    prices = base_price * (1 + returns).cumprod()
    
    data = []
    for i, date in enumerate(dates):
        price = prices[i]
        daily_range = abs(np.random.randn()) * price * 0.02
        
        open_price = price
        close_price = price + np.random.randn() * daily_range * 0.5
        high_price = max(open_price, close_price) + abs(np.random.randn()) * daily_range * 0.5
        low_price = min(open_price, close_price) - abs(np.random.randn()) * daily_range * 0.5
        volume = int(np.random.randint(100000, 500000))
        
        data.append({
            'time': pd.Timestamp(date),
            'date': date.date(),
            'open': open_price,
            'high': high_price,
            'low': low_price,
            'close': close_price,
            'volume': volume
        })
    
    df = pd.DataFrame(data)
    
    # Add derived fields
    df['is_green'] = df['close'] > df['open']
    df['day_return_pct'] = ((df['close'] - df['open']) / df['open']) * 100
    df['volume_sma_10'] = df['volume'].rolling(10, min_periods=1).mean()
    df['weekday'] = df['date'].apply(lambda d: pd.Timestamp(d).day_name())
    
    return df

