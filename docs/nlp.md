---

## `nlp.py`

nlp.py -- NLP Integration for Documentation Generation.

This module integrates Cloud LLM APIs (specifically Google Gemini)
to automatically generate human-readable summaries and descriptions
for code elements (functions, classes) that lack docstrings.

Usage:
    from src.generator.nlp import NLPEngine
    
    engine = NLPEngine(api_key="...", enabled=True)
    summary = engine.generate_function_summary(func_info, "my_module.py")

### Module Statistics

| Metric | Value |
|---|---|
| Functions | 0 |
| Classes | 1 |
| Methods | 6 |
| Imports | 5 |
| Lines | 153 |
| Doc Coverage | 100% |

### Imports

```python
from __future__ import annotations
import logging
import os
from typing import Optional
from src.parser.base import ClassInfo, FunctionInfo
```

### Module-Level Variables

- `logger`

### Classes

#### `NLPEngine`

```python
class NLPEngine
```

(public) | Lines 26-153

Natural Language Processing engine for enhancing documentation.

<details>
<summary>Full Documentation</summary>

```
Natural Language Processing engine for enhancing documentation.

Uses the Google Gemini API to analyze function signatures and class
structures and generate concise descriptions.
```

</details>

**Methods:**

| Method | Visibility | Static | Class Method |
|---|---|---|---|
| `generate_function_summary` | public | - | - |
| `generate_class_summary` | public | - | - |

##### `generate_function_summary`

```python
def generate_function_summary(func: FunctionInfo, module_name: str) -> Optional[str]
```

Generate a concise summary for a function.

| Name | Type | Default |
|---|---|---|
| `func` | `FunctionInfo` | - |
| `module_name` | `str` | - |

**Returns:** `Optional[str]`

##### `generate_class_summary`

```python
def generate_class_summary(module_name: str) -> Optional[str]
```

Generate a concise summary for a class.

| Name | Type | Default |
|---|---|---|
| `module_name` | `str` | - |

**Returns:** `Optional[str]`
