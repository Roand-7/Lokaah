"""Tools for VEDA teaching agent"""

from __future__ import annotations

from typing import Any, Optional

from app.tools.base import BaseTool, ToolResult


class GeneratePracticeQuestionTool(BaseTool):
    """Generate practice question - routes to ORACLE"""

    name = "generate_practice_question"
    description = "Generate a practice question on a specific concept at given difficulty level"

    async def execute(self, concept: str, difficulty: float) -> ToolResult:
        """
        Signal to route to ORACLE for question generation

        Args:
            concept: Mathematical concept (e.g., "trigonometry", "quadratic_equations")
            difficulty: Difficulty level from 0.0 (easy) to 1.0 (hard)
        """
        return ToolResult(
            success=True,
            data={
                "action": "route_to_oracle",
                "concept": concept,
                "difficulty": min(1.0, max(0.0, difficulty))
            },
            metadata={"tool_type": "routing"}
        )


class FetchExamQuestionTool(BaseTool):
    """Fetch real CBSE exam question from database"""

    name = "fetch_exam_question"
    description = "Fetch a real CBSE board exam question from the database for reference or practice"

    def __init__(self, exam_db):
        self.exam_db = exam_db

    async def execute(
        self,
        chapter: str,
        year: int = 2024,
        difficulty: str = "medium"
    ) -> ToolResult:
        """
        Fetch exam question from database

        Args:
            chapter: Chapter name (e.g., "trigonometry", "quadratic_equations")
            year: Exam year (2015-2025)
            difficulty: Question difficulty ("easy", "medium", "hard")
        """
        try:
            question = await self.exam_db.get_question(
                chapter=chapter,
                board="CBSE",
                year=year,
                difficulty=difficulty
            )

            if question:
                return ToolResult(
                    success=True,
                    data={
                        "question_text": question.text,
                        "marks": question.marks,
                        "year": question.year,
                        "set_number": question.set_number,
                        "attempt_rate": question.statistics.get("attempt_rate", 0.0),
                        "success_rate": question.statistics.get("avg_score", 0.0)
                    }
                )
            else:
                return ToolResult(
                    success=False,
                    data=None,
                    error=f"No question found for chapter '{chapter}' in year {year}"
                )

        except Exception as exc:
            return ToolResult(
                success=False,
                data=None,
                error=f"Failed to fetch exam question: {str(exc)}"
            )


class CreateDiagramTool(BaseTool):
    """Generate visual diagram for mathematical concepts"""

    name = "create_diagram"
    description = "Generate a visual diagram to explain a mathematical concept or problem"

    def __init__(self, diagram_gen):
        self.diagram_gen = diagram_gen

    async def execute(
        self,
        description: str,
        style: str = "minimal"
    ) -> ToolResult:
        """
        Generate diagram

        Args:
            description: Description of what to draw (e.g., "right triangle with sides 3, 4, 5")
            style: Visual style ("minimal", "detailed", "annotated")
        """
        try:
            diagram = await self.diagram_gen.generate(
                description=description,
                style=style,
                language="english"  # Could be made dynamic
            )

            return ToolResult(
                success=True,
                data={
                    "svg": diagram.svg,
                    "ascii": diagram.ascii,
                    "description": description
                }
            )

        except Exception as exc:
            return ToolResult(
                success=False,
                data=None,
                error=f"Failed to generate diagram: {str(exc)}"
            )


class GetStudentMasteryTool(BaseTool):
    """Get student's mastery score for a concept from database"""

    name = "get_student_mastery"
    description = "Retrieve student's current mastery level for a specific mathematical concept"

    def __init__(self, supabase_client):
        self.db = supabase_client

    async def execute(self, session_id: str, concept: str) -> ToolResult:
        """
        Get mastery score

        Args:
            session_id: Current session identifier
            concept: Concept to check (e.g., "trigonometry", "quadratic_equations")
        """
        try:
            result = self.db.table('concept_mastery')\
                .select('score, attempts, correct_attempts, last_attempted')\
                .eq('session_id', session_id)\
                .eq('concept', concept)\
                .single()\
                .execute()

            if result.data:
                return ToolResult(
                    success=True,
                    data={
                        "concept": concept,
                        "score": result.data.get('score', 0.5),
                        "attempts": result.data.get('attempts', 0),
                        "correct_attempts": result.data.get('correct_attempts', 0),
                        "last_attempted": result.data.get('last_attempted')
                    }
                )
            else:
                # No data yet - return default
                return ToolResult(
                    success=True,
                    data={
                        "concept": concept,
                        "score": 0.5,  # Default neutral score
                        "attempts": 0,
                        "correct_attempts": 0,
                        "last_attempted": None
                    },
                    metadata={"default_value": True}
                )

        except Exception as exc:
            return ToolResult(
                success=False,
                data=None,
                error=f"Failed to fetch mastery score: {str(exc)}"
            )
