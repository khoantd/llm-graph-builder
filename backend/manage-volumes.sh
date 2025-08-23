#!/bin/bash

# LLM Graph Builder - Volume Management Script
# Manages persistent data volumes for Docker deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Volume directories
VOLUME_DIRS=(
    "data"
    "chunks"
    "merged_files"
    "logs"
    "cache"
    "uploads"
    "models"
    "temp"
)

# Volume names for Docker
VOLUME_NAMES=(
    "llm_graph_data"
    "llm_graph_chunks"
    "llm_graph_merged"
    "llm_graph_logs"
    "llm_graph_cache"
    "llm_graph_uploads"
    "llm_graph_models"
    "llm_graph_temp"
)

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

# Function to create local directories
create_local_directories() {
    print_header "Creating Local Data Directories"
    
    for dir in "${VOLUME_DIRS[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            print_status "Created directory: $dir"
        else
            print_warning "Directory already exists: $dir"
        fi
    done
    
    # Set proper permissions
    for dir in "${VOLUME_DIRS[@]}"; do
        chmod 755 "$dir"
        print_status "Set permissions for: $dir"
    done
}

# Function to create Docker volumes
create_docker_volumes() {
    print_header "Creating Docker Volumes"
    
    for volume in "${VOLUME_NAMES[@]}"; do
        if ! docker volume inspect "$volume" >/dev/null 2>&1; then
            docker volume create "$volume"
            print_status "Created Docker volume: $volume"
        else
            print_warning "Docker volume already exists: $volume"
        fi
    done
}

# Function to list volumes
list_volumes() {
    print_header "Docker Volumes Status"
    
    for volume in "${VOLUME_NAMES[@]}"; do
        if docker volume inspect "$volume" >/dev/null 2>&1; then
            volume_info=$(docker volume inspect "$volume" | jq -r '.[0].Mountpoint // "N/A"')
            print_status "$volume: $volume_info"
        else
            print_error "$volume: Not found"
        fi
    done
    
    print_header "Local Directories Status"
    
    for dir in "${VOLUME_DIRS[@]}"; do
        if [ -d "$dir" ]; then
            size=$(du -sh "$dir" 2>/dev/null | cut -f1 || echo "N/A")
            print_status "$dir: $size"
        else
            print_error "$dir: Not found"
        fi
    done
}

# Function to backup volumes
backup_volumes() {
    local backup_dir="backup_$(date +%Y%m%d_%H%M%S)"
    
    print_header "Creating Volume Backup"
    
    mkdir -p "$backup_dir"
    
    for dir in "${VOLUME_DIRS[@]}"; do
        if [ -d "$dir" ] && [ "$(ls -A "$dir" 2>/dev/null)" ]; then
            print_status "Backing up: $dir"
            tar -czf "$backup_dir/${dir}.tar.gz" -C . "$dir"
        else
            print_warning "Skipping empty directory: $dir"
        fi
    done
    
    print_status "Backup completed: $backup_dir"
}

# Function to restore volumes
restore_volumes() {
    local backup_dir="$1"
    
    if [ -z "$backup_dir" ]; then
        print_error "Please specify backup directory"
        echo "Usage: $0 restore <backup_directory>"
        exit 1
    fi
    
    if [ ! -d "$backup_dir" ]; then
        print_error "Backup directory not found: $backup_dir"
        exit 1
    fi
    
    print_header "Restoring Volumes from Backup"
    
    for dir in "${VOLUME_DIRS[@]}"; do
        backup_file="$backup_dir/${dir}.tar.gz"
        if [ -f "$backup_file" ]; then
            print_status "Restoring: $dir"
            rm -rf "$dir"
            tar -xzf "$backup_file"
        else
            print_warning "Backup file not found: $backup_file"
        fi
    done
    
    print_status "Restore completed"
}

# Function to clean volumes
clean_volumes() {
    print_header "Cleaning Volumes"
    
    read -p "Are you sure you want to clean all volumes? This will delete all data! (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        for dir in "${VOLUME_DIRS[@]}"; do
            if [ -d "$dir" ]; then
                print_status "Cleaning: $dir"
                rm -rf "$dir"/*
            fi
        done
        
        for volume in "${VOLUME_NAMES[@]}"; do
            if docker volume inspect "$volume" >/dev/null 2>&1; then
                print_status "Removing Docker volume: $volume"
                docker volume rm "$volume"
            fi
        done
        
        print_status "Clean completed"
    else
        print_warning "Clean operation cancelled"
    fi
}

# Function to show volume usage
show_usage() {
    print_header "Volume Usage Statistics"
    
    total_size=0
    
    for dir in "${VOLUME_DIRS[@]}"; do
        if [ -d "$dir" ]; then
            size=$(du -sb "$dir" 2>/dev/null | cut -f1 || echo "0")
            size_mb=$((size / 1024 / 1024))
            total_size=$((total_size + size))
            print_status "$dir: ${size_mb}MB"
        fi
    done
    
    total_mb=$((total_size / 1024 / 1024))
    print_status "Total size: ${total_mb}MB"
}

# Function to show help
show_help() {
    echo "LLM Graph Builder - Volume Management Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  create      Create local directories and Docker volumes"
    echo "  list        List all volumes and their status"
    echo "  backup      Create a backup of all volumes"
    echo "  restore     Restore volumes from backup"
    echo "  clean       Clean all volumes (DESTRUCTIVE)"
    echo "  usage       Show volume usage statistics"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 create"
    echo "  $0 backup"
    echo "  $0 restore backup_20240101_120000"
    echo "  $0 list"
}

# Main script logic
case "${1:-help}" in
    create)
        create_local_directories
        create_docker_volumes
        print_status "Volume setup completed successfully"
        ;;
    list)
        list_volumes
        ;;
    backup)
        backup_volumes
        ;;
    restore)
        restore_volumes "$2"
        ;;
    clean)
        clean_volumes
        ;;
    usage)
        show_usage
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
