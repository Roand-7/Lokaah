"""
Error Pattern DNA - Classifies student mistake types

Instead of just "wrong answer," this identifies the EXACT type of error:
- Sign error (changed + to -)
- Formula swap (used wrong formula)
- Arithmetic slip (calculation mistake)
- Concept gap (fundamental misunderstanding)
- Incomplete answer (correct approach but stopped early)
- Unit mismatch (forgot units or wrong conversion)
- Misread question (solved a different problem)

Tracks per-student error patterns to provide targeted interventions.
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timezone
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class ErrorClassification:
    """Classification result for a student's error"""
    error_type: str
    confidence: float
    explanation: str
    intervention: str


class ErrorDNA:
    """
    Analyzes student errors and tracks error patterns over time.

    Builds a "DNA" of recurring mistake types for each student.
    """

    ERROR_TYPES = {
        "sign_error": {
            "description": "Changed + to - or vice versa",
            "keywords": ["sign", "negative", "positive", "minus", "plus"],
            "intervention": "Slow down when dealing with signs. Circle every + and - before solving."
        },
        "formula_swap": {
            "description": "Used wrong formula (e.g., distance formula instead of section formula)",
            "keywords": ["formula", "equation", "wrong approach"],
            "intervention": "Write down which formula you're using and why before starting."
        },
        "arithmetic_slip": {
            "description": "Calculation mistake in basic operations",
            "keywords": ["multiply", "divide", "add", "subtract", "calculation", "arithmetic"],
            "intervention": "Double-check calculations. Use a calculator for verification."
        },
        "concept_gap": {
            "description": "Fundamental misunderstanding of the concept",
            "keywords": ["concept", "misunderstanding", "confusion", "don't understand"],
            "intervention": "Let's revisit the concept from scratch with examples."
        },
        "incomplete_answer": {
            "description": "Correct approach but stopped before final answer",
            "keywords": ["incomplete", "partial", "not finished", "stopped"],
            "intervention": "Always verify: Did I answer what the question asked?"
        },
        "unit_mismatch": {
            "description": "Forgot to convert units or add units",
            "keywords": ["unit", "meter", "centimeter", "conversion", "dimension"],
            "intervention": "Always write units next to numbers. Check unit consistency."
        },
        "misread_question": {
            "description": "Solved a different problem than what was asked",
            "keywords": ["misread", "wrong question", "asked for", "question says"],
            "intervention": "Underline what the question is asking before solving."
        },
    }

    def __init__(self, gemini_client=None):
        """
        Initialize error analyzer.

        Args:
            gemini_client: Optional Gemini client for AI-powered classification
        """
        self.gemini = gemini_client
        self._error_history: Dict[str, List[str]] = defaultdict(list)

    async def classify_error(
        self,
        question: str,
        correct_answer: str,
        student_answer: str,
        correct_steps: Optional[List[str]] = None,
        student_steps: Optional[List[str]] = None,
    ) -> ErrorClassification:
        """
        Classify the type of error a student made.

        Args:
            question: The question text
            correct_answer: The correct answer
            student_answer: Student's incorrect answer
            correct_steps: Optional correct solution steps
            student_steps: Optional student's solution steps

        Returns:
            ErrorClassification with type, confidence, explanation, and intervention
        """
        # Use Gemini AI for intelligent classification if available
        if self.gemini:
            return await self._classify_with_ai(
                question, correct_answer, student_answer, correct_steps, student_steps
            )
        else:
            # Fallback: rule-based classification
            return self._classify_with_rules(
                question, correct_answer, student_answer, correct_steps, student_steps
            )

    async def _classify_with_ai(
        self,
        question: str,
        correct_answer: str,
        student_answer: str,
        correct_steps: Optional[List[str]],
        student_steps: Optional[List[str]],
    ) -> ErrorClassification:
        """Use Gemini to classify error type"""
        prompt = f"""Analyze this student's math error:

**Question:** {question}

**Correct Answer:** {correct_answer}
**Student's Answer:** {student_answer}

{f"**Correct Steps:**\n" + chr(10).join(f"{i+1}. {s}" for i, s in enumerate(correct_steps)) if correct_steps else ""}
{f"**Student's Steps:**\n" + chr(10).join(f"{i+1}. {s}" for i, s in enumerate(student_steps)) if student_steps else ""}

**Error Types:**
1. sign_error - Changed + to - or vice versa
2. formula_swap - Used wrong formula
3. arithmetic_slip - Calculation mistake
4. concept_gap - Fundamental misunderstanding
5. incomplete_answer - Correct approach but stopped early
6. unit_mismatch - Forgot units or wrong conversion
7. misread_question - Solved a different problem

**Task:** Classify the error type and explain what went wrong.

**Output Format (JSON):**
{{
    "error_type": "one of the 7 types above",
    "confidence": 0.0-1.0,
    "explanation": "brief explanation of what student did wrong",
    "root_cause": "why this mistake happened"
}}
"""

        try:
            response = self.gemini.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )

            # Parse response (simplified - assumes JSON response)
            import json
            import re

            text = response.text if hasattr(response, 'text') else str(response)
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                error_type = result.get("error_type", "concept_gap")
                confidence = float(result.get("confidence", 0.7))
                explanation = result.get("explanation", "Error in solving the problem")

                intervention = self.ERROR_TYPES.get(error_type, {}).get(
                    "intervention",
                    "Let's work through this step-by-step"
                )

                return ErrorClassification(
                    error_type=error_type,
                    confidence=confidence,
                    explanation=explanation,
                    intervention=intervention
                )

        except Exception as e:
            logger.warning(f"AI classification failed: {e}, using fallback")

        # Fallback to rules
        return self._classify_with_rules(
            question, correct_answer, student_answer, correct_steps, student_steps
        )

    def _classify_with_rules(
        self,
        question: str,
        correct_answer: str,
        student_answer: str,
        correct_steps: Optional[List[str]],
        student_steps: Optional[List[str]],
    ) -> ErrorClassification:
        """Rule-based error classification (fallback)"""
        # Simple heuristics
        combined_text = f"{question} {student_answer}"
        if student_steps:
            combined_text += " " + " ".join(student_steps)

        combined_lower = combined_text.lower()

        # Check for keywords
        scores = {}
        for error_type, info in self.ERROR_TYPES.items():
            score = sum(1 for kw in info["keywords"] if kw in combined_lower)
            scores[error_type] = score

        # Get highest scoring error type
        if max(scores.values()) > 0:
            error_type = max(scores, key=scores.get)
            confidence = min(0.9, scores[error_type] * 0.2 + 0.5)
        else:
            error_type = "concept_gap"
            confidence = 0.6

        return ErrorClassification(
            error_type=error_type,
            confidence=confidence,
            explanation=f"Detected {error_type.replace('_', ' ')}: {self.ERROR_TYPES[error_type]['description']}",
            intervention=self.ERROR_TYPES[error_type]['intervention']
        )

    def track_error(self, session_id: str, error_type: str) -> None:
        """Track error in student's error history"""
        self._error_history[session_id].append(error_type)

    def get_error_dna(self, session_id: str) -> Dict[str, int]:
        """Get student's error pattern distribution"""
        errors = self._error_history.get(session_id, [])
        if not errors:
            return {}

        dna = defaultdict(int)
        for error in errors:
            dna[error] += 1

        return dict(dna)

    def get_primary_weakness(self, session_id: str) -> Optional[str]:
        """Identify student's most common error type"""
        dna = self.get_error_dna(session_id)
        if not dna:
            return None

        return max(dna, key=dna.get)


# Global singleton
_analyzer: Optional[ErrorDNA] = None


def get_error_analyzer(gemini_client=None) -> ErrorDNA:
    """Get global error analyzer instance"""
    global _analyzer
    if _analyzer is None:
        _analyzer = ErrorDNA(gemini_client=gemini_client)
    return _analyzer
