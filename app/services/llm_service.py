from openai import AsyncOpenAI
from app.config import settings
from typing import Optional

client = AsyncOpenAI(api_key=settings.openai_api_key)
MODEL = settings.openai_model

async def generate_outline(title: str, notes: str) -> str:
    prompt = f"You are a professional book editor and author. Generate a detailed chapter-by-chapter outline for a book titled '{title}'.\n"
    if notes:
        prompt += f"Consider the following notes and instructions while generating the outline:\n{notes}\n"
        
    response = await client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You output professional book outlines."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content

async def regenerate_outline(title: str, current_outline: str, notes_after: str) -> str:
    prompt = f"You are a professional book editor. Here is the current outline for the book titled '{title}':\n\n{current_outline}\n\n"
    prompt += f"Please revise the outline strictly following these new notes and feedback from the editor:\n{notes_after}\n"
    prompt += "Output the complete revised outline."
    
    response = await client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You output professional book outlines."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content

async def generate_chapter(title: str, outline: str, chapter_number: int, prev_summaries: str, notes: Optional[str] = None) -> str:
    prompt = f"We are writing a book titled '{title}'.\n"
    prompt += f"Here is the full outline:\n{outline}\n\n"
    if prev_summaries:
        prompt += f"Here are the summaries of the previous chapters to maintain context:\n{prev_summaries}\n\n"
    
    prompt += f"Your task is to write Chapter {chapter_number} in a highly professional, engaging tone."
    if notes:
        prompt += f"\nFollow these specific instructions for this chapter:\n{notes}"
        
    response = await client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are an expert author drafting a book chapter."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content

async def summarize_chapter(chapter_number: int, chapter_content: str) -> str:
    prompt = f"Provide a brief but comprehensive summary of the following content for Chapter {chapter_number}, which will be used as context for the next chapters.\n\n{chapter_content}"
    
    response = await client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You summarize book chapters accurately."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )
    return response.choices[0].message.content
