"""
Quick Test: Generate a question with JSXGraph visual
Run this after setting GEMINI_API_KEY or ANTHROPIC_API_KEY
"""

import os
import sys
from pathlib import Path

# Load .env file
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / '.env'
    load_dotenv(env_path)
    print(f"🔐 Loaded .env from: {env_path}")
except ImportError:
    print("⚠️  python-dotenv not installed, using system environment variables")

# Add app to path
sys.path.insert(0, os.path.dirname(__file__))

def main():
    print("🧪 Testing JSXGraph Visual Generation")
    print("=" * 60)
    
    # Check API keys
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")
    
    if not (anthropic_key or gemini_key):
        print("❌ ERROR: No API keys found!")
        print("\nPlease set either:")
        print("  ANTHROPIC_API_KEY=your-key")
        print("  GEMINI_API_KEY=your-key")
        print("\nSee QUICK_START_JSXGRAPH.md for instructions")
        return 1
    
    print(f"✅ API Key found: {'Anthropic' if anthropic_key else 'Gemini'}")
    
    # Import and test
    try:
        from app.oracle.true_ai_oracle import TrueAIOracle
        
        print("\n🔄 Initializing AI Oracle...")
        oracle = TrueAIOracle()
        
        print("🎲 Generating trigonometry question with visual...")
        print("   (This may take 2-5 seconds)\n")
        
        result = oracle.generate_question(
            concept="trigonometry_heights",
            marks=3,
            difficulty=0.6
        )
        
        print("=" * 60)
        print("✅ QUESTION GENERATED SUCCESSFULLY!")
        print("=" * 60)
        
        print(f"\n📝 QUESTION TEXT:")
        print(f"   {result.question_text}\n")
        
        print(f"💡 FINAL ANSWER:")
        print(f"   {result.final_answer}\n")
        
        print(f"🔢 VARIABLES USED:")
        for key, value in (result.variables or {}).items():
            print(f"   {key}: {value}")
        
        print(f"\n📊 SOLUTION STEPS:")
        for i, step in enumerate(result.solution_steps, 1):
            print(f"   {i}. {step}")
        
        if result.jsxgraph_code:
            print(f"\n✅ JSXGRAPH CODE GENERATED:")
            print(f"   Length: {len(result.jsxgraph_code)} characters")
            print(f"   Preview (first 300 chars):")
            print("   " + "-" * 57)
            preview = result.jsxgraph_code[:300].replace('\n', '\n   ')
            print(f"   {preview}")
            print("   " + "-" * 57)
            print(f"   ... (+{len(result.jsxgraph_code) - 300} more chars)")
            
            # Save to file for testing
            output_file = "test_jsxgraph_output.js"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(result.jsxgraph_code)
            print(f"\n   💾 Full code saved to: {output_file}")
            
            # Validate JSXGraph code
            print(f"\n   🔍 Code Validation:")
            checks = {
                "Has board.create": "board.create" in result.jsxgraph_code,
                "Has point": "point" in result.jsxgraph_code.lower(),
                "Has visual element": any(x in result.jsxgraph_code.lower() for x in ["line", "polygon", "circle", "segment"]),
                "Has labels": "text" in result.jsxgraph_code.lower() or "name:" in result.jsxgraph_code.lower(),
            }
            for check, passed in checks.items():
                print(f"      {'✅' if passed else '❌'} {check}")
        else:
            print(f"\n⚠️  NO JSXGRAPH CODE:")
            print(f"   This concept might not require a visual")
            print(f"   Try: trigonometry_heights, coordinate_geometry_distance")
        
        print("\n" + "=" * 60)
        print("🎉 TEST COMPLETE!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Review the question quality")
        print("2. Copy jsx code to Flutter JSXGraphViewer widget")
        print("3. Test in your Flutter app")
        print("4. Run full verification: python verify_jsxgraph_integration.py")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
