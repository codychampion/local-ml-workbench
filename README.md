# MLOps Workspace

A professional MLOps repository focused on **reproducibility** and **experiment tracking**. This workspace provides a complete pipeline infrastructure for machine learning projects with integrated tooling for data management, experiment tracking, and visualization.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        MLOps Workspace Architecture                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────────────┐  │
│  │   Projects   │    │   Storage    │    │   Experiment Tracking    │  │
│  ├──────────────┤    ├──────────────┤    ├──────────────────────────┤  │
│  │ flux-comfyui │───▶│  B2 Client   │───▶│   Weights & Biases       │  │
│  │ adversarial  │    │  (Mocked P1) │    │   (Offline Mode P1)      │  │
│  └──────────────┘    └──────────────┘    └──────────────────────────┘  │
│         │                   │                        │                  │
│         ▼                   ▼                        ▼                  │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                    FiftyOne Visualization                         │  │
│  │                    (Local Data Exploration)                       │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## Phases

### Phase 1: Local Core (Current)
- **Environment**: CPU-only, resource-constrained development
- **Storage**: Mocked B2 client using local manifest
- **Tracking**: W&B offline mode
- **Visualization**: FiftyOne local server

### Phase 2/3: Scaling (Future)
- **Orchestration**: Prefect for workflow management
- **Compute**: SkyPilot for cloud GPU provisioning
- **Storage**: Full B2 integration with encryption
- **Tracking**: W&B online with team collaboration

---

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Git
- 8GB RAM recommended (4GB minimum)

### Phase 1 Execution Steps

#### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd mlops-workspace

# Create required directories
mkdir -p data/raw data/processed outputs/wandb outputs/models
```

#### 2. Build and Start Container

```bash
# Build the Docker image
docker-compose build

# Start the container
docker-compose up -d

# Enter the container
docker-compose exec mlops bash
```

#### 3. Run Image Generation Pipeline (Flux-ComfyUI)

```bash
# Inside the container
python projects/flux-comfyui-generation/run_generation.py \
    --prompts "A mountain at sunset" "A futuristic city" \
    --output-dir ./outputs/flux-generations \
    --width 256 \
    --height 256 \
    --seed 42
```

**Expected Output:**
- Generated images saved to `./outputs/flux-generations/`
- W&B run saved to `./outputs/wandb/offline-*/`
- Uploaded to mocked B2 storage

#### 4. Run Adversarial Patch Pipeline

```bash
# Generate adversarial patches and visualize with FiftyOne
python projects/adversarial-patches/generate_patch.py \
    --output-dir ./outputs/adversarial-patches \
    --patch-size 64 64 \
    --num-samples 5 \
    --patterns noise checkerboard gradient \
    --launch-app
```

**Expected Output:**
- Patched images saved to `./outputs/adversarial-patches/`
- FiftyOne dataset created for visualization
- FiftyOne app launched at http://localhost:5151

#### 5. View W&B Results (Offline)

```bash
# Sync offline runs when you have internet access
wandb sync ./outputs/wandb/offline-*

# Or view locally without syncing
ls -la ./outputs/wandb/
```

---

## Project Structure

```
mlops-workspace/
├── Dockerfile                      # CPU-optimized container
├── docker-compose.yml              # Service orchestration
├── requirements.txt                # Python dependencies
├── config.py                       # Central configuration
├── .b2_local_manifest.json         # Mocked B2 file manifest
│
├── data_transfer/                  # Cloud storage module
│   ├── __init__.py
│   └── b2_client.py               # B2 client (mocked in Phase 1)
│
├── projects/
│   ├── flux-comfyui-generation/
│   │   ├── __init__.py
│   │   └── run_generation.py      # Image generation pipeline
│   │
│   └── adversarial-patches/
│       ├── __init__.py
│       └── generate_patch.py      # Adversarial attack pipeline
│
├── data/
│   ├── raw/                       # Raw input data
│   ├── processed/                 # Processed data
│   └── fiftyone/                  # FiftyOne database
│
└── outputs/
    ├── wandb/                     # W&B offline runs
    ├── models/                    # Saved models
    └── logs/                      # Application logs
```

---

## Tool Integration Guide

### Weights & Biases (W&B)

**Phase 1 Configuration:**
```python
import wandb

wandb.init(
    project="mlops-workspace",
    mode="offline",  # Required for Phase 1
    dir="./outputs/wandb"
)

# Log metrics
wandb.log({"loss": 0.5, "accuracy": 0.95})

# Log images
wandb.log({"image": wandb.Image(numpy_array)})
```

**Environment Variables:**
```bash
WANDB_MODE=offline
WANDB_PROJECT=mlops-workspace
WANDB_DIR=/workspace/outputs/wandb
```

<!-- PHASE 2/3 TODO: W&B Online Configuration
export WANDB_API_KEY=your-api-key
export WANDB_MODE=online
export WANDB_ENTITY=your-team
-->

### FiftyOne

**Loading and Visualizing Data:**
```python
import fiftyone as fo
import fiftyone.zoo as foz

# Load a small dataset
dataset = foz.load_zoo_dataset("quickstart", max_samples=10)

# Launch visualization app
session = fo.launch_app(dataset, port=5151)
```

**Access**: http://localhost:5151

### Backblaze B2 (Mocked)

**Phase 1 Usage:**
```python
from data_transfer import B2Client

# Automatically uses MockedB2Client in Phase 1
client = B2Client()

# List files from local manifest
files = client.list_files(prefix="datasets/")

# Download (copies from local data/raw/)
client.download_file("image.png", Path("./output.png"))

