---

## `universal_parser.py`

### Module Statistics

| Metric | Value |
|---|---|
| Functions | 0 |
| Classes | 1 |
| Methods | 3 |
| Imports | 4 |
| Lines | 61 |
| Doc Coverage | 100% |

### Imports

```python
import re
from pathlib import Path
from typing import Optional
from src.parser.base import BaseParser, ParseResult, ModuleInfo, ClassInfo, FunctionInfo, Visibility
```

### Classes

#### `UniversalParser`

```python
class UniversalParser(BaseParser)
```

(public) | Lines 7-61

Regex-based fallback parser for non-Python languages.

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
