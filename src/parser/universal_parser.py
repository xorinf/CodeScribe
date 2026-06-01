"""
universal_parser.py -- Fallback Parser for non-Python languages.

Uses regular expressions to extract basic class and function structures
from various programming languages.
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
    """Regex-based fallback parser for multiple programming languages.

    Extracts basic class and function definitions when a language-specific
    parser is not available.
    """

    def language(self) -> str:
        """Return the language identifier.

        Returns:
            The string "universal".
        """
        return "universal"

    def supported_extensions(self) -> list[str]:
        """Return supported file extensions for Universal Parser.

        Returns:
            A list of extensions.
        """
        return [
            ".js", ".ts", ".java", ".cpp", ".c", ".cs", ".go",
            ".rs", ".rb", ".php", ".swift", ".kt", ".scala", ".m", ".h"
        ]

    def parse_file(self, file_path: Path) -> ModuleInfo:
        """Parse a single source file into a ModuleInfo structure.

        Args:
            file_path: Path to the source file.

        Returns:
            A populated ModuleInfo dataclass.

        Raises:
            FileNotFoundError: If the file does not exist.
        """
        file_path = Path(file_path).resolve()

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            source = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            source = file_path.read_text(encoding="utf-8", errors="replace")

        module_info = ModuleInfo(file_path=file_path)

        class_pattern = re.compile(
            r'^\s*(?:public\s+|private\s+|protected\s+|export\s+|default\s+)?class\s+([A-Za-z0-9_]+)',
            re.MULTILINE
        )
        func_pattern = re.compile(
            r'^\s*(?:public\s+|private\s+|protected\s+|export\s+|default\s+)?(?:static\s+)?(?:async\s+)?(?:function\s+|func\s+|def\s+|fn\s+)?(?:[A-Za-z0-9_<>\[\]]+\s+)?([A-Za-z0-9_]+)\s*\(',
            re.MULTILINE
        )

        classes = class_pattern.findall(source)
        for cls_name in set(classes):
            module_info.classes.append(ClassInfo(name=cls_name))

        functions = func_pattern.findall(source)
        ignore_keywords = {"if", "for", "while", "switch", "catch", "return", "elif"}

        # Deduplicate while preserving some order or just deduplicate
        seen_funcs = set()
        for func_name in functions:
            if func_name not in ignore_keywords and func_name not in seen_funcs:
                module_info.functions.append(FunctionInfo(name=func_name))
                seen_funcs.add(func_name)

        return module_info
