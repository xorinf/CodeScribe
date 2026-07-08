---

## `base.py`

base.py -- Abstract Interfaces and Data Models for Code Parsing.

This module defines the contracts that every language-specific parser
must fulfill, along with the data structures used to represent parsed
code elements. These models are intentionally language-agnostic so that
the analyzer and generator modules can work with any supported language
through a single, unified interface.

Data Flow:
    Source File  -->  BaseParser.parse()  -->  ParseResult
                                                 |
                                                 +-- ModuleInfo
                                                       +-- FunctionInfo
                                                       +-- ClassInfo
                                                             +-- MethodInfo

### Module Statistics

| Metric | Value |
|---|---|
| Functions | 0 |
| Classes | 9 |
| Methods | 5 |
| Imports | 6 |
| Lines | 313 |
| Doc Coverage | 100% |

### Imports

```python
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional
```

### Classes

#### `Visibility`

```python
class Visibility(Enum)
```

(public) | Lines 33-42

Visibility level of a code element.

<details>
<summary>Full Documentation</summary>

```
Visibility level of a code element.

Used to distinguish between public API surface and internal
implementation details during documentation generation.
```

</details>

#### `Parameter`

```python
@dataclass(frozen=True)
class Parameter
```

(public) | Lines 51-62

Represents a single function or method parameter.

<details>
<summary>Full Documentation</summary>

```
Represents a single function or method parameter.

Attributes:
    name: The parameter name as it appears in the source code.
    type_hint: The declared type annotation, if present.
    default_value: The default value expression as a string, if present.
```

</details>

#### `FunctionInfo`

```python
@dataclass(frozen=True)
class FunctionInfo
```

(public) | Lines 66-87

Represents a standalone function defined at module level.

<details>
<summary>Full Documentation</summary>

```
Represents a standalone function defined at module level.

Attributes:
    name: The function name.
    docstring: The raw docstring extracted from the source, if present.
    parameters: An ordered list of the function's parameters.
    return_type: The declared return type annotation, if present.
    decorators: A list of decorator names applied to the function.
    visibility: Whether the function is public or private.
    start_line: The line number where the function definition begins.
    end_line: The line number where the function definition ends.
```

</details>

#### `MethodInfo`

```python
@dataclass(frozen=True)
class MethodInfo
```

(public) | Lines 91-119

Represents a method defined inside a class body.

<details>
<summary>Full Documentation</summary>

```
Represents a method defined inside a class body.

Identical in structure to FunctionInfo but semantically distinct.
Methods always belong to a parent ClassInfo.

Attributes:
    name: The method name.
    docstring: The raw docstring extracted from the source, if present.
    parameters: An ordered list of the method's parameters.
    return_type: The declared return type annotation, if present.
    decorators: A list of decorator names applied to the method.
    visibility: Whether the method is public or private.
    is_static: True if the method is decorated with @staticmethod.
    is_classmethod: True if the method is decorated with @classmethod.
    start_line: The line number where the method definition begins.
    end_line: The line number where the method definition ends.
```

</details>

#### `ClassInfo`

```python
@dataclass(frozen=True)
class ClassInfo
```

(public) | Lines 123-144

Represents a class definition within a module.

<details>
<summary>Full Documentation</summary>

```
Represents a class definition within a module.

Attributes:
    name: The class name.
    docstring: The raw docstring extracted from the source, if present.
    base_classes: A list of parent class names this class inherits from.
    methods: An ordered list of methods defined in this class.
    decorators: A list of decorator names applied to the class.
    visibility: Whether the class is public or private.
    start_line: The line number where the class definition begins.
    end_line: The line number where the class definition ends.
```

</details>

#### `ImportInfo`

```python
@dataclass(frozen=True)
class ImportInfo
```

(public) | Lines 148-162

Represents a single import statement.

<details>
<summary>Full Documentation</summary>

```
Represents a single import statement.

Attributes:
    module: The module path being imported (e.g. "os.path").
    names: The specific names imported (e.g. ["join", "dirname"]).
          Empty list means the entire module was imported.
    alias: The alias used in an `import X as Y` statement, if any.
    is_relative: True if this is a relative import (starts with a dot).
```

</details>

#### `ModuleInfo`

```python
@dataclass
class ModuleInfo
```

(public) | Lines 166-186

Represents a single parsed source file (module).

<details>
<summary>Full Documentation</summary>

```
Represents a single parsed source file (module).

This is the central data structure produced by a parser for one file.
It aggregates all top-level elements discovered during parsing.

Attributes:
    file_path: Absolute path to the source file.
    module_docstring: The module-level docstring, if present.
    imports: All import statements found in the module.
    functions: All top-level function definitions.
    classes: All class definitions.
    global_variables: Names of module-level variable assignments.
```

</details>

#### `ParseResult`

```python
@dataclass
class ParseResult
```

(public) | Lines 190-205

Aggregated result of parsing an entire codebase.

<details>
<summary>Full Documentation</summary>

```
Aggregated result of parsing an entire codebase.

Produced by running a parser across all source files in a project.
This is the top-level structure handed off to the analyzer module.

Attributes:
    modules: A list of ModuleInfo objects, one per parsed file.
    language: The language identifier (e.g. "python").
    errors: A list of human-readable error messages for files
            that could not be parsed.
```

</details>

#### `BaseParser`

```python
class BaseParser(ABC)
```

(public) | Lines 213-313

Abstract interface that all language-specific parsers must implement.

<details>
<summary>Full Documentation</summary>

```
Abstract interface that all language-specific parsers must implement.

A concrete parser (e.g. PythonParser) subclasses BaseParser and
provides implementations for parsing individual files and collecting
results across an entire directory tree.

Example usage (once a concrete parser exists):
    parser = PythonParser()
    if parser.can_parse(Path("main.py")):
        module = parser.parse_file(Path("main.py"))
```

</details>

**Methods:**

| Method | Visibility | Static | Class Method |
|---|---|---|---|
| `language` | public | - | - |
| `supported_extensions` | public | - | - |
| `can_parse` | public | - | - |
| `parse_file` | public | - | - |
| `parse_directory` | public | - | - |

##### `language`

```python
@abstractmethod
def language() -> str
```

Return the language identifier this parser handles.

**Returns:** `str`

##### `supported_extensions`

```python
@abstractmethod
def supported_extensions() -> list[str]
```

Return the file extensions this parser can handle.

**Returns:** `list[str]`

##### `can_parse`

```python
def can_parse(file_path: Path) -> bool
```

Check whether this parser supports the given file.

| Name | Type | Default |
|---|---|---|
| `file_path` | `Path` | - |

**Returns:** `bool`

##### `parse_file`

```python
@abstractmethod
def parse_file(file_path: Path) -> ModuleInfo
```

Parse a single source file into a ModuleInfo structure.

| Name | Type | Default |
|---|---|---|
| `file_path` | `Path` | - |

**Returns:** `ModuleInfo`

##### `parse_directory`

```python
def parse_directory(root: Path, exclude_dirs: Optional[list[str]] = None) -> ParseResult
```

Parse all supported files under a directory tree.

| Name | Type | Default |
|---|---|---|
| `root` | `Path` | - |
| `exclude_dirs` | `Optional[list[str]]` | `None` |

**Returns:** `ParseResult`
