FROM nvidia/cuda:12.8.0-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3.10-venv \
    python3-pip \
    python3-tk \
    git \
    wget \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Clone Kohya_ss with submodules
RUN git clone --recursive https://github.com/bmaltais/kohya_ss.git . && \
    git checkout master && \
    git submodule update --init --recursive

# Install PyTorch nightly with CUDA 12.8 for RTX 5090 support
# Use torch nightly for RTX 5090 sm_120 support, but stable torchvision to avoid version conflicts
RUN pip3 install --no-cache-dir --pre \
    torch --index-url https://download.pytorch.org/whl/nightly/cu128 && \
    pip3 install --no-cache-dir torchvision --index-url https://download.pytorch.org/whl/cu121

# Install core Kohya_ss dependencies manually (avoid file:/// reference issue)
RUN pip3 install --no-cache-dir \
    gradio \
    transformers \
    diffusers \
    accelerate \
    datasets \
    opencv-python \
    einops \
    pytorch-lightning \
    bitsandbytes \
    altair \
    easygui \
    toml \
    voluptuous \
    huggingface-hub \
    safetensors \
    tk \
    pillow \
    dadaptation

# Install additional training optimizers
RUN pip3 install --no-cache-dir \
    xformers \
    wandb \
    tensorboard \
    lycoris-lora \
    prodigyopt

# Create directories
RUN mkdir -p /app/datasets /app/models /app/output /app/logs

# Run as non-root user
RUN useradd -m -u 1000 kohya && \
    chown -R kohya:kohya /app

USER kohya

# Expose web UI port
EXPOSE 7860

# Start Kohya GUI
CMD ["python3", "kohya_gui.py", "--listen", "0.0.0.0", "--server_port", "7860", "--headless"]
