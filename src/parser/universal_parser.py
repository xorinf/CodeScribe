"""
Universal fallback parser for non-Python languages using regex.
Extracts basic structures like classes and functions.
"""

from __future__ import annotations

import re
from pathlib import Path

from src.parser.base import (
    BaseParser,
    ClassInfo,
    FunctionInfo,
    ModuleInfo,
)


class UniversalParser(BaseParser):
    """Regex-based parser for fallback language support."""

    def __init__(self, extensions: list[str]) -> None:
        """Initialize with a specific set of extensions.

        Args:
            extensions: List of supported file extensions (e.g. [".js", ".ts"]).
        """
        self._extensions = extensions

    def language(self) -> str:
        """Return the language identifier."""
        return "universal"

    def supported_extensions(self) -> list[str]:
        """Return the file extensions this parser can handle."""
        return self._extensions

    def parse_file(self, file_path: Path) -> ModuleInfo:
        """Parse a single source file using heuristics.

        Args:
            file_path: Absolute or relative path to the source file.

        Returns:
            A ModuleInfo populated with discovered functions and classes.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as exc:
            raise RuntimeError(f"Could not read file {file_path}: {exc}") from exc

        module_info = ModuleInfo(file_path=file_path)

        # 1. Regex for keyword-based functions (def, func, fn, function)
        kw_func_pattern = re.compile(
            r'\b(def|func|fn|function)\s+([A-Za-z0-9_]+)(?:\s*\()?'
        )
        for match in kw_func_pattern.finditer(content):
            name = match.group(2)
            # Avoid duplicates
            if not any(f.name == name for f in module_info.functions):
                module_info.functions.append(FunctionInfo(name=name))

        # 2. Regex for C-family functions (return_type name(args))
        # Matches: [modifiers] ReturnType name (
        cfam_func_pattern = re.compile(
            r'^\s*(?:(?:public|private|protected|static|virtual|inline|const|abstract|final|override|async|extern)\s+)*([A-Za-z0-9_<>:\[\]&*]+)\s+([A-Za-z0-9_]+)\s*\(',
            re.MULTILINE
        )

        ignored_returns = {
            "if", "for", "while", "switch", "catch", "return", "new",
            "class", "function", "def", "func", "fn", "else", "elseif", "elif"
        }

        for match in cfam_func_pattern.finditer(content):
            ret = match.group(1)
            name = match.group(2)
            if ret in ignored_returns or name in ignored_returns:
                continue
            if not any(f.name == name for f in module_info.functions):
                module_info.functions.append(FunctionInfo(name=name, return_type=ret))

        # 3. Regex for classes (class, struct, interface)
        class_pattern = re.compile(r'\b(?:class|struct|interface)\s+([A-Za-z0-9_]+)')
        for match in class_pattern.finditer(content):
            name = match.group(1)
            if not any(c.name == name for c in module_info.classes):
                module_info.classes.append(ClassInfo(name=name))

        return module_info
