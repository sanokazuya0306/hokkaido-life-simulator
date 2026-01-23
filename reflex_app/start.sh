#!/bin/bash
# Production startup script for Reflex app

set -e

echo "=== Starting Reflex App ==="
echo "PORT: ${PORT:-not set}"
echo "RAILWAY_PUBLIC_DOMAIN: ${RAILWAY_PUBLIC_DOMAIN:-not set}"
echo "PWD: $(pwd)"
echo "Contents: $(ls -la)"

# Get the public URL from environment
if [ -n "$RAILWAY_PUBLIC_DOMAIN" ]; then
    PUBLIC_URL="https://${RAILWAY_PUBLIC_DOMAIN}"
elif [ -n "$RENDER_EXTERNAL_URL" ]; then
    PUBLIC_URL="${RENDER_EXTERNAL_URL}"
else
    PUBLIC_URL="http://localhost:${PORT:-8080}"
fi

echo "Public URL: ${PUBLIC_URL}"

# Check if .web/_static exists
if [ -d ".web/_static" ]; then
    echo "Found .web/_static directory"
    # Replace localhost:8000 with actual public URL in built JS files
    find .web/_static -name "*.js" -type f -exec sed -i "s|http://localhost:8000|${PUBLIC_URL}|g" {} \; 2>/dev/null || true
    echo "URL replacement done"
else
    echo "WARNING: .web/_static not found!"
    ls -la .web/ 2>/dev/null || echo ".web directory not found"
fi

echo "Starting Caddy..."
caddy start --config Caddyfile
sleep 2

echo "Starting Reflex backend..."
exec reflex run --env prod --backend-only --loglevel info
