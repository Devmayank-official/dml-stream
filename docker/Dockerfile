# =============================================================================
# DML Stream - Dockerfile (v2.5)
# =============================================================================
# Enterprise-Level Terminal-Based Video Download Solution
# Developed by DML Labs | Lead Engineer: @devmayank-official
# 
# Multi-stage build for production-ready, secure container
# Supports: linux/amd64, linux/arm64 (Apple Silicon, Raspberry Pi)
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: Base Image with Common Setup
# -----------------------------------------------------------------------------
FROM python:3.11-slim-bookworm as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random

# Labels
LABEL maintainer="devmayank.inbox@gmail.com" \
    org.opencontainers.image.title="DML Stream" \
    org.opencontainers.image.description="Enterprise-Level Terminal-Based Video Download Solution" \
    org.opencontainers.image.vendor="DML Labs" \
    org.opencontainers.image.authors="DML Labs <devmayank.inbox@gmail.com>" \
    org.opencontainers.image.licenses="Apache-2.0" \
    org.opencontainers.image.source="https://github.com/devmayank-official/dml-stream"

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# -----------------------------------------------------------------------------
# Stage 2: Builder Stage
# -----------------------------------------------------------------------------
FROM base as builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip and install build tools
RUN pip install --upgrade pip setuptools wheel

# Copy and install application
COPY pyproject.toml README.md LICENSE ./
COPY src/ ./src/

RUN pip install --no-cache-dir . && \
    python -m compileall /opt/venv/lib/python*/site-packages/dml_stream

# -----------------------------------------------------------------------------
# Stage 3: Production Stage
# -----------------------------------------------------------------------------
FROM base as production

# Set version from build arg
ARG VERSION=2.5.0
ENV DML_STREAM_VERSION=${VERSION}

# Create non-root user and group for security
RUN groupadd --gid 1000 dmlgroup && \
    useradd --uid 1000 --gid dmlgroup --shell /bin/bash --create-home dmluser

# Set working directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application
COPY --chown=dmluser:dmlgroup pyproject.toml README.md LICENSE ./
COPY --chown=dmluser:dmlgroup src/ ./src/

# Create directory structure with proper permissions
RUN mkdir -p /app/downloads/videos \
    /app/downloads/audio \
    /app/downloads/playlists \
    /app/logs \
    /app/config \
    /app/cache \
    && chown -R dmluser:dmlgroup /app \
    && chmod -R 755 /app

# Switch to non-root user
USER dmluser

# Set environment variables
ENV DML_STREAM_DEFAULT_OUTPUT_FOLDER=/app/downloads \
    DML_STREAM_LOG_FILE_PATH=/app/logs/app.log.json \
    DML_STREAM_CONFIG_FILE_PATH=/app/config/config.json \
    DML_STREAM_HISTORY_FILE_PATH=/app/config/download_history.json \
    DML_STREAM_SCHEDULED_DOWNLOADS_FILE_PATH=/app/config/scheduled_downloads.json \
    DML_STREAM_BATCH_DOWNLOADS_FILE_PATH=/app/config/batch_downloads.json \
    DML_STREAM_LOG_LEVEL=INFO \
    DML_STREAM_DEFAULT_THREADS=4 \
    HOME=/home/dmluser

# Expose volumes for persistence
VOLUME ["/app/downloads", "/app/logs", "/app/config", "/app/cache"]

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "from dml_stream import __version__; print(f'OK v{__version__}')" || exit 1

# Default command
ENTRYPOINT ["dml-stream"]
CMD ["--help"]

# -----------------------------------------------------------------------------
# Stage 4: Development Stage
# -----------------------------------------------------------------------------
FROM production as development

# Switch to root to install dev dependencies
USER root

# Install development dependencies
RUN pip install --no-cache-dir ".[dev,docs]"

# Install development tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    vim \
    nano \
    htop \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Configure git for development
RUN git config --global --add safe.directory /app

# Switch back to dmluser
USER dmluser

# Set development environment
ENV DML_STREAM_LOG_LEVEL=DEBUG \
    PYTHONBREAKPOINT=pdb.set_trace

WORKDIR /app

CMD ["bash"]

# -----------------------------------------------------------------------------
# Stage 5: Minimal Stage (for size-sensitive deployments)
# -----------------------------------------------------------------------------
FROM python:3.11-alpine as minimal

# Minimal labels
LABEL maintainer="devmayank.inbox@gmail.com" \
    org.opencontainers.image.title="DML Stream Minimal" \
    org.opencontainers.image.description="Minimal DML Stream container"

# Install FFmpeg (Alpine)
RUN apk add --no-cache ffmpeg

# Create user
RUN addgroup -g 1000 dmlgroup && \
    adduser -u 1000 -G dmlgroup -s /bin/sh -D dmluser

WORKDIR /app

# Install directly without venv for minimal size
COPY pyproject.toml README.md LICENSE ./
COPY src/ ./src/

RUN pip install --no-cache-dir . && \
    python -m compileall /usr/local/lib/python3.11/site-packages/dml_stream

# Setup directories
RUN mkdir -p /app/downloads /app/logs /app/config /app/cache && \
    chown -R dmluser:dmlgroup /app

USER dmluser

ENV DML_STREAM_DEFAULT_OUTPUT_FOLDER=/app/downloads \
    DML_STREAM_LOG_FILE_PATH=/app/logs/app.log.json \
    HOME=/home/dmluser

VOLUME ["/app/downloads", "/app/logs", "/app/config"]

ENTRYPOINT ["dml-stream"]
CMD ["--help"]
