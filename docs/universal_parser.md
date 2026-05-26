---

## `universal_parser.py`

### Module Statistics

| Metric | Value |
|---|---|
| Functions | 0 |
| Classes | 1 |
| Methods | 3 |
| Imports | 3 |
| Lines | 39 |
| Doc Coverage | 0% |

### Imports

```python
from pathlib import Path
import re
from src.parser.base import BaseParser, ModuleInfo, ClassInfo, FunctionInfo
```

### Classes

#### `UniversalParser`

```python
class UniversalParser(BaseParser)
```

(public) | Lines 6-39

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
