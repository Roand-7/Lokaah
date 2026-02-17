"""
Quick test to examine a generated question in detail
"""
import os
import sys
import json

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from cbse.class10_engine import CBSEClass10Engine

def inspect_question():
    print("=" * 80)
    print("DETAILED QUESTION INSPECTION")
    print("=" * 80)
    
    engine = CBSEClass10Engine()
    
    # Generate a question
    question = engine.generate_question(
        chapter_number=6,
        topic="Pythagoras theorem",
        marks=2
    )
    
    # Pretty print the entire question structure
    print("\n📋 Complete Question Structure:")
    print(json.dumps(question, indent=2, default=str))
    
    print("\n" + "=" * 80)
    print("✅ Inspection complete - verifying robustness:")
    print("=" * 80)
    
    # Robustness checks
    checks = {
        "Has question_id": "question_id" in question,
        "Has question_text": "question_text" in question,
        "Has solution_steps": "solution_steps" in question and len(question["solution_steps"]) > 0,
        "Has final_answer": "final_answer" in question,
        "Has socratic_hints": "socratic_hints" in question,
        "Has CBSE format": "cbse_format" in question,
        "Has chapter info": "chapter" in question,
        "Has generation method": "generation_method" in question,
        "Marks correctly set": question.get("marks") == 2,
        "Has visual placeholder": "visual" in question if question.get("chapter") in [6,7,8,10,11,12,13] else True,
        "Solution has multiple steps": len(question.get("solution_steps", [])) >= 3,
        "Has proper question ID format": question.get("question_id", "").startswith("CBSE10_"),
    }
    
    for check, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"   {status} {check}")
    
    all_passed = all(checks.values())
    
    print("\n" + "=" * 80)
    if all_passed:
        print("🎉 ALL ROBUSTNESS CHECKS PASSED!")
        print("The CBSE Class 10 Engine is production-ready for existing patterns.")
    else:
        print("⚠️ Some checks failed - review needed")
    print("=" * 80)

if __name__ == "__main__":
    inspect_question()
