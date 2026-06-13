"""
universal_parser.py -- Regex-based Universal Parser for Non-Python Languages.

This module provides a fallback parser for extracting basic structures
(functions, classes) from non-Python languages using regular expressions.
It handles both keyword-based declarations (e.g., def, func, fn) and
C-family return-type-based declarations.
"""

from __future__ import annotations

import re
from pathlib import Path

from src.parser.base import (
    BaseParser,
    ClassInfo,
    FunctionInfo,
    ModuleInfo,
    ParseResult,
    Visibility,
)


class UniversalParser(BaseParser):
    """Fallback parser for non-Python languages."""

    _SUPPORTED_EXTENSIONS = [
        ".js", ".ts", ".java", ".cpp", ".c", ".h", ".hpp",
        ".cs", ".go", ".rs", ".php", ".rb", ".swift", ".kt"
    ]

    # Keyword-based function regex: e.g., def my_func(, func MyFunc(, fn my_func(, function myFunc(
    _KEYWORD_FUNC_REGEX = re.compile(
        r'\b(?:def|func|fn|function)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(',
        re.MULTILINE
    )

    # C-family function regex: e.g., int my_func(, public static void main(
    _CFAMILY_FUNC_REGEX = re.compile(
        r'^\s*(?:(?:public|private|protected|static|final|inline|virtual|override|abstract)\s+)*'
        r'[a-zA-Z_][a-zA-Z0-9_<>\[\]]*\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(',
        re.MULTILINE
    )

    # Class regex: e.g., class MyClass {
    _CLASS_REGEX = re.compile(
        r'\bclass\s+([a-zA-Z_][a-zA-Z0-9_]*)',
        re.MULTILINE
    )

    # Keywords to ignore in C-family regex matches
    _IGNORE_KEYWORDS = {"if", "while", "for", "switch", "catch", "return", "new", "throw"}

    def language(self) -> str:
        """Return the language identifier."""
        return "universal"

    def supported_extensions(self) -> list[str]:
        """Return the supported file extensions."""
        return self._SUPPORTED_EXTENSIONS

    def parse_file(self, file_path: Path) -> ModuleInfo:
        """Parse a single source file into a ModuleInfo structure."""
        content = file_path.read_text(encoding="utf-8", errors="replace")

        module = ModuleInfo(file_path=file_path)

        found_funcs = set()

        # Extract keyword-based functions
        for match in self._KEYWORD_FUNC_REGEX.finditer(content):
            name = match.group(1)
            if name not in found_funcs and name not in self._IGNORE_KEYWORDS:
                found_funcs.add(name)
                func_info = FunctionInfo(
                    name=name,
                    visibility=Visibility.PUBLIC,
                    start_line=content.count('\n', 0, match.start()) + 1
                )
                module.functions.append(func_info)

        # Extract C-family functions
        for match in self._CFAMILY_FUNC_REGEX.finditer(content):
            name = match.group(1)
            if name not in found_funcs and name not in self._IGNORE_KEYWORDS:
                found_funcs.add(name)
                func_info = FunctionInfo(
                    name=name,
                    visibility=Visibility.PUBLIC,
                    start_line=content.count('\n', 0, match.start()) + 1
                )
                module.functions.append(func_info)

        found_classes = set()

        # Extract classes
        for match in self._CLASS_REGEX.finditer(content):
            name = match.group(1)
            if name not in found_classes:
                found_classes.add(name)
                class_info = ClassInfo(
                    name=name,
                    visibility=Visibility.PUBLIC,
                    start_line=content.count('\n', 0, match.start()) + 1
                )
                module.classes.append(class_info)

        return module
