#!/usr/bin/env python3
"""
Test script to validate the chat message history fix
Tests various scenarios for the chat_bot API
"""

import requests
import json
import sys

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

def test_chat_bot(question, document_names, mode, session_id, description):
    """Test the chat_bot endpoint with different parameters"""
    print(f"\n🧪 Testing: {description}")
    print(f"   Question: '{question}'")
    print(f"   Mode: {mode}")
    print(f"   Session ID: {session_id}")
    print(f"   Document Names: '{document_names}'")
    
    data = {
        **TEST_CREDENTIALS,
        "question": question,
        "document_names": document_names,
        "mode": mode,
        "session_id": session_id
    }
    
    try:
        response = requests.post(TEST_ENDPOINT, data=data, timeout=60)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Success: {result.get('message', 'No message')[:100]}...")
            if 'info' in result:
                info = result['info']
                print(f"   📊 Mode: {info.get('mode', 'N/A')}")
                print(f"   📊 Response Time: {info.get('response_time', 'N/A')}")
        else:
            print(f"   ❌ Error: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Request failed: {e}")
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")

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
    print("🚀 Testing LLM Graph Builder - Chat Bot API Fix")
    print("=" * 60)
    
    # First check if server is running
    if not test_health_endpoint():
        print("\n❌ Server is not running. Please start the backend server first.")
        print("   Run: ./run-backend.sh")
        return
    
    # Test scenarios
    test_cases = [
        {
            "question": "What is the main topic?",
            "document_names": "[]",
            "mode": "vector",
            "session_id": "test_session_1",
            "description": "Vector mode with empty documents"
        },
        {
            "question": "Tell me about the content",
            "document_names": "[\"test.pdf\"]",
            "mode": "graph_vector",
            "session_id": "test_session_2",
            "description": "Graph+Vector mode with single document"
        },
        {
            "question": "Summarize the information",
            "document_names": "[\"doc1.pdf\", \"doc2.pdf\"]",
            "mode": "graph",
            "session_id": "test_session_3",
            "description": "Graph mode with multiple documents"
        },
        {
            "question": "What are the key points?",
            "document_names": "null",
            "mode": "vector",
            "session_id": "test_session_4",
            "description": "Vector mode with null documents"
        },
        {
            "question": "Explain the concepts",
            "document_names": "",
            "mode": "fulltext",
            "session_id": "test_session_5",
            "description": "Fulltext mode with empty string documents"
        }
    ]
    
    for test_case in test_cases:
        test_chat_bot(**test_case)
    
    print("\n" + "=" * 60)
    print("✅ Test completed!")
    print("\nExpected behavior after fix:")
    print("- No more 'Got unexpected message type: None' errors")
    print("- Chat history should be properly validated and cleaned")
    print("- Corrupted history should be automatically reset")
    print("- All chat modes should work without crashing")

if __name__ == "__main__":
    main()
