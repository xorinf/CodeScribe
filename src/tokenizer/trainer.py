"""
Trainer for the CodeScribe custom BPE tokenizer.
"""

import json
import logging
from pathlib import Path
from typing import Iterator

from tokenizers import Tokenizer, decoders, models, pre_tokenizers, trainers

logger = logging.getLogger("CodeScribe.Tokenizer.Trainer")


class CodeTokenizerTrainer:
    """Trains a Byte-Level BPE tokenizer on a JSONL dataset."""

    def __init__(self, vocab_size: int = 50000):
        self.vocab_size = vocab_size
        
        # Initialize a BPE model
        self.tokenizer = Tokenizer(models.BPE())
        
        # ByteLevel pre-tokenizer naturally preserves whitespace and syntax semantics
        # by mapping all bytes to visible characters.
        self.tokenizer.pre_tokenizer = pre_tokenizers.ByteLevel(add_prefix_space=False)
        self.tokenizer.decoder = decoders.ByteLevel()
        
        # Define special tokens commonly used in code models (including FIM tokens)
        self.special_tokens = [
            "<|endoftext|>",
            "<|fim_prefix|>",
            "<|fim_middle|>",
            "<|fim_suffix|>",
            "<|pad|>",
        ]

    def _dataset_iterator(self, dataset_path: Path) -> Iterator[str]:
        """Yields raw code content from the JSONL dataset one by one."""
        try:
            with open(dataset_path, "r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        record = json.loads(line)
                        content = record.get("content")
                        if content:
                            yield content
                    except json.JSONDecodeError:
                        logger.warning("Skipped invalid JSON line in dataset.")
        except FileNotFoundError:
            logger.error(f"Dataset file not found: {dataset_path}")

    def train(self, dataset_path: Path, output_path: Path):
        """Train the tokenizer and save it."""
        logger.info(f"Starting tokenizer training on {dataset_path}")
        logger.info(f"Target vocabulary size: {self.vocab_size}")

        trainer = trainers.BpeTrainer(
            vocab_size=self.vocab_size,
            special_tokens=self.special_tokens,
            show_progress=True,
            initial_alphabet=pre_tokenizers.ByteLevel.alphabet()
        )

        # Train from the iterator to save memory
        iterator = self._dataset_iterator(dataset_path)
        
        try:
            self.tokenizer.train_from_iterator(iterator, trainer=trainer)
            
            # Post-processor for byte-level
            from tokenizers import processors
            self.tokenizer.post_processor = processors.ByteLevel(trim_offsets=False)
            
            output_path.parent.mkdir(parents=True, exist_ok=True)
            self.tokenizer.save(str(output_path))
            logger.info(f"Training complete. Tokenizer saved to {output_path}")
        except Exception as e:
            logger.error(f"Failed to train tokenizer: {e}")
            raise
