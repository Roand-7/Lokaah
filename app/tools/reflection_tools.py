"""Tools for Reflection node (quality control)"""

from __future__ import annotations

import json
import logging
import re
from typing import Any, Dict, List

from app.tools.base import BaseTool, ToolResult

logger = logging.getLogger(__name__)


class EvaluateResponseQualityTool(BaseTool):
    """Evaluate response quality across multiple criteria"""

    name = "evaluate_response_quality"
    description = "Evaluate the quality of an AI response across pedagogical and communication criteria"

    def __init__(self, gemini_client):
        self.client = gemini_client

    async def execute(
        self,
        response: str,
        criteria: List[str]
    ) -> ToolResult:
        """
        Evaluate response

        Args:
            response: The response text to evaluate
            criteria: List of criteria to evaluate (e.g., ["tone_encouraging", "accuracy_correct"])
        """
        if not self.client:
            # Fallback: simple heuristic evaluation
            return self._fallback_evaluation(response, criteria)

        try:
            prompt = f"""
You are a quality evaluator for educational AI responses.
Evaluate this response on the following criteria (score each 0.0-1.0):

CRITERIA:
{chr(10).join(f"- {c}" for c in criteria)}

RESPONSE TO EVALUATE:
{response}

Return ONLY valid JSON (no markdown, no explanation):
{{
  "scores": {{"criterion1": 0.8, "criterion2": 0.9, ...}},
  "overall": 0.85,
  "feedback": "Brief constructive feedback if score < 0.7"
}}
"""

            response_obj = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )

            raw = response_obj.text if hasattr(response_obj, 'text') else ""

            # Parse JSON from response
            parsed = self._parse_json(raw)

            if not parsed:
                return self._fallback_evaluation(response, criteria)

            return ToolResult(
                success=True,
                data=parsed
            )

        except Exception as exc:
            logger.warning(f"Evaluation failed, using fallback: {exc}")
            return self._fallback_evaluation(response, criteria)

    def _fallback_evaluation(self, response: str, criteria: List[str]) -> ToolResult:
        """Simple heuristic evaluation if LLM fails"""
        scores = {}
        response_lower = response.lower()

        for criterion in criteria:
            if "encouraging" in criterion or "tone" in criterion:
                # Check for positive words
                positive_words = ["great", "good", "excellent", "perfect", "well done", "nice"]
                score = 0.7 if any(word in response_lower for word in positive_words) else 0.5
            elif "accuracy" in criterion or "correct" in criterion:
                # Assume accurate unless obvious errors
                error_indicators = ["error", "wrong", "incorrect", "mistake"]
                score = 0.5 if any(word in response_lower for word in error_indicators) else 0.8
            elif "socratic" in criterion or "pedagogy" in criterion:
                # Check for questions
                score = 0.8 if "?" in response else 0.6
            else:
                score = 0.7  # Default

            scores[criterion] = score

        overall = sum(scores.values()) / len(scores) if scores else 0.7

        return ToolResult(
            success=True,
            data={
                "scores": scores,
                "overall": overall,
                "feedback": "Fallback evaluation used - consider improving specific criteria" if overall < 0.7 else ""
            },
            metadata={"fallback": True}
        )

    def _parse_json(self, raw: str) -> Dict[str, Any]:
        """Extract JSON from response"""
        # Try direct parse
        try:
            return json.loads(raw.strip())
        except json.JSONDecodeError:
            pass

        # Try extracting JSON from markdown code block
        match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', raw, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass

        # Try finding first JSON object
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass

        return {}


class CheckMathAccuracyTool(BaseTool):
    """Verify mathematical accuracy of solutions"""

    name = "check_math_accuracy"
    description = "Verify that mathematical calculations and final answers are correct"

    async def execute(
        self,
        answer: str,
        correct_answer: str,
        tolerance: float = 0.01
    ) -> ToolResult:
        """
        Check math accuracy

        Args:
            answer: Student's answer or solution step
            correct_answer: The correct answer to compare against
            tolerance: Acceptable error margin for numerical answers
        """
        try:
            # Try numeric comparison
            answer_clean = self._extract_number(answer)
            correct_clean = self._extract_number(correct_answer)

            if answer_clean is not None and correct_clean is not None:
                # Numeric comparison
                error = abs(answer_clean - correct_clean)
                is_correct = error <= tolerance

                return ToolResult(
                    success=True,
                    data={
                        "is_correct": is_correct,
                        "answer_value": answer_clean,
                        "correct_value": correct_clean,
                        "error": error,
                        "tolerance": tolerance,
                        "method": "numeric"
                    }
                )

            # Fall back to string comparison
            answer_normalized = answer.strip().lower().replace(" ", "")
            correct_normalized = correct_answer.strip().lower().replace(" ", "")

            is_correct = answer_normalized == correct_normalized

            # Check for common equivalent forms
            if not is_correct:
                is_correct = self._check_equivalents(answer_normalized, correct_normalized)

            return ToolResult(
                success=True,
                data={
                    "is_correct": is_correct,
                    "method": "string_match",
                    "answer": answer.strip(),
                    "correct": correct_answer.strip()
                }
            )

        except Exception as exc:
            return ToolResult(
                success=False,
                data=None,
                error=f"Failed to check accuracy: {str(exc)}"
            )

    def _extract_number(self, text: str) -> float | None:
        """Extract numeric value from text"""
        # Remove common math symbols and text
        cleaned = re.sub(r'[a-zA-Z°]', ' ', text)
        cleaned = re.sub(r'[^\d.\-+/]', ' ', cleaned)

        # Find numbers
        numbers = re.findall(r'-?\d+\.?\d*', cleaned)

        if numbers:
            try:
                # Return first number found
                return float(numbers[0])
            except ValueError:
                pass

        return None

    def _check_equivalents(self, answer: str, correct: str) -> bool:
        """Check for mathematically equivalent forms"""
        # Common equivalents
        equivalents = [
            # Fractions
            ("1/2", "0.5"),
            ("1/4", "0.25"),
            ("3/4", "0.75"),
            # Roots
            ("√2", "sqrt(2)"),
            ("√3", "sqrt(3)"),
            # Pi
            ("π", "pi"),
            ("3.14", "pi"),
        ]

        for form1, form2 in equivalents:
            if (form1 in answer and form2 in correct) or (form2 in answer and form1 in correct):
                return True

        return False
