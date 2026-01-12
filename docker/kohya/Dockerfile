FROM nvidia/cuda:12.8.0-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3.10-venv \
    python3-pip \
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

# Clone Kohya_ss
RUN git clone https://github.com/bmaltais/kohya_ss.git . && \
    git checkout master

# Install PyTorch nightly with CUDA 12.8 for RTX 5090 support
RUN pip3 install --no-cache-dir --pre \
    torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128

# Install Kohya_ss requirements
RUN pip3 install --no-cache-dir -r requirements.txt

# Install additional dependencies
RUN pip3 install --no-cache-dir \
    xformers \
    bitsandbytes \
    wandb \
    tensorboard

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
