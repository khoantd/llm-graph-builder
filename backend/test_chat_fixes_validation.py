#!/usr/bin/env python3
"""
Test script to validate the fixes for chat history issues:
1. 'Neo4jChatMessageHistory' object has no attribute 'session_id'
2. TypeError: the JSON object must be str, bytes or bytearray, not NoneType
"""

import requests
import json
import sys
import time

# Configuration
BASE_URL = "http://localhost:8000"

# Test credentials (update these with your actual values)
TEST_CREDENTIALS = {
    "uri": "neo4j://localhost:7687",
    "userName": "neo4j",
    "password": "password",
    "database": "neo4j",
    "email": "test@example.com"
}

def test_chat_with_none_document_names():
    """Test chat with None document_names to validate JSON parsing fix"""
    print(f"\n🧪 Testing: Chat with None document_names")
    
    test_session_id = f"test_none_docnames_{int(time.time())}"
    
    # Test with None document_names
    data = {
        **TEST_CREDENTIALS,
        "question": "Hello, this is a test with None document_names",
        "document_names": None,  # This should trigger the fix
        "mode": "vector",
        "session_id": test_session_id
    }
    
    try:
        response = requests.post(f"{BASE_URL}/chat_bot", data=data, timeout=60)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Success: {result.get('message', 'No message')[:50]}...")
            if 'info' in result:
                info = result['info']
                print(f"   📊 Mode: {info.get('mode', 'N/A')}")
                print(f"   📊 Response Time: {info.get('response_time', 'N/A')}")
            return True
        else:
            print(f"   ❌ Error: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Request failed: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False

def test_chat_with_empty_document_names():
    """Test chat with empty document_names to validate JSON parsing fix"""
    print(f"\n🧪 Testing: Chat with empty document_names")
    
    test_session_id = f"test_empty_docnames_{int(time.time())}"
    
    # Test with empty string document_names
    data = {
        **TEST_CREDENTIALS,
        "question": "Hello, this is a test with empty document_names",
        "document_names": "",  # This should trigger the fix
        "mode": "vector",
        "session_id": test_session_id
    }
    
    try:
        response = requests.post(f"{BASE_URL}/chat_bot", data=data, timeout=60)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Success: {result.get('message', 'No message')[:50]}...")
            if 'info' in result:
                info = result['info']
                print(f"   📊 Mode: {info.get('mode', 'N/A')}")
                print(f"   📊 Response Time: {info.get('response_time', 'N/A')}")
            return True
        else:
            print(f"   ❌ Error: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Request failed: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False

def test_chat_with_invalid_json_document_names():
    """Test chat with invalid JSON document_names to validate JSON parsing fix"""
    print(f"\n🧪 Testing: Chat with invalid JSON document_names")
    
    test_session_id = f"test_invalid_json_{int(time.time())}"
    
    # Test with invalid JSON document_names
    data = {
        **TEST_CREDENTIALS,
        "question": "Hello, this is a test with invalid JSON document_names",
        "document_names": "invalid json string",  # This should trigger the fix
        "mode": "vector",
        "session_id": test_session_id
    }
    
    try:
        response = requests.post(f"{BASE_URL}/chat_bot", data=data, timeout=60)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Success: {result.get('message', 'No message')[:50]}...")
            if 'info' in result:
                info = result['info']
                print(f"   📊 Mode: {info.get('mode', 'N/A')}")
                print(f"   📊 Response Time: {info.get('response_time', 'N/A')}")
            return True
        else:
            print(f"   ❌ Error: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Request failed: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False

def test_chat_history_session_id_fix():
    """Test chat history to validate session_id attribute fix"""
    print(f"\n🧪 Testing: Chat History Session ID Fix")
    
    test_session_id = f"test_session_id_fix_{int(time.time())}"
    
    # Send multiple messages to test chat history
    messages = [
        "First message to test session_id",
        "Second message to test session_id",
        "Third message to test session_id"
    ]
    
    success_count = 0
    for i, message in enumerate(messages, 1):
        print(f"   Message {i}: '{message}'")
        
        data = {
            **TEST_CREDENTIALS,
            "question": message,
            "document_names": "[]",
            "mode": "vector",
            "session_id": test_session_id
        }
        
        try:
            response = requests.post(f"{BASE_URL}/chat_bot", data=data, timeout=60)
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Success: {result.get('message', 'No message')[:30]}...")
                success_count += 1
            else:
                print(f"   ❌ Error: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Request failed: {e}")
        except Exception as e:
            print(f"   ❌ Unexpected error: {e}")
        
        # Small delay between messages
        time.sleep(1)
    
    print(f"   📊 Success rate: {success_count}/{len(messages)} messages")
    return success_count == len(messages)

def test_health_endpoint():
    """Test the health endpoint to ensure the server is running"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Health check passed - server is running")
            return True
        else:
            print(f"❌ Health check failed - status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check failed - {e}")
        return False

def main():
    """Run all test scenarios"""
    print("🚀 Testing LLM Graph Builder - Chat Fixes Validation")
    print("=" * 60)
    
    # First check if server is running
    if not test_health_endpoint():
        print("\n❌ Server is not running. Please start the backend server first.")
        print("   Run: ./run-backend.sh")
        return
    
    # Test scenarios
    test_results = []
    
    print("\n" + "=" * 40)
    print("📋 Test 1: Document Names JSON Parsing Fixes")
    print("=" * 40)
    
    # Test 1.1: None document_names
    result1 = test_chat_with_none_document_names()
    test_results.append(("None document_names", result1))
    
    # Test 1.2: Empty document_names
    result2 = test_chat_with_empty_document_names()
    test_results.append(("Empty document_names", result2))
    
    # Test 1.3: Invalid JSON document_names
    result3 = test_chat_with_invalid_json_document_names()
    test_results.append(("Invalid JSON document_names", result3))
    
    print("\n" + "=" * 40)
    print("📋 Test 2: Session ID Attribute Fix")
    print("=" * 40)
    
    # Test 2: Session ID attribute fix
    result4 = test_chat_history_session_id_fix()
    test_results.append(("Session ID attribute fix", result4))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    
    passed_tests = 0
    total_tests = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed_tests += 1
    
    print(f"\n📈 Overall Results: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! The fixes are working correctly.")
        print("\n✅ Fixed Issues:")
        print("- 'Neo4jChatMessageHistory' object has no attribute 'session_id'")
        print("- TypeError: the JSON object must be str, bytes or bytearray, not NoneType")
        print("\n✅ Expected Behavior:")
        print("- Chat works with None, empty, or invalid document_names")
        print("- Chat history properly handles session_id attribute")
        print("- No more JSON parsing errors")
        print("- No more session_id attribute errors")
    else:
        print("⚠️  Some tests failed. Please check the logs for details.")
        print("\n🔍 Failed tests may indicate:")
        print("- Server not properly restarted with fixes")
        print("- Database connection issues")
        print("- Other underlying problems")

if __name__ == "__main__":
    main()
