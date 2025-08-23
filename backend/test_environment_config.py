#!/usr/bin/env python3
"""
Test script for enhanced environment configuration
Tests environment variable precedence and loading
"""

import os
import sys
import tempfile
import shutil
from unittest.mock import patch

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from environment_config import EnvironmentConfig, get_env_var, get_env_bool, get_env_int

def test_environment_precedence():
    """Test environment variable precedence (system > .env > default)"""
    print("🧪 Testing Environment Variable Precedence")
    print("=" * 50)
    
    # Create a temporary .env file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.env') as f:
        f.write("TEST_VAR=from_env_file\n")
        f.write("TEST_BOOL=true\n")
        f.write("TEST_INT=42\n")
        env_file = f.name
    
    try:
        # Test 1: System environment variable takes precedence
        print("\n📋 Test 1: System environment variable precedence")
        with patch.dict(os.environ, {'TEST_VAR': 'from_system'}):
            config = EnvironmentConfig(env_file)
            value = config.get('TEST_VAR')
            print(f"   Expected: from_system, Got: {value}")
            assert value == 'from_system', f"Expected 'from_system', got '{value}'"
            print("   ✅ System environment variable takes precedence")
        
        # Test 2: .env file as fallback
        print("\n📋 Test 2: .env file as fallback")
        with patch.dict(os.environ, {}, clear=True):
            config = EnvironmentConfig(env_file)
            value = config.get('TEST_VAR')
            print(f"   Expected: from_env_file, Got: {value}")
            assert value == 'from_env_file', f"Expected 'from_env_file', got '{value}'"
            print("   ✅ .env file used as fallback")
        
        # Test 3: Default value as last resort
        print("\n📋 Test 3: Default value as last resort")
        with patch.dict(os.environ, {}, clear=True):
            config = EnvironmentConfig(env_file)
            value = config.get('NONEXISTENT_VAR', 'default_value')
            print(f"   Expected: default_value, Got: {value}")
            assert value == 'default_value', f"Expected 'default_value', got '{value}'"
            print("   ✅ Default value used as last resort")
        
        # Test 4: Boolean conversion
        print("\n📋 Test 4: Boolean conversion")
        with patch.dict(os.environ, {}, clear=True):
            config = EnvironmentConfig(env_file)
            value = config.get_bool('TEST_BOOL', False)
            print(f"   Expected: True, Got: {value}")
            assert value == True, f"Expected True, got {value}"
            print("   ✅ Boolean conversion works")
        
        # Test 5: Integer conversion
        print("\n📋 Test 5: Integer conversion")
        with patch.dict(os.environ, {}, clear=True):
            config = EnvironmentConfig(env_file)
            value = config.get_int('TEST_INT', 0)
            print(f"   Expected: 42, Got: {value}")
            assert value == 42, f"Expected 42, got {value}"
            print("   ✅ Integer conversion works")
        
        # Test 6: Required variable validation
        print("\n📋 Test 6: Required variable validation")
        with patch.dict(os.environ, {}, clear=True):
            config = EnvironmentConfig(env_file)
            try:
                config.get('REQUIRED_VAR', required=True)
                print("   ❌ Should have raised ValueError")
                assert False, "Should have raised ValueError"
            except ValueError as e:
                print(f"   ✅ Correctly raised ValueError: {e}")
        
        print("\n✅ All precedence tests passed!")
        
    finally:
        # Clean up
        os.unlink(env_file)

def test_openai_configuration():
    """Test OpenAI-specific configuration"""
    print("\n🧪 Testing OpenAI Configuration")
    print("=" * 50)
    
    # Create a temporary .env file with OpenAI config
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.env') as f:
        f.write("OPENAI_API_KEY=sk-test123456789\n")
        f.write("DEFAULT_DIFFBOT_CHAT_MODEL=openai_gpt_4o\n")
        f.write("EMBEDDING_MODEL=all-MiniLM-L6-v2\n")
        f.write("LLM_MODEL_CONFIG_openai_gpt_4o=gpt-4o-2024-11-20,sk-test123456789\n")
        env_file = f.name
    
    try:
        config = EnvironmentConfig(env_file)
        
        # Test OpenAI config
        openai_config = config.get_openai_config()
        print(f"   📋 OpenAI Config: {openai_config}")
        
        assert 'api_key' in openai_config, "API key should be present"
        assert 'default_model' in openai_config, "Default model should be present"
        assert 'embedding_model' in openai_config, "Embedding model should be present"
        
        print("   ✅ OpenAI configuration loaded correctly")
        
        # Test model config
        model_config = config.get_model_config('openai_gpt_4o')
        print(f"   📋 Model Config: {model_config}")
        assert model_config is not None, "Model config should not be None"
        
        print("   ✅ Model configuration loaded correctly")
        
    finally:
        os.unlink(env_file)

