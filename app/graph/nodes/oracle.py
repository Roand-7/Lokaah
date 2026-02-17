from __future__ import annotations

import random
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from app.core.config import settings
from app.graph.personas import build_prefixed_text
from app.graph.state import AgentState, safe_last_user_message
from app.oracle.hybrid_orchestrator import get_hybrid_orchestrator


TOPIC_HINTS = [
    ("trigonometry", "trigonometry_heights"),
    ("triangle", "triangle_bpt_basic"),
    ("circle", "circle_tangent_equal_length"),
    ("coordinate", "coord_distance_formula"),
    ("statistics", "statistics_mean_frequency_table"),
    ("probability", "probability_single_card"),
    ("quadratic", "quadratic_formula_solve"),
    ("linear", "linear_equations"),
    ("ap", "ap_nth_term_basic"),
    ("progression", "ap_sum_n_terms"),
]


class OracleNode:
    def __init__(self, mode: str = "oracle") -> None:
        self.mode = mode
        self.orchestrator = None
        self._init_error: Optional[str] = None

    async def run(self, state: AgentState) -> Dict[str, Any]:
        user_text = safe_last_user_message(state.get("messages", []))
        concept = self._guess_concept(user_text)
        difficulty = self._infer_difficulty(user_text)
        marks = 5 if self.mode == "spark" else 3

        if self.mode == "spark":
            difficulty = max(0.8, difficulty)

        orchestrator = self._get_orchestrator()
        if orchestrator is None:
            content = build_prefixed_text(
                "spark" if self.mode == "spark" else "oracle",
                self._fallback_question_text(concept=concept, marks=marks),
            )
            return {
                "messages": [
                    {
                        "role": "assistant",
                        "name": "spark" if self.mode == "spark" else "oracle",
                        "content": content,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                ],
                "response": {
                    "agent_name": "spark" if self.mode == "spark" else "oracle",
                    "content": content,
                    "payload": {"fallback": True, "error": self._init_error, "concept": concept},
                },
            }

        result = orchestrator.generate_question(concept=concept, marks=marks, difficulty=difficulty)

        text = self._render_question(result.question_text, marks, result.source)
        agent_name = "spark" if self.mode == "spark" else "oracle"
        content = build_prefixed_text(agent_name, text)
        return {
            "messages": [
                {
                    "role": "assistant",
                    "name": agent_name,
                    "content": content,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            ],
            "response": {
                "agent_name": agent_name,
                "content": content,
                "payload": {
                    "question_id": result.question_id,
                    "question_text": result.question_text,
                    "marks": result.marks,
                    "difficulty": result.difficulty,
                    "source": result.source,
                    "solution_steps": result.solution_steps,
                    "jsxgraph_code": result.jsxgraph_code,
                },
            },
        }

    def _get_orchestrator(self):
        if self.orchestrator is not None:
            return self.orchestrator
        try:
            self.orchestrator = get_hybrid_orchestrator(ai_ratio=settings.AI_RATIO)
            return self.orchestrator
        except Exception as exc:
            self._init_error = str(exc)
            return None

    def _guess_concept(self, text: str) -> str:
        lower = (text or "").lower()
        for keyword, concept in TOPIC_HINTS:
            if keyword in lower:
                return concept
        return "trigonometry_heights"

    def _infer_difficulty(self, text: str) -> float:
        lower = (text or "").lower()
        if any(token in lower for token in ("easy", "basic", "simple")):
            return 0.35
        if any(token in lower for token in ("hard", "tough", "challenge", "5 mark")):
            return 0.85
        return 0.6

    def _render_question(self, question_text: str, marks: int, source: str) -> str:
        """
        Generate natural conversational wrapper for question.
        Uses random variations to feel less templated.
        """
        # Define natural intros based on mode
        if self.mode == "spark":
            intros = [
                "Alright, ready for a challenge?",
                "Let's kick it up a notch!",
                "Think you can handle this one?",
                "Time to test your skills!",
                "Here's a good one for you:",
                "Let's see what you've got!",
            ]
        else:
            intros = [
                "Try this one:",
                "Here's a question for you:",
                "Let's work on this:",
                "Give this a shot:",
                "See if you can solve this:",
                "Here's your next problem:",
            ]
        
        # Define natural closings
        closings = [
            "What do you think?",
            "Give it a try!",
            "Show me your work.",
            "Take your time.",
            "See what you come up with.",
            "Let me know your answer!",
        ]
        
        intro = random.choice(intros)
        closing = random.choice(closings)
        
        return (
            f"{intro}\n\n"
            f"**({marks} marks)**\n"
            f"{question_text}\n\n"
            f"{closing}"
        )

    def _fallback_question_text(self, concept: str, marks: int) -> str:
        return (
            f"Here's a quick one for you. **({marks} marks)**\n\n"
            "A ladder leans against a wall making a 60 deg angle with the ground. "
            "If the foot of the ladder is 4 m from the wall, find the height reached.\n\n"
            "What do you get?"
        )
