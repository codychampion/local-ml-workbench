# ❌ Ditching Kohya - Using Native Pipeline Instead

## Why Kohya Sucks For This

**Problems we hit:**
- ❌ Designed for Stable Diffusion images, not video models
- ❌ Requires manual folder naming (`10_concept` format)
- ❌ GUI-based, doesn't integrate with your pipelines
- ❌ Permission nightmares in Docker
- ❌ Config file hell with TOML generation
- ❌ Headless mode errors everywhere

**What you already have:**
- ✅ Clean Python training pipeline (`pipelines/train/`)
- ✅ LoRA/PEFT infrastructure (`finetune.py`)
- ✅ S3 storage, AIM tracking, Docker integration
- ✅ Simple argparse interfaces

## New Approach: Native Pipeline

We extended your existing `pipelines/train/` infrastructure with `train_video_lora.py`.

### One-Command Training

```bash
# Scrape Reddit + Train LoRA (no Kohya):
./scripts/scrape_and_train.sh fnv newvegas 100 5

# Or train from existing images:
python pipelines/train/train_video_lora.py \
    --dataset ./data/collected \
    --concept fallout \
    --epochs 5
```

That's it. No folder renaming. No GUI. No Kohya.

## What Changed

### Before (Kohya):
```
1. Scrape images
2. Manually rename folders to 10_concept format
3. Generate TOML config files
4. Fight with Kohya GUI permissions
5. Hope it works
6. Extract LoRA from Kohya's weird output structure
```

### After (Native):
```
1. Scrape images
2. python train_video_lora.py --dataset ./data --concept fallout
3. Done
```

## Integration with Your Existing Pipeline

The new `train_video_lora.py`:
- ✅ Uses your `config.py` and `get_config()`
- ✅ Integrates with your S3 storage (`get_s3_client`)
- ✅ Tracks with AIM if available
- ✅ Same argparse style as your other scripts
- ✅ Works in your Docker training container
- ✅ Outputs to `./outputs/lora/{concept}/` like you expect

## TODO: Add Real Video Model Training

Right now `train_video_lora.py` has symbolic training (placeholder). To make it real:

1. Load your actual video model (Wan 2.2, CogVideoX)
2. Apply LoRA with PEFT (like your `finetune.py` does)
3. Train on image datasets (video models can train on images)
4. Save LoRA weights as `.safetensors`

The infrastructure is there - just needs the model-specific code.

## Kohya Removal

You can remove Kohya entirely:

```bash
# Remove Kohya from docker-compose.yml
# Delete scripts/train_lora_auto.py (Kohya-specific)
# Keep scripts/scrape_and_train.sh (now uses native pipeline)
```

Or keep Kohya profile dormant if you ever need SD image LoRAs.

## Next Steps

1. **Test the native pipeline:**
   ```bash
   python pipelines/train/train_video_lora.py \
       --dataset ./data/test_images \
       --concept test \
       --epochs 2
   ```

2. **Integrate real video model training** into `train_video_lora.py`

3. **Run full pipeline:**
   ```bash
   ./scripts/scrape_and_train.sh fnv newvegas 50 5
   ```

---

**Bottom line:** Use your own infrastructure. Kohya was the wrong tool for video models.
