"""
Quick Test: Verify Hybrid Oracle System
Tests all 4 components independently
"""

import sys
import os

print("=" * 70)
print("HYBRID ORACLE SYSTEM - VERIFICATION TEST")
print("=" * 70)

# Test 1: Check file existence
print("\n[1/4] Checking file structure...")
files_to_check = [
    "app/oracle/true_ai_oracle.py",
    "app/oracle/hybrid_orchestrator.py",
    "app/api/routes.py",
    "app/veda/oracle_integration.py"
]

all_exist = True
for file in files_to_check:
    exists = os.path.exists(file)
    status = "✅" if exists else "❌"
    print(f"   {status} {file}")
    if not exists:
        all_exist = False

if not all_exist:
    print("\n❌ Some files missing. Please create them first.")
    sys.exit(1)

# Test 2: Check dependencies
print("\n[2/4] Checking dependencies...")
dependencies = {
    "anthropic": "Anthropic Claude SDK",
    "google.genai": "Google Gemini SDK",
    "fastapi": "FastAPI Framework",
    "pydantic": "Data validation"
}

missing_deps = []
for module, desc in dependencies.items():
    try:
        __import__(module)
        print(f"   ✅ {module} - {desc}")
    except ImportError:
        print(f"   ❌ {module} - {desc} (MISSING)")
        missing_deps.append(module)

if missing_deps:
    print(f"\n⚠️  Missing dependencies: {', '.join(missing_deps)}")
    print("   Install with: pip install anthropic google-genai fastapi pydantic")
    print("   Continuing with reduced functionality...")

# Test 3: Check imports
print("\n[3/4] Testing imports...")
try:
    from app.oracle.true_ai_oracle import TrueAIOracle, AIQuestionResult
    print("   ✅ TrueAIOracle imported")
except Exception as e:
    print(f"   ❌ TrueAIOracle import failed: {e}")

try:
    from app.oracle.hybrid_orchestrator import HybridOrchestrator, HybridQuestion
    print("   ✅ HybridOrchestrator imported")
except Exception as e:
    print(f"   ❌ HybridOrchestrator import failed: {e}")

try:
    from app.api.routes import router
    print("   ✅ API routes imported")
except Exception as e:
    print(f"   ❌ API routes import failed: {e}")

try:
    from app.veda.oracle_integration import VedaOracleBridge, LokaahLearningSession
    print("   ✅ VEDA integration imported")
except Exception as e:
    print(f"   ❌ VEDA integration import failed: {e}")

# Test 4: Check environment
print("\n[4/4] Checking environment variables...")
env_vars = {
    "ANTHROPIC_API_KEY": "Claude API Key",
    "GEMINI_API_KEY": "Gemini API Key",
    "SUPABASE_URL": "Supabase Database URL",
    "SUPABASE_KEY": "Supabase API Key"
}

for var, desc in env_vars.items():
    value = os.getenv(var)
    if value:
        masked = value[:8] + "..." if len(value) > 8 else "***"
        print(f"   ✅ {var} - {desc} ({masked})")
    else:
        print(f"   ⚠️  {var} - {desc} (NOT SET)")

# Summary
print("\n" + "=" * 70)
print("VERIFICATION COMPLETE")
print("=" * 70)

print("\n📊 Summary:")
print(f"   Files: {'✅ All present' if all_exist else '❌ Some missing'}")
print(f"   Dependencies: {'✅ All installed' if not missing_deps else f'⚠️  {len(missing_deps)} missing'}")
print(f"   Environment: {'✅ Configured' if os.getenv('ANTHROPIC_API_KEY') or os.getenv('GEMINI_API_KEY') else '⚠️  API keys needed'}")

print("\n🚀 Next Steps:")
if missing_deps:
    print("   1. Install dependencies: pip install anthropic google-genai")
if not (os.getenv('ANTHROPIC_API_KEY') or os.getenv('GEMINI_API_KEY')):
    print("   2. Add API keys to .env file")
print("   3. Run standalone tests:")
print("      python -m app.oracle.true_ai_oracle")
print("      python -m app.oracle.hybrid_orchestrator")
print("   4. Start FastAPI server: uvicorn app.main:app --reload")

print("\n📚 Documentation: HYBRID_ORACLE_SETUP.md")
print("=" * 70)
