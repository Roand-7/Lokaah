from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional
import os


@dataclass
class ExamQuestion:
    text: str
    marks: int
    year: int
    set_number: str
    statistics: Dict[str, float] = field(default_factory=dict)


class ExamDatabase:
    async def get_question(
        self, chapter: str, board: str, year: int, difficulty: str
    ) -> Optional[ExamQuestion]:
        raise NotImplementedError


class SupabaseExamDatabase(ExamDatabase):
    def __init__(self) -> None:
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_SERVICE_KEY")
        self.table = os.getenv("EXAM_QUESTIONS_TABLE", "exam_questions")
        self._client = None

    def _client_or_none(self):
        if not self.url or not self.key:
            return None
        if self._client is not None:
            return self._client
        try:
            from supabase import create_client  # type: ignore

            self._client = create_client(self.url, self.key)
            return self._client
        except Exception:
            return None

    async def get_question(
        self, chapter: str, board: str, year: int, difficulty: str
    ) -> Optional[ExamQuestion]:
        client = self._client_or_none()
        if not client:
            return None

        try:
            response = (
                client.table(self.table)
                .select("*")
                .eq("chapter", chapter)
                .eq("board", board)
                .eq("year", year)
                .eq("difficulty", difficulty)
                .limit(1)
                .execute()
            )
            rows = response.data or []
            if not rows:
                return None
            row = rows[0]
            return ExamQuestion(
                text=str(row.get("question_text") or row.get("text") or ""),
                marks=int(row.get("marks") or 0),
                year=int(row.get("year") or year),
                set_number=str(row.get("set_number") or row.get("set") or "A"),
                statistics={
                    "attempt_rate": float(row.get("attempt_rate") or 0.0),
                    "avg_score": float(row.get("avg_score") or 0.0),
                },
            )
        except Exception:
            return None


class MockExamDatabase(ExamDatabase):
    async def get_question(
        self, chapter: str, board: str, year: int, difficulty: str
    ) -> Optional[ExamQuestion]:
        return ExamQuestion(
            text=f"Sample {board} question for {chapter} ({year}).",
            marks=4,
            year=year,
            set_number="A",
            statistics={"attempt_rate": 0.78, "avg_score": 2.6},
        )


def build_exam_database() -> ExamDatabase:
    db = SupabaseExamDatabase()
    if db._client_or_none():
        return db
    return MockExamDatabase()
