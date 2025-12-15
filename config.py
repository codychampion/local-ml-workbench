"""
MLOps Workspace Configuration
=============================
Central configuration module using environment variables with sensible defaults.
All sensitive credentials should be set via environment variables, never hardcoded.

Phase 1: Local Core - CPU-only, offline mode, mocked cloud services
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class WandBConfig:
    """Weights & Biases configuration."""

    project: str = field(default_factory=lambda: os.getenv("WANDB_PROJECT", "mlops-workspace"))
    entity: Optional[str] = field(default_factory=lambda: os.getenv("WANDB_ENTITY"))
    # PHASE 1: Always use offline mode for local development
    mode: str = field(default_factory=lambda: os.getenv("WANDB_MODE", "offline"))
    dir: Path = field(default_factory=lambda: Path(os.getenv("WANDB_DIR", "./outputs/wandb")))

    # PHASE 2/3 TODO: Add online mode support with proper API key management
    # api_key: Optional[str] = field(default_factory=lambda: os.getenv("WANDB_API_KEY"))
    # run_group: Optional[str] = None  # For grouping distributed training runs


@dataclass
class B2Config:
    """Backblaze B2 storage configuration."""

    # PHASE 1: Mocked - these are placeholders for future use
    application_key_id: Optional[str] = field(
        default_factory=lambda: os.getenv("B2_APPLICATION_KEY_ID")
    )
    application_key: Optional[str] = field(
        default_factory=lambda: os.getenv("B2_APPLICATION_KEY")
    )
    bucket_name: str = field(
        default_factory=lambda: os.getenv("B2_BUCKET_NAME", "mlops-data-bucket")
    )

    # PHASE 1: Local mock paths
    local_manifest_path: Path = field(
        default_factory=lambda: Path(os.getenv("B2_LOCAL_MANIFEST", ".b2_local_manifest.json"))
    )
    local_data_dir: Path = field(
        default_factory=lambda: Path(os.getenv("B2_LOCAL_DATA_DIR", "./data/raw"))
    )

    # Rate limiting configuration (simulated in Phase 1)
    max_requests_per_minute: int = field(
        default_factory=lambda: int(os.getenv("B2_MAX_REQUESTS_PER_MIN", "100"))
    )

    # PHASE 2/3 TODO: Add encryption settings for data at rest
    # encryption_key: Optional[str] = field(default_factory=lambda: os.getenv("B2_ENCRYPTION_KEY"))


@dataclass
class FiftyOneConfig:
    """FiftyOne data visualization configuration."""

    dataset_dir: Path = field(
        default_factory=lambda: Path(os.getenv("FIFTYONE_DATASET_DIR", "./data/fiftyone"))
    )
    # PHASE 1: Local server only
    port: int = field(default_factory=lambda: int(os.getenv("FIFTYONE_PORT", "5151")))
    address: str = field(default_factory=lambda: os.getenv("FIFTYONE_ADDRESS", "0.0.0.0"))

    # PHASE 2/3 TODO: Add remote access configuration for team collaboration
    # remote_url: Optional[str] = field(default_factory=lambda: os.getenv("FIFTYONE_REMOTE_URL"))


@dataclass
class ComputeConfig:
    """Compute resource configuration."""

    # PHASE 1: CPU-only execution
    device: str = field(default_factory=lambda: os.getenv("COMPUTE_DEVICE", "cpu"))
    num_workers: int = field(
        default_factory=lambda: int(os.getenv("NUM_WORKERS", "2"))
    )

    # PHASE 2/3 TODO: SkyPilot integration for cloud GPU provisioning
    # skypilot_config:
    #   - cloud_providers: ["aws", "gcp", "azure"]
    #   - instance_types: ["p3.2xlarge", "a100-40gb"]
    #   - spot_instances: True  # Cost optimization
    #   - max_cost_per_hour: 10.0

    # PHASE 2/3 TODO: Prefect integration for workflow orchestration
    # prefect_api_url: Optional[str] = field(default_factory=lambda: os.getenv("PREFECT_API_URL"))
    # prefect_api_key: Optional[str] = field(default_factory=lambda: os.getenv("PREFECT_API_KEY"))


@dataclass
class ProjectPaths:
    """Standard project paths."""

    root: Path = field(default_factory=lambda: Path(os.getenv("PROJECT_ROOT", ".")))
    data_raw: Path = field(default_factory=lambda: Path("./data/raw"))
    data_processed: Path = field(default_factory=lambda: Path("./data/processed"))
    outputs: Path = field(default_factory=lambda: Path("./outputs"))
    models: Path = field(default_factory=lambda: Path("./outputs/models"))
    logs: Path = field(default_factory=lambda: Path("./outputs/logs"))

    def ensure_dirs(self) -> None:
        """Create all project directories if they don't exist."""
        for path_attr in ["data_raw", "data_processed", "outputs", "models", "logs"]:
            path = getattr(self, path_attr)
            path.mkdir(parents=True, exist_ok=True)


@dataclass
class Config:
    """Main configuration container."""

    wandb: WandBConfig = field(default_factory=WandBConfig)
    b2: B2Config = field(default_factory=B2Config)
    fiftyone: FiftyOneConfig = field(default_factory=FiftyOneConfig)
    compute: ComputeConfig = field(default_factory=ComputeConfig)
    paths: ProjectPaths = field(default_factory=ProjectPaths)

    # Environment identification
    environment: str = field(
        default_factory=lambda: os.getenv("MLOPS_ENV", "development")
    )
    debug: bool = field(
        default_factory=lambda: os.getenv("DEBUG", "false").lower() == "true"
    )

    def __post_init__(self):
        """Ensure required directories exist on initialization."""
        self.paths.ensure_dirs()
        self.wandb.dir.mkdir(parents=True, exist_ok=True)


# Global configuration instance
config = Config()


def get_config() -> Config:
    """Get the global configuration instance."""
    return config


def reload_config() -> Config:
    """Reload configuration from environment variables."""
    global config
    config = Config()
    return config


# PHASE 2/3 TODO: Add configuration validation
# def validate_config() -> List[str]:
#     """Validate configuration and return list of warnings/errors."""
#     issues = []
#     if config.environment == "production":
#         if config.wandb.mode == "offline":
#             issues.append("WARNING: W&B offline mode in production")
#         if not config.b2.application_key_id:
#             issues.append("ERROR: B2 credentials required in production")
#     return issues
