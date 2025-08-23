#!/usr/bin/env python3
"""
Setup script for LLM Graph Builder environment configuration
Helps users create and configure their .env file
"""

import os
import sys
import shutil

def create_env_file():
    """Create .env file from example.env if it doesn't exist"""
    if os.path.exists('.env'):
        print("📁 .env file already exists")
        return True
    
    if os.path.exists('example.env'):
        try:
            shutil.copy('example.env', '.env')
            print("✅ Created .env file from example.env")
            return True
        except Exception as e:
            print(f"❌ Error creating .env file: {e}")
            return False
    else:
        print("❌ example.env file not found")
        return False

def get_user_input(prompt, default=""):
    """Get user input with a default value"""
    if default:
        user_input = input(f"{prompt} (default: {default}): ").strip()
        return user_input if user_input else default
    else:
        return input(f"{prompt}: ").strip()

def configure_openai():
    """Configure OpenAI settings"""
    print("\n🔑 OpenAI Configuration")
    print("=" * 40)
    
    api_key = get_user_input("Enter your OpenAI API key (starts with 'sk-')")
    if not api_key.startswith('sk-'):
        print("⚠️  Warning: API key should start with 'sk-'")
    
    model_choice = get_user_input(
        "Choose default model",
        "openai_gpt_4o"
    )
    
    return {
        'OPENAI_API_KEY': api_key,
        'DEFAULT_DIFFBOT_CHAT_MODEL': model_choice
    }

def configure_neo4j():
    """Configure Neo4j settings"""
    print("\n🗄️  Neo4j Configuration")
    print("=" * 40)
    
    uri = get_user_input("Neo4j URI", "neo4j://localhost:7687")
    username = get_user_input("Neo4j Username", "neo4j")
    password = get_user_input("Neo4j Password", "password")
    database = get_user_input("Neo4j Database", "neo4j")
    
    return {
        'NEO4J_URI': uri,
        'NEO4J_USERNAME': username,
        'NEO4J_PASSWORD': password,
        'NEO4J_DATABASE': database
    }

def configure_optional_settings():
    """Configure optional settings"""
    print("\n⚙️  Optional Settings")
    print("=" * 40)
    
    embedding_model = get_user_input(
        "Embedding model",
        "all-MiniLM-L6-v2"
    )
    
    gcs_cache = get_user_input(
        "Enable GCS file cache (True/False)",
        "False"
    )
    
    return {
        'EMBEDDING_MODEL': embedding_model,
        'GCS_FILE_CACHE': gcs_cache
    }

def update_env_file(config):
    """Update .env file with new configuration"""
    if not os.path.exists('.env'):
        print("❌ .env file not found. Run setup first.")
        return False
    
    try:
        # Read current .env file
        with open('.env', 'r') as f:
            lines = f.readlines()
        
        # Create a dictionary of current values
        current_config = {}
        for line in lines:
            if '=' in line and not line.strip().startswith('#'):
                key, value = line.split('=', 1)
                current_config[key.strip()] = value.strip()
        
        # Update with new values
        current_config.update(config)
        
        # Write back to .env file
        with open('.env', 'w') as f:
            for key, value in current_config.items():
                f.write(f'{key}={value}\n')
        
        print("✅ Updated .env file with new configuration")
        return True
        
    except Exception as e:
        print(f"❌ Error updating .env file: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 LLM Graph Builder - Environment Setup")
    print("=" * 50)
    
    # Step 1: Create .env file
    if not create_env_file():
        print("❌ Failed to create .env file")
        return
    
    # Step 2: Get configuration from user
    print("\n📝 Please provide the following configuration:")
    
    # OpenAI configuration
    openai_config = configure_openai()
    
    # Neo4j configuration
    neo4j_config = configure_neo4j()
    
    # Optional settings
    optional_config = configure_optional_settings()
    
    # Combine all configurations
    all_config = {**openai_config, **neo4j_config, **optional_config}
    
    # Step 3: Update .env file
    if update_env_file(all_config):
        print("\n✅ Setup completed successfully!")
        print("\n📋 Configuration Summary:")
        for key, value in all_config.items():
            if 'PASSWORD' in key or 'API_KEY' in key:
                display_value = f"{value[:10]}...{value[-4:]}" if len(value) > 14 else "***"
            else:
                display_value = value
            print(f"   {key}: {display_value}")
        
        print("\n🔧 Next Steps:")
        print("1. Run configuration test: python3 test_configuration.py")
        print("2. Start the backend: ./run-backend.sh")
        print("3. Test the API endpoints")
    else:
        print("❌ Setup failed. Please check the error messages above.")

if __name__ == "__main__":
    main()
