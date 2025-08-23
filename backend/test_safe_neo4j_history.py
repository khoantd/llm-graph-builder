#!/usr/bin/env python3
"""
Test script to validate SafeNeo4jChatMessageHistory class methods
Tests that all required methods are available and working
"""

import os
import sys
import tempfile
import json
from unittest.mock import Mock, patch

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_safe_neo4j_history_methods():
    """Test that SafeNeo4jChatMessageHistory has all required methods"""
    print("🧪 Testing SafeNeo4jChatMessageHistory Methods")
    print("=" * 50)
    
    try:
        from QA_integration import SafeNeo4jChatMessageHistory
        
        # Mock the Neo4jChatMessageHistory
        mock_graph = Mock()
        mock_neo4j_history = Mock()
        
        with patch('QA_integration.Neo4jChatMessageHistory', return_value=mock_neo4j_history):
            # Create instance
            history = SafeNeo4jChatMessageHistory(graph=mock_graph, session_id="test_session")
            
            # Test required methods
            required_methods = [
                'add_message',
                'add_user_message', 
                'add_ai_message',
                'add_system_message',
                'clear',
                'messages',
                'session_id'
            ]
            
            for method_name in required_methods:
                if hasattr(history, method_name):
                    print(f"   ✅ Method exists: {method_name}")
                else:
                    print(f"   ❌ Method missing: {method_name}")
                    return False
            
            # Test magic methods
            magic_methods = ['__len__', '__iter__', '__getitem__']
            for method_name in magic_methods:
                if hasattr(history, method_name):
                    print(f"   ✅ Magic method exists: {method_name}")
                else:
                    print(f"   ❌ Magic method missing: {method_name}")
                    return False
            
            print("   ✅ All required methods are present")
            return True
            
    except Exception as e:
        print(f"   ❌ Error testing methods: {e}")
        return False

def test_safe_neo4j_history_functionality():
    """Test the functionality of SafeNeo4jChatMessageHistory methods"""
    print("\n🧪 Testing SafeNeo4jChatMessageHistory Functionality")
    print("=" * 50)
    
    try:
        from QA_integration import SafeNeo4jChatMessageHistory
        from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
        
        # Mock the Neo4jChatMessageHistory
        mock_graph = Mock()
        mock_neo4j_history = Mock()
        mock_neo4j_history._messages = []
        
        with patch('QA_integration.Neo4jChatMessageHistory', return_value=mock_neo4j_history):
            # Create instance
            history = SafeNeo4jChatMessageHistory(graph=mock_graph, session_id="test_session")
            
            # Test session_id property
            if history.session_id == "test_session":
                print("   ✅ session_id property works")
            else:
                print(f"   ❌ session_id property failed: expected 'test_session', got '{history.session_id}'")
                return False
            
            # Test add_user_message
            try:
                history.add_user_message("Hello, how are you?")
                print("   ✅ add_user_message works")
            except Exception as e:
                print(f"   ❌ add_user_message failed: {e}")
                return False
            
            # Test add_ai_message
            try:
                history.add_ai_message("I'm doing well, thank you!")
                print("   ✅ add_ai_message works")
            except Exception as e:
                print(f"   ❌ add_ai_message failed: {e}")
                return False
            
            # Test add_system_message
            try:
                history.add_system_message("You are a helpful assistant.")
                print("   ✅ add_system_message works")
            except Exception as e:
                print(f"   ❌ add_system_message failed: {e}")
                return False
            
            # Test add_message with direct message objects
            try:
                user_msg = HumanMessage(content="Direct message test")
                history.add_message(user_msg)
                print("   ✅ add_message with direct message works")
            except Exception as e:
                print(f"   ❌ add_message with direct message failed: {e}")
                return False
            
            # Test clear method
            try:
                history.clear()
                print("   ✅ clear method works")
            except Exception as e:
                print(f"   ❌ clear method failed: {e}")
                return False
            
            # Test messages property
            try:
                messages = history.messages
                if isinstance(messages, list):
                    print("   ✅ messages property works")
                else:
                    print(f"   ❌ messages property failed: expected list, got {type(messages)}")
                    return False
            except Exception as e:
                print(f"   ❌ messages property failed: {e}")
                return False
            
            # Test magic methods
            try:
                length = len(history)
                print(f"   ✅ __len__ method works: {length}")
            except Exception as e:
                print(f"   ❌ __len__ method failed: {e}")
                return False
            
            try:
                # Test iteration
                for msg in history:
                    print(f"   ✅ __iter__ method works: found message of type {type(msg)}")
                    break
                else:
                    print("   ✅ __iter__ method works: no messages to iterate")
            except Exception as e:
                print(f"   ❌ __iter__ method failed: {e}")
                return False
            
            print("   ✅ All functionality tests passed")
            return True
            
    except Exception as e:
        print(f"   ❌ Error testing functionality: {e}")
        return False

