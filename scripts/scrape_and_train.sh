#!/bin/bash
# End-to-end pipeline: Scrape Reddit data and train LoRA (all in Docker)
set -e

# Configuration
SUBREDDIT="${1:-fo4}"
CONCEPT="${2:-fallout}"
LIMIT="${3:-100}"
EPOCHS="${4:-5}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_DIR="data/scraped/${CONCEPT}_${TIMESTAMP}"

echo "=========================================="
echo "🤖 SCRAPE + TRAIN PIPELINE (Docker)"
echo "=========================================="
echo "Subreddit: r/${SUBREDDIT}"
echo "Concept: ${CONCEPT}"
echo "Limit: ${LIMIT} images"
echo "Epochs: ${EPOCHS}"
echo "=========================================="

# Step 1: Scrape images from Reddit (in Docker)
echo ""
echo "[1/2] 📥 Scraping images from r/${SUBREDDIT}..."
docker compose --profile pipeline run --rm collect \
    python pipelines/collect/collect_reddit.py \
    --subreddit "${SUBREDDIT}" \
    --limit "${LIMIT}" \
    --output "/workspace/${OUTPUT_DIR}"

# Count images
IMAGE_COUNT=$(find "${OUTPUT_DIR}" -type f \( -name "*.jpg" -o -name "*.png" -o -name "*.jpeg" \) 2>/dev/null | wc -l)
echo "✓ Collected ${IMAGE_COUNT} images"

if [ "${IMAGE_COUNT}" -lt 10 ]; then
    echo "❌ Error: Need at least 10 images for training"
    echo "   Images saved to: ${OUTPUT_DIR}"
    exit 1
fi

# Step 2: Train LoRA (in Docker)
echo ""
echo "[2/2] 🚀 Training LoRA..."
docker compose --profile pipeline run --rm train \
    python pipelines/train/train_video_lora.py \
    --dataset "/workspace/${OUTPUT_DIR}" \
    --concept "${CONCEPT}" \
    --epochs "${EPOCHS}" \
    --batch-size 1 \
    --learning-rate 1e-4 \
    --lora-rank 8

echo ""
echo "=========================================="
echo "✅ Pipeline Complete!"
echo "=========================================="
echo "Scraped images: ${OUTPUT_DIR}"
echo "Trained LoRA: ./outputs/lora/${CONCEPT}/"
echo ""

