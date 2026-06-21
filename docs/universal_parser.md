---

## `universal_parser.py`

Universal fallback parser for non-Python languages using regex.
Extracts basic structures like classes and functions.

### Module Statistics

| Metric | Value |
|---|---|
| Functions | 0 |
| Classes | 1 |
| Methods | 4 |
| Imports | 4 |
| Lines | 92 |
| Doc Coverage | 100% |

### Imports

```python
from __future__ import annotations
import re
from pathlib import Path
from src.parser.base import BaseParser, ClassInfo, FunctionInfo, ModuleInfo
```

### Classes

#### `UniversalParser`

```python
class UniversalParser(BaseParser)
```

(public) | Lines 19-92

Regex-based parser for fallback language support.

**Methods:**

| Method | Visibility | Static | Class Method |
|---|---|---|---|
| `language` | public | - | - |
| `supported_extensions` | public | - | - |
| `parse_file` | public | - | - |

##### `language`

```python
def language() -> str
```

Return the language identifier.

**Returns:** `str`

##### `supported_extensions`

```python
def supported_extensions() -> list[str]
```

Return the file extensions this parser can handle.

**Returns:** `list[str]`

##### `parse_file`

```python
def parse_file(file_path: Path) -> ModuleInfo
```

Parse a single source file using heuristics.

| Name | Type | Default |
|---|---|---|
| `file_path` | `Path` | - |

**Returns:** `ModuleInfo`
