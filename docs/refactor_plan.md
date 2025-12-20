# MLOps Workbench Refactor Plan

**Goal:** Lean, graph-first architecture with Obsidian as local vault, Khoj as chat interface, MinIO as core storage, dockerized pipelines, and on-demand UIs.

## Target Architecture Summary

### Always-On (default `docker compose up`)
- `minio` + `minio-init` — S3-compatible storage (core)

### Profile-Based Services (opt-in)
| Profile | Services | Description |
|---------|----------|-------------|
| `chat` | khoj, postgres (pgvector) | AI chat over code/notes/papers |
| `cv_ui` | fiftyone, mongodb | CV dataset visualization |
| `labeling` | label-studio | Image/text annotation |
| `tracking` | aim | Experiment tracking UI |
| `registry` | registry:2 | Local docker registry for model images |
| `pipeline` | collect, annotate, train, evaluate, infer | ML pipeline containers |
| `dev` | dev | Interactive development shell |
| `test` | test, test-quick | Integration tests |

---

## Inventory: Services

### REMOVE (Default docker-compose)

| Service | Current File/Line | Reason | Migration Path |
|---------|-------------------|--------|----------------|
| `vault` | docker-compose.yml:253-278 | Over-engineered for solo use | Use `.env` vars directly |
| `prefect-server` | docker-compose.yml:286-310 | Unused server, flows run locally | Keep `@flow`/`@task` decorators, run CLI |
| `litellm` | docker-compose.yml:316-345 | Gateway unnecessary for direct API calls | Use provider APIs directly via env vars |
| `obsidian-couchdb` | docker-compose.yml:397-420 | Obsidian is local app, not service | Obsidian reads `./knowledge/` directly |
| `obsidian-init` | docker-compose.yml:423-435 | No longer needed | Remove |
| `zotero` | docker-compose.yml:438-465 | Container overhead for simple use case | Local file-based paper notes in vault |
| `redis` | docker-compose.yml:134-151 | Only used by JuiceFS (not active) | Remove unless proven needed |

### KEEP (Reorganize into profiles)

| Service | Current Location | New Profile | Notes |
|---------|------------------|-------------|-------|
| `minio` | docker-compose.yml:61-87 | (default) | Core storage |
| `minio-init` | docker-compose.yml:90-107 | (default) | Bucket init |
| `mongodb` | docker-compose.yml:110-131 | `cv_ui` | FiftyOne backend |
| `postgres` | docker-compose.yml:154-176 | `chat` | Khoj pgvector backend |
| `aim` | docker-compose.yml:182-207 | `tracking` | Experiment tracking |
| `label-studio` | docker-compose.yml:213-247 | `labeling` | Annotation |
| `khoj` | docker-compose.yml:355-394 | `chat` | AI search/chat |
| `fiftyone` | docker-compose.yml:471-510 | `cv_ui` | Dataset viz |
| `collect` | docker-compose.yml:517-547 | `pipeline` | Already profiled |
| `annotate` | docker-compose.yml:550-585 | `pipeline` | Already profiled |
| `train` | docker-compose.yml:588-623 | `pipeline` | Already profiled |
| `evaluate` | docker-compose.yml:626-663 | `pipeline` | Already profiled |
| `infer` | docker-compose.yml:666-704 | `pipeline` | Already profiled |
| `dev` | docker-compose.yml:710-748 | `dev` | Already profiled |
| `test`/`test-quick` | docker-compose.yml:760-844 | `test` | Already profiled |

### ADD (New services)

| Service | Profile | Description |
|---------|---------|-------------|
| `registry` | `registry` | Local Docker registry (registry:2) for model images |

---

## Inventory: Volumes

### REMOVE
| Volume | Reason |
|--------|--------|
| `redis-data` | Redis removed |
| `prefect-data` | Prefect server removed |
| `obsidian-vault` | No longer needed (local folder) |
| `couchdb-data` | CouchDB removed |
| `zotero-data` | Zotero container removed |
| `zotero-storage` | Zotero container removed |

### KEEP
| Volume | Used By |
|--------|---------|
| `minio-data` | minio |
| `mongodb-data` | fiftyone |
| `postgres-data` | khoj |
| `aim-data` | aim |
| `label-studio-data` | label-studio |
| `fiftyone-data` | fiftyone |
| `huggingface-cache` | pipeline containers |
| `khoj-data` | khoj |

