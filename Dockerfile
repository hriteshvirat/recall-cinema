# ==============================================================================
# Multi-stage Dockerfile for RECALL: Cloud Run Production Deployment
# ==============================================================================

# Stage 1: Build React Frontend
FROM node:20-slim AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 2: Python Backend & MCP Runtime
FROM python:3.11-slim AS runner
WORKDIR /app

# Install system dependencies (ffmpeg for media analysis, curl for healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt pillow

# Copy backend and agent source code
COPY backend/ ./backend/
COPY agent/ ./agent/
COPY sample_data/ ./sample_data/
COPY scripts/ ./scripts/

# Copy built frontend assets to static mount
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Create uploads directory
RUN mkdir -p /app/uploads && chmod 777 /app/uploads

# Set runtime environment
ENV PORT=8080
ENV PYTHONPATH=/app
EXPOSE 8080

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Start production uvicorn server
CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT}"]
