---

## `universal.py`

Universal Regex-Based Parser.

A fallback parser that uses regular expressions to extract basic
class and function structures from unsupported languages.

### Module Statistics

| Metric | Value |
|---|---|
| Functions | 0 |
| Classes | 1 |
| Methods | 4 |
| Imports | 5 |
| Lines | 114 |
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

(public) | Lines 24-114

Regex-based parser for general programming languages.

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

Return supported file extensions.

**Returns:** `list[str]`

##### `parse_file`

```python
def parse_file(file_path: Path) -> ModuleInfo
```

Parse a file using regex to find classes and functions.

| Name | Type | Default |
|---|---|---|
| `file_path` | `Path` | - |

**Returns:** `ModuleInfo`
