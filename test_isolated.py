"""Test JUST the quadratic example to isolate the issue"""
import requests
import time

BASE_URL = "http://localhost:8000"
CHAT_ENDPOINT = f"{BASE_URL}/api/v1/chat"

def send_message(session_id: str, message: str) -> dict:
    response = requests.post(CHAT_ENDPOINT, json={"session_id": session_id, "message": message})
    return response.json()

# Use EXACT same session ID format as production test
session_id = f"test_context_{int(time.time())}"

print("="*60)
print("TEST 1: VEDA Context Memory (Quadratic → Example)")
print("="*60)

# Step 1
print("\n👤 User: explain quadratic equations")
result1 = send_message(session_id, "explain quadratic equations")
response1 = result1["response"]
print(f"🤖 {result1['agent_label']}: {response1[:200]}...")

# Step 2
print("\n👤 User: can you show me an example")
result2 = send_message(session_id, "can you show me an example")
response2 = result2["response"].lower()
print(f"🤖 {result2['agent_label']}: {result2['response'][:400]}...")

# Validation
print("\n" + "="*60)
print("VALIDATION:")
print("="*60)
if "quadratic" in response2 or "x²" in response2 or "x^2" in response2:
    print("✅ PASS: Got quadratic example!")
else:
    print("❌ FAIL: Did NOT get quadratic example!")

if "pizza" in response2:
    print("❌ ERROR: Got pizza example instead!")
