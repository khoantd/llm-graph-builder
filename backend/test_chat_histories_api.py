#!/usr/bin/env python3
"""
Test script for the new chat history APIs
Tests get_chat_histories, get_chat_history, and delete_chat_history endpoints
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

def test_get_chat_histories(limit=10, offset=0, description=""):
    """Test the get_chat_histories endpoint"""
    print(f"\n🧪 Testing: Get Chat Histories {description}")
    print(f"   Limit: {limit}, Offset: {offset}")
    
    data = {
        **TEST_CREDENTIALS,
        "limit": limit,
        "offset": offset
    }
    
    try:
        response = requests.post(f"{BASE_URL}/get_chat_histories", data=data, timeout=30)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Success: {result.get('message', 'No message')}")
            
            if 'data' in result and result['data']:
                data_content = result['data']
                chat_histories = data_content.get('chat_histories', [])
                pagination = data_content.get('pagination', {})
                
                print(f"   📊 Retrieved {len(chat_histories)} chat histories")
                print(f"   📊 Total count: {pagination.get('total_count', 0)}")
                print(f"   📊 Current page: {pagination.get('current_page', 0)}")
                print(f"   📊 Total pages: {pagination.get('total_pages', 0)}")
                
                # Show first few chat histories
                for i, history in enumerate(chat_histories[:3]):
                    print(f"   📝 History {i+1}: {history.get('session_id', 'N/A')} - {history.get('message_count', 0)} messages")
                
                return chat_histories
            else:
                print(f"   📊 No chat histories found")
                return []
        else:
            print(f"   ❌ Error: {response.text}")
            return []
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Request failed: {e}")
        return []
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return []

def test_get_chat_history(session_id, description=""):
    """Test the get_chat_history endpoint"""
    print(f"\n🧪 Testing: Get Chat History {description}")
    print(f"   Session ID: {session_id}")
    
    data = {
        **TEST_CREDENTIALS,
        "session_id": session_id
    }
    
    try:
        response = requests.post(f"{BASE_URL}/get_chat_history", data=data, timeout=30)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Success: {result.get('message', 'No message')}")
            
            if 'data' in result and result['data']:
                data_content = result['data']
                messages = data_content.get('messages', [])
                
                print(f"   📊 Session: {data_content.get('session_id', 'N/A')}")
                print(f"   📊 Message count: {len(messages)}")
                print(f"   📊 Created: {data_content.get('created_at', 'N/A')}")
                print(f"   📊 Updated: {data_content.get('updated_at', 'N/A')}")
                
                # Show first few messages
                for i, message in enumerate(messages[:3]):
                    print(f"   💬 Message {i+1}: {message.get('type', 'N/A')} - {message.get('content', '')[:50]}...")
                
                return data_content
            else:
                print(f"   📊 No chat history data found")
                return None
        else:
            print(f"   ❌ Error: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Request failed: {e}")
        return None
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return None

def test_delete_chat_history(session_id, description=""):
    """Test the delete_chat_history endpoint"""
    print(f"\n🧪 Testing: Delete Chat History {description}")
    print(f"   Session ID: {session_id}")
    
    data = {
        **TEST_CREDENTIALS,
        "session_id": session_id
    }
    
    try:
        response = requests.post(f"{BASE_URL}/delete_chat_history", data=data, timeout=30)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Success: {result.get('message', 'No message')}")
            
            if 'data' in result and result['data']:
                data_content = result['data']
                print(f"   📊 Deleted: {data_content.get('deleted', False)}")
                print(f"   📊 Session: {data_content.get('session_id', 'N/A')}")
            
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
    print("🚀 Testing LLM Graph Builder - Chat Histories API")
    print("=" * 60)
    
    # First check if server is running
    if not test_health_endpoint():
        print("\n❌ Server is not running. Please start the backend server first.")
        print("   Run: ./run-backend.sh")
        return
    
    # Test 1: Get all chat histories with pagination
    print("\n" + "=" * 40)
    print("📋 Test 1: Get All Chat Histories")
    print("=" * 40)
    
    chat_histories = test_get_chat_histories(limit=5, offset=0, description="(First 5)")
    
    if chat_histories:
        # Test 2: Get specific chat history
        print("\n" + "=" * 40)
        print("📋 Test 2: Get Specific Chat History")
        print("=" * 40)
        
        first_session_id = chat_histories[0].get('session_id') if chat_histories else None
        if first_session_id:
            chat_history = test_get_chat_history(first_session_id, description="(First session)")
            
            # Test 3: Delete chat history (only if we have a valid session)
            if chat_history:
                print("\n" + "=" * 40)
                print("📋 Test 3: Delete Chat History")
                print("=" * 40)
                
                # Create a test session first by sending a chat message
                print("   🔄 Creating test chat session...")
                test_session_id = f"test_delete_session_{int(time.time())}"
                
                # Send a test message to create a session
                chat_data = {
                    **TEST_CREDENTIALS,
                    "question": "Hello, this is a test message",
                    "document_names": "[]",
                    "mode": "vector",
                    "session_id": test_session_id
                }
                
                try:
                    chat_response = requests.post(f"{BASE_URL}/chat_bot", data=chat_data, timeout=30)
                    if chat_response.status_code == 200:
                        print(f"   ✅ Test session created: {test_session_id}")
                        
                        # Now test deletion
                        delete_success = test_delete_chat_history(test_session_id, description="(Test session)")
                        
                        if delete_success:
                            # Verify deletion by trying to get the deleted session
                            print(f"\n   🔍 Verifying deletion...")
                            deleted_history = test_get_chat_history(test_session_id, description="(Should be deleted)")
                            if not deleted_history:
                                print(f"   ✅ Deletion verified - session no longer exists")
                            else:
                                print(f"   ⚠️  Deletion verification failed - session still exists")
                        else:
                            print(f"   ❌ Deletion failed")
                    else:
                        print(f"   ❌ Failed to create test session")
                except Exception as e:
                    print(f"   ❌ Error creating test session: {e}")
        else:
            print("   ⚠️  No chat histories found to test with")
    else:
        print("   ⚠️  No chat histories found")
    
    # Test 4: Pagination
    print("\n" + "=" * 40)
    print("📋 Test 4: Pagination")
    print("=" * 40)
    
    test_get_chat_histories(limit=3, offset=0, description="(Page 1)")
    test_get_chat_histories(limit=3, offset=3, description="(Page 2)")
    
    # Test 5: Error handling
    print("\n" + "=" * 40)
    print("📋 Test 5: Error Handling")
    print("=" * 40)
    
    # Test with invalid parameters
    print("   🧪 Testing invalid limit...")
    test_get_chat_histories(limit=0, offset=0, description="(Invalid limit)")
    
    print("   🧪 Testing invalid offset...")
    test_get_chat_histories(limit=10, offset=-1, description="(Invalid offset)")
    
    print("   🧪 Testing missing session_id...")
    test_get_chat_history("", description="(Empty session ID)")
    
    print("   🧪 Testing non-existent session...")
    test_get_chat_history("non_existent_session_12345", description="(Non-existent session)")
    
    print("\n" + "=" * 60)
    print("✅ Chat Histories API Test completed!")
    print("\nAPI Endpoints tested:")
    print("- POST /get_chat_histories - Get all chat histories with pagination")
    print("- POST /get_chat_history - Get specific chat history by session ID")
    print("- POST /delete_chat_history - Delete specific chat history by session ID")
    print("\nFeatures tested:")
    print("- Pagination (limit/offset)")
    print("- Error handling")
    print("- Data validation")
    print("- CRUD operations")

if __name__ == "__main__":
    main()
