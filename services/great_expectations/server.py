#!/usr/bin/env python3
"""
Great Expectations Data Validation Server
==========================================
Provides a web UI and REST API for data validation using Great Expectations.

Endpoints:
    GET  /                  - Dashboard home
    GET  /health            - Health check
    GET  /api/datasources   - List data sources
    GET  /api/expectations  - List expectation suites
    POST /api/validate      - Run validation
    GET  /api/results       - Get validation results
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List

from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS

# Great Expectations
try:
    import great_expectations as gx
    from great_expectations.data_context import FileDataContext
    GX_AVAILABLE = True
except ImportError:
    GX_AVAILABLE = False
    print("[Warning] Great Expectations not available")

# S3 integration
import boto3
from botocore.client import Config

app = Flask(__name__)
CORS(app)

# Configuration
GX_ROOT = Path(os.getenv("GX_ROOT_DIR", "/workspace/great_expectations"))
S3_ENDPOINT = os.getenv("AWS_S3_ENDPOINT_URL", "http://minio:9000")
S3_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID", "mlops-admin")
S3_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "mlops-dev-password")
S3_BUCKET = os.getenv("GE_DATASOURCE_DEFAULT_BUCKET", "mlops-data")

# Initialize Great Expectations context
context: Optional[FileDataContext] = None


def get_s3_client():
    """Get S3 client configured for MinIO."""
    return boto3.client(
        's3',
        endpoint_url=S3_ENDPOINT,
        aws_access_key_id=S3_ACCESS_KEY,
        aws_secret_access_key=S3_SECRET_KEY,
        config=Config(signature_version='s3v4'),
        region_name='us-east-1'
    )


def init_great_expectations():
    """Initialize Great Expectations data context."""
    global context

    if not GX_AVAILABLE:
        return None

    GX_ROOT.mkdir(parents=True, exist_ok=True)

    # Check if context already exists
    if (GX_ROOT / "great_expectations.yml").exists():
        context = gx.get_context(context_root_dir=str(GX_ROOT))
    else:
        # Create new context
        context = gx.get_context(mode="file", project_root_dir=str(GX_ROOT))

        # Add S3 data source for MinIO
        try:
            context.sources.add_pandas_s3(
                name="minio_data",
                bucket=S3_BUCKET,
                boto3_options={
                    "endpoint_url": S3_ENDPOINT,
                    "aws_access_key_id": S3_ACCESS_KEY,
                    "aws_secret_access_key": S3_SECRET_KEY,
                }
            )
            print(f"[GX] Added MinIO S3 data source: {S3_BUCKET}")
        except Exception as e:
            print(f"[GX] Failed to add S3 data source: {e}")

        # Add local filesystem data source
        try:
            context.sources.add_pandas_filesystem(
                name="local_data",
                base_directory="/workspace/data"
            )
            print("[GX] Added local filesystem data source")
        except Exception as e:
            print(f"[GX] Failed to add local data source: {e}")

    return context


# Dashboard HTML template
DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Great Expectations - Data Validation</title>
    <style>
        body { font-family: -apple-system, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { background: #1a1a2e; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .card { background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .card h3 { margin-top: 0; color: #1a1a2e; }
        .status { display: inline-block; padding: 4px 12px; border-radius: 4px; font-size: 12px; }
        .status-ok { background: #28a745; color: white; }
        .status-warning { background: #ffc107; color: black; }
        .status-error { background: #dc3545; color: white; }
        table { width: 100%; border-collapse: collapse; }
        th, td { text-align: left; padding: 12px; border-bottom: 1px solid #dee2e6; }
        th { background: #e9ecef; }
        .btn { padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; }
        .btn-primary { background: #007bff; color: white; }
        code { background: #e9ecef; padding: 2px 6px; border-radius: 4px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🔍 Great Expectations - Data Validation</h1>
        <p>Self-hosted data quality monitoring for MLOps</p>
    </div>

    <div class="card">
        <h3>📊 Data Sources</h3>
        <table>
            <tr><th>Name</th><th>Type</th><th>Status</th></tr>
            {% for ds in datasources %}
            <tr>
                <td><code>{{ ds.name }}</code></td>
                <td>{{ ds.type }}</td>
                <td><span class="status status-ok">Connected</span></td>
            </tr>
            {% endfor %}
        </table>
    </div>

    <div class="card">
        <h3>✅ Expectation Suites</h3>
        <table>
            <tr><th>Suite Name</th><th>Expectations</th><th>Last Run</th></tr>
            {% for suite in suites %}
            <tr>
                <td><code>{{ suite.name }}</code></td>
                <td>{{ suite.count }}</td>
                <td>{{ suite.last_run }}</td>
            </tr>
            {% endfor %}
            {% if not suites %}
            <tr><td colspan="3">No expectation suites defined. Create one via the API.</td></tr>
            {% endif %}
        </table>
    </div>

    <div class="card">
        <h3>🚀 Quick Start</h3>
        <p>Use the REST API to validate your data:</p>
        <pre><code>
# Validate a CSV file from MinIO
curl -X POST http://localhost:8084/api/validate \\
  -H "Content-Type: application/json" \\
  -d '{"datasource": "minio_data", "asset": "datasets/train.csv", "suite": "default"}'

# Create an expectation suite
curl -X POST http://localhost:8084/api/expectations \\
  -H "Content-Type: application/json" \\
  -d '{"name": "my_suite", "expectations": [{"type": "expect_column_to_exist", "column": "id"}]}'
        </code></pre>
    </div>

    <div class="card">
        <h3>📚 API Endpoints</h3>
        <table>
            <tr><th>Method</th><th>Endpoint</th><th>Description</th></tr>
            <tr><td>GET</td><td><code>/api/datasources</code></td><td>List data sources</td></tr>
            <tr><td>GET</td><td><code>/api/expectations</code></td><td>List expectation suites</td></tr>
            <tr><td>POST</td><td><code>/api/expectations</code></td><td>Create expectation suite</td></tr>
            <tr><td>POST</td><td><code>/api/validate</code></td><td>Run validation</td></tr>
            <tr><td>GET</td><td><code>/api/results</code></td><td>Get validation results</td></tr>
        </table>
    </div>
</body>
</html>
"""


