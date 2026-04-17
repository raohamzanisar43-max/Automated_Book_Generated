#!/usr/bin/env python3
"""
Simple startup script for the Automated Book Generation System
This script will set up the database and start the server
"""

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.connection import engine, db_manager
from app.db.migrations import run_migrations
from app.config import settings

async def setup_and_start():
    """Set up database and start the server"""
    
    print("🚀 Starting Automated Book Generation System...")
    print("=" * 50)
    
    try:
        # Step 1: Check database connection
        print("📡 Step 1: Checking database connection...")
        health_status = await db_manager.health_check()
        
        if not health_status["connection"]:
            print("❌ Database connection failed!")
            print(f"   Error: {health_status.get('error', 'Unknown error')}")
            print("\n🔧 Please check:")
            print("   1. PostgreSQL is running on localhost:5432")
            print("   2. Database 'automated_book' exists")
            print("   3. Your password in .env is correct")
            return False
        
        print("✅ Database connection successful!")
        
        # Step 2: Run migrations
        print("\n🔄 Step 2: Running database migrations...")
        migration_results = await run_migrations()
        
        if not migration_results["success"]:
            print("❌ Database migrations failed!")
            print(f"   Errors: {migration_results['errors']}")
            return False
        
        print("✅ Database migrations completed!")
        print(f"   Tables created: {migration_results['tables_created']}")
        
        # Step 3: Start the server
        print("\n🌐 Step 3: Starting FastAPI server...")
        print("=" * 50)
        print("🎉 System is ready!")
        print("\n📍 Localhost URLs:")
        print("   🎨 Frontend: http://localhost:3000")
        print("   🔧 Backend:  http://localhost:8000")
        print("   📚 API Docs: http://localhost:8000/docs")
        print("   ❤️ Health:   http://localhost:8000/health")
        print("   🗄️ Database: http://localhost:8000/api/v1/database/health")
        print("\n🚀 Starting server...")
        
        # Import and run uvicorn
        import uvicorn
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=settings.DEBUG,
            log_level="info"
        )
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
        return True
    except Exception as e:
        print(f"❌ Startup failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(setup_and_start())
