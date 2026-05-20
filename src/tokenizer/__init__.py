"""
Tokenizer package for CodeScribe.
Provides utilities to train and manage the custom Byte-Level BPE tokenizer.
"""

from .trainer import CodeTokenizerTrainer

__all__ = ["CodeTokenizerTrainer"]
