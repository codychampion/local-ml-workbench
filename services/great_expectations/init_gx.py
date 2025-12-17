#!/usr/bin/env python3
"""
Great Expectations Initialization Script
=========================================
Sets up default expectation suites for the MLOps workbench.

Usage:
    python init_gx.py

This creates:
    - Default data sources (MinIO S3, local filesystem)
    - Common expectation suites for ML datasets
"""

import os
from pathlib import Path

import great_expectations as gx
from great_expectations.core.expectation_configuration import ExpectationConfiguration


def init_default_suites(context):
    """Create default expectation suites for ML workflows."""

    # Image dataset expectations
    image_suite = context.add_or_update_expectation_suite("image_dataset")
    image_suite.add_expectation(ExpectationConfiguration(
        expectation_type="expect_column_to_exist",
        kwargs={"column": "filepath"}
    ))
    image_suite.add_expectation(ExpectationConfiguration(
        expectation_type="expect_column_to_exist",
        kwargs={"column": "caption"}
    ))
    image_suite.add_expectation(ExpectationConfiguration(
        expectation_type="expect_column_values_to_not_be_null",
        kwargs={"column": "filepath"}
    ))
    image_suite.add_expectation(ExpectationConfiguration(
        expectation_type="expect_column_values_to_match_regex",
        kwargs={"column": "filepath", "regex": r".*\.(jpg|jpeg|png|webp)$"}
    ))
    context.save_expectation_suite(image_suite)
    print("[GX] Created 'image_dataset' expectation suite")

    # Caption dataset expectations
    caption_suite = context.add_or_update_expectation_suite("caption_dataset")
    caption_suite.add_expectation(ExpectationConfiguration(
        expectation_type="expect_column_to_exist",
        kwargs={"column": "image_path"}
    ))
    caption_suite.add_expectation(ExpectationConfiguration(
        expectation_type="expect_column_to_exist",
        kwargs={"column": "caption"}
    ))
    caption_suite.add_expectation(ExpectationConfiguration(
        expectation_type="expect_column_values_to_not_be_null",
        kwargs={"column": "caption"}
    ))
    caption_suite.add_expectation(ExpectationConfiguration(
        expectation_type="expect_column_value_lengths_to_be_between",
        kwargs={"column": "caption", "min_value": 10, "max_value": 500}
    ))
    context.save_expectation_suite(caption_suite)
    print("[GX] Created 'caption_dataset' expectation suite")

    # Training metrics expectations
    metrics_suite = context.add_or_update_expectation_suite("training_metrics")
    metrics_suite.add_expectation(ExpectationConfiguration(
        expectation_type="expect_column_to_exist",
        kwargs={"column": "epoch"}
    ))
    metrics_suite.add_expectation(ExpectationConfiguration(
        expectation_type="expect_column_to_exist",
        kwargs={"column": "loss"}
    ))
    metrics_suite.add_expectation(ExpectationConfiguration(
        expectation_type="expect_column_values_to_be_between",
        kwargs={"column": "loss", "min_value": 0, "max_value": 100}
    ))
    context.save_expectation_suite(metrics_suite)
    print("[GX] Created 'training_metrics' expectation suite")


def main():
    """Initialize Great Expectations with default configuration."""
    print("=" * 60)
    print("Great Expectations Initialization")
    print("=" * 60)

    gx_root = Path(os.getenv("GX_ROOT_DIR", "/workspace/great_expectations"))
    gx_root.mkdir(parents=True, exist_ok=True)

    # Initialize context
    if (gx_root / "great_expectations.yml").exists():
        context = gx.get_context(context_root_dir=str(gx_root))
        print("[GX] Loaded existing context")
    else:
        context = gx.get_context(mode="file", project_root_dir=str(gx_root))
        print("[GX] Created new context")

    # Add data sources
    s3_endpoint = os.getenv("AWS_S3_ENDPOINT_URL", "http://minio:9000")
    s3_access_key = os.getenv("AWS_ACCESS_KEY_ID", "mlops-admin")
    s3_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY", "mlops-dev-password")
    s3_bucket = os.getenv("GE_DATASOURCE_DEFAULT_BUCKET", "mlops-data")

    # Add MinIO S3 data source
    if "minio_data" not in context.list_datasources():
        try:
            context.sources.add_pandas_s3(
                name="minio_data",
                bucket=s3_bucket,
                boto3_options={
                    "endpoint_url": s3_endpoint,
                    "aws_access_key_id": s3_access_key,
                    "aws_secret_access_key": s3_secret_key,
                }
            )
            print(f"[GX] Added MinIO S3 data source: {s3_bucket}")
        except Exception as e:
            print(f"[GX] Warning: Could not add S3 data source: {e}")

    # Add local filesystem data source
    if "local_data" not in context.list_datasources():
        try:
            context.sources.add_pandas_filesystem(
                name="local_data",
                base_directory="/workspace/data"
            )
            print("[GX] Added local filesystem data source")
        except Exception as e:
            print(f"[GX] Warning: Could not add local data source: {e}")

    # Create default expectation suites
    init_default_suites(context)

    print("=" * 60)
    print("Great Expectations initialized successfully!")
    print(f"Data sources: {context.list_datasources()}")
    print(f"Expectation suites: {context.list_expectation_suite_names()}")
    print("=" * 60)


if __name__ == "__main__":
    main()
