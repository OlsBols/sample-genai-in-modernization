# Multi-stage Dockerfile for Business Case Generator
# Stage 1: Build React frontend
# Stage 2: Build Python backend with frontend

# ============================================================================
# Stage 1: Build Frontend
# ============================================================================
FROM node:20-alpine3.21 AS frontend-build

WORKDIR /app/ui

# Copy package files
COPY ui/package*.json ./

# Install dependencies (including optional dependencies for rollup)
RUN npm ci

# Copy frontend source
COPY ui/ ./

# Build frontend for production
RUN npm run build

# ============================================================================
# Stage 2: Build Backend with Frontend
# ============================================================================
FROM python:3.11-slim-bookworm

WORKDIR /app

# Install system dependencies and update all packages to patch CVEs
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && apt-get upgrade -y \
    && apt-get dist-upgrade -y \
    && rm -rf /var/lib/apt/lists/*

# Copy Python requirements
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY agents/ ./agents/
COPY prompt_library/ ./prompt_library/
COPY utils/ ./utils/
COPY ui/backend/ ./ui/backend/

# Copy frontend build from stage 1
COPY --from=frontend-build /app/ui/build ./ui/dist

# Create necessary directories
RUN mkdir -p /tmp/input /tmp/output

# Set environment variables
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/api/health', timeout=5)"

# Run with Gunicorn
CMD ["gunicorn", \
     "--bind", "0.0.0.0:8080", \
     "--workers", "2", \
     "--threads", "4", \
     "--timeout", "300", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--chdir", "/app/ui/backend", \
     "app:app"]
