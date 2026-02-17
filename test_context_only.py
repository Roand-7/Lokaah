"""Quick test for context memory only"""
import requests
import time

BASE_URL = "http://localhost:8000"
CHAT_ENDPOINT = f"{BASE_URL}/api/v1/chat"

session_id = f"debug_context_{int(time.time())}"

print("\n1. First message: explain quadratic equations")
response1 = requests.post(CHAT_ENDPOINT, json={"session_id": session_id, "message": "explain quadratic equations"})
print(f"Response 1: {response1.json()['response'][:200]}...")

print("\n2. Second message: can you show me an example")
response2 = requests.post(CHAT_ENDPOINT, json={"session_id": session_id, "message": "can you show me an example"})
result = response2.json()
print(f"Response 2: {result['response'][:400]}...")

if "quadratic" in result['response'].lower() or "x²" in result['response'] or "x^2" in result['response']:
    print("\n✅ SUCCESS: Got quadratic example!")
else:
    print("\n❌ FAIL: Did NOT get quadratic example!")
