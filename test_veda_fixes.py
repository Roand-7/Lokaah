"""Verify VEDA fixes for greetings, identity, and context memory"""
import requests
import json
import time

API_BASE = "http://localhost:8000"

def test_veda_fixes():
    """Test the specific issues user reported"""
    
    print("🧪 Testing VEDA Fixes\n" + "="*60)
    
    session_id = "test_veda_fix_" + str(int(time.time()))
    
    tests = [
        {
            "name": "Test 1: Initial Hello",
            "message": "hello",
            "expected_behavior": "Should greet warmly, ask what to learn"
        },
        {
            "name": "Test 2: Good Morning (in mid-conversation)",
            "message": "good morning",
            "expected_behavior": "Should respond to greeting, NOT launch into pizza problem"
        },
        {
            "name": "Test 3: Who Are You?",
            "message": "who are you?",
            "expected_behavior": "Should explain VEDA's role, NOT talk about Instagram"
        },
        {
            "name": "Test 4: Explain Pythagoras",
            "message": "explain pythagoras theorem",
            "expected_behavior": "Should teach Pythagoras theorem"
        },
        {
            "name": "Test 5: Follow-up - Show Example",
            "message": "can you show me an example",
            "expected_behavior": "Should give Pythagoras EXAMPLE (remember context!)"
        },
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        print(f"\n{'─'*60}")
        print(f"📤 {test['name']}")
        print(f"   Message: '{test['message']}'")
        print(f"   Expected: {test['expected_behavior']}")
        
        try:
            response = requests.post(
                f"{API_BASE}/api/v1/chat",
                json={
                    "message": test['message'],
                    "session_id": session_id
                },
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                agent = data.get("agent_name", "unknown")
                response_text = data.get("response", "")
                
                print(f"\n✅ Response from: {agent}")
                print(f"   Text (first 200 chars):")
                print(f"   {response_text[:200]}...")
                
                # Validation checks
                issues = []
                
                if test['name'] == "Test 2: Good Morning (in mid-conversation)":
                    if "pizza" in response_text.lower():
                        issues.append("❌ FAIL: Still talking about pizza!")
                    if "instagram" in response_text.lower() or "influencer" in response_text.lower():
                        issues.append("❌ FAIL: Random scenario instead of greeting")
                    if not any(word in response_text.lower() for word in ["hey", "hi", "hello", "morning", "ready"]):
                        issues.append("⚠️  WARNING: Doesn't seem like a greeting response")
                
                if test['name'] == "Test 3: Who Are You?":
                    if "instagram" in response_text.lower() or "influencer" in response_text.lower():
                        issues.append("❌ FAIL: Still talking about Instagram!")
                    if "veda" not in response_text.lower():
                        issues.append("❌ FAIL: Doesn't mention VEDA")
                    if "tutor" not in response_text.lower() and "ai" not in response_text.lower():
                        issues.append("⚠️  WARNING: Doesn't explain what VEDA is")
                
                if test['name'] == "Test 5: Follow-up - Show Example":
                    if "pizza" in response_text.lower() and "pythagoras" not in response_text.lower():
                        issues.append("❌ FAIL: Talking about pizza instead of Pythagoras!")
                    if "pythagoras" in response_text.lower() or "triangle" in response_text.lower() or "hypotenuse" in response_text.lower():
                        issues.append("✅ GOOD: Remembered Pythagoras context")
                
                if issues:
                    print("\n   Validation:")
                    for issue in issues:
                        print(f"   {issue}")
                        if "FAIL" in issue:
                            failed += 1
                        else:
                            passed += 1
                else:
                    print("   ✅ No obvious issues detected")
                    passed += 1
                    
            else:
                print(f"❌ HTTP {response.status_code}: {response.text[:100]}")
                failed += 1
                
        except Exception as e:
            print(f"❌ Error: {str(e)[:100]}")
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"Tests completed: {passed + failed}")
    print(f"✅ Good responses: {passed}")
    print(f"❌ Issues found: {failed}")
    print(f"\n{'='*60}")
    
    if failed == 0:
        print("🎉 All VEDA fixes working correctly!")
    else:
        print("⚠️  Some issues remain - check responses above")

if __name__ == "__main__":
    test_veda_fixes()
