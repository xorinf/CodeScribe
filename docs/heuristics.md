---

## `heuristics.py`

Quality and heuristic filters for CodeScribe Data Cleanser.

### Module Statistics

| Metric | Value |
|---|---|
| Functions | 0 |
| Classes | 1 |
| Methods | 3 |
| Imports | 3 |
| Lines | 69 |
| Doc Coverage | 100% |

### Imports

```python
import re
import logging
from typing import Optional
```

### Module-Level Variables

- `logger`

### Classes

#### `QualityFilter`

```python
class QualityFilter
```

(public) | Lines 11-69

Applies heuristic checks to filter out low-quality code or boilerplate.

**Methods:**

| Method | Visibility | Static | Class Method |
|---|---|---|---|
| `is_auto_generated` | public | - | - |
| `is_high_quality` | public | - | - |

##### `is_auto_generated`

```python
def is_auto_generated(content: str) -> bool
```

Check if the first few lines contain auto-generated markers.

| Name | Type | Default |
|---|---|---|
| `content` | `str` | - |

**Returns:** `bool`

##### `is_high_quality`

```python
def is_high_quality(content: str) -> bool
```

Main heuristic check for file content.

| Name | Type | Default |
|---|---|---|
| `content` | `str` | - |

**Returns:** `bool`
