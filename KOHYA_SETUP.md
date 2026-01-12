# 🚀 Kohya Setup - Step by Step

## What I Fixed

1. ✅ **Removed user permission restriction** - Container now runs as root to write config files
2. ✅ **HuggingFace cache working** - Using `./cache` directory
3. ✅ **Created proper folder structure** - Folders with correct naming at `data/fallout/10_*`

## ⚠️ YOU NEED TO DO THIS

Your images are on Windows at: `C:\Users\cody\Documents\GitHub\ml_workbench\data\fallout\fnv`

But the training folders are **EMPTY**. You need to move your images into the correctly named folders.

### On Windows PowerShell:

```powershell
cd C:\Users\cody\Documents\GitHub\ml_workbench

# Check what images you have:
dir data\fallout\fnv\*.jpg

# Move images to the correct folders:
move data\fallout\fnv\*.* data\fallout\10_newvegas\
move data\fallout\Fallout\*.* data\fallout\10_fallout\
move data\fallout\fo4\*.* data\fallout\10_fallout4\
move data\fallout\fo76\*.* data\fallout\10_fallout76\

# Or if you prefer to COPY instead of move:
copy data\fallout\fnv\*.* data\fallout\10_newvegas\
copy data\fallout\Fallout\*.* data\fallout\10_fallout\
copy data\fallout\fo4\*.* data\fallout\10_fallout4\
copy data\fallout\fo76\*.* data\fallout\10_fallout76\
```

## Then Restart Kohya

```bash
docker compose --profile kohya down
docker compose --profile kohya up -d
```

## In Kohya GUI (http://localhost:7860)

Use these **exact** paths:

- **Image folder**: `/app/data/fallout` (DreamBooth tab)
  - Or for LoRA: `/app/data/fallout/10_newvegas` (pick one folder)
- **Model**: `/app/models/unet/wan2.2_t2v_high_noise_14B_fp8_scaled.safetensors`
- **Output**: `/app/outputs/lora/fallout`
- **Logs**: `/app/logs`

## Expected Folder Structure

After moving images, you should have:

```
data/fallout/
├── 10_fallout/          # Your general Fallout images HERE
│   ├── image1.jpg
│   ├── image2.jpg
│   └── ...
├── 10_newvegas/         # Your New Vegas images HERE
│   └── ...
├── 10_fallout4/         # Your Fallout 4 images HERE
│   └── ...
└── 10_fallout76/        # Your Fallout 76 images HERE
    └── ...
```

## Why "10_" prefix?

The `10` means each image will be repeated 10 times per epoch during training. This is Kohya's required naming format: `{repeats}_{concept_name}`

## Still Getting Errors?

Run this to check if images are in the right place:

```bash
# Count images in each folder:
./scripts/setup_kohya_folders.sh
```

If folders are empty, the training will fail with "No data found" error.
