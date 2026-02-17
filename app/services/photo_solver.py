"""
Photo Solver Service - Multi-Subject Question Solver using Gemini Vision

Supports ALL CBSE Class 10 subjects:
- Mathematics
- Physics
- Chemistry
- Biology
- Social Science (History, Geography, Civics, Economics)
- English (Grammar, Literature, Writing)

Uses Gemini 2.0 Flash Vision (multimodal) for:
- OCR (extract text from images)
- Question understanding
- Step-by-step solutions
- Visual diagram analysis (geometry, graphs, etc.)
"""

from __future__ import annotations

import base64
import hashlib
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.core.config import settings
from app.core.database import get_db

logger = logging.getLogger(__name__)


@dataclass
class SolvedQuestion:
    """Result of photo solving"""
    success: bool
    question_text: Optional[str] = None
    subject: Optional[str] = None
    chapter: Optional[str] = None
    solution: Optional[str] = None
    explanation: Optional[str] = None
    key_concepts: Optional[List[str]] = None
    difficulty_level: Optional[float] = None  # 0.0 to 1.0
    language: Optional[str] = None  # Detected language
    error: Optional[str] = None
    confidence: Optional[float] = None  # AI confidence in solution (0.0 to 1.0)


class PhotoSolver:
    """
    Multi-subject question solver using Gemini Vision

    Features:
    - Supports images: JPG, PNG, HEIC, WebP
    - Handles handwritten and printed text
    - Extracts diagrams, graphs, tables
    - Provides step-by-step solutions
    - Stores solved questions in database
    - Works with all CBSE Class 10 subjects
    """

    # Subject-specific prompt engineering
    SUBJECT_PROMPTS = {
        "mathematics": """
You are an expert CBSE Class 10 Mathematics teacher analyzing a question from an image.

TASK:
1. Extract the complete question text (including numbers, symbols, units)
2. Identify the chapter/topic (e.g., "Quadratic Equations", "Trigonometry", "Coordinate Geometry")
3. Provide a COMPLETE step-by-step solution with:
   - Clear mathematical reasoning at each step
   - All calculations shown
   - Diagrams/graphs if needed (describe in text)
   - Final answer highlighted
4. List key concepts used (e.g., "Quadratic Formula", "Pythagoras Theorem")
5. Estimate difficulty (0.0=very easy, 1.0=very hard)

RESPONSE FORMAT (JSON):
```json
{
    "question_text": "Full question extracted from image",
    "subject": "mathematics",
    "chapter": "Chapter name",
    "solution": "Step-by-step solution with LaTeX math",
    "explanation": "Why this approach works (conceptual understanding)",
    "key_concepts": ["Concept1", "Concept2"],
    "difficulty_level": 0.6,
    "language": "english",
    "confidence": 0.95
}
```

Use LaTeX notation for math: $x = \\frac{-b \\pm \\sqrt{b^2-4ac}}{2a}$
""",
        "physics": """
You are an expert CBSE Class 10 Physics teacher analyzing a question from an image.

TASK:
1. Extract the complete question (including numerical values, units, diagrams)
2. Identify the chapter (e.g., "Light", "Electricity", "Magnetic Effects of Current")
3. Provide detailed solution with:
   - Given data clearly listed
   - Formulas used (with derivations if needed)
   - All calculations with units
   - Circuit diagrams or ray diagrams (describe in text)
   - Final answer with correct units
4. List physics concepts/laws used
5. Estimate difficulty

RESPONSE FORMAT (JSON):
Same as Mathematics, but with "subject": "physics"

Important:
- Always include units (m, kg, s, A, V, Ω, etc.)
- Show unit conversions if needed
- Explain physical intuition behind formulas
""",
        "chemistry": """
You are an expert CBSE Class 10 Chemistry teacher analyzing a question from an image.

TASK:
1. Extract the question (chemical equations, reactions, molecular structures)
2. Identify chapter (e.g., "Chemical Reactions", "Acids, Bases and Salts", "Periodic Classification")
3. Provide solution with:
   - Balanced chemical equations
   - Step-by-step reaction mechanism
   - Molecular diagrams/electron configurations (describe in text)
   - Calculations with proper significant figures
   - Final answer
4. List chemistry concepts (e.g., "Redox Reaction", "pH Scale", "Covalent Bonding")
5. Estimate difficulty

RESPONSE FORMAT (JSON):
Same as Mathematics, but with "subject": "chemistry"

Important:
- Balance all chemical equations
- Include states of matter (s, l, g, aq)
- Show oxidation states if relevant
""",
        "biology": """
You are an expert CBSE Class 10 Biology teacher analyzing a question from an image.

TASK:
1. Extract the question (diagrams, labels, descriptions)
2. Identify chapter (e.g., "Life Processes", "Heredity and Evolution", "Human Reproductive System")
3. Provide solution with:
   - Labeled diagrams (describe structure in text)
   - Step-by-step explanation
   - Key biological processes
   - Examples from nature
   - Final answer
4. List biology concepts (e.g., "Photosynthesis", "Mendelian Genetics", "Natural Selection")
5. Estimate difficulty

RESPONSE FORMAT (JSON):
Same as Mathematics, but with "subject": "biology"

Important:
- Use proper biological terminology
- Explain processes clearly
- Include real-world examples
""",
        "social_science": """
You are an expert CBSE Class 10 Social Science teacher analyzing a question from an image.

Covers: History, Geography, Civics (Political Science), Economics

TASK:
1. Extract the question (maps, timelines, data tables, passages)
2. Identify chapter and sub-subject
3. Provide solution with:
   - Historical context or geographical explanation
   - Key events, people, places, concepts
   - Map descriptions if applicable
   - Data analysis if given tables/graphs
   - Well-structured answer (intro, body, conclusion)
4. List key concepts
5. Estimate difficulty

RESPONSE FORMAT (JSON):
Same as Mathematics, but with "subject": "social_science"

Important:
- Use proper historical dates and terminology
- Explain cause-effect relationships
- Include multiple perspectives if relevant
""",
        "english": """
You are an expert CBSE Class 10 English teacher analyzing a question from an image.

Covers: Grammar, Literature (Poetry, Prose), Writing (Essays, Letters, Articles)

TASK:
1. Extract the question (passages, poems, grammar exercises, writing prompts)
2. Identify type (Grammar, Literature, Writing)
3. Provide solution with:
   - For Grammar: Rules explained, correct answers, examples
   - For Literature: Analysis of themes, characters, literary devices, context
   - For Writing: Sample answer/essay, structure tips, key points
4. List key concepts (e.g., "Figures of Speech", "Tenses", "Formal Letter Format")
5. Estimate difficulty

RESPONSE FORMAT (JSON):
Same as Mathematics, but with "subject": "english"

Important:
- Use proper English language terminology
- Provide comprehensive literary analysis
- Give well-structured writing samples
"""
    }

    def __init__(self):
        """Initialize PhotoSolver with Gemini Vision client"""
        try:
            from google import genai

            if settings.GEMINI_API_KEY:
                self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
                logger.info("PhotoSolver initialized with Gemini Vision")
            else:
                self.client = None
                logger.warning("PhotoSolver: Gemini API key not configured")

        except ImportError:
            self.client = None
            logger.error("PhotoSolver: google-genai package not installed")

    async def solve_from_image(
        self,
        image_data: bytes,
        subject: str = "mathematics",
        session_id: Optional[str] = None,
        language: str = "english",
        store_in_db: bool = True
    ) -> SolvedQuestion:
        """
        Solve question from image using Gemini Vision

        Args:
            image_data: Image bytes (JPG, PNG, HEIC, WebP)
            subject: Subject area (mathematics, physics, chemistry, biology, social_science, english)
            session_id: Optional session ID to link to student
            language: Preferred response language (english, hinglish, etc.)
            store_in_db: Whether to store solved question in database

        Returns:
            SolvedQuestion with solution or error
        """
        if not self.client:
            return SolvedQuestion(
                success=False,
                error="Gemini Vision not configured. Set GEMINI_API_KEY in .env"
            )

        if subject not in self.SUBJECT_PROMPTS:
            return SolvedQuestion(
                success=False,
                error=f"Subject '{subject}' not supported. Available: {list(self.SUBJECT_PROMPTS.keys())}"
            )

        try:
            # Prepare image for Gemini
            image_b64 = base64.b64encode(image_data).decode('utf-8')

            # Get subject-specific prompt
            system_prompt = self.SUBJECT_PROMPTS[subject]

            # Add language preference
            if language != "english":
                system_prompt += f"\n\nIMPORTANT: Respond in {language.upper()} (mix local language with English naturally)."

            # Call Gemini Vision
            response = self.client.models.generate_content(
                model="gemini-2.0-flash-exp",  # Vision-capable model
                contents=[
                    system_prompt,
                    {
                        "mime_type": "image/jpeg",  # Auto-detected by Gemini
                        "data": image_b64
                    }
                ],
                config={
                    "temperature": 0.3,  # Lower temperature for accuracy
                    "response_mime_type": "application/json"  # Request JSON response
                }
            )

            # Parse JSON response
            import json
            result_json = json.loads(response.text)

            # Validate required fields
            if not all(k in result_json for k in ["question_text", "subject", "solution"]):
                return SolvedQuestion(
                    success=False,
                    error="Gemini response missing required fields"
                )

            # Create SolvedQuestion object
            solved = SolvedQuestion(
                success=True,
                question_text=result_json.get("question_text"),
                subject=result_json.get("subject"),
                chapter=result_json.get("chapter"),
                solution=result_json.get("solution"),
                explanation=result_json.get("explanation"),
                key_concepts=result_json.get("key_concepts", []),
                difficulty_level=result_json.get("difficulty_level", 0.5),
                language=result_json.get("language", language),
                confidence=result_json.get("confidence", 0.9)
            )

            # Store in database if requested
            if store_in_db and session_id:
                await self._store_solved_question(solved, session_id, image_data)

            logger.info(f"Photo solved successfully: subject={subject}, confidence={solved.confidence}")
            return solved

        except json.JSONDecodeError as exc:
            logger.error(f"Failed to parse Gemini JSON response: {exc}")
            # Return raw text as solution
            return SolvedQuestion(
                success=True,
                question_text="[Could not extract]",
                subject=subject,
                solution=response.text,  # Fallback to raw text
                explanation="Gemini response was not in JSON format",
                confidence=0.7
            )

        except Exception as exc:
            logger.exception(f"Photo solving failed: {exc}")
            return SolvedQuestion(
                success=False,
                error=f"Photo solving failed: {str(exc)}"
            )

    async def _store_solved_question(
        self,
        solved: SolvedQuestion,
        session_id: str,
        image_data: bytes
    ):
        """Store solved question in database for future reference"""
        try:
            db = get_db()

            # Create hash of image for deduplication
            image_hash = hashlib.sha256(image_data).hexdigest()

            # Check if already solved
            existing = db.table('solved_questions').select('id').eq('image_hash', image_hash).execute()

            if existing.data and len(existing.data) > 0:
                logger.info(f"Question already solved: image_hash={image_hash}")
                return

            # Store new solved question
            record = {
                'session_id': session_id,
                'image_hash': image_hash,
                'subject': solved.subject,
                'chapter': solved.chapter,
                'question_text': solved.question_text,
                'solution': solved.solution,
                'explanation': solved.explanation,
                'key_concepts': solved.key_concepts,
                'difficulty_level': solved.difficulty_level,
                'language': solved.language,
                'confidence': solved.confidence,
                'solved_at': datetime.now(timezone.utc).isoformat()
            }

            db.table('solved_questions').insert(record).execute()
            logger.info(f"Stored solved question: session_id={session_id}, subject={solved.subject}")

        except Exception as exc:
            logger.exception(f"Failed to store solved question: {exc}")
            # Don't fail the whole request if storage fails

    def list_supported_subjects(self) -> List[str]:
        """List all supported subjects"""
        return list(self.SUBJECT_PROMPTS.keys())


# Singleton instance
_photo_solver: Optional[PhotoSolver] = None


def get_photo_solver() -> PhotoSolver:
    """Get or create PhotoSolver singleton"""
    global _photo_solver
    if _photo_solver is None:
        _photo_solver = PhotoSolver()
    return _photo_solver
