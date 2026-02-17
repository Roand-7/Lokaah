from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List

from app.agents.pulse import PulseAgent
from app.graph.personas import build_prefixed_text
from app.graph.state import AgentState, safe_last_user_message
from app.tools import get_tool_registry

logger = logging.getLogger(__name__)


class PulseNode:
    """
    PULSE Node - Mental Resilience & Growth Mindset Builder
    Converts from hardcoded templates to full LLM-powered agent
    """

    def __init__(self) -> None:
        self.pulse = PulseAgent()

    async def run(self, state: AgentState) -> Dict[str, Any]:
        user_text = safe_last_user_message(state.get("messages", []))
        session_id = state.get("session_id", "chat")
        history = self._history_for_pulse(state.get("messages", []))

        logger.info(f"PulseNode: {len(state.get('messages', []))} messages, {len(history)} history items")

        # Get PULSE's tools (breathing exercises, escalation, etc.)
        registry = get_tool_registry()
        tools = registry.to_gemini_tools("pulse") if registry.is_initialized else None

        if tools:
            logger.info(f"PulseNode: {len(tools)} tools available")

        try:
            result = await self.pulse.support(
                student_message=user_text,
                session_id=session_id,
                conversation_history=history,
                tools=tools,
            )

            # Check if PULSE wants to call tools
            if result.get("tool_calls"):
                logger.info(f"PulseNode: PULSE requested {len(result['tool_calls'])} tool calls")

                # Execute tools
                tool_results = []
                for tool_call in result["tool_calls"]:
                    tool_name = tool_call.get("tool_name")
                    tool_args = tool_call.get("args", {})

                    tool = registry.get(tool_name)
                    if tool:
                        logger.info(f"PulseNode: Executing tool '{tool_name}'")
                        tool_result = await tool.execute(**tool_args)
                        tool_results.append({
                            "tool_name": tool_name,
                            "args": tool_args,
                            "data": tool_result.data if tool_result.success else None,
                            "error": tool_result.error,
                            "success": tool_result.success
                        })
                    else:
                        logger.warning(f"PulseNode: Tool '{tool_name}' not found")
                        tool_results.append({
                            "tool_name": tool_name,
                            "error": f"Tool '{tool_name}' not found",
                            "success": False
                        })

                # Return with tool_results in state
                return {
                    "tool_results": tool_results,
                    "hop_count": state.get("hop_count", 0) + 1,
                    "agent_history": state.get("agent_history", []) + ["pulse"]
                }

            # Normal support response
            text = result.get("text", "I'm here for you. Let's take this one step at a time.")

        except Exception as exc:
            logger.exception(f"PulseNode error: {exc}")
            text = "I'm here for you. Let's pause and breathe. Tell me what feels hardest right now."
            result = {"fallback": True}

        content = build_prefixed_text("pulse", text)
        return {
            "messages": [
                {
                    "role": "assistant",
                    "name": "pulse",
                    "content": content,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            ],
            "response": {
                "agent_name": "pulse",
                "content": content,
                "payload": result,
            },
            "hop_count": state.get("hop_count", 0) + 1,
            "agent_history": state.get("agent_history", []) + ["pulse"]
        }

    def _history_for_pulse(self, messages: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Get recent conversation history for context"""
        history = []
        for item in messages[-8:]:  # Last 8 messages for emotional context
            role = item.get("role")
            if role in {"user", "assistant"}:
                history.append({"role": role, "content": item.get("content", "")})
        return history
