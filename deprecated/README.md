# Deprecated Code

Code moved here during the lean architecture refactor.

## b2_client.py
Legacy Backblaze B2 client. Use `S3Client` from `data_transfer` instead - it works with MinIO, B2 (via S3 API), and AWS S3.

## services/zotero/
Zotero API server. Replaced by local paper notes in `knowledge/papers/notes/`.
