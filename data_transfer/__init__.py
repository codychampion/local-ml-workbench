"""
Data Transfer Module - S3-Compatible Storage
=============================================
Works with MinIO locally and any S3-compatible storage in production.
"""

try:
    from .s3_client import S3Client, S3Config, S3Object, get_s3_client
    S3_AVAILABLE = True
except ImportError:
    S3Client = S3Config = S3Object = get_s3_client = None
    S3_AVAILABLE = False

__all__ = ["S3Client", "S3Config", "S3Object", "get_s3_client", "S3_AVAILABLE"]
