"""
Database models for the Automated Book Generation System
Professional SQLAlchemy models with proper relationships and constraints
"""

from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
import uuid

from .connection import Base

# Enums for database constraints
class BookStatus(str, Enum):
    DRAFT_OUTLINE = "draft_outline"
    REVIEW_OUTLINE = "review_outline"
    GENERATING_CHAPTERS = "generating_chapters"
    REVIEWING_CHAPTERS = "reviewing_chapters"
    COMPILING = "compiling"
    COMPLETED = "completed"
    PAUSED = "paused"

class NotesStatus(str, Enum):
    YES = "yes"
    NO_NOTES_NEEDED = "no_notes_needed"
    NO = "no"

class ChapterStatus(str, Enum):
    DRAFT_OUTLINE = "draft_outline"
    GENERATING = "generating"
    REVIEW_NEEDED = "review_needed"
    APPROVED = "approved"
    PAUSED = "paused"

class Book(Base):
    """
    Book model - represents a book in the generation system
    """
    __tablename__ = "books"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Book information
    title = Column(String(500), nullable=False, index=True)
    outline = Column(Text, nullable=True)
    
    # Outline stage fields
    notes_on_outline_before = Column(Text, nullable=True)
    notes_on_outline_after = Column(Text, nullable=True)
    status_outline_notes = Column(SQLEnum(NotesStatus), default=NotesStatus.NO, nullable=False)
    
    # Final review fields
    final_review_notes = Column(Text, nullable=True)
    final_review_notes_status = Column(SQLEnum(NotesStatus), default=NotesStatus.NO, nullable=False)
    
    # Workflow status
    status = Column(SQLEnum(BookStatus), default=BookStatus.DRAFT_OUTLINE, nullable=False, index=True)
    
    # File information
    file_url = Column(String(1000), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    chapters = relationship("Chapter", back_populates="book", cascade="all, delete-orphan", lazy="dynamic")
    
    def __repr__(self):
        return f"<Book(id={self.id}, title='{self.title}', status='{self.status}')>"
    
    @property
    def chapter_count(self) -> int:
        """Get the number of chapters for this book"""
        return self.chapters.count()
    
    @property
    def completed_chapters(self) -> int:
        """Get the number of completed chapters"""
        return self.chapters.filter(Chapter.status == ChapterStatus.APPROVED).count()
    
    @property
    def progress_percentage(self) -> float:
        """Calculate progress percentage based on workflow status"""
        status_progress = {
            BookStatus.DRAFT_OUTLINE: 10,
            BookStatus.REVIEW_OUTLINE: 25,
            BookStatus.GENERATING_CHAPTERS: 50,
            BookStatus.REVIEWING_CHAPTERS: 75,
            BookStatus.COMPILING: 90,
            BookStatus.COMPLETED: 100,
            BookStatus.PAUSED: self.progress_percentage if hasattr(self, '_cached_progress') else 0
        }
        
        if self.status == BookStatus.PAUSED:
            # Calculate based on chapters if paused
            if self.chapter_count > 0:
                return (self.completed_chapters / self.chapter_count) * 100
            return 25  # Default if no chapters
        
        return status_progress.get(self.status, 0)
    
    def to_dict(self) -> dict:
        """Convert book to dictionary for API responses"""
        return {
            "id": str(self.id),
            "title": self.title,
            "outline": self.outline,
            "notes_on_outline_before": self.notes_on_outline_before,
            "notes_on_outline_after": self.notes_on_outline_after,
            "status_outline_notes": self.status_outline_notes,
            "final_review_notes": self.final_review_notes,
            "final_review_notes_status": self.final_review_notes_status,
            "status": self.status,
            "file_url": self.file_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "chapter_count": self.chapter_count,
            "completed_chapters": self.completed_chapters,
            "progress_percentage": self.progress_percentage
        }

class Chapter(Base):
    """
    Chapter model - represents a chapter in a book
    """
    __tablename__ = "chapters"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Foreign key to book
    book_id = Column(UUID(as_uuid=True), ForeignKey("books.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Chapter information
    chapter_number = Column(Integer, nullable=False, index=True)
    title = Column(String(500), nullable=True)
    content = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    
    # Review fields
    chapter_notes = Column(Text, nullable=True)
    chapter_notes_status = Column(SQLEnum(NotesStatus), default=NotesStatus.NO_NOTES_NEEDED, nullable=False)
    
    # Workflow status
    status = Column(SQLEnum(ChapterStatus), default=ChapterStatus.DRAFT_OUTLINE, nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    book = relationship("Book", back_populates="chapters")
    
    # Constraints
    __table_args__ = (
        {"schema": "public"},
    )
    
    def __repr__(self):
        return f"<Chapter(id={self.id}, book_id={self.book_id}, chapter_number={self.chapter_number}, status='{self.status}')>"
    
    @property
    def word_count(self) -> int:
        """Get the word count of the chapter content"""
        if not self.content:
            return 0
        return len(self.content.split())
    
    def to_dict(self) -> dict:
        """Convert chapter to dictionary for API responses"""
        return {
            "id": str(self.id),
            "book_id": str(self.book_id),
            "chapter_number": self.chapter_number,
            "title": self.title,
            "content": self.content,
            "summary": self.summary,
            "chapter_notes": self.chapter_notes,
            "chapter_notes_status": self.chapter_notes_status,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "word_count": self.word_count
        }
    
    def get_previous_chapter_summary(self, session) -> str:
        """Get the summary of the previous chapter for context chaining"""
        if self.chapter_number <= 1:
            return ""
        
        previous_chapter = session.query(Chapter).filter(
            Chapter.book_id == self.book_id,
            Chapter.chapter_number == self.chapter_number - 1
        ).first()
        
        return previous_chapter.summary if previous_chapter else ""

# Database constraints and indexes
from sqlalchemy import Index, UniqueConstraint

# Add unique constraint for chapter numbers per book
Chapter.__table_args__ = (
    UniqueConstraint('book_id', 'chapter_number', name='uq_book_chapter'),
    Index('idx_book_status', 'status'),
    Index('idx_book_created', 'created_at'),
    Index('idx_chapter_book_status', 'book_id', 'status'),
    Index('idx_chapter_number', 'chapter_number'),
)
