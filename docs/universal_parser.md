---

## `universal_parser.py`

### Module Statistics

| Metric | Value |
|---|---|
| Functions | 0 |
| Classes | 1 |
| Methods | 4 |
| Imports | 4 |
| Lines | 84 |
| Doc Coverage | 100% |

### Imports

```python
from pathlib import Path
import re
from typing import Optional
from src.parser.base import BaseParser, ParseResult, ModuleInfo, FunctionInfo, ClassInfo, Visibility
```

### Classes

#### `UniversalParser`

```python
class UniversalParser(BaseParser)
```

(public) | Lines 15-84

Fallback parser for unsupported languages.

<details>
<summary>Full Documentation</summary>

```
Fallback parser for unsupported languages.

Uses regex heuristics to extract basic function and class definitions
from a variety of programming languages.
```

</details>

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
