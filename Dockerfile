# HAiOS Dockerfile
# Multi-stage build for optimized production image

# Build stage
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create and activate virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install Python dependencies
COPY requirements.txt pyproject.toml ./
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install build

# Copy source code
COPY src/ ./src/
COPY docs/ ./docs/
COPY README.md ./

# Build the package
RUN python -m build

# Production stage
FROM python:3.11-slim as production

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    HAIOS_MODE=production \
    HAIOS_LOG_LEVEL=INFO

# Install runtime system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -r haios \
    && useradd -r -g haios -d /app -s /bin/bash haios

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Copy built package and install
COPY --from=builder dist/*.whl /tmp/
RUN pip install /tmp/*.whl && rm /tmp/*.whl

# Create application directory and set ownership
WORKDIR /app
RUN chown -R haios:haios /app

# Copy application files
COPY --chown=haios:haios src/ ./src/
COPY --chown=haios:haios docs/ ./docs/
COPY --chown=haios:haios .haios_config.json ./

# Create necessary directories
RUN mkdir -p /app/os_root /app/core_scaffold /app/logs && \
    chown -R haios:haios /app/os_root /app/core_scaffold /app/logs

# Switch to non-root user
USER haios

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import src; print('HAiOS is healthy')" || exit 1

# Expose port (if needed for future web interface)
EXPOSE 8080

# Default command
CMD ["python", "-m", "src", "--help"]

# Labels for metadata
LABEL org.opencontainers.image.title="HAiOS" \
      org.opencontainers.image.description="Hybrid AI Operating System - An orchestration layer for AI-assisted project execution" \
      org.opencontainers.image.vendor="HAiOS Team" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.source="https://github.com/haios-team/haios" \
      org.opencontainers.image.documentation="https://haios-team.github.io/haios" 