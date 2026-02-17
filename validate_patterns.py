"""
Quality control for generated pattern files.

Checks:
1) Required schema fields exist.
2) Variable expressions evaluate with restricted sandbox.
3) solver_code executes successfully for N randomized trials.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

from app.oracle.secure_sandbox import SafeMathSandbox, SandboxError


REQUIRED_KEYS = {
    "pattern_id",
    "chapter",
    "topic",
    "difficulty",
    "template",
    "variables",
    "solver_code",
}


class PatternValidator:
    def __init__(self, iterations: int) -> None:
        self.iterations = iterations
        self.sandbox = SafeMathSandbox()

    def validate_pattern(self, pattern: Dict[str, Any]) -> Tuple[bool, str]:
        missing = REQUIRED_KEYS - set(pattern.keys())
        if missing:
            return False, f"Missing keys: {sorted(missing)}"

        if not isinstance(pattern["variables"], dict):
            return False, "variables must be an object"
        if not isinstance(pattern["solver_code"], str) or not pattern["solver_code"].strip():
            return False, "solver_code must be a non-empty string"

        for _ in range(self.iterations):
            try:
                values = self._evaluate_variables(pattern["variables"])
                _ = self.sandbox.execute_solver(pattern["solver_code"], context=values)
            except (SandboxError, ValueError, KeyError, TypeError) as exc:
                return False, f"Execution failed: {exc}"

        return True, "ok"

    def _evaluate_variables(self, variable_expressions: Dict[str, str]) -> Dict[str, Any]:
        values: Dict[str, Any] = {}
        pending = dict(variable_expressions)

        for _ in range(max(1, len(pending))):
            progress = False
            for name in list(pending.keys()):
                expression = pending[name]
                if not isinstance(expression, str):
                    raise ValueError(f"Variable '{name}' expression must be string")

                rendered = expression
                if "{" in expression and "}" in expression:
                    try:
                        rendered = expression.format(**values)
                    except KeyError:
                        continue

                values[name] = self.sandbox.evaluate_expression(
                    rendered,
                    context=values,
                    allow_random=True,
                )
                del pending[name]
                progress = True

            if not pending:
                break
            if not progress:
                unresolved = ", ".join(sorted(pending.keys()))
                raise ValueError(f"Unresolved variable expressions: {unresolved}")

        return values


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate generated pattern JSON files")
    parser.add_argument(
        "--dir",
        default="app/oracle/pattern_factory/generated",
        help="Directory containing generated pattern files",
    )
    parser.add_argument("--iterations", type=int, default=100, help="Runs per pattern")
    args = parser.parse_args()

    patterns_dir = Path(args.dir)
    if not patterns_dir.exists():
        print(f"Directory not found: {patterns_dir}")
        return 1

    files = sorted(p for p in patterns_dir.glob("patterns_*.json") if p.is_file())
    if not files:
        print(f"No pattern files found in {patterns_dir}")
        return 1

    validator = PatternValidator(iterations=args.iterations)

    total_patterns = 0
    failures: List[str] = []
    for file_path in files:
        with file_path.open("r", encoding="utf-8") as file_obj:
            data = json.load(file_obj)
        if not isinstance(data, list):
            failures.append(f"{file_path}: file must contain a JSON array")
            continue

        for index, pattern in enumerate(data, start=1):
            total_patterns += 1
            ok, message = validator.validate_pattern(pattern)
            if not ok:
                pattern_id = pattern.get("pattern_id", f"index_{index}")
                failures.append(f"{file_path}:{index} [{pattern_id}] {message}")

    passed = total_patterns - len(failures)
    print(f"Validated patterns: {total_patterns}")
    print(f"Passed: {passed}")
    print(f"Failed: {len(failures)}")

    if failures:
        print("\nSample failures:")
        for entry in failures[:20]:
            print(f"- {entry}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
