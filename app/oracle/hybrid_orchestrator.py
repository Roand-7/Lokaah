"""
HYBRID ORACLE ORCHESTRATOR
50% Hardcoded Patterns (reliable) + 50% AI Generation (infinite)
Intelligently routes between the two based on context
"""

import random
import time
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

# Import both systems
from .true_ai_oracle import TrueAIOracle
from .pattern_manager import PatternManager


@dataclass
class HybridQuestion:
    """Unified question format from either source"""
    question_id: str
    question_text: str
    solution_steps: List[str]
    final_answer: str
    socratic_hints: List[Dict]
    difficulty: float
    marks: int
    source: str  # "pattern" or "ai"
    concept: str
    jsxgraph_code: Optional[str] = None
    variables: Optional[Dict] = None
    generation_time_ms: float = 0


class HybridOrchestrator:
    """
    Central controller: Decides 50/50 split between Pattern ORACLE and AI ORACLE
    """
    
    def __init__(self, ai_ratio: float = 0.5):
        """
        Args:
            ai_ratio: Percentage of questions from AI (0.0 to 1.0)
                     Default 0.5 = 50% AI, 50% Patterns
        """
        self.ai_ratio = ai_ratio
        self.pattern_ratio = 1.0 - ai_ratio
        
        # Initialize both engines
        print("Initializing Hybrid Orchestrator...")
        self.pattern_manager = PatternManager()  # NEW: Use PatternManager instead of RecipeEngine
        self.ai_oracle = TrueAIOracle()

        # Statistics
        self.stats = {
            "total_generated": 0,
            "pattern_count": 0,
            "ai_count": 0,
            "avg_generation_time_ms": 0
        }

        # Smart routing logic
        self.concept_history = {}  # Track which concepts need AI vs Pattern

        # Get pattern stats
        pattern_stats = self.pattern_manager.get_stats()

        print("Hybrid Orchestrator ready")
        print(f"   - Pattern Manager: {pattern_stats['total_patterns']} patterns loaded")
        print(f"   - Topics covered: {', '.join(list(pattern_stats['topics'].keys())[:5])}...")
        print(f"   - AI Engine: Gemini-only")
        print(f"   - Split: {int(self.pattern_ratio*100)}% Pattern / {int(self.ai_ratio*100)}% AI")
    
    def generate_question(
        self,
        concept: str,
        marks: int,
        difficulty: float,
        force_source: Optional[str] = None,
        student_id: Optional[str] = None
    ) -> HybridQuestion:
        """
        Generate question using 50-50 split (or forced source)
        """
        start_time = time.time()
        
        # Decide source
        if force_source:
            source = force_source
        else:
            source = self._decide_source(concept, student_id)
        
        # Route to appropriate engine
        if source == "ai":
            result = self._generate_from_ai(concept, marks, difficulty)
            self.stats["ai_count"] += 1
        else:
            result = self._generate_from_pattern(concept, marks, difficulty)
            self.stats["pattern_count"] += 1
        
        # Track timing
        generation_time = (time.time() - start_time) * 1000
        result.generation_time_ms = generation_time
        
        # Update stats
        self.stats["total_generated"] += 1
        self._update_avg_time(generation_time)
        
        return result
    
    def _decide_source(self, concept: str, student_id: Optional[str]) -> str:
        """
        Smart routing: Decide whether to use Pattern or AI
        """
        # Always use patterns for these (reliable, fast, exam-accurate, 100% math accuracy):
        pattern_preferred = [
            # Quadratic Equations - perfect for patterns
            "quadratic_nature_of_roots", "quadratic_formula_solve", "quadratic_sum_product_roots",
            "quadratic_consecutive_integers", "quadratic_age_problem",
            # AP - formula-based
            "ap_nth_term_basic", "ap_sum_n_terms", "ap_find_common_difference",
            "ap_salary_increment", "ap_auditorium_seats",
            # Coordinate Geometry - always same formulas
            "coord_distance_formula", "coord_section_formula", "coord_area_triangle",
            # Probability - standard CBSE format
            "probability_single_card", "probability_two_dice", "probability_balls_without_replacement",
            # Real Numbers & Polynomials
            "terminating_decimal", "irrationality_proof", "lcm_hcf",
            "polynomial_sum_product", "polynomial_division_algorithm",
        ]

        # Always use AI for these (needs creativity, context):
        ai_preferred = [
            "word_problem_real_world",    # Needs unique scenarios
            "application_problem",        # Needs Indian context
            "visual_geometry",           # Needs JSXGraph
            "creative_scenario",         # Novel situations
        ]

        # Check forced preferences
        if any(p in concept for p in pattern_preferred):
            return "pattern"
        if any(a in concept for a in ai_preferred):
            return "ai"

        # Check student history (if student struggling, use AI for variety)
        if student_id and student_id in self.concept_history:
            history = self.concept_history[student_id]
            if concept in history:
                if history[concept]["wrong_attempts"] >= 2:
                    # Student stuck - give AI-generated fresh perspective
                    return "ai"

        # Default: Random 50-50 split
        return "ai" if random.random() < self.ai_ratio else "pattern"
    
    def _generate_from_pattern(self, concept: str, marks: int, difficulty: float) -> HybridQuestion:
        """Generate from JSON pattern templates (fast, reliable, zero-hallucination)"""

        # Map legacy concept names to pattern_ids
        pattern_id = self._map_concept_to_pattern(concept)

        # If no direct mapping, search by topic/marks/difficulty
        if not self.pattern_manager.get_pattern(pattern_id):
            patterns = self.pattern_manager.find_patterns(marks=marks)
            if patterns:
                # Select by difficulty match
                best_pattern = min(patterns,
                                 key=lambda p: abs(p.difficulty - difficulty))
                pattern_id = best_pattern.pattern_id
            else:
                # Fallback to first available pattern
                all_patterns = list(self.pattern_manager._cache.values())
                pattern_id = all_patterns[0].pattern_id if all_patterns else "quadratic_nature_of_roots"

        # Generate using PatternManager
        try:
            result = self.pattern_manager.generate_question(pattern_id)
        except Exception as e:
            print(f"[WARN] Pattern generation failed for {pattern_id}: {e}")
            # Fallback to a known working pattern
            result = self.pattern_manager.generate_question("quadratic_nature_of_roots")

        return HybridQuestion(
            question_id=result["question_id"],
            question_text=result["question_text"],
            solution_steps=result["solution_steps"],
            final_answer=result["final_answer"],
            socratic_hints=result["socratic_hints"],
            difficulty=result["difficulty"],
            marks=result["marks"],
            source="pattern",
            concept=result["topic"],
            jsxgraph_code=None,  # JSXGraph enhancement coming in Phase 4
            variables=result.get("variables")
        )

    def _map_concept_to_pattern(self, concept: str) -> str:
        """Map legacy concept strings to new pattern_ids"""
        # Direct pattern mappings
        concept_map = {
            "trigonometry_heights": "trig_tower_height_single_angle",
            "trigonometry": "trig_identity_proof",
            "triangle_bpt_basic": "triangle_bpt_basic",
            "triangle": "triangle_similarity_area_ratio",
            "circle_tangent_equal_length": "circle_tangent_equal_length",
            "circle": "circle_concentric_chord_tangent",
            "coord_distance_formula": "coord_distance_formula",
            "coordinate": "coord_section_formula",
            "statistics_mean_frequency_table": "statistics_mean_frequency_table",
            "statistics": "statistics_median_grouped_data",
            "probability_single_card": "probability_single_card",
            "probability": "probability_two_dice",
            "quadratic_formula_solve": "quadratic_formula_solve",
            "quadratic": "quadratic_nature_of_roots",
            "linear_equations": "consistency",
            "linear": "digit_problem",
            "ap_nth_term_basic": "ap_nth_term_basic",
            "ap_sum_n_terms": "ap_sum_n_terms",
            "ap": "ap_salary_increment",
            "progression": "ap_auditorium_seats",
            "polynomial": "polynomial_sum_product",
            "real_numbers": "terminating_decimal",
            "algebra": "polynomial_division_algorithm",
            "geometry": "mensuration_sector_area_arc",
            "mensuration": "volume_frustum_cone",
        }

        # Check if concept is already a pattern_id
        if self.pattern_manager.get_pattern(concept):
            return concept

        # Try exact match
        if concept in concept_map:
            return concept_map[concept]

        # Try partial match
        for key, pattern_id in concept_map.items():
            if key in concept or concept in key:
                return pattern_id

        # Default fallback
        return "quadratic_nature_of_roots"
    
    def _generate_from_ai(self, concept: str, marks: int, difficulty: float) -> HybridQuestion:
        """Generate from AI Oracle (creative, infinite, contextual)"""
        
        ai_result = self.ai_oracle.generate_question(
            concept=concept,
            marks=marks,
            difficulty=difficulty
        )
        
        # Convert to HybridQuestion format
        return HybridQuestion(
            question_id=f"AI_{random.randint(10000,99999)}_{int(time.time())}",
            question_text=ai_result.question_text,
            solution_steps=ai_result.solution_steps,
            final_answer=ai_result.final_answer,
            socratic_hints=[
                {"level": 1, "hint": "Analyze the problem carefully", "nudge": "What is given and what is asked?"},
                {"level": 2, "hint": f"This involves {concept}", "nudge": "Recall the relevant formula"},
                {"level": 3, "hint": "Substitute the values", "nudge": "Calculate step by step"}
            ],
            difficulty=difficulty,
            marks=marks,
            source="ai",
            concept=concept,
            jsxgraph_code=ai_result.jsxgraph_code,
            variables=ai_result.variables
        )
    
    def generate_exam(
        self,
        chapters: List[int],
        total_marks: int = 80,
        duration_minutes: int = 180
    ) -> Dict:
        """
        Generate complete CBSE exam with 50-50 split
        """
        exam_structure = self._get_cbse_exam_structure()
        questions = []
        
        for section in exam_structure:
            for i in range(section["num_questions"]):
                # Alternate between pattern and AI for variety
                force_source = "ai" if i % 2 == 0 else "pattern"
                
                q = self.generate_question(
                    concept=random.choice(["trigonometry", "algebra", "geometry"]),
                    marks=section["marks"],
                    difficulty=self._marks_to_difficulty(section["marks"]),
                    force_source=force_source
                )
                questions.append(asdict(q))
        
        return {
            "exam_id": f"EXAM_{int(time.time())}",
            "questions": questions,
            "total_marks": total_marks,
            "duration_minutes": duration_minutes,
            "ai_percentage": int(self.stats["ai_count"] / max(1, self.stats["total_generated"]) * 100),
            "pattern_percentage": int(self.stats["pattern_count"] / max(1, self.stats["total_generated"]) * 100)
        }
    
    def _get_cbse_exam_structure(self) -> List[Dict]:
        """CBSE Class 10 2025-26 exam format"""
        return [
            {"section": "A", "marks": 1, "num_questions": 18},  # MCQ/VSA
            {"section": "B", "marks": 2, "num_questions": 5},   # VSA
            {"section": "C", "marks": 3, "num_questions": 6},   # SA
            {"section": "D", "marks": 5, "num_questions": 4},   # LA
            {"section": "E", "marks": 4, "num_questions": 3},   # Case Study
        ]
    
    def _marks_to_difficulty(self, marks: int) -> float:
        """Convert marks to difficulty score"""
        mapping = {1: 0.3, 2: 0.45, 3: 0.6, 4: 0.7, 5: 0.8}
        return mapping.get(marks, 0.5)
    
    def _update_avg_time(self, new_time: float):
        """Update running average"""
        n = self.stats["total_generated"]
        old_avg = self.stats["avg_generation_time_ms"]
        self.stats["avg_generation_time_ms"] = ((old_avg * (n-1)) + new_time) / n
    
    def get_recommendation(self, concept: str, wrong_attempts: int) -> str:
        """
        Recommend which source to use based on student performance
        """
        if wrong_attempts >= 3:
            return "ai"  # Need fresh approach
        elif wrong_attempts >= 1:
            return "pattern"  # Practice standard format
        else:
            return "mixed"
    
    def get_stats(self) -> Dict:
        """Return generation statistics"""
        return {
            **self.stats,
            "ai_ratio_configured": self.ai_ratio,
            "pattern_ratio_configured": self.pattern_ratio,
            "pattern_manager_stats": self.pattern_manager.get_stats(),
            "ai_engine_stats": self.ai_oracle.get_stats() if hasattr(self.ai_oracle, "get_stats") else {}
        }


