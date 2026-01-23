#!/bin/bash
# Production startup script for Reflex app

set -e

# Get the public URL from environment (Railway sets RAILWAY_PUBLIC_DOMAIN)
if [ -n "$RAILWAY_PUBLIC_DOMAIN" ]; then
    PUBLIC_URL="https://${RAILWAY_PUBLIC_DOMAIN}"
elif [ -n "$RENDER_EXTERNAL_URL" ]; then
    PUBLIC_URL="${RENDER_EXTERNAL_URL}"
elif [ -n "$PUBLIC_URL" ]; then
    PUBLIC_URL="${PUBLIC_URL}"
else
    PUBLIC_URL="http://localhost:8080"
fi

echo "Public URL: ${PUBLIC_URL}"

# Replace localhost:8000 with actual public URL in built JS files
find .web/_static -name "*.js" -type f -exec sed -i "s|http://localhost:8000|${PUBLIC_URL}|g" {} \; 2>/dev/null || true

echo "Starting Caddy on port 8080..."
caddy start --config Caddyfile

echo "Starting Reflex backend on port 8000..."
exec reflex run --env prod --backend-only --loglevel warning
