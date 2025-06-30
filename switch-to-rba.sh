#!/bin/bash

# Script to switch between OS Hub and RBA databases for testing
# Usage: ./switch-to-rba.sh [os_hub|rba]

set -e

MODE=${1:-rba}

if [[ "$MODE" != "rba" && "$MODE" != "os_hub" ]]; then
    echo "Usage: $0 [os_hub|rba]"
    echo "  os_hub - Use the default OS Hub database"
    echo "  rba    - Use the RBA database (default)"
    exit 1
fi

echo "Switching to $MODE database..."

if [[ "$MODE" == "rba" ]]; then
    echo "Starting RBA database..."
    docker-compose --profile rba up -d rba_db
    
    echo "Waiting for RBA database to be ready..."
    docker-compose --profile rba exec -T rba_db pg_isready -U opensupplyhub || {
        echo "Waiting for database to be ready..."
        sleep 5
    }
    
    echo "Setting environment variables for RBA..."
    export POSTGRES_HOST=rba_db
    export POSTGRES_DB=rba
    export INSTANCE_SOURCE=rba
    
    echo "✅ Switched to RBA database"
    echo "   Database: rba_db:5432/rba"
    echo "   Instance Source: rba"
    echo ""
    echo "To start services with RBA:"
    echo "  POSTGRES_HOST=rba_db POSTGRES_DB=rba INSTANCE_SOURCE=rba docker-compose --profile rba up -d"
    echo ""
    echo "To sync data from OS Hub to RBA:"
    echo "  docker-compose exec django python manage.py sync_oshub_rba --dry-run"
    echo "  docker-compose exec django python manage.py sync_oshub_rba"
    
else
    echo "Setting environment variables for OS Hub..."
    export POSTGRES_HOST=database
    export POSTGRES_DB=opensupplyhub
    export INSTANCE_SOURCE=os_hub
    
    echo "✅ Switched to OS Hub database"
    echo "   Database: database:5432/opensupplyhub"
    echo "   Instance Source: os_hub"
    echo ""
    echo "To start services with OS Hub:"
    echo "  docker-compose up -d"
fi

echo ""
echo "Current environment variables:"
echo "  POSTGRES_HOST=$POSTGRES_HOST"
echo "  POSTGRES_DB=$POSTGRES_DB"
echo "  INSTANCE_SOURCE=$INSTANCE_SOURCE" 