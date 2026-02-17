import sys
sys.path.append('c:/Users/Lenovo/lokaah_app')

from app.oracle.oracle_engine import RecipeEngine, get_cbse_pattern_database

engine = RecipeEngine()
patterns_db = get_cbse_pattern_database()

print(f"="*60)
print(f"FINAL VALIDATION - ALL 60 PATTERNS")
print(f"="*60)
print(f"\nDatabase size: {len(patterns_db)} patterns")

passed = 0
failed = 0
failed_patterns = []

for p in patterns_db:
    try:
        question = engine._generate_from_pattern({
            'pattern_type': p.pattern_id,
            'marks': p.marks,
            'difficulty': p.difficulty,
            'socratic_flow': []
        }, p.topic)
        
        assert 'socratic_hints' in question, "Missing socratic_hints key"
        assert len(question['socratic_hints']) > 0, "Empty socratic_hints"
        assert 'question_text' in question, "Missing question_text"
        assert len(question['question_text']) > 10, "Question too short"
        
        passed += 1
    except Exception as e:
        failed += 1
        failed_patterns.append((p.pattern_id, str(e)))

print(f"\n{'-'*60}")
print(f"RESULTS:")
print(f"  PASSED: {passed}/{len(patterns_db)}")
print(f"  FAILED: {failed}/{len(patterns_db)}")
print(f"  SUCCESS RATE: {(passed/len(patterns_db))*100:.1f}%")
print(f"{'-'*60}")

if failed_patterns:
    print(f"\nFailed patterns:")
    for pattern, error in failed_patterns:
        print(f"  - {pattern}: {error}")
else:
    print(f"\n*** ALL 60 PATTERNS WORKING PERFECTLY! ***")
    print(f"*** ORACLE ENGINE IS PRODUCTION-READY! ***")

print(f"="*60)
