---

## `universal_parser.py`

universal_parser.py -- Regex-based Universal Parser for Non-Python Languages.

This module provides a fallback parser for extracting basic structures
(functions, classes) from non-Python languages using regular expressions.
It handles both keyword-based declarations (e.g., def, func, fn) and
C-family return-type-based declarations.

### Module Statistics

| Metric | Value |
|---|---|
| Functions | 0 |
| Classes | 1 |
| Methods | 3 |
| Imports | 4 |
| Lines | 109 |
| Doc Coverage | 100% |

### Imports

```python
from __future__ import annotations
import re
from pathlib import Path
from src.parser.base import BaseParser, ClassInfo, FunctionInfo, ModuleInfo, ParseResult, Visibility
```

### Classes

#### `UniversalParser`

```python
class UniversalParser(BaseParser)
```

(public) | Lines 25-109

Fallback parser for non-Python languages.

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

Return the supported file extensions.

**Returns:** `list[str]`

##### `parse_file`

```python
def parse_file(file_path: Path) -> ModuleInfo
```

Parse a single source file into a ModuleInfo structure.

| Name | Type | Default |
|---|---|---|
| `file_path` | `Path` | - |

**Returns:** `ModuleInfo`
