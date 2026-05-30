---

## `engine.py`

Scraping engine orchestrator.

### Module Statistics

| Metric | Value |
|---|---|
| Functions | 0 |
| Classes | 1 |
| Methods | 3 |
| Imports | 8 |
| Lines | 83 |
| Doc Coverage | 100% |

### Imports

```python
import asyncio
import json
import logging
from pathlib import Path
from typing import List, Optional
from github import GitHubScraper
from gitlab import GitLabScraper
from models import RepositoryMetadata
```

### Module-Level Variables

- `logger`

### Classes

#### `AsyncScraperEngine`

```python
class AsyncScraperEngine
```

(public) | Lines 18-83

Orchestrates asynchronous repository discovery and ingestion.

**Methods:**

| Method | Visibility | Static | Class Method |
|---|---|---|---|
| `ingest_repositories` | public | - | - |

##### `ingest_repositories`

```python
def ingest_repositories(platform: str, query: str, output_dir: Path, limit: int = 100, download_source: bool = True)
```

Main ingestion pipeline.

| Name | Type | Default |
|---|---|---|
| `platform` | `str` | - |
| `query` | `str` | - |
| `output_dir` | `Path` | - |
| `limit` | `int` | `100` |
| `download_source` | `bool` | `True` |
