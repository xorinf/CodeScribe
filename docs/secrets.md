---

## `secrets.py`

Secret scanning heuristics for CodeScribe Data Cleanser.

### Module Statistics

| Metric | Value |
|---|---|
| Functions | 0 |
| Classes | 1 |
| Methods | 1 |
| Imports | 3 |
| Lines | 36 |
| Doc Coverage | 100% |

### Imports

```python
import re
import logging
from typing import List
```

### Module-Level Variables

- `logger`

### Classes

#### `SecretScanner`

```python
class SecretScanner
```

(public) | Lines 11-36

Scans code for common secrets (PII, tokens, keys).

**Methods:**

| Method | Visibility | Static | Class Method |
|---|---|---|---|
| `has_secrets` | public | - | - |

##### `has_secrets`

```python
def has_secrets(content: str) -> bool
```

Check if the content contains any matched secrets.

| Name | Type | Default |
|---|---|---|
| `content` | `str` | - |

**Returns:** `bool`
