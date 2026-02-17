"""
ATLAS - Strategic Life & Exam Planner
Develops future-ready strategic thinking through personalized goal systems
"""

import logging
import httpx
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
import os

from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class AtlasConfig:
    model: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    temperature: float = 0.7  # Balanced for strategic planning
    max_tokens: int = 1000  # Detailed plans need space


class AtlasAgent:
    """
    ATLAS - Strategic Life & Exam Planner

    ENHANCED MISSION:
    Not just exam schedules - but developing STRATEGIC THINKING and
    TIME MANAGEMENT mastery that makes students future-ready.

    CORE CAPABILITIES:
    1. Adaptive Study Plans (exam-driven, mastery-optimized)
    2. Strategic Prioritization (weak areas vs comprehensive coverage)
    3. Time Management Mastery (Pareto principle, timeboxing, sprints)
    4. Goal System Design (SMART goals, milestone tracking)
    5. Future-Ready Skills (meta-learning, strategic thinking)

    PHILOSOPHY:
    - Learn to plan = Learn to succeed in life
    - Balance short-term (exam scores) with long-term (conceptual mastery)
    - 80/20 rule: Focus 80% effort on 20% high-impact topics
    - Deadlines are not enemies - they're focus amplifiers
    - Strategic planning is a life skill, not just exam prep

    DECISION FRAMEWORK:
    - Exam < 30 days away: Prioritize weak areas + high-weightage topics
    - Exam 30-60 days away: Balanced coverage with depth in weak areas
    - Exam > 60 days away: Comprehensive mastery-focused learning
    """

    def __init__(self, config: Optional[AtlasConfig] = None, client: Any = None):
        self.config = config or AtlasConfig()
        self.client = client or self._init_gemini_client()

    def _init_gemini_client(self) -> Optional[Any]:
        api_key = settings.GEMINI_API_KEY
        try:
            from google import genai

            if api_key:
                client = genai.Client(api_key=api_key)
                logger.info("ATLAS: Gemini client initialized")
                return client
            else:
                logger.warning("ATLAS: No Gemini API key, using fallback")
                return None
        except Exception as exc:
            logger.exception(f"ATLAS: Gemini client init failed: {exc}")
            return None

    async def plan(
        self,
        student_message: str,
        session_id: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        student_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create strategic study plans, track progress, or generate mock tests

        Args:
            student_message: Student's planning request
            session_id: Current session ID
            conversation_history: Recent conversation context
            tools: Available tools (create_study_plan, fetch_cbse_exam_dates, prioritize_topics)
            student_context: Student's mastery scores, weak areas, etc.

        Returns:
            Response with study plan and/or tool calls
        """

        # Detect intent
        message_lower = student_message.lower()
        
        # Progress tracking request
        if any(keyword in message_lower for keyword in ["progress", "how am i doing", "my performance", "weak areas", "stats"]):
            try:
                # Try to fetch progress data from API
                import httpx
                async with httpx.AsyncClient() as client:
                    response = await client.get(f"http://localhost:8000/api/v1/progress/{session_id}")
                    if response.status_code == 200:
                        progress_data = response.json()
                        return self._format_progress_response(progress_data, session_id)
            except Exception as e:
                logging.getLogger(__name__).warning(f"Could not fetch progress: {e}")
                return {
                    "agent": "atlas",
                    "session_id": session_id,
                    "text": "I'd love to show your progress, but I need a few more practice sessions from you first! Try solving 10 questions, then ask me again. 📊"
                }
        
        # Mock test / full exam request
        if any(keyword in message_lower for keyword in ["mock test", "full exam", "80 marks", "board exam", "sample paper", "complete exam"]):
            return {
                "agent": "atlas",
                "session_id": session_id,
                "text": """🎯 **Ready for a Full Board Exam Mock Test?**

I can generate a complete CBSE-style exam for you:
- **Total Marks:** 80
- **Duration:** 3 hours
- **Sections:** A (MCQs), B (Short), C (Long), D (Case Study)
- **Pattern:** Exactly like board exams

**Which subjects do you want to focus on?**
Tell me chapters, and I'll create your personalized mock test! For example:
- "All chapters from Class 10 Math"
- "Only Trigonometry, Quadratic Equations, and Statistics"
- "My weak areas: Probability and Constructions"

Once you tell me, I'll generate a full exam paper you can practice with proper timing! ⏱️"""
            }

        # Fallback if no Gemini client
        if not self.client:
            return self._fallback_response()

        # Build system prompt (enhanced mission)
        system_prompt = self._build_system_prompt(student_context)

        # Build conversation context
        messages = conversation_history or []
        messages.append({"role": "user", "content": student_message})

        # Convert to Gemini format
        prompt = self._build_gemini_prompt(system_prompt, messages)

        try:
            # Build generate_content arguments
            gen_args = {
                "model": self.config.model,
                "contents": prompt,
            }

            # Tools parameter disabled - causes TypeError with current Gemini client version
            # Will be re-enabled when Gemini SDK supports function calling via this param
            # if tools:
            #     gen_args["tools"] = tools

            response = self.client.models.generate_content(**gen_args)

            # Check for function calls (tool calls)
            function_calls = getattr(response, 'function_calls', None)
            if function_calls and tools:
                # Tool calling mode
                tool_calls = []
                for call in function_calls:
                    tool_calls.append({
                        "tool_name": call.name,
                        "args": dict(call.args) if hasattr(call, 'args') else {}
                    })

                return {
                    "agent": "atlas",
                    "session_id": session_id,
                    "tool_calls": tool_calls,
                    "state": "tool_calling",
                    "text": "",
                }

            # Extract text response
            text = self._extract_response_text(response)
            if not text:
                return self._fallback_response()

            return {
                "agent": "atlas",
                "session_id": session_id,
                "state": "plan_created",
                "text": text,
            }

        except Exception as exc:
            logger.exception(f"ATLAS: Error in plan: {exc}")
            return self._fallback_response()

    def _build_system_prompt(self, student_context: Optional[Dict[str, Any]]) -> str:
        """Build enhanced system prompt for strategic planning"""

        # Extract student context
        weak_areas = []
        exam_date = "March 2026"
        mastery_scores = {}

        if student_context:
            weak_areas = student_context.get("weak_areas", [])
            exam_date = student_context.get("exam_date", "March 2026")
            mastery_scores = student_context.get("mastery_scores", {})

        mastery_summary = ""
        if mastery_scores:
            mastery_summary = "\n".join([
                f"- {concept}: {score:.0%} mastery"
                for concept, score in list(mastery_scores.items())[:10]
            ])
        else:
            mastery_summary = "No mastery data available yet"

        return f"""You are ATLAS - Strategic Life & Exam Planner for Indian board exam students.

MISSION: Develop STRATEGIC THINKING and time management mastery that makes students future-ready.

YOUR CAPABILITIES:
1. Adaptive Study Plans: Customize based on exam date, weak areas, mastery scores
2. Strategic Prioritization: 80/20 rule - focus on high-impact topics first
3. Time Management: Teach timeboxing, sprints, Pareto principle
4. Goal Systems: SMART goals with milestone tracking
5. Meta-Learning: Teach HOW to plan, not just WHAT to study

STUDENT CONTEXT:
Exam Date: {exam_date}
Weak Areas: {', '.join(weak_areas) if weak_areas else 'Not identified yet'}

Current Mastery Scores:
{mastery_summary}

PLANNING FRAMEWORK:

EXAM PROXIMITY:
- < 30 days: CRISIS MODE → Focus 80% on weak areas + high-weightage topics
- 30-60 days: BALANCED → 60% weak areas, 40% comprehensive coverage
- > 60 days: MASTERY MODE → Comprehensive learning with deep understanding

PRIORITIZATION STRATEGY (80/20 Rule):
1. High-weightage topics (15+ marks): Priority 1
2. Student's weak areas (< 60% mastery): Priority 2
3. Medium-weightage topics (6-10 marks): Priority 3
4. Strong areas (> 80% mastery): Maintenance only

TIME ALLOCATION:
- Daily: 2-3 focused sprints (45-90 min each)
- Weekly: 5 study days, 2 active rest days (light review, practice tests)
- Monthly: 1 comprehensive mock exam to track progress

TOOLS YOU HAVE:
- create_study_plan: Generate personalized weekly study plan
- fetch_cbse_exam_dates: Get official CBSE exam schedule
- prioritize_topics: Analyze mastery data and suggest priority order

RESPONSE STYLE:
- Strategic, clear, actionable
- Default to English. Use vernacular only if student explicitly uses it (Hinglish, Tanglish, Tenglish, Kanglish, Manglish, Benglish, Marathglish, Gujarlish)
- Focus on WHY (strategy) before WHAT (tasks)
- Teach meta-skills: "Here's how to plan when I'm not around"
- Balance urgency with sustainability (no burnout marathons)

DECISION LOGIC:

IF student asks "What should I study?":
→ Use prioritize_topics tool to analyze weak areas
→ Apply 80/20 rule: Focus on high-impact topics first
→ Explain WHY this prioritization (teach strategic thinking)

IF student asks "How much time for each topic?":
→ Use create_study_plan tool with exam date + weak areas
→ Allocate time using: Weak areas (60%) + High-weightage (30%) + Review (10%)

IF student asks "When is the exam?":
→ Use fetch_cbse_exam_dates tool
→ Calculate days remaining
→ Adjust strategy based on proximity

RESPONSE FORMAT:
1. Strategic context: "With X days until exam, here's the strategy..."
2. Prioritized plan: "Focus 80% effort on these 3 topics first..."
3. Time allocation: "Week 1: [specific topics with hours]..."
4. Meta-lesson: "This teaches you a planning skill you'll use in college/career"

Remember: You're not just helping students pass exams - you're building strategic thinkers who excel at planning their entire lives.
"""

    def _build_gemini_prompt(
        self, system_prompt: str, messages: List[Dict[str, str]]
    ) -> str:
        """Build prompt in Gemini format"""
        history_lines = []
        for msg in messages[-5:]:  # Last 5 messages for context
            role = msg.get("role", "user")
            content = msg.get("content", "")
            prefix = "Student" if role == "user" else "ATLAS"
            history_lines.append(f"{prefix}: {content}")

        prompt = f"""{system_prompt}

CONVERSATION HISTORY:
{chr(10).join(history_lines)}

Create a strategic, actionable study plan. Use tools when appropriate. Teach the meta-skill of planning."""

        return prompt

    def _extract_response_text(self, response: Any) -> str:
        """Extract text from Gemini response"""
        try:
            if hasattr(response, 'text'):
                return response.text.strip()
            elif hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                    parts = candidate.content.parts
                    if parts and hasattr(parts[0], 'text'):
                        return parts[0].text.strip()
            return ""
        except Exception as exc:
            logger.warning(f"ATLAS: Failed to extract text: {exc}")
            return ""

    def _fallback_response(self) -> Dict[str, Any]:
        """Fallback response when Gemini unavailable"""
        return {
            "agent": "atlas",
            "text": (
                "Let's create a strategic study plan together. "
                "With your exam coming up, we'll use the 80/20 rule: "
                "focus 80% effort on your weak areas and high-weightage topics. "
                "Tell me which topics feel hardest right now, and we'll prioritize from there."
            ),
            "fallback": True,
        }
    def _format_progress_response(self, progress_data: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Format progress data into a student-friendly response"""
        
        total_attempted = progress_data.get("total_questions_attempted", 0)
        accuracy = progress_data.get("accuracy", 0)
        weak_areas = progress_data.get("weak_areas", [])
        mastered_topics = progress_data.get("mastered_topics", [])
        overall_mastery = progress_data.get("overall_mastery", 0) * 100
        recommendations = progress_data.get("recommendations", [])
        
        # Build response text
        response_lines = [
            "📊 **Your Progress Report**\n",
            f"**Questions Attempted:** {total_attempted}",
            f"**Overall Accuracy:** {accuracy}%",
            f"**Mastery Level:** {overall_mastery:.0f}%\n"
        ]
        
        if mastered_topics:
            response_lines.append("✅ **Mastered Topics:**")
            for topic in mastered_topics[:5]:
                response_lines.append(f"  - {topic.replace('_', ' ').title()}")
            response_lines.append("")
        
        if weak_areas:
            response_lines.append("⚠️ **Needs Practice:**")
            for area in weak_areas[:5]:
                response_lines.append(f"  - {area.replace('_', ' ').title()}")
            response_lines.append("")
        
        if recommendations:
            response_lines.append("💡 **Recommendations:**")
            for rec in recommendations:
                response_lines.append(f"  - {rec}")
        
        if total_attempted < 10:
            response_lines.append("\n🎯 **Keep going!** Complete at least 50 questions for a detailed analysis.")
        elif accuracy < 60:
            response_lines.append("\n📚 **Focus on understanding first.** Quality over speed!")
        elif accuracy > 85:
            response_lines.append("\n🌟 **Excellent work!** Ready for harder challenges?")
        
        return {
            "agent": "atlas",
            "session_id": session_id,
            "text": "\n".join(response_lines)
        }