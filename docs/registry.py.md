---

## `registry.py`

registry.py -- Central Parser Registry.

Provides a singleton registry that maps file extensions to their
corresponding parser implementations. The CLI and other entry points
use this registry to look up the correct parser for a given file
without needing to know about specific parser classes.

Usage:
    from src.parser.registry import ParserRegistry

    registry = ParserRegistry()
    registry.register(PythonParser())

    parser = registry.get_parser_for_file(Path("main.py"))
    if parser:
        result = parser.parse_file(Path("main.py"))

### Module Statistics

| Metric | Value |
|---|---|
| Functions | 0 |
| Classes | 1 |
| Methods | 8 |
| Imports | 4 |
| Lines | 125 |
| Doc Coverage | 100% |

### Imports

```python
from __future__ import annotations
from pathlib import Path
from typing import Optional
from src.parser.base import BaseParser, ParseResult
```

### Classes

#### `ParserRegistry`

```python
class ParserRegistry
```

(public) | Lines 28-125

Maps file extensions to parser instances.

<details>
<summary>Full Documentation</summary>

```
Maps file extensions to parser instances.

Acts as a lookup table so the rest of the application can resolve
the correct parser for any given file without tight coupling to
specific language implementations.

Attributes:
    _parsers: Internal mapping of file extension to BaseParser.
```

</details>

**Methods:**

| Method | Visibility | Static | Class Method |
|---|---|---|---|
| `register` | public | - | - |
| `get_parser_for_file` | public | - | - |
| `get_parser_for_extension` | public | - | - |
| `supported_extensions` | public | - | - |
| `parse_all` | public | - | - |

##### `register`

```python
def register(parser: BaseParser) -> None
```

Register a parser for all of its supported extensions.

| Name | Type | Default |
|---|---|---|
| `parser` | `BaseParser` | - |

**Returns:** `None`

##### `get_parser_for_file`

```python
def get_parser_for_file(file_path: Path) -> Optional[BaseParser]
```

Look up the appropriate parser for a given file.

| Name | Type | Default |
|---|---|---|
| `file_path` | `Path` | - |

**Returns:** `Optional[BaseParser]`

##### `get_parser_for_extension`

```python
def get_parser_for_extension(extension: str) -> Optional[BaseParser]
```

Look up the appropriate parser for a given extension string.

| Name | Type | Default |
|---|---|---|
| `extension` | `str` | - |

**Returns:** `Optional[BaseParser]`

##### `supported_extensions`

```python
def supported_extensions() -> list[str]
```

Return all file extensions that have a registered parser.

**Returns:** `list[str]`

##### `parse_all`

```python
def parse_all(root: Path, exclude_dirs: Optional[list[str]] = None) -> list[ParseResult]
```

Run every registered parser across the given directory.

| Name | Type | Default |
|---|---|---|
| `root` | `Path` | - |
| `exclude_dirs` | `Optional[list[str]]` | `None` |

**Returns:** `list[ParseResult]`
