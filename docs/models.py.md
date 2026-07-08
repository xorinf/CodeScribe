---

## `models.py`

models.py -- Data Models for Semantic Analysis Results.

Defines the output structures produced by the semantic analyzer.
These models capture the relationships, dependencies, and metrics
that the analyzer discovers by examining parsed code data.

Data Flow:
    ParseResult (from parser)  -->  SemanticAnalyzer.analyze()  -->  AnalysisResult
                                                                        |
                                                                        +-- DependencyGraph
                                                                        +-- InheritanceTree
                                                                        +-- ModuleMetrics
                                                                        +-- CodebaseStats

### Module Statistics

| Metric | Value |
|---|---|
| Functions | 0 |
| Classes | 7 |
| Methods | 2 |
| Imports | 4 |
| Lines | 232 |
| Doc Coverage | 100% |

### Imports

```python
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
```

### Classes

#### `DependencyEdge`

```python
@dataclass
class DependencyEdge
```

(public) | Lines 30-45

Represents a single dependency from one module to another.

<details>
<summary>Full Documentation</summary>

```
Represents a single dependency from one module to another.

Attributes:
    source: The module that contains the import statement.
    target: The module being imported.
    imported_names: Specific names imported (empty means whole module).
    is_internal: True if the target is part of this codebase.
    is_relative: True if this is a relative import.
```

</details>

#### `DependencyGraph`

```python
@dataclass
class DependencyGraph
```

(public) | Lines 49-86

Represents the full import dependency graph of the codebase.

<details>
<summary>Full Documentation</summary>

```
Represents the full import dependency graph of the codebase.

Attributes:
    edges: All dependency edges discovered across all modules.
    modules: Set of all module names that appear in the graph.
    external_deps: Set of third-party/stdlib module names.
    internal_deps: Set of project-internal module names.
```

</details>

**Methods:**

| Method | Visibility | Static | Class Method |
|---|---|---|---|
| `get_dependencies_of` | public | - | - |
| `get_dependents_of` | public | - | - |

##### `get_dependencies_of`

```python
def get_dependencies_of(module_name: str) -> list[DependencyEdge]
```

Return all edges where the given module is the source.

| Name | Type | Default |
|---|---|---|
| `module_name` | `str` | - |

**Returns:** `list[DependencyEdge]`

##### `get_dependents_of`

```python
def get_dependents_of(module_name: str) -> list[DependencyEdge]
```

Return all edges where the given module is the target.

| Name | Type | Default |
|---|---|---|
| `module_name` | `str` | - |

**Returns:** `list[DependencyEdge]`

#### `InheritanceNode`

```python
@dataclass
class InheritanceNode
```

(public) | Lines 95-110

Represents a class and its position in the inheritance hierarchy.

<details>
<summary>Full Documentation</summary>

```
Represents a class and its position in the inheritance hierarchy.

Attributes:
    class_name: The fully qualified class name (module.ClassName).
    module_path: The file path where this class is defined.
    base_classes: Direct parent class names.
    subclasses: Direct child class names discovered in the codebase.
    depth: The depth in the inheritance tree (0 = no known parent).
```

</details>

#### `InheritanceTree`

```python
@dataclass
class InheritanceTree
```

(public) | Lines 114-123

The full class inheritance hierarchy of the codebase.

<details>
<summary>Full Documentation</summary>

```
The full class inheritance hierarchy of the codebase.

Attributes:
    nodes: Mapping of fully qualified class name to its node.
    roots: Class names that have no known parent in the codebase.
```

</details>

#### `ModuleMetrics`

```python
@dataclass
class ModuleMetrics
```

(public) | Lines 132-167

Quantitative metrics computed for a single module.

<details>
<summary>Full Documentation</summary>

```
Quantitative metrics computed for a single module.

Attributes:
    module_name: The module's file name or qualified path.
    file_path: Absolute path to the source file.
    total_lines: Approximate line count of the module.
    num_functions: Number of top-level functions.
    num_classes: Number of class definitions.
    num_methods: Total number of methods across all classes.
    num_imports: Number of import statements.
    num_global_vars: Number of module-level variable assignments.
    has_docstring: Whether the module has a top-level docstring.
    documented_functions: Number of functions that have docstrings.
    documented_classes: Number of classes that have docstrings.
    documentation_coverage: Percentage of documented elements (0.0 - 1.0).
    avg_params_per_function: Average parameter count per function.
    public_api_count: Number of public functions and classes.
    private_api_count: Number of protected/private functions and classes.
```

</details>

#### `CodebaseStats`

```python
@dataclass
class CodebaseStats
```

(public) | Lines 176-203

Aggregated statistics across the entire analyzed codebase.

<details>
<summary>Full Documentation</summary>

```
Aggregated statistics across the entire analyzed codebase.

Attributes:
    total_modules: Number of source files analyzed.
    total_functions: Total function definitions across all modules.
    total_classes: Total class definitions across all modules.
    total_methods: Total method definitions across all classes.
    total_imports: Total import statements across all modules.
    total_lines: Approximate total line count.
    overall_doc_coverage: Percentage of documented elements (0.0 - 1.0).
    avg_functions_per_module: Average functions per module.
    avg_classes_per_module: Average classes per module.
    most_complex_module: Module with the highest element count.
    most_depended_on: Module that is imported by the most others.
```

</details>

#### `AnalysisResult`

```python
@dataclass
class AnalysisResult
```

(public) | Lines 212-232

Complete output of the semantic analyzer.

<details>
<summary>Full Documentation</summary>

```
Complete output of the semantic analyzer.

Aggregates all analysis products into a single structure for
downstream consumption by the generator module.

Attributes:
    dependency_graph: The import dependency graph.
    inheritance_tree: The class inheritance hierarchy.
    module_metrics: Per-module quantitative metrics.
    codebase_stats: Aggregated statistics for the whole codebase.
    language: The language of the analyzed codebase.
    warnings: Non-fatal issues discovered during analysis.
```

</details>
