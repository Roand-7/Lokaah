from __future__ import annotations

import json
import logging
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

from dotenv import load_dotenv

from app.graph.state import AgentState, normalize_agent_name, safe_last_user_message
from app.core.config import settings


load_dotenv()
logger = logging.getLogger(__name__)


@dataclass
class RouteDecision:
    next_agent: str
    reason: str
    confidence: float


class SupervisorNode:
    """
    Nirmola supervisor:
    1) slash-command manual override
    2) keyword/rule fallback
    3) optional Gemini classifier for tougher ambiguity
    """

    def __init__(self) -> None:
        self._client = self._init_client()

    def _init_client(self):
        try:
            from google import genai  # type: ignore

            if settings.GEMINI_API_KEY:
                return genai.Client(api_key=settings.GEMINI_API_KEY)
            if settings.GOOGLE_APPLICATION_CREDENTIALS and settings.GOOGLE_CLOUD_PROJECT:
                os.environ.setdefault(
                    "GOOGLE_APPLICATION_CREDENTIALS",
                    settings.GOOGLE_APPLICATION_CREDENTIALS,
                )
                return genai.Client(
                    vertexai=True,
                    project=settings.GOOGLE_CLOUD_PROJECT,
                    location=settings.GOOGLE_CLOUD_LOCATION,
                )
            return None
        except Exception:
            return None

    def route(self, state: AgentState) -> Dict[str, Any]:
        user_text = safe_last_user_message(state.get("messages", []))
        session_id = str(state.get("session_id", "unknown"))
        slash_command = (user_text or "").strip().split(" ", 1)[0].lower()

        slash_decision = self._route_slash_command(user_text)
        if slash_decision:
            self._log_decision(
                session_id=session_id,
                decision=slash_decision,
                route_source="slash",
                slash_command=slash_command,
            )
            return self._to_state_payload(
                slash_decision, route_source="slash", slash_command=slash_command
            )

        rule_decision = self._route_by_rules(user_text)
        if rule_decision.confidence >= 0.82:
            self._log_decision(session_id=session_id, decision=rule_decision, route_source="rules")
            return self._to_state_payload(rule_decision, route_source="rules")

        llm_decision, llm_error = self._route_by_llm(user_text)
        if llm_decision:
            self._log_decision(session_id=session_id, decision=llm_decision, route_source="llm")
            return self._to_state_payload(llm_decision, route_source="llm")

        if llm_error:
            fallback = RouteDecision("veda", "llm parse/error fallback to veda", 0.51)
            self._log_decision(
                session_id=session_id,
                decision=fallback,
                route_source="llm_fallback",
                llm_error=llm_error,
            )
            return self._to_state_payload(fallback, route_source="llm_fallback")

        self._log_decision(session_id=session_id, decision=rule_decision, route_source="rules_low_conf")
        return self._to_state_payload(rule_decision, route_source="rules_low_conf")

    def _route_slash_command(self, text: str) -> Optional[RouteDecision]:
        command = (text or "").strip().split(" ", 1)[0].lower()
        mapping = {
            "/test": ("oracle", "manual override: test mode", 1.0),
            "/spark": ("spark", "manual override: spark mode", 1.0),
            "/chill": ("pulse", "manual override: calm mode", 1.0),
            "/plan": ("atlas", "manual override: plan mode", 1.0),
            "/veda": ("veda", "manual override: teaching mode", 1.0),
            "/oracle": ("oracle", "manual override: oracle mode", 1.0),
            "/pulse": ("pulse", "manual override: pulse mode", 1.0),
            "/atlas": ("atlas", "manual override: atlas mode", 1.0),
            "/bye": ("FINISH", "manual override: finish", 1.0),
        }
        if command in mapping:
            agent, reason, confidence = mapping[command]
            return RouteDecision(agent, reason, confidence)
        return None

    def _route_by_rules(self, text: str) -> RouteDecision:
        message = (text or "").lower()

        # Only end session for explicit closures (not simple "thank you")
        if any(phrase in message for phrase in ("goodbye", "see you later", "that's all", "i'm done", "close session")):
            return RouteDecision("FINISH", "conversation closure intent", 0.98)
        
        # Explicit /bye command only
        if message.strip() == "bye" or message.strip() == "/bye":
            return RouteDecision("FINISH", "explicit bye command", 1.0)
        
        # Casual greetings/thanks should stay with VEDA for natural conversation
        if any(phrase in message for phrase in ("thank", "thanks", "hello", "hi ", "hey ", "good morning", "good evening", "namaste")):
            return RouteDecision("veda", "greeting/acknowledgment - continuing conversation", 0.85)

        if any(
            token in message
            for token in (
                "stupid",
                "panic",
                "anxious",
                "stress",
                "depressed",
                "burnout",
                "i can't",
                "i am failing",
                "i'm failing",
            )
        ):
            return RouteDecision("pulse", "wellbeing support intent", 0.93)

        if any(
            token in message
            for token in (
                "schedule",
                "timetable",
                "when is my exam",
                "date sheet",
                "revision plan",
                "study plan",
                "calendar",
            )
        ):
            return RouteDecision("atlas", "planning/schedule intent", 0.9)

        if any(
            token in message
            for token in (
                "challenge",
                "hard question",
                "mock test",
                "test me",
                "5 mark",
                "exam pattern",
                "give question",
                "practice",
                "quiz",
            )
        ):
            if any(token in message for token in ("hard", "challenge", "5 mark", "90% fail")):
                return RouteDecision("spark", "high-intensity challenge intent", 0.91)
            return RouteDecision("oracle", "practice/exam intent", 0.88)

        if any(
            token in message
            for token in (
                "explain",
                "understand",
                "how to solve",
                "teach me",
                "what is",
                "why",
                "concept",
                "confused",
            )
        ):
            return RouteDecision("veda", "teaching/concept intent", 0.86)

        return RouteDecision("veda", "default tutoring intent", 0.7)

    def _route_by_llm(self, text: str) -> Tuple[Optional[RouteDecision], Optional[str]]:
        if not self._client:
            return None, None

        prompt = (
            "You are Nirmola, the routing supervisor for Lokaah AI.\n"
            "Classify the user message into one of: veda, oracle, spark, pulse, atlas, FINISH.\n"
            "Return only JSON object: "
            '{"next_agent":"...", "reason":"...", "confidence":0.0}\n'
            "Rules:\n"
            "- pulse: stress, panic, confidence, emotional support\n"
            "- atlas: schedule, plan, exam dates, calendar\n"
            "- oracle: practice/test/challenge questions\n"
            "- spark: difficult challenge or high-energy challenge mode\n"
            "- veda: explanations/teaching/general math chat\n"
            "- FINISH: goodbye/ending chat\n\n"
            f"User message: {text}"
        )

        try:
            response = self._client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=prompt,
            )
            raw = (getattr(response, "text", "") or "").strip()
            parsed = self._parse_json(raw)
            if not parsed:
                return None, "json_parse_failed"
            agent = normalize_agent_name(parsed.get("next_agent"))
            confidence = float(parsed.get("confidence", 0.75))
            reason = str(parsed.get("reason", "llm route"))
            return RouteDecision(agent, reason, confidence), None
        except Exception:
            return None, "llm_exception"

    def _parse_json(self, raw: str) -> Optional[Dict[str, Any]]:
        if not raw:
            return None
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if not match:
                return None
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                return None

    def _to_state_payload(
        self,
        decision: RouteDecision,
        route_source: str = "unknown",
        slash_command: Optional[str] = None,
    ) -> Dict[str, Any]:
        agent = decision.next_agent if decision.next_agent == "FINISH" else normalize_agent_name(decision.next_agent)
        metadata: Dict[str, Any] = {
            "router": "nirmola",
            "route_reason": decision.reason,
            "route_confidence": round(decision.confidence, 3),
            "route_source": route_source,
        }
        if slash_command:
            metadata["slash_command"] = slash_command
        return {
            "next_agent": agent,
            "metadata": metadata,
        }

    def _log_decision(
        self,
        session_id: str,
        decision: RouteDecision,
        route_source: str,
        slash_command: Optional[str] = None,
        llm_error: Optional[str] = None,
    ) -> None:
        message = (
            "router_decision session_id=%s route=%s source=%s reason=%s confidence=%.3f"
        )
        args: list[Any] = [
            session_id,
            decision.next_agent,
            route_source,
            decision.reason,
            decision.confidence,
        ]
        if slash_command:
            message += " slash_command=%s"
            args.append(slash_command)
        if llm_error:
            message += " llm_error=%s"
            args.append(llm_error)
        logger.info(message, *args)
