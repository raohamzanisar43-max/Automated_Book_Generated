from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID

from app.api.deps import get_current_db_session, verify_token
from app.crud import book as book_crud, chapter as chapter_crud
from app.models import BookStatus, OutlineNotesStatus, ChapterNotesStatus
from app.schemas import (
    Book, BookCreate, BookUpdate, BookResponse,
    OutlineGenerationRequest, OutlineUpdateRequest,
    ChapterGenerationRequest, ChapterResponse,
    FinalReviewRequest, ExportRequest, SuccessResponse
)
from app.services import (
    ai_service, research_service, 
    notification_service, export_service
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/", response_model=BookResponse)
async def create_book(
    book_in: BookCreate,
    db: AsyncSession = Depends(get_current_db_session),
    current_user: dict = Depends(verify_token)
):
    """Create a new book and start outline generation"""
    try:
        # Create book record
        book = await book_crud.create(db, book_in)
        
        # Generate outline asynchronously
        try:
            outline = await ai_service.generate_outline(
                title=book.title,
                notes=book.notes_on_outline_before
            )
            
            # Update book with generated outline
            book_update = BookUpdate(
                outline=outline,
                status=BookStatus.review_outline
            )
            book = await book_crud.update(db, book, book_update)
            
            # Send notification
            await notification_service.notify_outline_ready(
                book_id=str(book.id),
                title=book.title
            )
            
        except Exception as e:
            logger.error(f"Error generating outline for book {book.id}: {str(e)}")
            # Update book status to error
            await book_crud.update_status(db, book.id, BookStatus.paused)
            
            await notification_service.notify_error(
                book_id=str(book.id),
                title=book.title,
                error_message=f"Outline generation failed: {str(e)}"
            )
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate outline: {str(e)}"
            )
        
        return book
        
    except Exception as e:
        logger.error(f"Error creating book: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create book: {str(e)}"
        )

@router.get("/", response_model=List[BookResponse])
async def get_books(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_current_db_session),
    current_user: dict = Depends(verify_token)
):
    """Get all books with pagination"""
    try:
        books = await book_crud.get_multi(db, skip=skip, limit=limit)
        return books
    except Exception as e:
        logger.error(f"Error getting books: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get books: {str(e)}"
        )

@router.get("/{book_id}", response_model=BookResponse)
async def get_book(
    book_id: UUID,
    db: AsyncSession = Depends(get_current_db_session),
    current_user: dict = Depends(verify_token)
):
    """Get a specific book by ID"""
    try:
        book = await book_crud.get(db, book_id)
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book not found"
            )
        return book
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting book {book_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get book: {str(e)}"
        )

@router.put("/{book_id}/outline", response_model=BookResponse)
async def update_outline(
    book_id: UUID,
    outline_update: OutlineUpdateRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_current_db_session),
    current_user: dict = Depends(verify_token)
):
    """Update outline with feedback and regenerate if needed"""
    try:
        book = await book_crud.get(db, book_id)
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book not found"
            )
        
        # Update outline and notes
        book_update = BookUpdate(
            outline=outline_update.outline,
            notes_on_outline_after=outline_update.notes_on_outline_after,
            status_outline_notes=outline_update.status_outline_notes
        )
        
        book = await book_crud.update(db, book, book_update)
        
        # Handle status logic
        if outline_update.status_outline_notes == OutlineNotesStatus.no_notes_needed:
            # Proceed to chapter generation
            await book_crud.update_status(db, book_id, BookStatus.generating_chapters)
            
            # Start chapter generation in background
            background_tasks.add_task(
                start_chapter_generation,
                str(book_id),
                book.title,
                book.outline
            )
            
        elif outline_update.status_outline_notes == OutlineNotesStatus.yes:
            # Wait for notes
            await book_crud.update_status(db, book_id, BookStatus.paused)
            
            await notification_service.notify_waiting_for_notes(
                book_id=str(book_id),
                title=book.title,
                stage="outline review"
            )
            
        elif outline_update.status_outline_notes == OutlineNotesStatus.no:
            # Pause workflow
            await book_crud.update_status(db, book_id, BookStatus.paused)
            
            await notification_service.notify_waiting_for_notes(
                book_id=str(book_id),
                title=book.title,
                stage="outline approval needed"
            )
        
        return book
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating outline for book {book_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update outline: {str(e)}"
        )

