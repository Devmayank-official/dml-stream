# =============================================================================
# DML Stream - Dockerfile
# =============================================================================
# Enterprise-Level Terminal-Based Video Download Solution
# Developed by DML Labs
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: Build Stage
# -----------------------------------------------------------------------------
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY pyproject.toml .
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -e .[dev]

# -----------------------------------------------------------------------------
# Stage 2: Production Stage
# -----------------------------------------------------------------------------
FROM python:3.11-slim as production

# Labels
LABEL maintainer="devmayank.inbox@gmail.com" \
    version="2.0.0" \
    description="Enterprise-Level Terminal-Based Video Download Solution by DML Labs" \
    repository="https://github.com/devmayank-official/dml-stream" \
    author="DML Labs"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DEBIAN_FRONTEND=noninteractive

# Install runtime dependencies including FFmpeg
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN groupadd --gid 1000 dmlgroup && \
    useradd --uid 1000 --gid dmlgroup --shell /bin/bash --create-home dmluser

# Set working directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY --chown=dmluser:dmlgroup src/ ./src/
COPY --chown=dmluser:dmlgroup pyproject.toml .
COPY --chown=dmluser:dmlgroup README.md .
COPY --chown=dmluser:dmlgroup LICENSE .

# Create necessary directories
RUN mkdir -p /app/downloads/videos \
    /app/downloads/audio \
    /app/downloads/playlists \
    /app/logs \
    /app/config \
    && chown -R dmluser:dmlgroup /app

# Switch to non-root user
USER dmluser

# Set environment variables for application
ENV DML_STREAM_DEFAULT_OUTPUT_FOLDER=/app/downloads \
    DML_STREAM_LOG_FILE_PATH=/app/logs/app.log.json \
    DML_STREAM_CONFIG_FILE_PATH=/app/config/config.json \
    DML_STREAM_HISTORY_FILE_PATH=/app/config/download_history.json \
    DML_STREAM_SCHEDULED_DOWNLOADS_FILE_PATH=/app/config/scheduled_downloads.json \
    DML_STREAM_BATCH_DOWNLOADS_FILE_PATH=/app/config/batch_downloads.json

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import dml_stream; print('OK')" || exit 1

# Default command - run interactive mode
ENTRYPOINT ["dml-stream"]
CMD ["interactive"]

# -----------------------------------------------------------------------------
# Stage 3: Development Stage
# -----------------------------------------------------------------------------
FROM production as development

# Install development dependencies
RUN pip install -e .[dev,docs]

# Switch back to root for development
USER root

# Install additional development tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    vim \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Switch back to dmluser
USER dmluser

# Default command for development
CMD ["bash"]
