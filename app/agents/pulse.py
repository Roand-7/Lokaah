"""
PULSE - Resilience & Growth Mindset Builder
Transforms student mental blocks into breakthrough moments
"""

import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
import os

from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class PulseConfig:
    model: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    temperature: float = 0.8  # Higher for empathetic, creative responses
    max_tokens: int = 800  # Concise, actionable support


class PulseAgent:
    """
    PULSE - Mental Resilience & Growth Mindset Coach

    ENHANCED MISSION:
    Not just stress relief - but building UNSHAKEABLE mental resilience
    that helps students excel in exams AND life.

    CORE CAPABILITIES:
    1. Crisis Detection & Intervention (panic attacks, severe anxiety)
    2. Growth Mindset Development ("I can't do this YET" vs "I'm stupid")
    3. Emotional Regulation Techniques (breathing, grounding, reframing)
    4. Resilience Building (learn from failure, celebrate small wins)
    5. Strategic Escalation (counselor for serious mental health issues)

    PHILOSOPHY:
    - Stress is not the enemy - poor coping strategies are
    - Every struggle is a chance to build mental muscle
    - Small consistent wins > big sporadic victories
    - Mental fitness is as important as academic performance
    """

    def __init__(self, config: Optional[PulseConfig] = None, client: Any = None):
        self.config = config or PulseConfig()
        self.client = client or self._init_gemini_client()

    def _init_gemini_client(self) -> Optional[Any]:
        api_key = settings.GEMINI_API_KEY
        try:
            from google import genai

            if api_key:
                client = genai.Client(api_key=api_key)
                logger.info("PULSE: Gemini client initialized")
                return client
            else:
                logger.warning("PULSE: No Gemini API key, using fallback")
                return None
        except Exception as exc:
            logger.exception(f"PULSE: Gemini client init failed: {exc}")
            return None

    async def support(
        self,
        student_message: str,
        session_id: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Provide mental health support and resilience coaching

        Args:
            student_message: Student's message expressing stress/anxiety
            session_id: Current session ID
            conversation_history: Recent conversation context
            tools: Available tools (breathing exercises, escalation, etc.)

        Returns:
            Response with support message and/or tool calls
        """

        # Fallback if no Gemini client
        if not self.client:
            return self._fallback_response(student_message)

        # Build system prompt (enhanced mission)
        system_prompt = self._build_system_prompt()

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

            # Add tools if provided
            if tools:
                gen_args["tools"] = tools

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
                    "agent": "pulse",
                    "session_id": session_id,
                    "tool_calls": tool_calls,
                    "state": "tool_calling",
                    "text": "",
                }

            # Extract text response
            text = self._extract_response_text(response)
            if not text:
                return self._fallback_response(student_message)

            return {
                "agent": "pulse",
                "session_id": session_id,
                "state": "support_provided",
                "text": text,
                "mode": self._detect_mode(student_message),
            }

        except Exception as exc:
            logger.exception(f"PULSE: Error in support: {exc}")
            return self._fallback_response(student_message)

    def _build_system_prompt(self) -> str:
        """Build enhanced system prompt for resilience coaching"""
        return """You are PULSE - a Mental Resilience & Growth Mindset Coach for Indian board exam students.

MISSION: Transform mental blocks into breakthrough moments. Build UNSHAKEABLE resilience.

YOUR CAPABILITIES:
1. Crisis Intervention: Detect panic/severe anxiety, provide immediate grounding techniques
2. Growth Mindset: Reframe "I'm stupid" → "I haven't mastered this YET"
3. Emotional Regulation: Breathing, grounding, cognitive reframing
4. Resilience Building: Learn from failure, celebrate small wins, progressive challenges
5. Strategic Escalation: Flag serious mental health issues for professional help

COMMUNICATION STYLE:
- Warm, empathetic, non-judgmental
- Default to English. Use vernacular only if student explicitly uses it (Hinglish, Tanglish, Tenglish, Kanglish, Manglish, Benglish, Marathglish, Gujarlish)
- Short, actionable messages (3-4 sentences max)
- Focus on immediate relief THEN long-term resilience
- Celebrate effort, not just results

DECISION FRAMEWORK:

IF student shows CRISIS signs (panic attack, self-harm thoughts, severe anxiety):
→ Use send_breathing_exercise tool (4-4-4-4 rhythm)
→ If crisis persists after 2 interventions: escalate_to_counselor

IF student shows FIXED mindset ("I'm stupid", "I can't do this", "I'll fail"):
→ Reframe with growth mindset ("You haven't mastered this YET")
→ Celebrate effort, not outcomes ("You tried 5 problems - that's progress!")

IF student shows BURNOUT (overwhelmed, exhausted, giving up):
→ Use suggest_break tool (5-10 min strategic break)
→ Help prioritize: "Let's do ONE easy win right now to rebuild momentum"

IF student shows PERFORMANCE anxiety (exam fear, comparison with others):
→ Normalize: "Every topper felt this way at some point"
→ Focus on process, not outcome: "Let's master one concept today"

TOOLS YOU HAVE:
- send_breathing_exercise: Guided breathing for immediate calm
- suggest_break: Strategic breaks to prevent burnout
- escalate_to_counselor: Flag for professional mental health support

RESPONSE FORMAT:
1. Acknowledge emotion: "I hear you're feeling overwhelmed"
2. Immediate relief: Breathing/break/reframe
3. Growth moment: "This struggle is building your mental muscle"
4. Next tiny step: "Let's do just ONE easy problem to rebuild confidence"

Remember: Every student struggle is a chance to build resilience. Small wins compound into unstoppable confidence.
"""

    def _build_gemini_prompt(
        self, system_prompt: str, messages: List[Dict[str, str]]
    ) -> str:
        """Build prompt in Gemini format"""
        history_lines = []
        for msg in messages[-5:]:  # Last 5 messages for context
            role = msg.get("role", "user")
            content = msg.get("content", "")
            prefix = "Student" if role == "user" else "PULSE"
            history_lines.append(f"{prefix}: {content}")

        prompt = f"""{system_prompt}

CONVERSATION HISTORY:
{chr(10).join(history_lines)}

Provide empathetic, actionable support. Use tools when appropriate. Keep response under 4 sentences."""

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
            logger.warning(f"PULSE: Failed to extract text: {exc}")
            return ""

    def _detect_mode(self, message: str) -> str:
        """Detect support mode based on message content"""
        lower = message.lower()

        if any(word in lower for word in ["panic", "attack", "heart racing", "can't breathe"]):
            return "crisis"
        elif any(word in lower for word in ["stupid", "failure", "can't do", "giving up"]):
            return "growth_mindset"
        elif any(word in lower for word in ["tired", "exhausted", "overwhelmed", "too much"]):
            return "burnout"
        elif any(word in lower for word in ["exam", "scared", "nervous", "anxious"]):
            return "performance_anxiety"
        else:
            return "general_support"

    def _fallback_response(self, message: str) -> Dict[str, Any]:
        """Fallback response when Gemini unavailable"""
        mode = self._detect_mode(message)

        fallback_messages = {
            "crisis": (
                "I hear you. Let's pause everything and breathe together. "
                "Inhale for 4 counts, hold 4, exhale 4, repeat 4 times. "
                "You are safe. After this, we tackle one tiny step."
            ),
            "growth_mindset": (
                "You're not the problem - your strategy needs tuning. "
                "Every topper struggled before breaking through. "
                "Let's reset and finish ONE easy win now to rebuild momentum."
            ),
            "burnout": (
                "You're carrying too much. Let's reduce pressure: "
                "one 10-minute sprint, one concept, then quick break. "
                "Small consistent wins beat heroic marathons."
            ),
            "performance_anxiety": (
                "Exam anxiety is normal - it means you care. "
                "But let's channel it: focus on mastering today's topic, not tomorrow's results. "
                "One concept at a time builds unstoppable confidence."
            ),
            "general_support": (
                "I'm here for you. Tell me what's making this feel hard right now, "
                "and we'll break it into one manageable step together."
            ),
        }

        return {
            "agent": "pulse",
            "text": fallback_messages.get(mode, fallback_messages["general_support"]),
            "mode": mode,
            "fallback": True,
        }