### ADD
| Volume | Used By |
|--------|---------|
| `registry-data` | docker registry |

---

## Inventory: Python Modules

### utils/

| File | Status | Changes |
|------|--------|---------|
| `__init__.py` | MODIFY | Remove vault exports from default, keep as optional |
| `vault.py` | MODIFY | Make optional: env-vars first, Vault only if `VAULT_ADDR` set |
| `storage.py` | MODIFY | Remove Vault dependency, use env vars directly |
| `model_registry.py` | MODIFY | Add Docker image registry support |
| `aim_ingestion.py` | KEEP | Already good, minor path updates |
| `hydra_aim.py` | KEEP | No changes |
| `knowledge_sync.py` | REVIEW | May need updates for new knowledge structure |

### data_transfer/

| File | Status | Changes |
|------|--------|---------|
| `s3_client.py` | KEEP | Core, no changes needed |
| `b2_client.py` | DEPRECATE | Move to `deprecated/`, remove usage |
| `__init__.py` | MODIFY | Remove B2Client export |

### hooks/

| File | Status | Changes |
|------|--------|---------|
| `summarize_pr.py` | KEEP | No changes |

### pipelines/

| File | Status | Changes |
|------|--------|---------|
| All Dockerfiles | MODIFY | Remove VAULT_* env vars |
| `train/train_lora.py` | MODIFY | Replace B2Client with S3Client |
| Other pipeline scripts | REVIEW | Check for B2/Vault usage |

### services/

| Directory | Status | Changes |
|-----------|--------|---------|
| `zotero/` | DEPRECATE | Move to `deprecated/` |
| `fiftyone/` | KEEP | No changes |

### config.py

| Status | Changes |
|--------|---------|
| REVIEW | Check for Vault/LiteLLM references |

---

## Inventory: Configuration Files

### conf/

| File | Status | Changes |
|------|--------|---------|
| `config.yaml` | KEEP | No changes |
| `infrastructure/default.yaml` | MODIFY | Remove vault, litellm, juicefs sections; remove B2 section |
| `pipeline/*.yaml` | KEEP | No changes |
| `experiment/*.yaml` | KEEP | No changes |

### docker/

| Directory | Status | Changes |
|-----------|--------|---------|
| `base/` | KEEP | No changes |
| `litellm/` | REMOVE | Delete entirely |
| `init-scripts/` | KEEP | Review for Vault usage |

---

## Inventory: Tests

### tests/integration/

| File | Status | Changes |
|------|--------|---------|
| `conftest.py` | MODIFY | Remove VAULT_HOST, LITELLM_HOST, COUCHDB_HOST, ZOTERO_HOST, PREFECT_HOST, REDIS_HOST, GE_HOST, CVAT_HOST, SPOTLIGHT_HOST, COMFYUI_HOST |
| `test_services_health.py` | MODIFY | Remove tests for: vault, litellm, couchdb, zotero, prefect, redis, great_expectations, cvat, spotlight, comfyui |
| `test_minio_integration.py` | KEEP | Core tests |
| `test_mlops_services.py` | MODIFY | Remove vault/prefect tests |
| `test_knowledge_stack.py` | MODIFY | Remove zotero, couchdb tests; keep khoj tests |

---

## New Files to Create

### scripts/ (Glue Scripts)

| File | Purpose |
|------|---------|
| `scripts/new_experiment.py` | Create experiment plan note, return exp_id |
| `scripts/ingest_aim_run.py` | Takes run_id or "latest", writes markdown summary |
| `scripts/dataset_card_from_manifest.py` | Generate dataset card from manifest file |
| `scripts/labelstudio_sync.py` | FiftyOne <-> Label Studio sync |
| `scripts/register_model_image.py` | Build/tag/push model image to registry, write note |

### knowledge/ (Standardized Structure)

```
knowledge/
├── .obsidian/              # Obsidian config (gitignored internals)
├── topics/                 # General topic notes
├── papers/
│   ├── pdfs/              # PDF storage (gitignored)
│   └── notes/             # Paper notes (markdown)
├── datasets/
│   ├── cards/             # Dataset cards
│   └── manifests/         # Dataset manifests (json/yaml)
├── experiments/
│   ├── plans/             # Experiment plan notes
│   └── runs/              # Run summary notes (auto-generated)
├── models/
│   └── registry/          # Model registry notes
│       └── README.md      # Registry index
└── templates/             # Keep existing + add new
    ├── paper-note.md
    ├── dataset-card.md
    ├── experiment-plan.md
    ├── run-summary.md
    └── model-registry.md
```

