#!/usr/bin/env python3
"""
Demonstration script for enhanced environment configuration
Shows how environment variables are loaded with proper precedence
"""

import os
import sys

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from environment_config import EnvironmentConfig, get_env_var

def demo_environment_precedence():
    """Demonstrate environment variable precedence"""
    print("🚀 Enhanced Environment Configuration Demo")
    print("=" * 60)
    
    # Create a demo .env file
    with open('.env.demo', 'w') as f:
        f.write("OPENAI_API_KEY=sk-from-env-file\n")
        f.write("NEO4J_PASSWORD=password-from-env-file\n")
        f.write("DEBUG=true\n")
        f.write("PORT=8000\n")
    
    try:
        print("📁 Created demo .env file with values:")
        with open('.env.demo', 'r') as f:
            for line in f:
                print(f"   {line.strip()}")
        
        print("\n🔧 Loading environment configuration...")
        config = EnvironmentConfig('.env.demo')
        
        print("\n📋 Environment Configuration Summary:")
        config.log_configuration_summary()
        
        print("\n🧪 Testing precedence scenarios:")
        
        # Test 1: Value from .env file
        print("\n1. Value from .env file (no system override):")
        value = config.get('DEBUG', 'false')
        print(f"   DEBUG = {value}")
        
        # Test 2: System environment variable override
        print("\n2. System environment variable override:")
        os.environ['NEO4J_PASSWORD'] = 'password-from-system'
        value = config.get('NEO4J_PASSWORD', 'default-password')
        print(f"   NEO4J_PASSWORD = {value}")
        
        # Test 3: Default value when not set
        print("\n3. Default value when not set:")
        value = config.get('UNSET_VAR', 'default-value')
        print(f"   UNSET_VAR = {value}")
        
        # Test 4: Type conversions
        print("\n4. Type conversions:")
        debug_bool = config.get_bool('DEBUG', False)
        port_int = config.get_int('PORT', 3000)
        print(f"   DEBUG (bool) = {debug_bool}")
        print(f"   PORT (int) = {port_int}")
        
        # Test 5: Required variable validation
        print("\n5. Required variable validation:")
        try:
            config.get('REQUIRED_VAR', required=True)
        except ValueError as e:
            print(f"   ✅ Correctly caught missing required variable: {e}")
        
        print("\n✅ Environment configuration demo completed!")
        
    finally:
        # Clean up
        if os.path.exists('.env.demo'):
            os.unlink('.env.demo')

def demo_docker_integration():
    """Demonstrate Docker environment variable integration"""
    print("\n🐳 Docker Environment Variable Integration Demo")
    print("=" * 60)
    
    print("📋 Docker environment variables take precedence over .env file")
    print("\nExample Docker commands:")
    
    print("\n1. Docker run with environment variables:")
    print("   docker run -e OPENAI_API_KEY='sk-your-key' \\")
    print("              -e NEO4J_PASSWORD='your-password' \\")
    print("              -e DEFAULT_DIFFBOT_CHAT_MODEL='openai_gpt_4o' \\")
    print("              your-image")
    
    print("\n2. Docker Compose with environment:")
    print("   version: '3.8'")
    print("   services:")
    print("     backend:")
    print("       image: llm-graph-builder-backend:latest")
    print("       environment:")
    print("         - OPENAI_API_KEY=sk-your-key")
    print("         - NEO4J_PASSWORD=your-password")
    print("         - DEFAULT_DIFFBOT_CHAT_MODEL=openai_gpt_4o")
    
    print("\n3. Docker Compose with .env file:")
    print("   # .env file")
    print("   OPENAI_API_KEY=sk-your-key")
    print("   NEO4J_PASSWORD=your-password")
    print("   ")
    print("   # docker-compose.yml")
    print("   version: '3.8'")
    print("   services:")
    print("     backend:")
    print("       image: llm-graph-builder-backend:latest")
    print("       env_file:")
    print("         - .env")
    
    print("\n✅ Docker integration demo completed!")

def main():
    """Main demonstration function"""
    demo_environment_precedence()
    demo_docker_integration()
    
    print("\n" + "=" * 60)
    print("🎉 Enhanced Environment Configuration Demo Complete!")
    print("\n📚 Key Benefits:")
    print("- ✅ System environment variables take precedence")
    print("- ✅ .env file provides fallback values")
    print("- ✅ Default values ensure application stability")
    print("- ✅ Type conversion for different variable types")
    print("- ✅ Required variable validation")
    print("- ✅ Comprehensive logging and debugging")
    print("- ✅ Docker-friendly configuration")
    
    print("\n🔧 Next Steps:")
    print("1. Test with your own environment variables")
    print("2. Deploy with Docker using environment variables")
    print("3. Use the configuration test: python3 test_environment_config.py")

if __name__ == "__main__":
    main()
