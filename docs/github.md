---

## `github.py`

GitHub scraper integration for CodeScribe.

### Module Statistics

| Metric | Value |
|---|---|
| Functions | 0 |
| Classes | 1 |
| Methods | 7 |
| Imports | 8 |
| Lines | 152 |
| Doc Coverage | 100% |

### Imports

```python
import asyncio
import json
import logging
from pathlib import Path
from typing import AsyncGenerator, List, Optional, Dict, Any
import aiohttp
import aiofiles
from models import RepositoryMetadata
```

### Module-Level Variables

- `logger`

### Classes

#### `GitHubScraper`

```python
class GitHubScraper
```

(public) | Lines 18-152

Handles asynchronous scraping of GitHub repositories.

**Methods:**

| Method | Visibility | Static | Class Method |
|---|---|---|---|
| `search_repositories` | public | - | - |
| `download_zipball` | public | - | - |

##### `search_repositories`

```python
def search_repositories(query: str, sort: str = 'stars', order: str = 'desc', limit: int = 100) -> AsyncGenerator[RepositoryMetadata, None]
```

Search for repositories on GitHub and yield metadata.

| Name | Type | Default |
|---|---|---|
| `query` | `str` | - |
| `sort` | `str` | `'stars'` |
| `order` | `str` | `'desc'` |
| `limit` | `int` | `100` |

**Returns:** `AsyncGenerator[RepositoryMetadata, None]`

##### `download_zipball`

```python
def download_zipball(repo: RepositoryMetadata, output_dir: Path) -> Optional[Path]
```

Download the repository zipball.

| Name | Type | Default |
|---|---|---|
| `repo` | `RepositoryMetadata` | - |
| `output_dir` | `Path` | - |

**Returns:** `Optional[Path]`
