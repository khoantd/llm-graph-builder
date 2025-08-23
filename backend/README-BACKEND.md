# LLM Graph Builder Backend - Docker Setup

This guide explains how to build and run the LLM Graph Builder backend as a separate Docker container.

## 🐳 Building the Docker Image

### Prerequisites
- Docker installed and running
- Git repository cloned

### Build Steps

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Build the Docker image:**
   ```bash
   docker build -t llm-graph-builder-backend .
   ```

   This will create an image named `llm-graph-builder-backend` with all dependencies installed.

## 🚀 Running the Backend Container

### Method 1: Using the Run Script (Recommended)

1. **Create environment file:**
   ```bash
   cp example.env .env
   ```

2. **Edit the .env file** with your configuration:
   ```bash
   # Required settings
   OPENAI_API_KEY=your_openai_api_key
   DIFFBOT_API_KEY=your_diffbot_api_key
   NEO4J_URI=your_neo4j_uri
   NEO4J_USERNAME=your_username
   NEO4J_PASSWORD=your_password
   NEO4J_DATABASE=your_database
   
   # Optional settings
   EMBEDDING_MODEL=all-MiniLM-L6-v2
   IS_EMBEDDING=TRUE
   ```

3. **Run the backend:**
   ```bash
   ./run-backend.sh
   ```

### Method 2: Using Docker Compose

1. **Create environment file** (same as above)

2. **Run with docker-compose:**
   ```bash
   docker-compose -f docker-compose.backend.yml up
   ```

### Method 3: Manual Docker Run

```bash
docker run -it --rm \
    --name llm-graph-builder-backend \
    -p 8000:8000 \
    --env-file .env \
    llm-graph-builder-backend
```

## 🔧 Configuration

### Environment Variables

The backend requires several environment variables. See `example.env` for the complete list:

**Required:**
- `OPENAI_API_KEY` - OpenAI API key for LLM operations
- `DIFFBOT_API_KEY` - Diffbot API key for NLP services
- `NEO4J_URI` - Neo4j database connection URI
- `NEO4J_USERNAME` - Neo4j username
- `NEO4J_PASSWORD` - Neo4j password
- `NEO4J_DATABASE` - Neo4j database name

**Optional:**
- `EMBEDDING_MODEL` - Embedding model (default: all-MiniLM-L6-v2)
- `IS_EMBEDDING` - Enable embeddings (default: TRUE)
- `GEMINI_ENABLED` - Enable Google Gemini (default: False)
- `AWS_ACCESS_KEY_ID` - AWS credentials for S3
- `AWS_SECRET_ACCESS_KEY` - AWS credentials for S3

### LLM Model Configuration

Configure different LLM models using the `LLM_MODEL_CONFIG_` prefix:

```bash
# OpenAI models
LLM_MODEL_CONFIG_openai_gpt_4o="gpt-4o-2024-11-20,openai_api_key"
LLM_MODEL_CONFIG_openai_gpt_4o_mini="gpt-4o-mini-2024-07-18,openai_api_key"

# Gemini models
LLM_MODEL_CONFIG_gemini_1.5_pro="gemini-1.5-pro-002"
LLM_MODEL_CONFIG_gemini_1.5_flash="gemini-1.5-flash-002"

# Diffbot
LLM_MODEL_CONFIG_diffbot="diffbot,diffbot_api_key"
```

## 🌐 Accessing the Backend

Once running, the backend will be available at:

- **API Base URL:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

## 📁 File Processing

The backend creates temporary directories for file processing:
- `./chunks/` - Document chunks
- `./merged_files/` - Merged document files

These directories are automatically created and cleaned up.

## 🔍 Troubleshooting

### Common Issues

1. **Port already in use:**
   ```bash
   # Change the port
   PORT=8001 ./run-backend.sh
   ```

2. **Environment variables missing:**
   - Ensure `.env` file exists and contains required variables
   - Check that API keys are valid

3. **Neo4j connection issues:**
   - Verify Neo4j URI, username, and password
   - Ensure Neo4j database is running and accessible

4. **Memory issues:**
   ```bash
   # Run with more memory
   docker run -it --rm \
       --name llm-graph-builder-backend \
       -p 8000:8000 \
       --memory=4g \
       --env-file .env \
       llm-graph-builder-backend
   ```

