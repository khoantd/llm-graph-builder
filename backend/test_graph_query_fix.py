#!/usr/bin/env python3
"""
Test script to validate the graph_query API fix
Tests various scenarios for the document_names parameter
"""

import requests
import json
import sys

# Configuration
BASE_URL = "http://localhost:8000"
TEST_ENDPOINT = f"{BASE_URL}/graph_query"

# Test credentials (update these with your actual values)
TEST_CREDENTIALS = {
    "uri": "neo4j://localhost:7687",
    "userName": "neo4j",
    "password": "password",
    "database": "neo4j",
    "email": "test@example.com"
}

def test_graph_query(document_names, description):
    """Test the graph_query endpoint with different document_names values"""
    print(f"\n🧪 Testing: {description}")
    print(f"   document_names: '{document_names}'")
    
    data = {
        **TEST_CREDENTIALS,
        "document_names": document_names
    }
    
    try:
        response = requests.post(TEST_ENDPOINT, data=data, timeout=30)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Success: {result.get('message', 'No message')}")
            if 'data' in result and result['data']:
                nodes_count = len(result['data'].get('nodes', []))
                rels_count = len(result['data'].get('relationships', []))
                print(f"   📊 Results: {nodes_count} nodes, {rels_count} relationships")
            else:
                print(f"   📊 Results: No data returned")
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
    print("🚀 Testing LLM Graph Builder - Graph Query API Fix")
    print("=" * 60)
    
    # First check if server is running
    if not test_health_endpoint():
        print("\n❌ Server is not running. Please start the backend server first.")
        print("   Run: ./run-backend.sh")
        return
    
    # Test scenarios
    test_cases = [
        ("", "Empty string"),
        ("null", "String 'null'"),
        (None, "None value"),
        ("[]", "Empty JSON array"),
        ("[\"test.pdf\"]", "Single document"),
        ("[\"doc1.pdf\", \"doc2.pdf\"]", "Multiple documents"),
        ("invalid json", "Invalid JSON string"),
        ("{\"wrong\": \"format\"}", "Wrong JSON format (object instead of array)"),
    ]
    
    for document_names, description in test_cases:
        test_graph_query(document_names, description)
    
    print("\n" + "=" * 60)
    print("✅ Test completed!")
    print("\nExpected behavior after fix:")
    print("- Empty/null values should return empty results (not crash)")
    print("- Valid JSON arrays should work normally")
    print("- Invalid JSON should return validation error (not crash)")
    print("- No more 'ParameterMissing' or 'NoneType' errors")

if __name__ == "__main__":
    main()
