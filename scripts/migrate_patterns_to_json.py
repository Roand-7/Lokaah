"""
Automated Pattern Migration Script
Converts hardcoded Python generators in oracle_engine.py to JSON templates
"""

import json
import re
import ast
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime


class PatternMigrator:
    """Analyzes Python generator methods and converts to JSON templates"""

    def __init__(self, oracle_file: str, output_dir: str):
        self.oracle_file = Path(oracle_file)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        with open(self.oracle_file, 'r', encoding='utf-8') as f:
            self.source_code = f.read()

    def extract_all_patterns(self) -> List[str]:
        """Extract all _gen_* method names"""
        pattern_regex = r"def (_gen_\w+)\(self, pattern, topic\):"
        matches = re.findall(pattern_regex, self.source_code)

        # Filter out generic/helper methods
        excluded = ['_gen_generic', '_gen_default', '_gen_from_pattern']
        return [m for m in matches if m not in excluded]

    def extract_method_code(self, method_name: str) -> str:
        """Extract full method source code"""
        # Find method start
        start_pattern = rf"def {method_name}\(self, pattern, topic\):"
        start_match = re.search(start_pattern, self.source_code)

        if not start_match:
            return None

        start_pos = start_match.start()

        # Find method end (next def or end of class)
        lines = self.source_code[start_pos:].split('\n')
        method_lines = [lines[0]]  # def line

        for line in lines[1:]:
            # Stop at next method or class end
            if line.strip() and not line.startswith(' ') and not line.startswith('\t'):
                break
            if re.match(r'^\s{4}def ', line):  # Next method (4-space indent)
                break
            method_lines.append(line)

        return '\n'.join(method_lines)

    def analyze_pattern(self, method_code: str, method_name: str) -> Dict[str, Any]:
        """
        Analyze Python code to extract pattern metadata
        Returns JSON template structure
        """
        # Extract pattern_id from return statement
        pattern_id_match = re.search(r'"pattern_id":\s*"(\w+)"', method_code)
        pattern_id = pattern_id_match.group(1) if pattern_id_match else method_name.replace('_gen_', '')

        # Extract topic
        topic_match = re.search(r'# Pattern:\s*(.+)', method_code) or \
                     re.search(r'"""[\s\S]*?Pattern:\s*(.+)', method_code)
        topic = "Unknown"
        if topic_match:
            topic = topic_match.group(1).strip()

        # Extract marks
        marks_match = re.search(r'"marks":\s*(\d+)', method_code) or \
                     re.search(r'marks=(\d+)', method_code)
        marks = int(marks_match.group(1)) if marks_match else 2

        # Extract difficulty
        difficulty_match = re.search(r'"difficulty":\s*(0\.\d+)', method_code) or \
                          re.search(r'difficulty=(0\.\d+)', method_code)
        difficulty = float(difficulty_match.group(1)) if difficulty_match else 0.5

        # Extract question template
        question_match = re.search(r'question_text\s*=\s*\(?\s*f?"([^"]+)"', method_code, re.MULTILINE)
        template_text = question_match.group(1) if question_match else f"Question for {pattern_id}"

        # Convert f-string variables to placeholders
        template_text = self._convert_fstring_to_template(template_text)

        # Extract variables (basic heuristic)
        variables = self._extract_variables(method_code)

        # Extract solution steps
        solution_template = self._extract_solution_steps(method_code)

        # Extract answer template
        answer_match = re.search(r'"final_answer":\s*f?"([^"]+)"', method_code)
        answer_template = answer_match.group(1) if answer_match else "{answer}"
        answer_template = self._convert_fstring_to_template(answer_template)

        # Extract socratic hints
        socratic_hints = self._extract_socratic_hints(method_code)

        return {
            "pattern_id": pattern_id,
            "topic": topic,
            "marks": marks,
            "difficulty": difficulty,
            "template_text": template_text,
            "variables": variables,
            "solution_template": solution_template,
            "answer_template": answer_template,
            "validation_rules": [],
            "socratic_hints": socratic_hints,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

    def _convert_fstring_to_template(self, text: str) -> str:
        """Convert Python f-string to template placeholders"""
        # {a} → {a}  (already correct)
        # {a:.2f} → {a:.2f}  (preserve formatting)
        # Other conversions as needed
        return text

    def _extract_variables(self, code: str) -> Dict[str, Dict]:
        """Extract variable definitions from code"""
        variables = {}

        # Look for random.randint patterns
        randint_matches = re.findall(r'(\w+)\s*=\s*random\.randint\((\d+),\s*(\d+)\)', code)
        for var_name, min_val, max_val in randint_matches:
            if not var_name.startswith('_'):
                variables[var_name] = {
                    "type": "int",
                    "min": int(min_val),
                    "max": int(max_val)
                }

        # Look for random.choice patterns
        choice_matches = re.findall(r'(\w+)\s*=\s*random\.choice\(\[([^\]]+)\]\)', code)
        for var_name, choices_str in choice_matches:
            if not var_name.startswith('_'):
                try:
                    choices = [int(x.strip()) for x in choices_str.split(',')]
                    variables[var_name] = {
                        "type": "choice",
                        "choices": choices
                    }
                except:
                    pass

        # Look for calculated variables (basic heuristic)
        calc_matches = re.findall(r'(\w+)\s*=\s*(.+?\*\*.+?|.+?[\+\-\*/].+)', code)
        for var_name, formula in calc_matches:
            if var_name not in variables and not var_name.startswith('_'):
                # Convert Python expression to template formula
                formula_template = self._convert_to_formula(formula.strip())
                if formula_template:
                    variables[var_name] = {
                        "type": "calculated",
                        "formula": formula_template
                    }

        return variables

    def _convert_to_formula(self, python_expr: str) -> str:
        """Convert Python expression to template formula"""
        # b**2 - 4*a*c → {b}**2 - 4*{a}*{c}
        # This is a simplified conversion - may need manual adjustment

        # Find variable names (lowercase single letters or common names)
        var_pattern = r'\b([a-z]|discriminant|root|sqrt_d)\b'
        converted = re.sub(var_pattern, r'{\1}', python_expr)

        return converted

    def _extract_solution_steps(self, code: str) -> List[str]:
        """Extract solution steps from code"""
        # Look for solution_steps array
        steps_match = re.search(r'solution_steps\s*=\s*\[([\s\S]*?)\]', code)

        if not steps_match:
            return ["Step 1", "Step 2", "Step 3"]

        steps_text = steps_match.group(1)

        # Extract f-strings
        step_pattern = r'f?"([^"]+)"'
        steps = re.findall(step_pattern, steps_text)

        # Convert f-strings to templates
        return [self._convert_fstring_to_template(s) for s in steps]

    def _extract_socratic_hints(self, code: str) -> List[Dict]:
        """Extract socratic hints from code"""
        hints = []

        # Look for socratic_hints array
        hints_match = re.search(r'socratic_hints\s*=\s*\[([\s\S]*?)\](?=\s+return)', code)

        if not hints_match:
            return [
                {"level": 1, "hint": "Think about the approach", "nudge": "Use the relevant formula"},
                {"level": 2, "hint": "Calculate the intermediate values", "nudge": "Substitute the given values"},
                {"level": 3, "hint": "Complete the solution", "nudge": "Simplify to get final answer"}
            ]

        hints_text = hints_match.group(1)

        # Extract hint dictionaries (simplified)
        hint_blocks = re.findall(r'\{[^}]+\}', hints_text, re.DOTALL)

        for block in hint_blocks:
            level_match = re.search(r'"level":\s*(\d+)', block)
            hint_match = re.search(r'"hint":\s*f?"([^"]+)"', block)
            nudge_match = re.search(r'"nudge":\s*f?"([^"]+)"', block)

            if level_match and hint_match and nudge_match:
                hints.append({
                    "level": int(level_match.group(1)),
                    "hint": self._convert_fstring_to_template(hint_match.group(1)),
                    "nudge": self._convert_fstring_to_template(nudge_match.group(1))
                })

        return hints if hints else [
            {"level": 1, "hint": "Think about the approach", "nudge": "Use the relevant formula"}
        ]

    def migrate_pattern(self, method_name: str) -> bool:
        """Migrate a single pattern to JSON"""
        try:
            print(f"Migrating {method_name}...")

            # Extract method code
            code = self.extract_method_code(method_name)
            if not code:
                print(f"  ⚠️  Could not extract code for {method_name}")
                return False

            # Analyze pattern
            pattern_data = self.analyze_pattern(code, method_name)
            pattern_id = pattern_data['pattern_id']

            # Save JSON
            output_file = self.output_dir / f"{pattern_id}.json"

            # Skip if already exists
            if output_file.exists():
                print(f"  ⏭️  Skipping (already exists): {pattern_id}.json")
                return True

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(pattern_data, f, indent=2, ensure_ascii=False)

            print(f"  ✅ Created: {pattern_id}.json")
            return True

        except Exception as e:
            print(f"  ❌ Error migrating {method_name}: {e}")
            return False

    def migrate_all(self) -> Dict[str, int]:
        """Migrate all patterns"""
        patterns = self.extract_all_patterns()

        print(f"\n{'='*60}")
        print(f"PATTERN MIGRATION: {len(patterns)} patterns found")
        print(f"{'='*60}\n")

        stats = {"success": 0, "failed": 0, "skipped": 0}

        for method_name in patterns:
            success = self.migrate_pattern(method_name)
            if success:
                stats["success"] += 1
            else:
                stats["failed"] += 1

        print(f"\n{'='*60}")
        print(f"MIGRATION COMPLETE")
        print(f"{'='*60}")
        print(f"  ✅ Success: {stats['success']}")
        print(f"  ❌ Failed:  {stats['failed']}")
        print(f"  📊 Total:   {len(patterns)}")
        print(f"\nOutput directory: {self.output_dir}")

        return stats


if __name__ == "__main__":
    migrator = PatternMigrator(
        oracle_file="app/oracle/oracle_engine.py",
        output_dir="app/oracle/patterns"
    )

    stats = migrator.migrate_all()

    # Verify
    json_files = list(Path("app/oracle/patterns").glob("*.json"))
    print(f"\n📁 JSON patterns created: {len(json_files)}")

    if stats["failed"] > 0:
        print("\n⚠️  Some patterns failed. Review and manually fix if needed.")
