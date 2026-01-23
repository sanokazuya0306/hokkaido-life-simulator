# Reflex用Dockerfile for Render/Railway
FROM python:3.11-slim

# Install Node.js (required for Reflex frontend)
RUN apt-get update && apt-get install -y \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Initialize Reflex
RUN reflex init

# Default port (Render uses 10000, can be overridden by PORT env)
ENV PORT=10000
EXPOSE 10000

# Start Reflex
CMD reflex run --env prod --backend-host 0.0.0.0 --backend-port $PORT
