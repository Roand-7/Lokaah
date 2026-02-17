"""Tools for ORACLE assessment agent"""

from __future__ import annotations

from datetime import datetime, timezone

from app.tools.base import BaseTool, ToolResult
from app.services.knowledge_tracer import get_knowledge_tracer


class TrackStudentAttemptTool(BaseTool):
    """Track student attempt to adjust difficulty adaptively"""

    name = "track_student_attempt"
    description = "Record student's attempt result to track progress and adjust difficulty"

    def __init__(self, supabase_client):
        self.db = supabase_client

    async def execute(
        self,
        session_id: str,
        concept: str,
        is_correct: bool
    ) -> ToolResult:
        """
        Track attempt and update mastery

        Args:
            session_id: Current session identifier
            concept: Concept being practiced
            is_correct: Whether the student answered correctly
        """
        try:
            # Get current mastery score
            mastery_query = self.db.table('concept_mastery')\
                .select('score')\
                .eq('session_id', session_id)\
                .eq('concept', concept)\
                .execute()

            # Get prior mastery (or use initial if first attempt)
            tracer = get_knowledge_tracer()
            if mastery_query.data and len(mastery_query.data) > 0:
                prior_mastery = mastery_query.data[0].get('score', tracer.get_initial_mastery())
            else:
                prior_mastery = tracer.get_initial_mastery()

            # Update mastery using Bayesian Knowledge Tracing
            new_score = tracer.update_mastery(
                concept=concept,
                prior_mastery=prior_mastery,
                is_correct=is_correct
            )

            # Record attempt
            attempt_data = {
                'session_id': session_id,
                'concept': concept,
                'is_correct': is_correct,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'metadata': {
                    'prior_mastery': prior_mastery,
                    'updated_mastery': new_score
                }
            }

            self.db.table('concept_attempts').insert(attempt_data).execute()

            # Get total attempts count
            history = self.db.table('concept_attempts')\
                .select('is_correct')\
                .eq('session_id', session_id)\
                .eq('concept', concept)\
                .execute()

            attempts = history.data if history.data else []
            recent_success_rate = sum(1 for a in attempts if a.get('is_correct')) / len(attempts) if attempts else 0.0

            # Upsert mastery score
            mastery_data = {
                'session_id': session_id,
                'concept': concept,
                'score': new_score,
                'attempts': len(attempts),
                'correct_attempts': sum(1 for a in attempts if a.get('is_correct')),
                'last_attempted': datetime.now(timezone.utc).isoformat()
            }

            self.db.table('concept_mastery').upsert(mastery_data).execute()

            return ToolResult(
                success=True,
                data={
                    "concept": concept,
                    "is_correct": is_correct,
                    "new_score": new_score,
                    "total_attempts": len(attempts),
                    "recent_success_rate": recent_success_rate if attempts else 0.0
                }
            )

        except Exception as exc:
            return ToolResult(
                success=False,
                data=None,
                error=f"Failed to track attempt: {str(exc)}"
            )


class AdjustDifficultyTool(BaseTool):
    """Adjust session difficulty based on recent performance"""

    name = "adjust_difficulty"
    description = "Dynamically adjust question difficulty based on student's recent performance"

    def __init__(self, supabase_client):
        self.db = supabase_client

    async def execute(
        self,
        session_id: str,
        current_difficulty: float = 0.6
    ) -> ToolResult:
        """
        Adjust difficulty based on recent attempts

        Args:
            session_id: Current session identifier
            current_difficulty: Current difficulty level (0.0-1.0)
        """
        try:
            # Get recent attempts (last 5)
            recent = self.db.table('concept_attempts')\
                .select('is_correct')\
                .eq('session_id', session_id)\
                .order('timestamp', desc=True)\
                .limit(5)\
                .execute()

            if not recent.data:
                # No data yet, return current difficulty
                return ToolResult(
                    success=True,
                    data={
                        "difficulty": current_difficulty,
                        "change": 0.0,
                        "reason": "No attempt history yet"
                    }
                )

            # Calculate success rate
            correct_count = sum(1 for a in recent.data if a.get('is_correct'))
            success_rate = correct_count / len(recent.data)

            # Adjust difficulty
            if success_rate >= 0.8:
                # Student excelling - increase difficulty
                new_difficulty = min(1.0, current_difficulty + 0.1)
                reason = "High success rate - increasing difficulty"
            elif success_rate <= 0.4:
                # Student struggling - decrease difficulty
                new_difficulty = max(0.2, current_difficulty - 0.1)
                reason = "Low success rate - decreasing difficulty"
            else:
                # Balanced - maintain difficulty
                new_difficulty = current_difficulty
                reason = "Balanced performance - maintaining difficulty"

            change = new_difficulty - current_difficulty

            return ToolResult(
                success=True,
                data={
                    "difficulty": new_difficulty,
                    "change": change,
                    "success_rate": success_rate,
                    "reason": reason,
                    "attempts_analyzed": len(recent.data)
                }
            )

        except Exception as exc:
            return ToolResult(
                success=False,
                data=None,
                error=f"Failed to adjust difficulty: {str(exc)}"
            )
