FROM nvidia/cuda:12.6.3-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies including build tools for PyTorch
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3.10-dev \
    python3-pip \
    git \
    wget \
    cmake \
    ninja-build \
    ccache \
    libopenblas-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory for PyTorch build
WORKDIR /tmp/pytorch-build

# Build PyTorch from source with sm_120 (RTX 5090) support
# This takes ~1-2 hours but is necessary for RTX 50-series GPUs
RUN git clone --recursive --branch main https://github.com/pytorch/pytorch && \
    cd pytorch && \
    pip3 install --no-cache-dir -r requirements.txt && \
    pip3 install --no-cache-dir mkl mkl-include && \
    # Set build flags for sm_120 support with reduced memory usage
    export USE_CUDA=1 && \
    export USE_CUDNN=1 && \
    export TORCH_CUDA_ARCH_LIST="8.6;9.0;12.0" && \
    export MAX_JOBS=1 && \
    export BUILD_CAFFE2=0 && \
    export USE_DISTRIBUTED=0 && \
    export USE_NCCL=0 && \
    export BUILD_TEST=0 && \
    # Build and install PyTorch
    python3 setup.py develop

# Install torchvision and torchaudio from source
RUN cd /tmp/pytorch-build && \
    git clone https://github.com/pytorch/vision torchvision && \
    cd torchvision && \
    python3 setup.py develop && \
    cd /tmp/pytorch-build && \
    git clone https://github.com/pytorch/audio torchaudio && \
    cd torchaudio && \
    python3 setup.py develop

# Clean up build artifacts to reduce image size
RUN rm -rf /tmp/pytorch-build && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set working directory for ComfyUI
WORKDIR /app

# Clone ComfyUI
RUN git clone https://github.com/comfyanonymous/ComfyUI.git . && \
    git checkout master

# Install ComfyUI dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Install ComfyUI-Manager for easy model downloading and custom node management
RUN cd custom_nodes && \
    git clone https://github.com/ltdrdata/ComfyUI-Manager.git && \
    cd ComfyUI-Manager && \
    pip3 install --no-cache-dir -r requirements.txt

# Create directories for models, outputs, and inputs
RUN mkdir -p models/checkpoints models/vae models/loras \
    output input/custom user

# Expose ComfyUI port
EXPOSE 8188

# Run as non-root user
RUN useradd -m -u 1000 comfyui && \
    chown -R comfyui:comfyui /app

USER comfyui

CMD ["python3", "main.py", "--listen", "0.0.0.0", "--port", "8188"]
