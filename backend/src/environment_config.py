"""
Enhanced Environment Configuration Module
Handles environment variable loading with proper precedence:
1. System environment variables (highest priority)
2. .env file (fallback)
3. Default values (lowest priority)
"""

import os
import logging
from typing import Optional, Any
from dotenv import load_dotenv

class EnvironmentConfig:
    """
    Enhanced environment configuration manager that properly handles
    environment variable precedence for Docker deployments.
    """
    
    def __init__(self, env_file_path: str = ".env"):
        """
        Initialize the environment configuration.
        
        Args:
            env_file_path: Path to the .env file (default: .env)
        """
        self.env_file_path = env_file_path
        self._loaded = False
        self._load_environment()
    
    def _load_environment(self):
        """Load environment variables with proper precedence."""
        try:
            # Load .env file as fallback (system env vars take precedence)
            if os.path.exists(self.env_file_path):
                logging.info(f"Loading environment from {self.env_file_path}")
                load_dotenv(self.env_file_path, override=False)  # Don't override system vars
            else:
                logging.warning(f".env file not found at {self.env_file_path}")
            
            self._loaded = True
            logging.info("Environment configuration loaded successfully")
            
        except Exception as e:
            logging.error(f"Error loading environment configuration: {e}")
            self._loaded = False
    
    def get(self, key: str, default: Any = None, required: bool = False) -> Optional[str]:
        """
        Get an environment variable with proper precedence handling.
        
        Args:
            key: Environment variable name
            default: Default value if not found
            required: Whether the variable is required
            
        Returns:
            Environment variable value or default
            
        Raises:
            ValueError: If required variable is not found
        """
        # System environment variables take precedence
        value = os.environ.get(key)
        
        if value is not None:
            logging.debug(f"Using system environment variable: {key}")
            return value
        
        # Check if .env file was loaded and try again
        if not self._loaded:
            self._load_environment()
            value = os.environ.get(key)
        
        if value is not None:
            logging.debug(f"Using .env file variable: {key}")
            return value
        
        if required:
            raise ValueError(f"Required environment variable '{key}' not found in system environment or .env file")
        
        logging.debug(f"Using default value for: {key}")
        return default
    
    def get_bool(self, key: str, default: bool = False) -> bool:
        """Get a boolean environment variable."""
        value = self.get(key, str(default))
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'on')
        return bool(value)
    
    def get_int(self, key: str, default: int = 0) -> int:
        """Get an integer environment variable."""
        value = self.get(key, str(default))
        try:
            return int(value)
        except (ValueError, TypeError):
            logging.warning(f"Invalid integer value for {key}: {value}, using default: {default}")
            return default
    
    def get_float(self, key: str, default: float = 0.0) -> float:
        """Get a float environment variable."""
        value = self.get(key, str(default))
        try:
            return float(value)
        except (ValueError, TypeError):
            logging.warning(f"Invalid float value for {key}: {value}, using default: {default}")
            return default
    
    def validate_required_vars(self, required_vars: list) -> dict:
        """
        Validate that all required environment variables are present.
        
        Args:
            required_vars: List of required environment variable names
            
        Returns:
            Dictionary of validated variables
            
        Raises:
            ValueError: If any required variable is missing
        """
        missing_vars = []
        validated_vars = {}
        
        for var in required_vars:
            try:
                value = self.get(var, required=True)
                validated_vars[var] = value
                logging.info(f"✅ Validated required variable: {var}")
            except ValueError:
                missing_vars.append(var)
                logging.error(f"❌ Missing required variable: {var}")
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return validated_vars
    
    def get_openai_config(self) -> dict:
        """Get OpenAI-specific configuration."""
        return {
            'api_key': self.get('OPENAI_API_KEY', required=True),
            'default_model': self.get('DEFAULT_DIFFBOT_CHAT_MODEL', 'openai_gpt_4o'),
            'embedding_model': self.get('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
        }
    
    def get_neo4j_config(self) -> dict:
        """Get Neo4j-specific configuration."""
        return {
            'uri': self.get('NEO4J_URI', 'neo4j://localhost:7687'),
            'username': self.get('NEO4J_USERNAME', 'neo4j'),
            'password': self.get('NEO4J_PASSWORD', 'password'),
            'database': self.get('NEO4J_DATABASE', 'neo4j')
        }
    
    def get_model_config(self, model_name: str) -> Optional[str]:
        """Get LLM model configuration."""
        config_key = f"LLM_MODEL_CONFIG_{model_name}"
        return self.get(config_key)
    
    def log_configuration_summary(self):
        """Log a summary of the current configuration."""
        logging.info("=" * 60)
        logging.info("🔧 Environment Configuration Summary")
        logging.info("=" * 60)
        
        # Log important configuration values
        important_vars = [
            'OPENAI_API_KEY',
            'DEFAULT_DIFFBOT_CHAT_MODEL',
            'EMBEDDING_MODEL',
            'NEO4J_URI',
            'NEO4J_USERNAME',
            'NEO4J_DATABASE',
            'GEMINI_ENABLED',
            'GCS_FILE_CACHE'
        ]
        
        for var in important_vars:
            value = self.get(var)
            if value:
                if 'PASSWORD' in var or 'API_KEY' in var:
                    display_value = f"{value[:10]}...{value[-4:]}" if len(value) > 14 else "***"
                else:
                    display_value = value
                logging.info(f"📋 {var}: {display_value}")
            else:
                logging.warning(f"⚠️  {var}: Not set")
        
        logging.info("=" * 60)

# Global environment configuration instance
env_config = EnvironmentConfig()

def get_env_var(key: str, default: Any = None, required: bool = False) -> Optional[str]:
    """
    Convenience function to get environment variables.
    
    Args:
        key: Environment variable name
        default: Default value
        required: Whether the variable is required
        
    Returns:
        Environment variable value
    """
    return env_config.get(key, default, required)

def get_env_bool(key: str, default: bool = False) -> bool:
    """Get a boolean environment variable."""
    return env_config.get_bool(key, default)

def get_env_int(key: str, default: int = 0) -> int:
    """Get an integer environment variable."""
    return env_config.get_int(key, default)

def get_env_float(key: str, default: float = 0.0) -> float:
    """Get a float environment variable."""
    return env_config.get_float(key, default)
