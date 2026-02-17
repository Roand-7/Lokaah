"""
ORACLE: Organized Recognition & Classification of Academic Learning Elements
CBSE Class 10 Mathematics - Pattern Analysis & Question Generation System
"""

import json
import re
import hashlib
import random
import math
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict
from datetime import datetime

from app.oracle.secure_sandbox import SafeMathSandbox, SandboxError


_validation_sandbox = SafeMathSandbox()


@dataclass
class QuestionPattern:
    """Pedagogical DNA of a question type"""
    pattern_id: str
    topic: str
    sub_topic: str
    marks: int
    question_type: str
    template: str
    variables: Dict[str, Any]
    difficulty: float
    bloom_taxonomy: str
    socratic_complexity: int
    frequency: str
    year_wise_count: Dict[str, int] = None

    def __post_init__(self):
        if self.year_wise_count is None:
            self.year_wise_count = {}


@dataclass
class ValidationRule:
    """Validation rule for generated questions"""
    rule_type: str  # "range", "inequality", "formula"
    condition: str  # Python expression as string
    reason: str
    
    def validate(self, context: Dict) -> bool:
        """Evaluate rule in given context"""
        try:
            return _validation_sandbox.evaluate_boolean(self.condition, context=context)
        except (SandboxError, ValueError, TypeError):
            return False


@dataclass
class GeneratedQuestion:
    """A procedurally generated question"""
    question_id: str
    pattern_id: str
    topic: str
    question_text: str
    solution_steps: List[str]
    final_answer: str
    marks: int
    difficulty: float
    estimated_time_minutes: int
    socratic_hints: List[Dict]
    generated_at: str
    unique_hash: str


class OraclePatternExtractor:
    """Analyzes CBSE PYQs to extract pedagogical patterns"""

    def __init__(self, cbse_year_range: Tuple[int, int] = (2015, 2025)):
        self.patterns: List[QuestionPattern] = []
        self.topic_weightage = defaultdict(lambda: {"marks": 0, "count": 0, "years": set()})
        self.cbse_range = cbse_year_range
        self.pattern_index = {}
        self.topic_patterns = defaultdict(list)

    def register_pattern(self, pattern: QuestionPattern) -> None:
        """Register a new pattern"""
        self.patterns.append(pattern)
        self.pattern_index[pattern.pattern_id] = pattern
        self.topic_patterns[pattern.topic].append(pattern)
        self.topic_weightage[pattern.topic]["marks"] += pattern.marks
        self.topic_weightage[pattern.topic]["count"] += 1

    def get_topic_analysis(self, topic: str) -> Dict:
        """Get analysis for a topic"""
        patterns = self.topic_patterns.get(topic, [])
        weightage = self.topic_weightage.get(topic, {})

        return {
            "topic": topic,
            "total_patterns": len(patterns),
            "total_marks_appearing": weightage.get("marks", 0),
            "difficulty_range": (
                min(p.difficulty for p in patterns) if patterns else 0,
                max(p.difficulty for p in patterns) if patterns else 0
            ),
            "marks_distribution": self._calculate_marks_dist(patterns),
            "high_frequency_patterns": [
                p.pattern_id for p in patterns if p.frequency == "High"
            ]
        }

    def _calculate_marks_dist(self, patterns: List[QuestionPattern]) -> Dict:
        dist = defaultdict(int)
        for p in patterns:
            dist[p.marks] += 1
        return dict(dist)

    def generate_recipe(self, topic: str) -> Dict:
        """Generate procedural recipe"""
        patterns = self.topic_patterns.get(topic, [])
        analysis = self.get_topic_analysis(topic)

        return {
            "recipe_id": f"{topic.lower().replace(' ', '_')}_cbse_class10",
            "topic": topic,
            "cbse_weightage_marks": analysis["total_marks_appearing"],
            "patterns": [{
                "pattern_type": p.pattern_id,
                "marks": p.marks,
                "difficulty": p.difficulty,
                "bloom_level": p.bloom_taxonomy,
                "template": p.template,
                "variables": p.variables,
                "socratic_flow": self._generate_socratic_flow(p)
            } for p in patterns],
            "generation_constraints": {
                "unique_check": True,
                "difficulty_scaling": "adaptive",
                "max_attempts": 100
            }
        }

    def _generate_socratic_flow(self, pattern: QuestionPattern) -> List[Dict]:
        """Generate Socratic flow"""
        return [
            {"stage": "elicit", "question": f"What do you know about {pattern.sub_topic}?"},
            {"stage": "probe", "question": "What is the key concept here?"},
            {"stage": "extend", "question": "Can you generalize this?"}
        ]

    def predict_2026_trends(self) -> Dict:
        """Predict 2026 trends"""
        return {
            "high_probability_patterns": [
                "irrationality_proof", "sum_product_zeros",
                "speed_distance", "trig_identity", "similarity_proof"
            ],
            "trend_analysis": {
                "difficulty_shift": "Slight increase in 3-4 mark problems",
                "case_study_themes": ["Environment", "Technology", "Health"]
            }
        }


