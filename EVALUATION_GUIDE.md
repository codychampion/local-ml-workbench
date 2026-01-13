# LoRA Evaluation Guide

## Understanding "Accuracy" for Video LoRAs

Unlike classification models, video generation LoRAs don't have traditional accuracy metrics. Instead, you evaluate **quality** through:

### 1. Visual Comparison (Primary Method)

**Generate videos with and without your LoRA:**

```bash
# Setup evaluation
python scripts/evaluate_lora.py \
    --lora ./outputs/lora/fallout/fallout_epoch5.safetensors \
    --concept fallout
```

This creates a test plan. Then in ComfyUI:
1. Generate video **WITHOUT** your LoRA (baseline)
2. Generate video **WITH** your LoRA at strength 0.5
3. Generate video **WITH** your LoRA at strength 0.8
4. Generate video **WITH** your LoRA at strength 1.0

**Compare side-by-side:**
- Does the LoRA version look more "Fallout-themed"?
- Are details (power armor, pip-boy, wasteland) more accurate?
- Is the style consistent with your concept?

### 2. Prompt Adherence Test

**Test with specific prompts:**

```
Test Prompt: "A vault dweller in blue jumpsuit opening rusty vault door"
```

**Without LoRA:** Generic post-apocalyptic scene
**With LoRA (good):** Recognizable Vault-Tec aesthetic, correct color scheme, Fallout-style details
**With LoRA (bad):** Ignores prompt, always generates same scene

### 3. Strength Testing

Different strengths = different use cases:

| Strength | Effect | Use Case |
|----------|--------|----------|
| 0.3-0.5 | Subtle theme | Keep flexibility, slight style |
| 0.6-0.8 | Balanced | Strong theme, still controllable |
| 0.9-1.0 | Maximum | Pure concept, less prompt control |

**Test command:**
```bash
# In ComfyUI, adjust LoraLoaderModelOnly node strength slider
# Try 0.5, 0.8, 1.0 and compare results
```

### 4. Diversity Check

**Generate 5 videos with different prompts:**
- Do you get 5 different scenes?
- Or the same image repeated?

**Good LoRA:** Variety while maintaining theme
**Overfitted LoRA:** Always generates similar output

### 5. Quality Metrics (Optional, Advanced)

If you want quantitative metrics:

**FID Score (Fréchet Inception Distance):**
- Measures similarity between generated and real images
- Lower = better
- Requires reference dataset of "good" Fallout images

**CLIP Score:**
- Measures text-prompt alignment
- Higher = better prompt following

```python
# Example: Calculate CLIP score
from transformers import CLIPProcessor, CLIPModel
import torch

model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

# Generate video frame, then:
inputs = processor(text=["vault dweller"], images=frame, return_tensors="pt")
outputs = model(**inputs)
score = outputs.logits_per_image.item()
```

## Quick Evaluation Workflow

### Step 1: Train Your LoRA

```bash
./scripts/scrape_and_train.sh fnv newvegas 50 5
```

### Step 2: Setup Evaluation

```bash
python scripts/evaluate_lora.py \
    --lora ./outputs/lora/newvegas/newvegas_epoch5.safetensors \
    --concept newvegas
```

### Step 3: Test in ComfyUI

1. **Open your workflow** (http://localhost:8188)

2. **Find LoraLoaderModelOnly node** (#83 or #85)

3. **Test configurations:**

**A. Baseline (No LoRA):**
- Remove/bypass LoRA node
- Generate video with prompt: "NCR ranger at Hoover Dam"
- Save as `baseline_1.mp4`

**B. Your LoRA (Strength 0.5):**
- Load your LoRA: `newvegas_epoch5.safetensors`
- Set strength: 0.5
- Same prompt: "NCR ranger at Hoover Dam"
- Save as `lora_0.5_1.mp4`

**C. Your LoRA (Strength 0.8):**
- Keep your LoRA loaded
- Set strength: 0.8
- Same prompt
- Save as `lora_0.8_1.mp4`

**D. Your LoRA (Strength 1.0):**
- Set strength: 1.0
- Same prompt
- Save as `lora_1.0_1.mp4`

4. **Watch all 4 videos side-by-side**

### Step 4: Evaluate Quality

**Ask yourself:**

✅ **Theme Accuracy:**
- Does it look more like New Vegas?
- Are signature elements present (Lucky 38, NCR, desert)?

✅ **Visual Quality:**
- Is detail improved or degraded?
- Are colors/lighting better?

✅ **Prompt Control:**
- Does changing the prompt still work?
- Or does it ignore prompts and always generate similar scenes?

✅ **Optimal Strength:**
- Which strength gave the best balance?
- Too weak = no effect, too strong = overfitted

### Step 5: Iterate if Needed

**If LoRA is too weak:**
```bash
# Retrain with more epochs
./scripts/scrape_and_train.sh fnv newvegas 50 10
```

**If LoRA is too strong (overfitted):**
```bash
# Retrain with fewer epochs
./scripts/scrape_and_train.sh fnv newvegas 50 3

# Or use lower strength in ComfyUI (0.5-0.6)
```

**If quality is poor:**
```bash
# Get more/better training images
# Increase dataset from 50 to 100+
./scripts/scrape_and_train.sh fnv newvegas 100 5
```

## Real Example

**Prompt:** "Power-armored soldier in wasteland"

**Baseline (no LoRA):**
- Generic robot/armor
- Bland color palette
- Generic wasteland

**With Fallout LoRA (0.8 strength):**
- Recognizable T-51 power armor design
- Fallout color scheme (browns, greens)
- Specific wasteland aesthetic (retro-futuristic)
- Maybe even Vault-Tec logo visible

**Expected improvement:** 30-50% more "Fallout-like"

## When LoRA Is Working Well

You'll know your LoRA is good when:
- ✅ Friends say "That looks like Fallout!"
- ✅ Theme is consistent across different prompts
- ✅ Still responds to prompt variations
- ✅ Quality matches or exceeds baseline
- ✅ Strength 0.7-0.8 gives best results

## When to Retrain

Retrain if:
- ❌ No visible difference from baseline (undertrained)
- ❌ Always generates same image (overfitted)
- ❌ Quality degraded vs baseline
- ❌ Ignores prompts completely
- ❌ Artifacts or distortions

---

**Remember:** Video generation is subjective. Trust your eyes more than metrics!
