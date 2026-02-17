"""
Production Readiness Test - Final validation before user testing
Tests all critical fixes:
1. VEDA context memory (quadratic example should be about quadratics, not linear)
2. Oracle natural responses (no "Challenge accepted")
3. Greeting handling
4. Identity questions
"""

import requests
import time
import json

BASE_URL = "http://localhost:8000"
CHAT_ENDPOINT = f"{BASE_URL}/api/v1/chat"

def send_message(session_id: str, message: str) -> dict:
    """Send a message and return the response"""
    response = requests.post(
        CHAT_ENDPOINT,
        json={"session_id": session_id, "message": message}
    )
    assert response.status_code == 200, f"Request failed: {response.status_code}"
    return response.json()

def test_veda_context_memory():
    """Test that VEDA remembers context for follow-up questions"""
    print("\n" + "="*60)
    print("TEST 1: VEDA Context Memory (Quadratic → Example)")
    print("="*60)
    
    session_id = f"test_context_{int(time.time())}"
    
    # Step 1: Ask about quadratic equations
    print("\n👤 User: explain quadratic equations")
    result1 = send_message(session_id, "explain quadratic equations")
    response1 = result1["response"]
    print(f"🤖 {result1['agent_label']}: {response1[:200]}...")
    
    # Step 2: Ask for example (should be quadratic, NOT linear!)
    print("\n👤 User: can you show me an example")
    result2 = send_message(session_id, "can you show me an example")
    response2 = result2["response"].lower()
    print(f"🤖 {result2['agent_label']}: {response2[:300]}...")
    
    # Validation
    issues = []
    if "quadratic" not in response2 and "x²" not in response2 and "x^2" not in response2:
        issues.append("⚠️ FAILED: Example is NOT about quadratic equations!")
    
    if "2x + 5" in response2 or "linear" in response2:
        issues.append("❌ CRITICAL: Gave LINEAR equation example instead of QUADRATIC!")
    
    if any(word in response2 for word in ["quadratic", "squared", "x²", "x^2", "parabola"]):
        print("✅ PASSED: Example is about quadratic equations")
    else:
        issues.append("⚠️ WARNING: No quadratic-related terms found")
    
    if issues:
        print("\n".join(issues))
        return False
    return True

def test_oracle_natural_responses():
    """Test that Oracle uses natural language, not templates"""
    print("\n" + "="*60)
    print("TEST 2: Oracle Natural Responses")
    print("="*60)
    
    session_id = f"test_oracle_{int(time.time())}"
    
    print("\n👤 User: /test")
    result = send_message(session_id, "/test")
    response = result["response"]
    print(f"🤖 {result['agent_label']}: {response[:400]}...")
    
    # Validation
    issues = []
    if "Challenge accepted" in response:
        issues.append("❌ FAILED: Still using 'Challenge accepted' template!")
    
    if "High-focus mode ON" in response:
        issues.append("❌ FAILED: Still using 'High-focus mode ON' template!")
    
    if "source: pattern" in response or "source: ai" in response:
        issues.append("❌ FAILED: Exposing source metadata!")
    
    if not issues:
        print("✅ PASSED: Oracle response is natural (no templates)")
        return True
    else:
        print("\n".join(issues))
        return False

def test_greeting_handling():
    """Test that greetings work at any time"""
    print("\n" + "="*60)
    print("TEST 3: Greeting Handling")
    print("="*60)
    
    session_id = f"test_greeting_{int(time.time())}"
    
    # First greeting
    print("\n👤 User: hello")
    result1 = send_message(session_id, "hello")
    print(f"🤖 {result1['agent_label']}: {result1['response'][:150]}...")
    
    # Some conversation
    print("\n👤 User: what topics can you teach?")
    result2 = send_message(session_id, "what topics can you teach?")
    print(f"🤖 {result2['agent_label']}: {result2['response'][:150]}...")
    
    # Greeting again (mid-conversation)
    print("\n👤 User: good evening")
    result3 = send_message(session_id, "good evening")
    response3 = result3["response"].lower()
    print(f"🤖 {result3['agent_label']}: {result3['response'][:150]}...")
    
    # Validation
    if any(greeting in response3 for greeting in ["hey", "hello", "hi", "evening", "kaise"]):
        print("✅ PASSED: Greeting recognized mid-conversation")
        return True
    else:
        print("❌ FAILED: Greeting not recognized (might have started teaching instead)")
        return False

def test_identity_question():
    """Test that 'who are you' gets direct answer"""
    print("\n" + "="*60)
    print("TEST 4: Identity Question")
    print("="*60)
    
    session_id = f"test_identity_{int(time.time())}"
    
    print("\n👤 User: who are you?")
    result = send_message(session_id, "who are you?")
    response = result["response"].lower()
    print(f"🤖 {result['agent_label']}: {result['response'][:300]}...")
    
    # Validation
    if "veda" in response and ("expert digital assistant" in response or "tutor" in response):
        print("✅ PASSED: Identity question answered directly")
        return True
    else:
        print("❌ FAILED: No clear VEDA introduction")
        return False

def main():
    print("\n" + "🧪"*30)
    print("PRODUCTION READINESS TEST")
    print("🧪"*30)
    print("\nWaiting 3 seconds for server to be ready...")
    time.sleep(3)
    
    results = []
    
    try:
        results.append(("VEDA Context Memory", test_veda_context_memory()))
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        results.append(("VEDA Context Memory", False))
    
    try:
        results.append(("Oracle Natural Responses", test_oracle_natural_responses()))
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        results.append(("Oracle Natural Responses", False))
    
    try:
        results.append(("Greeting Handling", test_greeting_handling()))
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        results.append(("Greeting Handling", False))
    
    try:
        results.append(("Identity Question", test_identity_question()))
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        results.append(("Identity Question", False))
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED - Platform is production ready!")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed - needs attention")

if __name__ == "__main__":
    main()
