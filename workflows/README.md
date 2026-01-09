# Workflow Templates

This directory stores workflow templates for various services.

## ComfyUI Workflows (`comfyui/`)

Store your ComfyUI workflow JSON files here.

### How to use:

1. **Save a workflow from ComfyUI:**
   - In ComfyUI web interface, click "Save" button
   - Download the JSON file
   - Place it in `workflows/comfyui/`

2. **Load a workflow in ComfyUI:**
   - In ComfyUI, click "Load" button
   - Navigate to `/app/workflows/comfyui/` in the container
   - Select your workflow JSON file

3. **Share workflows:**
   - Commit workflow JSON files to git
   - Others can load them from the workflows directory

### Workflow naming convention:
- `txt2img_basic.json` - Basic text-to-image generation
- `lora_training.json` - LoRA training workflow
- `style_transfer.json` - Style transfer workflow
- etc.
