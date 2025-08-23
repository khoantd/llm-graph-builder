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

## 🐳 Enhanced Docker Deployment with Persistent Volumes

The application now includes comprehensive Docker deployment options with persistent data volumes for production-ready deployments.

### 📁 Persistent Data Volumes

The application uses the following persistent data volumes:

| Volume | Purpose | Path |
|--------|---------|------|
| `data` | General application data | `/code/data` |
| `chunks` | Document chunks | `/code/chunks` |
| `merged_files` | Merged document files | `/code/merged_files` |
| `logs` | Application logs | `/code/logs` |
| `cache` | Application cache | `/code/cache` |
| `uploads` | File uploads | `/code/uploads` |
| `models` | ML models and embeddings | `/code/models` |
| `temp` | Temporary files | `/code/temp` |

### 🚀 Deployment Options

#### 1. Development Deployment (Local Bind Mounts)

```bash
# Use development configuration
docker-compose -f docker-compose.development.yml up -d

# Or use the enhanced run script
./run-backend-with-volumes.sh start
```

**Features:**
- ✅ Local directory bind mounts
- ✅ Live code reloading
- ✅ Easy debugging
- ✅ Direct file access

#### 2. Production Deployment (Docker Volumes)

```bash
# Create persistent volumes first
./manage-volumes.sh create

# Use production configuration
docker-compose -f docker-compose.production.yml up -d
```

**Features:**
- ✅ External Docker volumes
- ✅ Data persistence across container restarts
- ✅ Resource limits and health checks
- ✅ Production logging

#### 3. Standard Deployment (Mixed Volumes)

```bash
# Use standard configuration
docker-compose -f docker-compose.backend.yml up -d
```

**Features:**
- ✅ Local bind mounts for development
- ✅ Docker volumes for production
- ✅ Flexible configuration

### 📋 Volume Management

#### Volume Management Script

Use the volume management script for comprehensive volume operations:

```bash
# Create volumes and directories
./manage-volumes.sh create

# List volume status
./manage-volumes.sh list

# Create backup
./manage-volumes.sh backup

# Restore from backup
./manage-volumes.sh restore backup_20240101_120000

# Show usage statistics
./manage-volumes.sh usage

# Clean all volumes (DESTRUCTIVE)
./manage-volumes.sh clean
```

#### Enhanced Docker Run Script

Use the enhanced run script for complete container management:

```bash
# Start container with volumes
./run-backend-with-volumes.sh start

# Check container status
./run-backend-with-volumes.sh status

# View logs
./run-backend-with-volumes.sh logs

# Open shell in container
./run-backend-with-volumes.sh shell

# Create backup
./run-backend-with-volumes.sh backup

# Stop container
./run-backend-with-volumes.sh stop

# Restart container
./run-backend-with-volumes.sh restart
```

### 🔧 Docker Compose Configurations

#### Development Configuration (`docker-compose.development.yml`)

```yaml
version: '3.8'
services:
  backend:
    image: llm-graph-builder-backend:latest
    container_name: llm-graph-builder-backend-dev
    ports:
      - "8000:8000"
    environment:
      - NODE_ENV=development
      - DEBUG=true
    volumes:
      # Local bind mounts for development
      - ./data:/code/data
      - ./chunks:/code/chunks
      - ./merged_files:/code/merged_files
      - ./logs:/code/logs
      - ./cache:/code/cache
      - ./uploads:/code/uploads
      - ./models:/code/models
      - ./temp:/code/temp
      
      # Source code for live reloading
      - ./src:/code/src
      - ./score.py:/code/score.py
```

#### Production Configuration (`docker-compose.production.yml`)

```yaml
version: '3.8'
services:
  backend:
    image: llm-graph-builder-backend:latest
    container_name: llm-graph-builder-backend
    ports:
      - "8000:8000"
    environment:
      - NODE_ENV=production
    volumes:
      # External persistent volumes
      - llm_graph_data:/code/data
      - llm_graph_chunks:/code/chunks
      - llm_graph_merged:/code/merged_files
      - llm_graph_logs:/code/logs
      - llm_graph_cache:/code/cache
      - llm_graph_uploads:/code/uploads
      - llm_graph_models:/code/models
      - llm_graph_temp:/code/temp
    deploy:
      resources:
        limits:
          memory: 8G
          cpus: '4.0'
    logging:
      driver: "json-file"
      options:
        max-size: "100m"
        max-file: "3"

volumes:
  llm_graph_data:
    external: true
  llm_graph_chunks:
    external: true
  # ... other volumes
```

### 🔄 Data Persistence Strategies

#### 1. Local Bind Mounts (Development)

```bash
# Mount local directories directly
docker run -v $(pwd)/data:/code/data \
           -v $(pwd)/chunks:/code/chunks \
           -v $(pwd)/logs:/code/logs \
           your-image
```

**Pros:**
- ✅ Easy debugging
- ✅ Direct file access
- ✅ Live code reloading
- ✅ Simple backup/restore

