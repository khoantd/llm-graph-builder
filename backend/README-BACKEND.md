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

Key endpoints available:

- `POST /upload-file` - Upload and process files
- `POST /generate-graph` - Generate knowledge graph
- `POST /chat` - Chat with processed data
- `GET /files` - List processed files
- `GET /health` - Health check

For complete API documentation, visit http://localhost:8000/docs when the backend is running.