@router.post("/{book_id}/regenerate-outline", response_model=BookResponse)
async def regenerate_outline(
    book_id: UUID,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_current_db_session),
    current_user: dict = Depends(verify_token)
):
    """Regenerate outline based on feedback"""
    try:
        book = await book_crud.get(db, book_id)
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book not found"
            )
        
        if not book.notes_on_outline_after:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No feedback available for regeneration"
            )
        
        # Regenerate outline
        new_outline = await ai_service.regenerate_outline(
            title=book.title,
            notes=book.notes_on_outline_before,
            current_outline=book.outline,
            feedback=book.notes_on_outline_after
        )
        
        # Update book with new outline
        book_update = BookUpdate(
            outline=new_outline,
            status=BookStatus.review_outline
        )
        
        book = await book_crud.update(db, book, book_update)
        
        # Send notification
        await notification_service.notify_outline_ready(
            book_id=str(book.id),
            title=book.title
        )
        
        return book
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error regenerating outline for book {book_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to regenerate outline: {str(e)}"
        )

@router.get("/{book_id}/chapters", response_model=List[ChapterResponse])
async def get_book_chapters(
    book_id: UUID,
    db: AsyncSession = Depends(get_current_db_session),
    current_user: dict = Depends(verify_token)
):
    """Get all chapters for a book"""
    try:
        chapters = await chapter_crud.get_multi_by_book(db, book_id)
        return chapters
    except Exception as e:
        logger.error(f"Error getting chapters for book {book_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get chapters: {str(e)}"
        )

@router.post("/{book_id}/chapters/{chapter_number}", response_model=ChapterResponse)
async def generate_chapter(
    book_id: UUID,
    chapter_number: int,
    chapter_request: ChapterGenerationRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_current_db_session),
    current_user: dict = Depends(verify_token)
):
    """Generate a specific chapter"""
    try:
        book = await book_crud.get(db, book_id)
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book not found"
            )
        
        # Check if chapter already exists
        existing_chapter = await chapter_crud.get_by_book_and_number(db, book_id, chapter_number)
        if existing_chapter:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Chapter {chapter_number} already exists"
            )
        
        # Get previous chapter summaries for context
        previous_summaries = await chapter_crud.get_previous_summaries(db, book_id, chapter_number)
        
        # Research chapter topic if web search is available
        research_context = None
        try:
            chapter_topic = f"Chapter {chapter_number} of {book.title}"
            research_context = await research_service.research_chapter_topic(
                book.title, chapter_topic
            )
        except Exception as e:
            logger.warning(f"Research failed for chapter {chapter_number}: {str(e)}")
        
        # Generate chapter
        chapter_data = await ai_service.generate_chapter(
            title=book.title,
            outline=book.outline,
            chapter_number=chapter_number,
            previous_summaries=previous_summaries,
            research_context=research_context,
            chapter_notes=chapter_request.chapter_notes
        )
        
        # Create chapter record
        chapter_create = {
            "book_id": str(book_id),
            "chapter_number": chapter_number,
            "title": f"Chapter {chapter_number}",
            "content": chapter_data["content"],
            "summary": chapter_data["summary"],
            "chapter_notes_status": chapter_request.chapter_notes_status
        }
        
        chapter = await chapter_crud.create(db, chapter_create)
        
        # Send notification
        await notification_service.notify_chapter_ready(
            book_id=str(book_id),
            title=book.title,
            chapter_number=chapter_number
        )
        
        return chapter
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating chapter {chapter_number} for book {book_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate chapter: {str(e)}"
        )

@router.put("/{book_id}/final-review", response_model=BookResponse)
async def final_review(
    book_id: UUID,
    final_review: FinalReviewRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_current_db_session),
    current_user: dict = Depends(verify_token)
):
    """Handle final review and compilation"""
    try:
        book = await book_crud.get(db, book_id)
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book not found"
            )
        
        # Update final review status
        book_update = BookUpdate(
            final_review_notes_status=final_review.final_review_notes_status,
            final_review_notes=final_review.final_review_notes
        )
        
        book = await book_crud.update(db, book, book_update)
        
        # Handle final review logic
        if final_review.final_review_notes_status == OutlineNotesStatus.no_notes_needed:
            # Proceed to compilation
            await book_crud.update_status(db, book_id, BookStatus.compiling)
            
            # Start compilation in background
            background_tasks.add_task(
                compile_book,
                str(book_id),
                book.title
            )
            
        else:
            # Wait for final notes
            await book_crud.update_status(db, book_id, BookStatus.paused)
            
            await notification_service.notify_waiting_for_notes(
                book_id=str(book_id),
                title=book.title,
                stage="final review"
            )
        
        return book
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in final review for book {book_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process final review: {str(e)}"
        )

