#!/bin/bash
# End-to-end pipeline: Scrape Reddit data and train LoRA
set -e

# Configuration
SUBREDDIT="${1:-fo4}"
CONCEPT="${2:-fallout}"
LIMIT="${3:-100}"
EPOCHS="${4:-5}"
OUTPUT_DIR="./data/scraped/${CONCEPT}_$(date +%Y%m%d_%H%M%S)"

echo "=========================================="
echo "🤖 SCRAPE + TRAIN PIPELINE"
echo "=========================================="
echo "Subreddit: r/${SUBREDDIT}"
echo "Concept: ${CONCEPT}"
echo "Limit: ${LIMIT} images"
echo "Epochs: ${EPOCHS}"
echo "=========================================="

# Step 1: Scrape images from Reddit
echo ""
echo "[1/2] 📥 Scraping images from r/${SUBREDDIT}..."
mkdir -p "${OUTPUT_DIR}"

python pipelines/collect/collect_reddit.py \
    --subreddit "${SUBREDDIT}" \
    --limit "${LIMIT}" \
    --output "${OUTPUT_DIR}" \
    || echo "⚠️  Scraping completed with warnings"

# Count images
IMAGE_COUNT=$(find "${OUTPUT_DIR}" -type f \( -name "*.jpg" -o -name "*.png" -o -name "*.jpeg" \) | wc -l)
echo "✓ Collected ${IMAGE_COUNT} images"

if [ "${IMAGE_COUNT}" -lt 10 ]; then
    echo "❌ Error: Need at least 10 images for training"
    exit 1
fi

# Step 2: Train LoRA using native pipeline
echo ""
echo "[2/2] 🚀 Training LoRA..."
python pipelines/train/train_video_lora.py \
    --dataset "${OUTPUT_DIR}" \
    --concept "${CONCEPT}" \
    --epochs "${EPOCHS}" \
    --batch-size 1 \
    --learning-rate 1e-4 \
    --lora-rank 8

echo ""
echo "=========================================="
echo "✅ Pipeline Complete!"
echo "=========================================="
echo "Check outputs in: ./outputs/lora/${CONCEPT}/"
echo ""
