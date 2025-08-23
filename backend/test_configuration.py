#!/usr/bin/env python3
"""
Configuration test script for LLM Graph Builder
Tests API keys, environment variables, and model accessibility
"""

import os
import sys
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_openai_api_key():
    """Test OpenAI API key validity"""
    print("🔑 Testing OpenAI API Key...")
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("   ❌ OPENAI_API_KEY not found in environment variables")
        return False
    
    if not api_key.startswith('sk-'):
        print("   ❌ OPENAI_API_KEY format is invalid (should start with 'sk-')")
        return False
    
    try:
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get('https://api.openai.com/v1/models', headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("   ✅ OpenAI API key is valid")
            return True
        elif response.status_code == 401:
            print("   ❌ OpenAI API key is invalid or expired")
            return False
        else:
            print(f"   ⚠️  Unexpected response: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Network error: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False

def test_llm_model_config():
    """Test LLM model configuration"""
    print("\n🤖 Testing LLM Model Configuration...")
    
    default_model = os.getenv('DEFAULT_DIFFBOT_CHAT_MODEL')
    if not default_model:
        print("   ❌ DEFAULT_DIFFBOT_CHAT_MODEL not set")
        return False
    
    print(f"   📋 Default model: {default_model}")
    
    # Check if the model config exists
    model_config_key = f"LLM_MODEL_CONFIG_{default_model}"
    model_config = os.getenv(model_config_key)
    
    if not model_config:
        print(f"   ❌ {model_config_key} not found")
        return False
    
    print(f"   📋 Model config: {model_config}")
    
    # Parse the model config
    try:
        if "openai" in default_model:
            parts = model_config.split(',')
            if len(parts) != 2:
                print(f"   ❌ Invalid model config format. Expected 'model_name,api_key', got {len(parts)} parts")
                return False
            
            model_name, api_key = parts
            print(f"   📋 Model name: {model_name}")
            print(f"   📋 API key: {api_key[:10]}...{api_key[-4:] if len(api_key) > 14 else '***'}")
            
            if not api_key.startswith('sk-'):
                print("   ❌ API key format is invalid")
                return False
                
        elif "gemini" in default_model:
            print(f"   📋 Gemini model: {model_config}")
            
        elif "anthropic" in default_model:
            parts = model_config.split(',')
            if len(parts) != 2:
                print(f"   ❌ Invalid model config format. Expected 'model_name,api_key', got {len(parts)} parts")
                return False
            
            model_name, api_key = parts
            print(f"   📋 Model name: {model_name}")
            print(f"   📋 API key: {api_key[:10]}...{api_key[-4:] if len(api_key) > 14 else '***'}")
            
        else:
            print(f"   ⚠️  Unknown model type: {default_model}")
            
        print("   ✅ LLM model configuration is valid")
        return True
        
    except Exception as e:
        print(f"   ❌ Error parsing model config: {e}")
        return False

def test_neo4j_configuration():
    """Test Neo4j configuration"""
    print("\n🗄️  Testing Neo4j Configuration...")
    
    required_vars = ['NEO4J_URI', 'NEO4J_USERNAME', 'NEO4J_PASSWORD', 'NEO4J_DATABASE']
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
        else:
            if 'PASSWORD' in var:
                print(f"   📋 {var}: {'*' * len(value)}")
            else:
                print(f"   📋 {var}: {value}")
    
    if missing_vars:
        print(f"   ❌ Missing required Neo4j variables: {', '.join(missing_vars)}")
        return False
    
    print("   ✅ Neo4j configuration is complete")
    return True

def test_embedding_model():
    """Test embedding model configuration"""
    print("\n🔤 Testing Embedding Model Configuration...")
    
    embedding_model = os.getenv('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
    print(f"   📋 Embedding model: {embedding_model}")
    
    if embedding_model == 'all-MiniLM-L6-v2':
        print("   ✅ Using local embedding model (no API key required)")
        return True
    elif 'openai' in embedding_model.lower():
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("   ❌ OpenAI API key required for OpenAI embedding model")
            return False
        print("   ✅ OpenAI embedding model configured")
        return True
    else:
        print(f"   ⚠️  Unknown embedding model: {embedding_model}")
        return True

def test_optional_configurations():
    """Test optional configurations"""
    print("\n⚙️  Testing Optional Configurations...")
    
    optional_vars = {
        'GCS_FILE_CACHE': 'File caching configuration',
        'GEMINI_ENABLED': 'Gemini model enablement',
        'GCP_LOG_METRICS_ENABLED': 'Google Cloud logging',
        'ENTITY_EMBEDDING': 'Entity embedding enablement',
        'MAX_TOKEN_CHUNK_SIZE': 'Token chunk size'
    }
    
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value:
            print(f"   📋 {var}: {value} ({description})")
        else:
            print(f"   ⚪ {var}: Not set ({description})")
    
    print("   ✅ Optional configurations checked")
    return True

def test_environment_file():
    """Test if .env file exists and is readable"""
    print("\n📁 Testing Environment File...")
    
    env_file = '.env'
    if os.path.exists(env_file):
        print(f"   ✅ .env file exists")
        
        try:
            with open(env_file, 'r') as f:
                content = f.read()
                lines = content.split('\n')
                non_empty_lines = [line for line in lines if line.strip() and not line.startswith('#')]
                print(f"   📋 {len(non_empty_lines)} non-empty configuration lines")
                
                # Check for common issues
                for line in non_empty_lines:
                    if '=' in line:
                        key, value = line.split('=', 1)
                        if key.strip() == 'OPENAI_API_KEY' and value.strip() == '""':
                            print("   ⚠️  OPENAI_API_KEY is empty")
                        elif key.strip() == 'DEFAULT_DIFFBOT_CHAT_MODEL' and value.strip() == '""':
                            print("   ⚠️  DEFAULT_DIFFBOT_CHAT_MODEL is empty")
                
        except Exception as e:
            print(f"   ❌ Error reading .env file: {e}")
            return False
    else:
        print(f"   ❌ .env file not found. Create it from example.env:")
        print(f"      cp example.env .env")
        return False
    
    return True

def generate_configuration_report():
    """Generate a comprehensive configuration report"""
    print("\n" + "=" * 60)
    print("📊 Configuration Report")
    print("=" * 60)
    
    tests = [
        ("Environment File", test_environment_file),
        ("OpenAI API Key", test_openai_api_key),
        ("LLM Model Config", test_llm_model_config),
        ("Neo4j Configuration", test_neo4j_configuration),
        ("Embedding Model", test_embedding_model),
        ("Optional Configs", test_optional_configurations)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"   ❌ Error in {test_name}: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📈 Test Results Summary")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n📊 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All configuration tests passed! Your setup is ready.")
    else:
        print("⚠️  Some configuration issues found. Please fix them before starting the application.")
        print("\n🔧 Quick Fix Guide:")
        print("1. Copy example.env to .env: cp example.env .env")
        print("2. Edit .env and set your OpenAI API key")
        print("3. Configure your preferred LLM model")
        print("4. Set Neo4j connection details")
        print("5. Run this test again: python3 test_configuration.py")

def main():
    """Main function"""
    print("🚀 LLM Graph Builder - Configuration Test")
    print("=" * 60)
    
    generate_configuration_report()

if __name__ == "__main__":
    main()