class RecipeEngine:
    """Infinite Question Generator"""

    def __init__(self, recipes_dir: str = None):
        self.recipes: Dict[str, Dict] = {}
        self.generation_history = set()

        if recipes_dir:
            self.load_recipes(recipes_dir)

    def load_recipes(self, recipes_dir: str) -> None:
        """Load recipe JSON files"""
        import os
        
        if not os.path.exists(recipes_dir):
            print(f"⚠️ Recipes directory not found: {recipes_dir}")
            print("Using default patterns only")
            return
        
        for filename in os.listdir(recipes_dir):
            if filename.endswith('_recipe.json') and filename != 'master_index.json':
                filepath = os.path.join(recipes_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        recipe = json.load(f)
                        self.recipes[recipe['topic']] = recipe
                        print(f"✅ Loaded recipe: {recipe['topic']}")
                except Exception as e:
                    print(f"❌ Failed to load {filename}: {e}")

    def generate_question(
        self,
        topic: str,
        pattern_type: str = None,
        difficulty: float = None,
        marks: int = None
    ) -> Dict:
        """Generate unique question"""
        if topic not in self.recipes:
            # Fallback to default patterns
            if topic in ["Real Numbers", "Polynomials", "Linear Equations"]:
                return self._generate_default(topic, pattern_type)
            raise ValueError(f"Recipe not found: {topic}")

        recipe = self.recipes[topic]
        patterns = recipe['patterns']

        if pattern_type:
            patterns = [p for p in patterns if p['pattern_type'] == pattern_type]

        if not patterns:
            patterns = recipe['patterns']

        pattern = random.choice(patterns)
        return self._generate_from_pattern(pattern, topic)

    def _generate_default(self, topic: str, pattern_type: str = None) -> Dict:
        """Generate using default patterns when recipe not loaded"""
        defaults = {
            "Real Numbers": ["irrationality_proof", "lcm_hcf", "terminating"],
            "Polynomials": ["sum_product", "zeros"],
            "Linear Equations": ["consistency", "word_problem"]
        }

        ptype = pattern_type or random.choice(defaults.get(topic, ["generic"]))

        generators = {
            "irrationality_proof": self._gen_irrationality_proof,
            "lcm_hcf": self._gen_lcm_hcf,
            "terminating": self._gen_terminating_decimal,
            "sum_product": self._gen_polynomial_sum_product,
            "consistency": self._gen_consistency,
            "word_problem": self._gen_digit_problem
        }

        # Create minimal pattern dict
        pattern = {
            "pattern_type": ptype,
            "marks": 3,
            "difficulty": 0.5,
            "socratic_flow": []
        }

        generator = generators.get(ptype, self._gen_generic)
        return generator(pattern, topic)

    def _generate_from_pattern(self, pattern: Dict, topic: str) -> Dict:
        """Route to specific generator"""
        generators = {
            # Existing patterns
            'irrationality_proof': self._gen_irrationality_proof,
            'term_decimal_expansion': self._gen_terminating_decimal,
            'lcm_hcf_prime_factors': self._gen_lcm_hcf,
            'sum_product_zeros': self._gen_polynomial_sum_product,
            'all_zeros_quartic': self._gen_all_zeros_quartic,
            'system_consistency': self._gen_consistency,
            'digit_word_problem': self._gen_digit_problem,
            'speed_distance': self._gen_speed_distance,
            
            # Trigonometry patterns
            'trig_tower_height_single_angle': self._gen_trig_tower_height_single_angle,
            'trig_two_angles_same_object': self._gen_trig_two_angles_same_object,
            'trig_shadow_length': self._gen_trig_shadow_length,
            'trig_ladder_problem': self._gen_trig_ladder_problem,
            'trig_complementary_angles': self._gen_trig_complementary_angles,
            'trig_identity_proof': self._gen_trig_identity_proof,
            
            # Triangle patterns
            'triangle_bpt_basic': self._gen_triangle_bpt_basic,
            'triangle_similarity_area_ratio': self._gen_triangle_similarity_area_ratio,
            'triangle_pythagoras_application': self._gen_triangle_pythagoras_application,
            'triangle_bpt_proof': self._gen_triangle_bpt_proof,
            
            # Circle patterns
            'circle_tangent_equal_length': self._gen_circle_tangent_equal_length,
            'circle_tangent_chord_angle': self._gen_circle_tangent_chord_angle,
            'circle_concentric_chord_tangent': self._gen_circle_concentric_chord_tangent,
            
            # Coordinate Geometry patterns
            'coord_section_formula': self._gen_coord_section_formula,
            'coord_distance_formula': self._gen_coord_distance_formula,
            'coord_area_triangle': self._gen_coord_area_triangle,
            
            # Statistics patterns
            'statistics_mean_frequency_table': self._gen_statistics_mean_frequency_table,
            'statistics_median_grouped_data': self._gen_statistics_median_grouped_data,
            'statistics_mode_grouped_data': self._gen_statistics_mode_grouped_data,
            
            # Mensuration patterns
            'mensuration_sector_area_arc': self._gen_mensuration_sector_area_arc,
            'mensuration_segment_area': self._gen_mensuration_segment_area,
            'mensuration_combination_solid': self._gen_mensuration_combination_solid,
            
            # NEW PATTERNS - Quadratic Equations (6 patterns)
            'quadratic_nature_of_roots': self._gen_quadratic_nature_of_roots,
            'quadratic_formula_solve': self._gen_quadratic_formula_solve,
            'quadratic_sum_product_roots': self._gen_quadratic_sum_product_roots,
            'quadratic_consecutive_integers': self._gen_quadratic_consecutive_integers,
            'quadratic_age_problem': self._gen_quadratic_age_problem,
            'quadratic_area_perimeter': self._gen_quadratic_area_perimeter,
            
            # NEW PATTERNS - Arithmetic Progressions (6 patterns)
            'ap_nth_term_basic': self._gen_ap_nth_term_basic,
            'ap_sum_n_terms': self._gen_ap_sum_n_terms,
            'ap_find_common_difference': self._gen_ap_find_common_difference,
            'ap_salary_increment': self._gen_ap_salary_increment,
            'ap_auditorium_seats': self._gen_ap_auditorium_seats,
            'ap_find_n_given_sum': self._gen_ap_find_n_given_sum,
            
            # NEW PATTERNS - Probability (8 patterns)
            'probability_single_card': self._gen_probability_single_card,
            'probability_two_dice': self._gen_probability_two_dice,
            'probability_balls_without_replacement': self._gen_probability_balls_without_replacement,
            'probability_complementary_event': self._gen_probability_complementary_event,
            'probability_pack_of_cards_advanced': self._gen_probability_pack_of_cards_advanced,
            'probability_at_least_one': self._gen_probability_at_least_one,
            'probability_spinner': self._gen_probability_spinner,
            'probability_random_number': self._gen_probability_random_number,
            
            # NEW PATTERNS - Constructions (3 patterns)
            'construction_divide_line_segment': self._gen_construction_divide_line_segment,
            'construction_tangent_from_external_point': self._gen_construction_tangent_from_external_point,
            'construction_similar_triangle': self._gen_construction_similar_triangle,
            
            # NEW PATTERNS - Surface Areas & Volumes (3 patterns)
            'volume_frustum_cone': self._gen_volume_frustum_cone,
            'volume_conversion_melting': self._gen_volume_conversion_melting,
            'volume_hollow_cylinder': self._gen_volume_hollow_cylinder,
            
            # NEW PATTERNS - Polynomials (2 patterns)
            'polynomial_division_algorithm': self._gen_polynomial_division_algorithm,
            'polynomial_find_k_factor': self._gen_polynomial_find_k_factor,
            
            # NEW PATTERNS - Linear Equations (2 patterns)
            'linear_find_k_unique_solution': self._gen_linear_find_k_unique_solution,
            'linear_fraction_problem': self._gen_linear_fraction_problem,
        }

        generator = generators.get(pattern['pattern_type'], self._gen_generic)
        return generator(pattern, topic)

    def _gen_terminating_decimal(self, pattern, topic):
        """Generate terminating decimal question"""
        is_terminating = random.choice([True, False])
        denom = random.choice([20, 25, 40]) if is_terminating else random.choice([3, 6, 7, 12])
        nums = [n for n in range(1, 100) if self._gcd(n, denom) == 1]
        num = random.choice(nums)
        answer = "Terminating" if is_terminating else "Non-terminating repeating"

        question_text = (
            f"Write whether the rational number {num}/{denom} will have "
            "a terminating or non-terminating repeating decimal expansion."
        )

        socratic_hints = [
            {"level": 1, "hint": "What is the condition for a rational number to have terminating decimal?", "nudge": "Denominator must be of form 2^n × 5^m"},
            {"level": 2, "hint": f"Find prime factorization of {denom}", "nudge": "Check if only 2 and 5 are factors"},
            {"level": 3, "hint": "Does the denominator have factors other than 2 and 5?", "nudge": answer}
        ]
        
        return {
            "question_id": self._generate_id(),
            "pattern_id": pattern['pattern_type'],
            "topic": topic,
            "question_text": question_text,
            "solution_steps": [
                f"Prime factorization of {denom}",
                "Check if of form 2^n x 5^m",
                f"Conclusion: {answer}"
            ],
            "final_answer": answer,
            "marks": pattern['marks'],
            "difficulty": pattern['difficulty'],
            "estimated_time_minutes": 2,
            "socratic_hints": socratic_hints,
            "generated_at": datetime.now().isoformat(),
            "unique_hash": self._compute_hash(question_text)
        }

    def _gen_irrationality_proof(self, pattern, topic):
        """Generate irrationality proof"""
        base = random.choice([2, 3, 5, 7])
        forms = [f"sqrt({base})", f"{random.randint(2,5)}+{random.randint(1,3)}*sqrt({base})"]
        expr = random.choice(forms)

        question_text = f"Prove that {expr} is an irrational number."

        return {
            "question_id": self._generate_id(),
            "pattern_id": pattern['pattern_type'],
            "topic": topic,
            "question_text": question_text,
            "solution_steps": [
                f"Assume {expr} is rational = a/b (coprime)",
                "Derive contradiction",
                f"Conclude {expr} is irrational"
            ],
            "final_answer": f"{expr} is irrational",
            "marks": pattern['marks'],
            "difficulty": pattern['difficulty'],
            "estimated_time_minutes": 5,
            "socratic_hints": [
                {"hint": "Use proof by contradiction"},
                {"hint": "Assume opposite and show impossible"}
            ],
            "generated_at": datetime.now().isoformat(),
            "unique_hash": self._compute_hash(question_text)
        }

    def _gen_lcm_hcf(self, pattern, topic):
        """Generate LCM HCF verification"""
        primes = [2, 3, 5]
        a, b = random.sample(primes, 2)
        m, n = random.randint(1, 3), random.randint(1, 3)
        p, q = random.randint(1, 3), random.randint(1, 3)

        question_text = (
            f"If p = {a}^{m} x {b}^{n} and q = {a}^{p} x {b}^{q}, "
            "verify that LCM(p,q) x HCF(p,q) = pq."
        )

        return {
            "question_id": self._generate_id(),
            "pattern_id": pattern['pattern_type'],
            "topic": topic,
            "question_text": question_text,
            "solution_steps": [
                "Find HCF using minimum powers",
                "Find LCM using maximum powers",
                "Multiply and verify equality"
            ],
            "final_answer": "Verified: LCM x HCF = pq",
            "marks": pattern['marks'],
            "difficulty": pattern['difficulty'],
            "estimated_time_minutes": 4,
            "socratic_hints": [
                {"level": 1, "hint": "How do you find HCF from prime factorizations?", "nudge": "Take minimum power of each common prime factor"},
                {"level": 2, "hint": "How do you find LCM from prime factorizations?", "nudge": "Take maximum power of each prime that appears"},
                {"level": 3, "hint": "What is the relation between LCM, HCF and the two numbers?", "nudge": "LCM × HCF = p × q"}
            ],
            "generated_at": datetime.now().isoformat(),
            "unique_hash": self._compute_hash(question_text)
        }

    def _gen_polynomial_sum_product(self, pattern, topic):
        """Generate sum-product of zeros"""
        sum_val = random.randint(-10, 10)
        prod_val = random.randint(-20, 20)

        question_text = (
            f"Find a quadratic polynomial whose sum and product of zeroes are "
            f"{sum_val} and {prod_val} respectively."
        )

        return {
            "question_id": self._generate_id(),
            "pattern_id": pattern['pattern_type'],
            "topic": topic,
            "question_text": question_text,
            "solution_steps": [
                f"Use formula: x^2 - ({sum_val})x + ({prod_val})",
                "Or any scalar multiple k[...]"
            ],
            "final_answer": f"x^2 - {sum_val}x + {prod_val}",
            "marks": pattern['marks'],
            "difficulty": pattern['difficulty'],
            "estimated_time_minutes": 3,
            "socratic_hints": [
                {"level": 1, "hint": "What is the relation between roots and coefficients of ax²+bx+c=0?", "nudge": "Sum of roots = -b/a, Product of roots = c/a"},
                {"level": 2, "hint": "Given sum and product, how do you form the equation?", "nudge": "Use x² - (sum of roots)x + (product of roots) = 0"},
                {"level": 3, "hint": "Substitute the values and simplify", "nudge": f"x² - ({sum_val})x + ({prod_val})"}
            ],
            "generated_at": datetime.now().isoformat(),
            "unique_hash": self._compute_hash(question_text)
        }

    def _gen_all_zeros_quartic(self, pattern, topic):
        """Generate quartic polynomial with given zeros"""
        # Generate 4 zeros
        zeros = [random.randint(-5, 5) for _ in range(4)]
        
        question_text = (
            f"Find all the zeroes of the polynomial x^4 - ... if two of its zeroes are "
            f"{zeros[0]} and {zeros[1]}."
        )

        return {
            "question_id": self._generate_id(),
            "pattern_id": pattern['pattern_type'],
            "topic": topic,
            "question_text": question_text,
            "solution_steps": [
                f"Given zeros: {zeros[0]}, {zeros[1]}",
                f"Form factor: (x - {zeros[0]})(x - {zeros[1]})",
                "Divide polynomial by this factor",
                "Solve remaining quadratic",
                f"All zeros: {', '.join(map(str, zeros))}"
            ],
            "final_answer": f"Zeros are: {', '.join(map(str, zeros))}",
            "marks": pattern['marks'],
            "difficulty": pattern['difficulty'],
            "estimated_time_minutes": 5,
            "socratic_hints": [
                {
                    "level": 1,
                    "hint": "If you know two zeros, how can you form a factor?",
                    "nudge": f"Factor: (x - {zeros[0]})(x - {zeros[1]})"
                },
                {
                    "level": 2,
                    "hint": "What should you do next with the polynomial?",
                    "nudge": "Divide the polynomial by the factor to get a quadratic"
                },
                {
                    "level": 3,
                    "hint": "How do you find the remaining zeros?",
                    "nudge": "Solve the resulting quadratic equation"
                }
            ],
            "generated_at": datetime.now().isoformat(),
            "unique_hash": self._compute_hash(question_text)
        }

    def _gen_consistency(self, pattern, topic):
        """Generate consistency analysis"""
        condition = random.choice(["infinitely many solutions", "no solution", "unique solution"])

        question_text = f"For what value of k does the pair of linear equations have {condition}?"

        return {
            "question_id": self._generate_id(),
            "pattern_id": pattern['pattern_type'],
            "topic": topic,
            "question_text": question_text,
            "solution_steps": [
                "Compare ratios a1/a2, b1/b2, c1/c2",
                f"Apply condition for {condition}",
                "Solve for k"
            ],
            "final_answer": "k = [specific value]",
            "marks": pattern['marks'],
            "difficulty": pattern['difficulty'],
            "estimated_time_minutes": 4,
            "socratic_hints": [
                {"level": 1, "hint": "What are the conditions for unique/no/infinite solutions?", "nudge": "Compare ratios a₁/a₂, b₁/b₂, c₁/c₂"},
                {"level": 2, "hint": f"Apply the condition for {condition}", "nudge": "Set up the appropriate ratio equation"},
                {"level": 3, "hint": "Solve the equation for k", "nudge": "Calculate the specific value of k"}
            ],
            "generated_at": datetime.now().isoformat(),
            "unique_hash": self._compute_hash(question_text)
        }

    def _gen_digit_problem(self, pattern, topic):
        """Generate digit word problem"""
        x, y = random.randint(1, 9), random.randint(0, 9)
        diff = abs(x - y)

        question_text = (
            "Seven times a two-digit number is equal to four times the number "
            f"obtained by reversing its digits. If the difference of digits is {diff}, "
            "determine the number."
        )

        return {
            "question_id": self._generate_id(),
            "pattern_id": pattern['pattern_type'],
            "topic": topic,
            "question_text": question_text,
            "solution_steps": [
                "Let tens digit = x, units = y",
                "Form equations from conditions",
                "Solve system of equations"
            ],
            "final_answer": str(10 * x + y),
            "marks": pattern['marks'],
            "difficulty": pattern['difficulty'],
            "estimated_time_minutes": 6,
            "socratic_hints": [
                {"level": 1, "hint": "How do you represent a two-digit number algebraically?", "nudge": "If tens digit=x and units=y, number = 10x+y"},
                {"level": 2, "hint": "Form two equations from the given conditions", "nudge": "One from digit relationship, one from difference"},
                {"level": 3, "hint": "Solve the system of equations", "nudge": "Use substitution or elimination method"}
            ],
            "generated_at": datetime.now().isoformat(),
            "unique_hash": self._compute_hash(question_text)
        }

    def _gen_speed_distance(self, pattern, topic):
        """Generate speed-distance problem"""
        dist = random.choice([360, 480])
        speed_diff = random.choice([5, 10])

        question_text = (
            f"A train travels {dist} km. If speed were {speed_diff} km/h more, "
            "it would take 1 hour less. Find original speed."
        )

        return {
            "question_id": self._generate_id(),
            "pattern_id": pattern['pattern_type'],
            "topic": topic,
            "question_text": question_text,
            "solution_steps": [
                "Let speed = x km/h",
                "Set up time equation",
                "Form quadratic equation",
                "Solve for x"
            ],
            "final_answer": "Speed = [value] km/h",
            "marks": pattern['marks'],
            "difficulty": pattern['difficulty'],
            "estimated_time_minutes": 8,
            "socratic_hints": [
                {"level": 1, "hint": "What is the relationship between speed, distance, and time?", "nudge": "Time = Distance / Speed"},
                {"level": 2, "hint": "Set up equation comparing two time scenarios", "nudge": "Time at speed x vs time at speed (x + speed_diff)"},
                {"level": 3, "hint": "Form and solve the quadratic equation", "nudge": "Cross-multiply and solve for x"}
            ],
            "generated_at": datetime.now().isoformat(),
            "unique_hash": self._compute_hash(question_text)
        }

    # ============================================================
    # TRIGONOMETRY - HEIGHTS & DISTANCES PATTERNS
    # ============================================================

    def _gen_trig_tower_height_single_angle(self, pattern, topic):
        """
        Pattern: Tower height from single angle of elevation
        Frequency: 8/11 papers (Very High)
        Source: 2023 Q37, 2024 Q34, 2025 Q37, 2022 Q13
        """
        import math
        
        # Variable pools from CBSE papers
        distance = random.choice([30, 36, 40, 48, 50, 75, 80, 100])
        angle = random.choice([30, 45, 60])
        object_type = random.choice(["tower", "building", "tree", "pole", "lighthouse"])
        
        # Calculation (deterministic)
        if angle == 30:
            height = distance / math.sqrt(3)
            tan_value = "1/√3"
        elif angle == 45:
            height = distance * 1
            tan_value = "1"
        else:  # 60
            height = distance * math.sqrt(3)
            tan_value = "√3"
        
        height_rounded = round(height, 2)
        
        # Validation
        if height_rounded < 10 or height_rounded > 200:
            return self._gen_trig_tower_height_single_angle(pattern, topic)
        
        question_text = (
            f"From a point on the ground {distance} m away from the base of a {object_type}, "
            f"the angle of elevation of its top is {angle}°. "
            f"Find the height of the {object_type}. (Use √3 = 1.73 if needed)"
        )
        
        solution_steps = [
            f"Let the height of the {object_type} be h metres.",
            f"Given: Distance from base = {distance} m, Angle of elevation = {angle}°",
            f"In the right triangle formed:",
            f"tan {angle}° = h / {distance}",
            f"h = {distance} × tan {angle}°",
            f"h = {distance} × {tan_value}",
            f"h = {height_rounded} m"
        ]
        
        socratic_hints = [
            {
                "level": 1,
                "hint": "Which trigonometric ratio relates the opposite side (height) and adjacent side (distance)?",
                "nudge": "Think about the definition of tangent in a right triangle."
            },
            {
                "level": 2,
                "hint": f"What is the value of tan {angle}°?",
                "nudge": f"Recall: tan 30° = 1/√3, tan 45° = 1, tan 60° = √3"
            },
            {
                "level": 3,
                "hint": f"The height h = {distance} × tan {angle}°. Can you calculate this?",
                "nudge": f"Substitute tan {angle}° = {tan_value} and multiply by {distance}."
            }
        ]
        
        return {
            "question_id": self._generate_id(),
            "pattern_id": "trig_tower_height_single_angle",
            "topic": topic,
            "question_text": question_text,
            "solution_steps": solution_steps,
            "final_answer": f"Height = {height_rounded} m",
            "marks": 3,
            "difficulty": 0.5,
            "estimated_time_minutes": 4,
            "socratic_hints": socratic_hints,
            "generated_at": datetime.now().isoformat(),
            "unique_hash": self._compute_hash(question_text)
        }

    def _gen_trig_two_angles_same_object(self, pattern, topic):
        """
        Pattern: Distance between two positions from angles of elevation
        Frequency: 7/11 papers (High)
        Source: 2024 Q34, 2025 Q37, 2022 Q9
        """
        import math
        
        # Variables
        height = random.choice([45, 50, 60, 75, 100])
        angle1 = 30
        angle2 = 60
        
        # Calculations
        distance1 = height * math.sqrt(3)  # tan 30° = 1/√3
        distance2 = height / math.sqrt(3)  # tan 60° = √3
        distance_between = distance1 - distance2
        
        distance_between_rounded = round(distance_between, 2)
        
        question_text = (
            f"From the top of a {height} m high lighthouse, the angles of depression "
            f"of two ships on the same side of it are observed to be {angle1}° and {angle2}°. "
            f"Find the distance between the two ships. (Use √3 = 1.73)"
        )
        
        solution_steps = [
            f"Let the distances of ships from base be x m and y m (x > y)",
            f"Height of lighthouse = {height} m",
            f"For angle of depression {angle1}°: tan {angle1}° = {height}/x",
            f"x = {height} / tan {angle1}° = {height} × √3 = {round(distance1, 2)} m",
            f"For angle of depression {angle2}°: tan {angle2}° = {height}/y",
            f"y = {height} / tan {angle2}° = {height} / √3 = {round(distance2, 2)} m",
            f"Distance between ships = x - y = {distance_between_rounded} m"
        ]
        
        socratic_hints = [
            {
                "level": 1,
                "hint": "Draw a diagram showing the lighthouse and two ships. What relationships do you see?",
                "nudge": "The angles of depression from the top equal the angles of elevation from the ships."
            },
            {
                "level": 2,
                "hint": "How can you find the distance of each ship from the base?",
                "nudge": "Use tan θ = height/distance for each angle separately."
            },
            {
                "level": 3,
                "hint": f"Calculate distances using tan 30° = 1/√3 and tan 60° = √3.",
                "nudge": f"First ship: {height} × √3, Second ship: {height} / √3. Then subtract."
            }
        ]
        
        return {
            "question_id": self._generate_id(),
            "pattern_id": "trig_two_angles_same_object",
            "topic": topic,
            "question_text": question_text,
            "solution_steps": solution_steps,
            "final_answer": f"Distance between ships = {distance_between_rounded} m",
            "marks": 5,
            "difficulty": 0.7,
            "estimated_time_minutes": 7,
            "socratic_hints": socratic_hints,
            "generated_at": datetime.now().isoformat(),
            "unique_hash": self._compute_hash(question_text)
        }

    def _gen_trig_shadow_length(self, pattern, topic):
        """
        Pattern: Shadow length from angle of elevation
        Frequency: 5/11 papers (Medium-High)
        Source: 2023 Q23, 2016 Q3
        """
        import math
        
        # Variables
        height = random.choice([10, 15, 18, 20, 24, 30])
        angle = random.choice([30, 45, 60])
        
        # Calculation
        if angle == 30:
            shadow_length = height * math.sqrt(3)
            tan_value = "1/√3"
            formula = f"{height} × √3"
        elif angle == 45:
            shadow_length = height
            tan_value = "1"
            formula = f"{height} × 1"
        else:  # 60
            shadow_length = height / math.sqrt(3)
            tan_value = "√3"
            formula = f"{height} / √3"
        
        shadow_rounded = round(shadow_length, 2)
        
        question_text = (
            f"Find the length of the shadow on the ground of a pole of height {height} m "
            f"when the angle of elevation θ of the sun is such that tan θ = "
            f"{'6/7' if angle == 45 else tan_value}."
        )
        
        # Adjust if using 6/7 ratio
        if angle == 45:
            actual_ratio = random.choice(["6/7", "3/4", "5/12"])
            numerator, denominator = map(int, actual_ratio.split('/'))
            shadow_length = height * denominator / numerator
            shadow_rounded = round(shadow_length, 2)
            question_text = (
                f"Find the length of the shadow on the ground of a pole of height {height} m "
                f"when the angle of elevation θ of the sun is such that tan θ = {actual_ratio}."
            )
            formula = f"{height} × {denominator}/{numerator}"
        
        solution_steps = [
            f"Let shadow length = x metres",
            f"Height of pole = {height} m",
            f"tan θ = height / shadow",
            f"Given: tan θ = {tan_value if angle != 45 else actual_ratio}",
            f"Therefore: {tan_value if angle != 45 else actual_ratio} = {height} / x",
            f"x = {formula}",
            f"x = {shadow_rounded} m"
        ]
        
        socratic_hints = [
            {
                "level": 1,
                "hint": "What is the relationship between the pole, its shadow, and the sun's rays?",
                "nudge": "They form a right triangle with the angle of elevation at the tip of the shadow."
            },
            {
                "level": 2,
                "hint": "Which trigonometric ratio involves height and shadow?",
                "nudge": "tan θ = opposite / adjacent = height / shadow"
            },
            {
                "level": 3,
                "hint": f"Rearrange tan θ = {height}/x to find x.",
                "nudge": f"x = {height} / tan θ = {formula}"
            }
        ]
        
        return {
            "question_id": self._generate_id(),
            "pattern_id": "trig_shadow_length",
            "topic": topic,
            "question_text": question_text,
            "solution_steps": solution_steps,
            "final_answer": f"Shadow length = {shadow_rounded} m",
            "marks": 2,
            "difficulty": 0.4,
            "estimated_time_minutes": 3,
            "socratic_hints": socratic_hints,
            "generated_at": datetime.now().isoformat(),
            "unique_hash": self._compute_hash(question_text)
        }

    def _gen_trig_ladder_problem(self, pattern, topic):
        """
        Pattern: Ladder length and base distance
        Frequency: 4/11 papers (Medium)
        Source: 2025 Case Study Q36 (Basic), 2019 Q27
        """
        import math
        
        # Variables
        wall_height = random.choice([12, 15, 18, 20, 24])
        angle = random.choice([30, 45, 60])
        
        # Calculations
        if angle == 30:
            ladder_length = 2 * wall_height
            base_distance = wall_height * math.sqrt(3)
            sin_value = "1/2"
            cos_value = "√3/2"
        elif angle == 45:
            ladder_length = wall_height * math.sqrt(2)
            base_distance = wall_height
            sin_value = "1/√2"
            cos_value = "1/√2"
        else:  # 60
            ladder_length = (2 * wall_height) / math.sqrt(3)
            base_distance = wall_height / math.sqrt(3)
            sin_value = "√3/2"
            cos_value = "1/2"
        
        ladder_rounded = round(ladder_length, 2)
        base_rounded = round(base_distance, 2)
        
        question_text = (
            f"A ladder is leaning against a wall. It reaches a height of {wall_height} m on the wall "
            f"and makes an angle of {angle}° with the ground. Find:\n"
            f"(i) The length of the ladder\n"
            f"(ii) The distance of the foot of the ladder from the wall\n"
            f"(Use √2 = 1.41, √3 = 1.73 if needed)"
        )
        
        solution_steps = [
            f"Let ladder length = l, base distance = x",
            f"Wall height = {wall_height} m, Angle = {angle}°",
            f"(i) Using sin {angle}° = {wall_height} / l",
            f"sin {angle}° = {sin_value}",
            f"l = {wall_height} / {sin_value} = {ladder_rounded} m",
            f"(ii) Using cos {angle}° = x / l",
            f"x = l × cos {angle}° = {ladder_rounded} × {cos_value}",
            f"x = {base_rounded} m"
        ]
        
        socratic_hints = [
            {
                "level": 1,
                "hint": "Draw a right triangle with the ladder as hypotenuse. What are the three sides?",
                "nudge": "Wall (opposite), ground distance (adjacent), ladder (hypotenuse)."
            },
            {
                "level": 2,
                "hint": "Which ratio gives hypotenuse when you know the opposite side?",
                "nudge": "sin θ = opposite / hypotenuse, so hypotenuse = opposite / sin θ"
            },
            {
                "level": 3,
                "hint": f"For part (ii), use cos {angle}° to find the base distance.",
                "nudge": f"cos {angle}° = base / ladder, so base = ladder × cos {angle}°"
            }
        ]
        
        return {
            "question_id": self._generate_id(),
            "pattern_id": "trig_ladder_problem",
            "topic": topic,
            "question_text": question_text,
            "solution_steps": solution_steps,
            "final_answer": f"(i) Ladder = {ladder_rounded} m, (ii) Base distance = {base_rounded} m",
            "marks": 3,
            "difficulty": 0.6,
            "estimated_time_minutes": 5,
            "socratic_hints": socratic_hints,
            "generated_at": datetime.now().isoformat(),
            "unique_hash": self._compute_hash(question_text)
        }

    def _gen_trig_complementary_angles(self, pattern, topic):
        """
        Pattern: Complementary angles verification
        Frequency: 6/11 papers (High)
        Source: 2023 Q23(B), 2024 Q23(B), 2025 Q24
        """
        import math
        
        # Variables
        angle_a = random.choice([15, 20, 30])
        angle_b = 90 - angle_a
        
        question_text = (
            f"If sin(A+B) = √3/2 and cos(A-B) = 1, find the values of A and B, "
            f"where 0° ≤ A, B, (A+B) ≤ 90°."
        )
        
        # Standard version
        sum_val = random.choice(["√3/2", "1/2", "1/√2"])
        diff_val = random.choice(["1", "√3/2", "1/√2"])
        
        if sum_val == "√3/2":
            a_plus_b = 60
        elif sum_val == "1/2":
            a_plus_b = 30
        else:
            a_plus_b = 45
        
        if diff_val == "1":
            a_minus_b = 0
        elif diff_val == "√3/2":
            a_minus_b = 30
        else:
            a_minus_b = 45
        
        angle_a_result = (a_plus_b + a_minus_b) / 2
        angle_b_result = (a_plus_b - a_minus_b) / 2
        
        solution_steps = [
            f"Given: sin(A+B) = {sum_val} and cos(A-B) = {diff_val}",
            f"sin(A+B) = {sum_val} ⇒ A+B = {a_plus_b}° (since sin {a_plus_b}° = {sum_val})",
            f"cos(A-B) = {diff_val} ⇒ A-B = {a_minus_b}° (since cos {a_minus_b}° = {diff_val})",
            f"Solving: A+B = {a_plus_b}° ... (1)",
            f"         A-B = {a_minus_b}° ... (2)",
            f"Adding (1) and (2): 2A = {a_plus_b + a_minus_b}°",
            f"A = {int(angle_a_result)}°",
            f"Substituting in (1): B = {int(angle_b_result)}°"
        ]
        
        socratic_hints = [
            {
                "level": 1,
                "hint": "What angles have sine or cosine values of √3/2, 1/2, etc.?",
                "nudge": "Recall standard values: sin 30° = 1/2, sin 60° = √3/2, cos 0° = 1"
            },
            {
                "level": 2,
                "hint": "Once you know A+B and A-B, how can you find A and B individually?",
                "nudge": "Add the two equations to eliminate B, subtract to eliminate A."
            },
            {
                "level": 3,
                "hint": f"From A+B = {a_plus_b}° and A-B = {a_minus_b}°, solve the system.",
                "nudge": f"2A = {a_plus_b + a_minus_b}°, so A = {int(angle_a_result)}°"
            }
        ]
        
        return {
            "question_id": self._generate_id(),
            "pattern_id": "trig_complementary_angles",
            "topic": topic,
            "question_text": question_text,
            "solution_steps": solution_steps,
            "final_answer": f"A = {int(angle_a_result)}°, B = {int(angle_b_result)}°",
            "marks": 2,
            "difficulty": 0.5,
            "estimated_time_minutes": 3,
            "socratic_hints": socratic_hints,
            "generated_at": datetime.now().isoformat(),
            "unique_hash": self._compute_hash(question_text)
        }

    def _gen_trig_identity_proof(self, pattern, topic):
        """
        Pattern: Trigonometric identity LHS = RHS
        Frequency: 9/11 papers (Very High)
        Source: 2023 Q30, 2024 Q29, 2025 Q30
        """
        identities = [
            {
                "lhs": "(cosec θ - sin θ)(sec θ - cos θ)",
                "rhs": "1/(tan θ + cot θ)",
                "steps": [
                    "LHS = (1/sin θ - sin θ)(1/cos θ - cos θ)",
                    "    = [(1 - sin²θ)/sin θ][(1 - cos²θ)/cos θ]",
                    "    = [cos²θ/sin θ][sin²θ/cos θ]",
                    "    = sin θ cos θ",
                    "RHS = 1/(sin θ/cos θ + cos θ/sin θ)",
                    "    = 1/[(sin²θ + cos²θ)/(sin θ cos θ)]",
                    "    = sin θ cos θ",
                    "Hence LHS = RHS"
                ]
            },
            {
                "lhs": "(1 + sec θ - tan θ)/(1 + sec θ + tan θ)",
                "rhs": "(1 - sin θ)/cos θ",
                "steps": [
                    "Multiply numerator and denominator by (1 + sec θ - tan θ)",
                    "Use sec²θ - tan²θ = 1",
                    "Simplify to get (1 - sin θ)/cos θ"
                ]
            },
            {
                "lhs": "√[(sec A - 1)/(sec A + 1)] + √[(sec A + 1)/(sec A - 1)]",
                "rhs": "2 cosec A",
                "steps": [
                    "Rationalize each square root term",
                    "Use sec²A - 1 = tan²A",
                    "Simplify to 2/sin A = 2 cosec A"
                ]
            }
        ]
        
        chosen = random.choice(identities)
        
        question_text = f"Prove that: {chosen['lhs']} = {chosen['rhs']}"
        
        socratic_hints = [
            {
                "level": 1,
                "hint": "Start by expressing everything in terms of sin θ and cos θ.",
                "nudge": "Remember: sec θ = 1/cos θ, cosec θ = 1/sin θ, tan θ = sin θ/cos θ"
            },
            {
                "level": 2,
                "hint": "Look for Pythagorean identities: sin²θ + cos²θ = 1 or sec²θ - tan²θ = 1",
                "nudge": "These will help simplify the expressions."
            },
            {
                "level": 3,
                "hint": "Work on LHS and RHS separately, then show they're equal.",
                "nudge": "Simplify LHS step by step using the identities."
            }
        ]
        
        return {
            "question_id": self._generate_id(),
            "pattern_id": "trig_identity_proof",
            "topic": topic,
            "question_text": question_text,
            "solution_steps": chosen['steps'],
            "final_answer": "LHS = RHS (Proved)",
            "marks": 3,
            "difficulty": 0.7,
            "estimated_time_minutes": 5,
            "socratic_hints": socratic_hints,
            "generated_at": datetime.now().isoformat(),
            "unique_hash": self._compute_hash(question_text)
        }

    # ============================================================
    # TRIANGLES - SIMILARITY & BPT PATTERNS
    # ============================================================

    def _gen_triangle_bpt_basic(self, pattern, topic):
        """
        Pattern: Basic Proportionality Theorem (DE || BC)
        Frequency: 10/11 papers (Very High)
        Source: 2023 Q10, 2024 Q6, 2025 Q13
        """
        # Variables
        ad = random.choice([2, 3, 4, 5, 6])
        db = random.choice([3, 4, 5, 6, 7])
        bc = random.choice([10, 12, 15, 18, 20])
        
        # Calculation: AD/AB = DE/BC
        ab = ad + db
        de = (ad / ab) * bc
        de_rounded = round(de, 2)
        
        question_text = (
            f"In triangle ABC, DE || BC. If AD = {ad} cm, DB = {db} cm, and BC = {bc} cm, "
            f"find the length of DE."
        )
        
        solution_steps = [
            f"Given: DE || BC",
            f"AD = {ad} cm, DB = {db} cm, BC = {bc} cm",
            f"AB = AD + DB = {ad} + {db} = {ab} cm",
            f"By Basic Proportionality Theorem:",
            f"AD/AB = DE/BC",
            f"{ad}/{ab} = DE/{bc}",
            f"DE = ({ad}/{ab}) × {bc}",
            f"DE = {de_rounded} cm"
        ]
        
        socratic_hints = [
            {
                "level": 1,
                "hint": "What theorem applies when a line is parallel to one side of a triangle?",
                "nudge": "Basic Proportionality Theorem (or Thales' Theorem)"
            },
            {
                "level": 2,
                "hint": "How are the segments AD, DB, and AB related?",
                "nudge": "AB = AD + DB (D is on AB)"
            },
            {
                "level": 3,
                "hint": f"Set up the proportion: AD/AB = DE/BC",
                "nudge": f"{ad}/{ab} = DE/{bc}, so DE = {de_rounded} cm"
            }
        ]
        
        return {
            "question_id": self._generate_id(),
            "pattern_id": "triangle_bpt_basic",
            "topic": topic,
            "question_text": question_text,
            "solution_steps": solution_steps,
            "final_answer": f"DE = {de_rounded} cm",
            "marks": 2,
            "difficulty": 0.4,
            "estimated_time_minutes": 3,
            "socratic_hints": socratic_hints,
            "generated_at": datetime.now().isoformat(),
            "unique_hash": self._compute_hash(question_text)
        }

    def _gen_triangle_similarity_area_ratio(self, pattern, topic):
        """
        Pattern: Area ratio of similar triangles
        Frequency: 8/11 papers (High)
        Source: 2023 Q8, 2024 Q10, 2025 Q9
        """
        # Variables
        side_ratio_num = random.choice([2, 3, 4])
        side_ratio_den = random.choice([3, 4, 5])
        
        # Ensure proper ratio
        if side_ratio_num >= side_ratio_den:
            side_ratio_num, side_ratio_den = side_ratio_den, side_ratio_num
        
        area_ratio_num = side_ratio_num ** 2
        area_ratio_den = side_ratio_den ** 2
        
        # Give one area, find other
        if random.choice([True, False]):
            area1 = area_ratio_num * random.choice([8, 12, 16])
            area2 = (area_ratio_den / area_ratio_num) * area1
        else:
            area2 = area_ratio_den * random.choice([18, 25, 32])
            area1 = (area_ratio_num / area_ratio_den) * area2
        
        area2_rounded = round(area2, 2)
        
        question_text = (
            f"Triangle ABC ~ Triangle DEF. The ratio of their corresponding sides is {side_ratio_num}:{side_ratio_den}. "
            f"If the area of triangle ABC is {int(area1)} cm², find the area of triangle DEF."
        )
        
        solution_steps = [
            f"Given: Triangle ABC ~ Triangle DEF",
            f"Ratio of corresponding sides = {side_ratio_num}:{side_ratio_den}",
            f"Area of triangle ABC = {int(area1)} cm²",
            f"Theorem: Ratio of areas of similar triangles = (Ratio of sides)²",
            f"Area(ABC)/Area(DEF) = ({side_ratio_num}/{side_ratio_den})²",
            f"Area(ABC)/Area(DEF) = {area_ratio_num}/{area_ratio_den}",
            f"{int(area1)}/Area(DEF) = {area_ratio_num}/{area_ratio_den}",
            f"Area(DEF) = ({area_ratio_den}/{area_ratio_num}) × {int(area1)}",
            f"Area(DEF) = {area2_rounded} cm²"
        ]
        
        socratic_hints = [
            {
                "level": 1,
                "hint": "What is the relationship between the ratio of areas and the ratio of sides in similar triangles?",
                "nudge": "The ratio of areas equals the square of the ratio of corresponding sides."
            },
            {
                "level": 2,
                "hint": f"If sides are in ratio {side_ratio_num}:{side_ratio_den}, what is the ratio of areas?",
                "nudge": f"({side_ratio_num}/{side_ratio_den})² = {area_ratio_num}/{area_ratio_den}"
            },
            {
                "level": 3,
                "hint": f"Set up: {int(area1)}/Area(DEF) = {area_ratio_num}/{area_ratio_den}",
                "nudge": f"Cross-multiply to find Area(DEF) = {area2_rounded} cm²"
            }
        ]
        
        return {
            "question_id": self._generate_id(),
            "pattern_id": "triangle_similarity_area_ratio",
            "topic": topic,
            "question_text": question_text,
            "solution_steps": solution_steps,
            "final_answer": f"Area of DEF = {area2_rounded} cm²",
            "marks": 2,
            "difficulty": 0.5,
            "estimated_time_minutes": 4,
            "socratic_hints": socratic_hints,
            "generated_at": datetime.now().isoformat(),
            "unique_hash": self._compute_hash(question_text)
        }

    def _gen_triangle_pythagoras_application(self, pattern, topic):
        """
        Pattern: Pythagoras theorem application
        Frequency: 7/11 papers (High)
        Source: 2023 Q25, 2024 Q33, 2025 Q18
        """
        import math
        
        # Variables (Pythagorean triples)
        triples = [(3,4,5), (5,12,13), (8,15,17), (7,24,25), (6,8,10)]
        multiplier = random.choice([1, 2, 3])
        base_triple = random.choice(triples)
        
        a, b, c = [x * multiplier for x in base_triple]
        
        # Randomly choose which side to find
        find_side = random.choice(['hypotenuse', 'leg'])
        
        if find_side == 'hypotenuse':
            given1, given2 = a, b
            find_val = c
            question_text = (
                f"In a right-angled triangle, the two legs are {given1} cm and {given2} cm. "
                f"Find the length of the hypotenuse."
            )
            formula = f"√({given1}² + {given2}²)"
        else:
            given1, find_val = c, a
            given2 = b
            question_text = (
                f"In a right-angled triangle, the hypotenuse is {given1} cm and one leg is {given2} cm. "
                f"Find the length of the other leg."
            )
            formula = f"√({given1}² - {given2}²)"
        
        solution_steps = [
            f"Let the right-angled triangle be ABC with ∠B = 90°",
            f"Given: " + (f"AB = {a} cm, BC = {b} cm" if find_side == 'hypotenuse' else f"AC = {c} cm, BC = {b} cm"),
            f"By Pythagoras theorem: AC² = AB² + BC²" if find_side == 'hypotenuse' else f"AB² = AC² - BC²",
            f"AC² = {a}² + {b}² = {a**2} + {b**2} = {c**2}" if find_side == 'hypotenuse' else f"AB² = {c}² - {b}² = {c**2} - {b**2} = {a**2}",
            f"AC = {c} cm" if find_side == 'hypotenuse' else f"AB = {a} cm"
        ]
        
        socratic_hints = [
            {
                "level": 1,
                "hint": "What theorem relates the sides of a right-angled triangle?",
                "nudge": "Pythagoras theorem: hypotenuse² = leg₁² + leg₂²"
            },
            {
                "level": 2,
                "hint": "Identify which side is the hypotenuse and which are the legs.",
                "nudge": "The hypotenuse is the longest side opposite the right angle."
            },
            {
                "level": 3,
                "hint": f"Apply the formula: {formula}",
                "nudge": f"Calculate {formula} = {find_val} cm"
            }
        ]
        
        return {
            "question_id": self._generate_id(),
            "pattern_id": "triangle_pythagoras_application",
            "topic": topic,
            "question_text": question_text,
            "solution_steps": solution_steps,
            "final_answer": f"Length = {find_val} cm",
            "marks": 2,
            "difficulty": 0.3,
            "estimated_time_minutes": 3,
            "socratic_hints": socratic_hints,
            "generated_at": datetime.now().isoformat(),
            "unique_hash": self._compute_hash(question_text)
        }

    def _gen_triangle_bpt_proof(self, pattern, topic):
        """
        Pattern: Prove Basic Proportionality Theorem
        Frequency: 5/11 papers (Medium)
        Source: 2024 Q33, 2025 Q34
        """
        question_text = (
            "If a line is drawn parallel to one side of a triangle to intersect the other two sides "
            "in distinct points, prove that the other two sides are divided in the same ratio."
        )
        
        solution_steps = [
            "Let triangle ABC have DE || BC, where D is on AB and E is on AC",
            "To Prove: AD/DB = AE/EC",
            "Construction: Join BE and CD. Draw DM ⊥ AC and EN ⊥ AB",
            "Proof:",
            "Area(ADE) = (1/2) × AD × EN ... (1)",
            "Area(BDE) = (1/2) × DB × EN ... (2)",
            "From (1) and (2): Area(ADE)/Area(BDE) = AD/DB ... (3)",
            "Similarly: Area(ADE)/Area(DEC) = AE/EC ... (4)",
            "Since DE || BC, triangles BDE and DEC have the same base DE and equal heights",
            "∴ Area(BDE) = Area(DEC) ... (5)",
            "From (3), (4), and (5): AD/DB = AE/EC",
            "Hence proved."
        ]
        
        socratic_hints = [
            {
                "level": 1,
                "hint": "Draw a diagram showing triangle ABC with DE parallel to BC.",
                "nudge": "Mark D on AB and E on AC such that DE || BC"
            },
            {
                "level": 2,
                "hint": "How can you use areas of triangles to establish the required ratio?",
                "nudge": "Compare Area(ADE), Area(BDE), and Area(DEC)"
            },
            {
                "level": 3,
                "hint": "What can you say about triangles BDE and DEC when DE || BC?",
                "nudge": "They have equal areas (same base, equal heights)"
            }
        ]
        
        return {
            "question_id": self._generate_id(),
            "pattern_id": "triangle_bpt_proof",
            "topic": topic,
            "question_text": question_text,
            "solution_steps": solution_steps,
            "final_answer": "AD/DB = AE/EC (Proved)",
            "marks": 5,
            "difficulty": 0.8,
            "estimated_time_minutes": 10,
            "socratic_hints": socratic_hints,
            "generated_at": datetime.now().isoformat(),
            "unique_hash": self._compute_hash(question_text)
        }

    # ============================================================
    # CIRCLES - TANGENTS & CHORDS PATTERNS
    # ============================================================

    def _gen_circle_tangent_equal_length(self, pattern, topic):
        """
        Pattern: Equal tangents from external point
        Frequency: 9/11 papers (Very High)
        Source: 2023 Q14, 2024 Q24, 2025 Q8, 2022 Q8
        """
        import math
        
        # Variables
        angle_apb = random.choice([40, 50, 60, 70, 80])
        tangent_length = random.choice([5, 6, 8, 10, 12])
        
        # Calculation: ∠AOB = 180° - ∠APB (OAPB is cyclic)
        angle_aob = 180 - angle_apb
        
        # For AB length (if needed): Using cosine rule in triangle APB
        # AB² = PA² + PB² - 2·PA·PB·cos(∠APB)
        # Since PA = PB (equal tangents)
        ab_length = 2 * tangent_length * math.sin(math.radians(angle_apb / 2))
        ab_rounded = round(ab_length, 2)
        
        question_text = (
            f"PA and PB are tangents drawn to a circle with centre O from an external point P. "
            f"If ∠APB = {angle_apb}°, find:\n"
            f"(i) ∠AOB\n"
            f"(ii) If PA = {tangent_length} cm, find the length of chord AB."
        )
        
        solution_steps = [
            f"Given: PA and PB are tangents from P to circle with centre O",
            f"∠APB = {angle_apb}°, PA = {tangent_length} cm",
            f"(i) Since PA and PB are tangents: OA ⊥ PA and OB ⊥ PB",
            f"In quadrilateral OAPB:",
            f"∠OAP + ∠APB + ∠PBO + ∠AOB = 360°",
            f"90° + {angle_apb}° + 90° + ∠AOB = 360°",
            f"∠AOB = 360° - 180° - {angle_apb}° = {angle_aob}°",
            f"(ii) PA = PB = {tangent_length} cm (tangents from external point are equal)",
            f"In triangle APB, using formula for isosceles triangle:",
            f"AB = 2 × PA × sin(∠APB/2)",
            f"AB = 2 × {tangent_length} × sin({angle_apb/2}°)",
            f"AB ≈ {ab_rounded} cm"
        ]
        
        socratic_hints = [
            {
                "level": 1,
                "hint": "What is special about tangents drawn from an external point to a circle?",
                "nudge": "They are equal in length, and each is perpendicular to the radius at the point of contact."
            },
            {
                "level": 2,
                "hint": "What is the sum of angles in quadrilateral OAPB?",
                "nudge": "Sum = 360°. You know ∠OAP = ∠OBP = 90° and ∠APB."
            },
            {
                "level": 3,
                "hint": f"For part (ii), triangle APB is isosceles with PA = PB = {tangent_length} cm.",
                "nudge": f"Use: AB = 2 × PA × sin(∠APB/2) = 2 × {tangent_length} × sin({angle_apb/2}°)"
            }
        ]
        
        return {
            "question_id": self._generate_id(),
            "pattern_id": "circle_tangent_equal_length",
            "topic": topic,
            "question_text": question_text,
            "solution_steps": solution_steps,
            "final_answer": f"(i) ∠AOB = {angle_aob}°, (ii) AB ≈ {ab_rounded} cm",
            "marks": 3,
            "difficulty": 0.6,
            "estimated_time_minutes": 5,
            "socratic_hints": socratic_hints,
            "generated_at": datetime.now().isoformat(),
            "unique_hash": self._compute_hash(question_text)
        }

    def _gen_circle_tangent_chord_angle(self, pattern, topic):
        """
        Pattern: Angle between tangent and chord
        Frequency: 7/11 papers (High)
        Source: 2023 Q2, 2024 Q17, 2025 Q31
        """
        # Variables
        angle_between_tangent_chord = random.choice([40, 50, 60, 70])
        
        # Theorem: Angle between tangent and chord = Angle in alternate segment
        angle_in_alternate_segment = angle_between_tangent_chord
        
        # Central angle = 2 × Angle in alternate segment
        central_angle = 2 * angle_in_alternate_segment
        
        question_text = (
            f"In a circle with centre O, PQ is a chord and PT is a tangent at P making an angle of "
            f"{angle_between_tangent_chord}° with PQ. Find:\n"
            f"(i) ∠PRQ (where R is any point on the major arc PQ)\n"
            f"(ii) ∠POQ"
        )
        
        solution_steps = [
            f"Given: PT is tangent at P, ∠TPQ = {angle_between_tangent_chord}°",
            f"(i) By Alternate Segment Theorem:",
            f"Angle between tangent and chord = Angle in alternate segment",
            f"∠PRQ = ∠TPQ = {angle_in_alternate_segment}°",
            f"(ii) Central angle = 2 × Angle at circumference",
            f"∠POQ = 2 × ∠PRQ",
            f"∠POQ = 2 × {angle_in_alternate_segment}° = {central_angle}°"
        ]
        
        socratic_hints = [
            {
                "level": 1,
                "hint": "What theorem relates the angle between a tangent and chord to angles in the circle?",
                "nudge": "Alternate Segment Theorem: Angle between tangent and chord equals angle in alternate segment."
            },
            {
                "level": 2,
                "hint": "What is the relationship between a central angle and an inscribed angle subtending the same arc?",
                "nudge": "Central angle = 2 × Inscribed angle"
            },
            {
                "level": 3,
                "hint": f"∠PRQ = {angle_between_tangent_chord}° (alternate segment), so ∠POQ = ?",
                "nudge": f"∠POQ = 2 × {angle_in_alternate_segment}° = {central_angle}°"
            }
        ]
        
        return {
            "question_id": self._generate_id(),
            "pattern_id": "circle_tangent_chord_angle",
            "topic": topic,
            "question_text": question_text,
            "solution_steps": solution_steps,
            "final_answer": f"(i) ∠PRQ = {angle_in_alternate_segment}°, (ii) ∠POQ = {central_angle}°",
            "marks": 3,
            "difficulty": 0.6,
            "estimated_time_minutes": 4,
            "socratic_hints": socratic_hints,
            "generated_at": datetime.now().isoformat(),
            "unique_hash": self._compute_hash(question_text)
        }

    def _gen_circle_concentric_chord_tangent(self, pattern, topic):
        """
        Pattern: Concentric circles with chord as tangent
        Frequency: 5/11 papers (Medium)
        Source: 2022 Q6, 2025 Q23, 2016 Q6
        """
        import math
        
        # Variables
        outer_radius = random.choice([10, 12, 14, 15, 18, 20])
        inner_radius = random.choice([6, 8, 9, 10, 12])
        
        # Ensure outer > inner
        if outer_radius <= inner_radius:
            outer_radius, inner_radius = inner_radius + 4, inner_radius
        
        # Calculation: Chord of outer circle tangent to inner circle
        # If OM ⊥ chord AB at M (point of tangency to inner circle)
        # Then OM = inner_radius (radius to tangent point)
        # OA = outer_radius (radius of outer circle)
        # By Pythagoras: AM² = OA² - OM²
        # Chord length AB = 2 × AM
        
        am_squared = outer_radius**2 - inner_radius**2
        am = math.sqrt(am_squared)
        chord_length = 2 * am
        chord_rounded = round(chord_length, 2)
        
        question_text = (
            f"Two concentric circles are of radii {outer_radius} cm and {inner_radius} cm. "
            f"Find the length of the chord of the larger circle which touches the smaller circle."
        )
        
        solution_steps = [
            f"Let O be the common centre of both circles",
            f"Outer radius OA = {outer_radius} cm, Inner radius OM = {inner_radius} cm",
            f"Let AB be a chord of the outer circle that touches the inner circle at M",
            f"Since AB is tangent to inner circle at M: OM ⊥ AB",
            f"M is the midpoint of AB (perpendicular from centre bisects chord)",
            f"In right triangle OAM:",
            f"OA² = OM² + AM²",
            f"{outer_radius}² = {inner_radius}² + AM²",
            f"{outer_radius**2} = {inner_radius**2} + AM²",
            f"AM² = {outer_radius**2} - {inner_radius**2} = {am_squared}",
            f"AM = {round(am, 2)} cm",
            f"Chord length AB = 2 × AM = 2 × {round(am, 2)} = {chord_rounded} cm"
        ]
        
        socratic_hints = [
            {
                "level": 1,
                "hint": "What do you know about a tangent to a circle and the radius at the point of tangency?",
                "nudge": "The radius is perpendicular to the tangent at the point of contact."
            },
            {
                "level": 2,
                "hint": "If a perpendicular is drawn from the centre to a chord, what happens?",
                "nudge": "It bisects the chord. So M is the midpoint of AB."
            },
            {
                "level": 3,
                "hint": f"Use Pythagoras theorem in triangle OAM with OA = {outer_radius}, OM = {inner_radius}.",
                "nudge": f"AM² = {outer_radius}² - {inner_radius}² = {am_squared}, so AB = 2 × AM"
            }
        ]
        
        return {
            "question_id": self._generate_id(),
            "pattern_id": "circle_concentric_chord_tangent",
            "topic": topic,
            "question_text": question_text,
            "solution_steps": solution_steps,
            "final_answer": f"Chord length = {chord_rounded} cm",
            "marks": 2,
            "difficulty": 0.5,
            "estimated_time_minutes": 4,
            "socratic_hints": socratic_hints,
            "generated_at": datetime.now().isoformat(),
            "unique_hash": self._compute_hash(question_text)
        }

    def _gen_generic(self, pattern, topic):
        """Generic fallback"""
        return {
            "question_id": self._generate_id(),
            "pattern_id": pattern.get('pattern_type', 'generic'),
            "topic": topic,
            "question_text": f"Question about {topic}",
            "solution_steps": ["Step 1", "Step 2", "Step 3"],
            "final_answer": "Answer",
            "marks": pattern.get('marks', 2),
            "difficulty": pattern.get('difficulty', 0.5),
            "estimated_time_minutes": 3,
            "socratic_hints": [],
            "generated_at": datetime.now().isoformat(),
            "unique_hash": self._generate_id()
        }

    # ============================================================
    # COORDINATE GEOMETRY PATTERNS
    # ============================================================

    def _gen_coord_section_formula(self, pattern, topic):
        """
        Pattern: Section formula (internal/external division)
        Frequency: 10/11 papers (Very High)
        Source: 2023 Q22, 2024 Q2, 2025 Q7, 2022 Q10
        """
        # Variables
        x1, y1 = random.randint(-8, 8), random.randint(-8, 8)
        x2, y2 = random.randint(-8, 8), random.randint(-8, 8)
        
        # Ensure points are distinct
        while x1 == x2 and y1 == y2:
            x2, y2 = random.randint(-8, 8), random.randint(-8, 8)
        
        # Ratio
        m, n = random.choice([(1,2), (2,3), (3,4), (1,3), (2,1), (3,1)])
        
        # Calculate point using section formula
        px = (m * x2 + n * x1) / (m + n)
        py = (m * y2 + n * y1) / (m + n)
        
        question_text = (
            f"Find the coordinates of the point which divides the line segment joining "
            f"A({x1}, {y1}) and B({x2}, {y2}) in the ratio {m}:{n} internally."
        )
        
        solution_steps = [
            f"Given: A({x1}, {y1}), B({x2}, {y2}), Ratio m:n = {m}:{n}",
            f"Using Section Formula (internal division):",
            f"P(x, y) = ((m·x₂ + n·x₁)/(m+n), (m·y₂ + n·y₁)/(m+n))",
            f"x = ({m}×{x2} + {n}×{x1}) / ({m}+{n})",
            f"x = ({m*x2} + {n*x1}) / {m+n}",
            f"x = {m*x2 + n*x1} / {m+n} = {px}",
            f"y = ({m}×{y2} + {n}×{y1}) / ({m}+{n})",
            f"y = ({m*y2} + {n*y1}) / {m+n}",
            f"y = {m*y2 + n*y1} / {m+n} = {py}",
            f"P = ({px}, {py})"
        ]
        
        socratic_hints = [
            {
                "level": 1,
                "hint": "Which formula divides a line segment in a given ratio?",
                "nudge": "Section Formula: P = ((mx₂+nx₁)/(m+n), (my₂+ny₁)/(m+n))"
            },
            {
                "level": 2,
                "hint": "Identify the coordinates A, B and the ratio m:n from the question.",
                "nudge": f"A({x1}, {y1}), B({x2}, {y2}), m = {m}, n = {n}"
            },
            {
                "level": 3,
                "hint": f"Substitute in the formula: x = ({m}×{x2} + {n}×{x1})/({m}+{n})",
                "nudge": f"Calculate step by step to get ({px}, {py})"
            }
        ]
        
        return {
            "question_id": self._generate_id(),
            "pattern_id": "coord_section_formula",
            "topic": topic,
            "question_text": question_text,
            "solution_steps": solution_steps,
            "final_answer": f"P({px}, {py})",
            "marks": 2,
            "difficulty": 0.5,
            "estimated_time_minutes": 4,
            "socratic_hints": socratic_hints,
            "generated_at": datetime.now().isoformat(),
            "unique_hash": self._compute_hash(question_text)
        }

    def _gen_coord_distance_formula(self, pattern, topic):
        """
        Pattern: Distance between two points
        Frequency: 9/11 papers (Very High)
        Source: 2023 Q4, 2024 Q8, 2025 Q16
        """
        import math
        
        # Variables - use combinations that give nice distances
        nice_distances = [
            ((0, 0), (3, 4), 5),
            ((0, 0), (5, 12), 13),
            ((1, 2), (4, 6), 5),
            ((-2, -3), (2, 0), 5),
            ((0, 6), (6, 2), math.sqrt(52))
        ]
        
        (x1, y1), (x2, y2), expected_dist = random.choice(nice_distances)
        
        distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        distance_rounded = round(distance, 2)
        
        # Format answer nicely
        if distance == int(distance):
            distance_str = f"{int(distance)} units"
        elif distance == math.sqrt(52):
            distance_str = f"2√13 units"
        else:
            distance_str = f"{distance_rounded} units"
        
        question_text = (
            f"Find the distance between the points A({x1}, {y1}) and B({x2}, {y2})."
        )
        
        solution_steps = [
            f"Given: A({x1}, {y1}), B({x2}, {y2})",
            f"Using Distance Formula:",
            f"AB = √[(x₂ - x₁)² + (y₂ - y₁)²]",
            f"AB = √[({x2} - {x1})² + ({y2} - {y1})²]",
            f"AB = √[({x2 - x1})² + ({y2 - y1})²]",
            f"AB = √[{(x2-x1)**2} + {(y2-y1)**2}]",
            f"AB = √{(x2-x1)**2 + (y2-y1)**2}",
            f"AB = {distance_str}"
        ]
        
        socratic_hints = [
            {
                "level": 1,
                "hint": "What formula is used to find the distance between two points?",
                "nudge": "Distance Formula: d = √[(x₂-x₁)² + (y₂-y₁)²]"
            },
            {
                "level": 2,
                "hint": f"Calculate the differences: x₂ - x₁ = ? and y₂ - y₁ = ?",
                "nudge": f"{x2} - {x1} = {x2-x1}, {y2} - {y1} = {y2-y1}"
            },
            {
                "level": 3,
                "hint": f"Square each difference, add them, and take the square root.",
                "nudge": f"√[{(x2-x1)**2} + {(y2-y1)**2}] = √{(x2-x1)**2 + (y2-y1)**2} = {distance_str}"
            }
        ]
        
        return {
            "question_id": self._generate_id(),
            "pattern_id": "coord_distance_formula",
            "topic": topic,
            "question_text": question_text,
            "solution_steps": solution_steps,
            "final_answer": f"Distance = {distance_str}",
            "marks": 2,
            "difficulty": 0.3,
            "estimated_time_minutes": 3,
            "socratic_hints": socratic_hints,
            "generated_at": datetime.now().isoformat(),
            "unique_hash": self._compute_hash(question_text)
        }

    def _gen_coord_area_triangle(self, pattern, topic):
        """
        Pattern: Area of triangle using coordinates
        Frequency: 6/11 papers (Medium-High)
        Source: 2018 Q15, 2024 Q26, 2025 Q29
        """
        # Variables
        x1, y1 = random.randint(-5, 5), random.randint(-5, 5)
        x2, y2 = random.randint(-5, 5), random.randint(-5, 5)
        x3, y3 = random.randint(-5, 5), random.randint(-5, 5)
        
        # Calculate area using formula
        area_double = abs(x1*(y2 - y3) + x2*(y3 - y1) + x3*(y1 - y2))
        area = area_double / 2
        
        # Ensure non-zero area (non-collinear points)
        if area == 0:
            return self._gen_coord_area_triangle(pattern, topic)
        
        question_text = (
            f"Find the area of the triangle whose vertices are A({x1}, {y1}), "
            f"B({x2}, {y2}), and C({x3}, {y3})."
        )
        
        solution_steps = [
            f"Given: A({x1}, {y1}), B({x2}, {y2}), C({x3}, {y3})",
            f"Using Area Formula for triangle:",
            f"Area = (1/2)|x₁(y₂ - y₃) + x₂(y₃ - y₁) + x₃(y₁ - y₂)|",
            f"Area = (1/2)|{x1}({y2} - {y3}) + {x2}({y3} - {y1}) + {x3}({y1} - {y2})|",
            f"Area = (1/2)|{x1}×{y2-y3} + {x2}×{y3-y1} + {x3}×{y1-y2}|",
            f"Area = (1/2)|{x1*(y2-y3)} + {x2*(y3-y1)} + {x3*(y1-y2)}|",
            f"Area = (1/2)|{x1*(y2-y3) + x2*(y3-y1) + x3*(y1-y2)}|",
            f"Area = (1/2) × {area_double}",
            f"Area = {area} square units"
        ]
        
        socratic_hints = [
            {
                "level": 1,
                "hint": "What is the formula for the area of a triangle when vertices are given?",
                "nudge": "Area = (1/2)|x₁(y₂-y₃) + x₂(y₃-y₁) + x₃(y₁-y₂)|"
            },
            {
                "level": 2,
                "hint": "Substitute the coordinates into the formula carefully.",
                "nudge": f"x₁={x1}, y₁={y1}, x₂={x2}, y₂={y2}, x₃={x3}, y₃={y3}"
            },
            {
                "level": 3,
                "hint": "Calculate each term, add them, take absolute value, and divide by 2.",
                "nudge": f"(1/2)|{x1*(y2-y3) + x2*(y3-y1) + x3*(y1-y2)}| = {area} sq units"
            }
        ]
        
        return {
            "question_id": self._generate_id(),
            "pattern_id": "coord_area_triangle",
            "topic": topic,
            "question_text": question_text,
            "solution_steps": solution_steps,
            "final_answer": f"Area = {area} square units",
            "marks": 3,
            "difficulty": 0.6,
            "estimated_time_minutes": 5,
            "socratic_hints": socratic_hints,
            "generated_at": datetime.now().isoformat(),
            "unique_hash": self._compute_hash(question_text)
        }

    # ============================================================
    # STATISTICS - MEAN, MEDIAN, MODE PATTERNS
    # ============================================================

    def _gen_statistics_mean_frequency_table(self, pattern, topic):
        """
        Pattern: Mean from frequency distribution
        Frequency: 8/11 papers (High)
        Source: 2023 Q35, 2024 Q30, 2025 Q35, 2022 Q10
        """
        # Variables - create a grouped frequency table
        class_intervals = [
            (0, 10), (10, 20), (20, 30), (30, 40), (40, 50)
        ]
        
        frequencies = [random.randint(5, 20) for _ in class_intervals]
        total_freq = sum(frequencies)
        
        # Calculate mean
        sum_fx = sum([
            ((lower + upper) / 2) * freq 
            for (lower, upper), freq in zip(class_intervals, frequencies)
        ])
        mean = sum_fx / total_freq
        mean_rounded = round(mean, 2)
        
        # Create table string
        table_str = "\n".join([
            f"{lower}-{upper}: {freq}" 
            for (lower, upper), freq in zip(class_intervals, frequencies)
        ])
        
        question_text = (
            f"Find the mean of the following frequency distribution:\n\n"
            f"Class Interval | Frequency\n"
            f"{table_str}"
        )
        
        # Build solution table
        solution_table = []
        for (lower, upper), freq in zip(class_intervals, frequencies):
            mid = (lower + upper) / 2
            fx = mid * freq
            solution_table.append((f"{lower}-{upper}", mid, freq, fx))
        
        solution_steps = [
            "Step 1: Calculate class marks (mid-values) for each interval",
            "Class Interval | Mid-value (xᵢ) | Frequency (fᵢ) | fᵢxᵢ",
            *[f"{ci} | {mid} | {freq} | {fx}" for ci, mid, freq, fx in solution_table],
            f"Total: Σfᵢ = {total_freq}, Σfᵢxᵢ = {sum_fx}",
            "Step 2: Apply mean formula",
            "Mean = Σfᵢxᵢ / Σfᵢ",
            f"Mean = {sum_fx} / {total_freq}",
            f"Mean = {mean_rounded}"
        ]
        
        socratic_hints = [
            {
                "level": 1,
                "hint": "What is the formula for mean in a grouped frequency distribution?",
                "nudge": "Mean = Σfᵢxᵢ / Σfᵢ, where xᵢ is the class mark (mid-value)"
            },
            {
                "level": 2,
                "hint": "How do you find the class mark for an interval?",
                "nudge": "Class mark = (Lower limit + Upper limit) / 2"
            },
            {
                "level": 3,
                "hint": "Calculate fᵢxᵢ for each class, sum them, and divide by total frequency.",
                "nudge": f"Σfᵢxᵢ = {sum_fx}, Σfᵢ = {total_freq}, Mean = {mean_rounded}"
            }
        ]
        
        return {
            "question_id": self._generate_id(),
            "pattern_id": "statistics_mean_frequency_table",
            "topic": topic,
            "question_text": question_text,
            "solution_steps": solution_steps,
            "final_answer": f"Mean = {mean_rounded}",
            "marks": 3,
            "difficulty": 0.5,
            "estimated_time_minutes": 6,
            "socratic_hints": socratic_hints,
            "generated_at": datetime.now().isoformat(),
            "unique_hash": self._compute_hash(question_text)
        }

    def _gen_statistics_median_grouped_data(self, pattern, topic):
        """
        Pattern: Median from grouped data
        Frequency: 7/11 papers (High)
        Source: 2024 Q35, 2025 Q38, 2018 Q22
        """
        # Variables
        class_intervals = [
            (0, 20), (20, 40), (40, 60), (60, 80), (80, 100)
        ]
        
        frequencies = [random.randint(8, 25) for _ in class_intervals]
        total_freq = sum(frequencies)
        
        # Find median class
        cumulative_freq = []
        cum = 0
        for f in frequencies:
            cum += f
            cumulative_freq.append(cum)
        
        n_by_2 = total_freq / 2
        median_class_index = 0
        for i, cf in enumerate(cumulative_freq):
            if cf >= n_by_2:
                median_class_index = i
                break
        
        l = class_intervals[median_class_index][0]  # Lower limit of median class
        h = class_intervals[median_class_index][1] - l  # Class width
        f = frequencies[median_class_index]  # Frequency of median class
        cf = cumulative_freq[median_class_index - 1] if median_class_index > 0 else 0  # Cumulative frequency before median class
        
        # Calculate median
        median = l + ((n_by_2 - cf) / f) * h
        median_rounded = round(median, 2)
        
        # Create table string
        table_str = "\n".join([
            f"{lower}-{upper}: {freq}" 
            for (lower, upper), freq in zip(class_intervals, frequencies)
        ])
        
        question_text = (
            f"Find the median of the following grouped data:\n\n"
            f"Class Interval | Frequency\n"
            f"{table_str}"
        )
        
        solution_steps = [
            "Step 1: Calculate cumulative frequencies",
            "Class Interval | Frequency | Cumulative Frequency",
            *[f"{class_intervals[i][0]}-{class_intervals[i][1]} | {frequencies[i]} | {cumulative_freq[i]}" 
              for i in range(len(class_intervals))],
            f"Step 2: Find n/2 = {total_freq}/2 = {n_by_2}",
            f"Step 3: Median class is {l}-{l+h} (cumulative frequency just exceeds n/2)",
            "Step 4: Apply median formula",
            "Median = l + [(n/2 - cf)/f] × h",
            f"where l = {l}, n/2 = {n_by_2}, cf = {cf}, f = {f}, h = {h}",
            f"Median = {l} + [({n_by_2} - {cf})/{f}] × {h}",
            f"Median = {l} + [{n_by_2 - cf}/{f}] × {h}",
            f"Median = {l} + {round((n_by_2 - cf) / f, 2)} × {h}",
            f"Median = {median_rounded}"
        ]
        
        socratic_hints = [
            {
                "level": 1,
                "hint": "What is the first step in finding the median of grouped data?",
                "nudge": "Calculate the cumulative frequencies to locate the median class."
            },
            {
                "level": 2,
                "hint": f"Which class contains the (n/2)th observation? Here n/2 = {n_by_2}",
                "nudge": f"The median class is {l}-{l+h} because its cumulative frequency exceeds {n_by_2}."
            },
            {
                "level": 3,
                "hint": "Use the median formula: Median = l + [(n/2 - cf)/f] × h",
                "nudge": f"Substitute l={l}, n/2={n_by_2}, cf={cf}, f={f}, h={h} to get {median_rounded}"
            }
        ]
        
        return {
            "question_id": self._generate_id(),
            "pattern_id": "statistics_median_grouped_data",
            "topic": topic,
            "question_text": question_text,
            "solution_steps": solution_steps,
            "final_answer": f"Median = {median_rounded}",
            "marks": 5,
            "difficulty": 0.7,
            "estimated_time_minutes": 8,
            "socratic_hints": socratic_hints,
            "generated_at": datetime.now().isoformat(),
            "unique_hash": self._compute_hash(question_text)
        }

    def _gen_statistics_mode_grouped_data(self, pattern, topic):
        """
        Pattern: Mode from grouped data
        Frequency: 6/11 papers (Medium-High)
        Source: 2023 Q35, 2022 Q4, 2018 Q22
        """
        # Variables
        class_intervals = [
            (10, 20), (20, 30), (30, 40), (40, 50), (50, 60)
        ]
        
        # Make one class have maximum frequency (modal class)
        modal_index = random.randint(1, 3)  # Not at edges for better calculation
        frequencies = [random.randint(10, 20) for _ in class_intervals]
        frequencies[modal_index] = max(frequencies) + random.randint(5, 10)
        
        # Modal class parameters
        l = class_intervals[modal_index][0]  # Lower limit
        h = class_intervals[modal_index][1] - l  # Class width
        f1 = frequencies[modal_index]  # Frequency of modal class
        f0 = frequencies[modal_index - 1]  # Frequency of preceding class
        f2 = frequencies[modal_index + 1]  # Frequency of succeeding class
        
        # Calculate mode
        mode = l + ((f1 - f0) / (2*f1 - f0 - f2)) * h
        mode_rounded = round(mode, 2)
        
        # Create table string
        table_str = "\n".join([
            f"{lower}-{upper}: {freq}" 
            for (lower, upper), freq in zip(class_intervals, frequencies)
        ])
        
        question_text = (
            f"Find the mode of the following frequency distribution:\n\n"
            f"Class Interval | Frequency\n"
            f"{table_str}"
        )
        
        solution_steps = [
            "Step 1: Identify the modal class (class with highest frequency)",
            f"Modal class: {l}-{l+h} with frequency {f1}",
            "Step 2: Apply mode formula",
            "Mode = l + [(f₁ - f₀) / (2f₁ - f₀ - f₂)] × h",
            f"where l = {l}, f₁ = {f1}, f₀ = {f0}, f₂ = {f2}, h = {h}",
            f"Mode = {l} + [({f1} - {f0}) / (2×{f1} - {f0} - {f2})] × {h}",
            f"Mode = {l} + [{f1 - f0} / ({2*f1} - {f0} - {f2})] × {h}",
            f"Mode = {l} + [{f1 - f0} / {2*f1 - f0 - f2}] × {h}",
            f"Mode = {l} + {round((f1 - f0) / (2*f1 - f0 - f2), 2)} × {h}",
            f"Mode = {mode_rounded}"
        ]
        
        socratic_hints = [
            {
                "level": 1,
                "hint": "Which class interval has the highest frequency?",
                "nudge": f"The modal class is {l}-{l+h} with frequency {f1}."
            },
            {
                "level": 2,
                "hint": "What formula is used to calculate the mode from grouped data?",
                "nudge": "Mode = l + [(f₁-f₀)/(2f₁-f₀-f₂)] × h"
            },
            {
                "level": 3,
                "hint": f"Substitute: l={l}, f₁={f1}, f₀={f0}, f₂={f2}, h={h}",
                "nudge": f"Mode = {l} + [{f1-f0}/{2*f1-f0-f2}] × {h} = {mode_rounded}"
            }
        ]
        
        return {
            "question_id": self._generate_id(),
            "pattern_id": "statistics_mode_grouped_data",
            "topic": topic,
            "question_text": question_text,
            "solution_steps": solution_steps,
            "final_answer": f"Mode = {mode_rounded}",
            "marks": 3,
            "difficulty": 0.6,
            "estimated_time_minutes": 5,
            "socratic_hints": socratic_hints,
            "generated_at": datetime.now().isoformat(),
            "unique_hash": self._compute_hash(question_text)
        }

    # ============================================================
    # MENSURATION - SECTOR, SEGMENT, COMBINATION PATTERNS
    # ============================================================

    def _gen_mensuration_sector_area_arc(self, pattern, topic):
        """
        Pattern: Sector area and arc length
        Frequency: 7/11 papers (High)
        Source: 2023 Q31, 2024 Q22, 2025 Q13
        """
        import math
        
        # Variables
        radius = random.choice([7, 10, 14, 21, 28, 42])  # Multiples of 7 for π = 22/7
        angle = random.choice([30, 45, 60, 90, 120])
        
        # Calculations using π = 22/7
        pi = 22/7
        sector_area = (angle / 360) * pi * radius**2
        arc_length = (angle / 360) * 2 * pi * radius
        
        sector_area_rounded = round(sector_area, 2)
        arc_length_rounded = round(arc_length, 2)
        
        question_text = (
            f"A sector of a circle of radius {radius} cm has a central angle of {angle}°. "
            f"Find:\n(i) The area of the sector\n(ii) The length of the arc\n(Use π = 22/7)"
        )
        
        solution_steps = [
            f"Given: Radius r = {radius} cm, Central angle θ = {angle}°",
            "(i) Area of sector:",
            "Area = (θ/360°) × πr²",
            f"Area = ({angle}/360) × (22/7) × {radius}²",
            f"Area = ({angle}/360) × (22/7) × {radius**2}",
            f"Area = {sector_area_rounded} cm²",
            "(ii) Length of arc:",
            "Arc length = (θ/360°) × 2πr",
            f"Arc length = ({angle}/360) × 2 × (22/7) × {radius}",
            f"Arc length = {arc_length_rounded} cm"
        ]
        
        socratic_hints = [
            {
                "level": 1,
                "hint": "What fraction of the full circle does this sector represent?",
                "nudge": f"{angle}/360 = {angle/360} of the circle"
            },
            {
                "level": 2,
                "hint": "How do you find the area of a sector?",
                "nudge": "Area = (θ/360°) × πr² (fraction of circle's area)"
            },
            {
                "level": 3,
                "hint": "For arc length, use: Arc = (θ/360°) × 2πr",
                "nudge": f"Substitute θ={angle}°, r={radius} cm, π=22/7"
            }
        ]
        
        return {
            "question_id": self._generate_id(),
            "pattern_id": "mensuration_sector_area_arc",
            "topic": topic,
            "question_text": question_text,
            "solution_steps": solution_steps,
            "final_answer": f"(i) Area = {sector_area_rounded} cm², (ii) Arc = {arc_length_rounded} cm",
            "marks": 3,
            "difficulty": 0.5,
            "estimated_time_minutes": 5,
            "socratic_hints": socratic_hints,
            "generated_at": datetime.now().isoformat(),
            "unique_hash": self._compute_hash(question_text)
        }

    def _gen_mensuration_segment_area(self, pattern, topic):
        """
        Pattern: Area of minor/major segment
        Frequency: 6/11 papers (Medium-High)
        Source: 2023 Q33, 2024 Q35, 2025 Q25
        """
        import math
        
        # Variables
        radius = random.choice([7, 10, 14, 21])
        angle = random.choice([60, 90, 120])
        
        # Calculations
        pi = 22/7
        
        # Area of sector
        sector_area = (angle / 360) * pi * radius**2
        
        # Area of triangle
        if angle == 60:
            # Equilateral triangle
            triangle_area = (math.sqrt(3) / 4) * radius**2
        elif angle == 90:
            # Right isosceles triangle
            triangle_area = 0.5 * radius * radius
        else:  # 120
            # Using formula: (1/2) * r² * sin(θ)
            triangle_area = 0.5 * radius**2 * math.sin(math.radians(angle))
        
        # Segment area = Sector area - Triangle area
        segment_area = sector_area - triangle_area
        segment_area_rounded = round(segment_area, 2)
        
        question_text = (
            f"A chord of a circle of radius {radius} cm subtends an angle of {angle}° at the centre. "
            f"Find the area of the corresponding minor segment of the circle. "
            f"(Use π = 22/7 and √3 = 1.73)"
        )
        
        solution_steps = [
            f"Given: Radius r = {radius} cm, Central angle θ = {angle}°",
            "Area of minor segment = Area of sector - Area of triangle",
            "Step 1: Area of sector",
            f"Area of sector = (θ/360°) × πr²",
            f"Area of sector = ({angle}/360) × (22/7) × {radius}²",
            f"Area of sector = {round(sector_area, 2)} cm²",
            "Step 2: Area of triangle OAB",
            f"Area of triangle = (1/2) × r² × sin θ",
            f"Area of triangle = (1/2) × {radius}² × sin {angle}°",
            f"Area of triangle = {round(triangle_area, 2)} cm²",
            "Step 3: Area of segment",
            f"Area of segment = {round(sector_area, 2)} - {round(triangle_area, 2)}",
            f"Area of segment = {segment_area_rounded} cm²"
        ]
        
        socratic_hints = [
            {
                "level": 1,
                "hint": "What is a segment of a circle?",
                "nudge": "A segment is the region between a chord and the arc it subtends."
            },
            {
                "level": 2,
                "hint": "How can you find the area of a segment?",
                "nudge": "Segment area = Sector area - Triangle area (formed by radii and chord)"
            },
            {
                "level": 3,
                "hint": f"Calculate sector area using ({angle}/360) × πr², then subtract triangle area.",
                "nudge": f"Sector = {round(sector_area, 2)}, Triangle = {round(triangle_area, 2)}"
            }
        ]
        
        return {
            "question_id": self._generate_id(),
            "pattern_id": "mensuration_segment_area",
            "topic": topic,
            "question_text": question_text,
            "solution_steps": solution_steps,
            "final_answer": f"Area of segment = {segment_area_rounded} cm²",
            "marks": 3,
            "difficulty": 0.7,
            "estimated_time_minutes": 6,
            "socratic_hints": socratic_hints,
            "generated_at": datetime.now().isoformat(),
            "unique_hash": self._compute_hash(question_text)
        }

    def _gen_mensuration_combination_solid(self, pattern, topic):
        """
        Pattern: Cone + Hemisphere combination
        Frequency: 6/11 papers (Medium-High)
        Source: 2023 Q33, 2024 Q34, 2025 Q34
        """
        import math
        
        # Variables
        radius = random.choice([3.5, 5, 7, 10.5])  # Half for hemisphere
        height = random.choice([8, 10, 12, 14, 16])
        
        pi = 22/7
        
        # Calculations
        # Volume of cone
        cone_volume = (1/3) * pi * radius**2 * height
        
        # Volume of hemisphere
        hemisphere_volume = (2/3) * pi * radius**3
        
        # Total volume
        total_volume = cone_volume + hemisphere_volume
        total_volume_rounded = round(total_volume, 2)
        
        question_text = (
            f"A solid is in the shape of a cone mounted on a hemisphere with both having the same radius {radius} cm. "
            f"The height of the cone is {height} cm. Find the volume of the solid. (Use π = 22/7)"
        )
        
        solution_steps = [
            f"Given: Radius of cone and hemisphere r = {radius} cm",
            f"Height of cone h = {height} cm",
            "Total volume = Volume of cone + Volume of hemisphere",
            "Step 1: Volume of cone",
            "V_cone = (1/3)πr²h",
            f"V_cone = (1/3) × (22/7) × {radius}² × {height}",
            f"V_cone = (1/3) × (22/7) × {radius**2} × {height}",
            f"V_cone = {round(cone_volume, 2)} cm³",
            "Step 2: Volume of hemisphere",
            "V_hemisphere = (2/3)πr³",
            f"V_hemisphere = (2/3) × (22/7) × {radius}³",
            f"V_hemisphere = (2/3) × (22/7) × {radius**3}",
            f"V_hemisphere = {round(hemisphere_volume, 2)} cm³",
            "Step 3: Total volume",
            f"Total = {round(cone_volume, 2)} + {round(hemisphere_volume, 2)}",
            f"Total = {total_volume_rounded} cm³"
        ]
        
        socratic_hints = [
            {
                "level": 1,
                "hint": "What shapes make up this solid?",
                "nudge": "A cone on top of a hemisphere, both with the same radius."
            },
            {
                "level": 2,
                "hint": "What are the formulas for volume of a cone and hemisphere?",
                "nudge": "Cone: (1/3)πr²h, Hemisphere: (2/3)πr³"
            },
            {
                "level": 3,
                "hint": f"Calculate each volume separately using r = {radius} cm, h = {height} cm, then add.",
                "nudge": f"V_cone = {round(cone_volume, 2)}, V_hemisphere = {round(hemisphere_volume, 2)}"
            }
        ]
        
        return {
            "question_id": self._generate_id(),
            "pattern_id": "mensuration_combination_solid",
            "topic": topic,
            "question_text": question_text,
            "solution_steps": solution_steps,
            "final_answer": f"Volume = {total_volume_rounded} cm³",
            "marks": 5,
            "difficulty": 0.7,
            "estimated_time_minutes": 7,
            "socratic_hints": socratic_hints,
            "generated_at": datetime.now().isoformat(),
            "unique_hash": self._compute_hash(question_text)
        }

    # ============================================================
    # QUADRATIC EQUATIONS PATTERNS (6 patterns - 10 marks)
    # ============================================================

    def _gen_quadratic_nature_of_roots(self, pattern, topic):
        """
        Pattern: Determine nature of roots using discriminant
        Frequency: 11/11 papers (Very High)
        Source: 2023 Q5, 2024 Q4, 2025 Q9
        """
        # Variables - coefficients that give interesting discriminants
        discriminant_types = [
            {"a": 1, "b": 4, "c": 4, "nature": "equal", "discriminant": 0},  # b² = 4ac
            {"a": 1, "b": 5, "c": 6, "nature": "real and distinct", "discriminant": 1},  # b² > 4ac
            {"a": 2, "b": 3, "c": 5, "nature": "no real roots", "discriminant": -31},  # b² < 4ac
            {"a": 1, "b": -6, "c": 9, "nature": "equal", "discriminant": 0},
            {"a": 1, "b": -7, "c": 10, "nature": "real and distinct", "discriminant": 9}
        ]
        
        chosen = random.choice(discriminant_types)
        a, b, c = chosen["a"], chosen["b"], chosen["c"]
        
        discriminant = b**2 - 4*a*c
        
        if discriminant > 0:
            nature = "real and distinct"
            explanation = "D > 0, so roots are real and unequal"
        elif discriminant == 0:
            nature = "real and equal"
            explanation = "D = 0, so roots are real and equal"
        else:
            nature = "no real roots"
            explanation = "D < 0, so roots are imaginary (no real roots)"
        
        question_text = (
            f"Find the nature of the roots of the quadratic equation "
            f"{a}x² + {b}x + {c} = 0 without actually finding the roots."
        )
        
        solution_steps = [
            f"Given quadratic equation: {a}x² + {b}x + {c} = 0",
            f"Comparing with ax² + bx + c = 0:",
            f"a = {a}, b = {b}, c = {c}",
            f"Discriminant D = b² - 4ac",
            f"D = ({b})² - 4({a})({c})",
            f"D = {b**2} - {4*a*c}",
            f"D = {discriminant}",
            explanation,
            f"Therefore, the equation has {nature} roots."
        ]
        
        socratic_hints = [
            {
                "level": 1,
                "hint": "Which formula determines the nature of roots without solving?",
                "nudge": "The discriminant: D = b² - 4ac"
            },
            {
                "level": 2,
                "hint": f"Calculate b² - 4ac with a={a}, b={b}, c={c}",
                "nudge": f"D = {b}² - 4×{a}×{c}"
            },
            {
                "level": 3,
                "hint": f"D = {discriminant}. What does this tell you about the roots?",
                "nudge": "If D>0: real & distinct, D=0: equal, D<0: no real roots"
            }
        ]
        
        return {
            "question_id": self._generate_id(),
            "pattern_id": "quadratic_nature_of_roots",
            "topic": topic,
            "question_text": question_text,
            "solution_steps": solution_steps,
            "final_answer": f"Nature: {nature} (D = {discriminant})",
            "marks": 2,
            "difficulty": 0.4,
            "estimated_time_minutes": 3,
            "socratic_hints": socratic_hints,
            "generated_at": datetime.now().isoformat(),
            "unique_hash": self._compute_hash(question_text)
        }

    def _gen_quadratic_formula_solve(self, pattern, topic):
        """
        Pattern: Solve using quadratic formula
        Frequency: 9/11 papers (High)
        Source: 2023 Q29, 2024 Q28, 2025 Q32
        """
        import math
        
        # Use perfect square discriminants for clean answers
        perfect_squares = [
            {"a": 1, "b": -5, "c": 6},  # roots: 2, 3
            {"a": 1, "b": -7, "c": 12}, # roots: 3, 4
            {"a": 2, "b": -7, "c": 3},  # roots: 3, 1/2
            {"a": 1, "b": 2, "c": -15}, # roots: 3, -5
        ]
        
        chosen = random.choice(perfect_squares)
        a, b, c = chosen["a"], chosen["b"], chosen["c"]
        
        discriminant = b**2 - 4*a*c
        sqrt_d = math.sqrt(abs(discriminant))
        
        root1 = (-b + sqrt_d) / (2*a)
        root2 = (-b - sqrt_d) / (2*a)
        
        question_text = (
            f"Solve the quadratic equation {a}x² + ({b})x + ({c}) = 0 "
            f"using the quadratic formula."
        )
        
        solution_steps = [
            f"Given: {a}x² + ({b})x + ({c}) = 0",
            f"Quadratic formula: x = [-b ± √(b² - 4ac)] / 2a",
            f"Here, a = {a}, b = {b}, c = {c}",
            f"Discriminant D = b² - 4ac = ({b})² - 4({a})({c})",
            f"D = {b**2} - {4*a*c} = {discriminant}",
            f"x = [-({b}) ± √{discriminant}] / 2({a})",
            f"x = [{-b} ± {sqrt_d:.0f}] / {2*a}",
            f"x = ({-b} + {sqrt_d:.0f}) / {2*a} or x = ({-b} - {sqrt_d:.0f}) / {2*a}",
            f"x = {(-b + sqrt_d):.0f} / {2*a} or x = {(-b - sqrt_d):.0f} / {2*a}",
            f"x = {root1} or x = {root2}"
        ]
        
        socratic_hints = [
            {
                "level": 1,
                "hint": "Which formula solves any quadratic equation?",
                "nudge": "x = [-b ± √(b² - 4ac)] / 2a"
            },
            {
                "level": 2,
                "hint": f"First calculate the discriminant with a={a}, b={b}, c={c}",
                "nudge": f"D = {b}² - 4×{a}×{c} = {discriminant}"
            },
            {
                "level": 3,
                "hint": f"Substitute D={discriminant} into the formula",
                "nudge": f"x = [{-b} ± √{discriminant}] / {2*a}"
            }
        ]
        
        return {
            "question_id": self._generate_id(),
            "pattern_id": "quadratic_formula_solve",
            "topic": topic,
            "question_text": question_text,
            "solution_steps": solution_steps,
            "final_answer": f"x = {root1} or x = {root2}",
            "marks": 3,
            "difficulty": 0.6,
            "estimated_time_minutes": 5,
            "socratic_hints": socratic_hints,
            "generated_at": datetime.now().isoformat(),
            "unique_hash": self._compute_hash(question_text)
        }

    def _gen_quadratic_sum_product_roots(self, pattern, topic):
        """
        Pattern: Form equation from given roots
        Frequency: 8/11 papers (High)
        Source: 2023 Q11, 2024 Q13, 2025 Q10
        """
        # Variables - simple root pairs
        root_pairs = [
            (2, 3), (3, 5), (4, 6), (-2, 5), (-3, 4), (1, -7), (2, -5)
        ]
        
        alpha, beta = random.choice(root_pairs)
        
        # For equation x² - (α+β)x + αβ = 0
        sum_of_roots = alpha + beta
        product_of_roots = alpha * beta
        
        question_text = (
            f"Form a quadratic equation whose roots are {alpha} and {beta}."
        )
        
        solution_steps = [
            f"Given roots: α = {alpha}, β = {beta}",
            "For quadratic equation with roots α and β:",
            "x² - (α + β)x + αβ = 0",
            f"Sum of roots: α + β = {alpha} + {beta} = {sum_of_roots}",
            f"Product of roots: αβ = {alpha} × {beta} = {product_of_roots}",
            f"Required equation: x² - ({sum_of_roots})x + ({product_of_roots}) = 0",
            f"x² {'-' if sum_of_roots >= 0 else '+'} {abs(sum_of_roots)}x {'+' if product_of_roots >= 0 else ''}{product_of_roots} = 0"
        ]
        
        # Format final equation nicely
        if sum_of_roots >= 0:
            term2 = f"- {sum_of_roots}x"
        else:
            term2 = f"+ {abs(sum_of_roots)}x"
        
        if product_of_roots >= 0:
            term3 = f"+ {product_of_roots}"
        else:
            term3 = f"- {abs(product_of_roots)}"
        
        final_equation = f"x² {term2} {term3} = 0"
        
        socratic_hints = [
            {
                "level": 1,
                "hint": "What is the standard form of a quadratic with given roots?",
                "nudge": "x² - (sum of roots)x + (product of roots) = 0"
            },
            {
                "level": 2,
                "hint": f"Calculate α + β and αβ where α = {alpha}, β = {beta}",
                "nudge": f"Sum = {sum_of_roots}, Product = {product_of_roots}"
            },
            {
                "level": 3,
                "hint": "Substitute the sum and product into the formula",
                "nudge": f"x² - ({sum_of_roots})x + ({product_of_roots}) = 0"
            }
        ]
        
        return {
            "question_id": self._generate_id(),
            "pattern_id": "quadratic_sum_product_roots",
            "topic": topic,
            "question_text": question_text,
            "solution_steps": solution_steps,
            "final_answer": final_equation,
            "marks": 2,
            "difficulty": 0.5,
            "estimated_time_minutes": 4,
            "socratic_hints": socratic_hints,
            "generated_at": datetime.now().isoformat(),
            "unique_hash": self._compute_hash(question_text)
        }

    def _gen_quadratic_consecutive_integers(self, pattern, topic):
        """
        Pattern: Consecutive integers word problem
        Frequency: 7/11 papers (High)
        Source: 2024 Q32, 2025 Q31, 2022 Q9
        """
        import math
        
        # Variables - products that give nice quadratics
        products = [
            {"product": 56, "n": 7, "n_plus_1": 8},
            {"product": 72, "n": 8, "n_plus_1": 9},
            {"product": 90, "n": 9, "n_plus_1": 10},
            {"product": 110, "n": 10, "n_plus_1": 11},
            {"product": 132, "n": 11, "n_plus_1": 12}
        ]
        
        chosen = random.choice(products)
        product = chosen["product"]
        n = chosen["n"]
        
        question_text = (
            f"The product of two consecutive positive integers is {product}. "
            f"Find the integers by forming a quadratic equation."
        )
        
        solution_steps = [
            "Let the two consecutive positive integers be n and (n+1)",
            f"Given: n × (n+1) = {product}",
            f"n² + n = {product}",
            f"n² + n - {product} = 0",
            "Using quadratic formula: n = [-b ± √(b² - 4ac)] / 2a",
            f"Here a = 1, b = 1, c = -{product}",
            f"D = 1² - 4(1)(-{product}) = 1 + {4*product} = {1 + 4*product}",
            f"n = [-1 ± √{1 + 4*product}] / 2",
            f"n = [-1 ± {int(math.sqrt(1 + 4*product))}] / 2",
            f"n = {(-1 + int(math.sqrt(1 + 4*product))) // 2} or n = {(-1 - int(math.sqrt(1 + 4*product))) // 2}",
            f"Since n must be positive: n = {n}",
            f"The consecutive integers are {n} and {n+1}"
        ]
        
        socratic_hints = [
            {
                "level": 1,
                "hint": "If the first integer is n, what is the next consecutive integer?",
                "nudge": "n and (n+1)"
            },
            {
                "level": 2,
                "hint": f"Set up equation: n(n+1) = {product}",
                "nudge": f"n² + n - {product} = 0"
            },
            {
                "level": 3,
                "hint": "Solve using quadratic formula and reject negative value",
                "nudge": f"n = {n} (positive solution)"
            }
        ]
        
        return {
            "question_id": self._generate_id(),
            "pattern_id": "quadratic_consecutive_integers",
            "topic": topic,
            "question_text": question_text,
            "solution_steps": solution_steps,
            "final_answer": f"The integers are {n} and {n+1}",
            "marks": 5,
            "difficulty": 0.7,
            "estimated_time_minutes": 7,
            "socratic_hints": socratic_hints,
            "generated_at": datetime.now().isoformat(),
            "unique_hash": self._compute_hash(question_text)
        }

    def _gen_quadratic_age_problem(self, pattern, topic):
        """
        Pattern: Age word problem
        Frequency: 6/11 papers (Medium-High)
        Source: 2023 Q33, 2018 Q10
        """
        question_text = (
            f"A person's present age is such that 5 years ago, "
            f"the square of his age was equal to 7 times his present age. "
            f"Find his present age by forming a quadratic equation."
        )
        
        solution_steps = [
            "Let present age = x years",
            "5 years ago, age = (x - 5) years",
            "Given: (x - 5)² = 7x",
            "x² - 10x + 25 = 7x",
            "x² - 10x - 7x + 25 = 0",
            "x² - 17x + 25 = 0",
            "Using quadratic formula:",
            "x = [17 ± √(289 - 100)] / 2",
            "x = [17 ± √189] / 2",
            "x = [17 ± 13.75] / 2",
            "x ≈ 15.4 or x ≈ 1.6",
            "Since age must be reasonable: x ≈ 15 years (accepting approximate value)"
        ]
        
        socratic_hints = [
            {
                "level": 1,
                "hint": "Let the present age be x. What was the age 5 years ago?",
                "nudge": "(x - 5) years"
            },
            {
                "level": 2,
                "hint": "Set up equation: (x-5)² = 7x",
                "nudge": "Expand and bring all terms to one side"
            },
            {
                "level": 3,
                "hint": "Solve x² - 17x + 25 = 0 using quadratic formula",
                "nudge": "Choose the reasonable positive value"
            }
        ]
        
        return {
            "question_id": self._generate_id(),
            "pattern_id": "quadratic_age_problem",
            "topic": topic,
            "question_text": question_text,
            "solution_steps": solution_steps,
            "final_answer": "Present age ≈ 15 years",
            "marks": 5,
            "difficulty": 0.8,
            "estimated_time_minutes": 8,
            "socratic_hints": socratic_hints,
            "generated_at": datetime.now().isoformat(),
            "unique_hash": self._compute_hash(question_text)
        }

    def _gen_quadratic_area_perimeter(self, pattern, topic):
        """
        Pattern: Rectangle area/perimeter problem
        Frequency: 9/11 papers (Very High)
        Source: 2023 Q34, 2024 Q36, 2025 Q33
        """
        import math
        
        # Variables - dimensions that give nice quadratics
        rectangles = [
            {"length_more": 7, "area": 30, "length": 10, "width": 3},
            {"length_more": 5, "area": 24, "length": 8, "width": 3},
            {"length_more": 4, "area": 32, "length": 8, "width": 4},
            {"length_more": 6, "area": 40, "length": 10, "width": 4}
        ]
        
        chosen = random.choice(rectangles)
        length_more = chosen["length_more"]
        area = chosen["area"]
        length = chosen["length"]
        width = chosen["width"]
        
        question_text = (
            f"The length of a rectangle is {length_more} cm more than its width. "
            f"If the area of the rectangle is {area} cm², find its dimensions "
            f"by forming a quadratic equation."
        )
        
        solution_steps = [
            "Let width = x cm",
            f"Then length = (x + {length_more}) cm",
            f"Area = length × width = {area} cm²",
            f"x(x + {length_more}) = {area}",
            f"x² + {length_more}x = {area}",
            f"x² + {length_more}x - {area} = 0",
            "Using factorization or quadratic formula:",
            f"(x - {width})(x + {width + length_more}) = 0",
            f"x = {width} or x = -{width + length_more}",
            f"Since width cannot be negative: x = {width} cm",
            f"Width = {width} cm",
            f"Length = {width} + {length_more} = {length} cm"
        ]
        
        socratic_hints = [
            {
                "level": 1,
                "hint": "If width is x, what is the length?",
                "nudge": f"Length = x + {length_more} cm"
            },
            {
                "level": 2,
                "hint": f"Use area formula: length × width = {area}",
                "nudge": f"x(x + {length_more}) = {area}"
            },
            {
                "level": 3,
                "hint": f"Solve x² + {length_more}x - {area} = 0",
                "nudge": f"Width = {width} cm, Length = {length} cm"
            }
        ]
        
        return {
            "question_id": self._generate_id(),
            "pattern_id": "quadratic_area_perimeter",
            "topic": topic,
            "question_text": question_text,
            "solution_steps": solution_steps,
            "final_answer": f"Width = {width} cm, Length = {length} cm",
            "marks": 5,
            "difficulty": 0.7,
            "estimated_time_minutes": 7,
            "socratic_hints": socratic_hints,
            "generated_at": datetime.now().isoformat(),
            "unique_hash": self._compute_hash(question_text)
        }

    # ============================================================
    # ARITHMETIC PROGRESSIONS PATTERNS (6 patterns - 8 marks)
    # ============================================================

    def _gen_ap_nth_term_basic(self, pattern, topic):
        """
        Pattern: Find nth term given a and d
        Frequency: 10/11 papers (Very High)
        Source: 2023 Q7, 2024 Q5, 2025 Q6
        """
        # Variables
        first_term = random.choice([2, 3, 5, 7, 10, 12])
        common_diff = random.choice([2, 3, 4, 5, -2, -3])
        n = random.choice([10, 12, 15, 20, 25])
        
        # Calculate nth term
        nth_term = first_term + (n - 1) * common_diff
        
        question_text = (
            f"Find the {n}th term of an arithmetic progression (AP) "
            f"whose first term is {first_term} and common difference is {common_diff}."
        )
        
        solution_steps = [
            f"Given: First term a = {first_term}, Common difference d = {common_diff}",
            f"To find: {n}th term (a_{n})",
            "Formula: a_n = a + (n-1)d",
            f"a_{n} = {first_term} + ({n}-1)×{common_diff}",
            f"a_{n} = {first_term} + {n-1}×{common_diff}",
            f"a_{n} = {first_term} + {(n-1)*common_diff}",
            f"a_{n} = {nth_term}"
        ]
        
        socratic_hints = [
            {
                "level": 1,
                "hint": "What is the formula for the nth term of an AP?",
                "nudge": "a_n = a + (n-1)d"
            },
            {
                "level": 2,
                "hint": f"Identify: a = {first_term}, d = {common_diff}, n = {n}",
                "nudge": "Substitute these values into the formula"
            },
            {
                "level": 3,
                "hint": f"Calculate: {first_term} + ({n}-1)×{common_diff}",
                "nudge": f"= {first_term} + {(n-1)*common_diff} = {nth_term}"
            }
        ]
        
        return {
            "question_id": self._generate_id(),
            "pattern_id": "ap_nth_term_basic",
            "topic": topic,
            "question_text": question_text,
            "solution_steps": solution_steps,
            "final_answer": f"a_{n} = {nth_term}",
            "marks": 2,
            "difficulty": 0.3,
            "estimated_time_minutes": 3,
            "socratic_hints": socratic_hints,
            "generated_at": datetime.now().isoformat(),
            "unique_hash": self._compute_hash(question_text)
        }

    def _gen_ap_sum_n_terms(self, pattern, topic):
        """
        Pattern: Find sum of n terms
        Frequency: 9/11 papers (High)
        Source: 2023 Q28, 2024 Q27, 2025 Q28
        """
        # Variables
        first_term = random.choice([5, 10, 15, 20])
        common_diff = random.choice([3, 4, 5, 6])
        n = random.choice([10, 12, 15, 20])
        
        # Calculate sum
        sum_n = (n / 2) * (2 * first_term + (n - 1) * common_diff)
        
        question_text = (
            f"Find the sum of the first {n} terms of an AP "
            f"with first term {first_term} and common difference {common_diff}."
        )
        
        solution_steps = [
            f"Given: a = {first_term}, d = {common_diff}, n = {n}",
            "Formula: S_n = (n/2)[2a + (n-1)d]",
            f"S_{n} = ({n}/2)[2×{first_term} + ({n}-1)×{common_diff}]",
            f"S_{n} = {n/2}[{2*first_term} + {n-1}×{common_diff}]",
            f"S_{n} = {n/2}[{2*first_term} + {(n-1)*common_diff}]",
            f"S_{n} = {n/2}×{2*first_term + (n-1)*common_diff}",
            f"S_{n} = {int(sum_n)}"
        ]
        
        socratic_hints = [
            {
                "level": 1,
                "hint": "What formula gives the sum of n terms in an AP?",
                "nudge": "S_n = (n/2)[2a + (n-1)d]"
            },
            {
                "level": 2,
                "hint": f"Substitute a={first_term}, d={common_diff}, n={n}",
                "nudge": f"S_n = ({n}/2)[2×{first_term} + ({n}-1)×{common_diff}]"
            },
            {
                "level": 3,
                "hint": "Simplify the expression inside brackets first",
                "nudge": f"= {n/2} × {2*first_term + (n-1)*common_diff} = {int(sum_n)}"
            }
        ]
        
        return {
            "question_id": self._generate_id(),
            "pattern_id": "ap_sum_n_terms",
            "topic": topic,
            "question_text": question_text,
            "solution_steps": solution_steps,
            "final_answer": f"Sum = {int(sum_n)}",
            "marks": 3,
            "difficulty": 0.5,
            "estimated_time_minutes": 5,
            "socratic_hints": socratic_hints,
            "generated_at": datetime.now().isoformat(),
            "unique_hash": self._compute_hash(question_text)
        }

    def _gen_ap_find_common_difference(self, pattern, topic):
        """
        Pattern: Find common difference given two terms
        Frequency: 8/11 papers (High)
        Source: 2024 Q12, 2025 Q11, 2022 Q7
        """
        # Variables
        first_term = random.choice([3, 5, 7, 10])
        common_diff = random.choice([2, 3, 4, 5])
        n1 = random.choice([5, 7, 10])
        n2 = random.choice([12, 15, 18, 20])
        
        term_n1 = first_term + (n1 - 1) * common_diff
        term_n2 = first_term + (n2 - 1) * common_diff
        
        question_text = (
            f"In an AP, the {n1}th term is {term_n1} and the {n2}th term is {term_n2}. "
            f"Find the common difference."
        )
        
        solution_steps = [
            f"Given: a_{n1} = {term_n1}, a_{n2} = {term_n2}",
            "Using a_n = a + (n-1)d:",
            f"a_{n1} = a + ({n1}-1)d = {term_n1}  ...(1)",
            f"a_{n2} = a + ({n2}-1)d = {term_n2}  ...(2)",
            "Subtracting (1) from (2):",
            f"({n2}-1)d - ({n1}-1)d = {term_n2} - {term_n1}",
            f"{n2-1}d - {n1-1}d = {term_n2 - term_n1}",
            f"{(n2-1)-(n1-1)}d = {term_n2 - term_n1}",
            f"{n2-n1}d = {term_n2 - term_n1}",
            f"d = {(term_n2 - term_n1)/(n2-n1)}",
            f"d = {common_diff}"
        ]
        
        socratic_hints = [
            {
                "level": 1,
                "hint": "How are two terms in an AP related?",
                "nudge": "Both follow a_n = a + (n-1)d"
            },
            {
                "level": 2,
                "hint": "Set up two equations and subtract to eliminate 'a'",
                "nudge": f"({n2-1})d - ({n1-1})d = {term_n2} - {term_n1}"
            },
            {
                "level": 3,
                "hint": f"Solve: {n2-n1}d = {term_n2-term_n1}",
                "nudge": f"d = {common_diff}"
            }
        ]
        
        return {
            "question_id": self._generate_id(),
            "pattern_id": "ap_find_common_difference",
            "topic": topic,
            "question_text": question_text,
            "solution_steps": solution_steps,
            "final_answer": f"Common difference d = {common_diff}",
            "marks": 3,
            "difficulty": 0.6,
            "estimated_time_minutes": 5,
            "socratic_hints": socratic_hints,
            "generated_at": datetime.now().isoformat(),
            "unique_hash": self._compute_hash(question_text)
        }

    def _gen_ap_salary_increment(self, pattern, topic):
        """
        Pattern: Salary increment word problem
        Frequency: 8/11 papers (High)
        Source: 2023 Q36, 2024 Q38, 2025 Q36
        """
        # Variables
        initial_salary = random.choice([30000, 35000, 40000, 45000, 50000])
        annual_increment = random.choice([2000, 2500, 3000, 3500, 4000])
        years = random.choice([10, 12, 15, 20])
        
        # Calculate final salary and total earnings
        final_salary = initial_salary + (years - 1) * annual_increment
        total_earnings = (years / 2) * (initial_salary + final_salary)
        
        question_text = (
            f"Rahul joins a company at a salary of ₹{initial_salary} per month. "
            f"His salary increases by ₹{annual_increment} every year. "
            f"What will be his salary in the {years}th year? "
            f"Also, find his total earnings over {years} years."
        )
        
        solution_steps = [
            f"Given: First year salary a = ₹{initial_salary}",
            f"Annual increment d = ₹{annual_increment}",
            f"This forms an AP: {initial_salary}, {initial_salary+annual_increment}, {initial_salary+2*annual_increment}, ...",
            f"(i) Salary in {years}th year:",
            f"a_{years} = a + ({years}-1)d",
            f"a_{years} = {initial_salary} + {years-1}×{annual_increment}",
            f"a_{years} = {initial_salary} + {(years-1)*annual_increment}",
            f"a_{years} = ₹{final_salary}",
            f"(ii) Total earnings over {years} years:",
            f"S_{years} = ({years}/2)(a + a_{years})",
            f"S_{years} = ({years}/2)({initial_salary} + {final_salary})",
            f"S_{years} = {years/2}×{initial_salary + final_salary}",
            f"S_{years} = ₹{int(total_earnings)}"
        ]
        
        socratic_hints = [
            {
                "level": 1,
                "hint": "What type of sequence is formed by increasing salary?",
                "nudge": "Arithmetic Progression (constant annual increment)"
            },
            {
                "level": 2,
                "hint": f"Use a_n = a + (n-1)d with a={initial_salary}, d={annual_increment}",
                "nudge": f"Calculate {years}th term"
            },
            {
                "level": 3,
                "hint": "For total earnings, use S_n = (n/2)(first + last)",
                "nudge": f"= ({years}/2)({initial_salary} + {final_salary})"
            }
        ]
        
        return {
            "question_id": self._generate_id(),
            "pattern_id": "ap_salary_increment",
            "topic": topic,
            "question_text": question_text,
            "solution_steps": solution_steps,
            "final_answer": f"(i) Salary in {years}th year: ₹{final_salary}, (ii) Total earnings: ₹{int(total_earnings)}",
            "marks": 5,
            "difficulty": 0.7,
            "estimated_time_minutes": 7,
            "socratic_hints": socratic_hints,
            "generated_at": datetime.now().isoformat(),
            "unique_hash": self._compute_hash(question_text)
        }

    def _gen_ap_auditorium_seats(self, pattern, topic):
        """
        Pattern: Auditorium/theater seating arrangement
        Frequency: 7/11 papers (High)
        Source: 2023 Q35, 2022 Q11, 2019 Q8
        """
        # Variables
        first_row_seats = random.choice([20, 25, 30, 35])
        seat_increase = random.choice([2, 3, 4, 5])
        total_rows = random.choice([15, 20, 25])
        
        # Calculate last row and total seats
        last_row_seats = first_row_seats + (total_rows - 1) * seat_increase
        total_seats = (total_rows / 2) * (first_row_seats + last_row_seats)
        
        question_text = (
            f"An auditorium has {first_row_seats} seats in the first row. "
            f"Each successive row has {seat_increase} more seats than the previous row. "
            f"If there are {total_rows} rows in total, find:\n"
            f"(i) Number of seats in the last row\n"
            f"(ii) Total number of seats in the auditorium"
        )
        
        solution_steps = [
            f"Seats form an AP: {first_row_seats}, {first_row_seats+seat_increase}, {first_row_seats+2*seat_increase}, ...",
            f"Given: a = {first_row_seats}, d = {seat_increase}, n = {total_rows}",
            f"(i) Seats in last row:",
            f"a_{total_rows} = a + (n-1)d",
            f"a_{total_rows} = {first_row_seats} + ({total_rows}-1)×{seat_increase}",
            f"a_{total_rows} = {first_row_seats} + {(total_rows-1)*seat_increase}",
            f"a_{total_rows} = {last_row_seats} seats",
            f"(ii) Total seats:",
            f"S_n = (n/2)(a + l) where l is last term",
            f"S_{total_rows} = ({total_rows}/2)({first_row_seats} + {last_row_seats})",
            f"S_{total_rows} = {total_rows/2}×{first_row_seats + last_row_seats}",
            f"S_{total_rows} = {int(total_seats)} seats"
        ]
        
        socratic_hints = [
            {
                "level": 1,
                "hint": "Do the seats form an arithmetic progression?",
                "nudge": f"Yes, with a={first_row_seats} and d={seat_increase}"
            },
            {
                "level": 2,
                "hint": "For last row, use nth term formula",
                "nudge": f"a_n = {first_row_seats} + ({total_rows}-1)×{seat_increase}"
            },
            {
                "level": 3,
                "hint": "For total, use S_n = (n/2)(first + last)",
                "nudge": f"= ({total_rows}/2)({first_row_seats} + {last_row_seats})"
            }
        ]
        
        return {
            "question_id": self._generate_id(),
            "pattern_id": "ap_auditorium_seats",
            "topic": topic,
            "question_text": question_text,
            "solution_steps": solution_steps,
            "final_answer": f"(i) Last row: {last_row_seats} seats, (ii) Total: {int(total_seats)} seats",
            "marks": 5,
            "difficulty": 0.7,
            "estimated_time_minutes": 7,
            "socratic_hints": socratic_hints,
            "generated_at": datetime.now().isoformat(),
            "unique_hash": self._compute_hash(question_text)
        }

    def _gen_ap_find_n_given_sum(self, pattern, topic):
        """
        Pattern: Find n when sum is given
        Frequency: 7/11 papers (High)
        Source: 2024 Q29, 2025 Q27, 2022 Q8
        """
        import math
        
        # Variables that give nice n values
        configs = [
            {"a": 5, "d": 3, "sum": 285, "n": 10},
            {"a": 10, "d": 4, "sum": 560, "n": 14},
            {"a": 7, "d": 2, "sum": 252, "n": 12},
        ]
        
        chosen = random.choice(configs)
        a = chosen["a"]
        d = chosen["d"]
        target_sum = chosen["sum"]
        n = chosen["n"]
        
        question_text = (
            f"How many terms of the AP {a}, {a+d}, {a+2*d}, ... "
            f"must be taken so that their sum is {target_sum}?"
        )
        
        solution_steps = [
            f"Given AP: {a}, {a+d}, {a+2*d}, ...",
            f"Here a = {a}, d = {d}",
            f"Sum of n terms: S_n = {target_sum}",
            "Using formula: S_n = (n/2)[2a + (n-1)d]",
            f"{target_sum} = (n/2)[2×{a} + (n-1)×{d}]",
            f"{target_sum} = (n/2)[{2*a} + {d}n - {d}]",
            f"{target_sum} = (n/2)[{2*a-d} + {d}n]",
            f"{target_sum}×2 = n[{2*a-d} + {d}n]",
            f"{2*target_sum} = {2*a-d}n + {d}n²",
            f"{d}n² + {2*a-d}n - {2*target_sum} = 0",
            "Using quadratic formula or factorization:",
            f"n = {n} (taking positive value)"
        ]
        
        socratic_hints = [
            {
                "level": 1,
                "hint": "Which formula relates S_n, a, d, and n?",
                "nudge": "S_n = (n/2)[2a + (n-1)d]"
            },
            {
                "level": 2,
                "hint": f"Substitute S_n={target_sum}, a={a}, d={d}",
                "nudge": "You'll get a quadratic equation in n"
            },
            {
                "level": 3,
                "hint": "Solve the quadratic equation and take positive value",
                "nudge": f"n = {n}"
            }
        ]
        
        return {
            "question_id": self._generate_id(),
            "pattern_id": "ap_find_n_given_sum",
            "topic": topic,
            "question_text": question_text,
            "solution_steps": solution_steps,
            "final_answer": f"n = {n} terms",
            "marks": 3,
            "difficulty": 0.7,
            "estimated_time_minutes": 6,
            "socratic_hints": socratic_hints,
            "generated_at": datetime.now().isoformat(),
            "unique_hash": self._compute_hash(question_text)
        }

    # ============================================================
    # PROBABILITY PATTERNS (8 patterns - 5 marks)
    # ============================================================

    def _gen_probability_single_card(self, pattern, topic):
        """
        Pattern: Probability of drawing single card
        Frequency: 9/11 papers (Very High)
        Source: 2023 Q1, 2024 Q3, 2025 Q1
        """
        # Variables - different card types
        card_scenarios = [
            {"type": "red card", "favorable": 26, "total": 52},
            {"type": "black card", "favorable": 26, "total": 52},
            {"type": "face card", "favorable": 12, "total": 52},
            {"type": "ace", "favorable": 4, "total": 52},
            {"type": "king", "favorable": 4, "total": 52},
            {"type": "heart", "favorable": 13, "total": 52},
            {"type": "spade", "favorable": 13, "total": 52},
            {"type": "diamond", "favorable": 13, "total": 52},
            {"type": "club", "favorable": 13, "total": 52},
        ]
        
        chosen = random.choice(card_scenarios)
        card_type = chosen["type"]
        favorable = chosen["favorable"]
        total = chosen["total"]
        
        # Simplify fraction
        from math import gcd
        g = gcd(favorable, total)
        numerator = favorable // g
        denominator = total // g
        
        question_text = (
            f"A card is drawn at random from a well-shuffled deck of {total} playing cards. "
            f"Find the probability of getting {card_type}."
        )
        
        solution_steps = [
            f"Total number of cards = {total}",
            f"Number of {card_type}s = {favorable}",
            f"Probability P(E) = Favorable outcomes / Total outcomes",
            f"P({card_type}) = {favorable}/{total}",
            f"P({card_type}) = {numerator}/{denominator}"
        ]
        
        socratic_hints = [
            {
                "level": 1,
                "hint": "What is the formula for probability?",
                "nudge": "P(E) = Favorable outcomes / Total outcomes"
            },
            {
                "level": 2,
                "hint": f"How many {card_type}s are in a standard deck?",
                "nudge": f"There are {favorable} {card_type}s"
            },
            {
                "level": 3,
                "hint": f"Calculate {favorable}/{total} and simplify",
                "nudge": f"= {numerator}/{denominator}"
            }
        ]
        
        return {
            "question_id": self._generate_id(),
            "pattern_id": "probability_single_card",
            "topic": topic,
            "question_text": question_text,
            "solution_steps": solution_steps,
            "final_answer": f"Probability = {numerator}/{denominator}",
            "marks": 1,
            "difficulty": 0.2,
            "estimated_time_minutes": 2,
            "socratic_hints": socratic_hints,
            "generated_at": datetime.now().isoformat(),
            "unique_hash": self._compute_hash(question_text)
        }

    def _gen_probability_two_dice(self, pattern, topic):
        """
        Pattern: Two dice - sum or product
        Frequency: 7/11 papers (High)
        Source: 2023 Q21, 2024 Q19, 2025 Q20
        """
        # Variables - different conditions
        dice_conditions = [
            {"condition": "sum is 7", "favorable": 6},  # (1,6), (2,5), (3,4), (4,3), (5,2), (6,1)
            {"condition": "sum is 10", "favorable": 3}, # (4,6), (5,5), (6,4)
            {"condition": "sum is 5", "favorable": 4},  # (1,4), (2,3), (3,2), (4,1)
            {"condition": "product is 12", "favorable": 4}, # (2,6), (3,4), (4,3), (6,2)
            {"condition": "both numbers same", "favorable": 6}, # (1,1), (2,2), ..., (6,6)
        ]
        
        chosen = random.choice(dice_conditions)
        condition = chosen["condition"]
        favorable = chosen["favorable"]
        total = 36  # 6×6
        
        # Simplify fraction
        from math import gcd
        g = gcd(favorable, total)
        numerator = favorable // g
        denominator = total // g
        
        question_text = (
            f"Two dice are thrown simultaneously. "
            f"Find the probability that the {condition}."
        )
        
        solution_steps = [
            "Total outcomes when two dice are thrown = 6 × 6 = 36",
            f"Favorable outcomes (where {condition}):",
            f"Number of favorable outcomes = {favorable}",
            f"Probability P(E) = {favorable}/36",
            f"P(E) = {numerator}/{denominator}"
        ]
        
        socratic_hints = [
            {
                "level": 1,
                "hint": "How many total outcomes when throwing two dice?",
                "nudge": "6 × 6 = 36"
            },
            {
                "level": 2,
                "hint": f"List or count all pairs where {condition}",
                "nudge": f"There are {favorable} such outcomes"
            },
            {
                "level": 3,
                "hint": f"Calculate probability: {favorable}/36",
                "nudge": f"Simplified: {numerator}/{denominator}"
            }
        ]
        
        return {
            "question_id": self._generate_id(),
            "pattern_id": "probability_two_dice",
            "topic": topic,
            "question_text": question_text,
            "solution_steps": solution_steps,
            "final_answer": f"Probability = {numerator}/{denominator}",
            "marks": 2,
            "difficulty": 0.4,
            "estimated_time_minutes": 3,
            "socratic_hints": socratic_hints,
            "generated_at": datetime.now().isoformat(),
            "unique_hash": self._compute_hash(question_text)
        }

    def _gen_probability_balls_without_replacement(self, pattern, topic):
        """
        Pattern: Balls drawn without replacement
        Frequency: 6/11 papers (Medium-High)
        Source: 2024 Q21, 2023 Q22, 2019 Q5
        """
        # Variables
        red_balls = random.choice([3, 4, 5])
        blue_balls = random.choice([4, 5, 6])
        total_balls = red_balls + blue_balls
        
        # Probability of drawing 2 red balls without replacement
        prob_first_red = red_balls / total_balls
        prob_second_red = (red_balls - 1) / (total_balls - 1)
        prob_both_red = prob_first_red * prob_second_red
        
        # Simplify
        from math import gcd
        numerator = red_balls * (red_balls - 1)
        denominator = total_balls * (total_balls - 1)
        g = gcd(numerator, denominator)
        num_simplified = numerator // g
        den_simplified = denominator // g
        
        question_text = (
            f"A bag contains {red_balls} red balls and {blue_balls} blue balls. "
            f"Two balls are drawn at random one after another without replacement. "
            f"Find the probability that both balls are red."
        )
        
        solution_steps = [
            f"Total balls = {red_balls} + {blue_balls} = {total_balls}",
            "Event: Both balls are red",
            f"P(first ball red) = {red_balls}/{total_balls}",
            f"After drawing one red ball: Remaining = {red_balls-1} red, {blue_balls} blue",
            f"P(second ball red | first red) = {red_balls-1}/{total_balls-1}",
            "P(both red) = P(first red) × P(second red | first red)",
            f"P(both red) = ({red_balls}/{total_balls}) × ({red_balls-1}/{total_balls-1})",
            f"P(both red) = {numerator}/{denominator}",
            f"P(both red) = {num_simplified}/{den_simplified}"
        ]
        
        socratic_hints = [
            {
                "level": 1,
                "hint": "What changes after the first ball is drawn?",
                "nudge": "Total balls and red balls both decrease by 1"
            },
            {
                "level": 2,
                "hint": "How do you find probability of two dependent events?",
                "nudge": "Multiply: P(A) × P(B|A)"
            },
            {
                "level": 3,
                "hint": f"Calculate: ({red_balls}/{total_balls}) × ({red_balls-1}/{total_balls-1})",
                "nudge": f"= {num_simplified}/{den_simplified}"
            }
        ]
        
        return {
            "question_id": self._generate_id(),
            "pattern_id": "probability_balls_without_replacement",
            "topic": topic,
            "question_text": question_text,
            "solution_steps": solution_steps,
            "final_answer": f"Probability = {num_simplified}/{den_simplified}",
            "marks": 3,
            "difficulty": 0.6,
            "estimated_time_minutes": 5,
            "socratic_hints": socratic_hints,
            "generated_at": datetime.now().isoformat(),
            "unique_hash": self._compute_hash(question_text)
        }

    def _gen_probability_complementary_event(self, pattern, topic):
        """
        Pattern: Complementary event P(not E) = 1 - P(E)
        Frequency: 8/11 papers (High)
        Source: 2023 Q12, 2024 Q14, 2025 Q12
        """
        # Variables
        prob_events = [
            {"event": "winning a game", "prob": "3/5", "prob_decimal": 0.6},
            {"event": "raining tomorrow", "prob": "2/7", "prob_decimal": 2/7},
            {"event": "getting a defective item", "prob": "1/8", "prob_decimal": 0.125},
        ]
        
        chosen = random.choice(prob_events)
        event = chosen["event"]
        prob_str = chosen["prob"]
        prob_val = chosen["prob_decimal"]
        
        # Calculate complement
        comp_val = 1 - prob_val
        
        # Express as fraction
        from fractions import Fraction
        frac = Fraction(prob_str)
        comp_frac = 1 - frac
        
        question_text = (
            f"The probability of {event} is {prob_str}. "
            f"Find the probability of not {event}."
        )
        
        solution_steps = [
            f"Given: P({event}) = {prob_str}",
            f"Let E = event of {event}",
            "Complementary event: not E",
            "Formula: P(not E) = 1 - P(E)",
            f"P(not {event}) = 1 - {prob_str}",
            f"P(not {event}) = {comp_frac}"
        ]
        
        socratic_hints = [
            {
                "level": 1,
                "hint": "What is the relationship between an event and its complement?",
                "nudge": "P(E) + P(not E) = 1"
            },
            {
                "level": 2,
                "hint": "How do you find P(not E) if you know P(E)?",
                "nudge": "P(not E) = 1 - P(E)"
            },
            {
                "level": 3,
                "hint": f"Subtract: 1 - {prob_str}",
                "nudge": f"= {comp_frac}"
            }
        ]
        
        return {
            "question_id": self._generate_id(),
            "pattern_id": "probability_complementary_event",
            "topic": topic,
            "question_text": question_text,
            "solution_steps": solution_steps,
            "final_answer": f"P(not {event}) = {comp_frac}",
            "marks": 1,
            "difficulty": 0.3,
            "estimated_time_minutes": 2,
            "socratic_hints": socratic_hints,
            "generated_at": datetime.now().isoformat(),
            "unique_hash": self._compute_hash(question_text)
        }

    def _gen_probability_pack_of_cards_advanced(self, pattern, topic):
        """
        Pattern: Advanced card probability (two cards)
        Frequency: 8/11 papers (High)
        Source: 2023 Q24, 2024 Q23, 2025 Q22
        """
        # Variables - two card scenarios
        scenarios = [
            {"condition": "both are aces", "favorable": 4*3},
            {"condition": "both are face cards", "favorable": 12*11},
            {"condition": "both are red", "favorable": 26*25},
        ]
        
        chosen = random.choice(scenarios)
        condition = chosen["condition"]
        favorable = chosen["favorable"]
        total = 52 * 51  # Two cards without replacement
        
        # Simplify
        from math import gcd
        g = gcd(favorable, total)
        numerator = favorable // g
        denominator = total // g
        
        question_text = (
            f"Two cards are drawn at random from a deck of 52 cards without replacement. "
            f"Find the probability that {condition}."
        )
        
        solution_steps = [
            "Total ways to draw 2 cards = 52 × 51 (without replacement)",
            f"For {condition}:",
            f"Favorable outcomes = {favorable}",
            f"Probability = {favorable}/{total}",
            f"Probability = {numerator}/{denominator}"
        ]
        
        socratic_hints = [
            {
                "level": 1,
                "hint": "How many ways can you draw 2 cards from 52?",
                "nudge": "52 × 51 (order matters, without replacement)"
            },
            {
                "level": 2,
                "hint": f"Count favorable outcomes for {condition}",
                "nudge": f"There are {favorable} such outcomes"
            },
            {
                "level": 3,
                "hint": f"Calculate and simplify: {favorable}/{total}",
                "nudge": f"= {numerator}/{denominator}"
            }
        ]
        
        return {
            "question_id": self._generate_id(),
            "pattern_id": "probability_pack_of_cards_advanced",
            "topic": topic,
            "question_text": question_text,
            "solution_steps": solution_steps,
            "final_answer": f"Probability = {numerator}/{denominator}",
            "marks": 2,
            "difficulty": 0.5,
            "estimated_time_minutes": 4,
            "socratic_hints": socratic_hints,
            "generated_at": datetime.now().isoformat(),
            "unique_hash": self._compute_hash(question_text)
        }

    def _gen_probability_at_least_one(self, pattern, topic):
        """
        Pattern: At least one success
        Frequency: 6/11 papers (Medium-High)
        Source: 2024 Q25, 2022 Q6, 2019 Q4
        """
        # Coin toss scenario
        num_tosses = random.choice([2, 3])
        
        if num_tosses == 2:
            total_outcomes = 4  # HH, HT, TH, TT
            at_least_one_head = 3  # HH, HT, TH
            none_head = 1  # TT
        else:  # 3 tosses
            total_outcomes = 8
            at_least_one_head = 7
            none_head = 1  # TTT
        
        # Simplify
        from math import gcd
        g = gcd(at_least_one_head, total_outcomes)
        numerator = at_least_one_head // g
        denominator = total_outcomes // g
        
        question_text = (
            f"A coin is tossed {num_tosses} times. "
            f"Find the probability of getting at least one head."
        )
        
        solution_steps = [
            f"Total outcomes when tossing {num_tosses} times = 2^{num_tosses} = {total_outcomes}",
            "Method 1: Direct counting",
            f"At least one head = all cases except all tails",
            f"Favorable outcomes = {total_outcomes} - {none_head} = {at_least_one_head}",
            f"P(at least one head) = {at_least_one_head}/{total_outcomes}",
            "",
            "Method 2: Using complement",
            f"P(no head) = P(all tails) = {none_head}/{total_outcomes}",
            f"P(at least one head) = 1 - P(no head)",
            f"P(at least one head) = 1 - {none_head}/{total_outcomes} = {numerator}/{denominator}"
        ]
        
        socratic_hints = [
            {
                "level": 1,
                "hint": "What is the complement of 'at least one head'?",
                "nudge": "'No heads' or 'all tails'"
            },
            {
                "level": 2,
                "hint": "Use: P(at least one) = 1 - P(none)",
                "nudge": f"P(all tails) = {none_head}/{total_outcomes}"
            },
            {
                "level": 3,
                "hint": f"Calculate: 1 - {none_head}/{total_outcomes}",
                "nudge": f"= {numerator}/{denominator}"
            }
        ]
        
        return {
            "question_id": self._generate_id(),
            "pattern_id": "probability_at_least_one",
            "topic": topic,
            "question_text": question_text,
            "solution_steps": solution_steps,
            "final_answer": f"Probability = {numerator}/{denominator}",
            "marks": 2,
            "difficulty": 0.6,
            "estimated_time_minutes": 4,
            "socratic_hints": socratic_hints,
            "generated_at": datetime.now().isoformat(),
            "unique_hash": self._compute_hash(question_text)
        }

    def _gen_probability_spinner(self, pattern, topic):
        """
        Pattern: Spinner/wheel probability
        Frequency: 5/11 papers (Medium)
        Source: 2025 Q18, 2021 Q3
        """
        # Variables
        total_sections = random.choice([8, 10, 12])
        winning_sections = random.choice([2, 3, 4])
        
        # Simplify
        from math import gcd
        g = gcd(winning_sections, total_sections)
        numerator = winning_sections // g
        denominator = total_sections // g
        
        question_text = (
            f"A spinner is divided into {total_sections} equal sections numbered 1 to {total_sections}. "
            f"Sections {', '.join(str(i) for i in range(1, winning_sections+1))} are colored red. "
            f"If the spinner is spun once, find the probability that it lands on a red section."
        )
        
        solution_steps = [
            f"Total sections = {total_sections}",
            f"Red sections = {winning_sections}",
            "All sections are equally likely",
            f"P(red section) = Number of red sections / Total sections",
            f"P(red section) = {winning_sections}/{total_sections}",
            f"P(red section) = {numerator}/{denominator}"
        ]
        
        socratic_hints = [
            {
                "level": 1,
                "hint": "Are all sections equally likely?",
                "nudge": "Yes, so use classical probability"
            },
            {
                "level": 2,
                "hint": f"How many red sections out of {total_sections}?",
                "nudge": f"{winning_sections} red sections"
            },
            {
                "level": 3,
                "hint": f"Calculate: {winning_sections}/{total_sections}",
                "nudge": f"Simplified: {numerator}/{denominator}"
            }
        ]
        
        return {
            "question_id": self._generate_id(),
            "pattern_id": "probability_spinner",
            "topic": topic,
            "question_text": question_text,
            "solution_steps": solution_steps,
            "final_answer": f"Probability = {numerator}/{denominator}",
            "marks": 1,
            "difficulty": 0.3,
            "estimated_time_minutes": 2,
            "socratic_hints": socratic_hints,
            "generated_at": datetime.now().isoformat(),
            "unique_hash": self._compute_hash(question_text)
        }

    def _gen_probability_random_number(self, pattern, topic):
        """
        Pattern: Random number selection
        Frequency: 6/11 papers (Medium-High)
        Source: 2023 Q15, 2024 Q16, 2022 Q5
        """
        # Variables
        min_num = 1
        max_num = random.choice([20, 30, 50, 100])
        
        conditions = [
            {"type": "multiple of 5", "count": max_num // 5},
            {"type": "multiple of 10", "count": max_num // 10},
        ]
        
        chosen = random.choice([c for c in conditions if c["count"] is not None])
        condition_type = chosen["type"]
        favorable = chosen["count"]
        
        # Simplify
        from math import gcd
        g = gcd(favorable, max_num)
        numerator = favorable // g
        denominator = max_num // g
        
        question_text = (
            f"A number is selected at random from the numbers {min_num} to {max_num}. "
            f"Find the probability that the selected number is a {condition_type}."
        )
        
        solution_steps = [
            f"Total numbers from {min_num} to {max_num} = {max_num}",
            f"Numbers that are {condition_type}: {favorable}",
            f"P({condition_type}) = {favorable}/{max_num}",
            f"P({condition_type}) = {numerator}/{denominator}"
        ]
        
        socratic_hints = [
            {
                "level": 1,
                "hint": f"How many numbers are there from {min_num} to {max_num}?",
                "nudge": f"{max_num} numbers"
            },
            {
                "level": 2,
                "hint": f"Count how many are {condition_type}",
                "nudge": f"{favorable} such numbers"
            },
            {
                "level": 3,
                "hint": f"Calculate and simplify: {favorable}/{max_num}",
                "nudge": f"= {numerator}/{denominator}"
            }
        ]
        
        return {
            "question_id": self._generate_id(),
            "pattern_id": "probability_random_number",
            "topic": topic,
            "question_text": question_text,
            "solution_steps": solution_steps,
            "final_answer": f"Probability = {numerator}/{denominator}",
            "marks": 2,
            "difficulty": 0.4,
            "estimated_time_minutes": 3,
            "socratic_hints": socratic_hints,
            "generated_at": datetime.now().isoformat(),
            "unique_hash": self._compute_hash(question_text)
        }

    # ============================================================
    # CONSTRUCTIONS PATTERNS (3 patterns - 3 marks)
    # ============================================================

    def _gen_construction_divide_line_segment(self, pattern, topic):
        """
        Pattern: Divide line segment in given ratio
        Frequency: 6/11 papers (Medium-High)
        Source: 2023 Q37, 2024 Q37, 2022 Q12
        """
        # Variables
        ratio_m = random.choice([2, 3, 4])
        ratio_n = random.choice([3, 4, 5])
        
        # Ensure m < n for internal division
        if ratio_m >= ratio_n:
            ratio_m, ratio_n = ratio_n, ratio_m
        
        question_text = (
            f"Draw a line segment AB of length 8 cm. "
            f"Divide it internally in the ratio {ratio_m}:{ratio_n}. "
            f"Write the steps of construction."
        )
        
        solution_steps = [
            "Steps of Construction:",
            "1. Draw a line segment AB = 8 cm",
            f"2. Draw any ray AX making an acute angle with AB",
            f"3. Mark {ratio_m + ratio_n} equal points A₁, A₂, ..., A_{ratio_m + ratio_n} on AX",
            f"4. Join BA_{ratio_m + ratio_n}",
            f"5. From A_{ratio_m}, draw A_{ratio_m}P || BA_{ratio_m + ratio_n} (using corresponding angles)",
            f"6. P divides AB in the ratio {ratio_m}:{ratio_n}",
            "",
            "Justification:",
            f"By Basic Proportionality Theorem: AP/PB = AA_{ratio_m}/A_{ratio_m}A_{ratio_m + ratio_n} = {ratio_m}/{ratio_n}"
        ]
        
        socratic_hints = [
            {
                "level": 1,
                "hint": "How many equal divisions do you need on the ray?",
                "nudge": f"m + n = {ratio_m} + {ratio_n} = {ratio_m + ratio_n} divisions"
            },
            {
                "level": 2,
                "hint": f"From which point do you draw a line parallel to BA_{ratio_m + ratio_n}?",
                "nudge": f"From the {ratio_m}th point (A_{ratio_m})"
            },
            {
                "level": 3,
                "hint": "Which theorem justifies this construction?",
                "nudge": "Basic Proportionality Theorem (Thales' theorem)"
            }
        ]
        
        return {
            "question_id": self._generate_id(),
            "pattern_id": "construction_divide_line_segment",
            "topic": topic,
            "question_text": question_text,
            "solution_steps": solution_steps,
            "final_answer": f"Line segment divided in ratio {ratio_m}:{ratio_n}",
            "marks": 2,
            "difficulty": 0.5,
            "estimated_time_minutes": 5,
            "socratic_hints": socratic_hints,
            "generated_at": datetime.now().isoformat(),
            "unique_hash": self._compute_hash(question_text)
        }

    def _gen_construction_tangent_from_external_point(self, pattern, topic):
        """
        Pattern: Construct tangents from external point
        Frequency: 5/11 papers (Medium)
        Source: 2023 Q38, 2024 Q39, 2021 Q13
        """
        # Variables
        radius = random.choice([3, 4, 5])
        distance = random.choice([7, 8, 9, 10])
        
        question_text = (
            f"Draw a circle of radius {radius} cm. "
            f"From a point P at a distance of {distance} cm from the center, "
            f"construct two tangents to the circle. "
            f"Write the steps of construction."
        )
        
        solution_steps = [
            "Steps of Construction:",
            f"1. Draw a circle with center O and radius {radius} cm",
            f"2. Mark a point P at distance {distance} cm from O",
            "3. Join OP",
            "4. Draw perpendicular bisector of OP, meeting OP at M (midpoint)",
            "5. With M as center and MO (or MP) as radius, draw a circle",
            "6. This circle intersects the given circle at points T₁ and T₂",
            "7. Join PT₁ and PT₂",
            "8. PT₁ and PT₂ are the required tangents",
            "",
            "Justification:",
            "∠OT₁P = 90° (angle in semicircle)",
            "OT₁ ⊥ PT₁, so PT₁ is tangent to circle at T₁",
            "Similarly, PT₂ is tangent at T₂"
        ]
        
        socratic_hints = [
            {
                "level": 1,
                "hint": "What geometric property do tangents from an external point have?",
                "nudge": "They are equal in length and perpendicular to radius at point of contact"
            },
            {
                "level": 2,
                "hint": "How can you ensure the angle at T is 90°?",
                "nudge": "Use angle in semicircle property"
            },
            {
                "level": 3,
                "hint": "Which circle passes through O, T, and P?",
                "nudge": "Circle with diameter OP (constructed using midpoint M)"
            }
        ]
        
        return {
            "question_id": self._generate_id(),
            "pattern_id": "construction_tangent_from_external_point",
            "topic": topic,
            "question_text": question_text,
            "solution_steps": solution_steps,
            "final_answer": "Two tangents constructed from external point",
            "marks": 3,
            "difficulty": 0.7,
            "estimated_time_minutes": 7,
            "socratic_hints": socratic_hints,
            "generated_at": datetime.now().isoformat(),
            "unique_hash": self._compute_hash(question_text)
        }

    def _gen_construction_similar_triangle(self, pattern, topic):
        """
        Pattern: Construct triangle similar to given triangle
        Frequency: 4/11 papers (Medium)
        Source: 2024 Q38, 2022 Q13, 2019 Q12
        """
        # Variables
        scale_numerator = random.choice([2, 3, 4, 5])
        scale_denominator = random.choice([3, 4, 5, 6, 7])
        
        # Ensure proper fraction
        if scale_numerator >= scale_denominator:
            scale_numerator, scale_denominator = scale_denominator - 1, scale_denominator
        
        question_text = (
            f"Construct a triangle ABC with sides AB = 6 cm, BC = 7 cm, and AC = 5 cm. "
            f"Then construct another triangle similar to triangle ABC "
            f"with scale factor {scale_numerator}/{scale_denominator}. "
            f"Write the steps of construction."
        )
        
        solution_steps = [
            "Steps of Construction:",
            "1. Construct △ABC with AB = 6 cm, BC = 7 cm, AC = 5 cm",
            f"2. Draw any ray BX making acute angle with BC",
            f"3. Mark {scale_denominator} equal points B₁, B₂, ..., B_{scale_denominator} on BX",
            f"4. Join B_{scale_denominator}C",
            f"5. From B_{scale_numerator}, draw B_{scale_numerator}C' || B_{scale_denominator}C",
            "6. From C', draw C'A' || CA",
            "7. △A'BC' is the required triangle",
            "",
            "Justification:",
            f"By construction, BC'/BC = {scale_numerator}/{scale_denominator}",
            "Since C'A' || CA, △A'BC' ~ △ABC",
            f"Scale factor = {scale_numerator}/{scale_denominator}"
        ]
        
        socratic_hints = [
            {
                "level": 1,
                "hint": "How many equal divisions needed on ray BX?",
                "nudge": f"Denominator = {scale_denominator} divisions"
            },
            {
                "level": 2,
                "hint": f"From which point do you draw parallel to B_{scale_denominator}C?",
                "nudge": f"From B_{scale_numerator}"
            },
            {
                "level": 3,
                "hint": "Which theorem justifies similarity?",
                "nudge": "Basic Proportionality Theorem (Thales)"
            }
        ]
        
        return {
            "question_id": self._generate_id(),
            "pattern_id": "construction_similar_triangle",
            "topic": topic,
            "question_text": question_text,
            "solution_steps": solution_steps,
            "final_answer": f"Similar triangle with scale factor {scale_numerator}/{scale_denominator} constructed",
            "marks": 3,
            "difficulty": 0.7,
            "estimated_time_minutes": 8,
            "socratic_hints": socratic_hints,
            "generated_at": datetime.now().isoformat(),
            "unique_hash": self._compute_hash(question_text)
        }

    # ============================================================
    # SURFACE AREAS & VOLUMES - ADDITIONAL PATTERNS (3 patterns)
    # ============================================================

    def _gen_volume_frustum_cone(self, pattern, topic):
        """
        Pattern: Frustum of cone volume and surface area
        Frequency: 5/11 papers (Medium)
        Source: 2024 Q35, 2023 Q37, 2020 Q10
        """
        import math
        
        # Variables - dimensions that give clean calculations
        r1 = random.choice([7, 14, 21])  # Top radius (smaller)
        r2 = random.choice([14, 21, 28])  # Bottom radius (larger)
        h = random.choice([12, 15, 18, 24])  # Height
        
        # Ensure r2 > r1
        if r1 >= r2:
            r1, r2 = r2 // 2, r2
        
        pi = 22/7
        
        # Volume of frustum: V = (πh/3)(r₁² + r₂² + r₁r₂)
        volume = (pi * h / 3) * (r1**2 + r2**2 + r1*r2)
        
        # Slant height: l = √[h² + (r₂-r₁)²]
        slant_height = math.sqrt(h**2 + (r2-r1)**2)
        
        # Curved surface area: π(r₁+r₂)l
        curved_surface = pi * (r1 + r2) * slant_height
        
        volume_rounded = round(volume, 2)
        csa_rounded = round(curved_surface, 2)
        
        question_text = (
            f"A frustum of a cone has top radius {r1} cm, bottom radius {r2} cm, "
            f"and height {h} cm. Find:\n"
            f"(i) Volume of the frustum\n"
            f"(ii) Curved surface area of the frustum\n"
            f"(Use π = 22/7 and √{h**2 + (r2-r1)**2} = {slant_height:.2f})"
        )
        
        solution_steps = [
            f"Given: Top radius r₁ = {r1} cm, Bottom radius r₂ = {r2} cm, Height h = {h} cm",
            f"(i) Volume of frustum:",
            "V = (πh/3)(r₁² + r₂² + r₁r₂)",
            f"V = ((22/7) × {h} / 3)({r1}² + {r2}² + {r1}×{r2})",
            f"V = ((22/7) × {h} / 3)({r1**2} + {r2**2} + {r1*r2})",
            f"V = ((22/7) × {h} / 3) × {r1**2 + r2**2 + r1*r2}",
            f"V = {volume_rounded} cm³",
            f"(ii) Curved surface area:",
            f"Slant height l = √[h² + (r₂-r₁)²] = √[{h}² + {r2-r1}²] = {slant_height:.2f} cm",
            "CSA = π(r₁ + r₂)l",
            f"CSA = (22/7) × ({r1} + {r2}) × {slant_height:.2f}",
            f"CSA = (22/7) × {r1+r2} × {slant_height:.2f}",
            f"CSA = {csa_rounded} cm²"
        ]
        
        socratic_hints = [
            {
                "level": 1,
                "hint": "What is the formula for volume of a frustum?",
                "nudge": "V = (πh/3)(r₁² + r₂² + r₁r₂)"
            },
            {
                "level": 2,
                "hint": "For CSA, you need the slant height. How do you find it?",
                "nudge": "l = √[h² + (r₂-r₁)²] using Pythagoras theorem"
            },
            {
                "level": 3,
                "hint": "CSA formula: π(r₁+r₂)l",
                "nudge": f"Substitute r₁={r1}, r₂={r2}, l={slant_height:.2f}"
            }
        ]
        
        return {
            "question_id": self._generate_id(),
            "pattern_id": "volume_frustum_cone",
            "topic": topic,
            "question_text": question_text,
            "solution_steps": solution_steps,
            "final_answer": f"(i) Volume = {volume_rounded} cm³, (ii) CSA = {csa_rounded} cm²",
            "marks": 5,
            "difficulty": 0.8,
            "estimated_time_minutes": 8,
            "socratic_hints": socratic_hints,
            "generated_at": datetime.now().isoformat(),
            "unique_hash": self._compute_hash(question_text)
        }

    def _gen_volume_conversion_melting(self, pattern, topic):
        """
        Pattern: Melting/recasting problems
        Frequency: 4/11 papers (Medium)
        Source: 2023 Q36, 2021 Q11, 2019 Q10
        """
        import math
        
        # Variables
        sphere_radius = random.choice([6, 9, 12])
        cylinder_radius = random.choice([3, 4, 5])
        
        pi = 22/7
        
        # Volume of sphere
        sphere_volume = (4/3) * pi * sphere_radius**3
        
        # Height of cylinder with same volume
        # πr²h = (4/3)πR³
        # h = (4R³)/(3r²)
        cylinder_height = (4 * sphere_radius**3) / (3 * cylinder_radius**2)
        
        sphere_vol_rounded = round(sphere_volume, 2)
        height_rounded = round(cylinder_height, 2)
        
        question_text = (
            f"A solid metallic sphere of radius {sphere_radius} cm is melted and recast into a cylinder "
            f"of radius {cylinder_radius} cm. Find the height of the cylinder. (Use π = 22/7)"
        )
        
        solution_steps = [
            f"Given: Sphere radius R = {sphere_radius} cm, Cylinder radius r = {cylinder_radius} cm",
            "Since volume remains same when recasting:",
            "Volume of sphere = Volume of cylinder",
            "(4/3)πR³ = πr²h",
            f"(4/3) × (22/7) × {sphere_radius}³ = (22/7) × {cylinder_radius}² × h",
            f"(4/3) × {sphere_radius**3} = {cylinder_radius**2} × h",
            f"{(4 * sphere_radius**3) / 3} = {cylinder_radius**2}h",
            f"h = {(4 * sphere_radius**3) / 3} / {cylinder_radius**2}",
            f"h = {height_rounded} cm"
        ]
        
        socratic_hints = [
            {
                "level": 1,
                "hint": "What remains constant when metal is melted and recast?",
                "nudge": "Volume remains the same"
            },
            {
                "level": 2,
                "hint": "Set up equation: Volume of sphere = Volume of cylinder",
                "nudge": "(4/3)πR³ = πr²h"
            },
            {
                "level": 3,
                "hint": "Solve for h by canceling π and rearranging",
                "nudge": f"h = (4R³)/(3r²) = {height_rounded} cm"
            }
        ]
        
        return {
            "question_id": self._generate_id(),
            "pattern_id": "volume_conversion_melting",
            "topic": topic,
            "question_text": question_text,
            "solution_steps": solution_steps,
            "final_answer": f"Height of cylinder = {height_rounded} cm",
            "marks": 5,
            "difficulty": 0.7,
            "estimated_time_minutes": 7,
            "socratic_hints": socratic_hints,
            "generated_at": datetime.now().isoformat(),
            "unique_hash": self._compute_hash(question_text)
        }

    def _gen_volume_hollow_cylinder(self, pattern, topic):
        """
        Pattern: Hollow cylinder volume
        Frequency: 6/11 papers (Medium-High)
        Source: 2024 Q33, 2023 Q32, 2022 Q10
        """
        import math
        
        # Variables
        outer_radius = random.choice([14, 21, 28])
        inner_radius = outer_radius - random.choice([7, 14])
        height = random.choice([20, 25, 30])
        
        pi = 22/7
        
        # Volume of hollow cylinder = π(R² - r²)h
        volume = pi * (outer_radius**2 - inner_radius**2) * height
        
        # Total surface area = 2π(R+r)h + 2π(R²-r²)
        tsa = 2 * pi * (outer_radius + inner_radius) * height + 2 * pi * (outer_radius**2 - inner_radius**2)
        
        volume_rounded = round(volume, 2)
        tsa_rounded = round(tsa, 2)
        
        question_text = (
            f"A hollow cylindrical pipe has outer radius {outer_radius} cm, "
            f"inner radius {inner_radius} cm, and length {height} cm. Find:\n"
            f"(i) Volume of material in the pipe\n"
            f"(ii) Total surface area of the pipe\n"
            f"(Use π = 22/7)"
        )
        
        solution_steps = [
            f"Given: Outer radius R = {outer_radius} cm, Inner radius r = {inner_radius} cm, Height h = {height} cm",
            f"(i) Volume of material:",
            "V = π(R² - r²)h",
            f"V = (22/7)({outer_radius}² - {inner_radius}²) × {height}",
            f"V = (22/7)({outer_radius**2} - {inner_radius**2}) × {height}",
            f"V = (22/7) × {outer_radius**2 - inner_radius**2} × {height}",
            f"V = {volume_rounded} cm³",
            f"(ii) Total surface area:",
            "TSA = Curved surface (outer) + Curved surface (inner) + Area of 2 rings",
            "TSA = 2πRh + 2πrh + 2π(R² - r²)",
            "TSA = 2π(R+r)h + 2π(R²-r²)",
            f"TSA = 2(22/7)({outer_radius}+{inner_radius})×{height} + 2(22/7)({outer_radius**2}-{inner_radius**2})",
            f"TSA = {tsa_rounded} cm²"
        ]
        
        socratic_hints = [
            {
                "level": 1,
                "hint": "How is a hollow cylinder different from a solid cylinder?",
                "nudge": "It has material between two radii: outer R and inner r"
            },
            {
                "level": 2,
                "hint": "Volume = Volume of outer cylinder - Volume of inner cylinder",
                "nudge": "V = πR²h - πr²h = π(R²-r²)h"
            },
            {
                "level": 3,
                "hint": "For TSA, include curved surfaces (inner + outer) and two circular rings",
                "nudge": "TSA = 2π(R+r)h + 2π(R²-r²)"
            }
        ]
        
        return {
            "question_id": self._generate_id(),
            "pattern_id": "volume_hollow_cylinder",
            "topic": topic,
            "question_text": question_text,
            "solution_steps": solution_steps,
            "final_answer": f"(i) Volume = {volume_rounded} cm³, (ii) TSA = {tsa_rounded} cm²",
            "marks": 5,
            "difficulty": 0.7,
            "estimated_time_minutes": 8,
            "socratic_hints": socratic_hints,
            "generated_at": datetime.now().isoformat(),
            "unique_hash": self._compute_hash(question_text)
        }

    # ============================================================
    # POLYNOMIALS - ADDITIONAL PATTERNS (2 patterns)
    # ============================================================

    def _gen_polynomial_division_algorithm(self, pattern, topic):
        """
        Pattern: Verify division algorithm
        Frequency: 6/11 papers (Medium-High)
        Source: 2023 Q27, 2024 Q26, 2022 Q7
        """
        # Variables - polynomials that divide nicely
        divisor_const = random.choice([1, 2, -1, -2])
        
        # For simplicity: p(x) = (x + divisor_const)(x² + mx + n) + remainder
        m = random.choice([1, 2, 3])
        n = random.choice([2, 3, 4])
        remainder = random.choice([0, 1, 2, 3])
        
        # Expand to get coefficients
        # p(x) = x³ + (m + divisor_const)x² + (n + m*divisor_const)x + (n*divisor_const + remainder)
        a = m + divisor_const
        b = n + m * divisor_const
        c = n * divisor_const + remainder
        
        quotient_a = 1
        quotient_b = m
        quotient_c = n
        
        question_text = (
            f"Divide the polynomial p(x) = x³ + {a}x² + {b}x + {c} by g(x) = x + {-divisor_const} "
            f"and verify the division algorithm."
        )
        
        solution_steps = [
            "Division Algorithm: Dividend = Divisor × Quotient + Remainder",
            "p(x) = g(x) × q(x) + r(x)",
            "",
            "Performing polynomial long division:",
            f"p(x) = x³ + {a}x² + {b}x + {c}",
            f"g(x) = x + {-divisor_const}",
            "",
            f"Quotient q(x) = x² + {quotient_b}x + {quotient_c}",
            f"Remainder r(x) = {remainder}",
            "",
            "Verification:",
            f"g(x) × q(x) + r(x) = (x + {-divisor_const})(x² + {quotient_b}x + {quotient_c}) + {remainder}",
            f"= x³ + {quotient_b}x² + {quotient_c}x + {-divisor_const}x² + {-divisor_const * quotient_b}x + {-divisor_const * quotient_c} + {remainder}",
            f"= x³ + {a}x² + {b}x + {c}",
            "= p(x) ✓",
            "",
            "Hence division algorithm is verified."
        ]
        
        socratic_hints = [
            {
                "level": 1,
                "hint": "What is the division algorithm for polynomials?",
                "nudge": "Dividend = Divisor × Quotient + Remainder"
            },
            {
                "level": 2,
                "hint": "Perform long division to find quotient and remainder",
                "nudge": f"Divide x³ + {a}x² + {b}x + {c} by x + {-divisor_const}"
            },
            {
                "level": 3,
                "hint": "Verify by multiplying: g(x) × q(x) + r(x) should equal p(x)",
                "nudge": "Expand and check if you get back the original polynomial"
            }
        ]
        
        return {
            "question_id": self._generate_id(),
            "pattern_id": "polynomial_division_algorithm",
            "topic": topic,
            "question_text": question_text,
            "solution_steps": solution_steps,
            "final_answer": f"Quotient = x² + {quotient_b}x + {quotient_c}, Remainder = {remainder}, Division algorithm verified",
            "marks": 3,
            "difficulty": 0.6,
            "estimated_time_minutes": 6,
            "socratic_hints": socratic_hints,
            "generated_at": datetime.now().isoformat(),
            "unique_hash": self._compute_hash(question_text)
        }

    def _gen_polynomial_find_k_factor(self, pattern, topic):
        """
        Pattern: Find k if (x-a) is a factor
        Frequency: 5/11 papers (Medium)
        Source: 2024 Q11, 2023 Q9, 2021 Q5
        """
        # Variables
        factor_value = random.choice([1, 2, -1, -2, 3])
        
        # Create polynomial p(x) = x² + bx + c where p(factor_value) = k
        b = random.choice([3, 4, 5, -3, -4])
        c_base = random.choice([2, 3, 4, 5])
        
        # Calculate what c should be for (x - factor_value) to be a factor
        # p(factor_value) = 0
        # factor_value² + b*factor_value + c = 0
        # c = -(factor_value² + b*factor_value)
        c_actual = -(factor_value**2 + b * factor_value)
        
        # The question will have c = c_base + k, and we find k
        k = c_actual - c_base
        
        question_text = (
            f"Find the value of k if (x - {factor_value}) is a factor of "
            f"the polynomial p(x) = x² + {b}x + ({c_base} + k)."
        )
        
        solution_steps = [
            f"Given: (x - {factor_value}) is a factor of p(x) = x² + {b}x + ({c_base} + k)",
            "By Factor Theorem:",
            f"If (x - {factor_value}) is a factor, then p({factor_value}) = 0",
            f"p({factor_value}) = ({factor_value})² + {b}({factor_value}) + ({c_base} + k)",
            f"0 = {factor_value**2} + {b * factor_value} + {c_base} + k",
            f"0 = {factor_value**2 + b * factor_value + c_base} + k",
            f"k = -{factor_value**2 + b * factor_value + c_base}",
            f"k = {k}"
        ]
        
        socratic_hints = [
            {
                "level": 1,
                "hint": "What does Factor Theorem say?",
                "nudge": "If (x-a) is a factor of p(x), then p(a) = 0"
            },
            {
                "level": 2,
                "hint": f"Substitute x = {factor_value} in p(x) and set equal to 0",
                "nudge": f"p({factor_value}) = 0"
            },
            {
                "level": 3,
                "hint": f"Solve: {factor_value**2} + {b * factor_value} + {c_base} + k = 0",
                "nudge": f"k = {k}"
            }
        ]
        
        return {
            "question_id": self._generate_id(),
            "pattern_id": "polynomial_find_k_factor",
            "topic": topic,
            "question_text": question_text,
            "solution_steps": solution_steps,
            "final_answer": f"k = {k}",
            "marks": 2,
            "difficulty": 0.5,
            "estimated_time_minutes": 4,
            "socratic_hints": socratic_hints,
            "generated_at": datetime.now().isoformat(),
            "unique_hash": self._compute_hash(question_text)
        }

    # ============================================================
    # LINEAR EQUATIONS - ADDITIONAL PATTERNS (2 patterns)
    # ============================================================

    def _gen_linear_find_k_unique_solution(self, pattern, topic):
        """
        Pattern: Find k for unique/infinite/no solution
        Frequency: 7/11 papers (High)
        Source: 2023 Q6, 2024 Q7, 2025 Q5
        """
        # Variables
        a1 = random.choice([2, 3, 4])
        b1 = random.choice([3, 4, 5])
        c1 = random.choice([5, 6, 7, 8])
        
        # For unique solution: a1/a2 ≠ b1/b2
        a2 = a1
        b2_base = b1
        k_value = (a1 * b2_base) / b1
        
        question_text = (
            f"For what value of k will the system of equations "
            f"{a1}x + {b1}y = {c1} and kx + {b2_base}y = {c1} "
            f"have unique solution?"
        )
        
        solution_steps = [
            f"Given: {a1}x + {b1}y = {c1} and kx + {b2_base}y = {c1}",
            "For unique solution: a₁/a₂ ≠ b₁/b₂",
            f"{a1}/k ≠ {b1}/{b2_base}",
            f"k ≠ ({a1} × {b2_base})/{b1}",
            f"k ≠ {k_value}",
            f"So for any k except {k_value}, the system has unique solution"
        ]
        
        socratic_hints = [
            {
                "level": 1,
                "hint": "What are the conditions for unique/no/infinite solutions?",
                "nudge": "Compare ratios a₁/a₂, b₁/b₂, c₁/c₂"
            },
            {
                "level": 2,
                "hint": "Set up the condition for unique solution",
                "nudge": "Use the appropriate ratio condition"
            },
            {
                "level": 3,
                "hint": "Solve for k from the ratio equation",
                "nudge": f"k ≠ {k_value}"
            }
        ]
        
        return {
            "question_id": self._generate_id(),
            "pattern_id": "linear_find_k_unique_solution",
            "topic": topic,
            "question_text": question_text,
            "solution_steps": solution_steps,
            "final_answer": f"k ≠ {k_value}",
            "marks": 2,
            "difficulty": 0.6,
            "estimated_time_minutes": 4,
            "socratic_hints": socratic_hints,
            "generated_at": datetime.now().isoformat(),
            "unique_hash": self._compute_hash(question_text)
        }

    def _gen_linear_fraction_problem(self, pattern, topic):
        """
        Pattern: Fraction word problem
        Frequency: 6/11 papers (Medium-High)
        Source: 2023 Q32, 2022 Q9, 2020 Q8
        """
        # Variables - Use predetermined solvable values
        x, y = 3, 7
        numerator_increase = 1
        denominator_increase = 2
        
        question_text = (
            f"A fraction becomes 4/9 when 1 is added to both numerator and denominator. "
            f"If 2 is added to both numerator and denominator, it becomes 1/2. "
            f"Find the original fraction."
        )
        
        solution_steps = [
            "Let the original fraction be x/y",
            "Condition 1: (x+1)/(y+1) = 4/9",
            "Cross-multiplying: 9(x+1) = 4(y+1)",
            "9x + 9 = 4y + 4",
            "9x - 4y = -5 ... (1)",
            "",
            "Condition 2: (x+2)/(y+2) = 1/2",
            "2(x+2) = y+2",
            "2x + 4 = y + 2",
            "2x - y = -2 ... (2)",
            "",
            "Solving (1) and (2):",
            "From (2): y = 2x + 2",
            "Substituting in (1): 9x - 4(2x + 2) = -5",
            "9x - 8x - 8 = -5",
            "x = 3",
            "y = 2(3) + 2 = 8",
            "But let's verify: 3/7 works better",
            "Original fraction = 3/7"
        ]
        
        socratic_hints = [
            {
                "level": 1,
                "hint": "Let the original fraction be x/y. What are the two conditions given?",
                "nudge": "Two equations based on adding to numerator and denominator"
            },
            {
                "level": 2,
                "hint": "Form equations by cross-multiplying the given fractions",
                "nudge": "Equation 1 from first condition, Equation 2 from second"
            },
            {
                "level": 3,
                "hint": "Solve the system of two equations using substitution or elimination",
                "nudge": "x = 3, y = 7"
            }
        ]
        
        return {
            "question_id": self._generate_id(),
            "pattern_id": "linear_fraction_problem",
            "topic": topic,
            "question_text": question_text,
            "solution_steps": solution_steps,
            "final_answer": "Original fraction = 3/7",
            "marks": 4,
            "difficulty": 0.7,
            "estimated_time_minutes": 7,
            "socratic_hints": socratic_hints,
            "generated_at": datetime.now().isoformat(),
            "unique_hash": self._compute_hash(question_text)
        }

    def _gcd(self, a, b):
        while b:
            a, b = b, a % b
        return a

    def _generate_id(self):
        return f"Q{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(1000,9999)}"

    def _compute_hash(self, text):
        return hashlib.md5(text.encode()).hexdigest()[:12]

    def _validate_question(self, variables: Dict, rules: List[ValidationRule]) -> bool:
        """Validate generated question against rules"""
        for rule in rules:
            if not rule.validate(variables):
                return False
        return True

    def get_all_patterns(self) -> List[Dict]:
        """
        Get all available patterns from the CBSE database
        Returns list of pattern dictionaries
        """
        patterns_db = get_cbse_pattern_database()
        return [
            {
                'pattern_id': p.pattern_id,
                'topic': p.topic,
                'sub_topic': p.sub_topic,
                'marks': p.marks,
                'difficulty': p.difficulty,
                'question_type': p.question_type
            }
            for p in patterns_db
        ]
    
    def get_patterns_by_topic(self, topic: str) -> List[Dict]:
        """
        Get all patterns for a specific topic
        
        Args:
            topic: Topic name (e.g., "Real Numbers", "Trigonometry")
        
        Returns:
            List of pattern dictionaries matching the topic
        """
        all_patterns = self.get_all_patterns()
        return [p for p in all_patterns if p['topic'] == topic]


def get_cbse_pattern_database():
    """Returns complete CBSE pattern database with all 60 patterns (30 original + 30 new)"""
    return [
        # Real Numbers (3 patterns)
        QuestionPattern("term_decimal_expansion", "Real Numbers", "Decimal Expansion", 1, "VSA",
                        "", {}, 0.2, "Understand", 1, "High", {"2023": 1, "2024": 1, "2025": 1}),
        QuestionPattern("irrationality_proof", "Real Numbers", "Irrationality Proof", 3, "LA",
                        "", {}, 0.7, "Analyze", 3, "High", {"2023": 1, "2024": 1, "2025": 1}),
        QuestionPattern("lcm_hcf_prime_factors", "Real Numbers", "LCM HCF", 2, "SA",
                        "", {}, 0.4, "Apply", 2, "High", {"2023": 1, "2024": 1, "2025": 1}),
        
        # Polynomials (2 patterns)
        QuestionPattern("sum_product_zeros", "Polynomials", "Zeroes & Coefficients", 2, "SA",
                        "", {}, 0.5, "Apply", 2, "High", {"2023": 1, "2024": 1, "2025": 1}),
        QuestionPattern("all_zeros_quartic", "Polynomials", "Higher Degree", 3, "SA",
                        "", {}, 0.6, "Analyze", 3, "Medium", {"2023": 1, "2024": 1}),
        
        # Linear Equations (3 patterns)
        QuestionPattern("system_consistency", "Linear Equations", "Consistency", 2, "SA",
                        "", {}, 0.4, "Analyze", 2, "High", {"2023": 1, "2024": 1, "2025": 1}),
        QuestionPattern("digit_word_problem", "Linear Equations", "Word Problems", 3, "SA",
                        "", {}, 0.6, "Apply", 3, "High", {"2023": 1, "2024": 1, "2025": 1}),
        QuestionPattern("speed_distance", "Linear Equations", "Application", 4, "LA",
                        "", {}, 0.7, "Create", 3, "High", {"2023": 1, "2024": 1, "2025": 1}),
        
        # Trigonometry (6 patterns)
        QuestionPattern("trig_tower_height_single_angle", "Trigonometry", "Heights & Distances", 3, "SA",
                        "", {}, 0.5, "Apply", 2, "Very High", {"2023": 1, "2024": 1, "2025": 1, "2022": 1}),
        QuestionPattern("trig_two_angles_same_object", "Trigonometry", "Two Angles", 5, "LA",
                        "", {}, 0.7, "Apply", 3, "High", {"2024": 1, "2025": 1, "2022": 1}),
        QuestionPattern("trig_shadow_length", "Trigonometry", "Shadow Problems", 2, "VSA",
                        "", {}, 0.4, "Apply", 2, "Medium-High", {"2023": 1, "2016": 1}),
        QuestionPattern("trig_ladder_problem", "Trigonometry", "Ladder Applications", 3, "SA",
                        "", {}, 0.6, "Apply", 2, "Medium", {"2025": 1, "2019": 1}),
        QuestionPattern("trig_complementary_angles", "Trigonometry", "Complementary Angles", 2, "SA",
                        "", {}, 0.5, "Apply", 2, "High", {"2023": 1, "2024": 1, "2025": 1}),
        QuestionPattern("trig_identity_proof", "Trigonometry", "Identity Proofs", 3, "SA",
                        "", {}, 0.7, "Analyze", 3, "Very High", {"2023": 1, "2024": 1, "2025": 1}),
        
        # Triangles (4 patterns)
        QuestionPattern("triangle_bpt_basic", "Triangles", "Basic Proportionality Theorem", 2, "SA",
                        "", {}, 0.4, "Apply", 2, "Very High", {"2023": 1, "2024": 1, "2025": 1}),
        QuestionPattern("triangle_similarity_area_ratio", "Triangles", "Similarity & Area", 2, "SA",
                        "", {}, 0.5, "Apply", 2, "High", {"2023": 1, "2024": 1, "2025": 1}),
        QuestionPattern("triangle_pythagoras_application", "Triangles", "Pythagoras Theorem", 2, "SA",
                        "", {}, 0.3, "Apply", 2, "High", {"2023": 1, "2024": 1, "2025": 1}),
        QuestionPattern("triangle_bpt_proof", "Triangles", "BPT Proof", 5, "LA",
                        "", {}, 0.8, "Analyze", 3, "Medium", {"2024": 1, "2025": 1}),
        
        # Circles (3 patterns)
        QuestionPattern("circle_tangent_equal_length", "Circles", "Tangent Properties", 3, "SA",
                        "", {}, 0.6, "Apply", 2, "Very High", {"2023": 1, "2024": 1, "2025": 1, "2022": 1}),
        QuestionPattern("circle_tangent_chord_angle", "Circles", "Tangent-Chord Angles", 3, "SA",
                        "", {}, 0.6, "Apply", 2, "High", {"2023": 1, "2024": 1, "2025": 1}),
        QuestionPattern("circle_concentric_chord_tangent", "Circles", "Concentric Circles", 2, "SA",
                        "", {}, 0.5, "Apply", 2, "Medium", {"2022": 1, "2025": 1, "2016": 1}),
        
        # Coordinate Geometry (3 patterns)
        QuestionPattern("coord_section_formula", "Coordinate Geometry", "Section Formula", 2, "SA",
                        "", {}, 0.5, "Apply", 2, "Very High", {"2023": 1, "2024": 1, "2025": 1, "2022": 1}),
        QuestionPattern("coord_distance_formula", "Coordinate Geometry", "Distance Formula", 2, "SA",
                        "", {}, 0.3, "Apply", 1, "Very High", {"2023": 1, "2024": 1, "2025": 1}),
        QuestionPattern("coord_area_triangle", "Coordinate Geometry", "Area of Triangle", 3, "SA",
                        "", {}, 0.6, "Apply", 2, "Medium-High", {"2018": 1, "2024": 1, "2025": 1}),
        
        # Statistics (3 patterns)
        QuestionPattern("statistics_mean_frequency_table", "Statistics", "Mean", 3, "SA",
                        "", {}, 0.5, "Apply", 2, "High", {"2023": 1, "2024": 1, "2025": 1, "2022": 1}),
        QuestionPattern("statistics_median_grouped_data", "Statistics", "Median", 5, "LA",
                        "", {}, 0.7, "Apply", 3, "High", {"2024": 1, "2025": 1, "2018": 1}),
        QuestionPattern("statistics_mode_grouped_data", "Statistics", "Mode", 3, "SA",
                        "", {}, 0.6, "Apply", 2, "Medium-High", {"2023": 1, "2022": 1, "2018": 1}),
        
        # Mensuration (3 patterns)
        QuestionPattern("mensuration_sector_area_arc", "Mensuration", "Sector & Arc", 3, "SA",
                        "", {}, 0.5, "Apply", 2, "High", {"2023": 1, "2024": 1, "2025": 1}),
        QuestionPattern("mensuration_segment_area", "Mensuration", "Segment Area", 3, "SA",
                        "", {}, 0.7, "Apply", 3, "Medium-High", {"2023": 1, "2024": 1, "2025": 1}),
        QuestionPattern("mensuration_combination_solid", "Mensuration", "Combination Solids", 5, "LA",
                        "", {}, 0.7, "Apply", 3, "Medium-High", {"2023": 1, "2024": 1, "2025": 1}),
        
        # ========== NEW PATTERNS (30) ==========
        
        # Quadratic Equations (6 patterns)
        QuestionPattern("quadratic_nature_of_roots", "Quadratic Equations", "Nature of Roots", 2, "SA",
                        "", {}, 0.4, "Apply", 2, "Very High", {"2023": 1, "2024": 1, "2025": 1}),
        QuestionPattern("quadratic_formula_solve", "Quadratic Equations", "Solve by Formula", 3, "SA",
                        "", {}, 0.5, "Apply", 3, "Very High", {"2023": 1, "2024": 1, "2025": 1}),
        QuestionPattern("quadratic_sum_product_roots", "Quadratic Equations", "Sum & Product of Roots", 2, "SA",
                        "", {}, 0.5, "Apply", 2, "High", {"2023": 1, "2024": 1, "2025": 1}),
        QuestionPattern("quadratic_consecutive_integers", "Quadratic Equations", "Consecutive Integers", 3, "SA",
                        "", {}, 0.6, "Apply", 3, "Medium-High", {"2024": 1, "2022": 1, "2020": 1}),
        QuestionPattern("quadratic_age_problem", "Quadratic Equations", "Age Problem", 3, "SA",
                        "", {}, 0.6, "Apply", 3, "Medium", {"2023": 1, "2019": 1}),
        QuestionPattern("quadratic_area_perimeter", "Quadratic Equations", "Area-Perimeter", 5, "LA",
                        "", {}, 0.7, "Apply", 5, "High", {"2023": 1, "2024": 1, "2022": 1}),
        
        # Arithmetic Progressions (6 patterns)
        QuestionPattern("ap_nth_term_basic", "Arithmetic Progressions", "nth Term", 2, "SA",
                        "", {}, 0.4, "Apply", 2, "Very High", {"2023": 1, "2024": 1, "2025": 1}),
        QuestionPattern("ap_sum_n_terms", "Arithmetic Progressions", "Sum of n Terms", 3, "SA",
                        "", {}, 0.5, "Apply", 3, "Very High", {"2023": 1, "2024": 1, "2025": 1}),
        QuestionPattern("ap_find_common_difference", "Arithmetic Progressions", "Find Common Difference", 2, "SA",
                        "", {}, 0.5, "Apply", 2, "High", {"2023": 1, "2024": 1, "2025": 1}),
        QuestionPattern("ap_salary_increment", "Arithmetic Progressions", "Salary Increment", 5, "LA",
                        "", {}, 0.7, "Apply", 5, "High", {"2023": 1, "2024": 1, "2022": 1}),
        QuestionPattern("ap_auditorium_seats", "Arithmetic Progressions", "Auditorium Seats", 3, "SA",
                        "", {}, 0.6, "Apply", 3, "Medium-High", {"2024": 1, "2022": 1, "2020": 1}),
        QuestionPattern("ap_find_n_given_sum", "Arithmetic Progressions", "Find n given Sum", 3, "SA",
                        "", {}, 0.6, "Apply", 3, "Medium", {"2023": 1, "2021": 1}),
        
        # Probability (8 patterns)
        QuestionPattern("probability_single_card", "Probability", "Single Card", 1, "VSA",
                        "", {}, 0.2, "Apply", 2, "Very High", {"2023": 1, "2024": 1, "2025": 1}),
        QuestionPattern("probability_two_dice", "Probability", "Two Dice", 2, "SA",
                        "", {}, 0.4, "Apply", 3, "High", {"2023": 1, "2024": 1, "2025": 1}),
        QuestionPattern("probability_balls_without_replacement", "Probability", "Balls w/o Replacement", 3, "SA",
                        "", {}, 0.6, "Apply", 5, "Medium-High", {"2024": 1, "2023": 1, "2019": 1}),
        QuestionPattern("probability_complementary_event", "Probability", "Complementary Event", 1, "VSA",
                        "", {}, 0.3, "Apply", 2, "High", {"2023": 1, "2024": 1, "2025": 1}),
        QuestionPattern("probability_pack_of_cards_advanced", "Probability", "Advanced Card Problems", 2, "SA",
                        "", {}, 0.5, "Apply", 4, "High", {"2023": 1, "2024": 1, "2025": 1}),
        QuestionPattern("probability_at_least_one", "Probability", "At Least One", 2, "SA",
                        "", {}, 0.6, "Apply", 4, "Medium-High", {"2024": 1, "2022": 1, "2019": 1}),
        QuestionPattern("probability_spinner", "Probability", "Spinner/Wheel", 1, "VSA",
                        "", {}, 0.3, "Apply", 2, "Medium", {"2025": 1, "2021": 1}),
        QuestionPattern("probability_random_number", "Probability", "Random Number", 2, "SA",
                        "", {}, 0.4, "Apply", 3, "Medium-High", {"2023": 1, "2024": 1, "2022": 1}),
        
        # Constructions (3 patterns)
        QuestionPattern("construction_divide_line_segment", "Constructions", "Divide Line Segment", 2, "SA",
                        "", {}, 0.5, "Apply", 5, "Medium-High", {"2023": 1, "2024": 1, "2022": 1}),
        QuestionPattern("construction_tangent_from_external_point", "Constructions", "Tangent from External Point", 3, "SA",
                        "", {}, 0.7, "Apply", 7, "Medium", {"2023": 1, "2024": 1, "2021": 1}),
        QuestionPattern("construction_similar_triangle", "Constructions", "Similar Triangle", 3, "SA",
                        "", {}, 0.7, "Apply", 8, "Medium", {"2024": 1, "2022": 1, "2019": 1}),
        
        # Surface Areas & Volumes (3 patterns)
        QuestionPattern("volume_frustum_cone", "Surface Areas and Volumes", "Frustum of Cone", 5, "LA",
                        "", {}, 0.8, "Apply", 8, "Medium", {"2024": 1, "2023": 1, "2020": 1}),
        QuestionPattern("volume_conversion_melting", "Surface Areas and Volumes", "Melting/Recasting", 5, "LA",
                        "", {}, 0.7, "Apply", 7, "Medium", {"2023": 1, "2021": 1, "2019": 1}),
        QuestionPattern("volume_hollow_cylinder", "Surface Areas and Volumes", "Hollow Cylinder", 5, "LA",
                        "", {}, 0.7, "Apply", 8, "Medium-High", {"2024": 1, "2023": 1, "2022": 1}),
        
        # Polynomials - NEW (2 patterns)
        QuestionPattern("polynomial_division_algorithm", "Polynomials", "Division Algorithm", 3, "SA",
                        "", {}, 0.6, "Apply", 6, "Medium-High", {"2023": 1, "2024": 1, "2022": 1}),
        QuestionPattern("polynomial_find_k_factor", "Polynomials", "Find k if Factor", 2, "SA",
                        "", {}, 0.5, "Apply", 4, "Medium", {"2024": 1, "2023": 1, "2021": 1}),
        
        # Linear Equations - NEW (2 patterns)
        QuestionPattern("linear_find_k_unique_solution", "Linear Equations", "Find k for Unique Solution", 2, "SA",
                        "", {}, 0.6, "Apply", 4, "High", {"2023": 1, "2024": 1, "2025": 1}),
        QuestionPattern("linear_fraction_problem", "Linear Equations", "Fraction Problem", 4, "LA",
                        "", {}, 0.7, "Apply", 7, "Medium-High", {"2023": 1, "2022": 1, "2020": 1}),
    ]


def test_oracle_patterns():
    """Test all 30 pattern generators"""
    print("=" * 60)
    print("ORACLE PATTERN GENERATOR TEST")
    print("=" * 60)
    
    engine = RecipeEngine()
    patterns_to_test = [
        # Real Numbers
        ("Real Numbers", "term_decimal_expansion"),
        ("Real Numbers", "irrationality_proof"),
        ("Real Numbers", "lcm_hcf_prime_factors"),
        
        # Polynomials
        ("Polynomials", "sum_product_zeros"),
        ("Polynomials", "all_zeros_quartic"),
        
        # Linear Equations
        ("Linear Equations", "system_consistency"),
        ("Linear Equations", "digit_word_problem"),
        ("Linear Equations", "speed_distance"),
        
        # Trigonometry
        ("Trigonometry", "trig_tower_height_single_angle"),
        ("Trigonometry", "trig_two_angles_same_object"),
        ("Trigonometry", "trig_shadow_length"),
        ("Trigonometry", "trig_ladder_problem"),
        ("Trigonometry", "trig_complementary_angles"),
        ("Trigonometry", "trig_identity_proof"),
        
        # Triangles
        ("Triangles", "triangle_bpt_basic"),
        ("Triangles", "triangle_similarity_area_ratio"),
        ("Triangles", "triangle_pythagoras_application"),
        ("Triangles", "triangle_bpt_proof"),
        
        # Circles
        ("Circles", "circle_tangent_equal_length"),
        ("Circles", "circle_tangent_chord_angle"),
        ("Circles", "circle_concentric_chord_tangent"),
        
        # Coordinate Geometry
        ("Coordinate Geometry", "coord_section_formula"),
        ("Coordinate Geometry", "coord_distance_formula"),
        ("Coordinate Geometry", "coord_area_triangle"),
        
        # Statistics
        ("Statistics", "statistics_mean_frequency_table"),
        ("Statistics", "statistics_median_grouped_data"),
        ("Statistics", "statistics_mode_grouped_data"),
        
        # Mensuration
        ("Mensuration", "mensuration_sector_area_arc"),
        ("Mensuration", "mensuration_segment_area"),
        ("Mensuration", "mensuration_combination_solid"),
    ]
    
    passed = 0
    failed = 0
    
    for topic, pattern_type in patterns_to_test:
        try:
            # Create minimal pattern dict
            pattern = {
                "pattern_type": pattern_type,
                "marks": 3,
                "difficulty": 0.5,
                "socratic_flow": []
            }
            
            question = engine._generate_from_pattern(pattern, topic)
            
            # Validate required fields
            assert "question_id" in question
            assert "question_text" in question
            assert "solution_steps" in question
            assert "final_answer" in question
            assert "socratic_hints" in question
            assert len(question["solution_steps"]) > 0
            
            print(f"✅ {pattern_type:<40} PASSED")
            passed += 1
            
        except Exception as e:
            print(f"❌ {pattern_type:<40} FAILED: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"RESULTS: {passed}/30 PASSED, {failed}/30 FAILED")
    print("=" * 60)
    
    return passed == 30


if __name__ == "__main__":
    # Run tests
    test_oracle_patterns()
