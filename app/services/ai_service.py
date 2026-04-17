import openai
from typing import List, Optional, Dict, Any
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL

    async def generate_outline(self, title: str, notes: str) -> str:
        """Generate book outline based on title and notes"""
        prompt = f"""
        Generate a comprehensive and detailed outline for a book titled: "{title}"
        
        Additional notes and requirements: {notes}
        
        Please create a structured outline with:
        1. Main sections/chapters
        2. Sub-topics within each chapter
        3. Key points to cover
        4. Logical flow and progression
        
        The outline should be detailed enough to guide chapter generation while maintaining coherence throughout the book.
        """
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert book outline generator. Create detailed, well-structured outlines that serve as blueprints for comprehensive books."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating outline: {str(e)}")
            raise Exception(f"Failed to generate outline: {str(e)}")

    async def generate_chapter(self, 
                             title: str, 
                             outline: str, 
                             chapter_number: int, 
                             previous_summaries: List[str],
                             research_context: Optional[str] = None,
                             chapter_notes: Optional[str] = None) -> Dict[str, str]:
        """Generate a single chapter with context from previous chapters"""
        
        # Build context from previous chapters
        context = ""
        if previous_summaries:
            context = "Previous chapters summary:\n" + "\n".join([f"Chapter {i+1}: {summary}" for i, summary in enumerate(previous_summaries)])
        
        research_section = ""
        if research_context:
            research_section = f"\nResearch context to incorporate:\n{research_context}"
        
        notes_section = ""
        if chapter_notes:
            notes_section = f"\nSpecific notes for this chapter:\n{chapter_notes}"
        
        prompt = f"""
        Book Title: {title}
        
        Book Outline:
        {outline}
        
        {context}
        
        {research_section}
        
        {notes_section}
        
        Write Chapter {chapter_number} of this book. The chapter should:
        1. Be comprehensive and well-structured
        2. Flow naturally from previous chapters
        3. Incorporate the research context provided
        4. Address any specific notes mentioned
        5. Be engaging and informative
        6. Maintain consistency with the book's overall tone and style
        
        Please write the full chapter content.
        """
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert author writing a comprehensive book. Each chapter should be well-researched, engaging, and flow naturally from previous chapters."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=4000
            )
            
            content = response.choices[0].message.content.strip()
            
            # Generate summary for context chaining
            summary_prompt = f"Provide a concise summary of the following chapter for context in future chapters:\n\n{content}"
            
            summary_response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Create concise summaries that capture the main points and key information from chapters."},
                    {"role": "user", "content": summary_prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            summary = summary_response.choices[0].message.content.strip()
            
            return {
                "content": content,
                "summary": summary
            }
            
        except Exception as e:
            logger.error(f"Error generating chapter: {str(e)}")
            raise Exception(f"Failed to generate chapter: {str(e)}")

    async def regenerate_outline(self, title: str, notes: str, current_outline: str, feedback: str) -> str:
        """Regenerate outline based on feedback"""
        
        prompt = f"""
        Original book title: "{title}"
        Original notes: {notes}
        
        Current outline:
        {current_outline}
        
        Feedback for improvement:
        {feedback}
        
        Please regenerate the book outline incorporating the feedback. Make it more detailed, better structured, and address all the points mentioned in the feedback.
        """
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert book outline generator. Incorporate feedback to create improved, detailed outlines."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error regenerating outline: {str(e)}")
            raise Exception(f"Failed to regenerate outline: {str(e)}")

    async def regenerate_chapter(self, 
                                title: str, 
                                outline: str, 
                                chapter_number: int, 
                                previous_summaries: List[str],
                                current_content: str,
                                feedback: str,
                                research_context: Optional[str] = None) -> Dict[str, str]:
        """Regenerate a chapter based on feedback"""
        
        context = ""
        if previous_summaries:
            context = "Previous chapters summary:\n" + "\n".join([f"Chapter {i+1}: {summary}" for i, summary in enumerate(previous_summaries)])
        
        research_section = ""
        if research_context:
            research_section = f"\nResearch context to incorporate:\n{research_context}"
        
        prompt = f"""
        Book Title: {title}
        
        Book Outline:
        {outline}
        
        {context}
        
        {research_section}
        
        Current Chapter {chapter_number} content:
        {current_content}
        
        Feedback for improvement:
        {feedback}
        
        Please rewrite Chapter {chapter_number} incorporating the feedback. Address all the points mentioned and improve the quality, structure, and content.
        """
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert author revising book chapters based on feedback. Incorporate all suggestions to create improved content."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=4000
            )
            
            content = response.choices[0].message.content.strip()
            
            # Generate new summary
            summary_prompt = f"Provide a concise summary of the revised chapter:\n\n{content}"
            
            summary_response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Create concise summaries that capture the main points and key information from chapters."},
                    {"role": "user", "content": summary_prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            summary = summary_response.choices[0].message.content.strip()
            
            return {
                "content": content,
                "summary": summary
            }
            
        except Exception as e:
            logger.error(f"Error regenerating chapter: {str(e)}")
            raise Exception(f"Failed to regenerate chapter: {str(e)}")


# Global AI service instance
ai_service = AIService()
