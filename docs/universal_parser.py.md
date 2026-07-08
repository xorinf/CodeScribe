---

## `universal_parser.py`

universal_parser.py -- Universal Regex-based Parser.

Provides a fallback parser that uses regular expressions to extract
basic code structures (classes, functions) from languages that do not
have a dedicated AST parser implemented yet.

### Module Statistics

| Metric | Value |
|---|---|
| Functions | 0 |
| Classes | 1 |
| Methods | 4 |
| Imports | 4 |
| Lines | 115 |
| Doc Coverage | 100% |

### Imports

```python
import re
from pathlib import Path
from typing import Optional
from src.parser.base import BaseParser, ClassInfo, FunctionInfo, MethodInfo, ModuleInfo, Visibility
```

### Classes

#### `UniversalParser`

```python
class UniversalParser(BaseParser)
```

(public) | Lines 23-115

Regex-based parser for non-Python languages.

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
