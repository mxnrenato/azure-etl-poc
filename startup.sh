#!/bin/bash
cd /home/site/wwwroot
echo "Installing dependencies..."
pip install -r requirements.txt

echo "Starting Uvicorn..."
export PORT=${PORT:-8000}
uvicorn src.infrastructure.api.main:app \
    --host 0.0.0.0 \
    --port $PORT \
    --timeout-keep-alive 600 \
    --log-level debug \
    --access-log \
    --log-config None \
    --reload
