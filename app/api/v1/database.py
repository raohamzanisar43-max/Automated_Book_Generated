"""
Database management API endpoints
Professional database control and monitoring endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Dict, Any, List
import logging

from app.db.connection import get_db, db_manager
from app.db.migrations import run_migrations, get_database_stats, migration_manager
from app.api.deps import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/health", response_model=Dict[str, Any])
async def database_health_check():
    """
    Comprehensive database health check
    Returns detailed health status and statistics
    """
    try:
        health_status = await db_manager.health_check()
        
        if health_status["status"] == "healthy":
            # Add additional health metrics
            db_info = await db_manager.get_database_info()
            health_status.update(db_info)
        
        return health_status
        
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database health check failed: {str(e)}"
        )

@router.post("/migrate", response_model=Dict[str, Any])
async def run_database_migrations():
    """
    Run database migrations
    Creates tables, indexes, triggers, and sample data
    """
    try:
        logger.info("Starting database migration process...")
        
        # Run migrations
        migration_results = await run_migrations()
        
        if migration_results["success"]:
            logger.info("Database migrations completed successfully")
            return {
                "message": "Database migrations completed successfully",
                "migrations_run": migration_results["migrations_run"],
                "tables_created": migration_results["tables_created"],
                "status": "completed"
            }
        else:
            logger.error(f"Database migrations failed: {migration_results['errors']}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "message": "Database migrations failed",
                    "errors": migration_results["errors"]
                }
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during migrations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Migration process failed: {str(e)}"
        )

@router.get("/status", response_model=Dict[str, Any])
async def get_migration_status():
    """
    Get current migration status
    Returns information about created tables and their status
    """
    try:
        status = await migration_manager.get_migration_status()
        return status
        
    except Exception as e:
        logger.error(f"Error getting migration status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get migration status: {str(e)}"
        )

@router.get("/stats", response_model=Dict[str, Any])
async def get_database_statistics():
    """
    Get comprehensive database statistics
    Returns book counts, chapter counts, and other metrics
    """
    try:
        stats = await get_database_stats()
        return stats
        
    except Exception as e:
        logger.error(f"Error getting database statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get database statistics: {str(e)}"
        )

@router.get("/tables", response_model=List[Dict[str, Any]])
async def get_database_tables(db: Session = Depends(get_db)):
    """
    Get information about all database tables
    Returns table names, column counts, and row counts
    """
    try:
        # Get table information
        tables_query = text("""
            SELECT 
                t.table_name,
                COUNT(c.column_name) as column_count,
                COALESCE(s.row_count, 0) as row_count
            FROM information_schema.tables t
            LEFT JOIN information_schema.columns c ON t.table_name = c.table_name
            LEFT JOIN (
                SELECT 
                    schemaname,
                    tablename,
                    n_tup_ins - n_tup_del as row_count
                FROM pg_stat_user_tables
            ) s ON t.table_name = s.tablename
            WHERE t.table_schema = 'public'
            GROUP BY t.table_name, s.row_count
            ORDER BY t.table_name
        """)
        
        result = db.execute(tables_query)
        tables = []
        
        for row in result:
            tables.append({
                "table_name": row.table_name,
                "column_count": row.column_count,
                "row_count": row.row_count
            })
        
        return tables
        
    except Exception as e:
        logger.error(f"Error getting table information: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get table information: {str(e)}"
        )

@router.get("/tables/{table_name}/schema", response_model=Dict[str, Any])
async def get_table_schema(table_name: str, db: Session = Depends(get_db)):
    """
    Get detailed schema for a specific table
    Returns column information, data types, and constraints
    """
    try:
        # Validate table name
        if table_name not in ['books', 'chapters']:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Table '{table_name}' not found"
            )
        
        # Get column information
        columns_query = text("""
            SELECT 
                column_name,
                data_type,
                is_nullable,
                column_default,
                character_maximum_length,
                numeric_precision,
                numeric_scale
            FROM information_schema.columns
            WHERE table_name = :table_name AND table_schema = 'public'
            ORDER BY ordinal_position
        """)
        
        result = db.execute(columns_query, {"table_name": table_name})
        columns = []
        
        for row in result:
            columns.append({
                "name": row.column_name,
                "data_type": row.data_type,
                "nullable": row.is_nullable == "YES",
                "default": row.column_default,
                "max_length": row.character_maximum_length,
                "precision": row.numeric_precision,
                "scale": row.numeric_scale
            })
        
        # Get constraints
        constraints_query = text("""
            SELECT 
                constraint_name,
                constraint_type
            FROM information_schema.table_constraints
            WHERE table_name = :table_name AND table_schema = 'public'
        """)
        
        constraints_result = db.execute(constraints_query, {"table_name": table_name})
        constraints = [row.constraint_type for row in constraints_result]
        
        return {
            "table_name": table_name,
            "columns": columns,
            "constraints": constraints
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting table schema: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get table schema: {str(e)}"
        )

@router.post("/reset", response_model=Dict[str, Any])
async def reset_database():
    """
    Reset the entire database
    WARNING: This will delete all data!
    """
    try:
        logger.warning("Database reset requested - this will delete all data")
        
        # This is a dangerous operation, so we'll require additional confirmation
        # For now, we'll just return a warning message
        
        return {
            "message": "Database reset is disabled for safety",
            "warning": "To reset the database, manually drop and recreate the database",
            "status": "disabled"
        }
        
    except Exception as e:
        logger.error(f"Error during database reset: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database reset failed: {str(e)}"
        )

@router.get("/query", response_model=Dict[str, Any])
async def execute_custom_query(
    query: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Execute a custom SQL query (admin only)
    WARNING: This is a powerful endpoint that should be restricted
    """
    try:
        # Basic query validation
        dangerous_keywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE', 'TRUNCATE']
        query_upper = query.upper()
        
        if any(keyword in query_upper for keyword in dangerous_keywords):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Dangerous SQL keywords detected. Only SELECT queries are allowed."
            )
        
        # Execute the query
        result = db.execute(text(query))
        
        # Convert result to dictionary
        if result.returns_rows:
            rows = result.fetchall()
            columns = result.keys()
            
            data = []
            for row in rows:
                data.append(dict(zip(columns, row)))
            
            return {
                "data": data,
                "row_count": len(data),
                "columns": list(columns)
            }
        else:
            return {
                "message": "Query executed successfully",
                "rows_affected": result.rowcount
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing custom query: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query execution failed: {str(e)}"
        )
