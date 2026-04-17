from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
from typing import List, Optional
from uuid import UUID
from app.models import Book, Chapter, BookStatus, OutlineNotesStatus, ChapterNotesStatus
from app.schemas import BookCreate, BookUpdate, ChapterCreate, ChapterUpdate
import logging

logger = logging.getLogger(__name__)

class CRUDBook:
    async def get(self, db: AsyncSession, id: UUID) -> Optional[Book]:
        """Get a book by ID"""
        result = await db.execute(select(Book).filter(Book.id == id))
        return result.scalar_one_or_none()

    async def get_multi(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Book]:
        """Get multiple books with pagination"""
        result = await db.execute(
            select(Book).offset(skip).limit(limit).order_by(Book.created_at.desc())
        )
        return result.scalars().all()

    async def create(self, db: AsyncSession, obj_in: BookCreate) -> Book:
        """Create a new book"""
        db_obj = Book(
            title=obj_in.title,
            notes_on_outline_before=obj_in.notes_on_outline_before,
            status=BookStatus.draft_outline
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(self, db: AsyncSession, db_obj: Book, obj_in: BookUpdate) -> Book:
        """Update a book"""
        update_data = obj_in.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, id: UUID) -> Optional[Book]:
        """Delete a book"""
        obj = await self.get(db, id)
        if obj:
            await db.delete(obj)
            await db.commit()
        return obj

    async def update_status(self, db: AsyncSession, id: UUID, status: BookStatus) -> Book:
        """Update book status"""
        stmt = (
            update(Book)
            .where(Book.id == id)
            .values(status=status)
            .returning(Book)
        )
        result = await db.execute(stmt)
        await db.commit()
        return result.scalar_one()

    async def get_by_status(self, db: AsyncSession, status: BookStatus) -> List[Book]:
        """Get books by status"""
        result = await db.execute(
            select(Book).filter(Book.status == status).order_by(Book.created_at.desc())
        )
        return result.scalars().all()


class CRUDChapter:
    async def get(self, db: AsyncSession, id: UUID) -> Optional[Chapter]:
        """Get a chapter by ID"""
        result = await db.execute(select(Chapter).filter(Chapter.id == id))
        return result.scalar_one_or_none()

    async def get_by_book_and_number(self, db: AsyncSession, book_id: UUID, chapter_number: int) -> Optional[Chapter]:
        """Get a chapter by book ID and chapter number"""
        result = await db.execute(
            select(Chapter)
            .filter(Chapter.book_id == book_id, Chapter.chapter_number == chapter_number)
        )
        return result.scalar_one_or_none()

    async def get_multi_by_book(self, db: AsyncSession, book_id: UUID) -> List[Chapter]:
        """Get all chapters for a book, ordered by chapter number"""
        result = await db.execute(
            select(Chapter)
            .filter(Chapter.book_id == book_id)
            .order_by(Chapter.chapter_number)
        )
        return result.scalars().all()

    async def get_previous_summaries(self, db: AsyncSession, book_id: UUID, current_chapter: int) -> List[str]:
        """Get summaries of all previous chapters for context"""
        result = await db.execute(
            select(Chapter.summary)
            .filter(
                Chapter.book_id == book_id,
                Chapter.chapter_number < current_chapter,
                Chapter.summary.isnot(None)
            )
            .order_by(Chapter.chapter_number)
        )
        return [summary[0] for summary in result.fetchall() if summary[0]]

    async def create(self, db: AsyncSession, obj_in: ChapterCreate) -> Chapter:
        """Create a new chapter"""
        db_obj = Chapter(
            book_id=obj_in.book_id,
            chapter_number=obj_in.chapter_number,
            title=obj_in.title,
            content=obj_in.content,
            summary=obj_in.summary,
            chapter_notes=obj_in.chapter_notes,
            chapter_notes_status=obj_in.chapter_notes_status
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(self, db: AsyncSession, db_obj: Chapter, obj_in: ChapterUpdate) -> Chapter:
        """Update a chapter"""
        update_data = obj_in.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, id: UUID) -> Optional[Chapter]:
        """Delete a chapter"""
        obj = await self.get(db, id)
        if obj:
            await db.delete(obj)
            await db.commit()
        return obj

    async def get_next_chapter_number(self, db: AsyncSession, book_id: UUID) -> int:
        """Get the next chapter number for a book"""
        result = await db.execute(
            select(Chapter.chapter_number)
            .filter(Chapter.book_id == book_id)
            .order_by(Chapter.chapter_number.desc())
        )
        last_chapter = result.scalar_one_or_none()
        return (last_chapter or 0) + 1


# Create CRUD instances
book = CRUDBook()
chapter = CRUDChapter()
