# Great Expectations Data Validation Service
FROM python:3.11-slim

WORKDIR /workspace

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Great Expectations and dependencies
RUN pip install --no-cache-dir \
    great_expectations>=0.18.0 \
    boto3>=1.34.0 \
    s3fs>=2024.2.0 \
    pandas>=2.0.0 \
    pyarrow>=15.0.0 \
    flask>=3.0.0 \
    flask-cors>=4.0.0 \
    pyyaml>=6.0

# Create non-root user
RUN useradd -m -u 1000 mlops
RUN mkdir -p /workspace/great_expectations && chown -R mlops:mlops /workspace

USER mlops

# Copy service files
COPY --chown=mlops:mlops services/great_expectations/server.py /workspace/server.py
COPY --chown=mlops:mlops services/great_expectations/init_gx.py /workspace/init_gx.py

EXPOSE 8084

CMD ["python", "/workspace/server.py"]
