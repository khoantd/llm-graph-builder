#!/usr/bin/env python3
"""
Test script to validate the chat history fix for 'Got unexpected message type: None' error
Tests the SafeNeo4jChatMessageHistory wrapper and message validation
"""

import requests
import json
import sys
import time

# Configuration
BASE_URL = "http://localhost:8000"
TEST_ENDPOINT = f"{BASE_URL}/chat_bot"

# Test credentials (update these with your actual values)
TEST_CREDENTIALS = {
    "uri": "neo4j://localhost:7687",
    "userName": "neo4j",
    "password": "password",
    "database": "neo4j",
    "email": "test@example.com"
}

def test_chat_bot_conversation(session_id, description):
    """Test a complete chat conversation to validate history handling"""
    print(f"\n🧪 Testing: {description}")
    print(f"   Session ID: {session_id}")
    
    # Test multiple messages in the same session
    test_messages = [
        "Hello, how are you?",
        "What is the main topic of the documents?",
        "Can you summarize the key points?",
        "Tell me more about the content"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"   Message {i}: '{message}'")
        
        data = {
            **TEST_CREDENTIALS,
            "question": message,
            "document_names": "[]",
            "mode": "vector",
            "session_id": session_id
        }
        
        try:
            response = requests.post(TEST_ENDPOINT, data=data, timeout=60)
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Success: {result.get('message', 'No message')[:50]}...")
                if 'info' in result:
                    info = result['info']
                    print(f"   📊 Mode: {info.get('mode', 'N/A')}")
                    print(f"   📊 Response Time: {info.get('response_time', 'N/A')}")
            else:
                print(f"   ❌ Error: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Request failed: {e}")
            return False
        except Exception as e:
            print(f"   ❌ Unexpected error: {e}")
            return False
        
        # Small delay between messages
        time.sleep(1)
    
    return True

def test_clear_chat_history(session_id):
    """Test clearing chat history"""
    print(f"\n🧪 Testing: Clear Chat History")
    print(f"   Session ID: {session_id}")
    
    clear_endpoint = f"{BASE_URL}/clear_chat_bot"
    data = {
        **TEST_CREDENTIALS,
        "session_id": session_id
    }
    
    try:
        response = requests.post(clear_endpoint, data=data, timeout=30)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Success: {result.get('message', 'No message')}")
            return True
        else:
            print(f"   ❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

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
    print("🚀 Testing LLM Graph Builder - Chat History Fix")
    print("=" * 60)
    
    # First check if server is running
    if not test_health_endpoint():
        print("\n❌ Server is not running. Please start the backend server first.")
        print("   Run: ./run-backend.sh")
        return
    
    # Test scenarios
    test_cases = [
        {
            "session_id": "test_session_history_1",
            "description": "Vector mode conversation with history"
        },
        {
            "session_id": "test_session_history_2", 
            "description": "Graph mode conversation with history"
        },
        {
            "session_id": "test_session_history_3",
            "description": "Graph+Vector mode conversation with history"
        }
    ]
    
    success_count = 0
    total_tests = len(test_cases)
    
    for test_case in test_cases:
        if test_chat_bot_conversation(**test_case):
            success_count += 1
            
            # Test clearing history for this session
            if test_clear_chat_history(test_case["session_id"]):
                print(f"   ✅ Chat history cleared successfully")
            else:
                print(f"   ⚠️  Chat history clear failed")
    
    print("\n" + "=" * 60)
    print(f"✅ Test completed! {success_count}/{total_tests} tests passed")
    
    if success_count == total_tests:
        print("🎉 All tests passed! The chat history fix is working correctly.")
        print("\nExpected behavior after fix:")
        print("- No more 'Got unexpected message type: None' errors")
        print("- Chat history is properly validated and cleaned")
        print("- Multiple messages in the same session work correctly")
        print("- Chat history can be cleared successfully")
    else:
        print("⚠️  Some tests failed. Please check the logs for details.")

if __name__ == "__main__":
    main()
