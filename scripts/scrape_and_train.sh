#!/bin/bash
# End-to-end pipeline: Scrape Reddit data and train LoRA
set -e

# Configuration
SUBREDDIT="${1:-fo4}"
CONCEPT="${2:-fallout}"
LIMIT="${3:-100}"
OUTPUT_DIR="./data/scraped/${CONCEPT}_$(date +%Y%m%d_%H%M%S)"

echo "=========================================="
echo "🤖 SCRAPE + TRAIN PIPELINE"
echo "=========================================="
echo "Subreddit: r/${SUBREDDIT}"
echo "Concept: ${CONCEPT}"
echo "Limit: ${LIMIT} images"
echo "=========================================="

# Step 1: Scrape images from Reddit
echo ""
echo "[1/3] 📥 Scraping images from r/${SUBREDDIT}..."
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

# Step 2: Organize and generate config
echo ""
echo "[2/3] 📁 Organizing training data..."
python scripts/train_lora_auto.py \
    --source "${OUTPUT_DIR}" \
    --concept "${CONCEPT}" \
    --repeats 10 \
    --epochs 5 \
    --lr 1e-4

echo ""
echo "=========================================="
echo "✅ Pipeline Complete!"
echo "=========================================="
echo "Check outputs in: ./outputs/lora/${CONCEPT}/"
echo ""
