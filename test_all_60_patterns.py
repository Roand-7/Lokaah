"""
Test All 60 ORACLE Patterns (30 Original + 30 New)
===================================================
This script tests all pattern generators in oracle_engine.py
"""

import sys
sys.path.append('c:/Users/Lenovo/lokaah_app')

from app.oracle.oracle_engine import RecipeEngine

def test_all_patterns():
    """Test all 60 pattern generators"""
    print("=" * 80)
    print("TESTING ALL 60 ORACLE PATTERNS (30 ORIGINAL + 30 NEW)")
    print("=" * 80)
    
    engine = RecipeEngine()
    
    # Define all 60 patterns organized by topic
    all_patterns = {
        "Real Numbers (3)": [
            ("Real Numbers", "term_decimal_expansion"),
            ("Real Numbers", "irrationality_proof"),
            ("Real Numbers", "lcm_hcf_prime_factors"),
        ],
        
        "Polynomials (4)": [
            ("Polynomials", "sum_product_zeros"),
            ("Polynomials", "all_zeros_quartic"),
            ("Polynomials", "polynomial_division_algorithm"),  # NEW
            ("Polynomials", "polynomial_find_k_factor"),  # NEW
        ],
        
        "Linear Equations (5)": [
            ("Linear Equations", "system_consistency"),
            ("Linear Equations", "digit_word_problem"),
            ("Linear Equations", "speed_distance"),
            ("Linear Equations", "linear_find_k_unique_solution"),  # NEW
            ("Linear Equations", "linear_fraction_problem"),  # NEW
        ],
        
        "Quadratic Equations (6)": [
            ("Quadratic Equations", "quadratic_nature_of_roots"),  # NEW
            ("Quadratic Equations", "quadratic_formula_solve"),  # NEW
            ("Quadratic Equations", "quadratic_sum_product_roots"),  # NEW
            ("Quadratic Equations", "quadratic_consecutive_integers"),  # NEW
            ("Quadratic Equations", "quadratic_age_problem"),  # NEW
            ("Quadratic Equations", "quadratic_area_perimeter"),  # NEW
        ],
        
        "Arithmetic Progressions (6)": [
            ("Arithmetic Progressions", "ap_nth_term_basic"),  # NEW
            ("Arithmetic Progressions", "ap_sum_n_terms"),  # NEW
            ("Arithmetic Progressions", "ap_find_common_difference"),  # NEW
            ("Arithmetic Progressions", "ap_salary_increment"),  # NEW
            ("Arithmetic Progressions", "ap_auditorium_seats"),  # NEW
            ("Arithmetic Progressions", "ap_find_n_given_sum"),  # NEW
        ],
        
        "Trigonometry (6)": [
            ("Trigonometry", "trig_tower_height_single_angle"),
            ("Trigonometry", "trig_two_angles_same_object"),
            ("Trigonometry", "trig_shadow_length"),
            ("Trigonometry", "trig_ladder_problem"),
            ("Trigonometry", "trig_complementary_angles"),
            ("Trigonometry", "trig_identity_proof"),
        ],
        
        "Triangles (4)": [
            ("Triangles", "triangle_bpt_basic"),
            ("Triangles", "triangle_similarity_area_ratio"),
            ("Triangles", "triangle_pythagoras_application"),
            ("Triangles", "triangle_bpt_proof"),
        ],
        
        "Circles (3)": [
            ("Circles", "circle_tangent_equal_length"),
            ("Circles", "circle_tangent_chord_angle"),
            ("Circles", "circle_concentric_chord_tangent"),
        ],
        
        "Coordinate Geometry (3)": [
            ("Coordinate Geometry", "coord_section_formula"),
            ("Coordinate Geometry", "coord_distance_formula"),
            ("Coordinate Geometry", "coord_area_triangle"),
        ],
        
        "Probability (8)": [
            ("Probability", "probability_single_card"),  # NEW
            ("Probability", "probability_two_dice"),  # NEW
            ("Probability", "probability_balls_without_replacement"),  # NEW
            ("Probability", "probability_complementary_event"),  # NEW
            ("Probability", "probability_pack_of_cards_advanced"),  # NEW
            ("Probability", "probability_at_least_one"),  # NEW
            ("Probability", "probability_spinner"),  # NEW
            ("Probability", "probability_random_number"),  # NEW
        ],
        
        "Statistics (3)": [
            ("Statistics", "statistics_mean_frequency_table"),
            ("Statistics", "statistics_median_grouped_data"),
            ("Statistics", "statistics_mode_grouped_data"),
        ],
        
        "Constructions (3)": [
            ("Constructions", "construction_divide_line_segment"),  # NEW
            ("Constructions", "construction_tangent_from_external_point"),  # NEW
            ("Constructions", "construction_similar_triangle"),  # NEW
        ],
        
        "Mensuration (3)": [
            ("Mensuration", "mensuration_sector_area_arc"),
            ("Mensuration", "mensuration_segment_area"),
            ("Mensuration", "mensuration_combination_solid"),
        ],
        
        "Surface Areas & Volumes (3)": [
            ("Surface Areas and Volumes", "volume_frustum_cone"),  # NEW
            ("Surface Areas and Volumes", "volume_conversion_melting"),  # NEW
            ("Surface Areas and Volumes", "volume_hollow_cylinder"),  # NEW
        ],
    }
    
    total_patterns = sum(len(patterns) for patterns in all_patterns.values())
    print(f"\n📊 Total Patterns to Test: {total_patterns}")
    print()
    
    passed = 0
    failed = 0
    failed_patterns = []
    
    for category, patterns in all_patterns.items():
        print(f"\n{'='*80}")
        print(f"📁 {category}")
        print('='*80)
        
        for topic, pattern_type in patterns:
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
                assert "question_id" in question, "Missing question_id"
                assert "question_text" in question, "Missing question_text"
                assert "solution_steps" in question, "Missing solution_steps"
                assert "final_answer" in question, "Missing final_answer"
                assert "socratic_hints" in question, "Missing socratic_hints"
                assert len(question["solution_steps"]) > 0, "Empty solution_steps"
                assert len(question["socratic_hints"]) > 0, "No socratic hints"
                
                # Check question text is not empty
                assert len(question["question_text"]) > 10, "Question text too short"
                
                passed += 1
                print(f"  ✅ {pattern_type:<50} PASSED")
                
                # Show sample question
                if pattern_type.startswith(('quadratic_', 'ap_', 'probability_', 'construction_', 'volume_', 'polynomial_', 'linear_')):
                    print(f"      Sample: {question['question_text'][:80]}...")
                
            except Exception as e:
                failed += 1
                failed_patterns.append((pattern_type, str(e)))
                print(f"  ❌ {pattern_type:<50} FAILED")
                print(f"      Error: {str(e)}")
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"✅ Passed: {passed}/{total_patterns}")
    print(f"❌ Failed: {failed}/{total_patterns}")
    print(f"📊 Success Rate: {(passed/total_patterns)*100:.1f}%")
    
    if failed_patterns:
        print("\n❌ Failed Patterns:")
        for pattern, error in failed_patterns:
            print(f"  - {pattern}: {error}")
    else:
        print("\n🎉 ALL 60 PATTERNS PASSED! 🎉")
    
    print("\n" + "=" * 80)
    
    return passed == total_patterns