**Cons:**
- ❌ Platform-specific paths
- ❌ Less portable

#### 2. Docker Named Volumes (Production)

```bash
# Create named volumes
docker volume create llm_graph_data
docker volume create llm_graph_chunks

# Use named volumes
docker run -v llm_graph_data:/code/data \
           -v llm_graph_chunks:/code/chunks \
           your-image
```

**Pros:**
- ✅ Platform-independent
- ✅ Managed by Docker
- ✅ Easy migration
- ✅ Better performance

**Cons:**
- ❌ Less direct access
- ❌ Requires Docker commands for backup

#### 3. External Volumes (Enterprise)

```bash
# Use external storage
docker run -v /mnt/storage/llm_data:/code/data \
           -v /mnt/storage/llm_chunks:/code/chunks \
           your-image
```

**Pros:**
- ✅ Enterprise storage integration
- ✅ High availability
- ✅ Advanced backup solutions
- ✅ Scalable storage

**Cons:**
- ❌ Complex setup
- ❌ Requires storage expertise

### 📊 Backup and Recovery

#### Automated Backup

```bash
# Create backup with timestamp
./manage-volumes.sh backup

# Output: backup_20240101_120000/
# ├── data.tar.gz
# ├── chunks.tar.gz
# ├── merged_files.tar.gz
# ├── logs.tar.gz
# ├── cache.tar.gz
# ├── uploads.tar.gz
# ├── models.tar.gz
# └── temp.tar.gz
```

#### Restore from Backup

```bash
# Restore from specific backup
./manage-volumes.sh restore backup_20240101_120000
```

#### Manual Backup

```bash
# Manual backup of specific directories
tar -czf backup_data.tar.gz data/
tar -czf backup_chunks.tar.gz chunks/
tar -czf backup_models.tar.gz models/
```

### 🔍 Monitoring and Maintenance

#### Volume Usage Monitoring

```bash
# Check volume usage
./manage-volumes.sh usage

# Output:
# Volume Usage Statistics
# ================================
# data: 256MB
# chunks: 1.2GB
# merged_files: 512MB
# logs: 45MB
# cache: 128MB
# uploads: 64MB
# models: 2.1GB
# temp: 32MB
# Total size: 4.3GB
```

#### Container Health Monitoring

```bash
# Check container health
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# View health check logs
docker inspect llm-graph-builder-backend | jq '.[0].State.Health'
```

#### Log Management

```bash
# View application logs
docker logs -f llm-graph-builder-backend

# View logs with timestamps
docker logs -f --timestamps llm-graph-builder-backend

# View logs for specific time period
docker logs --since "2024-01-01T00:00:00" llm-graph-builder-backend
```

### 🚀 Quick Start Guide

#### 1. Development Setup

```bash
# Clone and setup
git clone <repository>
cd backend

# Create environment file
cp example.env .env
# Edit .env with your configuration

# Start with development volumes
./run-backend-with-volumes.sh start

# Check status
./run-backend-with-volumes.sh status
```

#### 2. Production Setup

```bash
# Create persistent volumes
./manage-volumes.sh create

# Start production deployment
docker-compose -f docker-compose.production.yml up -d

# Monitor deployment
docker-compose -f docker-compose.production.yml logs -f
```

#### 3. Backup Strategy

```bash
# Create regular backups
0 2 * * * /path/to/backend/manage-volumes.sh backup

# Clean old backups (keep last 7 days)
find ./backup_* -type d -mtime +7 -exec rm -rf {} \;
```

### 🔧 Troubleshooting

#### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Permission denied | Volume permissions | `chmod 755 data/ chunks/ logs/` |
| Volume not found | Volume not created | `./manage-volumes.sh create` |
| Data loss | Volume not mounted | Check volume mounts in docker-compose |
| Performance issues | Resource limits | Adjust memory/CPU limits |
| Backup fails | Insufficient space | Check disk space and cleanup |

#### Volume Inspection

```bash
# Inspect Docker volumes
docker volume inspect llm_graph_data

# Check volume mount points
docker inspect llm-graph-builder-backend | jq '.[0].Mounts'

# Verify data persistence
docker exec llm-graph-builder-backend ls -la /code/data
```

### 📈 Performance Optimization

#### Resource Allocation

```yaml
deploy:
  resources:
    limits:
      memory: 8G      # Adjust based on workload
      cpus: '4.0'     # Adjust based on CPU cores
    reservations:
      memory: 4G      # Minimum memory guarantee
      cpus: '2.0'     # Minimum CPU guarantee
```

#### Volume Performance

```bash
# Use SSD storage for high-performance volumes
docker run -v /ssd/data:/code/data \
           -v /ssd/cache:/code/cache \
           your-image

# Use tmpfs for temporary data
docker run --tmpfs /code/temp \
           your-image
```

The enhanced Docker deployment provides comprehensive data persistence, backup capabilities, and monitoring tools for both development and production environments.
