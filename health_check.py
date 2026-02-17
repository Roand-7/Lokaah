"""
LOKAAH Health Check Script
Tests all critical API endpoints and system components
"""

import requests
import sys
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def test_endpoint(name, method, endpoint, data=None, expected_status=200):
    """Test a single endpoint"""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        
        status_ok = response.status_code == expected_status
        status_icon = "✅" if status_ok else "❌"
        
        print(f"{status_icon} {method} {endpoint}")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                resp_json = response.json()
                print(f"   Response: {json.dumps(resp_json, indent=2)[:200]}...")
            except:
                print(f"   Response: {response.text[:100]}...")
        else:
            print(f"   Error: {response.text[:200]}")
        
        return status_ok
    except requests.exceptions.ConnectionError:
        print(f"❌ {method} {endpoint}")
        print(f"   Error: Cannot connect to server at {BASE_URL}")
        print(f"   Make sure the server is running!")
        return False
    except Exception as e:
        print(f"❌ {method} {endpoint}")
        print(f"   Error: {str(e)}")
        return False

def main():
    print_section(f"LOKAAH Health Check - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    # Test 1: Root endpoint (retry a few times to handle server startup)
    print_section("1. Basic Connectivity")
    for attempt in range(3):
        result = test_endpoint("Root", "GET", "/")
        if result:
            break
        if attempt < 2:
            print("   Retrying in 2 seconds...")
            time.sleep(2)
    results.append(result)
    
    # Test 2: Health check
    print_section("2. Health Check")
    results.append(test_endpoint("Health", "GET", "/api/v1/health"))
    
    # Test 3: Stats
    print_section("3. Oracle Stats")
    results.append(test_endpoint("Stats", "GET", "/api/v1/stats"))
    
    # Test 4: Question Generation
    print_section("4. Question Generation")
    question_data = {
        "chapter": "trigonometry",
        "concept": "basic_ratios",
        "difficulty": 0.5
    }
    results.append(test_endpoint("Question Gen", "POST", "/api/v1/question/generate", question_data))
    
    # Test 5: VEDA Chat
    print_section("5. VEDA Chat Interface")
    chat_data = {
        "message": "Hello, can you help me with trigonometry?",
        "session_id": "test_session_123"
    }
    results.append(test_endpoint("VEDA Chat", "POST", "/api/v1/veda/chat", chat_data))
    
    # Summary
    print_section("Test Summary")
    total_tests = len(results)
    passed_tests = sum(results)
    failed_tests = total_tests - passed_tests
    
    print(f"Total Tests: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {failed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
    
    if failed_tests == 0:
        print("\n🎉 All tests passed! System is ready for production.")
        return 0
    else:
        print(f"\n⚠️  {failed_tests} test(s) failed. Please fix before deploying.")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Health check interrupted by user")
        sys.exit(1)
