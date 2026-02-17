"""
Test ORACLE Integration with PatternManager
Verifies that Hybrid Orchestrator correctly uses the 60 validated patterns
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.oracle.hybrid_orchestrator import HybridOrchestrator


def test_pattern_generation():
    """Test that patterns generate correctly"""
    print("\n" + "="*70)
    print("TEST 1: Pattern Generation")
    print("="*70)

    orch = HybridOrchestrator(ai_ratio=0.0)  # Force 100% patterns

    # Test 10 different pattern types
    test_patterns = [
        "quadratic_nature_of_roots",
        "trig_tower_height_single_angle",
        "probability_single_card",
        "ap_nth_term_basic",
        "coord_distance_formula",
        "polynomial_sum_product",
        "terminating_decimal",
        "circle_tangent_equal_length",
        "triangle_similarity_area_ratio",
        "statistics_mean_frequency_table",
    ]

    passed = 0
    failed = 0

    for pattern_id in test_patterns:
        try:
            q = orch.generate_question(
                concept=pattern_id,
                marks=3,
                difficulty=0.5
            )

            assert q.source == "pattern", f"Expected 'pattern', got '{q.source}'"
            assert q.question_text, "Question text is empty"
            assert q.final_answer, "Final answer is empty"
            assert q.solution_steps, "Solution steps are empty"

            print(f"  [PASS] {pattern_id}")
            print(f"         Q: {q.question_text[:60]}...")
            passed += 1

        except Exception as e:
            print(f"  [FAIL] {pattern_id}: {e}")
            failed += 1

    print(f"\n  Results: {passed} passed, {failed} failed out of {len(test_patterns)}")
    return failed == 0


def test_concept_mapping():
    """Test that legacy concept names map to correct patterns"""
    print("\n" + "="*70)
    print("TEST 2: Concept Mapping")
    print("="*70)

    orch = HybridOrchestrator(ai_ratio=0.0)

    legacy_concepts = [
        "trigonometry_heights",
        "quadratic",
        "probability",
        "linear",
        "ap",
        "circle",
    ]

    passed = 0
    failed = 0

    for concept in legacy_concepts:
        try:
            q = orch.generate_question(
                concept=concept,
                marks=2,
                difficulty=0.5
            )

            assert q.source == "pattern"
            # Sanitize Unicode for Windows console
            question_preview = q.question_text[:50].encode('ascii', 'replace').decode('ascii')
            print(f"  [PASS] {concept} -> {question_preview}...")
            passed += 1

        except Exception as e:
            print(f"  [FAIL] {concept}: {e}")
            failed += 1

    print(f"\n  Results: {passed} passed, {failed} failed out of {len(legacy_concepts)}")
    return failed == 0


def test_hybrid_split():
    """Test that 50-50 split works correctly"""
    print("\n" + "="*70)
    print("TEST 3: Hybrid 50-50 Split")
    print("="*70)

    orch = HybridOrchestrator(ai_ratio=0.5)

    # Generate 20 questions
    num_questions = 20
    for i in range(num_questions):
        q = orch.generate_question(
            concept="trigonometry",
            marks=3,
            difficulty=0.6
        )
        # Just generate, don't print

    stats = orch.get_stats()

    pattern_pct = stats['pattern_count'] / stats['total_generated'] * 100
    ai_pct = stats['ai_count'] / stats['total_generated'] * 100

    print(f"  Generated: {stats['total_generated']} questions")
    print(f"  Pattern: {stats['pattern_count']} ({pattern_pct:.0f}%)")
    print(f"  AI: {stats['ai_count']} ({ai_pct:.0f}%)")

    # Allow 30-70% range (random variation expected)
    passed = 30 <= pattern_pct <= 70 and 30 <= ai_pct <= 70

    if passed:
        print(f"\n  [PASS] Split is within acceptable range (30-70%)")
    else:
        print(f"\n  [FAIL] Split outside range: {pattern_pct:.0f}% pattern, {ai_pct:.0f}% AI")

    return passed


def test_pattern_manager_stats():
    """Test that PatternManager stats are accessible"""
    print("\n" + "="*70)
    print("TEST 4: PatternManager Stats")
    print("="*70)

    orch = HybridOrchestrator(ai_ratio=0.5)
    stats = orch.get_stats()

    try:
        pm_stats = stats['pattern_manager_stats']

        assert 'total_patterns' in pm_stats
        assert 'topics' in pm_stats

        print(f"  Total patterns: {pm_stats['total_patterns']}")
        print(f"  Topics covered: {len(pm_stats['topics'])}")

        # Should have 60 patterns
        assert pm_stats['total_patterns'] == 60, f"Expected 60, got {pm_stats['total_patterns']}"

        print(f"\n  [PASS] PatternManager properly integrated")
        return True

    except Exception as e:
        print(f"\n  [FAIL] {e}")
        return False


def run_all_tests():
    """Run all integration tests"""
    print("\n" + "="*80)
    print(" ORACLE INTEGRATION TEST SUITE - PatternManager")
    print("="*80)

    tests = [
        ("Pattern Generation", test_pattern_generation),
        ("Concept Mapping", test_concept_mapping),
        ("Hybrid Split", test_hybrid_split),
        ("PatternManager Stats", test_pattern_manager_stats),
    ]

    results = []

    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"\n[ERROR] {name} crashed: {e}")
            results.append((name, False))

    # Summary
    print("\n" + "="*80)
    print(" TEST SUMMARY")
    print("="*80)

    total_passed = sum(1 for _, passed in results if passed)
    total_tests = len(results)

    for name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"  {status} {name}")

    print(f"\n  Total: {total_passed}/{total_tests} tests passed")

    if total_passed == total_tests:
        print("\n" + "="*80)
        print(" SUCCESS: All tests passed! ✅")
        print(" ORACLE Integration with PatternManager is working perfectly.")
        print("="*80)
    else:
        print("\n" + "="*80)
        print(" FAILED: Some tests did not pass")
        print(" Please review the errors above.")
        print("="*80)

    return total_passed == total_tests


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
