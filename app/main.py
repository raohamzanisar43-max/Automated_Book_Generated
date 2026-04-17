from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import time

from app.db.connection import engine, db_manager
from app.db.migrations import run_migrations
from app.api.v1 import api_router
from app.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info(" Starting up Automated Book Generation System...")
    
    try:
        # Check database connection
        logger.info(" Checking database connection...")
        health_status = await db_manager.health_check()
        
        if not health_status["connection"]:
            logger.error(" Database connection failed")
            raise Exception("Database connection failed")
        
        logger.info(" Database connection successful")
        
        # Run database migrations
        logger.info(" Running database migrations...")
        migration_results = await run_migrations()
        
        if migration_results["success"]:
            logger.info(f" Database migrations completed. Tables created: {migration_results['tables_created']}")
        else:
            logger.error(f" Database migrations failed: {migration_results['errors']}")
            raise Exception("Database migrations failed")
        
        logger.info(" System startup completed successfully!")
        
    except Exception as e:
        logger.error(f" Startup failed: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info(" Shutting down...")
    try:
        await db_manager.close_all_connections()
        logger.info(" All database connections closed")
    except Exception as e:
        logger.error(f" Error during shutdown: {e}")
    
    logger.info(" Shutdown completed")

app = FastAPI(
    title="Automated Book Generation System",
    description="A professional AI-powered system for automated book generation with human-in-the-loop review",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add timing middleware
@app.middleware("http")
async def add_process_time_header(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Include API routes
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "message": "Welcome to the Automated Book Generation System API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "database": "/api/v1/database/health"
    }

@app.get("/health")
async def health_check():
    """
    System health check
    Returns overall system health including database status
    """
    try:
        # Check database health
        db_health = await db_manager.health_check()
        
        return {
            "status": "healthy" if db_health["status"] == "healthy" else "unhealthy",
            "timestamp": time.time(),
            "version": "1.0.0",
            "database": db_health,
            "components": {
                "api": "healthy",
                "database": db_health["status"],
                "migrations": "completed"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "timestamp": time.time(),
            "version": "1.0.0",
            "error": str(e)
        }

@app.get("/api/v1/system/info")
async def system_info():
    """
    Get detailed system information
    """
    try:
        db_info = await db_manager.get_database_info()
        
        return {
            "system": {
                "name": "Automated Book Generation System",
                "version": "1.0.0",
                "environment": "development"
            },
            "database": db_info,
            "features": {
                "ai_generation": True,
                "human_review": True,
                "multi_format_export": True,
                "notifications": True,
                "web_search": True
            }
        }
    except Exception as e:
        logger.error(f"System info failed: {e}")
        return {
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )
