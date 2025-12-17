# =============================================================================
# ComfyUI Service Container - Real Implementation
# =============================================================================
# Full ComfyUI installation with MinIO S3 integration for model storage
FROM python:3.11-slim

LABEL maintainer="MLOps Team"
LABEL service="comfyui"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /workspace

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl libgl1 libglib2.0-0 libsm6 libxext6 libxrender-dev tini \
    && rm -rf /var/lib/apt/lists/*

# Create user
RUN useradd --create-home --shell /bin/bash --uid 1000 mlops \
    && mkdir -p /workspace && chown -R mlops:mlops /workspace

# Clone ComfyUI
RUN git clone https://github.com/comfyanonymous/ComfyUI.git /workspace/ComfyUI \
    && chown -R mlops:mlops /workspace/ComfyUI

WORKDIR /workspace/ComfyUI

# Python dependencies - CPU version
RUN pip install --no-cache-dir \
    --extra-index-url https://download.pytorch.org/whl/cpu \
    torch torchvision torchaudio

# ComfyUI requirements
RUN pip install --no-cache-dir -r requirements.txt

# Additional dependencies for S3 integration
RUN pip install --no-cache-dir \
    boto3>=1.34.0 \
    s3fs>=2024.2.0 \
    aiohttp>=3.9.0

# Create directories for models and outputs
RUN mkdir -p /workspace/ComfyUI/models/{checkpoints,clip,vae,loras,controlnet,upscale_models} \
    && mkdir -p /workspace/ComfyUI/output \
    && mkdir -p /workspace/ComfyUI/input \
    && mkdir -p /workspace/ComfyUI/custom_nodes \
    && chown -R mlops:mlops /workspace/ComfyUI

# Copy S3 sync helper script
COPY --chown=mlops:mlops services/comfyui/s3_sync.py /workspace/ComfyUI/
COPY --chown=mlops:mlops services/comfyui/startup.sh /workspace/ComfyUI/

RUN chmod +x /workspace/ComfyUI/startup.sh

USER mlops
WORKDIR /workspace/ComfyUI

ENV COMFYUI_PORT=8188
ENV COMFYUI_HOST=0.0.0.0

EXPOSE 8188

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8188/ || exit 1

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["/workspace/ComfyUI/startup.sh"]
