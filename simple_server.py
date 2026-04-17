from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Automated Book Generation System - Demo", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Automated Book Generation System API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": "demo mode"}

@app.get("/api/v1/books")
async def get_books():
    return [
        {
            "id": 1,
            "title": "Sample Book 1",
            "status": "draft_outline",
            "created_at": "2024-01-01T00:00:00Z"
        },
        {
            "id": 2,
            "title": "Sample Book 2", 
            "status": "generating_chapters",
            "created_at": "2024-01-02T00:00:00Z"
        }
    ]

@app.post("/api/v1/books")
async def create_book(book_data: dict):
    return {
        "id": 3,
        "title": book_data.get("title", "New Book"),
        "status": "draft_outline",
        "created_at": "2024-01-03T00:00:00Z"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
