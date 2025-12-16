# =============================================================================
# Captioner Container - Image Captioning & Annotation
# =============================================================================
# Dedicated container for image captioning with support for multiple models
# and fine-tuning capabilities.
#
# Usage:
#   docker-compose run --rm captioner python caption.py --input-dir ./data/collected
#   docker-compose run --rm captioner python finetune.py --dataset ./data/annotated
# =============================================================================
FROM python:3.13-slim

LABEL maintainer="MLOps Team"
LABEL project="captioner"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /workspace

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl libgl1 libglib2.0-0 libsm6 libxext6 libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Create user
RUN useradd --create-home --shell /bin/bash --uid 1000 mlops \
    && mkdir -p /workspace && chown -R mlops:mlops /workspace

# Python dependencies for captioning
RUN pip install --no-cache-dir \
    --extra-index-url https://download.pytorch.org/whl/cpu \
    torch torchvision \
    # Captioning models
    transformers>=4.36.0 \
    accelerate \
    # Fine-tuning
    peft>=0.7.0 \
    datasets>=2.16.0 \
    # Dataset management
    fiftyone \
    # Utilities
    Pillow numpy tqdm requests \
    python-dotenv pyyaml \
    sentencepiece

# Create directories
RUN mkdir -p /workspace/data/{collected,annotated,captions} \
    /workspace/outputs/captioner \
    /workspace/models/captioner \
    && chown -R mlops:mlops /workspace

# Copy project files
COPY --chown=mlops:mlops config.py /workspace/
COPY --chown=mlops:mlops projects/captioner/ /workspace/projects/captioner/

USER mlops

ENV HF_HOME=/workspace/.cache/huggingface
ENV TRANSFORMERS_CACHE=/workspace/.cache/huggingface/transformers

CMD ["python", "projects/captioner/caption.py", "--help"]
