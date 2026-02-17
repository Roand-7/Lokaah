"""
Simple Pattern Migration - No Unicode
Converts hardcoded Python generators to JSON templates
"""

import json
import re
from pathlib import Path
from datetime import datetime


# Manually defined pattern mappings (faster and more reliable)
PATTERN_DEFINITIONS = {
    "_gen_terminating_decimal": {
        "pattern_id": "terminating_decimal",
        "topic": "Real Numbers",
        "marks": 2,
        "difficulty": 0.3,
        "template_text": "Write whether the rational number {num}/{denom} will have a terminating or non-terminating repeating decimal expansion.",
        "variables": {
            "num": {"type": "int", "min": 1, "max": 99},
            "denom": {"type": "choice", "choices": [20, 25, 40, 3, 6, 7, 12]},
            "answer": {"type": "calculated", "formula": "'Terminating' if {denom} in [20, 25, 40] else 'Non-terminating repeating'"}
        }
    },
    "_gen_irrationality_proof": {
        "pattern_id": "irrationality_proof",
        "topic": "Real Numbers",
        "marks": 3,
        "difficulty": 0.7,
        "template_text": "Prove that {expr} is irrational.",
        "variables": {
            "base": {"type": "choice", "choices": [2, 3, 5, 7]},
            "expr": {"type": "calculated", "formula": "f'sqrt({base})'"}
        }
    },
    "_gen_lcm_hcf": {
        "pattern_id": "lcm_hcf",
        "topic": "Real Numbers",
        "marks": 2,
        "difficulty": 0.4,
        "template_text": "Find the HCF and LCM of {a} and {b} using prime factorization.",
        "variables": {
            "a": {"type": "choice", "choices": [12, 18, 24, 36, 48, 60, 72]},
            "b": {"type": "choice", "choices": [15, 20, 30, 45, 50, 75, 90]}
        }
    },
    # Trigonometry patterns
    "_gen_trig_tower_height_single_angle": {
        "pattern_id": "trig_tower_height_single_angle",
        "topic": "Heights and Distances",
        "marks": 3,
        "difficulty": 0.5,
        "template_text": "The angle of elevation of the top of a tower from a point {distance} meters away from its base is {angle}°. Find the height of the tower.",
        "variables": {
            "angle": {"type": "choice", "choices": [30, 45, 60]},
            "distance": {"type": "choice", "choices": [10, 20, 30, 40, 50, 100]}
        }
    },
    # Add more patterns here...
}


def create_pattern_json(pattern_def):
    """Create full JSON structure with default fields"""
    return {
        **pattern_def,
        "solution_template": ["Step 1", "Step 2", "Step 3"],
        "answer_template": "{answer}",
        "validation_rules": [],
        "socratic_hints": [
            {"level": 1, "hint": "Think about the approach", "nudge": "Use the relevant formula"},
            {"level": 2, "hint": "Calculate intermediate values", "nudge": "Substitute given values"},
            {"level": 3, "hint": "Complete the solution", "nudge": "Simplify to get final answer"}
        ],
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }


def migrate_patterns():
    """Migrate all defined patterns"""
    output_dir = Path("app/oracle/patterns")
    output_dir.mkdir(parents=True, exist_ok=True)

    print("\n" + "="*60)
    print(f"PATTERN MIGRATION: {len(PATTERN_DEFINITIONS)} patterns")
    print("="*60 + "\n")

    success_count = 0

    for method_name, pattern_def in PATTERN_DEFINITIONS.items():
        pattern_id = pattern_def['pattern_id']
        output_file = output_dir / f"{pattern_id}.json"

        if output_file.exists():
            print(f"  [SKIP] {pattern_id}.json")
            success_count += 1
            continue

        try:
            full_pattern = create_pattern_json(pattern_def)

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(full_pattern, f, indent=2, ensure_ascii=False)

            print(f"  [OK] Created {pattern_id}.json")
            success_count += 1

        except Exception as e:
            print(f"  [ERROR] Failed {pattern_id}: {e}")

    print("\n" + "="*60)
    print(f"COMPLETE: {success_count}/{len(PATTERN_DEFINITIONS)} patterns")
    print("="*60)

    # Count JSON files
    json_files = list(output_dir.glob("*.json"))
    print(f"\nTotal JSON files: {len(json_files)}")


if __name__ == "__main__":
    migrate_patterns()