@router.post("/{book_id}/export", response_model=SuccessResponse)
async def export_book(
    book_id: UUID,
    export_request: ExportRequest,
    db: AsyncSession = Depends(get_current_db_session),
    current_user: dict = Depends(verify_token)
):
    """Export book in specified format"""
    try:
        book = await book_crud.get(db, book_id)
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book not found"
            )
        
        # Get all chapters
        chapters = await chapter_crud.get_multi_by_book(db, book_id)
        if not chapters:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No chapters found for this book"
            )
        
        # Export book
        chapters_data = [
            {
                "chapter_number": ch.chapter_number,
                "title": ch.title,
                "content": ch.content
            }
            for ch in chapters if ch.content
        ]
        
        file_path = export_service.export_book(
            title=book.title,
            chapters=chapters_data,
            format=export_request.format
        )
        
        # Update book with file URL
        book_update = BookUpdate(
            book_output_status="completed",
            file_url=file_path
        )
        await book_crud.update(db, book, book_update)
        
        # Send notification
        await notification_service.notify_book_completed(
            book_id=str(book_id),
            title=book.title,
            file_url=file_path
        )
        
        return SuccessResponse(
            message=f"Book exported successfully to {export_request.format.upper()} format",
            data={"file_path": file_path, "format": export_request.format}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting book {book_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export book: {str(e)}"
        )

# Background task functions
async def start_chapter_generation(book_id: str, title: str, outline: str):
    """Background task to start chapter generation process"""
    from app.database import AsyncSessionLocal
    
    async with AsyncSessionLocal() as db:
        try:
            # Parse outline to determine number of chapters (simplified)
            # In a real implementation, you'd parse the outline more intelligently
            chapter_count = outline.count("Chapter") + 1  # Simple heuristic
            
            for chapter_num in range(1, chapter_count + 1):
                # Check if chapter already exists
                existing = await chapter_crud.get_by_book_and_number(
                    db, UUID(book_id), chapter_num
                )
                if existing:
                    continue
                
                # Get previous summaries
                previous_summaries = await chapter_crud.get_previous_summaries(
                    db, UUID(book_id), chapter_num
                )
                
                # Generate chapter
                chapter_data = await ai_service.generate_chapter(
                    title=title,
                    outline=outline,
                    chapter_number=chapter_num,
                    previous_summaries=previous_summaries
                )
                
                # Create chapter
                chapter_create = {
                    "book_id": book_id,
                    "chapter_number": chapter_num,
                    "title": f"Chapter {chapter_num}",
                    "content": chapter_data["content"],
                    "summary": chapter_data["summary"],
                    "chapter_notes_status": ChapterNotesStatus.no_notes_needed
                }
                
                await chapter_crud.create(db, chapter_create)
                
                # Send notification
                await notification_service.notify_chapter_ready(
                    book_id=book_id,
                    title=title,
                    chapter_number=chapter_num
                )
            
            # Update book status
            await book_crud.update_status(db, UUID(book_id), BookStatus.reviewing_chapters)
            
        except Exception as e:
            logger.error(f"Error in background chapter generation for book {book_id}: {str(e)}")
            await book_crud.update_status(db, UUID(book_id), BookStatus.paused)
            
            await notification_service.notify_error(
                book_id=book_id,
                title=title,
                error_message=f"Chapter generation failed: {str(e)}"
            )

async def compile_book(book_id: str, title: str):
    """Background task to compile book"""
    from app.database import AsyncSessionLocal
    
    async with AsyncSessionLocal() as db:
        try:
            # Get chapters
            chapters = await chapter_crud.get_multi_by_book(db, UUID(book_id))
            
            chapters_data = [
                {
                    "chapter_number": ch.chapter_number,
                    "title": ch.title,
                    "content": ch.content
                }
                for ch in chapters if ch.content
            ]
            
            # Export to DOCX
            file_path = export_service.export_book(
                title=title,
                chapters=chapters_data,
                format="docx"
            )
            
            # Update book
            book_update = BookUpdate(
                book_output_status="completed",
                file_url=file_path
            )
            await book_crud.update(db, await book_crud.get(db, UUID(book_id)), book_update)
            
            # Update status
            await book_crud.update_status(db, UUID(book_id), BookStatus.completed)
            
            # Send notification
            await notification_service.notify_book_completed(
                book_id=book_id,
                title=title,
                file_url=file_path
            )
            
        except Exception as e:
            logger.error(f"Error compiling book {book_id}: {str(e)}")
            await book_crud.update_status(db, UUID(book_id), BookStatus.paused)
            
            await notification_service.notify_error(
                book_id=book_id,
                title=title,
                error_message=f"Book compilation failed: {str(e)}"
            )
