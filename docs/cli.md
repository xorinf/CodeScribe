---

## `cli.py`

CodeScribe CLI - Command-Line Interface for the Documentation Engine.

This module provides the primary entry point for interacting with CodeScribe.
It exposes subcommands for generating documentation, analyzing codebases,
and initializing project configurations.

Usage:
    python -m src.cli generate --input ./my_project --output ./docs
    python -m src.cli analyze --input ./my_project
    python -m src.cli init
    python -m src.cli version

### Module Statistics

| Metric | Value |
|---|---|
| Functions | 14 |
| Classes | 0 |
| Methods | 0 |
| Imports | 8 |
| Lines | 738 |
| Doc Coverage | 100% |

### Imports

```python
import argparse
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Optional
```

### Module-Level Variables

- `APP_NAME`
- `APP_VERSION`
- `DEFAULT_CONFIG_FILENAME`
- `DEFAULT_OUTPUT_DIR`
- `SUPPORTED_LANGUAGES`
- `DEFAULT_CONFIG`
- `_LANGUAGE_EXTENSIONS`

### Functions

#### `main`

```python
def main() -> None
```

(public) | Lines 729-738

Parse arguments and dispatch to the appropriate subcommand handler.

**Returns:** `None`
