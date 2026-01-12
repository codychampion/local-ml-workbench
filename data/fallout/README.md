# Kohya Training Data - Fallout LoRA

## Automated Setup ✓

Run this script anytime to auto-fix folder names:
```bash
./scripts/setup_kohya_folders.sh
```

The script automatically:
- Renames folders to Kohya format (e.g., `fnv` → `10_newvegas`)
- Creates missing folders
- Counts images in each folder

## Folder Structure

Add your images to these folders:

- `10_fallout/` - General Fallout images
- `10_newvegas/` - Fallout New Vegas images
- `10_fallout4/` - Fallout 4 images
- `10_fallout76/` - Fallout 76 images

The number `10` means each image will be used 10 times per epoch (you can adjust this).

## Kohya GUI Configuration

When training, use these paths in the Kohya web interface:

- **Image folder**: `/app/data/fallout`
- **Model**: `/app/models/unet/wan2.2_t2v_high_noise_14B_fp8_scaled.safetensors`
- **Output**: `/app/outputs/lora/fallout`
- **Logs**: `/app/logs`

## Quick Start

1. **Add images** to the folders above (on your Windows machine at `data\fallout\10_newvegas\`, etc.)
2. **Start Kohya**: `docker compose --profile kohya up -d`
3. **Open GUI**: http://localhost:7860
4. **Configure training** with the paths above
5. **Start training** and watch for errors in logs

## Minimum Requirements

- At least 10-20 images per folder for testing
- 50-100+ images recommended for quality results
- Supported formats: JPG, PNG, WebP
- Resolution: 512x512 or larger recommended
