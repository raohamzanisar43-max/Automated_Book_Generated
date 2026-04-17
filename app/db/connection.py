"""
Database connection configuration
Professional database management with connection pooling and error handling
"""

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import logging
from typing import Generator

from app.config import settings

# Configure logging
logger = logging.getLogger(__name__)

# Create SQLAlchemy engine with professional configuration
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=3600,   # Recycle connections every hour
    echo=settings.SQL_DEBUG,  # Log SQL queries in debug mode
    future=True,  # Use SQLAlchemy 2.0 style
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    future=True,
)

# Create declarative base
Base = declarative_base()

# Metadata for migrations
metadata = MetaData()

def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session
    Professional session management with proper error handling
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

async def check_database_connection() -> bool:
    """
    Check if database connection is working
    Returns True if connection is successful, False otherwise
    """
    try:
        with engine.connect() as connection:
            connection.execute("SELECT 1")
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False

async def get_database_info() -> dict:
    """
    Get database information and statistics
    Returns dictionary with database stats
    """
    try:
        with engine.connect() as connection:
            # Get PostgreSQL version
            version_result = connection.execute("SELECT version()")
            version = version_result.scalar()
            
            # Get table counts
            tables_result = connection.execute("""
                SELECT table_name, 
                       (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as column_count
                FROM information_schema.tables t 
                WHERE table_schema = 'public' 
                ORDER BY table_name
            """)
            tables = dict(tables_result.fetchall())
            
            # Get database size
            size_result = connection.execute("""
                SELECT pg_size_pretty(pg_database_size(current_database()))
            """)
            size = size_result.scalar()
            
            return {
                "version": version,
                "tables": tables,
                "size": size,
                "connection_pool_size": engine.pool.size(),
                "connection_pool_checked_out": engine.pool.checkedout()
            }
    except Exception as e:
        logger.error(f"Error getting database info: {e}")
        return {"error": str(e)}

def create_database_session() -> Session:
    """
    Create a new database session
    Use this for manual session management outside of dependency injection
    """
    return SessionLocal()

class DatabaseManager:
    """
    Professional database manager class
    Handles advanced database operations and monitoring
    """
    
    def __init__(self):
        self.engine = engine
        self.session_factory = SessionLocal
    
    async def health_check(self) -> dict:
        """
        Comprehensive database health check
        """
        health_status = {
            "status": "healthy",
            "connection": False,
            "tables_created": False,
            "error": None
        }
        
        try:
            # Check connection
            health_status["connection"] = await check_database_connection()
            
            if health_status["connection"]:
                # Check if tables exist
                with self.engine.connect() as connection:
                    result = connection.execute("""
                        SELECT COUNT(*) FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name IN ('books', 'chapters')
                    """)
                    table_count = result.scalar()
                    health_status["tables_created"] = table_count == 2
            
            if not health_status["connection"] or not health_status["tables_created"]:
                health_status["status"] = "unhealthy"
                
        except Exception as e:
            health_status["status"] = "error"
            health_status["error"] = str(e)
            logger.error(f"Database health check failed: {e}")
        
        return health_status
    
    def get_session(self) -> Session:
        """Get a new database session"""
        return self.session_factory()
    
    async def close_all_connections(self):
        """Close all database connections"""
        try:
            self.engine.dispose()
            logger.info("All database connections closed")
        except Exception as e:
            logger.error(f"Error closing database connections: {e}")

# Global database manager instance
db_manager = DatabaseManager()
