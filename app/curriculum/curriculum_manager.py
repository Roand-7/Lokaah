"""
Curriculum Manager - Central registry for multi-board, multi-subject, multi-class education

This is the scalability backbone of LOKAAH.
Abstracts all curriculum operations to work across:
- 100+ boards (CBSE, Karnataka, Kerala, etc.)
- 10+ subjects (Math, Science, Social Studies, etc.)
- All classes (10, 11, 12, competitive exams)
- All languages (English, Hindi, Tamil, Telugu, etc.)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from uuid import UUID

logger = logging.getLogger(__name__)


@dataclass
class Board:
    """Educational board (CBSE, Karnataka, etc.)"""
    id: UUID
    code: str
    name: str
    full_name: str
    country: str
    default_language: str
    is_active: bool


@dataclass
class Subject:
    """Academic subject (Math, Science, etc.)"""
    id: UUID
    code: str
    name: str
    icon: str
    color: str
    description: Optional[str] = None


@dataclass
class Curriculum:
    """Board + Subject + Class combination"""
    id: UUID
    board_id: UUID
    subject_id: UUID
    class_level: int
    academic_year: str
    syllabus_version: str
    exam_pattern: Dict[str, Any]
    total_marks: int
    passing_marks: int
    time_limit_minutes: int
    ncert_aligned: bool
    is_published: bool

    # Cached relationships
    board: Optional[Board] = None
    subject: Optional[Subject] = None


@dataclass
class Topic:
    """Chapter/Topic in curriculum (hierarchical)"""
    id: UUID
    curriculum_id: UUID
    code: str
    name: str
    display_names: Dict[str, str]  # Multi-language
    parent_topic_id: Optional[UUID]
    sequence_order: int
    depth_level: int
    weightage_marks: int
    ncert_chapter_number: Optional[int]
    difficulty_avg: float
    description: Optional[str] = None
    learning_objectives: List[str] = None
    prerequisites: List[str] = None


@dataclass
class QuestionPattern:
    """Reusable question template"""
    id: UUID
    pattern_id: str
    topic_id: UUID
    name: str
    difficulty: float
    marks: int
    question_type: str
    template_text: str
    variables_schema: Dict[str, Any]
    solution_template: List[Dict[str, Any]]
    answer_template: str
    validation_rules: Optional[List[str]] = None
    marking_scheme: Optional[Dict[str, Any]] = None
    visual_type: Optional[str] = None
    visual_config: Optional[Dict[str, Any]] = None
    is_approved: bool = False
    usage_count: int = 0


class CurriculumManager:
    """
    Central curriculum registry - works across all boards, subjects, classes

    This is the **single source of truth** for:
    - What curricula exist (CBSE Class 10 Math, Karnataka Class 10 Math, etc.)
    - What topics are in each curriculum
    - What question patterns exist for each topic
    - How to scale to new boards/subjects/classes
    """

    def __init__(self, db):
        """
        Args:
            db: Supabase client or database connection
        """
        self.db = db
        self._cache: Dict[str, Any] = {}  # In-memory cache (Redis in production)

    # ========================================================================
    # BOARD OPERATIONS
    # ========================================================================

    async def get_board(self, code: str) -> Optional[Board]:
        """Get board by code (e.g., 'CBSE', 'KARNATAKA')"""
        cache_key = f"board:{code}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        try:
            result = self.db.table('boards')\
                .select('*')\
                .eq('code', code)\
                .eq('is_active', True)\
                .single()\
                .execute()

            if result.data:
                board = Board(**result.data)
                self._cache[cache_key] = board
                return board

        except Exception as exc:
            logger.warning(f"Failed to get board {code}: {exc}")

        return None

    async def list_boards(self, country: str = "India") -> List[Board]:
        """List all active boards in a country"""
        try:
            result = self.db.table('boards')\
                .select('*')\
                .eq('country', country)\
                .eq('is_active', True)\
                .execute()

            return [Board(**row) for row in result.data]

        except Exception as exc:
            logger.error(f"Failed to list boards: {exc}")
            return []

    # ========================================================================
    # SUBJECT OPERATIONS
    # ========================================================================

    async def get_subject(self, code: str) -> Optional[Subject]:
        """Get subject by code (e.g., 'MATH', 'SCIENCE')"""
        cache_key = f"subject:{code}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        try:
            result = self.db.table('subjects')\
                .select('*')\
                .eq('code', code)\
                .eq('is_active', True)\
                .single()\
                .execute()

            if result.data:
                subject = Subject(**result.data)
                self._cache[cache_key] = subject
                return subject

        except Exception as exc:
            logger.warning(f"Failed to get subject {code}: {exc}")

        return None

    async def list_subjects(self) -> List[Subject]:
        """List all active subjects"""
        try:
            result = self.db.table('subjects')\
                .select('*')\
                .eq('is_active', True)\
                .execute()

            return [Subject(**row) for row in result.data]

        except Exception as exc:
            logger.error(f"Failed to list subjects: {exc}")
            return []

    # ========================================================================
    # CURRICULUM OPERATIONS (CORE)
    # ========================================================================

    async def get_curriculum(
        self,
        board: str = "CBSE",
        subject: str = "MATH",
        class_level: int = 10,
        academic_year: str = "2024-25"
    ) -> Optional[Curriculum]:
        """
        Get curriculum configuration

        This is the **KEY METHOD** for scaling.
        Everything flows from curriculum selection:
        - CBSE Class 10 Math → topics → patterns
        - Karnataka Class 10 Math → different topics → different patterns

        Args:
            board: Board code (CBSE, KARNATAKA, etc.)
            subject: Subject code (MATH, SCIENCE, etc.)
            class_level: 10, 11, or 12
            academic_year: "2024-25"

        Returns:
            Curriculum object or None if not found
        """
        cache_key = f"curriculum:{board}:{subject}:{class_level}:{academic_year}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        try:
            # Get board and subject IDs
            board_obj = await self.get_board(board)
            subject_obj = await self.get_subject(subject)

            if not board_obj or not subject_obj:
                logger.error(f"Board {board} or subject {subject} not found")
                return None

            # Query curriculum
            result = self.db.table('curricula')\
                .select('*')\
                .eq('board_id', str(board_obj.id))\
                .eq('subject_id', str(subject_obj.id))\
                .eq('class_level', class_level)\
                .eq('academic_year', academic_year)\
                .eq('is_published', True)\
                .single()\
                .execute()

            if result.data:
                curriculum = Curriculum(**result.data)
                curriculum.board = board_obj
                curriculum.subject = subject_obj
                self._cache[cache_key] = curriculum

                logger.info(
                    f"Loaded curriculum: {board} Class {class_level} {subject} ({academic_year})"
                )
                return curriculum

        except Exception as exc:
            logger.error(f"Failed to get curriculum: {exc}")

        return None

    async def list_curricula(
        self,
        board: Optional[str] = None,
        subject: Optional[str] = None,
        class_level: Optional[int] = None
    ) -> List[Curriculum]:
        """
        List published curricula with optional filters

        Examples:
        - list_curricula(board="CBSE") → All CBSE curricula
        - list_curricula(class_level=10) → All Class 10 curricula
        - list_curricula(board="CBSE", class_level=10) → All CBSE Class 10 curricula
        """
        try:
            query = self.db.table('curricula').select('*').eq('is_published', True)

            if board:
                board_obj = await self.get_board(board)
                if board_obj:
                    query = query.eq('board_id', str(board_obj.id))

            if subject:
                subject_obj = await self.get_subject(subject)
                if subject_obj:
                    query = query.eq('subject_id', str(subject_obj.id))

            if class_level:
                query = query.eq('class_level', class_level)

            result = query.execute()
            return [Curriculum(**row) for row in result.data]

        except Exception as exc:
            logger.error(f"Failed to list curricula: {exc}")
            return []

    # ========================================================================
    # TOPIC OPERATIONS
    # ========================================================================

    async def get_topics(
        self,
        curriculum_id: UUID,
        parent_topic_id: Optional[UUID] = None
    ) -> List[Topic]:
        """
        Get topics for a curriculum (optionally filtered by parent)

        Args:
            curriculum_id: UUID of curriculum
            parent_topic_id: If provided, get subtopics only

        Returns:
            List of topics in sequence order
        """
        try:
            query = self.db.table('topics')\
                .select('*')\
                .eq('curriculum_id', str(curriculum_id))\
                .eq('is_active', True)\
                .order('sequence_order')

            if parent_topic_id:
                query = query.eq('parent_topic_id', str(parent_topic_id))
            else:
                # Get only top-level topics (chapters)
                query = query.is_('parent_topic_id', 'null')

            result = query.execute()
            return [Topic(**row) for row in result.data]

        except Exception as exc:
            logger.error(f"Failed to get topics: {exc}")
            return []

    async def get_topic_by_code(
        self,
        curriculum_id: UUID,
        topic_code: str
    ) -> Optional[Topic]:
        """Get specific topic by code (e.g., 'QUADRATIC_EQUATIONS')"""
        try:
            result = self.db.table('topics')\
                .select('*')\
                .eq('curriculum_id', str(curriculum_id))\
                .eq('code', topic_code)\
                .single()\
                .execute()

            if result.data:
                return Topic(**result.data)

        except Exception as exc:
            logger.warning(f"Topic {topic_code} not found: {exc}")

        return None

    async def get_topic_hierarchy(self, curriculum_id: UUID) -> Dict[str, Any]:
        """
        Get full topic hierarchy (chapters → sections → subsections)

        Returns nested structure:
        {
            "chapters": [
                {
                    "id": "...",
                    "name": "Quadratic Equations",
                    "sections": [
                        {"name": "Standard Form", "subsections": [...]},
                        {"name": "Solving Methods", "subsections": [...]}
                    ]
                }
            ]
        }
        """
        topics = await self.get_topics(curriculum_id)

        hierarchy = {"chapters": []}

        for chapter in topics:
            # Get sections (depth_level = 1)
            sections = await self.get_topics(curriculum_id, parent_topic_id=chapter.id)

            chapter_data = {
                "id": str(chapter.id),
                "code": chapter.code,
                "name": chapter.name,
                "weightage_marks": chapter.weightage_marks,
                "sections": []
            }

            for section in sections:
                # Get subsections (depth_level = 2)
                subsections = await self.get_topics(curriculum_id, parent_topic_id=section.id)

                section_data = {
                    "id": str(section.id),
                    "code": section.code,
                    "name": section.name,
                    "subsections": [
                        {"id": str(s.id), "code": s.code, "name": s.name}
                        for s in subsections
                    ]
                }

                chapter_data["sections"].append(section_data)

            hierarchy["chapters"].append(chapter_data)

        return hierarchy

    # ========================================================================
    # PATTERN OPERATIONS
    # ========================================================================

    async def get_patterns_for_topic(
        self,
        topic_id: UUID,
        difficulty: Optional[float] = None,
        marks: Optional[int] = None,
        question_type: Optional[str] = None
    ) -> List[QuestionPattern]:
        """
        Get question patterns for a topic with optional filters

        Args:
            topic_id: UUID of topic
            difficulty: 0.0-1.0 (±0.1 range if provided)
            marks: Exact marks (1, 2, 3, 5)
            question_type: "MCQ", "VSA", "SA", "LA"

        Returns:
            List of approved patterns matching criteria
        """
        try:
            query = self.db.table('question_patterns')\
                .select('*')\
                .eq('topic_id', str(topic_id))\
                .eq('is_approved', True)

            if difficulty is not None:
                # Range query: difficulty ±0.1
                query = query.gte('difficulty', difficulty - 0.1)\
                             .lte('difficulty', difficulty + 0.1)

            if marks is not None:
                query = query.eq('marks', marks)

            if question_type:
                query = query.eq('question_type', question_type)

            result = query.execute()
            return [QuestionPattern(**row) for row in result.data]

        except Exception as exc:
            logger.error(f"Failed to get patterns: {exc}")
            return []

    async def get_pattern_by_id(self, pattern_id: str) -> Optional[QuestionPattern]:
        """Get pattern by pattern_id (e.g., 'quadratic_discriminant_v1')"""
        cache_key = f"pattern:{pattern_id}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        try:
            result = self.db.table('question_patterns')\
                .select('*')\
                .eq('pattern_id', pattern_id)\
                .single()\
                .execute()

            if result.data:
                pattern = QuestionPattern(**result.data)
                self._cache[cache_key] = pattern
                return pattern

        except Exception as exc:
            logger.warning(f"Pattern {pattern_id} not found: {exc}")

        return None

    # ========================================================================
    # EXAM PATTERN UTILITIES
    # ========================================================================

    def get_exam_structure(self, curriculum: Curriculum) -> Dict[str, Any]:
        """
        Extract exam structure from curriculum

        Returns:
        {
            "sections": [...],
            "total_marks": 80,
            "time_limit_minutes": 180,
            "question_counts": {"MCQ": 20, "VSA": 5, "SA": 6, "LA": 2}
        }
        """
        pattern = curriculum.exam_pattern

        question_counts = {}
        for section in pattern.get("sections", []):
            q_type = section.get("type")
            count = section.get("questions", 0)
            question_counts[q_type] = count

        return {
            "sections": pattern.get("sections", []),
            "total_marks": curriculum.total_marks,
            "time_limit_minutes": curriculum.time_limit_minutes,
            "question_counts": question_counts,
            "has_internal_choice": pattern.get("internal_choice", False)
        }

    # ========================================================================
    # STATISTICS & ANALYTICS
    # ========================================================================

    async def get_curriculum_stats(self, curriculum_id: UUID) -> Dict[str, Any]:
        """
        Get curriculum statistics

        Returns:
        {
            "total_topics": 60,
            "total_patterns": 150,
            "pattern_distribution": {"MCQ": 50, "VSA": 40, "SA": 40, "LA": 20},
            "difficulty_distribution": {"easy": 40, "medium": 80, "hard": 30}
        }
        """
        topics = await self.get_topics(curriculum_id)

        # Count patterns across all topics
        total_patterns = 0
        pattern_distribution = {}
        difficulty_distribution = {"easy": 0, "medium": 0, "hard": 0}

        for topic in topics:
            patterns = await self.get_patterns_for_topic(topic.id)
            total_patterns += len(patterns)

            for pattern in patterns:
                # Count by type
                q_type = pattern.question_type
                pattern_distribution[q_type] = pattern_distribution.get(q_type, 0) + 1

                # Count by difficulty
                if pattern.difficulty < 0.4:
                    difficulty_distribution["easy"] += 1
                elif pattern.difficulty < 0.7:
                    difficulty_distribution["medium"] += 1
                else:
                    difficulty_distribution["hard"] += 1

        return {
            "total_topics": len(topics),
            "total_patterns": total_patterns,
            "pattern_distribution": pattern_distribution,
            "difficulty_distribution": difficulty_distribution
        }


# ============================================================================
# GLOBAL INSTANCE (SINGLETON)
# ============================================================================

_curriculum_manager: Optional[CurriculumManager] = None


def get_curriculum_manager(db) -> CurriculumManager:
    """Get singleton instance of CurriculumManager"""
    global _curriculum_manager
    if _curriculum_manager is None:
        _curriculum_manager = CurriculumManager(db)
    return _curriculum_manager
