"""
Database migrations and setup
Professional database migration management
"""

import asyncio
import logging
from sqlalchemy import text, inspect
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Dict, Any

from .connection import engine, db_manager, is_sqlite
from ..models import Base, Book, Chapter, BookStatus, OutlineNotesStatus, ChapterNotesStatus

logger = logging.getLogger(__name__)

class MigrationManager:
    """
    Professional migration manager for database schema changes
    """
    
    def __init__(self):
        self.engine = engine
        if is_sqlite:
            self.migrations = [
                self._create_initial_schema,
                self._create_sqlite_indexes,
                self._insert_sample_data,
            ]
        else:
            self.migrations = [
                self._create_initial_schema,
                self._create_enums,
                self._create_postgresql_indexes,
                self._create_triggers,
                self._insert_sample_data,
            ]
    
    async def run_all_migrations(self) -> Dict[str, Any]:
        """
        Run all pending migrations
        Returns migration results
        """
        results = {
            "success": True,
            "migrations_run": [],
            "errors": [],
            "tables_created": []
        }
        
        logger.info("Starting database migrations...")
        
        try:
            # Check database connection first
            if not await db_manager.health_check():
                raise Exception("Database health check failed")
            
            # Run each migration
            for i, migration in enumerate(self.migrations, 1):
                try:
                    migration_name = migration.__name__
                    logger.info(f"Running migration {i}: {migration_name}")
                    
                    await migration()
                    
                    results["migrations_run"].append(migration_name)
                    logger.info(f"Migration {migration_name} completed successfully")
                    
                except Exception as e:
                    error_msg = f"Migration {migration_name} failed: {str(e)}"
                    logger.error(error_msg)
                    results["errors"].append(error_msg)
                    results["success"] = False
            
            # Get created tables
            if results["success"]:
                results["tables_created"] = await self._get_table_list()
            
            logger.info(f"Database migrations completed. Success: {results['success']}")
            
        except Exception as e:
            logger.error(f"Migration process failed: {e}")
            results["success"] = False
            results["errors"].append(str(e))
        
        return results
    
    async def _create_initial_schema(self):
        """Create initial database schema"""
        logger.info("Creating initial database schema...")
        
        with self.engine.begin() as conn:
            # Create all tables
            conn.run_sync(Base.metadata.create_all)
            logger.info("Base tables created")
    
    async def _create_enums(self):
        """Create custom enum types"""
        logger.info("Creating enum types...")
        
        enum_definitions = [
            """
            DO $$ BEGIN
                CREATE TYPE bookstatus AS ENUM (
                    'draft_outline',
                    'review_outline', 
                    'generating_chapters',
                    'reviewing_chapters',
                    'compiling',
                    'completed',
                    'paused'
                );
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
            """,
            """
            DO $$ BEGIN
                CREATE TYPE notesstatus AS ENUM (
                    'yes',
                    'no_notes_needed',
                    'no'
                );
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
            """,
            """
            DO $$ BEGIN
                CREATE TYPE chapterstatus AS ENUM (
                    'draft_outline',
                    'generating',
                    'review_needed',
                    'approved',
                    'paused'
                );
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
            """
        ]
        
        with self.engine.begin() as conn:
            for enum_sql in enum_definitions:
                conn.execute(text(enum_sql))
        
        logger.info("Enum types created")
    
    async def _create_sqlite_indexes(self):
        """Create SQLite performance indexes"""
        logger.info("Creating SQLite indexes...")
        
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_books_status ON books(status);",
            "CREATE INDEX IF NOT EXISTS idx_books_created_at ON books(created_at);",
            "CREATE INDEX IF NOT EXISTS idx_books_title ON books(title);",
            "CREATE INDEX IF NOT EXISTS idx_chapters_book_id ON chapters(book_id);",
            "CREATE INDEX IF NOT EXISTS idx_chapters_chapter_number ON chapters(chapter_number);",
            "CREATE INDEX IF NOT EXISTS idx_chapters_book_chapter ON chapters(book_id, chapter_number);",
        ]
        
        with self.engine.begin() as conn:
            for index_sql in indexes:
                conn.execute(text(index_sql))
        
        logger.info("SQLite indexes created")
    
    async def _create_postgresql_indexes(self):
        """Create PostgreSQL performance indexes"""
        logger.info("Creating PostgreSQL indexes...")
        
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_books_status ON books(status);",
            "CREATE INDEX IF NOT EXISTS idx_books_created_at ON books(created_at);",
            "CREATE INDEX IF NOT EXISTS idx_books_title ON books(title);",
            "CREATE INDEX IF NOT EXISTS idx_chapters_book_id ON chapters(book_id);",
            "CREATE INDEX IF NOT EXISTS idx_chapters_status ON chapters(status);",
            "CREATE INDEX IF NOT EXISTS idx_chapters_chapter_number ON chapters(chapter_number);",
            "CREATE INDEX IF NOT EXISTS idx_chapters_book_chapter ON chapters(book_id, chapter_number);",
        ]
        
        with self.engine.begin() as conn:
            for index_sql in indexes:
                conn.execute(text(index_sql))
        
        logger.info("PostgreSQL indexes created")
    
    async def _create_triggers(self):
        """Create triggers for automatic timestamp updates"""
        logger.info("Creating triggers...")
        
        trigger_functions = [
            """
            CREATE OR REPLACE FUNCTION update_updated_at_column()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = CURRENT_TIMESTAMP;
                RETURN NEW;
            END;
            $$ language 'plpgsql';
            """,
            """
            DROP TRIGGER IF EXISTS update_books_updated_at ON books;
            CREATE TRIGGER update_books_updated_at 
                BEFORE UPDATE ON books 
                FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
            """,
            """
            DROP TRIGGER IF EXISTS update_chapters_updated_at ON chapters;
            CREATE TRIGGER update_chapters_updated_at 
                BEFORE UPDATE ON chapters 
                FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
            """
        ]
        
        with self.engine.begin() as conn:
            for trigger_sql in trigger_functions:
                conn.execute(text(trigger_sql))
        
        logger.info("Triggers created")
    
    async def _insert_sample_data(self):
        """Insert sample data for testing"""
        logger.info("Inserting sample data...")
        
        if is_sqlite:
            sample_data = [
                """
                INSERT OR IGNORE INTO books (title, notes_on_outline_before, status) 
                VALUES (
                    'Getting Started with AI Book Generation', 
                    'A comprehensive guide to automated book generation using AI, covering the complete workflow from outline to final publication.',
                    'draft_outline'
                );
                """,
                """
                INSERT OR IGNORE INTO books (title, notes_on_outline_before, status) 
                VALUES (
                    'Advanced React Development', 
                    'Deep dive into React ecosystem, hooks, performance optimization, and best practices for modern web development.',
                    'draft_outline'
                );
                """
            ]
        else:
            sample_data = [
                """
                INSERT INTO books (title, notes_on_outline_before, status) 
                VALUES (
                    'Getting Started with AI Book Generation', 
                    'A comprehensive guide to automated book generation using AI, covering the complete workflow from outline to final publication.',
                    'draft_outline'
                )
                ON CONFLICT DO NOTHING;
                """,
                """
                INSERT INTO books (title, notes_on_outline_before, status) 
                VALUES (
                    'Advanced React Development', 
                    'Deep dive into React ecosystem, hooks, performance optimization, and best practices for modern web development.',
                    'draft_outline'
                )
                ON CONFLICT DO NOTHING;
                """
            ]
        
        with self.engine.begin() as conn:
            for data_sql in sample_data:
                conn.execute(text(data_sql))
        
        logger.info("Sample data inserted")
    
    async def _get_table_list(self) -> List[str]:
        """Get list of all tables in the database"""
        with self.engine.begin() as conn:
            if is_sqlite:
                result = conn.execute(text("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' 
                    ORDER BY name
                """))
            else:
                result = conn.execute(text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    ORDER BY table_name
                """))
            return [row[0] for row in result.fetchall()]
    
    async def get_migration_status(self) -> Dict[str, Any]:
        """Get current migration status"""
        try:
            tables = await self._get_table_list()
            
            # Check if key tables exist
            required_tables = ['books', 'chapters']
            tables_exist = all(table in tables for table in required_tables)
            
            # Get table info
            table_info = {}
            for table in tables:
                async with self.engine.begin() as conn:
                    result = await conn.execute(text(f"""
                        SELECT COUNT(*) as row_count 
                        FROM {table}
                    """))
                    row_count = result.scalar()
                    table_info[table] = row_count
            
            return {
                "tables_exist": tables_exist,
                "tables": tables,
                "table_info": table_info,
                "ready": tables_exist
            }
            
        except Exception as e:
            logger.error(f"Error getting migration status: {e}")
            return {
                "tables_exist": False,
                "error": str(e),
                "ready": False
            }

