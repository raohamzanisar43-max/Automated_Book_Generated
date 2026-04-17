"""
Database module for the Automated Book Generation System
Handles all database operations, migrations, and management
"""

from .connection import get_db, engine, SessionLocal, Base
from .migrations import run_migrations, create_database_if_not_exists

__all__ = [
    'get_db',
    'engine', 
    'SessionLocal',
    'Base',
    'run_migrations',
    'create_database_if_not_exists'
]
