# 🤖 Automated LoRA Training Pipeline

Stop fighting with folder names and GUI configuration. Just run one command.

## Quick Start

### Option 1: Scrape + Train in One Command

```bash
# Scrape 100 images from r/fo4 and train a LoRA called "fallout"
./scripts/scrape_and_train.sh fo4 fallout 100

# Or customize:
./scripts/scrape_and_train.sh <subreddit> <concept_name> <num_images>
```

### Option 2: Train from Existing Data

```bash
# If you already have images in a folder:
python scripts/train_lora_auto.py \
    --source ./data/fallout/fnv \
    --concept newvegas \
    --epochs 10
```

## What It Does Automatically

1. ✅ Scrapes images from Reddit (or uses your existing images)
2. ✅ Organizes into Kohya's required `{repeats}_{concept}` format
3. ✅ Generates the TOML configuration file
4. ✅ Runs training via Kohya CLI
5. ✅ Saves LoRA to `./outputs/lora/{concept}/`

**No manual folder renaming. No GUI clicking. Just automation.**

## Full Options

```bash
python scripts/train_lora_auto.py \
    --source ./data/raw/images \          # Where your images are
    --concept fallout \                    # Concept name
    --model /app/models/your_model.safetensors \  # Base model
    --output my_lora \                     # Output LoRA name
    --repeats 10 \                         # Images per epoch
    --epochs 10 \                          # Training epochs
    --lr 1e-4 \                            # Learning rate
    --batch-size 1                         # Batch size
```

## Integration with Existing Pipelines

Add to your `collect_reddit.py` workflow:

```bash
# Collect Fallout images
python pipelines/collect/collect_reddit.py \
    --subreddit Fallout \
    --output ./data/scraped/fallout

# Train LoRA automatically
python scripts/train_lora_auto.py \
    --source ./data/scraped/fallout \
    --concept fallout \
    --epochs 5
```

## Check Training Progress

```bash
# Watch logs
docker compose logs kohya -f

# Check outputs
ls -la ./outputs/lora/
```

## Use Your Trained LoRA in ComfyUI

Once training completes, the LoRA will be in `./outputs/lora/{concept}/`

Since `./outputs` is shared with ComfyUI, you can immediately use it in your video generation workflows.

## Why This Is Better

| Manual Approach | Automated Pipeline |
|----------------|-------------------|
| Rename folders manually | ✅ Automatic organization |
| Click through GUI | ✅ CLI automation |
| Write TOML by hand | ✅ Generated config |
| Copy files around | ✅ Smart file handling |
| Hard to integrate | ✅ Pipeline-ready |

---

**That's it. One command. No hassle.**
