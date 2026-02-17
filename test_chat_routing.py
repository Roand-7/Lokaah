# Test script to verify the routing fix in actual chat API
import requests
import json

API_BASE = "http://localhost:8000"

def test_chat_routing():
    """Test that casual messages work correctly in chat API"""
    
    test_messages = [
        "hello",
        "thank you",
        "thanks",
        "good morning",
        "namaste",
        "who are you",
        "bye"  # This should end session
    ]
    
    print("🧪 Testing Chat API Routing\n" + "="*60)
    
    session_id = "test_routing_123"
    
    for message in test_messages:
        print(f"\n📤 Sending: '{message}'")
        
        try:
            response = requests.post(
                f"{API_BASE}/api/v1/chat",
                json={
                    "message": message,
                    "session_id": session_id
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                agent = data.get("agent_name", "unknown")
                response_text = data.get("response", "")[:100]  # First 100 chars
                
                print(f"✅ {response.status_code} | Agent: {agent}")
                print(f"   Response: {response_text}...")
                
                # Verify routing
                if message in ["thank you", "thanks", "hello", "good morning", "namaste", "who are you"]:
                    if agent != "veda":
                        print(f"   ⚠️ WARNING: Expected VEDA, got {agent}")
                elif message == "bye":
                    if agent != "veda":  # finish_node now returns veda
                        print(f"   ⚠️ WARNING: Expected VEDA (finish), got {agent}")
            else:
                print(f"❌ {response.status_code} | Error: {response.text[:100]}")
                
        except Exception as e:
            print(f"❌ Error: {str(e)[:100]}")
    
    print("\n" + "="*60)
    print("✅ Test complete! Check if all messages routed correctly.")

if __name__ == "__main__":
    test_chat_routing()