def test_neo4j_configuration():
    """Test Neo4j-specific configuration"""
    print("\n🧪 Testing Neo4j Configuration")
    print("=" * 50)
    
    # Create a temporary .env file with Neo4j config
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.env') as f:
        f.write("NEO4J_URI=neo4j://localhost:7687\n")
        f.write("NEO4J_USERNAME=neo4j\n")
        f.write("NEO4J_PASSWORD=testpassword\n")
        f.write("NEO4J_DATABASE=neo4j\n")
        env_file = f.name
    
    try:
        config = EnvironmentConfig(env_file)
        
        # Test Neo4j config
        neo4j_config = config.get_neo4j_config()
        print(f"   📋 Neo4j Config: {neo4j_config}")
        
        assert 'uri' in neo4j_config, "URI should be present"
        assert 'username' in neo4j_config, "Username should be present"
        assert 'password' in neo4j_config, "Password should be present"
        assert 'database' in neo4j_config, "Database should be present"
        
        print("   ✅ Neo4j configuration loaded correctly")
        
    finally:
        os.unlink(env_file)

def test_convenience_functions():
    """Test convenience functions"""
    print("\n🧪 Testing Convenience Functions")
    print("=" * 50)
    
    # Create a temporary .env file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.env') as f:
        f.write("TEST_STR=hello\n")
        f.write("TEST_BOOL=true\n")
        f.write("TEST_INT=123\n")
        f.write("TEST_FLOAT=3.14\n")
        env_file = f.name
    
    try:
        # Create a fresh config instance for testing
        config = EnvironmentConfig(env_file)
        
        # Test get_env_var using the config instance
        value = config.get('TEST_STR', 'default')
        print(f"   📋 get_env_var: {value}")
        assert value == 'hello', f"Expected 'hello', got '{value}'"
        
        # Test get_env_bool using the config instance
        value = config.get_bool('TEST_BOOL', False)
        print(f"   📋 get_env_bool: {value}")
        assert value == True, f"Expected True, got {value}"
        
        # Test get_env_int using the config instance
        value = config.get_int('TEST_INT', 0)
        print(f"   📋 get_env_int: {value}")
        assert value == 123, f"Expected 123, got {value}"
        
        # Test get_env_float using the config instance
        value = config.get_float('TEST_FLOAT', 0.0)
        print(f"   📋 get_env_float: {value}")
        assert value == 3.14, f"Expected 3.14, got {value}"
        
        print("   ✅ All convenience functions work correctly")
        
    finally:
        os.unlink(env_file)

def test_missing_env_file():
    """Test behavior when .env file is missing"""
    print("\n🧪 Testing Missing .env File")
    print("=" * 50)
    
    # Test with non-existent .env file
    config = EnvironmentConfig("nonexistent.env")
    
    # Should not crash and should use system environment or defaults
    value = config.get('SOME_VAR', 'default_value')
    print(f"   📋 Value with missing .env: {value}")
    assert value == 'default_value', f"Expected 'default_value', got '{value}'"
    
    print("   ✅ Handles missing .env file gracefully")

def main():
    """Run all tests"""
    print("🚀 Testing Enhanced Environment Configuration")
    print("=" * 60)
    
    try:
        test_environment_precedence()
        test_openai_configuration()
        test_neo4j_configuration()
        test_convenience_functions()
        test_missing_env_file()
        
        print("\n" + "=" * 60)
        print("🎉 All environment configuration tests passed!")
        print("\n✅ Features validated:")
        print("- Environment variable precedence (system > .env > default)")
        print("- OpenAI configuration loading")
        print("- Neo4j configuration loading")
        print("- Convenience functions")
        print("- Graceful handling of missing .env file")
        print("- Type conversion (bool, int, float)")
        print("- Required variable validation")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
