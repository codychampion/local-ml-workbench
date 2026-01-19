# HunyuanVideo LoRA Training with Diffusion-Pipe

## The Simple Solution That Actually Works

Forget all the complex scripts - this is a **pre-built Docker container with a web UI**. No Python, no command line debugging, just a working interface.

## Quick Start (3 Steps)

### 1. Start the Container

```bash
docker compose -f docker-compose.diffusion-pipe.yml up -d
```

**That's it.** The container is now running.

### 2. Open the Web UI

Go to: **http://localhost:7860**

You'll see a Gradio interface with all training options.

### 3. Configure & Train

In the web UI:

1. **Model Selection**: Choose "HunyuanVideo"
2. **Dataset Path**: `/workspace/datasets/scraped/fallout_nv_20260116_113625`
3. **Output Path**: `/workspace/outputs/lora/fallout_nv`
4. **LoRA Settings**:
   - Rank: 32
   - Alpha: 32
   - Learning Rate: 1e-4
5. **Training Settings**:
   - Epochs: 20
   - Batch Size: 1
   - Resolution: 960x544

Click **"Start Training"** and you're done.

## What You Get

- ✅ **Gradio Web UI**: No command line needed
- ✅ **TensorBoard**: Monitor training at http://localhost:6006
- ✅ **Jupyter Lab**: Manage files at http://localhost:8888
- ✅ **Automatic Setup**: Downloads models on first run
- ✅ **ComfyUI Compatible**: Outputs standard safetensors

## Monitoring Training

### TensorBoard (Recommended)
Open http://localhost:6006 to see:
- Loss curves
- Learning rate
- Training progress

### Jupyter Lab
Open http://localhost:8888 to:
- Browse output files
- Check training logs
- Manage datasets

### Container Logs
```bash
docker logs -f hunyuan-lora-trainer
```

## After Training

Your LoRA will be in:
```
outputs/lora/fallout_nv/fallout_nv_lora.safetensors
```

Copy to ComfyUI:
```bash
cp outputs/lora/fallout_nv/fallout_nv_lora.safetensors \
   /path/to/ComfyUI/models/loras/
```

Then use in your `LoraLoaderModelOnly` node with strength 0.8.

## Stopping the Container

```bash
docker compose -f docker-compose.diffusion-pipe.yml down
```

## Restarting Training

The container automatically saves progress. Just start it again:
```bash
docker compose -f docker-compose.diffusion-pipe.yml up -d
```

## Troubleshooting

### Can't Access Web UI
Check if container is running:
```bash
docker ps | grep hunyuan-lora-trainer
```

If not running, check logs:
```bash
docker logs hunyuan-lora-trainer
```

### Out of Memory
In the web UI, reduce:
- Batch size to 1 (already minimum)
- Resolution to 768x432
- Enable gradient checkpointing

### Training Stops
Check GPU temperature:
```bash
nvidia-smi
```

Should be below 85°C.

## Advanced Configuration

### Custom Config File

Create `configs/hunyuan_lora.toml`:
```toml
[model]
name = "HunyuanVideo"
type = "video"

[training]
learning_rate = 1e-4
batch_size = 1
epochs = 20
gradient_checkpointing = true

[lora]
rank = 32
alpha = 32
target_modules = ["to_q", "to_k", "to_v", "to_out"]

[optimizer]
type = "adamw8bit"
weight_decay = 0.01

[dataset]
path = "/workspace/datasets/scraped/fallout_nv_20260116_113625"
resolution = [960, 544]
```

Then select this config in the Gradio UI.

### Manual Command (If Gradio Fails)

SSH into the container:
```bash
docker exec -it hunyuan-lora-trainer bash
```

Run training manually:
```bash
conda activate pyenv
NCCL_P2P_DISABLE="1" NCCL_IB_DISABLE="1" \
deepspeed --num_gpus=1 train.py \
  --deepspeed \
  --config /workspace/configs/hunyuan_lora.toml
```

## Why This is Better

| Feature | Diffusion-Pipe | Our Custom Scripts |
|---------|----------------|-------------------|
| **Setup Time** | 1 command | Multiple steps |
| **User Interface** | Web UI ✅ | Command line ❌ |
| **Debugging** | Visual logs | Text parsing |
| **Model Download** | Automatic | Manual |
| **Error Messages** | Clear in UI | Buried in logs |
| **Community Support** | Active | DIY |
| **Works Out of Box** | Yes ✅ | Lots of fixes needed ❌ |

## Ports Used

- **7860**: Gradio training interface
- **8888**: Jupyter Lab file manager
- **6006**: TensorBoard monitoring

## Storage Locations

All data is in your project directory:
- `data/`: Your datasets
- `models/`: Downloaded models (~33GB)
- `outputs/`: Trained LoRAs
- `configs/`: Training configurations

## Expected Training Time

For your 34 Fallout NV images, 20 epochs:
- **First run**: ~7-8 hours (includes model download + training)
- **Subsequent runs**: ~6 hours (model cached)

## Getting Started Now

```bash
# 1. Start the container
docker compose -f docker-compose.diffusion-pipe.yml up -d

# 2. Wait 30 seconds for startup
sleep 30

# 3. Open your browser
# Go to: http://localhost:7860

# 4. Configure training in the UI
# (Point to your Fallout NV dataset)

# 5. Click "Start Training"

# 6. Monitor in TensorBoard
# Go to: http://localhost:6006
```

That's it. No scripts, no debugging, just training.

## References

- [Diffusion-Pipe GitHub](https://github.com/tdrussell/diffusion-pipe)
- [Docker UI Fork](https://github.com/alisson-anjos/diffusion-pipe-ui)
- [Civitai Tutorial](https://civitai.com/articles/10547/train-lora-for-hunyuan-video-using-diffusion-pipe-gradio-interface-with-docker-runpod-and-vastai)
- [RunPod Blog](https://blog.runpod.io/train-your-own-video-loras-with-diffusion-pipe/)
