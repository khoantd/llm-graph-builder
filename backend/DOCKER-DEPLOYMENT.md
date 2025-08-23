# 🐳 LLM Graph Builder - Enhanced Docker Deployment Guide

This guide provides comprehensive instructions for deploying the LLM Graph Builder backend with persistent data volumes, backup capabilities, and production-ready configurations.

## 📋 Table of Contents

1. [Quick Start](#-quick-start)
2. [Volume Management](#-volume-management)
3. [Deployment Options](#-deployment-options)
4. [Backup & Recovery](#-backup--recovery)
5. [Monitoring & Maintenance](#-monitoring--maintenance)
6. [Troubleshooting](#-troubleshooting)

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose installed
- At least 4GB RAM available
- 10GB+ disk space for data volumes

### 1. Clone and Setup

```bash
git clone <repository>
cd backend

# Create environment file
cp example.env .env
# Edit .env with your configuration
```

### 2. Development Deployment

```bash
# Start with development volumes (local bind mounts)
./run-backend-with-volumes.sh start

# Check status
./run-backend-with-volumes.sh status

# View logs
./run-backend-with-volumes.sh logs
```

### 3. Production Deployment

```bash
# Create persistent volumes
./manage-volumes.sh create

# Start production deployment
docker-compose -f docker-compose.production.yml up -d

# Monitor deployment
docker-compose -f docker-compose.production.yml logs -f
```

## 📁 Volume Management

### Volume Structure

The application uses 8 persistent data volumes:

| Volume | Purpose | Size Estimate | Persistence Level |
|--------|---------|---------------|-------------------|
| `data` | General application data | 100MB-1GB | High |
| `chunks` | Document chunks | 1GB-10GB | High |
| `merged_files` | Merged documents | 500MB-5GB | High |
| `logs` | Application logs | 50MB-500MB | Medium |
| `cache` | Application cache | 100MB-1GB | Low |
| `uploads` | File uploads | 100MB-2GB | High |
| `models` | ML models & embeddings | 2GB-20GB | High |
| `temp` | Temporary files | 50MB-500MB | Low |

### Volume Management Commands

```bash
# Create all volumes and directories
./manage-volumes.sh create

# List volume status
./manage-volumes.sh list

# Show volume usage
./manage-volumes.sh usage

# Create backup
./manage-volumes.sh backup

# Restore from backup
./manage-volumes.sh restore backup_20240101_120000

# Clean all volumes (DESTRUCTIVE)
./manage-volumes.sh clean
```

### Volume Types

#### 1. Local Bind Mounts (Development)
```bash
# Mount local directories directly
docker run -v $(pwd)/data:/code/data \
           -v $(pwd)/chunks:/code/chunks \
           your-image
```

**Pros:**
- ✅ Easy debugging and file access
- ✅ Simple backup/restore
- ✅ Live code reloading

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
- ✅ Better performance
- ✅ Easy migration

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

## 🚀 Deployment Options

### 1. Development Deployment

**File:** `docker-compose.development.yml`

```bash
# Start development deployment
docker-compose -f docker-compose.development.yml up -d

# Or use the enhanced script
./run-backend-with-volumes.sh start
```

**Features:**
- Local directory bind mounts
- Live code reloading
- Debug-friendly configuration
- Direct file access

### 2. Production Deployment

**File:** `docker-compose.production.yml`

```bash
# Create external volumes first
./manage-volumes.sh create

# Start production deployment
docker-compose -f docker-compose.production.yml up -d
```

**Features:**
- External Docker volumes
- Resource limits and health checks
- Production logging
- High availability

### 3. Standard Deployment

**File:** `docker-compose.backend.yml`

```bash
# Start standard deployment
docker-compose -f docker-compose.backend.yml up -d
```

**Features:**
- Mixed volume strategy
- Flexible configuration
- Balanced performance

### Enhanced Docker Run Script

```bash
# Complete container management
./run-backend-with-volumes.sh start    # Start container
./run-backend-with-volumes.sh stop     # Stop container
./run-backend-with-volumes.sh restart  # Restart container
./run-backend-with-volumes.sh status   # Check status
./run-backend-with-volumes.sh logs     # View logs
./run-backend-with-volumes.sh shell    # Open shell
./run-backend-with-volumes.sh backup   # Create backup
```

## 📊 Backup & Recovery

### Automated Backup

```bash
# Create timestamped backup
./manage-volumes.sh backup

# Output structure:
backup_20240101_120000/
├── data.tar.gz
├── chunks.tar.gz
├── merged_files.tar.gz
├── logs.tar.gz
├── cache.tar.gz
├── uploads.tar.gz
├── models.tar.gz
└── temp.tar.gz
```

### Restore from Backup

```bash
# Restore from specific backup
./manage-volumes.sh restore backup_20240101_120000
```

### Manual Backup

```bash
# Manual backup of specific directories
tar -czf backup_data.tar.gz data/
tar -czf backup_chunks.tar.gz chunks/
tar -czf backup_models.tar.gz models/
```

### Backup Strategy

#### Development Environment
```bash
# Daily backups during development
0 2 * * * /path/to/backend/manage-volumes.sh backup

# Keep last 7 days
find ./backup_* -type d -mtime +7 -exec rm -rf {} \;
```

#### Production Environment
```bash
# Hourly backups for critical data
0 * * * * /path/to/backend/manage-volumes.sh backup

# Daily full backups
0 2 * * * /path/to/backend/manage-volumes.sh backup

# Keep hourly backups for 24 hours
find ./backup_* -type d -mtime +1 -exec rm -rf {} \;

# Keep daily backups for 30 days
find ./backup_* -type d -mtime +30 -exec rm -rf {} \;
```

## 🔍 Monitoring & Maintenance

### Volume Usage Monitoring

```bash
# Check volume usage
./manage-volumes.sh usage

# Output example:
Volume Usage Statistics
================================
data: 256MB
chunks: 1.2GB
merged_files: 512MB
logs: 45MB
cache: 128MB
uploads: 64MB
models: 2.1GB
temp: 32MB
Total size: 4.3GB
```

### Container Health Monitoring

```bash
# Check container health
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# View health check logs
docker inspect llm-graph-builder-backend | jq '.[0].State.Health'

# Monitor resource usage
docker stats llm-graph-builder-backend
```

### Log Management

```bash
# View application logs
docker logs -f llm-graph-builder-backend

# View logs with timestamps
docker logs -f --timestamps llm-graph-builder-backend

# View logs for specific time period
docker logs --since "2024-01-01T00:00:00" llm-graph-builder-backend

# View logs with specific filters
docker logs llm-graph-builder-backend | grep ERROR
```

### Performance Monitoring

```bash
# Monitor container performance
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"

# Check volume I/O
docker exec llm-graph-builder-backend iostat -x 1 5

# Monitor disk usage
docker exec llm-graph-builder-backend df -h
```

## 🔧 Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Permission denied | Volume permissions | `chmod 755 data/ chunks/ logs/` |
| Volume not found | Volume not created | `./manage-volumes.sh create` |
| Data loss | Volume not mounted | Check volume mounts in docker-compose |
| Performance issues | Resource limits | Adjust memory/CPU limits |
| Backup fails | Insufficient space | Check disk space and cleanup |
| Container won't start | Port conflict | Change port in docker-compose |
| Health check fails | Application not ready | Increase start_period |

### Volume Inspection

```bash
# Inspect Docker volumes
docker volume inspect llm_graph_data

# Check volume mount points
docker inspect llm-graph-builder-backend | jq '.[0].Mounts'

# Verify data persistence
docker exec llm-graph-builder-backend ls -la /code/data

# Check volume permissions
docker exec llm-graph-builder-backend ls -la /code/
```

### Debug Commands

```bash
# Enter container shell
docker exec -it llm-graph-builder-backend /bin/bash

# Check container logs
docker logs llm-graph-builder-backend

# Check container configuration
docker inspect llm-graph-builder-backend

# Test volume access
docker exec llm-graph-builder-backend touch /code/data/test.txt

# Check disk usage in container
docker exec llm-graph-builder-backend df -h
```

### Performance Optimization

#### Resource Allocation

```yaml
# Adjust based on your hardware
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

# Optimize volume mount options
docker run -v /fast-storage:/code/data:rw,noatime \
           your-image
```

## 📈 Scaling Considerations

### Horizontal Scaling

```yaml
# docker-compose.scale.yml
version: '3.8'
services:
  backend:
    image: llm-graph-builder-backend:latest
    deploy:
      replicas: 3
    volumes:
      - shared_data:/code/data
      - shared_chunks:/code/chunks
    networks:
      - backend-network

volumes:
  shared_data:
    driver: rexray/s3fs
    driver_opts:
      bucket: llm-graph-data
  shared_chunks:
    driver: rexray/s3fs
    driver_opts:
      bucket: llm-graph-chunks

networks:
  backend-network:
    driver: overlay
```

### Load Balancing

```yaml
# docker-compose.lb.yml
version: '3.8'
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - backend

  backend:
    image: llm-graph-builder-backend:latest
    deploy:
      replicas: 3
    volumes:
      - shared_data:/code/data
```

## 🔒 Security Considerations

### Volume Security

```bash
# Set proper permissions
chmod 755 data/ chunks/ logs/
chown -R 1000:1000 data/ chunks/ logs/

# Use read-only mounts for config
docker run -v $(pwd)/.env:/code/.env:ro your-image

# Encrypt sensitive volumes
docker run -v encrypted_data:/code/data \
           --mount type=tmpfs,destination=/code/temp \
           your-image
```

### Network Security

```yaml
# Use internal networks
networks:
  backend:
    internal: true
  frontend:
    external: true

services:
  backend:
    networks:
      - backend
    expose:
      - "8000"
```

## 📚 Additional Resources

### Testing

```bash
# Test volume setup
python3 test-volume-setup.py

# Test environment configuration
python3 test_environment_config.py

# Test Docker deployment
./run-backend-with-volumes.sh start
./run-backend-with-volumes.sh status
```

### Documentation

- [Docker Compose Reference](https://docs.docker.com/compose/)
- [Docker Volume Management](https://docs.docker.com/storage/volumes/)
- [Docker Health Checks](https://docs.docker.com/engine/reference/builder/#healthcheck)

### Support

For issues and questions:
1. Check the troubleshooting section
2. Review container logs
3. Test volume setup
4. Verify environment configuration

---

**🎉 Enhanced Docker deployment provides comprehensive data persistence, backup capabilities, and monitoring tools for both development and production environments.**
