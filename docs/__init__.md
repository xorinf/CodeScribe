---

## `__init__.py`

src.parser -- Code Parsing and AST Generation Package.

This package is responsible for ingesting source code files and
producing structured, language-agnostic representations (parse results)
that downstream modules (analyzer, generator) can consume.

Architecture:
    - base.py      : Abstract interfaces and data models that every
                     language-specific parser must implement.
    - registry.py  : A central registry that maps file extensions to
                     their corresponding parser implementations.
    - python_parser.py : (Future) Concrete parser for Python source files.
    - universal.py : Universal parser for extracting classes and functions from various non-Python languages.

### Module Statistics

| Metric | Value |
|---|---|
| Functions | 0 |
| Classes | 0 |
| Methods | 0 |
| Imports | 1 |
| Lines | 19 |
| Doc Coverage | 0% |

### Imports

```python
from src.parser.universal import UniversalParser
```

### Module-Level Variables

- `__all__`
