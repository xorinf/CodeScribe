---

## `universal_parser.py`

universal_parser.py -- Universal Regex-based Parser for Non-Python Languages.

Acts as a fallback to extract basic class and function structures from
non-Python languages using regular expressions.

### Module Statistics

| Metric | Value |
|---|---|
| Functions | 0 |
| Classes | 1 |
| Methods | 3 |
| Imports | 4 |
| Lines | 73 |
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

(public) | Lines 23-73

Fallback parser for multiple languages using regular expressions.

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

No description provided.

| Name | Type | Default |
|---|---|---|
| `file_path` | `Path` | - |

**Returns:** `ModuleInfo`
