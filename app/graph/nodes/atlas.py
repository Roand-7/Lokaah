from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List

from app.agents.atlas import AtlasAgent
from app.graph.personas import build_prefixed_text
from app.graph.state import AgentState, safe_last_user_message
from app.tools import get_tool_registry

logger = logging.getLogger(__name__)


class AtlasNode:
    """
    ATLAS Node - Strategic Life & Exam Planner
    Converts from JSON-based schedules to full LLM-powered strategic planning
    """

    def __init__(self) -> None:
        self.atlas = AtlasAgent()

    async def run(self, state: AgentState) -> Dict[str, Any]:
        user_text = safe_last_user_message(state.get("messages", []))
        session_id = state.get("session_id", "chat")
        history = self._history_for_atlas(state.get("messages", []))

        logger.info(f"AtlasNode: {len(state.get('messages', []))} messages, {len(history)} history items")

        # Get ATLAS's tools (study plan creation, exam dates, prioritization)
        registry = get_tool_registry()
        tools = registry.to_gemini_tools("atlas") if registry.is_initialized else None

        if tools:
            logger.info(f"AtlasNode: {len(tools)} tools available")

        # Extract student context for personalized planning
        student_context = self._extract_student_context(state)

        try:
            result = await self.atlas.plan(
                student_message=user_text,
                session_id=session_id,
                conversation_history=history,
                tools=tools,
                student_context=student_context,
            )

            # Check if ATLAS wants to call tools
            if result.get("tool_calls"):
                logger.info(f"AtlasNode: ATLAS requested {len(result['tool_calls'])} tool calls")

                # Execute tools
                tool_results = []
                for tool_call in result["tool_calls"]:
                    tool_name = tool_call.get("tool_name")
                    tool_args = tool_call.get("args", {})

                    tool = registry.get(tool_name)
                    if tool:
                        logger.info(f"AtlasNode: Executing tool '{tool_name}'")
                        tool_result = await tool.execute(**tool_args)
                        tool_results.append({
                            "tool_name": tool_name,
                            "args": tool_args,
                            "data": tool_result.data if tool_result.success else None,
                            "error": tool_result.error,
                            "success": tool_result.success
                        })
                    else:
                        logger.warning(f"AtlasNode: Tool '{tool_name}' not found")
                        tool_results.append({
                            "tool_name": tool_name,
                            "error": f"Tool '{tool_name}' not found",
                            "success": False
                        })

                # Return with tool_results in state
                return {
                    "tool_results": tool_results,
                    "hop_count": state.get("hop_count", 0) + 1,
                    "agent_history": state.get("agent_history", []) + ["atlas"]
                }

            # Normal planning response
            text = result.get("text", "Let's create a strategic study plan together.")

        except Exception as exc:
            logger.exception(f"AtlasNode error: {exc}")
            text = (
                "Let's create a strategic study plan. Tell me which topics feel hardest, "
                "and we'll use the 80/20 rule to prioritize your effort."
            )
            result = {"fallback": True}

        content = build_prefixed_text("atlas", text)
        return {
            "messages": [
                {
                    "role": "assistant",
                    "name": "atlas",
                    "content": content,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            ],
            "response": {
                "agent_name": "atlas",
                "content": content,
                "payload": result,
            },
            "hop_count": state.get("hop_count", 0) + 1,
            "agent_history": state.get("agent_history", []) + ["atlas"]
        }

    def _history_for_atlas(self, messages: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Get recent conversation history for context"""
        history = []
        for item in messages[-8:]:  # Last 8 messages for planning context
            role = item.get("role")
            if role in {"user", "assistant"}:
                history.append({"role": role, "content": item.get("content", "")})
        return history

    def _extract_student_context(self, state: AgentState) -> Dict[str, Any]:
        """Extract student context from state for personalized planning"""
        # TODO: In future, fetch from database
        # For now, return basic context
        return {
            "exam_date": "March 2026",
            "weak_areas": [],  # Will be populated from concept_mastery table
            "mastery_scores": {},  # Will be populated from database
        }