### Logs

View container logs:
```bash
docker logs llm-graph-builder-backend
```

### Container Management

- **Stop container:** `docker stop llm-graph-builder-backend`
- **Remove container:** `docker rm llm-graph-builder-backend`
- **Remove image:** `docker rmi llm-graph-builder-backend`

## 🔗 Integration with Frontend

To connect the frontend to this backend:

1. Set the backend URL in your frontend configuration:
   ```bash
   VITE_BACKEND_API_URL=http://localhost:8000
   ```

2. Ensure CORS is properly configured (handled automatically by the backend)

## 📚 API Endpoints

### Core APIs
- `POST /connect` - Connect to Neo4j database
- `POST /upload` - Upload and process documents
- `POST /schema` - Get database schema
- `POST /graph_query` - Query the knowledge graph
- `POST /chat_bot` - Chat with the knowledge graph
- `POST /clear_chat_bot` - Clear chat history

### Chat History Management APIs
- `POST /get_chat_histories` - Get all chat histories with pagination
- `POST /get_chat_history` - Get specific chat history by session ID
- `POST /delete_chat_history` - Delete specific chat history by session ID

### Health & Status
- `GET /health` - Health check endpoint

## Chat History Management

The backend now includes comprehensive chat history management capabilities:

### Get All Chat Histories
```bash
curl -X POST "http://localhost:8000/get_chat_histories" \
  -F "uri=neo4j://localhost:7687" \
  -F "userName=neo4j" \
  -F "password=password" \
  -F "database=neo4j" \
  -F "limit=10" \
  -F "offset=0"
```

**Parameters:**
- `uri`, `userName`, `password`, `database` (required) - Neo4j connection details
- `limit` (optional, default: 50) - Maximum number of chat histories to return (1-100)
- `offset` (optional, default: 0) - Number of chat histories to skip for pagination
- `email` (optional) - User email for logging

**Response:**
```json
{
  "status": "Success",
  "data": {
    "chat_histories": [
      {
        "session_id": "session_123",
        "created_at": "2024-01-01T10:00:00",
        "updated_at": "2024-01-01T10:30:00",
        "message_count": 5
      }
    ],
    "pagination": {
      "total_count": 25,
      "total_pages": 3,
      "current_page": 1,
      "limit": 10,
      "offset": 0,
      "has_next": true,
      "has_previous": false
    }
  },
  "message": "Retrieved 10 chat histories"
}
```

### Get Specific Chat History
```bash
curl -X POST "http://localhost:8000/get_chat_history" \
  -F "uri=neo4j://localhost:7687" \
  -F "userName=neo4j" \
  -F "password=password" \
  -F "database=neo4j" \
  -F "session_id=session_123"
```

**Parameters:**
- `uri`, `userName`, `password`, `database` (required) - Neo4j connection details
- `session_id` (required) - The session ID to retrieve
- `email` (optional) - User email for logging

**Response:**
```json
{
  "status": "Success",
  "data": {
    "session_id": "session_123",
    "created_at": "2024-01-01T10:00:00",
    "updated_at": "2024-01-01T10:30:00",
    "message_count": 5,
    "messages": [
      {
        "type": "human",
        "content": "Hello, how are you?",
        "additional_kwargs": {},
        "created_at": "2024-01-01T10:00:00"
      },
      {
        "type": "ai",
        "content": "I'm doing well, thank you!",
        "additional_kwargs": {},
        "created_at": "2024-01-01T10:00:05"
      }
    ]
  },
  "message": "Retrieved chat history for session session_123"
}
```

### Delete Chat History
```bash
curl -X POST "http://localhost:8000/delete_chat_history" \
  -F "uri=neo4j://localhost:7687" \
  -F "userName=neo4j" \
  -F "password=password" \
  -F "database=neo4j" \
  -F "session_id=session_123"
```

**Parameters:**
- `uri`, `userName`, `password`, `database` (required) - Neo4j connection details
- `session_id` (required) - The session ID to delete
- `email` (optional) - User email for logging

**Response:**
```json
{
  "status": "Success",
  "data": {
    "session_id": "session_123",
    "message": "Chat history deleted successfully",
    "deleted": true
  },
  "message": "Deleted chat history for session session_123"
}
```

## Testing Chat History APIs

