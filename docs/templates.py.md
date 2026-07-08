---

## `templates.py`

templates.py -- Markdown Templates for Documentation Generation.

Provides structured text templates that transform parsed and analyzed
code data into clean, human-readable Markdown documentation. Each
template function receives typed data and returns formatted strings.

This module acts as the "NLP layer" -- it handles all natural language
construction, phrasing decisions, and document formatting. By
centralizing text generation here, the main generator engine stays
focused on orchestration.

Design Note:
    Templates use Python's built-in string formatting rather than
    external template engines (Jinja2, etc.) to keep the project
    dependency-free. If a more powerful template engine is needed
    in the future, only this module needs to change.

### Module Statistics

| Metric | Value |
|---|---|
| Functions | 14 |
| Classes | 0 |
| Methods | 0 |
| Imports | 4 |
| Lines | 563 |
| Doc Coverage | 100% |

### Imports

```python
from __future__ import annotations
from typing import Optional
from src.parser.base import ClassInfo, FunctionInfo, ImportInfo, MethodInfo, ModuleInfo, Parameter, Visibility
from src.analyzer.models import AnalysisResult, CodebaseStats, DependencyEdge, InheritanceNode, ModuleMetrics
```

### Functions

#### `render_project_header`

```python
def render_project_header(project_name: str, stats: CodebaseStats, language: str) -> str
```

(public) | Lines 133-177

Render the top-level project documentation header.

<details>
<summary>Full Documentation</summary>

```
Render the top-level project documentation header.

Args:
    project_name: Name of the project.
    stats: Codebase-wide statistics.
    language: Primary language of the codebase.

Returns:
    Formatted markdown string for the project header section.
```

</details>

**Parameters:**

| Name | Type | Default |
|---|---|---|
| `project_name` | `str` | - |
| `stats` | `CodebaseStats` | - |
| `language` | `str` | - |

**Returns:** `str`

#### `render_table_of_contents`

```python
def render_table_of_contents(modules: list[ModuleInfo]) -> str
```

(public) | Lines 180-198

Render a table of contents linking to each module section.

<details>
<summary>Full Documentation</summary>

```
Render a table of contents linking to each module section.

Args:
    modules: List of parsed modules.

Returns:
    Formatted markdown TOC.
```

</details>

**Parameters:**

| Name | Type | Default |
|---|---|---|
| `modules` | `list[ModuleInfo]` | - |

**Returns:** `str`

#### `render_module_section`

```python
def render_module_section(mod: ModuleInfo, metrics: Optional[ModuleMetrics] = None) -> str
```

(public) | Lines 201-272

Render the full documentation section for a single module.

<details>
<summary>Full Documentation</summary>

```
Render the full documentation section for a single module.

Args:
    mod: The parsed module data.
    metrics: Optional metrics for this module.

Returns:
    Formatted markdown for the module.
```

</details>

**Parameters:**

| Name | Type | Default |
|---|---|---|
| `mod` | `ModuleInfo` | - |
| `metrics` | `Optional[ModuleMetrics]` | `None` |

**Returns:** `str`

#### `render_function`

```python
def render_function(func: FunctionInfo) -> str
```

(public) | Lines 291-362

Render documentation for a single function.

<details>
<summary>Full Documentation</summary>

```
Render documentation for a single function.

Produces a heading, signature, description, parameter table,
and return type information.

Args:
    func: The function info.

Returns:
    Formatted markdown for the function.
```

</details>

**Parameters:**

| Name | Type | Default |
|---|---|---|
| `func` | `FunctionInfo` | - |

**Returns:** `str`

#### `render_class`

```python
def render_class() -> str
```

(public) | Lines 365-433

Render documentation for a single class.

<details>
<summary>Full Documentation</summary>

```
Render documentation for a single class.

Produces a heading, class signature, description, method list,
and detailed method documentation.

Args:
    cls: The class info.

Returns:
    Formatted markdown for the class.
```

</details>

**Returns:** `str`

#### `render_method`

```python
def render_method(method: MethodInfo) -> str
```

(public) | Lines 436-478

Render documentation for a single class method.

<details>
<summary>Full Documentation</summary>

```
Render documentation for a single class method.

Args:
    method: The method info.

Returns:
    Formatted markdown for the method.
```

</details>

**Parameters:**

| Name | Type | Default |
|---|---|---|
| `method` | `MethodInfo` | - |

**Returns:** `str`

#### `render_dependency_section`

```python
def render_dependency_section(analysis: AnalysisResult) -> str
```

(public) | Lines 481-520

Render the dependency analysis section.

<details>
<summary>Full Documentation</summary>

```
Render the dependency analysis section.

Args:
    analysis: The full analysis result.

Returns:
    Formatted markdown for the dependency overview.
```

</details>

**Parameters:**

| Name | Type | Default |
|---|---|---|
| `analysis` | `AnalysisResult` | - |

**Returns:** `str`

#### `render_inheritance_section`

```python
def render_inheritance_section(analysis: AnalysisResult) -> str
```

(public) | Lines 523-563

Render the class inheritance hierarchy section.

<details>
<summary>Full Documentation</summary>

```
Render the class inheritance hierarchy section.

Args:
    analysis: The full analysis result.

Returns:
    Formatted markdown for the inheritance overview.
```

</details>

**Parameters:**

| Name | Type | Default |
|---|---|---|
| `analysis` | `AnalysisResult` | - |

**Returns:** `str`
