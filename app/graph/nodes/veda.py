from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List

from app.agents.veda import VEDAAdapter
from app.graph.personas import build_prefixed_text
from app.graph.state import AgentState, safe_last_user_message
from app.tools import get_tool_registry

logger = logging.getLogger(__name__)


class VedaNode:
    def __init__(self) -> None:
        self.veda = VEDAAdapter()

    async def run(self, state: AgentState) -> Dict[str, Any]:
        user_text = safe_last_user_message(state.get("messages", []))
        session_id = state.get("session_id", "chat")
        history = self._history_for_veda(state.get("messages", []))

        # Get language preference from user profile (defaults to None = auto-detect)
        user_profile = state.get("user_profile", {})
        language_pref = user_profile.get("language_preference")

        logger.info(f"VedaNode: {len(state.get('messages', []))} messages, {len(history)} history items, language={language_pref or 'auto-detect'}")

        # Get VEDA's tools (Phase 4: Agentic transformation)
        registry = get_tool_registry()
        tools = registry.to_gemini_tools("veda") if registry.is_initialized else None

        if tools:
            logger.info(f"VedaNode: {len(tools)} tools available for autonomous calling")

        try:
            result = await self.veda.agent.teach(
                student_message=user_text,
                session_id=session_id,
                conversation_history=history,
                explicit_language=language_pref,  # Pass user's language preference
                tools=tools,  # NEW: Enable autonomous tool calling
            )

            # Check if VEDA wants to call tools
            if result.get("tool_calls"):
                logger.info(f"VedaNode: VEDA requested {len(result['tool_calls'])} tool calls")

                # Execute tools
                tool_results = []
                for tool_call in result["tool_calls"]:
                    tool_name = tool_call.get("tool_name")
                    tool_args = tool_call.get("args", {})

                    tool = registry.get(tool_name)
                    if tool:
                        logger.info(f"VedaNode: Executing tool '{tool_name}' with args {tool_args}")
                        tool_result = await tool.execute(**tool_args)
                        tool_results.append({
                            "tool_name": tool_name,
                            "args": tool_args,
                            "data": tool_result.data if tool_result.success else None,
                            "error": tool_result.error,
                            "success": tool_result.success
                        })
                    else:
                        logger.warning(f"VedaNode: Tool '{tool_name}' not found in registry")
                        tool_results.append({
                            "tool_name": tool_name,
                            "args": tool_args,
                            "error": f"Tool '{tool_name}' not found",
                            "success": False
                        })

                # Return with tool_results in state (triggers routing)
                return {
                    "tool_results": tool_results,
                    "hop_count": state.get("hop_count", 0) + 1,
                    "agent_history": state.get("agent_history", []) + ["veda"]
                }

            # Normal teaching response (no tool calls)
            text = (result.get("text") or "").strip()
            if result.get("socratic_question"):
                text = (text + "\n\n" + result["socratic_question"]).strip()
            if not text:
                text = "Let's break this into one small step. What exactly is confusing you?"

        except Exception as exc:
            logger.exception(f"VedaNode error: {exc}")
            text = "Let's restart with one simple step. Tell me which part feels confusing."
            result = {"fallback": True}

        content = build_prefixed_text("veda", text)
        return {
            "messages": [
                {
                    "role": "assistant",
                    "name": "veda",
                    "content": content,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            ],
            "response": {
                "agent_name": "veda",
                "content": content,
                "payload": result,
            },
            "hop_count": state.get("hop_count", 0) + 1,
            "agent_history": state.get("agent_history", []) + ["veda"]
        }

    def _history_for_veda(self, messages: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        history: List[Dict[str, str]] = []
        for item in messages[-16:]:
            role = item.get("role")
            if role in {"user", "assistant"}:
                history.append({"role": role, "content": item.get("content", "")})
        return history
