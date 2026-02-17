"""Tool system for agentic LOKAAH"""

from __future__ import annotations

import logging
from typing import Any, Dict, List

from app.tools.base import BaseTool, ToolResult
from app.tools.veda_tools import (
    CreateDiagramTool,
    FetchExamQuestionTool,
    GeneratePracticeQuestionTool,
    GetStudentMasteryTool,
)
from app.tools.oracle_tools import (
    AdjustDifficultyTool,
    TrackStudentAttemptTool,
)
from app.tools.pulse_tools import (
    EscalateToCounselorTool,
    SendBreathingExerciseTool,
    SuggestBreakTool,
)
from app.tools.atlas_tools import (
    CreateStudyPlanTool,
    FetchCBSEExamDatesTool,
    PrioritizeTopicsTool,
)
from app.tools.supervisor_tools import (
    EscalateToHumanTool,
    FetchUserProfileTool,
    LogAnalyticsTool,
)
from app.tools.reflection_tools import (
    CheckMathAccuracyTool,
    EvaluateResponseQualityTool,
)
from app.tools.calculation_tools import (
    CheckStudentCalculationTool,
    GenerateSolutionStepsTool,
    VerifyAndCalculateTool,
)


logger = logging.getLogger(__name__)


class ToolRegistry:
    """Central registry for all agent tools"""

    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        self._initialized = False

    def register(self, tool: BaseTool):
        """Register a tool"""
        if not tool.name:
            raise ValueError(f"Tool {tool.__class__.__name__} must have a name")

        if tool.name in self._tools:
            logger.warning(f"Tool '{tool.name}' already registered, overwriting")

        self._tools[tool.name] = tool
        logger.debug(f"Registered tool: {tool.name}")

    def get(self, name: str) -> BaseTool | None:
        """Get tool by name"""
        return self._tools.get(name)

    def get_tools_for_agent(self, agent_name: str) -> List[BaseTool]:
        """Get tools assigned to a specific agent"""
        agent_tool_map = {
            "veda": [
                "generate_practice_question",
                "fetch_exam_question",
                "create_diagram",
                "get_student_mastery",
                "verify_and_calculate",  # NEW: VEDA can verify math
                "generate_solution_steps",  # NEW: VEDA generates verified solutions
                "check_student_calculation"  # NEW: VEDA checks student work
            ],
            "oracle": [
                "track_student_attempt",
                "adjust_difficulty",
                "verify_and_calculate"  # NEW: ORACLE can verify answers
            ],
            "pulse": [
                "send_breathing_exercise",
                "suggest_break",
                "escalate_to_counselor"
            ],
            "atlas": [
                "create_study_plan",
                "fetch_cbse_exam_dates",
                "prioritize_topics"
            ],
            "supervisor": [
                "fetch_user_profile",
                "log_analytics",
                "escalate_to_human"
            ],
            "reflection": [
                "evaluate_response_quality",
                "check_math_accuracy",
                "verify_and_calculate"  # NEW: Reflection verifies calculations
            ]
        }

        tool_names = agent_tool_map.get(agent_name.lower(), [])
        tools = []

        for name in tool_names:
            tool = self._tools.get(name)
            if tool:
                tools.append(tool)
            else:
                logger.warning(f"Tool '{name}' assigned to {agent_name} but not registered")

        return tools

    def to_gemini_tools(self, agent_name: str) -> List[Dict[str, Any]]:
        """Convert agent's tools to Gemini function calling format"""
        tools = self.get_tools_for_agent(agent_name)
        return [tool.to_gemini_tool() for tool in tools]

    def list_all_tools(self) -> List[str]:
        """List all registered tool names"""
        return list(self._tools.keys())

    @property
    def is_initialized(self) -> bool:
        """Check if registry has been initialized"""
        return self._initialized

    def mark_initialized(self):
        """Mark registry as initialized"""
        self._initialized = True


# Global registry instance
_registry: ToolRegistry | None = None


def get_tool_registry() -> ToolRegistry:
    """Get the global tool registry instance"""
    global _registry
    if _registry is None:
        _registry = ToolRegistry()
    return _registry


def initialize_tools(
    supabase_client: Any,
    gemini_client: Any,
    exam_db: Any,
    diagram_gen: Any
) -> ToolRegistry:
    """
    Initialize all tools with their dependencies

    Args:
        supabase_client: Supabase database client
        gemini_client: Gemini AI client
        exam_db: Exam database instance
        diagram_gen: Diagram generator instance

    Returns:
        Initialized ToolRegistry
    """
    registry = get_tool_registry()

    # Skip if already initialized
    if registry.is_initialized:
        logger.info("Tool registry already initialized, skipping")
        return registry

    logger.info("Initializing tool registry...")

    # VEDA tools (4)
    registry.register(GeneratePracticeQuestionTool())
    registry.register(FetchExamQuestionTool(exam_db))
    registry.register(CreateDiagramTool(diagram_gen))
    registry.register(GetStudentMasteryTool(supabase_client))

    # ORACLE tools (2)
    registry.register(TrackStudentAttemptTool(supabase_client))
    registry.register(AdjustDifficultyTool(supabase_client))

    # PULSE tools (3)
    registry.register(SendBreathingExerciseTool())
    registry.register(SuggestBreakTool())
    registry.register(EscalateToCounselorTool(supabase_client))

    # ATLAS tools (3)
    registry.register(CreateStudyPlanTool())
    registry.register(FetchCBSEExamDatesTool())
    registry.register(PrioritizeTopicsTool())

    # Supervisor tools (3)
    registry.register(FetchUserProfileTool(supabase_client))
    registry.register(LogAnalyticsTool(supabase_client))
    registry.register(EscalateToHumanTool(supabase_client))

    # Reflection tools (2)
    registry.register(EvaluateResponseQualityTool(gemini_client))
    registry.register(CheckMathAccuracyTool())

    # Calculation tools (3) - NEW: Zero-hallucination math
    registry.register(VerifyAndCalculateTool())
    registry.register(GenerateSolutionStepsTool(gemini_client))
    registry.register(CheckStudentCalculationTool())

    registry.mark_initialized()

    total_tools = len(registry.list_all_tools())
    logger.info(f"Tool registry initialized with {total_tools} tools")

    # Log tools per agent
    for agent in ["veda", "oracle", "pulse", "atlas", "supervisor", "reflection"]:
        tools = registry.get_tools_for_agent(agent)
        logger.info(f"  {agent.upper()}: {len(tools)} tools")

    return registry


# Export all public classes and functions
__all__ = [
    "BaseTool",
    "ToolResult",
    "ToolRegistry",
    "get_tool_registry",
    "initialize_tools",
    # VEDA tools
    "GeneratePracticeQuestionTool",
    "FetchExamQuestionTool",
    "CreateDiagramTool",
    "GetStudentMasteryTool",
    # ORACLE tools
    "TrackStudentAttemptTool",
    "AdjustDifficultyTool",
    # PULSE tools
    "SendBreathingExerciseTool",
    "SuggestBreakTool",
    "EscalateToCounselorTool",
    # ATLAS tools
    "CreateStudyPlanTool",
    "FetchCBSEExamDatesTool",
    "PrioritizeTopicsTool",
    # Supervisor tools
    "FetchUserProfileTool",
    "LogAnalyticsTool",
    "EscalateToHumanTool",
    # Reflection tools
    "EvaluateResponseQualityTool",
    "CheckMathAccuracyTool",
]
