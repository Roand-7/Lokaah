"""
Bulk Pattern Generator - Creates minimal JSON templates for all 61 patterns
These can be enhanced later with specific details
"""

import json
from pathlib import Path
from datetime import datetime


# Complete list of all 61 pattern generators from oracle_engine.py
ALL_PATTERNS = [
    # Real Numbers (3)
    ("terminating_decimal", "Real Numbers", 2, 0.3),
    ("irrationality_proof", "Real Numbers", 3, 0.7),
    ("lcm_hcf", "Real Numbers", 2, 0.4),

    # Polynomials (4)
    ("polynomial_sum_product", "Polynomials", 2, 0.4),
    ("all_zeros_quartic", "Polynomials", 3, 0.6),
    ("polynomial_division_algorithm", "Polynomials", 3, 0.6),
    ("polynomial_find_k_factor", "Polynomials", 2, 0.5),

    # Linear Equations (4)
    ("consistency", "Linear Equations", 2, 0.5),
    ("digit_problem", "Linear Equations", 3, 0.6),
    ("speed_distance", "Linear Equations", 3, 0.5),
    ("linear_fraction_problem", "Linear Equations", 3, 0.6),
    ("linear_find_k_unique_solution", "Linear Equations", 2, 0.5),

    # Quadratic Equations (6)
    ("quadratic_nature_of_roots", "Quadratic Equations", 2, 0.4),
    ("quadratic_formula_solve", "Quadratic Equations", 3, 0.5),
    ("quadratic_sum_product_roots", "Quadratic Equations", 2, 0.5),
    ("quadratic_consecutive_integers", "Quadratic Equations", 3, 0.6),
    ("quadratic_age_problem", "Quadratic Equations", 3, 0.6),
    ("quadratic_area_perimeter", "Quadratic Equations", 3, 0.6),

    # Arithmetic Progressions (6)
    ("ap_nth_term_basic", "Arithmetic Progressions", 2, 0.4),
    ("ap_sum_n_terms", "Arithmetic Progressions", 3, 0.5),
    ("ap_find_common_difference", "Arithmetic Progressions", 2, 0.4),
    ("ap_salary_increment", "Arithmetic Progressions", 3, 0.6),
    ("ap_auditorium_seats", "Arithmetic Progressions", 3, 0.6),
    ("ap_find_n_given_sum", "Arithmetic Progressions", 3, 0.7),

    # Coordinate Geometry (3)
    ("coord_section_formula", "Coordinate Geometry", 3, 0.5),
    ("coord_distance_formula", "Coordinate Geometry", 2, 0.4),
    ("coord_area_triangle", "Coordinate Geometry", 3, 0.5),

    # Trigonometry (6)
    ("trig_tower_height_single_angle", "Heights and Distances", 3, 0.5),
    ("trig_two_angles_same_object", "Heights and Distances", 5, 0.7),
    ("trig_shadow_length", "Heights and Distances", 3, 0.5),
    ("trig_ladder_problem", "Heights and Distances", 3, 0.6),
    ("trig_complementary_angles", "Trigonometry", 2, 0.4),
    ("trig_identity_proof", "Trigonometry", 3, 0.7),

    # Triangles (4)
    ("triangle_bpt_basic", "Triangles", 3, 0.5),
    ("triangle_similarity_area_ratio", "Triangles", 3, 0.6),
    ("triangle_pythagoras_application", "Triangles", 3, 0.5),
    ("triangle_bpt_proof", "Triangles", 5, 0.8),

    # Circles (3)
    ("circle_tangent_equal_length", "Circles", 2, 0.4),
    ("circle_tangent_chord_angle", "Circles", 3, 0.6),
    ("circle_concentric_chord_tangent", "Circles", 3, 0.7),

    # Statistics (3)
    ("statistics_mean_frequency_table", "Statistics", 3, 0.5),
    ("statistics_median_grouped_data", "Statistics", 3, 0.6),
    ("statistics_mode_grouped_data", "Statistics", 3, 0.6),

    # Mensuration (6)
    ("mensuration_sector_area_arc", "Surface Areas and Volumes", 3, 0.5),
    ("mensuration_segment_area", "Surface Areas and Volumes", 3, 0.6),
    ("mensuration_combination_solid", "Surface Areas and Volumes", 5, 0.7),
    ("volume_frustum_cone", "Surface Areas and Volumes", 5, 0.7),
    ("volume_conversion_melting", "Surface Areas and Volumes", 5, 0.7),
    ("volume_hollow_cylinder", "Surface Areas and Volumes", 3, 0.6),

    # Probability (8)
    ("probability_single_card", "Probability", 2, 0.3),
    ("probability_two_dice", "Probability", 2, 0.4),
    ("probability_balls_without_replacement", "Probability", 3, 0.6),
    ("probability_complementary_event", "Probability", 2, 0.5),
    ("probability_pack_of_cards_advanced", "Probability", 3, 0.6),
    ("probability_at_least_one", "Probability", 3, 0.7),
    ("probability_spinner", "Probability", 2, 0.4),
    ("probability_random_number", "Probability", 2, 0.4),

    # Constructions (3)
    ("construction_divide_line_segment", "Constructions", 3, 0.5),
    ("construction_tangent_from_external_point", "Constructions", 3, 0.6),
    ("construction_similar_triangle", "Constructions", 3, 0.7),
]


