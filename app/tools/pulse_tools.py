"""Tools for PULSE wellbeing agent"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.tools.base import BaseTool, ToolResult


class SendBreathingExerciseTool(BaseTool):
    """Send guided breathing exercise for stress relief"""

    name = "send_breathing_exercise"
    description = "Provide a guided breathing exercise pattern to help student calm down and reduce anxiety"

    async def execute(self, pattern: str = "4-4-4-4") -> ToolResult:
        """
        Send breathing exercise configuration

        Args:
            pattern: Breathing pattern ("4-4-4-4" for box breathing, "4-7-8" for relaxing breath)
        """
        patterns = {
            "4-4-4-4": {
                "name": "Box Breathing",
                "inhale": 4,
                "hold": 4,
                "exhale": 4,
                "rest": 4,
                "cycles": 4
            },
            "4-7-8": {
                "name": "Relaxing Breath",
                "inhale": 4,
                "hold": 7,
                "exhale": 8,
                "rest": 0,
                "cycles": 3
            },
            "3-3-3": {
                "name": "Quick Calm",
                "inhale": 3,
                "hold": 3,
                "exhale": 3,
                "rest": 0,
                "cycles": 5
            }
        }

        config = patterns.get(pattern, patterns["4-4-4-4"])

        # Calculate total duration
        duration_seconds = (
            config["inhale"] +
            config["hold"] +
            config["exhale"] +
            config["rest"]
        ) * config["cycles"]

        return ToolResult(
            success=True,
            data={
                "type": "breathing_exercise",
                "name": config["name"],
                "pattern": pattern,
                "config": config,
                "duration_seconds": duration_seconds,
                "instructions": f"Let's do {config['name']}: Inhale {config['inhale']}s, hold {config['hold']}s, exhale {config['exhale']}s. Repeat {config['cycles']} times."
            },
            metadata={"intervention_type": "breathing"}
        )


class SuggestBreakTool(BaseTool):
    """Schedule a study break reminder"""

    name = "suggest_break"
    description = "Suggest and schedule a study break to prevent burnout"

    async def execute(self, duration_minutes: int = 10) -> ToolResult:
        """
        Schedule break

        Args:
            duration_minutes: Break duration in minutes (5-30)
        """
        # Clamp duration
        duration_minutes = min(30, max(5, duration_minutes))

        break_time = datetime.now(timezone.utc) + timedelta(minutes=duration_minutes)

        return ToolResult(
            success=True,
            data={
                "type": "break_scheduled",
                "duration_minutes": duration_minutes,
                "resume_at": break_time.isoformat(),
                "resume_at_readable": break_time.strftime("%I:%M %p"),
                "message": f"Perfect timing for a {duration_minutes}-minute break! Stretch, hydrate, and come back refreshed. I'll be here when you return!",
                "suggestions": [
                    "Stretch your body",
                    "Drink water",
                    "Step outside for fresh air",
                    "Close your eyes and rest"
                ]
            },
            metadata={"intervention_type": "break"}
        )


class EscalateToCounselorTool(BaseTool):
    """Flag session for human counselor review (crisis intervention)"""

    name = "escalate_to_counselor"
    description = "Escalate to human counselor for serious mental health concerns or crisis situations"

    def __init__(self, supabase_client):
        self.db = supabase_client

    async def execute(
        self,
        session_id: str,
        reason: str,
        urgency: str = "medium"
    ) -> ToolResult:
        """
        Escalate to counselor

        Args:
            session_id: Current session identifier
            reason: Reason for escalation (e.g., "self-harm mention", "severe anxiety")
            urgency: Urgency level ("low", "medium", "high", "critical")
        """
        # Validate urgency
        valid_urgencies = ["low", "medium", "high", "critical"]
        if urgency not in valid_urgencies:
            urgency = "medium"

        try:
            escalation_data = {
                'session_id': session_id,
                'reason': reason,
                'urgency': urgency,
                'status': 'pending',
                'flagged_at': datetime.now(timezone.utc).isoformat(),
                'resolved_at': None,
                'counselor_notes': None
            }

            result = self.db.table('counselor_escalations').insert(escalation_data).execute()

            escalation_id = result.data[0]['id'] if result.data else None

            # Determine message based on urgency
            if urgency == "critical":
                message = "I've immediately connected you with our crisis support team. Someone will reach out within minutes. You're not alone."
            elif urgency == "high":
                message = "I've flagged this for urgent review by our support team. They'll reach out within the hour."
            else:
                message = "I've noted this for our support team to follow up. They'll check in with you soon."

            return ToolResult(
                success=True,
                data={
                    "escalation_id": escalation_id,
                    "urgency": urgency,
                    "message": message,
                    "flagged_at": escalation_data['flagged_at']
                },
                metadata={"intervention_type": "escalation", "urgency": urgency}
            )

        except Exception as exc:
            return ToolResult(
                success=False,
                data=None,
                error=f"Failed to escalate to counselor: {str(exc)}"
            )