def test_pattern_database():
    """Test that pattern database has all 60 patterns"""
    from app.oracle.oracle_engine import get_cbse_pattern_database
    
    print("\n" + "=" * 80)
    print("TESTING PATTERN DATABASE")
    print("=" * 80)
    
    patterns = get_cbse_pattern_database()
    print(f"\n📊 Total patterns in database: {len(patterns)}")
    
    # Count by topic
    topic_counts = {}
    for pattern in patterns:
        topic = pattern.topic
        topic_counts[topic] = topic_counts.get(topic, 0) + 1
    
    print("\n📁 Patterns by Topic:")
    for topic, count in sorted(topic_counts.items()):
        print(f"  {topic:<30} {count:>3} patterns")
    
    expected = 60
    if len(patterns) == expected:
        print(f"\n✅ Database has correct number of patterns: {expected}")
        return True
    else:
        print(f"\n❌ Expected {expected} patterns, found {len(patterns)}")
        return False


def generate_sample_questions():
    """Generate sample questions from new patterns"""
    print("\n" + "=" * 80)
    print("SAMPLE QUESTIONS FROM NEW PATTERNS")
    print("=" * 80)
    
    engine = RecipeEngine()
    
    sample_patterns = [
        ("Quadratic Equations", "quadratic_nature_of_roots"),
        ("Arithmetic Progressions", "ap_nth_term_basic"),
        ("Probability", "probability_single_card"),
        ("Constructions", "construction_divide_line_segment"),
        ("Surface Areas and Volumes", "volume_frustum_cone"),
    ]
    
    for topic, pattern_type in sample_patterns:
        pattern = {
            "pattern_type": pattern_type,
            "marks": 3,
            "difficulty": 0.5,
            "socratic_flow": []
        }
        
        question = engine._generate_from_pattern(pattern, topic)
        
        print(f"\n{'─'*80}")
        print(f"📝 Pattern: {pattern_type}")
        print(f"📚 Topic: {topic}")
        print(f"{'─'*80}")
        print(f"\n❓ QUESTION:\n{question['question_text']}")
        print(f"\n💡 ANSWER:\n{question['final_answer']}")
        print(f"\n🔑 SOLUTION STEPS ({len(question['solution_steps'])} steps)")
        for i, step in enumerate(question['solution_steps'][:3], 1):
            print(f"  {i}. {step}")
        if len(question['solution_steps']) > 3:
            print(f"  ... and {len(question['solution_steps']) - 3} more steps")
        print(f"\n🤔 SOCRATIC HINTS: {len(question['socratic_hints'])} levels")


if __name__ == "__main__":
    print("\n🚀 Starting Comprehensive Pattern Test...\n")
    
    # Test 1: Pattern Database
    db_pass = test_pattern_database()
    
    # Test 2: All Pattern Generators
    gen_pass = test_all_patterns()
    
    # Test 3: Generate Sample Questions
    if gen_pass:
        generate_sample_questions()
    
    # Final Result
    print("\n" + "=" * 80)
    print("FINAL RESULT")
    print("=" * 80)
    if db_pass and gen_pass:
        print("✅ ALL TESTS PASSED - ORACLE ENGINE READY FOR PRODUCTION!")
    else:
        print("❌ SOME TESTS FAILED - PLEASE REVIEW ERRORS ABOVE")
    print("=" * 80 + "\n")
