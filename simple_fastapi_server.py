from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.config import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Automated Book Generation System", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def root():
    return {"message": "Automated Book Generation System API", "status": "running"}

@app.get("/health")
async def health_check():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}

@app.get("/api/v1/database/health")
async def database_health():
    try:
        with engine.connect() as conn:
            # Test basic connection
            conn.execute(text("SELECT 1"))
            
            # Check if tables exist
            result = conn.execute(text("""
                SELECT COUNT(*) FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('books', 'chapters')
            """))
            table_count = result.scalar()
            
            return {
                "status": "healthy" if table_count == 2 else "setup_needed",
                "connection": True,
                "tables_created": table_count == 2,
                "tables_found": table_count
            }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "error",
            "connection": False,
            "tables_created": False,
            "error": str(e)
        }

@app.post("/api/v1/database/migrate")
async def run_migrations():
    try:
        with engine.connect() as conn:
            # Create basic tables
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS books (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    title VARCHAR NOT NULL,
                    status VARCHAR DEFAULT 'draft_outline',
                    notes_on_outline_before TEXT,
                    outline TEXT,
                    notes_on_outline_after TEXT,
                    status_outline_notes VARCHAR,
                    final_review_notes_status VARCHAR,
                    book_output_status VARCHAR DEFAULT 'pending',
                    file_url VARCHAR,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))
            
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS chapters (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    book_id UUID NOT NULL REFERENCES books(id) ON DELETE CASCADE,
                    chapter_number INTEGER NOT NULL,
                    content TEXT,
                    summary TEXT,
                    chapter_notes_status VARCHAR,
                    chapter_notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))
            
            # Create indexes
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_books_status ON books(status);"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_chapters_book_id ON chapters(book_id);"))
            
            conn.commit()
            
        return {"success": True, "message": "Database migrations completed successfully"}
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise HTTPException(status_code=500, detail=f"Migration failed: {str(e)}")

@app.get("/api/v1/books")
async def get_books():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT * FROM books ORDER BY created_at DESC"))
            books = []
            for row in result:
                books.append({
                    "id": str(row[0]),
                    "title": row[1],
                    "status": row[2],
                    "created_at": row[9].isoformat() if row[9] else None,
                    "updated_at": row[10].isoformat() if row[10] else None
                })
            return books
    except Exception as e:
        logger.error(f"Error fetching books: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch books: {str(e)}")

@app.get("/api/v1/books/{book_id}")
async def get_book(book_id: str):
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT * FROM books WHERE id = :book_id"), {"book_id": book_id})
            row = result.fetchone()
            
            if not row:
                raise HTTPException(status_code=404, detail="Book not found")
            
            return {
                "id": str(row[0]),
                "title": row[1],
                "status": row[2],
                "notes_on_outline_before": row[3],
                "outline": row[4],
                "notes_on_outline_after": row[5],
                "status_outline_notes": row[6],
                "final_review_notes_status": row[7],
                "book_output_status": row[8],
                "file_url": row[9],
                "created_at": row[10].isoformat() if row[10] else None,
                "updated_at": row[11].isoformat() if row[11] else None
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching book {book_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch book: {str(e)}")

@app.get("/api/v1/books/{book_id}/chapters")
async def get_book_chapters(book_id: str):
    try:
        # First verify the book exists
        with engine.connect() as conn:
            book_result = conn.execute(text("SELECT id FROM books WHERE id = :book_id"), {"book_id": book_id})
            if not book_result.fetchone():
                raise HTTPException(status_code=404, detail="Book not found")
            
            # Get chapters for the book
            result = conn.execute(text("""
                SELECT * FROM chapters 
                WHERE book_id = :book_id 
                ORDER BY chapter_number
            """), {"book_id": book_id})
            
            chapters = []
            for row in result:
                chapters.append({
                    "id": str(row[0]),
                    "book_id": str(row[1]),
                    "chapter_number": row[2],
                    "content": row[3],
                    "summary": row[4],
                    "chapter_notes_status": row[5],
                    "chapter_notes": row[6],
                    "created_at": row[7].isoformat() if row[7] else None,
                    "updated_at": row[8].isoformat() if row[8] else None
                })
            
            return chapters
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching chapters for book {book_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch chapters: {str(e)}")

@app.post("/api/v1/books")
async def create_book(book_data: dict):
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                INSERT INTO books (title, notes_on_outline_before, status) 
                VALUES (:title, :notes, 'draft_outline')
                RETURNING id
            """), {
                "title": book_data.get("title"),
                "notes": book_data.get("notes_on_outline_before", "")
            })
            book_id = str(result.scalar())
            conn.commit()
            
            return {
                "id": book_id,
                "title": book_data.get("title"),
                "status": "draft_outline",
                "created_at": None,
                "updated_at": None
            }
    except Exception as e:
        logger.error(f"Error creating book: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create book: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
