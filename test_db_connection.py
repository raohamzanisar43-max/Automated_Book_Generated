import asyncio
from app.db.connection import db_manager

async def test_connection():
    print("Testing database connection...")
    health = await db_manager.health_check()
    print(f"Health check result: {health}")
    
    if health["connection"]:
        print("Database connection successful!")
        
        # Run migrations
        from app.db.migrations import run_migrations
        print("Running migrations...")
        migration_results = await run_migrations()
        print(f"Migration results: {migration_results}")
    else:
        print(f"Database connection failed: {health.get('error', 'Unknown error')}")

if __name__ == "__main__":
    asyncio.run(test_connection())
