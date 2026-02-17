"""Tools for Supervisor (meta-level operations)"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict

from app.tools.base import BaseTool, ToolResult


class FetchUserProfileTool(BaseTool):
    """Fetch complete user profile with learning history"""

    name = "fetch_user_profile"
    description = "Retrieve student's complete profile including preferences, history, and mastery scores"

    def __init__(self, supabase_client):
        self.db = supabase_client

    async def execute(self, user_id: str) -> ToolResult:
        """
        Fetch user profile

        Args:
            user_id: User identifier
        """
        try:
            # Get profile with related data
            profile = self.db.table('profiles')\
                .select('*, concept_mastery(*), learning_sessions(count)')\
                .eq('id', user_id)\
                .single()\
                .execute()

            if not profile.data:
                return ToolResult(
                    success=False,
                    data=None,
                    error=f"User profile not found for user_id: {user_id}"
                )

            # Extract mastery scores
            mastery_scores = {}
            if 'concept_mastery' in profile.data:
                for entry in profile.data['concept_mastery']:
                    mastery_scores[entry['concept']] = entry['score']

            return ToolResult(
                success=True,
                data={
                    "user_id": user_id,
                    "name": profile.data.get('name'),
                    "grade": profile.data.get('grade'),
                    "board": profile.data.get('board', 'CBSE'),
                    "language_preference": profile.data.get('language_preference', 'hinglish'),
                    "gender": profile.data.get('gender', 'neutral'),
                    "mastery_scores": mastery_scores,
                    "total_sessions": profile.data.get('learning_sessions', [{}])[0].get('count', 0) if profile.data.get('learning_sessions') else 0,
                    "created_at": profile.data.get('created_at')
                }
            )

        except Exception as exc:
            return ToolResult(
                success=False,
                data=None,
                error=f"Failed to fetch user profile: {str(exc)}"
            )


class LogAnalyticsTool(BaseTool):
    """Log analytics events for tracking and improvement"""

    name = "log_analytics"
    description = "Log an analytics event to track user behavior, agent performance, or system metrics"

    def __init__(self, supabase_client):
        self.db = supabase_client

    async def execute(
        self,
        session_id: str,
        event: str,
        metadata: Dict[str, Any]
    ) -> ToolResult:
        """
        Log analytics event

        Args:
            session_id: Current session identifier
            event: Event name (e.g., "agent_routing", "tool_called", "error_occurred")
            metadata: Additional event data
        """
        try:
            event_data = {
                'session_id': session_id,
                'event_name': event,
                'metadata': metadata,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }

            self.db.table('analytics_events').insert(event_data).execute()

            return ToolResult(
                success=True,
                data={
                    "logged": True,
                    "event": event,
                    "timestamp": event_data['timestamp']
                },
                metadata={"analytics": True}
            )

        except Exception as exc:
            # Don't fail critical path if analytics fails
            return ToolResult(
                success=False,
                data={"logged": False},
                error=f"Analytics logging failed: {str(exc)}"
            )


class EscalateToHumanTool(BaseTool):
    """Escalate complex queries to human educators"""

    name = "escalate_to_human"
    description = "Escalate a complex or sensitive query to a human educator for review and response"

    def __init__(self, supabase_client):
        self.db = supabase_client

    async def execute(
        self,
        session_id: str,
        reason: str,
        context: Dict[str, Any]
    ) -> ToolResult:
        """
        Escalate to human

        Args:
            session_id: Current session identifier
            reason: Reason for escalation (e.g., "complex proof required", "beyond AI capability")
            context: Additional context for the educator
        """
        try:
            escalation_data = {
                'session_id': session_id,
                'reason': reason,
                'context': context,
                'status': 'pending',
                'created_at': datetime.now(timezone.utc).isoformat(),
                'resolved_at': None,
                'educator_notes': None
            }

            result = self.db.table('human_escalations').insert(escalation_data).execute()

            escalation_id = result.data[0]['id'] if result.data else None

            # TODO: In production, send notification via webhook/email
            # await send_educator_notification(escalation_id, reason)

            return ToolResult(
                success=True,
                data={
                    "escalation_id": escalation_id,
                    "status": "pending",
                    "message": "I've connected you with a senior educator who specializes in this. They'll review and respond shortly!",
                    "created_at": escalation_data['created_at']
                },
                metadata={"escalation_type": "human_educator"}
            )

        except Exception as exc:
            return ToolResult(
                success=False,
                data=None,
                error=f"Failed to escalate to human: {str(exc)}"
            )
