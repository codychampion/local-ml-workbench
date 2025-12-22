#!/usr/bin/env python3
"""
CUAD Dataset Downloader
=======================
Download the Contract Understanding Atticus Dataset (CUAD) from Hugging Face Hub.

CUAD contains 13,000+ labels across 510 commercial legal contracts for 41 clause types.
This script downloads and prepares the dataset for contract review experiments.

Usage (CLI):
    python -m pipelines.collect.collect_cuad --split train --limit 1000

Usage (Hydra):
    python -m pipelines.collect.collect_cuad pipeline=collect_cuad
"""

import argparse
import json
import os
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime

# Optional Hydra
try:
    import hydra
    from omegaconf import DictConfig
except ImportError:
    hydra = None
    DictConfig = None

# HF datasets
try:
    from datasets import load_dataset
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False


def download_cuad_dataset(
    dataset: str,
    split: str,
    limit: int,
    output_dir: Path,
    save_metadata: bool = True,
) -> Dict[str, int]:
    """Download CUAD dataset and prepare for contract review tasks.

    Args:
        dataset: Dataset name (theatticusproject/cuad)
        split: Dataset split (train/test)
        limit: Max samples to download (-1 for all)
        output_dir: Output base directory
        save_metadata: Whether to save metadata file

    Returns:
        Dictionary with download statistics
    """
    if not HF_AVAILABLE:
        raise RuntimeError("datasets package not installed. pip install datasets")

    print(f"[CUAD] Loading dataset '{dataset}' split='{split}'...")
    ds = load_dataset(dataset, split=split, streaming=False)

    target_dir = output_dir / "cuad" / split
    target_dir.mkdir(parents=True, exist_ok=True)

    # Prepare output file
    output_file = target_dir / "cuad_contracts.jsonl"
    stats = {"total_samples": 0, "clause_categories": set()}

    print(f"[CUAD] Processing samples...")
    with output_file.open("w", encoding="utf-8") as f:
        for idx, sample in enumerate(ds):
            if limit > 0 and idx >= limit:
                break

            # Extract sample data
            # CUAD format: {'text': '...', additional fields for each clause type}
            sample_data = {
                "id": idx,
                "text": sample.get("text", ""),
                "text_length": len(sample.get("text", "")),
                "timestamp": datetime.now().isoformat(),
            }

            # Add all other fields (clause annotations, etc.)
            for key, value in sample.items():
                if key != "text":
                    sample_data[key] = value
                    if value:  # Track which clause categories are present
                        stats["clause_categories"].add(key)

            f.write(json.dumps(sample_data, ensure_ascii=False) + "\n")
            stats["total_samples"] += 1

            if (idx + 1) % 100 == 0:
                print(f"[CUAD] Processed {idx + 1} samples...")

    # Save metadata
    if save_metadata:
        metadata = {
            "dataset": dataset,
            "split": split,
            "download_date": datetime.now().isoformat(),
            "total_samples": stats["total_samples"],
            "clause_categories": sorted(list(stats["clause_categories"])),
            "num_categories": len(stats["clause_categories"]),
            "output_file": str(output_file),
        }

        metadata_file = target_dir / "metadata.json"
        with metadata_file.open("w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        print(f"[CUAD] Metadata saved to {metadata_file}")

    print(f"[CUAD] Downloaded {stats['total_samples']} samples to {target_dir}")
    print(f"[CUAD] Found {len(stats['clause_categories'])} clause categories")

    return stats


def prepare_for_maker_experiment(
    cuad_dir: Path,
    output_dir: Path,
    clause_category: Optional[str] = None,
) -> None:
    """Prepare CUAD data for MAKER-style decomposition experiments.

    This function prepares the dataset for the contract review experiment
    by decomposing the task into individual clause identification subtasks.

    Args:
        cuad_dir: Directory containing CUAD data
        output_dir: Output directory for experiment data
        clause_category: Specific clause category to focus on (None for all)
    """
    print("[CUAD] Preparing data for MAKER experiment...")

    input_file = cuad_dir / "cuad_contracts.jsonl"
    if not input_file.exists():
        raise FileNotFoundError(f"CUAD data not found at {input_file}")

    output_dir.mkdir(parents=True, exist_ok=True)

    # Load and decompose tasks
    tasks = []
    with input_file.open("r", encoding="utf-8") as f:
        for line in f:
            sample = json.loads(line)

            # Create individual tasks for each clause category
            for key in sample.keys():
                if key not in ["id", "text", "text_length", "timestamp"]:
                    if clause_category is None or key == clause_category:
                        task = {
                            "contract_id": sample["id"],
                            "text": sample["text"],
                            "clause_category": key,
                            "label": sample[key],
                            "task_type": "clause_identification",
                        }
                        tasks.append(task)

    # Save decomposed tasks
    output_file = output_dir / "maker_tasks.jsonl"
    with output_file.open("w", encoding="utf-8") as f:
        for task in tasks:
            f.write(json.dumps(task, ensure_ascii=False) + "\n")

    print(f"[CUAD] Created {len(tasks)} subtasks for MAKER experiment")
    print(f"[CUAD] Saved to {output_file}")


def main_cli():
    parser = argparse.ArgumentParser(description="Download CUAD dataset")
    parser.add_argument("--dataset", default="theatticusproject/cuad",
                       help="Dataset name (default: theatticusproject/cuad)")
    parser.add_argument("--split", default="train", help="Dataset split (default: train)")
    parser.add_argument("--limit", type=int, default=1000,
                       help="Max samples to download (-1 for all, default: 1000)")
    parser.add_argument("--output-dir", type=Path, default=Path("./data/collected"),
                       help="Output base directory")
    parser.add_argument("--prepare-maker", action="store_true",
                       help="Prepare data for MAKER experiment")
    args = parser.parse_args()

    stats = download_cuad_dataset(
        dataset=args.dataset,
        split=args.split,
        limit=args.limit,
        output_dir=args.output_dir,
    )

    if args.prepare_maker:
        cuad_dir = args.output_dir / "cuad" / args.split
        maker_dir = args.output_dir / "cuad_maker_experiment"
        prepare_for_maker_experiment(cuad_dir, maker_dir)


def main_hydra(cfg: DictConfig):
    cuad_cfg = cfg.get("collect_cuad", {})
    output_root = Path(cuad_cfg.get("output_dir", "./data/collected"))

    stats = download_cuad_dataset(
        dataset=cuad_cfg.get("dataset", "theatticusproject/cuad"),
        split=cuad_cfg.get("split", "train"),
        limit=cuad_cfg.get("limit", 1000),
        output_dir=output_root,
        save_metadata=cuad_cfg.get("save_metadata", True),
    )

    # Prepare for MAKER experiment if task decomposition is enabled
    if cuad_cfg.get("task_decomposition", {}).get("enabled", False):
        cuad_dir = output_root / "cuad" / cuad_cfg.get("split", "train")
        maker_dir = output_root / "cuad_maker_experiment"
        prepare_for_maker_experiment(cuad_dir, maker_dir)


if __name__ == "__main__":
    if hydra is not None and "--hydra" in os.sys.argv:
        @hydra.main(config_path="../../conf", config_name="config", version_base=None)
        def hydra_entry(cfg: DictConfig):
            main_hydra(cfg)
        hydra_entry()
    else:
        main_cli()
