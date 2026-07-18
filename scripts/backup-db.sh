#!/usr/bin/env bash
#
# PostgreSQL Database Backup Script
#
# Usage: ./scripts/backup-db.sh [output_dir]
#
# Environment variables required:
#   POSTGRES_USER     - Database user
#   POSTGRES_PASSWORD - Database password
#   POSTGRES_DB       - Database name
#   POSTGRES_SERVER   - Database host (default: db)
#   POSTGRES_PORT     - Database port (default: 5432)
#
# Optional environment variables:
#   BACKUP_RETENTION_DAYS - Number of days to keep backups (default: 7)
#

set -euo pipefail

# Configuration
OUTPUT_DIR="${1:-./backups}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-7}"

# Database connection (defaults for docker-compose setup)
POSTGRES_SERVER="${POSTGRES_SERVER:-db}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"

# Validate required environment variables
: "${POSTGRES_USER:?Environment variable POSTGRES_USER is required}"
: "${POSTGRES_PASSWORD:?Environment variable POSTGRES_PASSWORD is required}"
: "${POSTGRES_DB:?Environment variable POSTGRES_DB is required}"

# Create output directory if it doesn't exist
mkdir -p "${OUTPUT_DIR}"

# Backup filename
BACKUP_FILE="${OUTPUT_DIR}/${POSTGRES_DB}_${TIMESTAMP}.sql.gz"

echo "Starting backup of database '${POSTGRES_DB}'..."
echo "Output: ${BACKUP_FILE}"

# Run pg_dump with compression
export PGPASSWORD="${POSTGRES_PASSWORD}"
pg_dump \
    -h "${POSTGRES_SERVER}" \
    -p "${POSTGRES_PORT}" \
    -U "${POSTGRES_USER}" \
    -d "${POSTGRES_DB}" \
    --no-owner \
    --no-acl \
    | gzip > "${BACKUP_FILE}"

# Verify backup was created
if [[ -f "${BACKUP_FILE}" ]]; then
    BACKUP_SIZE=$(du -h "${BACKUP_FILE}" | cut -f1)
    echo "Backup completed successfully!"
    echo "File: ${BACKUP_FILE}"
    echo "Size: ${BACKUP_SIZE}"
else
    echo "ERROR: Backup file was not created"
    exit 1
fi

# Cleanup old backups
if [[ "${BACKUP_RETENTION_DAYS}" -gt 0 ]]; then
    echo "Cleaning up backups older than ${BACKUP_RETENTION_DAYS} days..."
    find "${OUTPUT_DIR}" -name "*.sql.gz" -type f -mtime +${BACKUP_RETENTION_DAYS} -delete
    echo "Cleanup completed."
fi

echo "Backup process finished."
