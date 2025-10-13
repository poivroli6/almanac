"""
Economic Events Calendar

Tracks important economic events like CPI, FOMC, NFP, etc.
This module provides functionality to check if a date has a major economic release.
"""

import pandas as pd
from datetime import date, datetime
from typing import Optional, Set, List


# Manually curated list of important economic event dates
# Note: In a production system, this should be loaded from a database or API
# Format: 'YYYY-MM-DD'
ECONOMIC_EVENTS = {
    'CPI': {
        # 2024 CPI Release Dates
        '2024-01-11', '2024-02-13', '2024-03-12', '2024-04-10', '2024-05-15', 
        '2024-06-12', '2024-07-11', '2024-08-14', '2024-09-11', '2024-10-10', 
        '2024-11-13', '2024-12-11',
        # 2025 CPI Release Dates (typical schedule - may need updating)
        '2025-01-15', '2025-02-12', '2025-03-12', '2025-04-10', '2025-05-13',
        '2025-06-11', '2025-07-10', '2025-08-13', '2025-09-10', '2025-10-14',
        '2025-11-12', '2025-12-10',
        # 2023 CPI Release Dates
        '2023-01-12', '2023-02-14', '2023-03-14', '2023-04-12', '2023-05-10',
        '2023-06-13', '2023-07-12', '2023-08-10', '2023-09-13', '2023-10-12',
        '2023-11-14', '2023-12-12',
    },
    'FOMC': {
        # 2024 FOMC Meeting Dates (decision announcement days)
        '2024-01-31', '2024-03-20', '2024-05-01', '2024-06-12', 
        '2024-07-31', '2024-09-18', '2024-11-07', '2024-12-18',
        # 2025 FOMC Meeting Dates
        '2025-01-29', '2025-03-19', '2025-05-07', '2025-06-18',
        '2025-07-30', '2025-09-17', '2025-11-05', '2025-12-17',
        # 2023 FOMC Meeting Dates
        '2023-02-01', '2023-03-22', '2023-05-03', '2023-06-14',
        '2023-07-26', '2023-09-20', '2023-11-01', '2023-12-13',
    },
    'NFP': {  # Non-Farm Payrolls (typically first Friday of month)
        # 2024 NFP Dates
        '2024-01-05', '2024-02-02', '2024-03-08', '2024-04-05', '2024-05-03',
        '2024-06-07', '2024-07-05', '2024-08-02', '2024-09-06', '2024-10-04',
        '2024-11-01', '2024-12-06',
        # 2025 NFP Dates
        '2025-01-10', '2025-02-07', '2025-03-07', '2025-04-04', '2025-05-02',
        '2025-06-06', '2025-07-03', '2025-08-01', '2025-09-05', '2025-10-03',
        '2025-11-07', '2025-12-05',
        # 2023 NFP Dates
        '2023-01-06', '2023-02-03', '2023-03-10', '2023-04-07', '2023-05-05',
        '2023-06-02', '2023-07-07', '2023-08-04', '2023-09-01', '2023-10-06',
        '2023-11-03', '2023-12-08',
    },
    'PPI': {  # Producer Price Index
        # 2024 PPI Release Dates
        '2024-01-12', '2024-02-15', '2024-03-14', '2024-04-11', '2024-05-14',
        '2024-06-13', '2024-07-12', '2024-08-13', '2024-09-12', '2024-10-11',
        '2024-11-14', '2024-12-12',
        # 2025 PPI Release Dates
        '2025-01-14', '2025-02-13', '2025-03-13', '2025-04-11', '2025-05-14',
        '2025-06-12', '2025-07-11', '2025-08-12', '2025-09-11', '2025-10-10',
        '2025-11-13', '2025-12-11',
        # 2023 PPI Release Dates
        '2023-01-13', '2023-02-15', '2023-03-15', '2023-04-13', '2023-05-11',
        '2023-06-14', '2023-07-13', '2023-08-11', '2023-09-14', '2023-10-13',
        '2023-11-15', '2023-12-13',
    },
    'RETAIL_SALES': {  # Retail Sales
        # 2024 Retail Sales Dates
        '2024-01-17', '2024-02-15', '2024-03-14', '2024-04-15', '2024-05-15',
        '2024-06-18', '2024-07-16', '2024-08-15', '2024-09-17', '2024-10-17',
        '2024-11-15', '2024-12-17',
        # 2025 Retail Sales Dates
        '2025-01-16', '2025-02-14', '2025-03-14', '2025-04-16', '2025-05-15',
        '2025-06-17', '2025-07-16', '2025-08-14', '2025-09-16', '2025-10-16',
        '2025-11-14', '2025-12-16',
        # 2023 Retail Sales Dates
        '2023-01-18', '2023-02-15', '2023-03-15', '2023-04-14', '2023-05-16',
        '2023-06-15', '2023-07-18', '2023-08-15', '2023-09-14', '2023-10-17',
        '2023-11-15', '2023-12-14',
    },
    'GDP': {  # GDP (Quarterly releases)
        # 2024 GDP Release Dates
        '2024-01-25', '2024-02-29', '2024-03-28', '2024-04-25', '2024-05-30',
        '2024-06-27', '2024-07-25', '2024-08-29', '2024-09-26', '2024-10-30',
        '2024-11-27', '2024-12-19',
        # 2025 GDP Release Dates
        '2025-01-30', '2025-02-27', '2025-03-27', '2025-04-30', '2025-05-29',
        '2025-06-26', '2025-07-31', '2025-08-28', '2025-09-25', '2025-10-30',
        '2025-11-26', '2025-12-23',
        # 2023 GDP Release Dates
        '2023-01-26', '2023-02-23', '2023-03-30', '2023-04-27', '2023-05-25',
        '2023-06-29', '2023-07-27', '2023-08-30', '2023-09-28', '2023-10-26',
        '2023-11-29', '2023-12-21',
    },
    'PCE': {  # Personal Consumption Expenditures (Fed's preferred inflation gauge)
        # 2024 PCE Release Dates
        '2024-01-26', '2024-02-29', '2024-03-29', '2024-04-26', '2024-05-31',
        '2024-06-28', '2024-07-26', '2024-08-30', '2024-09-27', '2024-10-31',
        '2024-11-27', '2024-12-20',
        # 2025 PCE Release Dates
        '2025-01-31', '2025-02-28', '2025-03-28', '2025-04-30', '2025-05-30',
        '2025-06-27', '2025-07-31', '2025-08-29', '2025-09-26', '2025-10-31',
        '2025-11-26', '2025-12-23',
        # 2023 PCE Release Dates
        '2023-01-27', '2023-02-24', '2023-03-31', '2023-04-28', '2023-05-26',
        '2023-06-30', '2023-07-28', '2023-08-31', '2023-09-29', '2023-10-27',
        '2023-11-30', '2023-12-22',
    },
}


