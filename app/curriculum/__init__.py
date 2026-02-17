"""Curriculum management system for multi-board, multi-subject, multi-class education"""

from app.curriculum.curriculum_manager import (
    Board,
    Subject,
    Curriculum,
    Topic,
    QuestionPattern,
    CurriculumManager,
    get_curriculum_manager,
)

__all__ = [
    "Board",
    "Subject",
    "Curriculum",
    "Topic",
    "QuestionPattern",
    "CurriculumManager",
    "get_curriculum_manager",
]
