# Dataset Manifest System

Comprehensive tracking for collections and annotations with knowledge base integration.

## Overview

The manifest system provides **data provenance** and **traceability** for your ML datasets:

- **Collections** = Raw data downloads (e.g., images from Reddit)
- **Annotations** = Processing runs on collections (e.g., captions from BLIP)

**Key Feature:** One collection can have **multiple annotation datasets** (e.g., BLIP captions vs GPT-4V captions).

## Architecture

```
Collection (Reddit scrape)
├── collection_manifest.json       ← Metadata + git state
├── image1.jpg
├── image2.jpg
│
├── Annotation 1 (BLIP-base captions)
│   ├── annotation_manifest.json   ← Links to parent collection
│   ├── image1.txt
│   └── image2.txt
│
└── Annotation 2 (BLIP2-opt captions)
    ├── annotation_manifest.json   ← Links to same parent
    ├── image1.txt
    └── image2.txt
```

## Manifest Format

### Collection Manifest

```json
{
  "id": "col-20251221-a1b2c3d4",
  "type": "collection",
  "version": "1.0",
  "created_at": "2025-12-21T10:30:00",

  "source": {
    "type": "reddit",
    "url": "https://reddit.com/r/earthporn/top",
    "metadata": {
      "subreddit": "earthporn",
      "limit": 100,
      "sort": "top",
      "time_range": "week"
    }
  },

  "storage": {
    "path": "/workspace/data/collected/earthporn",
    "total_files": 102,
    "images": 95,
    "videos": 7
  },

  "git": {
    "commit": "abc123...",
    "commit_short": "abc123",
    "branch": "main",
    "dirty": false
  },

  "annotations": [
    {
      "id": "ann-20251221-x9y8z7",
      "type": "caption",
      "model": "blip-base",
      "path": "/workspace/data/collected/earthporn",
      "created_at": "2025-12-21T11:00:00"
    }
  ]
}
```

### Annotation Manifest

```json
{
  "id": "ann-20251221-x9y8z7",
  "type": "annotation",
  "version": "1.0",
  "created_at": "2025-12-21T11:00:00",

  "collection": {
    "id": "col-20251221-a1b2c3d4",
    "path": "/workspace/data/collected/earthporn"
  },

  "annotation": {
    "type": "caption",
    "model": "blip-base",
    "metadata": {
      "total_processed": 95,
      "successful": 93,
      "failed": 2,
      "output_format": "txt",
      "device": "cuda"
    }
  },

  "storage": {
    "path": "/workspace/data/collected/earthporn",
    "annotation_files": 93
  },

  "git": {
    "commit": "def456...",
    "commit_short": "def456",
    "branch": "main",
    "dirty": false
  }
}
```

## Usage

### Automatic Creation

Manifests are **automatically created** when you run pipelines:

```bash
# Collect data → creates collection_manifest.json
docker-compose run --rm collect python -m pipelines.collect.collect \
    --subreddit earthporn --limit 100

# Caption images → creates annotation_manifest.json + updates parent
docker-compose run --rm annotate python -m pipelines.annotate.caption \
    --input-dir ./data/collected/earthporn \
    --model blip-base
```

### Programmatic Access

```python
from utils.manifest import (
    create_collection_manifest,
    create_annotation_manifest,
    load_collection_manifest,
    find_all_collections,
    get_collection_tree
)

# Create collection manually
manifest = create_collection_manifest(
    output_dir="./data/my-dataset",
    source="filesystem",
    source_url="file:///data/external",
    metadata={"description": "Imported dataset"}
)

# Load existing collection
collection = load_collection_manifest("./data/collected/earthporn")
print(f"Collection {collection['id']} has {collection['storage']['images']} images")

# Find all collections
collections = find_all_collections(root_dir="./data")
for col in collections:
    print(f"{col['id']}: {col['source']['type']}")

# Get hierarchical view
tree = get_collection_tree(root_dir="./data")
for col_id, data in tree.items():
    print(f"Collection: {col_id}")
    for ann in data["annotations"]:
        print(f"  └─ {ann['annotation']['model']}")
```

### CLI Tools

```bash
# List all collections and annotations
python -m utils.manifest list --root ./data

# Show collection hierarchy
python -m utils.manifest tree --root ./data
```

## Knowledge Base Integration

Export manifests to Obsidian/Khoj-compatible markdown:

```bash
# Sync all sources (includes collections + annotations)
python -m utils.knowledge_sync

# Sync only collections
python -m utils.knowledge_sync --source collections

# Sync only annotations
python -m utils.knowledge_sync --source annotations

# Watch for changes
python -m utils.knowledge_sync --watch --interval 60
```

This creates:

```
knowledge/
├── collections/
│   └── col-20251221-a1b2c3d4.md
└── annotations/
    ├── ann-20251221-x9y8z7.md  (BLIP-base)
    └── ann-20251221-p8q9r0.md  (BLIP2-opt)
```

### Markdown Format

**Collection markdown:**

```markdown
---
type: collection
collection_id: "col-20251221-a1b2c3d4"
source_type: "reddit"
total_images: 95
tags:
  - collection
  - reddit
  - auto-generated
---

# Collection: col-20251221-a1b2c3d4

**Source:** reddit - https://reddit.com/r/earthporn/top

## Contents
- **Images:** 95
- **Videos:** 7

## Annotations
- `ann-20251221-x9y8z7`: caption using **blip-base** (2025-12-21T11:00:00)
- `ann-20251221-p8q9r0`: caption using **blip2-opt-2.7b** (2025-12-21T14:30:00)

## Usage
```bash
# Caption this collection
docker-compose run --rm annotate python -m pipelines.annotate.caption \
    --input-dir ./data/collected/earthporn \
    --model blip-base