### .env.example (Enhanced)

Add documentation for all env vars, remove Vault defaults.

---

## Implementation Order

### Phase 1: Compose Refactor + Core Cleanup
1. Create new `docker-compose.yml` with profiles
2. Create `.env.example` with full documentation
3. Remove Vault, Redis, Prefect, LiteLLM, CouchDB, Zotero from compose
4. Add docker registry service under `registry` profile

### Phase 2: Secrets Simplification
1. Modify `utils/vault.py` to be env-first, Vault optional
2. Modify `utils/storage.py` to not require Vault
3. Update `utils/__init__.py` exports
4. Update `conf/infrastructure/default.yaml`
5. Remove Vault env vars from pipeline Dockerfiles

### Phase 3: Dead Code Removal
1. Move `data_transfer/b2_client.py` to `deprecated/`
2. Move `services/zotero/` to `deprecated/`
3. Delete `docker/litellm/`
4. Update `data_transfer/__init__.py`
5. Update pipeline scripts to use S3Client instead of B2Client
6. Remove `.b2_local_manifest.json`

### Phase 4: Knowledge Structure
1. Create new knowledge folder structure
2. Add new templates
3. Update `utils/aim_ingestion.py` to use new paths
4. Update existing templates to match new structure

### Phase 5: Glue Scripts
1. Create `scripts/` directory
2. Implement `new_experiment.py`
3. Implement `ingest_aim_run.py`
4. Implement `dataset_card_from_manifest.py`
5. Implement `labelstudio_sync.py`
6. Implement `register_model_image.py`

### Phase 6: Test Updates
1. Update `tests/conftest.py`
2. Update `tests/integration/test_services_health.py`
3. Update other integration tests
4. Ensure tests only require services from their profile

### Phase 7: Documentation
1. Update `README.md` with new lean workflow
2. Update `CLAUDE.md` with new architecture
3. Create `docs/architecture.md`
4. Create `docs/workflow.md`
5. Add migration notes for removed services

---

## Validation Checklist

After refactor, verify:

- [ ] `docker compose up -d` starts only MinIO
- [ ] `docker compose --profile chat up -d` starts Khoj + Postgres
- [ ] `docker compose --profile cv_ui up -d` starts FiftyOne + MongoDB
- [ ] `docker compose --profile labeling up -d` starts Label Studio
- [ ] `docker compose --profile tracking up -d` starts AIM
- [ ] `docker compose --profile registry up -d` starts Docker registry
- [ ] `docker compose --profile pipeline run --rm train ...` works
- [ ] Khoj can index `./knowledge/` folder
- [ ] AIM logs experiments to `./outputs/aim/`
- [ ] `scripts/ingest_aim_run.py` creates markdown in knowledge
- [ ] `scripts/register_model_image.py` pushes to local registry
- [ ] No Vault dependency for basic operation
- [ ] No Redis, Prefect server, LiteLLM, CouchDB, Zotero containers
- [ ] All tests pass with appropriate profiles

---

## Files to Delete (Summary)

```
docker/litellm/                    # LiteLLM config
services/zotero/                   # Zotero API server (move to deprecated/)
.b2_local_manifest.json           # B2 mock manifest
```

## Files to Archive (deprecated/)

```
deprecated/
├── b2_client.py                  # Legacy B2 client
├── services/zotero/              # Zotero server
└── README.md                     # Explanation of deprecated code
```

## Environment Variables (New Standard)

```bash
# Core (required)
S3_ENDPOINT=http://minio:9000
S3_ACCESS_KEY=mlops-admin
S3_SECRET_KEY=mlops-dev-password
S3_REGION=us-east-1

# Khoj (for chat profile)
KHOJ_ADMIN_EMAIL=admin@mlops.local
KHOJ_ADMIN_PASSWORD=mlops-dev-password
POSTGRES_USER=mlops
POSTGRES_PASSWORD=mlops_dev_password

# Model Provider API Keys (optional, for Khoj chat)
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
OLLAMA_HOST=http://host.docker.internal:11434

# AIM (for tracking)
AIM_REPO=./outputs/aim

# Docker Registry (for registry profile)
REGISTRY_HOST=localhost:5000

# Feature flags
VAULT_ADDR=  # Empty = disabled, set to enable optional Vault
```
