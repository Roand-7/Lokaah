"""
VEDA-ORACLE service layer.
Provides adaptive practice, Socratic streaming, and exam prediction helpers.
"""

from __future__ import annotations

from typing import Any, AsyncGenerator, Dict, List, Optional
import asyncio
import json
from datetime import datetime

from .oracle_engine import OraclePatternExtractor, RecipeEngine


class VedaOracleService:
    def __init__(self, oracle: OraclePatternExtractor, recipe_engine: RecipeEngine) -> None:
        self.oracle = oracle
        self.recipe_engine = recipe_engine

    async def generate_adaptive_practice(
        self,
        user_id: str,
        topic: str,
        weak_areas: Optional[List[str]] = None,
        target_marks: int = 75,
        session_duration: int = 30,
    ) -> Dict[str, Any]:
        weak_areas = weak_areas or []

        questions: List[Dict[str, Any]] = []
        total_questions = max(5, min(20, session_duration // 3))

        for _ in range(total_questions):
            question = self.recipe_engine.generate_question(topic=topic)
            questions.append(question)

        return {
            "session_id": f"sess_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "user_id": user_id,
            "topic": topic,
            "weak_areas": weak_areas,
            "target_marks": target_marks,
            "session_duration": session_duration,
            "questions": questions,
        }

    async def socratic_solve(
        self,
        question_id: str,
        student_input: str,
        session_context: Dict[str, Any],
    ) -> AsyncGenerator[str, None]:
        steps = [
            {"stage": "elicit", "message": "What is the key concept here?"},
            {"stage": "probe", "message": "Which formula or relation applies?"},
            {"stage": "extend", "message": "Try applying it step-by-step."},
        ]

        for step in steps:
            payload = {
                "question_id": question_id,
                "stage": step["stage"],
                "message": step["message"],
                "session": session_context,
            }
            yield json.dumps(payload)
            await asyncio.sleep(0.05)

    async def predict_exam_questions(self, year: str) -> Dict[str, Any]:
        trends = self.oracle.predict_2026_trends()
        return {
            "year": year,
            "predictions": trends,
        }

    async def explain_mistake(
        self,
        question_id: str,
        wrong_answer: str,
        correct_reasoning: bool = False,
    ) -> Dict[str, Any]:
        return {
            "question_id": question_id,
            "wrong_answer": wrong_answer,
            "correct_reasoning": correct_reasoning,
            "analysis": "Check algebraic steps and verify arithmetic. Review the core concept.",
        }
