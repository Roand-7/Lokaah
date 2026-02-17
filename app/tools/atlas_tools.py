"""Tools for ATLAS study planning agent"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Dict, List

from app.tools.base import BaseTool, ToolResult


class CreateStudyPlanTool(BaseTool):
    """Generate personalized study plan based on weak areas and exam date"""

    name = "create_study_plan"
    description = "Create a personalized weekly study plan based on student's weak areas and upcoming exam date"

    async def execute(
        self,
        weak_areas: List[str],
        exam_date: str,
        hours_per_day: int = 2
    ) -> ToolResult:
        """
        Generate study plan

        Args:
            weak_areas: List of weak concepts/chapters to focus on
            exam_date: Exam date in ISO format (YYYY-MM-DD)
            hours_per_day: Study hours available per day (1-6)
        """
        try:
            # Parse exam date
            exam_dt = datetime.fromisoformat(exam_date.replace('Z', '+00:00'))
            today = datetime.now(timezone.utc)
            days_remaining = (exam_dt - today).days

            if days_remaining <= 0:
                return ToolResult(
                    success=False,
                    data=None,
                    error="Exam date has already passed or is today"
                )

            # Clamp hours per day
            hours_per_day = min(6, max(1, hours_per_day))

            # Calculate total available hours
            total_hours = days_remaining * hours_per_day

            # Allocate time proportionally to weak areas
            if not weak_areas:
                return ToolResult(
                    success=False,
                    data=None,
                    error="No weak areas specified"
                )

            hours_per_area = total_hours // len(weak_areas)

            # Generate day-by-day plan
            plan = []
            current_date = today

            for area in weak_areas:
                # Each area gets multiple sessions
                sessions_needed = max(1, hours_per_area // 2)  # 2-hour sessions

                for session in range(sessions_needed):
                    if current_date >= exam_dt:
                        break

                    plan.append({
                        "date": current_date.strftime("%Y-%m-%d"),
                        "day": current_date.strftime("%A"),
                        "topic": area,
                        "duration_minutes": 120,  # 2 hours
                        "focus": "Practice + Review",
                        "tasks": [
                            f"Review key concepts in {area}",
                            f"Solve 10 practice questions",
                            f"Identify and work on mistakes"
                        ]
                    })

                    current_date += timedelta(days=1)

            # Add final week revision plan
            revision_start = exam_dt - timedelta(days=7)
            if current_date < revision_start:
                current_date = revision_start

            while current_date < exam_dt:
                plan.append({
                    "date": current_date.strftime("%Y-%m-%d"),
                    "day": current_date.strftime("%A"),
                    "topic": "Full Revision",
                    "duration_minutes": hours_per_day * 60,
                    "focus": "Mock Tests + Revision",
                    "tasks": [
                        "Attempt full-length mock test",
                        "Review all formulas and concepts",
                        "Revise weak areas identified in tests"
                    ]
                })
                current_date += timedelta(days=1)

            # Calculate coverage
            study_days = len(plan)
            coverage_percentage = min(100, (study_days / days_remaining) * 100)

            return ToolResult(
                success=True,
                data={
                    "plan": plan[:30],  # Limit to 30 days for display
                    "total_sessions": len(plan),
                    "study_days": study_days,
                    "days_until_exam": days_remaining,
                    "coverage_percentage": round(coverage_percentage, 1),
                    "hours_allocated": study_days * 2,
                    "weak_areas_count": len(weak_areas)
                }
            )

        except Exception as exc:
            return ToolResult(
                success=False,
                data=None,
                error=f"Failed to create study plan: {str(exc)}"
            )


class FetchCBSEExamDatesTool(BaseTool):
    """Fetch CBSE board exam dates for current/upcoming year"""

    name = "fetch_cbse_exam_dates"
    description = "Get official CBSE board exam dates for a specific year and grade"

    async def execute(self, year: int, grade: int = 10) -> ToolResult:
        """
        Fetch exam dates

        Args:
            year: Exam year (2024-2027)
            grade: Grade level (10 or 12)
        """
        # In production, this would scrape from CBSE website or use cached data
        # For now, using realistic mock data

        exam_dates = {
            2026: {
                10: {
                    "mathematics_basic": "2026-03-15",
                    "mathematics_standard": "2026-03-15",
                    "science": "2026-03-18",
                    "social_science": "2026-03-12",
                    "english": "2026-03-10",
                    "hindi": "2026-03-08"
                },
                12: {
                    "mathematics": "2026-03-20",
                    "physics": "2026-03-16",
                    "chemistry": "2026-03-22",
                    "biology": "2026-03-18",
                    "english": "2026-03-10"
                }
            },
            2027: {
                10: {
                    "mathematics_basic": "2027-03-14",
                    "mathematics_standard": "2027-03-14",
                    "science": "2027-03-17",
                    "social_science": "2027-03-11"
                }
            }
        }

        dates = exam_dates.get(year, {}).get(grade, {})

        if not dates:
            return ToolResult(
                success=False,
                data=None,
                error=f"Exam dates not available for year {year}, grade {grade}"
            )

        return ToolResult(
            success=True,
            data={
                "year": year,
                "grade": grade,
                "exam_dates": dates,
                "subjects": list(dates.keys()),
                "exam_window_start": min(dates.values()),
                "exam_window_end": max(dates.values())
            }
        )


class PrioritizeTopicsTool(BaseTool):
    """Prioritize topics based on mastery scores and exam weightage"""

    name = "prioritize_topics"
    description = "Analyze student's mastery scores and prioritize topics based on urgency and exam weightage"

    async def execute(self, mastery_scores: Dict[str, float]) -> ToolResult:
        """
        Prioritize topics

        Args:
            mastery_scores: Dictionary of concept to mastery score (0.0-1.0)
        """
        # CBSE Class 10 Math chapter weightage (out of 100 marks)
        chapter_weightage = {
            "real_numbers": 6,
            "polynomials": 4,
            "linear_equations": 7,
            "quadratic_equations": 8,
            "arithmetic_progressions": 6,
            "trigonometry": 12,
            "coordinate_geometry": 8,
            "triangles": 10,
            "circles": 6,
            "constructions": 6,
            "surface_area_volume": 8,
            "statistics": 10,
            "probability": 10
        }

        # Calculate priority scores
        priorities = []

        for topic, mastery in mastery_scores.items():
            # Normalize topic name
            topic_key = topic.lower().replace(" ", "_")

            weightage = chapter_weightage.get(topic_key, 5)  # Default weightage

            # Priority = (1 - mastery) * weightage
            # Low mastery + high weightage = highest priority
            urgency_score = (1 - mastery) * weightage

            priorities.append({
                "topic": topic,
                "mastery": round(mastery, 2),
                "weightage": weightage,
                "urgency_score": round(urgency_score, 2),
                "status": self._get_status(mastery)
            })

        # Sort by urgency descending
        priorities.sort(key=lambda x: x['urgency_score'], reverse=True)

        # Categorize
        critical = [p for p in priorities if p['mastery'] < 0.4]
        needs_work = [p for p in priorities if 0.4 <= p['mastery'] < 0.7]
        strong = [p for p in priorities if p['mastery'] >= 0.7]

        return ToolResult(
            success=True,
            data={
                "priorities": priorities,
                "critical_topics": critical,
                "needs_work_topics": needs_work,
                "strong_topics": strong,
                "recommendation": self._generate_recommendation(priorities)
            }
        )

    def _get_status(self, mastery: float) -> str:
        """Get status label based on mastery"""
        if mastery < 0.4:
            return "Critical - Needs immediate attention"
        elif mastery < 0.7:
            return "Needs work - Regular practice needed"
        else:
            return "Strong - Maintain with revision"

    def _generate_recommendation(self, priorities: List[Dict]) -> str:
        """Generate study recommendation"""
        if not priorities:
            return "No mastery data available yet. Start with any chapter!"

        top_3 = priorities[:3]
        critical_count = sum(1 for p in priorities if p['mastery'] < 0.4)

        if critical_count >= 3:
            rec = f"Focus urgently on: {', '.join(p['topic'] for p in top_3)}. These need immediate attention."
        elif critical_count > 0:
            rec = f"Priority areas: {', '.join(p['topic'] for p in top_3)}. Dedicate 70% of study time here."
        else:
            rec = f"Balance practice across: {', '.join(p['topic'] for p in top_3)}. You're doing well overall!"

        return rec
