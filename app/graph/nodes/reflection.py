"""Reflection node for quality control before sending responses to students"""

from __future__ import annotations

import logging
from typing import Any, Dict

from app.graph.state import AgentState, safe_last_user_message
from app.tools import get_tool_registry

logger = logging.getLogger(__name__)


class ReflectionNode:
    """
    Evaluates response quality before sending to user.
    Routes back to originating agent if quality is below threshold.
    """

    def __init__(self):
        self.quality_threshold = 0.7  # Minimum acceptable quality score
        self.max_reflections = 2  # Prevent infinite revision loops

    async def run(self, state: AgentState) -> Dict[str, Any]:
        """
        Evaluate response quality and decide whether to send or revise

        Args:
            state: Current agent state with messages

        Returns:
            Updated state with routing decision
        """
        logger.info("reflection_node evaluating response quality")

        # Get last assistant message
        last_message = self._get_last_assistant_message(state)
        if not last_message:
            logger.warning("No assistant message to reflect on, routing to END")
            return {"next_agent": "END"}

        # Check reflection count
        metadata = state.get("metadata", {})
        reflection_count = metadata.get("reflection_count", 0)

        if reflection_count >= self.max_reflections:
            logger.info(
                f"Max reflections ({self.max_reflections}) reached, approving response"
            )
            return {"next_agent": "END"}

        # Get the agent that generated this response
        last_agent = last_message.get("name", "veda")
        agent_history = state.get("agent_history", [])
        if agent_history:
            last_agent = agent_history[-1]

        # Evaluate response quality
        quality_result = await self._evaluate_quality(last_message, state)

        if not quality_result:
            # Evaluation failed, approve by default to avoid blocking
            logger.warning("Quality evaluation failed, approving response by default")
            return {"next_agent": "END"}

        quality_score = quality_result.get("overall", 0.0)
        logger.info(f"Response quality score: {quality_score:.2f}")

        # Check if quality meets threshold
        if quality_score >= self.quality_threshold:
            logger.info("Quality approved, routing to END")
            return {"next_agent": "END"}

        # Quality below threshold - route back for revision
        feedback = quality_result.get("feedback", "Please improve response quality")
        logger.info(f"Quality below threshold, routing back to {last_agent}")

        updated_metadata = dict(metadata)
        updated_metadata["reflection_count"] = reflection_count + 1

        return {
            "next_agent": last_agent,
            "reflection_feedback": feedback,
            "metadata": updated_metadata,
        }

    async def _evaluate_quality(
        self, message: Dict[str, Any], state: AgentState
    ) -> Dict[str, Any] | None:
        """Evaluate message quality using EvaluateResponseQualityTool"""
        registry = get_tool_registry()
        eval_tool = registry.get("evaluate_response_quality")

        if not eval_tool:
            logger.warning("EvaluateResponseQualityTool not available")
            return None

        try:
            # Define evaluation criteria
            criteria = [
                "tone_encouraging",  # Friendly and supportive
                "accuracy_correct",  # Mathematically/factually correct
                "pedagogy_socratic",  # Uses questions to guide learning
                "clarity_understandable",  # Clear for Class 10 students
            ]

            result = await eval_tool.execute(
                response=message.get("content", ""), criteria=criteria
            )

            if result.success:
                return result.data
            else:
                logger.warning(f"Quality evaluation failed: {result.error}")
                return None

        except Exception as exc:
            logger.exception(f"Error evaluating quality: {exc}")
            return None

    def _get_last_assistant_message(self, state: AgentState) -> Dict[str, Any] | None:
        """Get the last assistant message from state"""
        messages = state.get("messages", [])

        for msg in reversed(messages):
            if msg.get("role") == "assistant":
                return msg

        return None
