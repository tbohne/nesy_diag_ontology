#!/bin/bash

# check if at least two command-line arguments are provided
if [ $# -lt 2 ]; then
  echo "Usage: $0 KG_URL DATASET_NAME"
  exit 1
fi

FUSEKI_URL="$1"
DATASET_NAME="$2"
BACKUP_DIR="knowledge_base/live_kg_backups"
BACKUP_FILE="$BACKUP_DIR/backup_$(date +\%Y_\%m_\%d-\%H_\%M_\%S).nt.gz"
KG_SNAPSHOT_FILE="$BACKUP_DIR/kg_snapshot_$(date +\%Y_\%m_\%d-\%H_\%M_\%S).txt"

# construct URL for backup request
BACKUP_URL="$FUSEKI_URL/$DATASET_NAME/data?graph=default"

# trigger backup using curl and compress the result using gzip
curl -H "Accept: application/n-triples" "$BACKUP_URL" | gzip > "$BACKUP_FILE"

# check HTTP response code to ensure the backup was successful (200 OK)
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BACKUP_URL")

echo "HTTP status: $HTTP_STATUS"

# check if file was successfully created
if [ -s "$BACKUP_FILE" ]; then
  echo "backup completed successfully"
else
  echo "backup failed"
fi

echo "creating KG snapshot.."
python nesy_diag_ontology/knowledge_snapshot.py --perspective expert >> "$KG_SNAPSHOT_FILE"
python nesy_diag_ontology/knowledge_snapshot.py --perspective diag >> "$KG_SNAPSHOT_FILE"
