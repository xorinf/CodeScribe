---

## `trainer.py`

Trainer for the CodeScribe custom BPE tokenizer.

### Module Statistics

| Metric | Value |
|---|---|
| Functions | 0 |
| Classes | 1 |
| Methods | 3 |
| Imports | 5 |
| Lines | 82 |
| Doc Coverage | 100% |

### Imports

```python
import json
import logging
from pathlib import Path
from typing import Iterator
from tokenizers import Tokenizer, decoders, models, pre_tokenizers, trainers
```

### Module-Level Variables

- `logger`

### Classes

#### `CodeTokenizerTrainer`

```python
class CodeTokenizerTrainer
```

(public) | Lines 15-82

Trains a Byte-Level BPE tokenizer on a JSONL dataset.

**Methods:**

| Method | Visibility | Static | Class Method |
|---|---|---|---|
| `train` | public | - | - |

##### `train`

```python
def train(dataset_path: Path, output_path: Path)
```

Train the tokenizer and save it.

| Name | Type | Default |
|---|---|---|
| `dataset_path` | `Path` | - |
| `output_path` | `Path` | - |
