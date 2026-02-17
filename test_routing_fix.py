"""Test script to verify routing fixes for casual messages"""
import sys
from app.graph.nodes.supervisor import SupervisorNode

def test_routing():
    """Test that casual messages don't trigger FINISH"""
    supervisor = SupervisorNode()
    
    test_cases = [
        # (message, expected_agent, should_not_be)
        ("thank you", "veda", "FINISH"),
        ("thanks", "veda", "FINISH"),
        ("hello", "veda", "FINISH"),
        ("hi", "veda", "FINISH"),
        ("hey", "veda", "FINISH"),
        ("good morning", "veda", "FINISH"),
        ("namaste", "veda", "FINISH"),
        ("kaise ho", "veda", "FINISH"),
        ("who are you", "veda", "FINISH"),
        ("what can you do", "veda", "FINISH"),
        # These should trigger FINISH
        ("goodbye", "FINISH", "veda"),
        ("that's all", "FINISH", "veda"),
        ("/bye", "FINISH", "veda"),
        ("bye", "FINISH", "veda"),
    ]
    
    print("🧪 Testing Routing Fixes\n" + "="*50)
    passed = 0
    failed = 0
    
    for message, expected, should_not_be in test_cases:
        state = {
            "messages": [{"role": "user", "content": message}],
            "session_id": "test_123"
        }
        
        result = supervisor.route(state)
        agent = result.get("next_agent", "unknown")
        reason = result.get("metadata", {}).get("route_reason", "")
        confidence = result.get("metadata", {}).get("route_confidence", 0)
        
        if agent == expected and agent != should_not_be:
            print(f"✅ PASS: '{message}'")
            print(f"   → {agent} (confidence: {confidence:.2f})")
            print(f"   → Reason: {reason}\n")
            passed += 1
        else:
            print(f"❌ FAIL: '{message}'")
            print(f"   → Expected: {expected}, Got: {agent}")
            print(f"   → Reason: {reason}\n")
            failed += 1
    
    print("="*50)
    print(f"Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("\n🎉 All tests passed! Routing is fixed.")
        return 0
    else:
        print(f"\n⚠️ {failed} test(s) failed. Please review.")
        return 1

if __name__ == "__main__":
    sys.exit(test_routing())
