# Reflex用Dockerfile for Railway/Render/Heroku
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Initialize Reflex (prepare .web directory)
RUN reflex init

# Expose port (Railway uses PORT env variable)
EXPOSE 8000

# Start Reflex in production mode
# API_URL will be set at runtime via environment variable
CMD ["sh", "-c", "reflex run --env prod --loglevel warning"]
