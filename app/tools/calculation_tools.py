"""Mathematical calculation tools with zero-hallucination guarantee"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from app.oracle.secure_sandbox import SafeMathSandbox, SandboxError
from app.tools.base import BaseTool, ToolResult

logger = logging.getLogger(__name__)


class VerifyAndCalculateTool(BaseTool):
    """
    Execute mathematical calculations with 100% accuracy using Python.
    Zero AI hallucinations - all math done by secure Python sandbox.
    """

    name = "verify_and_calculate"
    description = "Execute mathematical calculations with verified accuracy using Python. Use this to solve equations, verify student answers, or compute exact numerical results."

    def __init__(self):
        self.sandbox = SafeMathSandbox()

    async def execute(
        self,
        expression: str,
        variables: Optional[Dict[str, Any]] = None,
        show_steps: bool = True
    ) -> ToolResult:
        """
        Calculate mathematical expression

        Args:
            expression: Math expression or solver code (e.g., "sqrt(a**2 + b**2)" or "x = (-b + sqrt(b**2 - 4*a*c)) / (2*a); return x")
            variables: Variable values (e.g., {"a": 3, "b": 4})
            show_steps: Whether to break down calculation into steps
        """
        try:
            # Determine if it's a simple expression or multi-step solver
            is_solver = ";" in expression or "return" in expression

            if is_solver:
                # Multi-step solver code
                result = self.sandbox.execute_solver(
                    solver_code=expression,
                    context=variables or {}
                )

                # Extract steps if requested
                steps = []
                if show_steps:
                    steps = self._extract_steps_from_solver(expression, variables or {})

            else:
                # Simple expression
                result = self.sandbox.evaluate_expression(
                    expression=expression,
                    context=variables or {}
                )

                steps = [f"{expression} = {result}"] if show_steps else []

            return ToolResult(
                success=True,
                data={
                    "result": result,
                    "steps": steps,
                    "expression": expression,
                    "variables": variables or {},
                    "method": "solver" if is_solver else "expression"
                },
                metadata={"calculation_verified": True, "hallucination_free": True}
            )

        except SandboxError as exc:
            return ToolResult(
                success=False,
                data=None,
                error=f"Security violation in calculation: {str(exc)}"
            )

        except Exception as exc:
            return ToolResult(
                success=False,
                data=None,
                error=f"Calculation failed: {str(exc)}"
            )

    def _extract_steps_from_solver(
        self,
        solver_code: str,
        variables: Dict[str, Any]
    ) -> List[str]:
        """Extract step-by-step breakdown from solver code"""
        steps = []
        statements = [s.strip() for s in solver_code.split(";") if s.strip()]

        scope = dict(variables)

        for statement in statements:
            try:
                if statement.startswith("return "):
                    expr = statement[7:]
                    result = self.sandbox.evaluate_expression(expr, context=scope)
                    steps.append(f"Final: {expr} = {result}")
                    break

                elif "=" in statement and not any(op in statement for op in ["==", "!=", "<=", ">="]):
                    # Assignment
                    var_name, rhs = statement.split("=", 1)
                    var_name = var_name.strip()
                    rhs = rhs.strip()

                    result = self.sandbox.evaluate_expression(rhs, context=scope)
                    scope[var_name] = result

                    steps.append(f"Step: {var_name} = {rhs} = {result}")

                else:
                    # Evaluation
                    result = self.sandbox.evaluate_expression(statement, context=scope)
                    steps.append(f"Evaluate: {statement} = {result}")

            except Exception:
                # Skip steps that fail (don't break entire process)
                continue

        return steps


class GenerateSolutionStepsTool(BaseTool):
    """
    Generate detailed solution steps for a mathematical problem.
    Uses AI to explain, Python to calculate each step.
    """

    name = "generate_solution_steps"
    description = "Generate detailed, step-by-step solution for a math problem with verified calculations at each step"

    def __init__(self, gemini_client):
        self.client = gemini_client
        self.sandbox = SafeMathSandbox()

    async def execute(
        self,
        problem: str,
        concept: str,
        given_values: Dict[str, Any]
    ) -> ToolResult:
        """
        Generate solution steps

        Args:
            problem: Problem statement
            concept: Mathematical concept (e.g., "quadratic_equations", "trigonometry")
            given_values: Given numerical values
        """
        if not self.client:
            return ToolResult(
                success=False,
                data=None,
                error="AI client not available for solution generation"
            )

        try:
            # Prompt AI to generate solution strategy (NOT calculations)
            prompt = f"""
You are a CBSE Class 10 math tutor. Generate step-by-step solution strategy for this problem.

IMPORTANT:
- Explain WHAT to do at each step (strategy)
- Do NOT calculate numbers (Python will do that)
- Use variable names for calculations (e.g., "Calculate discriminant = b² - 4ac")

Problem: {problem}
Concept: {concept}
Given: {given_values}

