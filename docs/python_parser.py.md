---

## `python_parser.py`

python_parser.py -- Concrete AST Parser for Python Source Files.

Uses Python's built-in `ast` module to parse source files into Abstract
Syntax Trees, then walks the tree to extract structured information
(functions, classes, methods, imports, docstrings, type hints) and
maps them onto the data models defined in base.py.

Supported Python features:
    - Module-level docstrings
    - Import and ImportFrom statements
    - Function definitions with parameters, type hints, decorators
    - Class definitions with base classes, methods, decorators
    - Visibility detection (public vs private via underscore convention)
    - Static methods and class methods
    - Global variable assignments at module level

### Module Statistics

| Metric | Value |
|---|---|
| Functions | 6 |
| Classes | 1 |
| Methods | 10 |
| Imports | 6 |
| Lines | 464 |
| Doc Coverage | 100% |

### Imports

```python
from __future__ import annotations
import ast
import logging
from pathlib import Path
from typing import Optional
from src.parser.base import BaseParser, ClassInfo, FunctionInfo, ImportInfo, MethodInfo, ModuleInfo, Parameter, Visibility
```

### Module-Level Variables

- `logger`

### Classes

#### `PythonParser`

```python
class PythonParser(BaseParser)
```

(public) | Lines 217-464

Concrete parser for Python source files using the ast module.

<details>
<summary>Full Documentation</summary>

```
Concrete parser for Python source files using the ast module.

Parses .py files into the unified data model defined in base.py.
Leverages Python's built-in ast module for reliable, standard-library
parsing without external dependencies.

Example:
    parser = PythonParser()
    module_info = parser.parse_file(Path("src/cli.py"))
    print(module_info.functions)
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

Return the language identifier.

**Returns:** `str`

##### `supported_extensions`

```python
def supported_extensions() -> list[str]
```

Return supported file extensions for Python.

**Returns:** `list[str]`

##### `parse_file`

```python
def parse_file(file_path: Path) -> ModuleInfo
```

Parse a single Python source file into a ModuleInfo structure.

| Name | Type | Default |
|---|---|---|
| `file_path` | `Path` | - |

**Returns:** `ModuleInfo`