def test_error_handling():
    """Test error handling in SafeNeo4jChatMessageHistory"""
    print("\n🧪 Testing Error Handling")
    print("=" * 50)
    
    try:
        from QA_integration import SafeNeo4jChatMessageHistory
        
        # Mock the Neo4jChatMessageHistory with errors
        mock_graph = Mock()
        mock_neo4j_history = Mock()
        mock_neo4j_history.add_message.side_effect = Exception("Test error")
        mock_neo4j_history.clear.side_effect = Exception("Test error")
        mock_neo4j_history._messages = [None, "invalid_message"]  # Invalid messages
        
        with patch('QA_integration.Neo4jChatMessageHistory', return_value=mock_neo4j_history):
            # Create instance
            history = SafeNeo4jChatMessageHistory(graph=mock_graph, session_id="test_session")
            
            # Test that add_user_message handles errors gracefully
            try:
                history.add_user_message("Test message")
                print("   ✅ add_user_message handles errors gracefully")
            except Exception as e:
                print(f"   ❌ add_user_message doesn't handle errors: {e}")
                return False
            
            # Test that clear handles errors gracefully
            try:
                history.clear()
                print("   ✅ clear method handles errors gracefully")
            except Exception as e:
                print(f"   ❌ clear method doesn't handle errors: {e}")
                return False
            
            # Test that messages property handles invalid messages
            try:
                messages = history.messages
                if isinstance(messages, list):
                    print("   ✅ messages property handles invalid messages gracefully")
                else:
                    print(f"   ❌ messages property failed with invalid messages: {type(messages)}")
                    return False
            except Exception as e:
                print(f"   ❌ messages property doesn't handle invalid messages: {e}")
                return False
            
            print("   ✅ All error handling tests passed")
            return True
            
    except Exception as e:
        print(f"   ❌ Error testing error handling: {e}")
        return False

def test_compatibility_with_standard_interface():
    """Test that SafeNeo4jChatMessageHistory is compatible with standard ChatMessageHistory interface"""
    print("\n🧪 Testing Interface Compatibility")
    print("=" * 50)
    
    try:
        from QA_integration import SafeNeo4jChatMessageHistory
        from langchain_community.chat_message_histories import ChatMessageHistory
        
        # Mock the Neo4jChatMessageHistory
        mock_graph = Mock()
        mock_neo4j_history = Mock()
        mock_neo4j_history._messages = []
        
        with patch('QA_integration.Neo4jChatMessageHistory', return_value=mock_neo4j_history):
            # Create instances
            safe_history = SafeNeo4jChatMessageHistory(graph=mock_graph, session_id="test_session")
            standard_history = ChatMessageHistory()
            
            # Test that both have the same interface methods
            safe_methods = set(dir(safe_history))
            standard_methods = set(dir(standard_history))
            
            # Key methods that should be present in both
            key_methods = {
                'add_message',
                'add_user_message',
                'add_ai_message', 
                'clear',
                'messages'
            }
            
            for method in key_methods:
                if method in safe_methods and method in standard_methods:
                    print(f"   ✅ Both have method: {method}")
                elif method in safe_methods:
                    print(f"   ⚠️  Only SafeNeo4jChatMessageHistory has: {method}")
                elif method in standard_methods:
                    print(f"   ❌ SafeNeo4jChatMessageHistory missing: {method}")
                    return False
                else:
                    print(f"   ❌ Neither has method: {method}")
                    return False
            
            print("   ✅ Interface compatibility verified")
            return True
            
    except Exception as e:
        print(f"   ❌ Error testing interface compatibility: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Testing SafeNeo4jChatMessageHistory Class")
    print("=" * 60)
    
    try:
        # Run all tests
        tests = [
            test_safe_neo4j_history_methods,
            test_safe_neo4j_history_functionality,
            test_error_handling,
            test_compatibility_with_standard_interface
        ]
        
        all_passed = True
        for test in tests:
            if not test():
                all_passed = False
        
        print("\n" + "=" * 60)
        if all_passed:
            print("🎉 All SafeNeo4jChatMessageHistory tests passed!")
            print("\n✅ Features validated:")
            print("- All required methods are present")
            print("- Methods work correctly")
            print("- Error handling is robust")
            print("- Interface compatibility maintained")
        else:
            print("❌ Some tests failed")
            return False
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
