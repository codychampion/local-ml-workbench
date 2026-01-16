# LoRA Training Status

## Current Situation

We successfully set up the infrastructure for Wan 2.2 / HunyuanVideo LoRA training, but hit compatibility issues:

### What Works ✅
- ✅ Docker setup with CUDA 12.8 for RTX 5090
- ✅ GPU detection working
- ✅ Dataset collection (34 Fallout NV images)
- ✅ Training script infrastructure
- ✅ Model downloading from HuggingFace

### What Doesn't Work ❌
1. **ComfyUI Safetensors**: FP8 quantized format incompatible with diffusers
   - Keys like `blocks.0.cross_attn.k.scale_input` are quantization-specific
   - Standard diffusers models don't support this format

2. **HunyuanVideo-1.5 from HuggingFace**: Config format incompatibility
   - Downloaded successfully (33GB)
   - Config has newer parameters diffusers 0.31.0 doesn't support
   - Error: `empty(): argument 'size' failed to unpack`

## Recommended Solutions

### Option 1: Use Official HunyuanVideo Training (RECOMMENDED)
Clone and use Tencent's official training code:
```bash
git clone https://github.com/Tencent-Hunyuan/HunyuanVideo-I2V
cd HunyuanVideo-I2V
# Follow their LoRA training guide
```

**Pros:**
- Official training method
- Guaranteed compatibility
- Proper FP8 support
- Documentation and examples

**Cons:**
- Different codebase than our ml_workbench
- Requires separate setup

### Option 2: Upgrade Diffusers to Latest
Update to diffusers >= 0.34.0 for HunyuanVideo-1.5 support:

Edit `pipelines/train/Dockerfile`:
```dockerfile
diffusers>=0.34.0 \
```

Then retry:
```bash
docker compose build train
docker compose --profile pipeline run --rm train \
    python pipelines/train/train_video_lora_real.py \
    --dataset data/scraped/fallout_nv_20260116_113625 \
    --concept "fallout_nv" \
    --model "tencent/HunyuanVideo-1.5" \
    --epochs 20
```

### Option 3: Try SimpleTuner
SimpleTuner has better HunyuanVideo support:
```bash
git clone https://github.com/bghira/SimpleTuner
# Configure for HunyuanVideo
```

### Option 4: Convert ComfyUI Model
Write a converter to transform FP8 quantized weights to standard format (complex).

## What We've Built

Even though training isn't working yet, we created:
- ✅ Complete training infrastructure
- ✅ Docker setup with proper CUDA support
- ✅ Data scraping pipeline
- ✅ Model loading strategies
- ✅ LoRA application code
- ✅ Flow matching training loop
- ✅ Checkpoint saving

This foundation will work once we get the model loading resolved!

## Next Steps

1. **Try Option 2** (upgrade diffusers) - Quickest fix if it works
2. **Try Option 1** (official repo) - Most reliable long-term
3. **Try Option 3** (SimpleTuner) - Proven HunyuanVideo LoRA training

## Files Created
- `pipelines/train/train_video_lora_real.py` - Real LoRA training implementation
- `scripts/scrape_and_train.sh` - End-to-end pipeline
- `models/README.md` - Model setup guide
- `WAN22_REAL_TRAINING.md` - Comprehensive training guide
- Docker setup with CUDA 12.8 support

The infrastructure is solid - we just need compatible model loading!
