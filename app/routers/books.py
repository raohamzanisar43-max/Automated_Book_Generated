from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from uuid import UUID

from app.database import get_db
from app.models import Book, Chapter, BookStatus, OutlineNotesStatus, ChapterNotesStatus
from app.schemas import BookCreate, BookResponse, OutlineReview, ChapterResponse, ChapterReview, FinalReview
from app.services import llm_service, notification_service, export_service

router = APIRouter(prefix="/books", tags=["Books"])

@router.post("/", response_model=BookResponse)
async def create_book(book_in: BookCreate, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    if not book_in.notes_on_outline_before:
        raise HTTPException(status_code=400, detail="notes_on_outline_before is mandatory for Outline stage")
        
    db_book = Book(
        title=book_in.title,
        notes_on_outline_before=book_in.notes_on_outline_before,
        status=BookStatus.draft_outline
    )
    db.add(db_book)
    await db.commit()
    await db.refresh(db_book)
    
    # Background generation
    async def generate_and_save_outline(book_id: UUID):
        async with db.bind.connect() as conn: # Better to use a fresh session in a real app
            # Re-fetching book in background
            session = AsyncSession(db.bind, expire_on_commit=False)
            book = await session.get(Book, book_id)
            try:
                outline_text = await llm_service.generate_outline(book.title, book.notes_on_outline_before)
                book.outline = outline_text
                book.status = BookStatus.review_outline
                await session.commit()
                notification_service.notify_review_required(book.title, "Outline", str(book.id))
            except Exception as e:
                book.status = BookStatus.paused
                await session.commit()
                notification_service.notify_workflow_paused(book.title, f"Outline generation failed: {str(e)}")
            finally:
                await session.close()
                
    background_tasks.add_task(generate_and_save_outline, db_book.id)
    return db_book

@router.put("/{book_id}/outline", response_model=BookResponse)
async def review_outline(book_id: UUID, review: OutlineReview, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    book = await db.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
        
    book.status_outline_notes = review.status_outline_notes
    if review.notes_on_outline_after:
        book.notes_on_outline_after = review.notes_on_outline_after
        
    if review.status_outline_notes == OutlineNotesStatus.yes:
        if not review.notes_on_outline_after:
            raise HTTPException(status_code=400, detail="notes_on_outline_after required when status is 'yes'")
        
        # Regenerate outline
        book.status = BookStatus.draft_outline
        await db.commit()
        
        async def regenerate_and_save(b_id: UUID):
             session = AsyncSession(db.bind, expire_on_commit=False)
             b = await session.get(Book, b_id)
             try:
                 new_outline = await llm_service.regenerate_outline(b.title, b.outline, b.notes_on_outline_after)
                 b.outline = new_outline
                 b.status = BookStatus.review_outline
                 await session.commit()
                 notification_service.notify_review_required(b.title, "Revised Outline", str(b.id))
             except Exception as e:
                 b.status = BookStatus.paused
                 await session.commit()
             finally:
                 await session.close()
                 
        background_tasks.add_task(regenerate_and_save, book.id)
        
    elif review.status_outline_notes == OutlineNotesStatus.no_notes_needed:
        book.status = BookStatus.generating_chapters
        await db.commit()
        
    elif review.status_outline_notes == OutlineNotesStatus.no:
        book.status = BookStatus.paused
        await db.commit()
        notification_service.notify_workflow_paused(book.title, "Outline marked NO, paused.")

    await db.refresh(book)
    return book

@router.post("/{book_id}/chapters", response_model=ChapterResponse)
async def generate_next_chapter(book_id: UUID, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    book = await db.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
        
    if book.status not in [BookStatus.generating_chapters, BookStatus.reviewing_chapters]:
        raise HTTPException(status_code=400, detail="Book not ready for chapter generation")
        
    result = await db.execute(select(Chapter).filter(Chapter.book_id == book_id).order_by(Chapter.chapter_number.desc()))
    chapters = result.scalars().all()
    next_chapter_number = 1 if not chapters else chapters[0].chapter_number + 1
    
    # Combine prev summaries
    prev_summaries = "\\n\\n".join([f"Chapter {c.chapter_number} Summary: {c.summary}" for c in chapters if c.summary])
    
    new_chapter = Chapter(
        book_id=book.id,
        chapter_number=next_chapter_number
    )
    db.add(new_chapter)
    await db.commit()
    await db.refresh(new_chapter)
    
    book.status = BookStatus.generating_chapters
    await db.commit()
    
    async def generate_chapter_task(b_id: UUID, c_id: UUID, p_sums: str):
        session = AsyncSession(db.bind, expire_on_commit=False)
        b = await session.get(Book, b_id)
        c = await session.get(Chapter, c_id)
        try:
            content = await llm_service.generate_chapter(b.title, b.outline, c.chapter_number, p_sums)
            c.content = content
            
            summary = await llm_service.summarize_chapter(c.chapter_number, content)
            c.summary = summary
            
            b.status = BookStatus.reviewing_chapters
            await session.commit()
            notification_service.notify_review_required(b.title, f"Chapter {c.chapter_number}", str(c.id))
        except Exception as e:
            b.status = BookStatus.paused
            await session.commit()
        finally:
            await session.close()
            
    background_tasks.add_task(generate_chapter_task, book.id, new_chapter.id, prev_summaries)
    
    return new_chapter

@router.put("/{book_id}/chapters/{chapter_id}", response_model=ChapterResponse)
async def review_chapter(book_id: UUID, chapter_id: UUID, review: ChapterReview, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    chapter = await db.get(Chapter, chapter_id)
    if not chapter or chapter.book_id != book_id:
        raise HTTPException(status_code=404, detail="Chapter not found")
        
    chapter.chapter_notes_status = review.chapter_notes_status
    if review.chapter_notes:
        chapter.chapter_notes = review.chapter_notes
        
    book = await db.get(Book, book_id)
        
    if review.chapter_notes_status == ChapterNotesStatus.yes:
        # Regenerate chapter
        book.status = BookStatus.generating_chapters
        await db.commit()
        
        result = await db.execute(select(Chapter).filter(Chapter.book_id == book_id, Chapter.chapter_number < chapter.chapter_number).order_by(Chapter.chapter_number))
        prev_chapters = result.scalars().all()
        prev_summaries = "\\n\\n".join([f"Chapter {c.chapter_number} Summary: {c.summary}" for c in prev_chapters if c.summary])
        
        async def regenerate_chapter_task(b_id: UUID, c_id: UUID, p_sums: str, notes: str):
            session = AsyncSession(db.bind, expire_on_commit=False)
            b = await session.get(Book, b_id)
            c = await session.get(Chapter, c_id)
            try:
                content = await llm_service.generate_chapter(b.title, b.outline, c.chapter_number, p_sums, notes)
                c.content = content
                
                summary = await llm_service.summarize_chapter(c.chapter_number, content)
                c.summary = summary
                
                b.status = BookStatus.reviewing_chapters
                await session.commit()
                notification_service.notify_review_required(b.title, f"Revised Chapter {c.chapter_number}", str(c.id))
            except Exception as e:
                b.status = BookStatus.paused
                await session.commit()
            finally:
                await session.close()
        
        background_tasks.add_task(regenerate_chapter_task, book.id, chapter.id, prev_summaries, review.chapter_notes)
        
    elif review.chapter_notes_status == ChapterNotesStatus.no_notes_needed:
        # ready for next chapter or compilation
        book.status = BookStatus.generating_chapters
        await db.commit()
    elif review.chapter_notes_status == ChapterNotesStatus.no:
        book.status = BookStatus.paused
        await db.commit()
        
    await db.refresh(chapter)
    return chapter

@router.post("/{book_id}/compile", response_model=BookResponse)
async def compile_book(book_id: UUID, review: FinalReview, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    book = await db.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
        
    book.final_review_notes_status = review.final_review_notes_status
    
    if review.final_review_notes_status == OutlineNotesStatus.no_notes_needed:
        book.status = BookStatus.compiling
        await db.commit()
        
        async def compile_task(b_id: str):
            session = AsyncSession(db.bind, expire_on_commit=False)
            b = await session.get(Book, b_id)
            try:
                filepath = await export_service.compile_book(session, b_id, "docx")
                b.file_url = filepath
                b.status = BookStatus.completed
                b.book_output_status = "ready"
                await session.commit()
                notification_service.notify_compilation_ready(b.title, filepath)
            except Exception as e:
                b.status = BookStatus.paused
                b.book_output_status = f"failed: {str(e)}"
                await session.commit()
            finally:
                await session.close()
                
        background_tasks.add_task(compile_task, str(book.id))
    else:
        book.status = BookStatus.paused
        await db.commit()
        
    return book