# Upload (copies to local data/raw/ and updates manifest)
client.upload_file(Path("./output.png"), "uploads/output.png")
```

**Local Manifest** (`.b2_local_manifest.json`):
```json
{
  "bucket_name": "mlops-data-bucket-mock",
  "files": [
    {
      "file_name": "datasets/sample_images/image_001.png",
      "file_id": "mock_file_001",
      "size_bytes": 1024,
      "content_sha256": "..."
    }
  ]
}
```

---

## Configuration

All configuration is managed through environment variables with sensible defaults.

### Core Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MLOPS_ENV` | `development` | Environment identifier |
| `DEBUG` | `false` | Enable debug logging |
| `COMPUTE_DEVICE` | `cpu` | Compute device (Phase 1: always cpu) |
| `NUM_WORKERS` | `2` | Number of worker processes |

### W&B Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `WANDB_MODE` | `offline` | W&B mode (offline for Phase 1) |
| `WANDB_PROJECT` | `mlops-workspace` | W&B project name |
| `WANDB_DIR` | `./outputs/wandb` | W&B local directory |

### B2 Configuration (Phase 1: Mocked)

| Variable | Default | Description |
|----------|---------|-------------|
| `B2_LOCAL_MANIFEST` | `.b2_local_manifest.json` | Local manifest file |
| `B2_LOCAL_DATA_DIR` | `./data/raw` | Local data directory |
| `B2_MAX_REQUESTS_PER_MIN` | `100` | Rate limit (simulated) |

---

## Phase 2/3 Roadmap

### Prefect Integration (Workflow Orchestration)

<!-- PHASE 2/3 TODO: Prefect Setup -->

Prefect will provide:
- **DAG-based workflows**: Define multi-step pipelines (Data Prep → Train → Deploy)
- **Scheduling**: Cron-based and event-driven triggers
- **Retries**: Automatic retry with exponential backoff
- **Observability**: Real-time workflow monitoring

**Planned Architecture:**
```
┌─────────────────────────────────────────────────────────────────┐
│                    Prefect Flow: Training Pipeline               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐  │
│  │  Fetch   │───▶│ Preprocess│───▶│  Train   │───▶│  Deploy  │  │
│  │   Data   │    │   Data   │    │  Model   │    │  Model   │  │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘  │
│       │               │               │               │         │
│       ▼               ▼               ▼               ▼         │
│  [B2 Storage]   [FiftyOne QA]  [W&B Tracking]  [Model Registry] │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Example Flow (Future):**
```python
from prefect import flow, task

@task(retries=3, retry_delay_seconds=60)
def fetch_data(dataset_id: str):
    """Fetch data from B2 storage."""
    pass

@task
def train_model(data, config: dict):
    """Train model with W&B tracking."""
    pass

@flow(name="training-pipeline")
def training_flow(config: dict):
    data = fetch_data(config["dataset_id"])
    model = train_model(data, config)
    return model
```

### SkyPilot Integration (Cloud GPU Provisioning)

<!-- PHASE 2/3 TODO: SkyPilot Setup -->

SkyPilot will provide:
- **Multi-cloud support**: AWS, GCP, Azure
- **Cost optimization**: Automatic spot instance selection
- **GPU provisioning**: A100, V100, T4 instances
- **Reproducibility**: Identical environments across clouds

**Planned Usage:**
```python
import sky

# Define task
task = sky.Task(
    run="python train.py --gpu",
    setup="pip install -r requirements.txt"
)

# Configure resources
task.set_resources(sky.Resources(
    accelerators={"A100": 1},
    cloud=sky.AWS(),
    use_spot=True,
    disk_size=256
))

# Launch
sky.launch(task, cluster_name="training-cluster")
```

**Sky YAML Configuration (Future):**
```yaml
# sky.yaml
resources:
  accelerators: A100:1
  use_spot: true
  disk_size: 256

setup: |
  pip install -r requirements.txt
  wandb login $WANDB_API_KEY

run: |
  python projects/flux-comfyui-generation/run_generation.py --gpu
```

---

## Development

### Running Tests

```bash
# Inside container
pytest tests/ -v --cov=.

# Run specific test
pytest tests/test_b2_client.py -v
```

### Code Quality

```bash
# Format code
black .

# Lint
ruff check .
```

### Adding New Projects

1. Create project directory:
   ```bash
   mkdir -p projects/my-new-project
   ```

2. Create `__init__.py` and main script following existing patterns

3. Use the standard imports:
   ```python
   from config import get_config
   from data_transfer import B2Client
   import wandb
   import fiftyone as fo
   ```

---

## Troubleshooting

### Common Issues

**FiftyOne Port Already in Use:**
```bash
# Find and kill process on port 5151
lsof -i :5151 | grep LISTEN
kill -9 <PID>
```

**W&B Offline Mode Issues:**
```bash
# Check WANDB_MODE is set
echo $WANDB_MODE  # Should be "offline"

# Verify wandb directory exists
ls -la ./outputs/wandb/
```

**Docker Memory Issues:**
```bash
# Check container resource usage
docker stats mlops-workspace

# Increase memory in docker-compose.yml if needed
```

### Getting Help

- Check existing documentation
- Review Phase 1 constraints (CPU-only, offline mode)
- Examine log files in `./outputs/logs/`

---

## Security Considerations

- **No hardcoded credentials**: All secrets via environment variables
- **Non-root container user**: Improved container security
- **Rate limiting**: Built into B2 client to prevent abuse
- **Encrypted transfers**: Simulated in Phase 1, real AES-256 in Phase 2/3
- **Adversarial research**: For authorized security research only

---

## License

MIT License - See LICENSE file for details.

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Follow existing code patterns
4. Add tests for new functionality
5. Submit a pull request

---

*Phase 1: Local Core - Built for reproducibility and CPU-only development*
