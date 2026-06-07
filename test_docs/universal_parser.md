---

## `universal_parser.py`

### Module Statistics

| Metric | Value |
|---|---|
| Functions | 0 |
| Classes | 1 |
| Methods | 3 |
| Imports | 4 |
| Lines | 115 |
| Doc Coverage | 100% |

### Imports

```python
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

(public) | Lines 15-115

Fallback parser for non-Python languages using regular expressions.

<details>
<summary>Full Documentation</summary>

```
Fallback parser for non-Python languages using regular expressions.

Extracts basic structural information (classes and functions) from
languages like JavaScript, TypeScript, Go, Rust, Java, C++, etc.
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
