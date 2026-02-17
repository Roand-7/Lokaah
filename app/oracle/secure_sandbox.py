"""
Secure sandbox for evaluating small math expressions and solver snippets.

This module intentionally supports a narrow DSL for arithmetic / logic.
It blocks imports, attribute traversal, and arbitrary Python execution.
"""

from __future__ import annotations

import ast
import logging
import math
import random
import re
from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class SandboxError(ValueError):
    """Raised when untrusted code violates sandbox constraints."""


@dataclass(frozen=True)
class SandboxLimits:
    max_expression_length: int = 300
    max_statements: int = 20


class SafeMathSandbox:
    """AST-restricted evaluator for pattern formulas and solver snippets."""

    _allowed_functions = {
        "abs": abs,
        "round": round,
        "min": min,
        "max": max,
        "int": int,
        "float": float,
        "pow": pow,
        "sum": sum,
        "len": len,
    }

    _allowed_math_functions = {
        "sqrt": math.sqrt,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "asin": math.asin,
        "acos": math.acos,
        "atan": math.atan,
        "degrees": math.degrees,
        "radians": math.radians,
        "pi": math.pi,
        "e": math.e,
        "gcd": math.gcd,
        "ceil": math.ceil,
        "floor": math.floor,
    }

    _allowed_random_functions = {
        "randint": random.randint,
        "uniform": random.uniform,
        "choice": random.choice,
    }

    _allowed_nodes = (
        ast.Expression,
        ast.BinOp,
        ast.UnaryOp,
        ast.BoolOp,
        ast.Compare,
        ast.IfExp,
        ast.Name,
        ast.Load,
        ast.Constant,
        ast.Call,
        ast.Attribute,
        ast.Tuple,
        ast.List,
        ast.Dict,
        ast.Subscript,
        ast.Slice,
        ast.Index,
        ast.And,
        ast.Or,
        ast.Not,
        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.Div,
        ast.FloorDiv,
        ast.Mod,
        ast.Pow,
        ast.USub,
        ast.UAdd,
        ast.Eq,
        ast.NotEq,
        ast.Lt,
        ast.LtE,
        ast.Gt,
        ast.GtE,
        ast.In,
        ast.NotIn,
        ast.Is,
        ast.IsNot,
    )

    _assignment_pattern = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.+)$")

    def __init__(self, limits: Optional[SandboxLimits] = None) -> None:
        self.limits = limits or SandboxLimits()

    def evaluate_expression(
        self,
        expression: str,
        context: Optional[Dict[str, Any]] = None,
        allow_random: bool = False,
    ) -> Any:
        expr = (expression or "").strip()
        if not expr:
            raise SandboxError("Empty expression")
        if len(expr) > self.limits.max_expression_length:
            raise SandboxError("Expression too long")

        context = dict(context or {})
        tree = ast.parse(expr, mode="eval")
        self._validate_tree(tree, context=context, allow_random=allow_random)

        safe_globals = self._build_globals(allow_random=allow_random)
        safe_locals = dict(context)
        return eval(compile(tree, "<sandbox>", "eval"), safe_globals, safe_locals)

    def evaluate_boolean(
        self, expression: str, context: Optional[Dict[str, Any]] = None
    ) -> bool:
        return bool(self.evaluate_expression(expression, context=context))

    def execute_solver(
        self, solver_code: str, context: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Execute limited solver snippets:
        - assignment statements: `x = a + b`
        - expression statements
        - optional `return ...` as final output
        Statements are separated by `;`.
        """
        code = (solver_code or "").strip()
        if not code:
            raise SandboxError("Empty solver code")

        statements = [segment.strip() for segment in code.split(";") if segment.strip()]
        if len(statements) > self.limits.max_statements:
            raise SandboxError("Too many statements in solver code")

        scope = dict(context or {})
        last_value: Any = None
        logger.info(
            "oracle_sandbox_run start code=%s context_keys=%s",
            self._truncate_for_log(code),
            ",".join(sorted(scope.keys())[:20]),
        )

        try:
            for statement in statements:
                if statement.startswith("return "):
                    result = self.evaluate_expression(statement[7:], context=scope)
                    logger.info(
                        "oracle_sandbox_run success code=%s result=%r",
                        self._truncate_for_log(code),
                        result,
                    )
                    return result

                assignment = self._assignment_pattern.match(statement)
                if assignment:
                    var_name = assignment.group(1)
                    rhs = assignment.group(2)
                    scope[var_name] = self.evaluate_expression(rhs, context=scope)
                    last_value = scope[var_name]
                    continue

                last_value = self.evaluate_expression(statement, context=scope)
        except Exception as exc:
            logger.warning(
                "oracle_sandbox_run failed code=%s error=%s",
                self._truncate_for_log(code),
                exc,
            )
            raise

        logger.info(
            "oracle_sandbox_run success code=%s result=%r",
            self._truncate_for_log(code),
            last_value,
        )
        return last_value

    def _build_globals(self, allow_random: bool) -> Dict[str, Any]:
        random_proxy = SimpleNamespace(**self._allowed_random_functions)
        safe_globals = {
            "__builtins__": {},
            **self._allowed_functions,
            **self._allowed_math_functions,
            "math": SimpleNamespace(**self._allowed_math_functions),
            "True": True,
            "False": False,
            "None": None,
        }
        if allow_random:
            safe_globals["random"] = random_proxy
        return safe_globals

    def _validate_tree(
        self, tree: ast.AST, context: Dict[str, Any], allow_random: bool
    ) -> None:
        allowed_names = set(context.keys()) | set(self._allowed_functions.keys())
        allowed_names |= set(self._allowed_math_functions.keys()) | {"math", "True", "False", "None"}
        if allow_random:
            allowed_names.add("random")

        for node in ast.walk(tree):
            if not isinstance(node, self._allowed_nodes):
                raise SandboxError(f"Disallowed syntax: {type(node).__name__}")

            if isinstance(node, ast.Name):
                if node.id not in allowed_names:
                    raise SandboxError(f"Unknown identifier: {node.id}")

            if isinstance(node, ast.Call):
                self._validate_call_node(node, allow_random=allow_random)

    def _validate_call_node(self, node: ast.Call, allow_random: bool) -> None:
        if isinstance(node.func, ast.Name):
            if (
                node.func.id not in self._allowed_functions
                and node.func.id not in self._allowed_math_functions
            ):
                raise SandboxError(f"Disallowed function call: {node.func.id}")
            return

        if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
            if node.func.value.id == "math":
                if node.func.attr not in self._allowed_math_functions:
                    raise SandboxError(f"Disallowed math function: {node.func.attr}")
                return
            if node.func.value.id == "random" and allow_random:
                if node.func.attr not in self._allowed_random_functions:
                    raise SandboxError(f"Disallowed random function: {node.func.attr}")
                return

        raise SandboxError("Disallowed call target")

    @staticmethod
    def _truncate_for_log(value: str, max_length: int = 180) -> str:
        if len(value) <= max_length:
            return value
        return value[: max_length - 3] + "..."
