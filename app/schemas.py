from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from app.models import BookStatus, OutlineNotesStatus, ChapterNotesStatus

class BookBase(BaseModel):
    title: str

class BookCreate(BookBase):
    notes_on_outline_before: str

class BookUpdate(BaseModel):
    title: Optional[str] = None
    outline: Optional[str] = None
    notes_on_outline_before: Optional[str] = None
    notes_on_outline_after: Optional[str] = None
    status_outline_notes: Optional[OutlineNotesStatus] = None
    final_review_notes_status: Optional[OutlineNotesStatus] = None
    book_output_status: Optional[str] = None
    file_url: Optional[str] = None

class OutlineReview(BaseModel):
    status_outline_notes: OutlineNotesStatus
    notes_on_outline_after: Optional[str] = None

class FinalReview(BaseModel):
    final_review_notes_status: OutlineNotesStatus

class ChapterBase(BaseModel):
    chapter_number: int

class ChapterCreate(ChapterBase):
    content: Optional[str] = None
    summary: Optional[str] = None
    chapter_notes_status: Optional[ChapterNotesStatus] = None
    chapter_notes: Optional[str] = None

class ChapterUpdate(BaseModel):
    content: Optional[str] = None
    summary: Optional[str] = None
    chapter_notes_status: Optional[ChapterNotesStatus] = None
    chapter_notes: Optional[str] = None

class WebSearchResult(BaseModel):
    title: str
    url: str
    snippet: str
    
class ExportRequest(BaseModel):
    format: str  # 'pdf', 'docx', 'txt'
    
class SuccessResponse(BaseModel):
    success: bool
    message: str

class ChapterResponse(ChapterBase):
    id: UUID
    book_id: UUID
    content: Optional[str] = None
    summary: Optional[str] = None
    chapter_notes_status: Optional[ChapterNotesStatus] = None
    chapter_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ChapterReview(BaseModel):
    chapter_notes_status: ChapterNotesStatus
    chapter_notes: Optional[str] = None

class BookResponse(BookBase):
    id: UUID
    status: BookStatus
    outline: Optional[str] = None
    notes_on_outline_before: Optional[str] = None
    notes_on_outline_after: Optional[str] = None
    status_outline_notes: Optional[OutlineNotesStatus] = None
    final_review_notes_status: Optional[OutlineNotesStatus] = None
    book_output_status: str
    file_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
