#!/bin/bash

# Quick Database Dump Script
# Simple script for creating and restoring database dumps

set -e

# Get database connection details from Django settings
get_db_config() {
    local db_alias=$1
    python3 -c "
import os
import sys
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oar.settings')
django.setup()

db_config = settings.DATABASES['$db_alias']
print(f\"{db_config['HOST']}:{db_config['PORT']}:{db_config['NAME']}:{db_config['USER']}:{db_config['PASSWORD']}\")
"
}

# Create dump
if [ "$1" = "dump" ]; then
    source_db=${2:-"default"}
    dump_name=${3:-"backup"}
    
    echo "Creating dump from $source_db database..."
    
    # Get connection details
    db_info=$(get_db_config $source_db)
    host=$(echo $db_info | cut -d: -f1)
    port=$(echo $db_info | cut -d: -f2)
    dbname=$(echo $db_info | cut -d: -f3)
    user=$(echo $db_info | cut -d: -f4)
    password=$(echo $db_info | cut -d: -f5)
    
    # Create dump directory
    mkdir -p ./db_dumps
    
    # Set password and create dump
    export PGPASSWORD=$password
    dump_file="./db_dumps/${dump_name}_$(date +%Y%m%d_%H%M%S).dump"
    
    pg_dump -h $host -p $port -U $user -d $dbname \
        --format=custom \
        --verbose \
        --no-owner \
        --no-privileges \
        --file="$dump_file"
    
    echo "Dump created: $dump_file"
    echo "Size: $(du -h "$dump_file" | cut -f1)"

# Restore dump
elif [ "$1" = "restore" ]; then
    target_db=${2:-"rba"}
    dump_file=$3
    
    if [ -z "$dump_file" ]; then
        echo "Usage: $0 restore [target_db] [dump_file]"
        echo "Example: $0 restore rba ./db_dumps/backup_20241201_120000.dump"
        exit 1
    fi
    
    if [ ! -f "$dump_file" ]; then
        echo "Error: Dump file not found: $dump_file"
        exit 1
    fi
    
    echo "WARNING: This will DESTROY all data in the $target_db database!"
    echo "Target file: $dump_file"
    read -p "Are you sure? (yes/no): " confirm
    
    if [ "$confirm" != "yes" ]; then
        echo "Restore cancelled"
        exit 0
    fi
    
    # Get connection details
    db_info=$(get_db_config $target_db)
    host=$(echo $db_info | cut -d: -f1)
    port=$(echo $db_info | cut -d: -f2)
    dbname=$(echo $db_info | cut -d: -f3)
    user=$(echo $db_info | cut -d: -f4)
    password=$(echo $db_info | cut -d: -f5)
    
    # Set password and restore
    export PGPASSWORD=$password
    
    echo "Dropping and recreating database..."
    psql -h $host -p $port -U $user -d postgres -c "DROP DATABASE IF EXISTS $dbname;"
    psql -h $host -p $port -U $user -d postgres -c "CREATE DATABASE $dbname;"
    
    echo "Restoring dump..."
    pg_restore -h $host -p $port -U $user -d $dbname \
        --verbose \
        --no-owner \
        --no-privileges \
        --clean \
        --if-exists \
        "$dump_file"
    
    echo "Restore completed!"

# List dumps
elif [ "$1" = "list" ]; then
    echo "Available dumps:"
    if [ -d "./db_dumps" ]; then
        ls -lh ./db_dumps/*.dump 2>/dev/null || echo "No dump files found"
    else
        echo "No dump directory found"
    fi

# Show help
else
    echo "Quick Database Dump Script"
    echo ""
    echo "Usage:"
    echo "  $0 dump [source_db] [dump_name]     Create dump"
    echo "  $0 restore [target_db] [dump_file]  Restore dump"
    echo "  $0 list                             List available dumps"
    echo ""
    echo "Examples:"
    echo "  $0 dump default opensupplyhub_backup"
    echo "  $0 dump rba rba_backup"
    echo "  $0 restore rba ./db_dumps/opensupplyhub_backup_20241201_120000.dump"
    echo "  $0 list"
    echo ""
    echo "Database aliases:"
    echo "  default - opensupplyhub database"
    echo "  rba     - RBA database"
fi 