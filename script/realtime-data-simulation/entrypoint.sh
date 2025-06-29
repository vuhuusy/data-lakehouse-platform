#!/bin/bash
set -e

echo "==> Configuring mc..."
mc alias set myminio https://minio.minio.svc.cluster.local:443 minio minio123 --insecure

echo "==> Copying data from MinIO..."
mc cp --recursive --insecure myminio/work-zone/tmp/transactions /workdir/

echo "==> Starting replay..."
for file in $(ls /workdir/transactions_*.csv | sort); do
    echo "==> Replaying $file ($(wc -l < "$file") lines)"
    python /app/replay.py "$file"
done
