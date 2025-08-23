#!/bin/bash

# LLM Graph Builder - Enhanced Docker Run Script with Persistent Volumes
# Runs the backend container with comprehensive volume mounts

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
IMAGE_NAME="llm-graph-builder-backend"
CONTAINER_NAME="llm-graph-builder-backend"
PORT=${PORT:-8000}
ENV_FILE=".env"

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Function to check prerequisites
check_prerequisites() {
    print_header "Checking Prerequisites"
    
    # Check if Docker is running
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
    print_status "Docker is running"
    
    # Check if image exists
    if ! docker image inspect "$IMAGE_NAME:latest" >/dev/null 2>&1; then
        print_warning "Docker image $IMAGE_NAME:latest not found"
        print_status "Building Docker image..."
        docker build -t "$IMAGE_NAME:latest" .
    else
        print_status "Docker image found: $IMAGE_NAME:latest"
    fi
    
    # Check if .env file exists
    if [ ! -f "$ENV_FILE" ]; then
        print_warning ".env file not found. Creating from example.env..."
        if [ -f "example.env" ]; then
            cp example.env .env
            print_status "Created .env file from example.env"
            print_warning "Please edit .env file with your configuration"
        else
            print_error "example.env file not found"
            exit 1
        fi
    else
        print_status "Environment file found: $ENV_FILE"
    fi
}

# Function to create data directories
create_data_directories() {
    print_header "Creating Data Directories"
    
    local directories=(
        "data"
        "chunks"
        "merged_files"
        "logs"
        "cache"
        "uploads"
        "models"
        "temp"
    )
    
    for dir in "${directories[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            print_status "Created directory: $dir"
        else
            print_warning "Directory already exists: $dir"
        fi
        chmod 755 "$dir"
    done
}

# Function to stop existing container
stop_existing_container() {
    print_header "Stopping Existing Container"
    
    if docker ps -q -f name="$CONTAINER_NAME" | grep -q .; then
        print_status "Stopping existing container: $CONTAINER_NAME"
        docker stop "$CONTAINER_NAME"
        docker rm "$CONTAINER_NAME"
        print_status "Container stopped and removed"
    else
        print_status "No existing container found"
    fi
}

# Function to run container with volumes
run_container() {
    print_header "Starting Container with Persistent Volumes"
    
    local volume_mounts=(
        "-v $(pwd)/data:/code/data"
        "-v $(pwd)/chunks:/code/chunks"
        "-v $(pwd)/merged_files:/code/merged_files"
        "-v $(pwd)/logs:/code/logs"
        "-v $(pwd)/cache:/code/cache"
        "-v $(pwd)/uploads:/code/uploads"
        "-v $(pwd)/models:/code/models"
        "-v $(pwd)/temp:/code/temp"
    )
    
    local env_mounts=(
        "-v $(pwd)/.env:/code/.env:ro"
        "-v $(pwd)/example.env:/code/example.env:ro"
    )
    
    # Build the docker run command
    local cmd="docker run -d"
    cmd="$cmd --name $CONTAINER_NAME"
    cmd="$cmd -p $PORT:8000"
    cmd="$cmd --env-file $ENV_FILE"
    cmd="$cmd --restart unless-stopped"
    
    # Add volume mounts
    for mount in "${volume_mounts[@]}"; do
        cmd="$cmd $mount"
    done
    
    # Add environment file mounts
    for mount in "${env_mounts[@]}"; do
        cmd="$cmd $mount"
    done
    
    # Add resource limits
    cmd="$cmd --memory=4g"
    cmd="$cmd --cpus=2.0"
    
    # Add health check
    cmd="$cmd --health-cmd='curl -f http://localhost:8000/health || exit 1'"
    cmd="$cmd --health-interval=30s"
    cmd="$cmd --health-timeout=10s"
    cmd="$cmd --health-retries=3"
    cmd="$cmd --health-start-period=40s"
    
    # Add logging
    cmd="$cmd --log-driver=json-file"
    cmd="$cmd --log-opt max-size=100m"
    cmd="$cmd --log-opt max-file=3"
    
    # Add the image
    cmd="$cmd $IMAGE_NAME:latest"
    
    print_status "Running command: $cmd"
    eval "$cmd"
    
    if [ $? -eq 0 ]; then
        print_status "Container started successfully"
    else
        print_error "Failed to start container"
        exit 1
    fi
}

# Function to show container status
show_status() {
    print_header "Container Status"
    
    if docker ps -q -f name="$CONTAINER_NAME" | grep -q .; then
        print_status "Container is running"
        docker ps -f name="$CONTAINER_NAME"
        
        print_header "Volume Mounts"
        docker inspect "$CONTAINER_NAME" | jq -r '.[0].Mounts[] | "\(.Source) -> \(.Destination)"' 2>/dev/null || echo "jq not available for detailed mount info"
        
        print_header "Logs (last 10 lines)"
        docker logs --tail 10 "$CONTAINER_NAME"
    else
        print_error "Container is not running"
    fi
}

# Function to show help
show_help() {
    echo "LLM Graph Builder - Enhanced Docker Run Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start       Start the container with persistent volumes"
    echo "  stop        Stop and remove the container"
    echo "  restart     Restart the container"
    echo "  status      Show container status and logs"
    echo "  logs        Show container logs"
    echo "  shell       Open shell in running container"
    echo "  backup      Create backup of data volumes"
    echo "  help        Show this help message"
    echo ""
    echo "Environment Variables:"
    echo "  PORT        Port to bind (default: 8000)"
    echo "  ENV_FILE    Environment file (default: .env)"
    echo ""
    echo "Examples:"
    echo "  $0 start"
    echo "  $0 status"
    echo "  $0 logs"
    echo "  PORT=9000 $0 start"
}

# Function to show logs
show_logs() {
    print_header "Container Logs"
    
    if docker ps -q -f name="$CONTAINER_NAME" | grep -q .; then
        docker logs -f "$CONTAINER_NAME"
    else
        print_error "Container is not running"
        exit 1
    fi
}

# Function to open shell
open_shell() {
    print_header "Opening Shell in Container"
    
    if docker ps -q -f name="$CONTAINER_NAME" | grep -q .; then
        docker exec -it "$CONTAINER_NAME" /bin/bash
    else
        print_error "Container is not running"
        exit 1
    fi
}

# Function to create backup
create_backup() {
    print_header "Creating Data Backup"
    
    local backup_dir="backup_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$backup_dir"
    
    local directories=("data" "chunks" "merged_files" "logs" "cache" "uploads" "models" "temp")
    
    for dir in "${directories[@]}"; do
        if [ -d "$dir" ] && [ "$(ls -A "$dir" 2>/dev/null)" ]; then
            print_status "Backing up: $dir"
            tar -czf "$backup_dir/${dir}.tar.gz" -C . "$dir"
        else
            print_warning "Skipping empty directory: $dir"
        fi
    done
    
    print_status "Backup completed: $backup_dir"
}

# Main script logic
case "${1:-help}" in
    start)
        check_prerequisites
        create_data_directories
        stop_existing_container
        run_container
        show_status
        ;;
    stop)
        print_header "Stopping Container"
        if docker ps -q -f name="$CONTAINER_NAME" | grep -q .; then
            docker stop "$CONTAINER_NAME"
            docker rm "$CONTAINER_NAME"
            print_status "Container stopped and removed"
        else
            print_warning "Container is not running"
        fi
        ;;
    restart)
        print_header "Restarting Container"
        $0 stop
        sleep 2
        $0 start
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    shell)
        open_shell
        ;;
    backup)
        create_backup
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
