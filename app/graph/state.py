from __future__ import annotations

import operator
from typing import Annotated, Any, Dict, List, Optional, TypedDict


class AgentMessage(TypedDict, total=False):
    role: str
    content: str
    name: str
    timestamp: str


class AgentState(TypedDict, total=False):
    messages: Annotated[List[AgentMessage], operator.add]
    next_agent: str
    user_profile: Dict[str, Any]
    session_id: str
    metadata: Dict[str, Any]
    response: Dict[str, Any]
    # Multi-hop routing fields
    tool_results: List[Dict[str, Any]]  # Store tool execution results
    hop_count: int  # Track hops (prevent infinite loops)
    reflection_feedback: Optional[str]  # Feedback from reflection
    semantic_summary: Optional[str]  # Conversation summary
    agent_history: List[str]  # Track routing path


ALLOWED_AGENTS = {"veda", "oracle", "pulse", "atlas", "spark", "FINISH"}


def safe_last_user_message(messages: List[AgentMessage]) -> str:
    for msg in reversed(messages):
        if msg.get("role") == "user":
            return msg.get("content", "")
    return ""


def normalize_agent_name(agent_name: Optional[str]) -> str:
    name = (agent_name or "").strip().lower()
    if name in ALLOWED_AGENTS:
        return name
    return "veda"
