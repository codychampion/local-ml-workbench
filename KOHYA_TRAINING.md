# Kohya_ss LoRA Training Guide

Kohya_ss is a powerful tool for training LoRAs (Low-Rank Adaptations) for Stable Diffusion models.

## Quick Start

### 1. Start Kohya_ss Web UI

```bash
docker compose --profile kohya up -d
```

Access the web UI at: **http://localhost:7860**

### 2. Prepare Your Dataset

**Option A: Caption images automatically**
```bash
# Use BLIP to auto-caption your images
docker compose --profile pipeline run --rm infer \
  python -m pipelines.infer.caption_images \
    --input ./data/training/my_style \
    --model blip \
    --output ./data/training/my_style_captioned
```

**Option B: Manual captions**
```bash
# Create a directory with images
mkdir -p data/training/my_lora/images

# Add text files with same names as images:
# - cat.jpg → cat.txt (contains: "a cute cat sitting")
# - dog.jpg → dog.txt (contains: "a happy dog running")
```

### 3. Training Workflow in Kohya Web UI

**Step 1: Configuration Tab**
- **Model**: Select base model (e.g., SD 1.5, SDXL)
- **Dataset Path**: `/app/datasets/training/my_lora/images`
- **Output Path**: `/app/output/loras/my_lora.safetensors`

**Step 2: Parameters Tab**
- **LoRA Rank**: 8-32 (lower = smaller file, 32 = more capacity)
- **Learning Rate**: 1e-4 to 5e-5 (start with 1e-4)
- **Batch Size**: 1-4 (depends on VRAM)
- **Epochs**: 10-20 (or use steps: 1000-3000)
- **Optimizer**: AdamW8bit (memory efficient)

**Step 3: Advanced Settings**
- **Resolution**: 512x512 (SD 1.5) or 1024x1024 (SDXL)
- **Enable xformers**: Yes (faster training)
- **Mixed Precision**: bf16 (RTX 5090 supports this)
- **Gradient Checkpointing**: Yes (saves VRAM)

**Step 4: Start Training**
- Click **"Start Training"**
- Monitor progress in the web UI or logs:
  ```bash
  docker compose logs -f kohya
  ```

### 4. Use Your Trained LoRA

**In ComfyUI:**
1. Copy LoRA from `./outputs/loras/` to `./models/loras/`
2. Restart ComfyUI: `docker compose --profile comfyui restart`
3. Load LoRA node in your workflow
4. Set weight: 0.5-1.0

**Test generation:**
```bash
# Your LoRA will be in outputs/loras/
ls -lh outputs/loras/
```

## Dataset Structure

```
data/training/my_lora/
├── images/
│   ├── image1.jpg
│   ├── image1.txt  # Caption: "a woman with red hair"
│   ├── image2.jpg
│   ├── image2.txt  # Caption: "a woman smiling"
│   └── ...
```

## Recommended Settings by Use Case

### Style LoRA (Art Style, Photography Style)
- **Images**: 50-200 images
- **Rank**: 16-32
- **Learning Rate**: 1e-4
- **Epochs**: 10-15
- **Caption**: Describe the style ("in art nouveau style", "oil painting")

### Character LoRA (Specific Person/Character)
- **Images**: 20-50 images
- **Rank**: 8-16
- **Learning Rate**: 5e-5
- **Epochs**: 15-20
- **Caption**: Describe person + context ("woman with blonde hair sitting", "man in suit")

### Concept LoRA (Objects, Poses, etc.)
- **Images**: 30-100 images
- **Rank**: 16
- **Learning Rate**: 1e-4
- **Epochs**: 10-15
- **Caption**: Describe the concept clearly

## Tips for Better Results

1. **Diverse Poses/Angles**: Include variety in your training data
2. **Consistent Quality**: Use high-quality images (no watermarks, good lighting)
3. **Good Captions**: Describe what makes images unique to your style/subject
4. **Don't Overtrain**: Stop if validation loss stops improving
5. **Test Frequently**: Generate samples every few epochs
6. **Use Regularization Images**: Add general images to prevent overfitting

## Monitoring Training

**TensorBoard** (optional):
```bash
# View training metrics
docker compose --profile kohya exec kohya \
  tensorboard --logdir /app/logs --host 0.0.0.0 --port 6006

# Access at http://localhost:6006
```

**Weights & Biases** (optional):
```bash
# Set WANDB_API_KEY in .env file
echo "WANDB_API_KEY=your_key_here" >> .env

# Restart Kohya to use W&B logging
docker compose --profile kohya restart
```

## Troubleshooting

### Out of Memory
- Reduce batch size to 1
- Lower resolution (512x512 instead of 768x768)
- Enable gradient checkpointing
- Reduce LoRA rank

### Training Too Slow
- Check GPU usage: `docker compose exec kohya nvidia-smi`
- Enable xformers
- Increase batch size if you have VRAM

### Bad Results
- More training data (at least 20-30 images)
- Better captions
- Adjust learning rate (try 5e-5)
- Try different LoRA ranks

## Advanced: Training from CLI

```bash
# Run accelerate training directly
docker compose --profile kohya exec kohya \
  accelerate launch train_network.py \
    --pretrained_model_name_or_path="runwayml/stable-diffusion-v1-5" \
    --train_data_dir="/app/datasets/training/my_lora" \
    --output_dir="/app/output/loras" \
    --network_module=networks.lora \
    --network_dim=32 \
    --learning_rate=1e-4 \
    --max_train_epochs=10
```

## Resources

- [Kohya_ss GitHub](https://github.com/bmaltais/kohya_ss)
- [LoRA Training Guide](https://rentry.org/lora_train)
- [Stable Diffusion Training Tips](https://rentry.org/2chAI_LoRA_Dreambooth_guide_english)
