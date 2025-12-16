# =============================================================================
# Data Collector Container
# =============================================================================
# Collects images/videos from Reddit and other sources for building datasets.
# For captioning, use the separate captioner container.
#
# Usage:
#   docker-compose run --rm data-collector python collect.py --subreddit earthporn --limit 100
#   docker-compose run --rm data-collector dvc repro collect-data
# =============================================================================
FROM python:3.13-slim

LABEL maintainer="MLOps Team"
LABEL project="data-collector"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /workspace

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Create user
RUN useradd --create-home --shell /bin/bash --uid 1000 mlops \
    && mkdir -p /workspace && chown -R mlops:mlops /workspace

# Python dependencies - lightweight, no ML frameworks
RUN pip install --no-cache-dir \
    # Data collection
    gallery-dl \
    yt-dlp \
    # Data versioning
    "dvc[all]>=3.0.0" \
    # Utilities
    Pillow requests tqdm \
    python-dotenv pyyaml

# Create directories
RUN mkdir -p /workspace/data/{collected,raw,processed} /workspace/outputs \
    && chown -R mlops:mlops /workspace

# Copy project files
COPY --chown=mlops:mlops config.py /workspace/
COPY --chown=mlops:mlops data_transfer/ /workspace/data_transfer/
COPY --chown=mlops:mlops projects/data-collector/ /workspace/projects/data-collector/

USER mlops

ENV GALLERY_DL_CONFIG=/workspace/projects/data-collector/gallery-dl.conf

CMD ["python", "projects/data-collector/collect.py", "--help"]
