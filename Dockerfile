# MLOps Workspace Dockerfile
# ==========================
# Phase 1: CPU-optimized development environment
# NO CUDA/GPU dependencies - designed for local reproducible builds
#
# PHASE 2/3 TODO: Create separate Dockerfile.gpu with CUDA support:
# FROM nvidia/cuda:12.1-cudnn8-runtime-ubuntu22.04
# Or use SkyPilot's managed images for cloud GPU instances

FROM python:3.11-slim

LABEL maintainer="MLOps Team"
LABEL description="CPU-optimized MLOps development environment"
LABEL phase="1-local-core"

# Prevent Python from writing pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /workspace

# Install system dependencies
# - git: version control
# - curl: for health checks and downloads
# - libgl1: required by some image processing libraries
# - libglib2.0-0: required by OpenCV/FiftyOne
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash mlops
RUN mkdir -p /workspace && chown -R mlops:mlops /workspace

# Copy requirements first for layer caching
COPY --chown=mlops:mlops requirements.txt .

# Install Python dependencies
# Note: Using --extra-index-url for CPU-only PyTorch
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=mlops:mlops . .

# Create necessary directories
RUN mkdir -p /workspace/data/raw \
    /workspace/data/processed \
    /workspace/data/fiftyone \
    /workspace/outputs/wandb \
    /workspace/outputs/models \
    /workspace/outputs/logs \
    && chown -R mlops:mlops /workspace

# Switch to non-root user
USER mlops

# Set environment variables for Phase 1
ENV MLOPS_ENV=development
ENV WANDB_MODE=offline
ENV COMPUTE_DEVICE=cpu
ENV FIFTYONE_DATABASE_DIR=/workspace/data/fiftyone

# PHASE 2/3 TODO: Add GPU environment variables
# ENV CUDA_VISIBLE_DEVICES=0
# ENV TORCH_CUDA_ARCH_LIST="7.0 7.5 8.0 8.6 9.0"

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import torch; import wandb; import fiftyone; print('OK')" || exit 1

# Default command - start an interactive shell
CMD ["/bin/bash"]

# PHASE 2/3 TODO: Alternative entrypoints for production
# ENTRYPOINT ["python", "-m", "prefect.cli"]
# CMD ["server", "start"]