```
```

**Annotation markdown:**

```markdown
---
type: annotation
annotation_id: "ann-20251221-x9y8z7"
collection_id: "col-20251221-a1b2c3d4"
annotation_type: "caption"
model: "blip-base"
---

# Annotation: ann-20251221-x9y8z7

**Model:** `blip-base`

## Parent Collection
**Collection ID:** `col-20251221-a1b2c3d4`

See: [[col-20251221-a1b2c3d4]]

## Metadata
- **total_processed**: `95`
- **successful**: `93`
- **failed**: `2`

## Usage
```bash
# Train on this dataset
docker-compose run --rm train python -m pipelines.train.finetune \
    --dataset ./data/collected/earthporn \
    --epochs 3
```
```

## Multiple Annotations Example

```bash
# Collect once
docker-compose run --rm collect python -m pipelines.collect.collect \
    --subreddit earthporn --limit 50
# → Creates: col-20251221-a1b2c3d4

# Caption with BLIP-base
docker-compose run --rm annotate python -m pipelines.annotate.caption \
    --input-dir ./data/collected/earthporn \
    --model blip-base
# → Creates: ann-20251221-x9y8z7 (linked to col-20251221-a1b2c3d4)

# Caption with BLIP2 (same images, different model)
docker-compose run --rm annotate python -m pipelines.annotate.caption \
    --input-dir ./data/collected/earthporn \
    --model blip2-opt-2.7b
# → Creates: ann-20251221-p8q9r0 (also linked to col-20251221-a1b2c3d4)

# Now the collection manifest shows both annotations
cat ./data/collected/earthporn/collection_manifest.json
# "annotations": [
#   {"id": "ann-20251221-x9y8z7", "model": "blip-base"},
#   {"id": "ann-20251221-p8q9r0", "model": "blip2-opt-2.7b"}
# ]
```

## Git Traceability

Every manifest captures the **exact git state** when created:

- **Commit hash** - Exact code version
- **Branch** - Which branch was active
- **Dirty flag** - Whether working directory had uncommitted changes
- **Commit URL** - Direct link to GitHub commit

This ensures **full reproducibility**:

```bash
# From manifest git.commit field
git checkout abc123def456

# Reproduce exact collection
docker-compose run --rm collect python -m pipelines.collect.collect \
    --subreddit earthporn --limit 100
```

## Benefits

1. **Data Lineage** - Track where data came from
2. **Reproducibility** - Git hash links code → data
3. **Multiple Annotations** - Compare different models on same data
4. **Knowledge Base** - Searchable markdown in Obsidian/Khoj
5. **Audit Trail** - When/how datasets were created
6. **Relationship Mapping** - Collections ↔ Annotations ↔ Training runs

## File Locations

| File | Location | Purpose |
|------|----------|---------|
| `collection_manifest.json` | Collection directory | Metadata + annotations list |
| `annotation_manifest.json` | Annotation directory | Metadata + parent link |
| `utils/manifest.py` | Codebase | Manifest creation/loading |
| `utils/knowledge_sync.py` | Codebase | Markdown export |
| `knowledge/collections/` | Knowledge base | Collection markdown files |
| `knowledge/annotations/` | Knowledge base | Annotation markdown files |

## Best Practices

1. **Never delete manifests** - They're your audit trail
2. **Use knowledge sync regularly** - Keep Obsidian up-to-date
3. **Check git state** - Commit before collecting data
4. **Name collections descriptively** - Use meaningful subreddit/source names
5. **Document annotation settings** - Record model params in metadata

## Integration with Existing Tools

### AIM Experiments

Link experiments to annotations:

```python
from aim import Run
from utils.manifest import load_annotation_manifest

run = Run()
annotation = load_annotation_manifest("./data/collected/earthporn")
run["annotation_id"] = annotation["id"]
run["collection_id"] = annotation["collection"]["id"]
```

### FiftyOne Datasets

Reference manifests in dataset metadata:

```python
import fiftyone as fo
from utils.manifest import load_collection_manifest

manifest = load_collection_manifest("./data/collected/earthporn")
dataset = fo.Dataset("earthporn")
dataset.info = {
    "collection_id": manifest["id"],
    "source": manifest["source"]
}
```

### DVC Pipelines

Track manifest IDs in `dvc.yaml`:

```yaml
stages:
  caption:
    cmd: python -m pipelines.annotate.caption --input-dir data/collected/earthporn
    deps:
      - data/collected/earthporn/collection_manifest.json
    outs:
      - data/collected/earthporn/annotation_manifest.json
```

## Troubleshooting

**Q: Collection manifest not created?**
```bash
# Create manually
python -c "from utils import create_collection_manifest; create_collection_manifest(
    output_dir='./data/my-dataset',
    source='filesystem',
    source_url='file:///data/external'
)"
```

**Q: Annotation not linked to parent?**
```bash
# Annotation manifest needs collection_path parameter
# Check caption.py line 351 - should pass collection_path=args.input_dir
```

**Q: Knowledge sync not finding manifests?**
```bash
# Check DATA_DIR environment variable
export DATA_DIR=./data
python -m utils.knowledge_sync --source collections
```

## See Also

- [Knowledge Base Sync](../utils/knowledge_sync.py)
- [Manifest Utilities](../utils/manifest.py)
- [Collection Pipeline](../pipelines/collect/collect.py)
- [Annotation Pipeline](../pipelines/annotate/caption.py)
