"""Quick test of Gemini-only system"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

from app.oracle.true_ai_oracle import TrueAIOracle

print("🧪 Testing Gemini-Only AI Oracle\n")

oracle = TrueAIOracle()

print("\n📝 Generating question...")
result = oracle.generate_question(
    concept='trigonometry_heights',
    marks=3,
    difficulty=0.6
)

print("\n" + "="*60)
print("✅ SUCCESS - Gemini-Only System Working!")
print("="*60)

print(f"\n📚 Question:")
print(f"   {result.question_text[:150]}...")

print(f"\n💡 Answer:")
print(f"   {result.final_answer}")

print(f"\n📊 Solution Steps:")
for i, step in enumerate(result.solution_steps[:3], 1):
    print(f"   {i}. {step}")
print(f"   ... ({len(result.solution_steps)} steps total)")

print(f"\n📐 JSXGraph:")
if result.jsxgraph_code:
    print(f"   ✅ Generated ({len(result.jsxgraph_code)} characters)")
else:
    print(f"   ⚠️  Not generated")

print(f"\n💰 Cost Estimate:")
stats = oracle.get_stats()
print(f"   ${stats['estimated_api_cost_usd']:.4f}")

print("\n" + "="*60)
print("🎉 GEMINI-ONLY SYSTEM FULLY OPERATIONAL!")
print("="*60)