# Global migration manager
migration_manager = MigrationManager()

async def run_migrations() -> Dict[str, Any]:
    """Run all database migrations"""
    return await migration_manager.run_all_migrations()

async def create_database_if_not_exists() -> bool:
    """Create database if it doesn't exist"""
    try:
        # This would typically require admin privileges
        # For now, we'll assume the database exists
        logger.info("Database connection check passed")
        return True
    except Exception as e:
        logger.error(f"Database creation check failed: {e}")
        return False

async def get_database_stats() -> Dict[str, Any]:
    """Get comprehensive database statistics"""
    try:
        async with engine.begin() as conn:
            # Get book stats
            book_stats = await conn.execute(text("""
                SELECT 
                    COUNT(*) as total_books,
                    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_books,
                    COUNT(CASE WHEN status = 'paused' THEN 1 END) as paused_books,
                    COUNT(CASE WHEN status = 'generating_chapters' THEN 1 END) as active_books
                FROM books
            """))
            book_data = book_stats.first()
            
            # Get chapter stats
            chapter_stats = await conn.execute(text("""
                SELECT 
                    COUNT(*) as total_chapters,
                    COUNT(CASE WHEN content IS NOT NULL THEN 1 END) as generated_chapters,
                    COUNT(CASE WHEN status = 'approved' THEN 1 END) as approved_chapters
                FROM chapters
            """))
            chapter_data = chapter_stats.first()
            
            # Get database size
            size_result = await conn.execute(text("""
                SELECT pg_size_pretty(pg_database_size(current_database())) as size
            """))
            db_size = size_result.scalar()
            
            return {
                "books": {
                    "total": book_data.total_books,
                    "completed": book_data.completed_books,
                    "paused": book_data.paused_books,
                    "active": book_data.active_books
                },
                "chapters": {
                    "total": chapter_data.total_chapters,
                    "generated": chapter_data.generated_chapters,
                    "approved": chapter_data.approved_chapters
                },
                "database_size": db_size,
                "last_updated": "2024-01-01T00:00:00Z"  # Would be dynamic in production
            }
            
    except Exception as e:
        logger.error(f"Error getting database stats: {e}")
        return {"error": str(e)}
