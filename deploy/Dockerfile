# Multi-stage production container for Google Antigravity Headless Agent & Integrations
FROM node:20-slim AS base

# Install system dependencies for headless browser subagents (Chromium, xvfb, fonts)
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    curl \
    git \
    ca-certificates \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    xvfb \
    dumb-init \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV NODE_ENV=production \
    PYTHONUNBUFFERED=1 \
    ANTIGRAVITY_DATA_DIR=/var/data/antigravity \
    PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true \
    CHROME_PATH=/usr/bin/chromium

# Create non-root system user for strict sandboxing
RUN groupadd -g 1001 antigravity && \
    useradd -u 1001 -g antigravity -m -s /bin/bash antigravity && \
    mkdir -p /var/data/antigravity/brain /app && \
    chown -R antigravity:antigravity /var/data/antigravity /app

WORKDIR /app

# Install Python requirements
COPY --chown=antigravity:antigravity requirements.txt* ./
RUN if [ -f requirements.txt ]; then \
      python3 -m pip install --no-cache-dir --break-system-packages -r requirements.txt; \
    fi

# Copy application source & workspace definitions
COPY --chown=antigravity:antigravity . /app

# Switch to non-root user
USER antigravity

# Expose HTTP / webhook gateway port
EXPOSE 8080

# Healthcheck probe
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8080/healthz || exit 1

# dumb-init handles PID 1 signals (SIGTERM) for graceful session checkpoints
ENTRYPOINT ["/usr/bin/dumb-init", "--"]
CMD ["python3", "integrations/whatsapp_gateway.py"]
