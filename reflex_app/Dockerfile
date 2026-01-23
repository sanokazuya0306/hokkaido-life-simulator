# Reflex用Dockerfile for Railway/Render/Heroku
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Install Caddy
RUN curl -fsSL https://github.com/caddyserver/caddy/releases/download/v2.8.4/caddy_2.8.4_linux_amd64.tar.gz | tar -xz -C /usr/local/bin

# Set working directory
WORKDIR /app

# Copy requirements first for caching
COPY requirements.txt .
COPY ../requirements.txt ./parent_requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r parent_requirements.txt || true

# Copy application code
COPY . .

# Initialize and export Reflex app
RUN reflex init
RUN reflex export --no-zip

# Copy Caddyfile
COPY Caddyfile /etc/caddy/Caddyfile

# Expose port
EXPOSE 8080

# Start Caddy and Reflex backend
CMD ["sh", "-c", "caddy start --config /etc/caddy/Caddyfile && reflex run --env prod --backend-only --loglevel warning"]