@app.route('/')
def dashboard():
    """Render the dashboard."""
    datasources = []
    suites = []

    if context:
        # Get data sources
        for name in context.list_datasources():
            ds = context.get_datasource(name)
            datasources.append({
                "name": name,
                "type": type(ds).__name__,
            })

        # Get expectation suites
        for suite_name in context.list_expectation_suite_names():
            suite = context.get_expectation_suite(suite_name)
            suites.append({
                "name": suite_name,
                "count": len(suite.expectations) if hasattr(suite, 'expectations') else 0,
                "last_run": "Never"
            })

    return render_template_string(
        DASHBOARD_TEMPLATE,
        datasources=datasources,
        suites=suites
    )


@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "great-expectations",
        "gx_available": GX_AVAILABLE,
        "context_initialized": context is not None,
        "s3_endpoint": S3_ENDPOINT,
    })


@app.route('/api/datasources')
def list_datasources():
    """List configured data sources."""
    if not context:
        return jsonify({"error": "Context not initialized"}), 500

    datasources = []
    for name in context.list_datasources():
        ds = context.get_datasource(name)
        datasources.append({
            "name": name,
            "type": type(ds).__name__,
        })

    return jsonify({"datasources": datasources})


@app.route('/api/expectations', methods=['GET'])
def list_expectations():
    """List expectation suites."""
    if not context:
        return jsonify({"error": "Context not initialized"}), 500

    suites = []
    for suite_name in context.list_expectation_suite_names():
        suite = context.get_expectation_suite(suite_name)
        suites.append({
            "name": suite_name,
            "expectation_count": len(suite.expectations) if hasattr(suite, 'expectations') else 0,
        })

    return jsonify({"suites": suites})


@app.route('/api/expectations', methods=['POST'])
def create_expectation_suite():
    """Create a new expectation suite."""
    if not context:
        return jsonify({"error": "Context not initialized"}), 500

    data = request.json
    suite_name = data.get("name")
    expectations = data.get("expectations", [])

    if not suite_name:
        return jsonify({"error": "Suite name required"}), 400

    try:
        suite = context.add_expectation_suite(suite_name)

        # Add expectations
        for exp in expectations:
            exp_type = exp.get("type")
            exp_kwargs = {k: v for k, v in exp.items() if k != "type"}

            if hasattr(suite, exp_type):
                getattr(suite, exp_type)(**exp_kwargs)

        context.save_expectation_suite(suite)

        return jsonify({
            "success": True,
            "suite": suite_name,
            "expectations_added": len(expectations)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/validate', methods=['POST'])
def validate_data():
    """Run validation on a data asset."""
    if not context:
        return jsonify({"error": "Context not initialized"}), 500

    data = request.json
    datasource = data.get("datasource")
    asset = data.get("asset")
    suite_name = data.get("suite", "default")

    if not datasource or not asset:
        return jsonify({"error": "datasource and asset required"}), 400

    try:
        # Get batch request
        batch_request = context.get_datasource(datasource).get_asset(asset).build_batch_request()

        # Create validator
        validator = context.get_validator(
            batch_request=batch_request,
            expectation_suite_name=suite_name
        )

        # Run validation
        results = validator.validate()

        return jsonify({
            "success": results.success,
            "statistics": {
                "evaluated_expectations": results.statistics.get("evaluated_expectations", 0),
                "successful_expectations": results.statistics.get("successful_expectations", 0),
                "unsuccessful_expectations": results.statistics.get("unsuccessful_expectations", 0),
                "success_percent": results.statistics.get("success_percent", 0),
            },
            "run_id": str(results.run_id) if hasattr(results, 'run_id') else None,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/results')
def get_results():
    """Get validation results history."""
    if not context:
        return jsonify({"error": "Context not initialized"}), 500

    # List validation results from GX store
    results_dir = GX_ROOT / "uncommitted" / "validations"
    results = []

    if results_dir.exists():
        for result_file in sorted(results_dir.glob("**/*.json"), reverse=True)[:20]:
            try:
                result_data = json.loads(result_file.read_text())
                results.append({
                    "file": str(result_file.relative_to(results_dir)),
                    "success": result_data.get("success"),
                    "run_time": result_data.get("meta", {}).get("run_id", {}).get("run_time"),
                })
            except Exception:
                pass

    return jsonify({"results": results})


def main():
    """Start the Great Expectations server."""
    print("=" * 60)
    print("Great Expectations Data Validation Server")
    print("=" * 60)
    print(f"GX Root: {GX_ROOT}")
    print(f"S3 Endpoint: {S3_ENDPOINT}")
    print(f"S3 Bucket: {S3_BUCKET}")
    print("-" * 60)

    # Initialize Great Expectations
    init_great_expectations()

    if context:
        print(f"[GX] Context initialized successfully")
        print(f"[GX] Data sources: {context.list_datasources()}")
    else:
        print("[GX] Warning: Context not initialized")

    print("=" * 60)
    print("Server starting at http://0.0.0.0:8084")
    print("=" * 60)

    app.run(host='0.0.0.0', port=8084, debug=False)


if __name__ == "__main__":
    main()