Run the comprehensive test script to validate all chat history functionality:

```bash
cd backend
python3 test_chat_histories_api.py
```

This test script covers:
- ✅ Get all chat histories with pagination
- ✅ Get specific chat history by session ID
- ✅ Delete chat history by session ID
- ✅ Error handling and validation
- ✅ Pagination functionality
- ✅ CRUD operations verification

## 🔑 API Key Configuration

### OpenAI API Key Setup

The application requires proper API key configuration to function. Follow these steps:

1. **Create `.env` file**:
   ```bash
   cp example.env .env
   ```

2. **Configure OpenAI API Key**:
   ```bash
   # Edit .env file and set your OpenAI API key
   OPENAI_API_KEY="sk-your-actual-openai-api-key-here"
   ```

3. **Configure LLM Model**:
   ```bash
   # Set the default chat model (must match LLM_MODEL_CONFIG format)
   DEFAULT_DIFFBOT_CHAT_MODEL="openai_gpt_4o"
   
   # Configure the model with API key
   LLM_MODEL_CONFIG_openai_gpt_4o="gpt-4o-2024-11-20,sk-your-actual-openai-api-key-here"
   ```

### Alternative Models

You can use other models by configuring the appropriate environment variables:

```bash
# For GPT-3.5
LLM_MODEL_CONFIG_openai_gpt_3.5="gpt-3.5-turbo-0125,sk-your-actual-openai-api-key-here"

# For GPT-4o Mini
LLM_MODEL_CONFIG_openai_gpt_4o_mini="gpt-4o-mini-2024-07-18,sk-your-actual-openai-api-key-here"

# For Gemini (requires Google Cloud setup)
LLM_MODEL_CONFIG_gemini_1.5_pro="gemini-1.5-pro-002"
GEMINI_ENABLED=True

# For Anthropic Claude
LLM_MODEL_CONFIG_anthropic_claude_4_sonnet="claude-sonnet-4-20250514,sk-your-anthropic-api-key-here"
```

### Troubleshooting Authentication Errors

#### Error: `AuthenticationError: Error code: 401 - Incorrect API key provided`

**Root Cause**: The API key is either missing, incorrect, or not properly configured.

**Solutions**:

1. **Check API Key Format**:
   ```bash
   # OpenAI API keys should start with 'sk-'
   OPENAI_API_KEY="sk-1234567890abcdef..."
   ```

2. **Verify Environment Variables**:
   ```bash
   # Check if .env file exists and has correct values
   cat .env | grep OPENAI_API_KEY
   cat .env | grep LLM_MODEL_CONFIG
   ```

3. **Test API Key**:
   ```bash
   # Test your OpenAI API key
   curl -H "Authorization: Bearer sk-your-api-key" \
        https://api.openai.com/v1/models
   ```

4. **Check Model Configuration**:
   ```bash
   # Ensure model config matches the default model
   echo $DEFAULT_DIFFBOT_CHAT_MODEL
   echo $LLM_MODEL_CONFIG_openai_gpt_4o
   ```

5. **Restart Application**:
   ```bash
   # After updating .env, restart the application
   docker-compose down
   docker-compose up -d
   ```

#### Common Issues and Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| `401 AuthenticationError` | Invalid or missing API key | Set correct API key in `.env` |
| `Model not found` | Incorrect model name | Check model name in OpenAI API |
| `Rate limit exceeded` | Too many requests | Wait or upgrade API plan |
| `Insufficient quota` | API quota exceeded | Check OpenAI account billing |

### Environment Variables Checklist

Before starting the application, ensure these are set:

```bash
# Required for OpenAI models
OPENAI_API_KEY="sk-your-api-key"
DEFAULT_DIFFBOT_CHAT_MODEL="openai_gpt_4o"
LLM_MODEL_CONFIG_openai_gpt_4o="gpt-4o-2024-11-20,sk-your-api-key"

# Required for Neo4j
NEO4J_URI="neo4j://localhost:7687"
NEO4J_USERNAME="neo4j"
NEO4J_PASSWORD="your-password"
NEO4J_DATABASE="neo4j"

# Optional but recommended
EMBEDDING_MODEL="all-MiniLM-L6-v2"
GCS_FILE_CACHE="False"
```

### Testing Configuration

Run the configuration test script:

```bash
python3 test_configuration.py
```

