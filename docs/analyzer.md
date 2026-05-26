---

## `analyzer.py`

analyzer.py -- Semantic Analyzer Engine.

Takes ParseResult data from the parser module and performs semantic
analysis to understand code relationships, dependencies, and structure.

Responsibilities:
    1. Build the import dependency graph (internal vs external).
    2. Map the class inheritance hierarchy.
    3. Compute per-module metrics (complexity, documentation coverage).
    4. Aggregate codebase-wide statistics.

Usage:
    from src.parser.registry import ParserRegistry
    from src.analyzer.analyzer import SemanticAnalyzer

    registry = ParserRegistry()
    # Assuming parsers are registered
    parse_results = registry.parse_all(Path("./src"))

    # Combine results if needed or analyze one
    analyzer = SemanticAnalyzer()
    if parse_results:
        analysis = analyzer.analyze(parse_results[0])
        print(analysis.codebase_stats)

### Module Statistics

| Metric | Value |
|---|---|
| Functions | 0 |
| Classes | 1 |
| Methods | 9 |
| Imports | 7 |
| Lines | 468 |
| Doc Coverage | 100% |

### Imports

```python
from __future__ import annotations
import logging
from collections import Counter
from pathlib import Path
from typing import Optional
from src.parser.base import ClassInfo, FunctionInfo, ModuleInfo, ParseResult, Visibility
from src.analyzer.models import AnalysisResult, CodebaseStats, DependencyEdge, DependencyGraph, InheritanceNode, InheritanceTree, ModuleMetrics
```

### Module-Level Variables

- `logger`

### Classes

#### `SemanticAnalyzer`

```python
class SemanticAnalyzer
```

(public) | Lines 55-468

Analyzes parsed code to discover relationships and compute metrics.

<details>
<summary>Full Documentation</summary>

```
Analyzes parsed code to discover relationships and compute metrics.

The analyzer is stateless. Each call to analyze() produces an
independent AnalysisResult from the provided ParseResult.

Attributes:
    _project_root: Optional root path used to resolve internal
                  module names. If not set, all imports are
                  treated based on heuristics.
```

</details>

**Methods:**

| Method | Visibility | Static | Class Method |
|---|---|---|---|
| `analyze` | public | - | - |

##### `analyze`

```python
def analyze(parse_result: ParseResult) -> AnalysisResult
```

Run the full analysis pipeline on a ParseResult.

| Name | Type | Default |
|---|---|---|
| `parse_result` | `ParseResult` | - |

**Returns:** `AnalysisResult`
