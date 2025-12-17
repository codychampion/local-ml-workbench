#!/usr/bin/env python3
"""
ComfyUI S3 Sync Utility
========================
Syncs models and outputs between ComfyUI and MinIO S3 storage.

Usage:
    python s3_sync.py download-models  # Download models from S3
    python s3_sync.py upload-outputs   # Upload outputs to S3
    python s3_sync.py sync-all         # Bidirectional sync
"""

import os
import sys
from pathlib import Path
from typing import Optional

import boto3
from botocore.client import Config


class ComfyUIS3Sync:
    """Syncs ComfyUI models and outputs with MinIO S3."""

    def __init__(self):
        self.s3_endpoint = os.getenv("AWS_S3_ENDPOINT_URL", "http://minio:9000")
        self.access_key = os.getenv("AWS_ACCESS_KEY_ID", "mlops-admin")
        self.secret_key = os.getenv("AWS_SECRET_ACCESS_KEY", "mlops-dev-password")
        self.models_bucket = os.getenv("S3_MODELS_BUCKET", "mlops-models")
        self.outputs_bucket = os.getenv("S3_OUTPUTS_BUCKET", "mlops-outputs")

        self.comfyui_root = Path("/workspace/ComfyUI")
        self.models_dir = self.comfyui_root / "models"
        self.output_dir = self.comfyui_root / "output"

        self.client = boto3.client(
            's3',
            endpoint_url=self.s3_endpoint,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            config=Config(signature_version='s3v4'),
            region_name='us-east-1'
        )

    def ensure_buckets(self):
        """Ensure required buckets exist."""
        for bucket in [self.models_bucket, self.outputs_bucket]:
            try:
                self.client.head_bucket(Bucket=bucket)
            except Exception:
                try:
                    self.client.create_bucket(Bucket=bucket)
                    print(f"[S3] Created bucket: {bucket}")
                except Exception as e:
                    print(f"[S3] Bucket {bucket} may already exist: {e}")

    def download_models(self, model_types: Optional[list] = None):
        """Download models from S3 to ComfyUI models directory."""
        if model_types is None:
            model_types = ["checkpoints", "loras", "clip", "vae", "controlnet"]

        print(f"[S3] Downloading models from s3://{self.models_bucket}/comfyui/")

        for model_type in model_types:
            s3_prefix = f"comfyui/{model_type}/"
            local_dir = self.models_dir / model_type
            local_dir.mkdir(parents=True, exist_ok=True)

            try:
                paginator = self.client.get_paginator('list_objects_v2')
                for page in paginator.paginate(Bucket=self.models_bucket, Prefix=s3_prefix):
                    for obj in page.get('Contents', []):
                        key = obj['Key']
                        filename = key[len(s3_prefix):]
                        if not filename:
                            continue

                        local_path = local_dir / filename
                        local_path.parent.mkdir(parents=True, exist_ok=True)

                        # Skip if already exists and same size
                        if local_path.exists() and local_path.stat().st_size == obj['Size']:
                            print(f"[S3] Skipping (exists): {filename}")
                            continue

                        print(f"[S3] Downloading: {model_type}/{filename}")
                        self.client.download_file(self.models_bucket, key, str(local_path))

            except Exception as e:
                print(f"[S3] Error downloading {model_type}: {e}")

        print("[S3] Model download complete")

    def upload_outputs(self, prefix: str = "comfyui/outputs"):
        """Upload ComfyUI outputs to S3."""
        print(f"[S3] Uploading outputs to s3://{self.outputs_bucket}/{prefix}/")

        if not self.output_dir.exists():
            print("[S3] No output directory found")
            return

        for file_path in self.output_dir.rglob("*"):
            if file_path.is_file():
                relative = file_path.relative_to(self.output_dir)
                s3_key = f"{prefix}/{relative}"

                try:
                    print(f"[S3] Uploading: {relative}")
                    self.client.upload_file(str(file_path), self.outputs_bucket, s3_key)
                except Exception as e:
                    print(f"[S3] Error uploading {relative}: {e}")

        print("[S3] Output upload complete")

    def upload_model(self, local_path: Path, model_type: str):
        """Upload a single model to S3."""
        s3_key = f"comfyui/{model_type}/{local_path.name}"
        print(f"[S3] Uploading model: {local_path.name} -> s3://{self.models_bucket}/{s3_key}")

        try:
            self.client.upload_file(str(local_path), self.models_bucket, s3_key)
            print(f"[S3] Upload complete: {local_path.name}")
        except Exception as e:
            print(f"[S3] Error uploading model: {e}")

    def list_available_models(self) -> dict:
        """List models available in S3."""
        models = {}
        model_types = ["checkpoints", "loras", "clip", "vae", "controlnet", "upscale_models"]

        for model_type in model_types:
            s3_prefix = f"comfyui/{model_type}/"
            models[model_type] = []

            try:
                paginator = self.client.get_paginator('list_objects_v2')
                for page in paginator.paginate(Bucket=self.models_bucket, Prefix=s3_prefix):
                    for obj in page.get('Contents', []):
                        key = obj['Key']
                        filename = key[len(s3_prefix):]
                        if filename:
                            models[model_type].append({
                                "name": filename,
                                "size_mb": obj['Size'] / 1024 / 1024,
                                "last_modified": obj['LastModified'].isoformat()
                            })
            except Exception as e:
                print(f"[S3] Error listing {model_type}: {e}")

        return models


def main():
    """Main entry point."""
    sync = ComfyUIS3Sync()
    sync.ensure_buckets()

    if len(sys.argv) < 2:
        print("Usage: python s3_sync.py <command>")
        print("Commands:")
        print("  download-models  - Download models from S3")
        print("  upload-outputs   - Upload outputs to S3")
        print("  sync-all         - Download models and upload outputs")
        print("  list-models      - List available models in S3")
        return

    command = sys.argv[1]

    if command == "download-models":
        sync.download_models()
    elif command == "upload-outputs":
        sync.upload_outputs()
    elif command == "sync-all":
        sync.download_models()
        sync.upload_outputs()
    elif command == "list-models":
        models = sync.list_available_models()
        for model_type, items in models.items():
            print(f"\n{model_type}:")
            if items:
                for item in items:
                    print(f"  - {item['name']} ({item['size_mb']:.1f} MB)")
            else:
                print("  (none)")
    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
