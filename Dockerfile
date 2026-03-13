# ── Stage 1: Build React dashboard ───────────────────────────────────────────
FROM node:22-alpine AS dashboard-builder
WORKDIR /app/dashboard
COPY dashboard/package*.json ./
RUN npm ci
COPY dashboard/ ./
RUN npm run build

# ── Stage 2: Python backend ───────────────────────────────────────────────────
FROM python:3.12-slim AS backend

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY src/ ./src/
COPY memory/ ./memory/

# Copy built dashboard from stage 1
COPY --from=dashboard-builder /app/dashboard/dist ./dashboard/dist

# Create data directory
RUN mkdir -p data credentials

# Run as non-root
RUN useradd -m -u 1001 coach && chown -R coach:coach /app
USER coach

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
