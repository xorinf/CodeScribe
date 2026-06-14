from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

from src.parser.base import (
    BaseParser,
    ClassInfo,
    FunctionInfo,
    ModuleInfo,
    Visibility,
)

class UniversalParser(BaseParser):
    """A regex-based parser that handles any non-Python language.

    Extracts basic class and function structures by matching common patterns
    across a variety of programming languages (e.g., keyword-based like `func`, `fn`, `function`
    or C-family return-type-based declarations).
    """

    def __init__(self, extensions: list[str]) -> None:
        """Initialize the parser with the given file extensions.

        Args:
            extensions: A list of supported file extensions (e.g., ['.js', '.cpp']).
        """
        self._extensions = extensions

        # Pattern for class declarations
        self._class_pattern = re.compile(
            r"^\s*(?:public\s+|private\s+|protected\s+|export\s+|abstract\s+)?(?:class|struct|interface)\s+([a-zA-Z_]\w*)",
            re.MULTILINE
        )

        # Pattern for keyword-based functions (e.g. fn, func, def, function)
        self._keyword_func_pattern = re.compile(
            r"^\s*(?:public\s+|private\s+|protected\s+|static\s+|export\s+|async\s+)?(?:def|func|fn|function)\s+([a-zA-Z_]\w*)\s*\(",
            re.MULTILINE
        )

        # Pattern for C-family functions (return type followed by function name)
        self._cfamily_func_pattern = re.compile(
            r"^\s*(?:public\s+|private\s+|protected\s+|static\s+|virtual\s+|inline\s+|override\s+)?([a-zA-Z_][a-zA-Z0-9_<>:,\s\*\&]*?)\s+([a-zA-Z_]\w*)\s*\(",
            re.MULTILINE
        )

    def language(self) -> str:
        return "universal"

    def supported_extensions(self) -> list[str]:
        return self._extensions

    def parse_file(self, file_path: Path) -> ModuleInfo:
        """Parse a single source file using regex patterns."""
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        module_info = ModuleInfo(file_path=file_path)

        # Find classes
        for match in self._class_pattern.finditer(content):
            class_name = match.group(1)
            module_info.classes.append(ClassInfo(name=class_name))

        # Find keyword-based functions
        seen_funcs = set()
        for match in self._keyword_func_pattern.finditer(content):
            func_name = match.group(1)
            if func_name not in seen_funcs:
                module_info.functions.append(FunctionInfo(name=func_name))
                seen_funcs.add(func_name)

        # Find C-family functions
        for match in self._cfamily_func_pattern.finditer(content):
            func_name = match.group(2)
            # Avoid matching typical control flow keywords mistakenly caught by regex
            if func_name in {"if", "for", "while", "switch", "catch", "return"}:
                continue
            if func_name not in seen_funcs:
                module_info.functions.append(FunctionInfo(name=func_name))
                seen_funcs.add(func_name)

        return module_info
