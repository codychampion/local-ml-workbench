"""
Data Transfer Module
====================
Handles cloud storage operations with rate limiting and security features.

Phase 1: Mocked implementation using local files
Phase 2/3: Full B2 integration with encryption
"""

from .b2_client import B2Client, MockedB2Client

__all__ = ["B2Client", "MockedB2Client"]
