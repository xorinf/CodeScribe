---

## `universal_parser.py`

universal_parser.py -- Regex-based Universal Parser.

Extracts basic class and function structures from non-Python languages
using regex. It handles keyword-based declarations (e.g., def, func, fn)
and C-family return-type-based declarations.

### Module Statistics

| Metric | Value |
|---|---|
| Functions | 0 |
| Classes | 1 |
| Methods | 3 |
| Imports | 5 |
| Lines | 84 |
| Doc Coverage | 100% |

### Imports

```python
from __future__ import annotations
import re
from pathlib import Path
from typing import Optional
from src.parser.base import BaseParser, ClassInfo, FunctionInfo, ModuleInfo, ParseResult, Visibility
```

### Classes

#### `UniversalParser`

```python
class UniversalParser(BaseParser)
```

(public) | Lines 24-84

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

No description provided.

**Returns:** `str`

##### `supported_extensions`

```python
def supported_extensions() -> list[str]
```

No description provided.

**Returns:** `list[str]`

##### `parse_file`

```python
def parse_file(file_path: Path) -> ModuleInfo
```

Parse a source file using regex heuristics.

| Name | Type | Default |
|---|---|---|
| `file_path` | `Path` | - |

**Returns:** `ModuleInfo`
