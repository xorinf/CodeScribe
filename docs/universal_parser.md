---

## `universal_parser.py`

Universal Parser for multi-language support using regex.

This parser provides a fallback mechanism to extract basic class and function
structures from languages other than Python.

### Module Statistics

| Metric | Value |
|---|---|
| Functions | 0 |
| Classes | 1 |
| Methods | 3 |
| Imports | 4 |
| Lines | 117 |
| Doc Coverage | 100% |

### Imports

```python
import re
from pathlib import Path
from typing import Optional
from src.parser.base import BaseParser, ClassInfo, FunctionInfo, ModuleInfo, Visibility
```

### Classes

#### `UniversalParser`

```python
class UniversalParser(BaseParser)
```

(public) | Lines 21-117

Regex-based parser for multiple programming languages.

<details>
<summary>Full Documentation</summary>

```
Regex-based parser for multiple programming languages.

Extracts class and function definitions using heuristics and regular expressions.
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

Parse a source file using regular expressions.

| Name | Type | Default |
|---|---|---|
| `file_path` | `Path` | - |

**Returns:** `ModuleInfo`
