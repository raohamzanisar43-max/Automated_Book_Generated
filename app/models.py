from sqlalchemy import Column, String, Integer, Text, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
import enum
from app.database import Base

class OutlineNotesStatus(str, enum.Enum):
    yes = "yes"
    no = "no"
    no_notes_needed = "no_notes_needed"

class ChapterNotesStatus(str, enum.Enum):
    yes = "yes"
    no = "no"
    no_notes_needed = "no_notes_needed"

class BookStatus(str, enum.Enum):
    draft_outline = "draft_outline"
    review_outline = "review_outline"
    generating_chapters = "generating_chapters"
    reviewing_chapters = "reviewing_chapters"
    compiling = "compiling"
    completed = "completed"
    paused = "paused"

class Book(Base):
    __tablename__ = "books"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    status = Column(Enum(BookStatus), default=BookStatus.draft_outline)
    
    notes_on_outline_before = Column(Text, nullable=True)
    outline = Column(Text, nullable=True)
    notes_on_outline_after = Column(Text, nullable=True)
    status_outline_notes = Column(Enum(OutlineNotesStatus), nullable=True)
    
    final_review_notes_status = Column(Enum(OutlineNotesStatus), nullable=True)
    book_output_status = Column(String, default="pending")
    file_url = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    chapters = relationship("Chapter", back_populates="book", cascade="all, delete-orphan")


class Chapter(Base):
    __tablename__ = "chapters"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    book_id = Column(UUID(as_uuid=True), ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    chapter_number = Column(Integer, nullable=False)
    
    content = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    
    chapter_notes_status = Column(Enum(ChapterNotesStatus), nullable=True)
    chapter_notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    book = relationship("Book", back_populates="chapters")
