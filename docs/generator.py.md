---

## `generator.py`

generator.py -- Documentation Generator Engine.

Orchestrates the full documentation generation pipeline. Takes an
AnalysisResult (from the analyzer) and the original ParseResult
(from the parser), then uses the template engine to produce
complete, structured Markdown documentation files.

Responsibilities:
    1. Generate a master index document with project overview.
    2. Generate per-module documentation pages.
    3. Write all output files to the target directory.

Usage:
    from src.generator.generator import DocGenerator

    generator = DocGenerator(project_name="CodeScribe")
    generator.generate(parse_result, analysis_result, output_dir=Path("./docs"))

### Module Statistics

| Metric | Value |
|---|---|
| Functions | 0 |
| Classes | 1 |
| Methods | 7 |
| Imports | 8 |
| Lines | 344 |
| Doc Coverage | 100% |

### Imports

```python
from __future__ import annotations
import logging
from pathlib import Path
from typing import Optional
from src.parser.base import ModuleInfo, ParseResult, FunctionInfo, ClassInfo
from src.analyzer.models import AnalysisResult, ModuleMetrics
from src.generator import templates
from src.generator.nlp import NLPEngine
```

### Module-Level Variables

- `logger`

### Classes

#### `DocGenerator`

```python
class DocGenerator
```

(public) | Lines 35-344

Transforms analysis results into Markdown documentation files.

<details>
<summary>Full Documentation</summary>

```
Transforms analysis results into Markdown documentation files.

The generator is the final stage of the CodeScribe pipeline.
It receives structured data from the parser and analyzer, applies
templates to produce human-readable documentation, and writes
the output to disk.

Attributes:
    _project_name: The name used in documentation headers.
    _include_private: Whether to document private/protected elements.
    _nlp_engine: The NLP Engine for enhancing docstrings.
```

</details>

**Methods:**

| Method | Visibility | Static | Class Method |
|---|---|---|---|
| `generate` | public | - | - |

##### `generate`

```python
def generate(parse_result: ParseResult, analysis: AnalysisResult, output_dir: Path, single_file: bool = True) -> list[Path]
```

Run the full documentation generation pipeline.

| Name | Type | Default |
|---|---|---|
| `parse_result` | `ParseResult` | - |
| `analysis` | `AnalysisResult` | - |
| `output_dir` | `Path` | - |
| `single_file` | `bool` | `True` |

**Returns:** `list[Path]`
