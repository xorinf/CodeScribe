---

## `__init__.py`

src.analyzer -- Semantic Analysis Package.

This package analyzes parsed code structures to understand relationships,
dependencies, and architectural patterns. It produces structured analysis
results consumed by the generator module.

Public API:
    - SemanticAnalyzer: The main analysis engine.
    - AnalysisResult: Top-level output container.
    - DependencyGraph, InheritanceTree: Relationship models.
    - ModuleMetrics, CodebaseStats: Quantitative outputs.

### Module Statistics

| Metric | Value |
|---|---|
| Functions | 0 |
| Classes | 0 |
| Methods | 0 |
| Imports | 2 |
| Lines | 31 |
| Doc Coverage | 0% |

### Imports

```python
from src.analyzer.analyzer import SemanticAnalyzer
from src.analyzer.models import AnalysisResult, CodebaseStats, DependencyGraph, InheritanceTree, ModuleMetrics
```

### Module-Level Variables

- `__all__`
