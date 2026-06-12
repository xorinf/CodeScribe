"""
universal_parser.py -- Regex-based Universal Parser.

Extracts basic class and function structures from non-Python languages
using regex. It handles keyword-based declarations (e.g., def, func, fn)
and C-family return-type-based declarations.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

from src.parser.base import (
    BaseParser,
    ClassInfo,
    FunctionInfo,
    ModuleInfo,
    ParseResult,
    Visibility,
)

class UniversalParser(BaseParser):
    """Regex-based parser for fallback language support."""

    # Matches class declarations
    _CLASS_REGEX = re.compile(r'^\s*class\s+([A-Za-z_][A-Za-z0-9_]*)', re.MULTILINE)

    # Matches keyword-based function declarations
    _FUNC_KEYWORD_REGEX = re.compile(r'^\s*(?:def|func|fn|function)\s+([A-Za-z_][A-Za-z0-9_]*)', re.MULTILINE)

    # Matches C-family return-type function declarations
    _FUNC_C_REGEX = re.compile(
        r'^\s*(?!if\b|while\b|for\b|switch\b|catch\b|return\b)(?:[A-Za-z_][A-Za-z0-9_<>\[\]*&]*\s+)+([A-Za-z_][A-Za-z0-9_]*)\s*\(',
        re.MULTILINE
    )

    def language(self) -> str:
        return "universal"

    def supported_extensions(self) -> list[str]:
        return [
            ".js", ".jsx", ".ts", ".tsx",
            ".java", ".c", ".cpp", ".cc", ".h", ".hpp",
            ".cs", ".go", ".rs", ".php", ".rb", ".kt", ".swift", ".m"
        ]

    def parse_file(self, file_path: Path) -> ModuleInfo:
        """Parse a source file using regex heuristics.

        Args:
            file_path: Absolute or relative path to the source file.

        Returns:
            A ModuleInfo dataclass populated with extracted elements.
        """
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        module = ModuleInfo(file_path=file_path.resolve())

        # Extract classes
        for match in self._CLASS_REGEX.finditer(content):
            class_name = match.group(1)
            # Add class without methods for simple regex parsing
            module.classes.append(ClassInfo(name=class_name))

        # Extract functions
        found_funcs = set()

        for match in self._FUNC_KEYWORD_REGEX.finditer(content):
            func_name = match.group(1)
            if func_name not in found_funcs:
                module.functions.append(FunctionInfo(name=func_name))
                found_funcs.add(func_name)

        for match in self._FUNC_C_REGEX.finditer(content):
            func_name = match.group(1)
            if func_name not in found_funcs:
                module.functions.append(FunctionInfo(name=func_name))
                found_funcs.add(func_name)

        return module
