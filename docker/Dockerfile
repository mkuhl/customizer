# Template Customizer Docker Image
# Multi-stage build for optimal size and security

# Stage 1: Builder
FROM python:3.12-slim AS builder

# Build argument for version (extracted from source during build)
ARG VERSION

# Install uv for fast dependency management
RUN pip install uv

# Set working directory
WORKDIR /build

# Copy project files
COPY pyproject.toml ./
COPY src/ ./src/
COPY README.md ./
COPY LICENSE ./

# Build the wheel package
RUN uv pip install --system build
RUN python -m build --wheel

# Install the package and dependencies in a virtual environment
RUN uv venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN uv pip install dist/*.whl

# Stage 2: Runtime
FROM python:3.12-slim AS runtime

# Build argument for version (passed from builder stage)
ARG VERSION

# Install security updates and clean up
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN groupadd -r templateuser && \
    useradd -r -g templateuser -d /home/templateuser -s /bin/bash templateuser && \
    mkdir -p /home/templateuser && \
    chown -R templateuser:templateuser /home/templateuser

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Set environment variables
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Create working directory for templates
RUN mkdir -p /workdir && \
    chown -R templateuser:templateuser /workdir

# Switch to non-root user
USER templateuser
WORKDIR /workdir

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD template-customizer --version || exit 1

# Entrypoint that calls template-customizer with --project /workdir
ENTRYPOINT ["template-customizer", "--project", "/workdir"]

# Default command runs process with help
CMD ["process", "--help"]

# Labels for metadata (using dynamic version)
LABEL org.opencontainers.image.title="Template Customizer"
LABEL org.opencontainers.image.description="A tool for customizing project templates using comment-based markers"
LABEL org.opencontainers.image.version="${VERSION:-unknown}"
LABEL org.opencontainers.image.source="https://github.com/example/template-customizer"
LABEL org.opencontainers.image.licenses="MIT"