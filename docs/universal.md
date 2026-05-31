---

## `universal.py`

### Module Statistics

| Metric | Value |
|---|---|
| Functions | 0 |
| Classes | 1 |
| Methods | 3 |
| Imports | 4 |
| Lines | 64 |
| Doc Coverage | 0% |

### Imports

```python
import re
from pathlib import Path
from typing import Optional
from src.parser.base import BaseParser, ClassInfo, FunctionInfo, MethodInfo, ModuleInfo, ParseResult, Visibility
```

### Module-Level Variables

- `CLASS_PATTERN`
- `FUNC_PATTERN`

### Classes

#### `UniversalParser`

```python
class UniversalParser(BaseParser)
```

(public) | Lines 20-64

No description provided.

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
