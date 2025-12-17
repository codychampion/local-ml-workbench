#!/bin/bash
# ComfyUI Startup Script with S3 Model Sync
# ==========================================

set -e

echo "=============================================="
echo "ComfyUI Starting..."
echo "=============================================="
echo "S3 Endpoint: $AWS_S3_ENDPOINT_URL"
echo "Models Bucket: $S3_MODELS_BUCKET"
echo "Outputs Bucket: $S3_OUTPUTS_BUCKET"
echo "=============================================="

# Sync models from S3 (non-blocking, continue if fails)
echo "[Startup] Syncing models from S3..."
python /workspace/ComfyUI/s3_sync.py download-models || echo "[Warning] Model sync failed, continuing..."

# List available models
echo ""
echo "[Startup] Available models:"
ls -la /workspace/ComfyUI/models/checkpoints/ 2>/dev/null || echo "  No checkpoints"
ls -la /workspace/ComfyUI/models/loras/ 2>/dev/null || echo "  No LoRAs"

echo ""
echo "=============================================="
echo "Starting ComfyUI server..."
echo "Web UI: http://0.0.0.0:${COMFYUI_PORT:-8188}"
echo "=============================================="

# Start ComfyUI
exec python main.py \
    --listen ${COMFYUI_HOST:-0.0.0.0} \
    --port ${COMFYUI_PORT:-8188} \
    --cpu \
    --dont-print-server