# Singleton instance for app-wide use
_orchestrator_instance = None

def get_hybrid_orchestrator(ai_ratio: float = 0.5) -> HybridOrchestrator:
    """Get or create singleton instance"""
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = HybridOrchestrator(ai_ratio=ai_ratio)
    return _orchestrator_instance


# Test function
if __name__ == "__main__":
    orch = HybridOrchestrator(ai_ratio=0.5)

    print("\n" + "="*70)
    print("HYBRID ORCHESTRATOR TEST - PatternManager Integration")
    print("="*70)

    # Test various pattern types
    test_concepts = [
        ("quadratic_nature_of_roots", 2, 0.5),
        ("trig_tower_height_single_angle", 3, 0.6),
        ("probability_single_card", 2, 0.4),
        ("ap_nth_term_basic", 2, 0.5),
        ("coord_distance_formula", 3, 0.6),
        ("polynomial_sum_product", 2, 0.5),
    ]

    for i, (concept, marks, difficulty) in enumerate(test_concepts, 1):
        q = orch.generate_question(
            concept=concept,
            marks=marks,
            difficulty=difficulty
        )
        print(f"\n{i}. [{q.source.upper()}] {concept}")
        print(f"   Q: {q.question_text[:80]}...")
        print(f"   A: {q.final_answer}")
        print(f"   Time: {q.generation_time_ms:.1f}ms")

    print("\n" + "="*70)
    print("FINAL STATS:")
    stats = orch.get_stats()
    print(f"   Total: {stats['total_generated']}")
    print(f"   Pattern: {stats['pattern_count']} ({stats['pattern_count']/max(1,stats['total_generated'])*100:.0f}%)")
    print(f"   AI: {stats['ai_count']} ({stats['ai_count']/max(1,stats['total_generated'])*100:.0f}%)")
    print(f"   Avg time: {stats['avg_generation_time_ms']:.1f}ms")

    print("\n" + "="*70)
    print("PATTERN MANAGER STATS:")
    pm_stats = stats['pattern_manager_stats']
    print(f"   Total patterns: {pm_stats['total_patterns']}")
    print(f"   Topics: {len(pm_stats['topics'])}")
    for topic, count in list(pm_stats['topics'].items())[:10]:
        print(f"     - {topic}: {count} patterns")

