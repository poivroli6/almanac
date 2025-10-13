"""
Database Configuration

Centralized database connection management.
"""

from typing import Optional

# Optional dependency - only needed if using database fallback
try:
    from sqlalchemy import create_engine
    from sqlalchemy.engine import Engine
    HAS_SQLALCHEMY = True
except ImportError:
    HAS_SQLALCHEMY = False
    Engine = None


# Default connection string for RESEARCH database
# Try these alternatives if default doesn't work:
# Option 1: Default instance (current)
DEFAULT_DB_CONN_STRING = (
    "mssql+pyodbc://@RESEARCH/HistoricalData?"
    "driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
)

# Option 2: Named instance (uncomment if RESEARCH has named instance)
# DEFAULT_DB_CONN_STRING = (
#     "mssql+pyodbc://@RESEARCH\\SQLEXPRESS/HistoricalData?"
#     "driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
# )

# Option 3: Specify port explicitly
# DEFAULT_DB_CONN_STRING = (
#     "mssql+pyodbc://@RESEARCH,1433/HistoricalData?"
#     "driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
# )

# Option 4: Use IP address instead of hostname
# DEFAULT_DB_CONN_STRING = (
#     "mssql+pyodbc://@192.168.2.5/HistoricalData?"
#     "driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
# )

_engine: Optional[Engine] = None


def get_engine(connection_string: str = DEFAULT_DB_CONN_STRING) -> Engine:
    """
    Get or create SQLAlchemy engine with connection pooling.
    
    Args:
        connection_string: Database connection string
        
    Returns:
        SQLAlchemy Engine instance
        
    Raises:
        ImportError: If SQLAlchemy is not installed
    """
    if not HAS_SQLALCHEMY:
        raise ImportError(
            "SQLAlchemy is not installed. "
            "Install it with: pip install sqlalchemy pyodbc"
        )
    
    global _engine
    
    if _engine is None:
        _engine = create_engine(
            connection_string,
            pool_pre_ping=True,  # Verify connections before using
            pool_recycle=3600,   # Recycle connections after 1 hour
            echo=False,          # Set to True for SQL debugging
        )
    
    return _engine


def reset_engine():
    """Reset the engine (useful for testing)."""
    global _engine
    if _engine is not None:
        _engine.dispose()
        _engine = None

