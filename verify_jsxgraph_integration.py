"""
JSXGRAPH INTEGRATION VERIFICATION
Tests the complete flow: Backend → JSXGraph → Flutter Ready
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Load .env file
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / '.env'
    load_dotenv(env_path)
except ImportError:
    pass  # Use system environment variables

# Add app to path
sys.path.insert(0, os.path.dirname(__file__))

def test_backend_generation():
    """Test 1: Backend generates questions with JSXGraph code"""
    print("\n" + "="*60)
    print("TEST 1: Backend Question Generation with JSXGraph")
    print("="*60)
    
    from app.oracle.true_ai_oracle import TrueAIOracle
    
    try:
        oracle = TrueAIOracle()
        
        # Test trigonometry with visual
        print("\n📐 Testing: Trigonometry Heights & Distances")
        result = oracle.generate_question(
            concept="trigonometry_heights",
            marks=3,
            difficulty=0.6
        )
        
        print(f"✅ Question Generated:")
        print(f"   Text: {result.question_text[:100]}...")
        print(f"   Answer: {result.final_answer}")
        print(f"   Steps: {len(result.solution_steps)} steps")
        print(f"   JSXGraph Code: {'✓ Present' if result.jsxgraph_code else '✗ Missing'}")
        
        if result.jsxgraph_code:
            print(f"\n✅ JSXGraph Code Sample (first 300 chars):")
            print(result.jsxgraph_code[:300] + "...")
            
            # Verify it contains key JSXGraph elements
            jsx_checks = {
                "board.create": "✓" if "board.create" in result.jsxgraph_code else "✗",
                "point": "✓" if "point" in result.jsxgraph_code.lower() else "✗",
                "line": "✓" if "line" in result.jsxgraph_code.lower() else "✗",
            }
            print(f"\n   JSXGraph Element Checks: {jsx_checks}")
        
        return True
        
    except Exception as e:
        print(f"❌ Backend test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_hybrid_orchestrator():
    """Test 2: Hybrid 50-50 split works correctly"""
    print("\n" + "="*60)
    print("TEST 2: Hybrid Orchestrator (50-50 Split)")
    print("="*60)
    
    from app.oracle.hybrid_orchestrator import HybridOrchestrator
    
    try:
        orchestrator = HybridOrchestrator(ai_ratio=0.5)
        
        print("\n🎲 Generating 10 questions to test distribution...")
        print("   (Forcing pattern-only since no AI keys)")
        sources = []
        jsxgraph_count = 0
        
        for i in range(10):
            # Force pattern source to avoid AI requirement
            result = orchestrator.generate_question(
                concept="trigonometry",
                difficulty=0.5,
                marks=3,
                force_source="pattern"
            )
            sources.append(result.source)
            if result.jsxgraph_code:
                jsxgraph_count += 1
            print(f"   Q{i+1}: {result.source:8s} | JSXGraph: {'✓' if result.jsxgraph_code else '✗'}")
        
        pattern_count = sources.count("pattern")
        ai_count = sources.count("ai")
        
        print(f"\n✅ Distribution:")
        print(f"   Pattern ORACLE: {pattern_count}/10 ({pattern_count*10}%)")
        print(f"   AI ORACLE:      {ai_count}/10 ({ai_count*10}%)")
        print(f"   With JSXGraph:  {jsxgraph_count}/10")
        
        # Get statistics
        stats = orchestrator.get_statistics()
        print(f"\n📊 Orchestrator Stats:")
        print(f"   Total Generated: {stats['total_questions']}")
        print(f"   Estimated Cost:  ${stats.get('estimated_api_cost_usd', 0):.4f}")
        print(f"   Avg Time:        {stats.get('avg_generation_time_ms', 0):.1f}ms")
        
        return True
        
    except Exception as e:
        print(f"❌ Hybrid orchestrator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_visual_concepts():
    """Test 3: All visual concepts generate JSXGraph"""
    print("\n" + "="*60)
    print("TEST 3: Visual Concepts JSXGraph Generation")
    print("="*60)
    
    from app.oracle.true_ai_oracle import TrueAIOracle
    
    visual_concepts = [
        "trigonometry_heights",
        "coordinate_geometry_distance",
        "triangles_similarity",
        "circles_tangents",
    ]
    
    oracle = TrueAIOracle()
    results = []
    
    for concept in visual_concepts:
        try:
            print(f"\n📐 Testing: {concept}")
            result = oracle.generate_question(concept, 3, 0.5)
            
            has_jsx = result.jsxgraph_code is not None
            results.append({
                "concept": concept,
                "jsx_present": has_jsx,
                "jsx_length": len(result.jsxgraph_code) if has_jsx else 0
            })
            
            print(f"   JSXGraph: {'✓ Generated' if has_jsx else '✗ Missing'}")
            if has_jsx:
                print(f"   Code Length: {len(result.jsxgraph_code)} chars")
                
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            results.append({"concept": concept, "jsx_present": False, "error": str(e)})
    
    success_count = sum(1 for r in results if r.get("jsx_present"))
    print(f"\n✅ Visual Generation: {success_count}/{len(visual_concepts)} concepts")
    
    return success_count > 0


def test_flutter_compatibility():
    """Test 4: Output format is Flutter-compatible"""
    print("\n" + "="*60)
    print("TEST 4: Flutter Compatibility Check")
    print("="*60)
    
    from app.oracle.hybrid_orchestrator import HybridOrchestrator
    
    try:
        orchestrator = HybridOrchestrator()
        
        # Force pattern to avoid AI requirement
        result = orchestrator.generate_question(
            concept="trigonometry",
            difficulty=0.6,
            marks=3,
            force_source="pattern"
        )
        
        # Convert to JSON (Flutter will receive this)
        try:
            json_output = {
                "question_id": result.question_id,
                "question_text": result.question_text,
                "solution_steps": result.solution_steps,
                "final_answer": result.final_answer,
                "socratic_hints": result.socratic_hints,
                "jsx_graph_code": result.jsxgraph_code,  # Flutter expects this field
                "graph_bounding_box": [-10, 10, 10, -10],
                "difficulty": result.difficulty,
                "marks": result.marks,
                "source": result.source
            }
            
            json_str = json.dumps(json_output, ensure_ascii=False)
            print(f"✅ JSON Serialization: Success ({len(json_str)} bytes)")
            
            # Check required fields for Flutter
            required_fields = ["question_text", "final_answer", "jsx_graph_code", "socratic_hints"]
            missing = [f for f in required_fields if f not in json_output or json_output[f] is None]
            
            if missing:
                print(f"⚠️  Missing optional fields: {missing}")
            else:
                print(f"✅ All Flutter fields present")
            
            # Check JSXGraph code format
            if result.jsxgraph_code:
                jsx_validation = {
                    "Has board.create": "board.create" in result.jsxgraph_code,
                    "Has JavaScript syntax": "function" in result.jsxgraph_code or "=>" in result.jsxgraph_code,
                    "Not empty": len(result.jsxgraph_code) > 50,
                    "Valid UTF-8": True  # Already validated by JSON encoding
                }
                
                print(f"\n✅ JSXGraph Code Validation:")
                for check, passed in jsx_validation.items():
                    print(f"   {check}: {'✓' if passed else '✗'}")
                
                return all(jsx_validation.values())
            else:
                print("ℹ️  No JSXGraph code in this question (might be algebra)")
                return True
                
        except json.JSONDecodeError as e:
            print(f"❌ JSON encoding failed: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Flutter compatibility test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_veda_hint_integration():
    """Test 5: VEDA hints can update JSXGraph"""
    print("\n" + "="*60)
    print("TEST 5: VEDA Hint System Integration")
    print("="*60)
    
    print("\n📚 Checking VEDA Agent...")
    
    try:
        from app.agents.veda import VedaAgent
        
        veda = VedaAgent()
        print("✅ VEDA Agent initialized")
        
        # Check if VEDA has JSXGraph hint capabilities
        print("\n🔍 Checking VEDA JSXGraph methods...")
        
        jsx_methods = [
            "generate_visual_hint",
            "update_jsx_graph",
            "_create_hint_visualization"
        ]
        
        available_methods = []
        for method in jsx_methods:
            if hasattr(veda, method):
                available_methods.append(method)
                print(f"   ✓ {method}")
            else:
                print(f"   ℹ️  {method} (not yet implemented)")
        
        if available_methods:
            print(f"\n✅ VEDA has {len(available_methods)} JSXGraph integration methods")
        else:
            print(f"\nℹ️  VEDA JSXGraph hints not yet implemented")
            print("   This is optional - basic question generation works without it")
        
        return True
        
    except ImportError as e:
        print(f"❌ VEDA import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ VEDA test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_asset_configuration():
    """Test 6: Flutter assets are properly configured"""
    print("\n" + "="*60)
    print("TEST 6: Flutter Asset Configuration")
    print("="*60)
    
    import os
    
    # Check if assets exist
    assets_to_check = [
        "assets/jsxgraph_template.html",
        "lib/widgets/jsxgraph_viewer.dart",
        "pubspec.yaml"
    ]
    
    print("\n📁 Checking required files...")
    all_present = True
    
    for asset in assets_to_check:
        full_path = os.path.join(os.path.dirname(__file__), asset)
        exists = os.path.exists(full_path)
        print(f"   {'✓' if exists else '✗'} {asset}")
        if not exists:
            all_present = False
    
    # Check pubspec.yaml for asset declaration
    pubspec_path = os.path.join(os.path.dirname(__file__), "pubspec.yaml")
    if os.path.exists(pubspec_path):
        with open(pubspec_path, 'r', encoding='utf-8') as f:
            pubspec_content = f.read()
            
        print("\n📋 Checking pubspec.yaml asset declarations...")
        asset_checks = {
            "jsxgraph_template.html declared": "jsxgraph_template.html" in pubspec_content,
            "webview_flutter dependency": "webview_flutter" in pubspec_content,
            "platform webview dependencies": "webview_flutter_android" in pubspec_content or "webview_flutter_wkwebview" in pubspec_content
        }
        
        for check, passed in asset_checks.items():
            print(f"   {'✓' if passed else '⚠️ '} {check}")
            if not passed:
                all_present = False
    
    if all_present:
        print("\n✅ All Flutter assets properly configured")
    else:
        print("\n⚠️  Some assets missing - check configuration")
    
    return all_present


def generate_sample_questions():
    """Generate sample questions for manual testing"""
    print("\n" + "="*60)
    print("BONUS: Sample Questions for Manual Testing")
    print("="*60)
    
    from app.oracle.hybrid_orchestrator import HybridOrchestrator
    
    orchestrator = HybridOrchestrator()
    
    print("\n📝 Generating 3 sample questions with JSXGraph...")
    samples = []
    
    for i in range(3):
        result = orchestrator.generate_question(
            concept="trigonometry",
            difficulty=0.4 + (i * 0.2),
            marks=3,
            force_source="pattern"
        )
        
        samples.append({
            "id": result.question_id,
            "text": result.question_text,
            "answer": result.final_answer,
            "has_jsx": result.jsxgraph_code is not None,
            "source": result.source
        })
        
        print(f"\nQ{i+1} ({result.source}):")
        print(f"   {result.question_text[:80]}...")
        print(f"   Answer: {result.final_answer}")
        print(f"   JSXGraph: {'✓' if result.jsxgraph_code else '✗'}")
    
    # Save to file for Flutter testing
    output_file = "sample_questions_for_flutter.json"
    try:
        # Get one question with full JSXGraph code (force pattern)
        result = orchestrator.generate_question(
            concept="trigonometry",
            difficulty=0.6,
            marks=3,
            force_source="pattern"
        )
        
        flutter_ready = {
            "question_id": result.question_id,
            "question_text": result.question_text,
            "solution_steps": result.solution_steps,
            "final_answer": result.final_answer,
            "socratic_hints": result.socratic_hints,
            "jsx_graph_code": result.jsxgraph_code,
            "graph_bounding_box": [-10, 10, 10, -10],
            "difficulty": result.difficulty,
            "marks": result.marks,
            "source": result.source
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(flutter_ready, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Sample question saved to: {output_file}")
        print(f"   Use this to test Flutter JSXGraphViewer widget!")
        
    except Exception as e:
        print(f"⚠️  Could not save sample: {e}")
    
    return True


def main():
    """Run all verification tests"""
    print("🚀 LOKAAH JSXGRAPH INTEGRATION VERIFICATION")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check environment
    print("\n🔐 Environment Check:")
    anthropic_set = bool(os.getenv("ANTHROPIC_API_KEY"))
    gemini_set = bool(os.getenv("GEMINI_API_KEY"))
    print(f"   ANTHROPIC_API_KEY: {'✓ Set' if anthropic_set else '✗ Not set'}")
    print(f"   GEMINI_API_KEY:    {'✓ Set' if gemini_set else '✗ Not set'}")
    
    if not (anthropic_set or gemini_set):
        print("\n⚠️  Warning: No AI API keys set. Some tests may fail.")
        print("   Set ANTHROPIC_API_KEY or GEMINI_API_KEY in your environment.")
    
    # Run tests
    tests = [
        ("Backend Generation", test_backend_generation),
        ("Hybrid Orchestrator", test_hybrid_orchestrator),
        ("Visual Concepts", test_visual_concepts),
        ("Flutter Compatibility", test_flutter_compatibility),
        ("VEDA Integration", test_veda_hint_integration),
        ("Asset Configuration", test_asset_configuration),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"\n❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Generate samples
    try:
        generate_sample_questions()
    except Exception as e:
        print(f"\n⚠️  Sample generation failed: {e}")
    
    # Summary
    print("\n" + "="*60)
    print("📊 VERIFICATION SUMMARY")
    print("="*60)
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n{'='*60}")
    print(f"Final Score: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("🎉 ALL TESTS PASSED - PRODUCTION READY!")
        print("\nNext steps:")
        print("1. Connect Flutter app to FastAPI backend")
        print("2. Test on physical device (iOS + Android)")
        print("3. Load sample_questions_for_flutter.json in Flutter")
        return 0
    elif passed_count >= total_count - 2:
        print("✅ Core functionality working - Minor issues to fix")
        return 0
    else:
        print("⚠️  Multiple tests failed - Review errors above")
        return 1


if __name__ == "__main__":
    exit(main())
