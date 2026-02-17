from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.graph.personas import PERSONA_META
from app.graph.state import AgentState, normalize_agent_name
from app.graph.nodes import AtlasNode, OracleNode, PulseNode, SupervisorNode, VedaNode
from app.graph.nodes.reflection import ReflectionNode
from app.tools import get_tool_registry, initialize_tools

logger = logging.getLogger(__name__)

class LokaahGraphRuntime:
    """
    Single-chat runtime with invisible handoff across specialized agents.
    Uses LangGraph when available, and falls back to a deterministic router.
    """

    def __init__(self) -> None:
        self.supervisor = SupervisorNode()
        self.veda = VedaNode()
        self.oracle = OracleNode(mode="oracle")
        self.spark = OracleNode(mode="spark")
        self.pulse = PulseNode()
        self.atlas = AtlasNode()
        self.reflection = ReflectionNode()

        # Initialize tool registry (Phase 1 integration)
        # Note: This will be enhanced in Phase 4 with real dependencies
        try:
            from app.core.database import get_db
            self.tool_registry = initialize_tools(
                supabase_client=get_db(),
                gemini_client=self.veda.veda.agent.client,
                exam_db=self.veda.veda.agent.exam_db,
                diagram_gen=self.veda.veda.agent.diagram_gen
            )
            logger.info("Tool registry initialized with %d tools", len(self.tool_registry.list_all_tools()))
        except Exception as exc:
            logger.warning("Tool registry initialization failed: %s", exc)
            self.tool_registry = get_tool_registry()

        self._session_memory: Dict[str, List[Dict[str, Any]]] = {}
        self._compiled_graph = None
        self._runtime_mode = "fallback"
        self._compile_error: Optional[str] = None
        self._has_checkpointer = False
        self._build_graph_if_available()

    def _build_graph_if_available(self) -> None:
        try:
            from langgraph.graph import END, StateGraph
            checkpointer = None
            try:
                from langgraph.checkpoint.memory import MemorySaver

                checkpointer = MemorySaver()
                self._has_checkpointer = True
            except Exception as exc:
                self._has_checkpointer = False
                logger.warning("LangGraph MemorySaver unavailable: %s", exc)

            workflow = StateGraph(AgentState)

            async def supervisor_node(state: AgentState) -> Dict[str, Any]:
                return self.supervisor.route(state)

            async def veda_node(state: AgentState) -> Dict[str, Any]:
                return await self.veda.run(state)

            async def oracle_node(state: AgentState) -> Dict[str, Any]:
                return await self.oracle.run(state)

            async def spark_node(state: AgentState) -> Dict[str, Any]:
                return await self.spark.run(state)

            async def pulse_node(state: AgentState) -> Dict[str, Any]:
                return await self.pulse.run(state)

            async def atlas_node(state: AgentState) -> Dict[str, Any]:
                return await self.atlas.run(state)

            async def reflection_node(state: AgentState) -> Dict[str, Any]:
                return await self.reflection.run(state)

            async def finish_node(state: AgentState) -> Dict[str, Any]:
                message = {
                    "role": "assistant",
                    "name": "veda",
                    "content": "Take care! Your progress is saved. Message me anytime you're ready to continue — I'll remember where we left off. 😊",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
                return {
                    "messages": [message],
                    "response": {"agent_name": "veda", "content": message["content"]},
                }

            workflow.add_node("supervisor", supervisor_node)
            workflow.add_node("veda", veda_node)
            workflow.add_node("oracle", oracle_node)
            workflow.add_node("spark", spark_node)
            workflow.add_node("pulse", pulse_node)
            workflow.add_node("atlas", atlas_node)
            workflow.add_node("reflection", reflection_node)
            workflow.add_node("finish", finish_node)

            workflow.set_entry_point("supervisor")
            workflow.add_conditional_edges(
                "supervisor",
                lambda state: state.get("next_agent", "veda"),
                {
                    "veda": "veda",
                    "oracle": "oracle",
                    "spark": "spark",
                    "pulse": "pulse",
                    "atlas": "atlas",
                    "FINISH": "finish",
                },
            )

            # Multi-hop routing functions
            def veda_router(state: AgentState) -> str:
                """Route VEDA to ORACLE (if practice requested) or REFLECTION"""
                # Check if hop limit reached
                hop_count = state.get("hop_count", 0)
                if hop_count >= 5:
                    logger.warning("Max hops (5) reached, forcing END")
                    return "END"

                # Check tool results for routing signals
                tool_results = state.get("tool_results", [])
                for result in tool_results:
                    if result.get("tool_name") == "generate_practice_question":
                        logger.info("VEDA routing to ORACLE for practice question")
                        return "oracle"

                # Default: route to reflection for quality check
                return "reflection"

            def oracle_router(state: AgentState) -> str:
                """Route ORACLE back to VEDA (if student struggling) or REFLECTION"""
                hop_count = state.get("hop_count", 0)
                if hop_count >= 5:
                    return "END"

                # Check tool results for student performance
                tool_results = state.get("tool_results", [])
                for result in tool_results:
                    if result.get("tool_name") == "track_student_attempt":
                        attempt_data = result.get("data", {})
                        if not attempt_data.get("is_correct"):
                            logger.info("ORACLE routing back to VEDA (student struggling)")
                            return "veda"

                # Default: route to reflection
                return "reflection"

            def reflection_router(state: AgentState) -> str:
                """Route from REFLECTION back to agent or to END"""
                next_agent = state.get("next_agent", "END")
                return next_agent

            def default_router(state: AgentState) -> str:
                """Default router for PULSE, ATLAS, SPARK - go to reflection"""
                hop_count = state.get("hop_count", 0)
                if hop_count >= 5:
                    return "END"
                return "reflection"

            # Add conditional edges for multi-hop routing
            workflow.add_conditional_edges("veda", veda_router, {
                "oracle": "oracle",
                "reflection": "reflection",
                "END": END
            })

            workflow.add_conditional_edges("oracle", oracle_router, {
                "veda": "veda",
                "reflection": "reflection",
                "END": END
            })

            workflow.add_conditional_edges("pulse", default_router, {
                "reflection": "reflection",
                "END": END
            })

            workflow.add_conditional_edges("atlas", default_router, {
                "reflection": "reflection",
                "END": END
            })

            workflow.add_conditional_edges("spark", default_router, {
                "reflection": "reflection",
                "END": END
            })

            workflow.add_conditional_edges("reflection", reflection_router, {
                "veda": "veda",
                "oracle": "oracle",
                "pulse": "pulse",
                "atlas": "atlas",
                "spark": "spark",
                "END": END
            })

            workflow.add_edge("finish", END)

            if checkpointer is not None:
                self._compiled_graph = workflow.compile(checkpointer=checkpointer)
            else:
                self._compiled_graph = workflow.compile()
            self._runtime_mode = "langgraph"
            logger.info(
                "LangGraph runtime ready. mode=%s checkpointer=%s",
                self._runtime_mode,
                self._has_checkpointer,
            )
        except Exception as exc:
            self._runtime_mode = "fallback"
            self._compile_error = str(exc)
            logger.warning("LangGraph compile failed; using fallback runtime: %s", exc)

    def _summarize_history(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Keep history concise: if > 20 messages, compress older ones into a
        single summary message so agent prompts aren't truncated.
        Keeps the 12 most recent messages intact for context.
        """
        if len(messages) <= 20:
            return messages

        recent_count = 12
        old_messages = messages[:-recent_count]
        recent_messages = messages[-recent_count:]

        # Build a concise summary of older conversation
        summary_parts = []
        for msg in old_messages:
            role = msg.get("role", "unknown")
            content = (msg.get("content") or "")[:120]
            if content:
                label = "Student" if role == "user" else msg.get("name", "Tutor")
                summary_parts.append(f"- {label}: {content}")

        summary_text = (
            "[Earlier conversation summary]\n"
            + "\n".join(summary_parts[-10:])  # Keep last 10 summaries max
        )

        summary_msg: Dict[str, Any] = {
            "role": "system",
            "content": summary_text,
            "name": "context_summary",
        }

        return [summary_msg] + recent_messages

    async def run_turn(
        self,
        message: str,
        session_id: Optional[str] = None,
        user_profile: Optional[Dict[str, Any]] = None,
        force_agent: Optional[str] = None,
    ) -> Dict[str, Any]:
        sid = session_id or f"chat_{uuid.uuid4().hex[:12]}"
        history = self._summarize_history(list(self._session_memory.get(sid, [])))

        user_message = {
            "role": "user",
            "content": message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        base_state: AgentState = {
            "messages": history + [user_message],
            "session_id": sid,
            "user_profile": user_profile or {},
            "metadata": {},
            # Multi-hop tracking (Phase 2)
            "tool_results": [],
            "hop_count": 0,
            "agent_history": [],
        }

        forced = normalize_agent_name(force_agent) if force_agent else None
        if forced:
            if message.strip().startswith("/"):
                logger.info(
                    "slash_command_used session_id=%s command=%s forced_agent=%s",
                    sid,
                    message.strip().split(" ", 1)[0].lower(),
                    forced,
                )
            logger.info(
                "router_decision session_id=%s route=%s source=manual_override reason=%s confidence=1.000",
                sid,
                forced,
                f"forced agent: {forced}",
            )
            final_state = await self._run_worker(forced, base_state, forced=True)
        elif self._compiled_graph is not None:
            if self._has_checkpointer:
                graph_input: AgentState = {
                    "messages": [user_message],
                    "session_id": sid,
                    "user_profile": user_profile or {},
                    "metadata": {},
                }
                final_state = await self._compiled_graph.ainvoke(
                    graph_input,
                    config={"configurable": {"thread_id": sid}},
                )
            else:
                final_state = await self._compiled_graph.ainvoke(base_state)
        else:
            final_state = await self._run_without_langgraph(base_state)

        messages = list(final_state.get("messages", []))
        # Bound session memory to prevent unbounded growth
        if len(self._session_memory) >= 500 and sid not in self._session_memory:
            oldest = next(iter(self._session_memory))
            del self._session_memory[oldest]
        self._session_memory[sid] = messages[-40:]

        response_payload = final_state.get("response", {})
        agent_name = str(response_payload.get("agent_name") or self._extract_last_agent(messages) or "veda")
        content = str(response_payload.get("content") or self._extract_last_assistant_content(messages))

        persona = PERSONA_META.get(agent_name, PERSONA_META["veda"])
        metadata = final_state.get("metadata", {})

        # Log debug metadata server-side only (never sent to client)
        logger.info(
            "chat_response session_id=%s agent=%s route_reason=%s confidence=%.3f runtime=%s",
            sid,
            agent_name,
            metadata.get("route_reason", "n/a"),
            metadata.get("route_confidence", 0.0),
            self._runtime_mode,
        )

        return {
            "session_id": sid,
            "response": content,
            "agent_name": agent_name,
            "agent_label": persona["label"],
            "agent_emoji": persona["emoji"],
            "agent_color": persona["color"],
        }

    async def _run_without_langgraph(self, state: AgentState) -> AgentState:
        route_data = self.supervisor.route(state)
        merged = {**state, **route_data}
        agent = route_data.get("next_agent", "veda")
        if agent == "FINISH":
            message = {
                "role": "assistant",
                "name": "veda",
                "content": "Great progress today! I'll remember everything. Come back anytime — we'll pick up right where we left off. 📚",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            merged["messages"] = list(merged.get("messages", [])) + [message]
            merged["response"] = {"agent_name": "veda", "content": message["content"]}
            return merged
        return await self._run_worker(agent, merged, forced=False)

    async def _run_worker(self, agent: str, state: AgentState, forced: bool) -> AgentState:
        name = normalize_agent_name(agent)

        # Track agent history and hop count (Phase 2)
        agent_history = list(state.get("agent_history", []))
        agent_history.append(name)
        hop_count = state.get("hop_count", 0) + 1

        # Update state with tracking
        state["agent_history"] = agent_history
        state["hop_count"] = hop_count

        logger.info(
            "agent_hop session_id=%s agent=%s hop=%d history=%s",
            state.get("session_id"),
            name,
            hop_count,
            " → ".join(agent_history)
        )

        node_map = {
            "veda": self.veda.run,
            "oracle": self.oracle.run,
            "spark": self.spark.run,
            "pulse": self.pulse.run,
            "atlas": self.atlas.run,
        }
        worker = node_map.get(name, self.veda.run)
        result = await worker(state)
        merged: AgentState = dict(state)
        if forced:
            merged["metadata"] = {
                **merged.get("metadata", {}),
                "router": "manual_override",
                "route_reason": f"forced agent: {name}",
                "route_confidence": 1.0,
            }
        merged["messages"] = list(state.get("messages", [])) + list(result.get("messages", []))
        if result.get("response"):
            merged["response"] = result["response"]
        return merged

    def _extract_last_assistant_content(self, messages: List[Dict[str, Any]]) -> str:
        for msg in reversed(messages):
            if msg.get("role") == "assistant":
                return str(msg.get("content", ""))
        return ""

    def _extract_last_agent(self, messages: List[Dict[str, Any]]) -> str:
        for msg in reversed(messages):
            if msg.get("role") == "assistant":
                return str(msg.get("name", "veda"))
        return "veda"


_runtime: Optional[LokaahGraphRuntime] = None


def get_chat_runtime() -> LokaahGraphRuntime:
    global _runtime
    if _runtime is None:
        _runtime = LokaahGraphRuntime()
    return _runtime