def is_economic_event_date(check_date: date | str | pd.Timestamp, 
                           event_type: str) -> bool:
    """
    Check if a given date has a specific economic event.
    
    Args:
        check_date: Date to check
        event_type: Type of event ('CPI', 'FOMC', 'NFP', 'PPI', 'RETAIL_SALES', 'GDP', 'PCE')
        
    Returns:
        True if the date has the specified economic event
    """
    if isinstance(check_date, pd.Timestamp):
        check_date = check_date.date()
    elif isinstance(check_date, str):
        check_date = pd.Timestamp(check_date).date()
    
    date_str = check_date.strftime('%Y-%m-%d')
    
    event_type = event_type.upper()
    if event_type not in ECONOMIC_EVENTS:
        return False
    
    return date_str in ECONOMIC_EVENTS[event_type]


def get_economic_event_dates(event_type: str) -> Set[str]:
    """
    Get all dates for a specific economic event type.
    
    Args:
        event_type: Type of event ('CPI', 'FOMC', 'NFP', etc.)
        
    Returns:
        Set of date strings in 'YYYY-MM-DD' format
    """
    event_type = event_type.upper()
    return ECONOMIC_EVENTS.get(event_type, set())


def get_all_major_event_dates() -> Set[str]:
    """
    Get all dates that have any major economic event.
    
    Returns:
        Set of date strings in 'YYYY-MM-DD' format
    """
    all_dates = set()
    for event_dates in ECONOMIC_EVENTS.values():
        all_dates.update(event_dates)
    return all_dates


def get_events_on_date(check_date: date | str | pd.Timestamp) -> List[str]:
    """
    Get all economic events that occur on a specific date.
    
    Args:
        check_date: Date to check
        
    Returns:
        List of event names that occur on that date
    """
    if isinstance(check_date, pd.Timestamp):
        check_date = check_date.date()
    elif isinstance(check_date, str):
        check_date = pd.Timestamp(check_date).date()
    
    date_str = check_date.strftime('%Y-%m-%d')
    
    events = []
    for event_type, event_dates in ECONOMIC_EVENTS.items():
        if date_str in event_dates:
            events.append(event_type)
    
    return events


def add_economic_events_to_dataframe(df: pd.DataFrame, 
                                     date_column: str = 'date') -> pd.DataFrame:
    """
    Add columns to dataframe indicating which economic events occur on each date.
    
    Args:
        df: DataFrame with a date column
        date_column: Name of the date column
        
    Returns:
        DataFrame with additional boolean columns for each event type
    """
    df = df.copy()
    
    for event_type in ECONOMIC_EVENTS.keys():
        col_name = f'is_{event_type.lower()}_date'
        df[col_name] = df[date_column].apply(
            lambda d: is_economic_event_date(d, event_type)
        )
    
    # Add column for any major event
    df['is_major_event_date'] = df[date_column].apply(
        lambda d: d.strftime('%Y-%m-%d') in get_all_major_event_dates() 
        if hasattr(d, 'strftime') else str(d) in get_all_major_event_dates()
    )
    
    return df