def create_minimal_pattern(pattern_id, topic, marks, difficulty):
    """Create minimal viable JSON pattern"""
    return {
        "pattern_id": pattern_id,
        "topic": topic,
        "marks": marks,
        "difficulty": difficulty,
        "template_text": f"Question for {pattern_id.replace('_', ' ')} (to be enhanced)",
        "variables": {
            "x": {"type": "int", "min": 1, "max": 100},
            "y": {"type": "int", "min": 1, "max": 100}
        },
        "solution_template": [
            "Step 1: Identify the given information",
            "Step 2: Apply the relevant formula or concept",
            "Step 3: Calculate the result",
            "Step 4: State the final answer"
        ],
        "answer_template": "{result}",
        "validation_rules": [],
        "socratic_hints": [
            {"level": 1, "hint": "What concept is being tested here?", "nudge": "Think about the topic and relevant formulas"},
            {"level": 2, "hint": "How do you set up the problem?", "nudge": "Identify what is given and what needs to be found"},
            {"level": 3, "hint": "What formula or method applies?", "nudge": "Use the standard approach for this topic"}
        ],
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "_note": "This is a minimal template. Enhance with specific question text, variables, and solution steps."
    }


def generate_all_patterns():
    """Generate JSON files for all patterns"""
    output_dir = Path("app/oracle/patterns")
    output_dir.mkdir(parents=True, exist_ok=True)

    print("\n" + "="*60)
    print(f"BULK PATTERN GENERATION: {len(ALL_PATTERNS)} patterns")
    print("="*60 + "\n")

    created = 0
    skipped = 0

    for pattern_id, topic, marks, difficulty in ALL_PATTERNS:
        output_file = output_dir / f"{pattern_id}.json"

        if output_file.exists():
            print(f"  [SKIP] {pattern_id}.json (already exists)")
            skipped += 1
            continue

        try:
            pattern_data = create_minimal_pattern(pattern_id, topic, marks, difficulty)

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(pattern_data, f, indent=2, ensure_ascii=False)

            print(f"  [CREATE] {pattern_id}.json")
            created += 1

        except Exception as e:
            print(f"  [ERROR] {pattern_id}: {e}")

    print("\n" + "="*60)
    print(f"GENERATION COMPLETE")
    print("="*60)
    print(f"  Created: {created}")
    print(f"  Skipped: {skipped}")
    print(f"  Total:   {len(ALL_PATTERNS)}")

    json_files = list(output_dir.glob("*.json"))
    print(f"\nTotal JSON files in patterns/: {len(json_files)}")


if __name__ == "__main__":
    generate_all_patterns()