This will verify:
- ✅ API key validity
- ✅ Model accessibility
- ✅ Neo4j connection
- ✅ Environment variables

## 🔧 Enhanced Environment Configuration

The application now uses an enhanced environment configuration system that properly handles environment variable precedence for Docker deployments.

### Environment Variable Precedence

The system follows this precedence order (highest to lowest priority):

1. **System Environment Variables** (highest priority)
2. **`.env` file** (fallback)
3. **Default values** (lowest priority)

This ensures that Docker environment variables take precedence over `.env` file values, which is the standard practice for containerized applications.

### Configuration Loading

The application automatically loads environment variables in the correct order:

```python
# System environment variables are checked first
# .env file is loaded as fallback (doesn't override system vars)
# Default values are used as last resort
```

### Usage Examples

#### Docker Deployment
```bash
# Docker environment variables take precedence
docker run -e OPENAI_API_KEY="sk-your-key" -e NEO4J_PASSWORD="your-password" your-image
```

#### Local Development
```bash
# .env file is used as fallback
cp example.env .env
# Edit .env with your values
```

#### Hybrid Setup
```bash
# System variables override .env file
export OPENAI_API_KEY="sk-your-key"
# .env file provides other variables
```

### Environment Configuration Module

The application includes a robust environment configuration module (`src/environment_config.py`) that provides:

- **Automatic precedence handling**
- **Type conversion** (bool, int, float)
- **Required variable validation**
- **Configuration summaries**
- **Graceful error handling**

#### Key Features

```python
from src.environment_config import get_env_var, get_env_bool, get_env_int

# Get environment variables with proper precedence
api_key = get_env_var('OPENAI_API_KEY', required=True)
debug_mode = get_env_bool('DEBUG', False)
port = get_env_int('PORT', 8000)
```

#### Configuration Validation

```python
# Validate required variables
required_vars = ['OPENAI_API_KEY', 'NEO4J_PASSWORD']
config.validate_required_vars(required_vars)
```

### Testing Environment Configuration

Run the environment configuration tests:

```bash
python3 test_environment_config.py
```

This validates:
- ✅ Environment variable precedence
- ✅ Type conversions
- ✅ Required variable validation
- ✅ Missing file handling
- ✅ Configuration loading

### Docker Environment Variables

When using Docker, you can set environment variables in several ways:

#### Docker Compose
```yaml
version: '3.8'
services:
  backend:
    image: llm-graph-builder-backend:latest
    environment:
      - OPENAI_API_KEY=sk-your-key
      - NEO4J_PASSWORD=your-password
      - DEFAULT_DIFFBOT_CHAT_MODEL=openai_gpt_4o
```

#### Docker Run
```bash
docker run -e OPENAI_API_KEY="sk-your-key" \
           -e NEO4J_PASSWORD="your-password" \
           -e DEFAULT_DIFFBOT_CHAT_MODEL="openai_gpt_4o" \
           your-image
```

#### Environment File
```bash
# Create .env file for docker-compose
echo "OPENAI_API_KEY=sk-your-key" > .env
echo "NEO4J_PASSWORD=your-password" >> .env
docker-compose up
```

### Troubleshooting Environment Issues

#### Check Environment Variables
```bash
# Test environment configuration
python3 test_environment_config.py

# Check system environment
env | grep OPENAI
env | grep NEO4J

# Check .env file
cat .env | grep -v "^#"
```

#### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Variables not loading | Wrong precedence order | Use enhanced config module |
| Docker vars ignored | .env file overriding | System vars take precedence |
| Missing variables | Not set anywhere | Set in Docker or .env file |
| Type errors | Wrong variable type | Use type conversion functions |

#### Debug Configuration

The application logs configuration details on startup:

```
🔧 Environment Configuration Summary
============================================================
📋 OPENAI_API_KEY: sk-1234567890...
📋 DEFAULT_DIFFBOT_CHAT_MODEL: openai_gpt_4o
📋 EMBEDDING_MODEL: all-MiniLM-L6-v2
📋 NEO4J_URI: neo4j://localhost:7687
📋 NEO4J_USERNAME: neo4j
📋 NEO4J_DATABASE: neo4j
⚠️  GEMINI_ENABLED: Not set
⚠️  GCS_FILE_CACHE: Not set
============================================================
```