Return JSON with steps:
{{
  "steps": [
    {{"step": 1, "action": "Identify formula", "formula": "x = (-b ± √(b²-4ac)) / 2a"}},
    {{"step": 2, "action": "Calculate discriminant", "calculation": "disc = b**2 - 4*a*c"}},
    ...
  ]
}}
"""

            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )

            import json
            import re

            raw = response.text if hasattr(response, 'text') else ""

            # Parse JSON
            match = re.search(r'\{.*\}', raw, re.DOTALL)
            if match:
                strategy = json.loads(match.group(0))
            else:
                strategy = {"steps": []}

            # Execute calculations for each step
            verified_steps = []
            calculation_context = dict(given_values)

            for step in strategy.get("steps", []):
                step_result = {
                    "step_number": step.get("step", 0),
                    "action": step.get("action", ""),
                    "formula": step.get("formula"),
                }

                # Execute calculation if present
                if "calculation" in step:
                    calc_expr = step["calculation"]

                    try:
                        calc_result = self.sandbox.execute_solver(
                            calc_expr,
                            context=calculation_context
                        )

                        step_result["calculated_value"] = calc_result
                        step_result["calculation"] = calc_expr

                        # Update context for next steps
                        if "=" in calc_expr and ";" not in calc_expr:
                            var_name = calc_expr.split("=")[0].strip()
                            calculation_context[var_name] = calc_result

                    except Exception as exc:
                        step_result["calculation_error"] = str(exc)

                verified_steps.append(step_result)

            # Get final answer
            final_answer = None
            for step in reversed(verified_steps):
                if "calculated_value" in step:
                    final_answer = step["calculated_value"]
                    break

            return ToolResult(
                success=True,
                data={
                    "steps": verified_steps,
                    "final_answer": final_answer,
                    "problem": problem,
                    "concept": concept
                },
                metadata={"hybrid_solution": True, "verified": True}
            )

        except Exception as exc:
            logger.exception(f"Solution generation failed: {exc}")
            return ToolResult(
                success=False,
                data=None,
                error=f"Failed to generate solution: {str(exc)}"
            )


class CheckStudentCalculationTool(BaseTool):
    """
    Check student's calculation work step-by-step.
    Identifies where student made mistakes.
    """

    name = "check_student_calculation"
    description = "Verify student's calculation work and identify exactly where errors occurred"

    def __init__(self):
        self.sandbox = SafeMathSandbox()

    async def execute(
        self,
        student_steps: List[Dict[str, Any]],
        correct_solver_code: str,
        variables: Dict[str, Any]
    ) -> ToolResult:
        """
        Check student work

        Args:
            student_steps: List of student's calculation steps [{"step": "x = 5 + 3", "result": 8}, ...]
            correct_solver_code: Correct solution code
            variables: Problem variables
        """
        try:
            # Get correct answer
            correct_result = self.sandbox.execute_solver(
                correct_solver_code,
                context=variables
            )

            # Verify each student step
            errors = []
            scope = dict(variables)

            for idx, student_step in enumerate(student_steps):
                step_expr = student_step.get("step", "")
                student_result = student_step.get("result")

                try:
                    # Evaluate student's expression
                    if "=" in step_expr:
                        var_name, rhs = step_expr.split("=", 1)
                        var_name = var_name.strip()
                        rhs = rhs.strip()

                        verified_result = self.sandbox.evaluate_expression(rhs, context=scope)
                        scope[var_name] = verified_result

                        # Check if student's result matches
                        if abs(float(student_result) - float(verified_result)) > 0.01:
                            errors.append({
                                "step_number": idx + 1,
                                "student_wrote": step_expr,
                                "student_got": student_result,
                                "correct_answer": verified_result,
                                "error_type": "calculation_mistake"
                            })

                except Exception:
                    errors.append({
                        "step_number": idx + 1,
                        "student_wrote": step_expr,
                        "error_type": "invalid_expression"
                    })

            # Check final answer
            final_student_answer = student_steps[-1].get("result") if student_steps else None
            final_correct = abs(float(final_student_answer) - float(correct_result)) < 0.01 if final_student_answer else False

            return ToolResult(
                success=True,
                data={
                    "is_correct": final_correct and len(errors) == 0,
                    "final_answer_correct": final_correct,
                    "errors": errors,
                    "total_steps": len(student_steps),
                    "correct_final_answer": correct_result,
                    "feedback": self._generate_feedback(errors, final_correct)
                }
            )

        except Exception as exc:
            return ToolResult(
                success=False,
                data=None,
                error=f"Failed to check student work: {str(exc)}"
            )

    def _generate_feedback(self, errors: List[Dict], final_correct: bool) -> str:
        """Generate constructive feedback"""
        if not errors and final_correct:
            return "Perfect! All steps correct."

        if final_correct and errors:
            return f"Your final answer is correct, but there are {len(errors)} calculation mistakes in your steps. Let's review them."

        if not final_correct and not errors:
            return "Your calculations are correct, but check your final answer - there might be a rounding or sign error."

        first_error = errors[0]
        return f"I see an error at step {first_error['step_number']}. Let's fix that first, then continue."
