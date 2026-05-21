---

## `pipeline.py`

Data cleansing pipeline for CodeScribe.
Extracts files from zipballs, applies filters, and writes cleaned data to JSONL.

### Module Statistics

| Metric | Value |
|---|---|
| Functions | 0 |
| Classes | 1 |
| Methods | 3 |
| Imports | 7 |
| Lines | 100 |
| Doc Coverage | 100% |

### Imports

```python
import json
import logging
import zipfile
from pathlib import Path
from typing import List, Set
from heuristics import QualityFilter
from secrets import SecretScanner
```

### Module-Level Variables

- `logger`

### Classes

#### `CleanserPipeline`

```python
class CleanserPipeline
```

(public) | Lines 17-100

Orchestrates the extraction and cleansing of scraped repositories.

**Methods:**

| Method | Visibility | Static | Class Method |
|---|---|---|---|
| `process_directory` | public | - | - |

##### `process_directory`

```python
def process_directory(input_dir: Path, output_file: Path)
```

Process all zipballs in a directory and write to a JSONL file.

| Name | Type | Default |
|---|---|---|
| `input_dir` | `Path` | - |
| `output_file` | `Path` | - |
