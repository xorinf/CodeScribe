"""
universal_parser.py -- Universal Regex-based Parser for Non-Python Languages.

Acts as a fallback to extract basic class and function structures from
non-Python languages using regular expressions.
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
    """Fallback parser for multiple languages using regular expressions."""

    def language(self) -> str:
        return "universal"

    def supported_extensions(self) -> list[str]:
        return [
            ".js", ".ts", ".java", ".cpp", ".c", ".cs", ".go", ".rs", ".rb", ".php"
        ]

    def parse_file(self, file_path: Path) -> ModuleInfo:
        file_path = Path(file_path).resolve()
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        source = file_path.read_text(encoding="utf-8")
        module_info = ModuleInfo(file_path=file_path)

        # Basic regex to find class declarations
        # e.g. class Foo, public class Bar, abstract class Baz
        class_pattern = re.compile(
            r"^\s*(?:public\s+|private\s+|protected\s+)?(?:abstract\s+)?class\s+([A-Za-z0-9_]+)",
            re.MULTILINE
        )

        # Basic regex to find function declarations
        # e.g. function foo(, def bar(, public static void baz(, fn qux(
        func_pattern = re.compile(
            r"^\s*(?:public\s+|private\s+|protected\s+)?(?:static\s+)?(?:async\s+)?(?:function\s+|func\s+|def\s+|fn\s+)?([A-Za-z0-9_]+)\s*\(",
            re.MULTILINE
        )

        for match in class_pattern.finditer(source):
            class_name = match.group(1)
            # Default to public visibility and no docstring/methods for now
            module_info.classes.append(
                ClassInfo(name=class_name, visibility=Visibility.PUBLIC)
            )

        for match in func_pattern.finditer(source):
            func_name = match.group(1)
            # Filter out common control flow keywords that might match the pattern
            if func_name in ("if", "for", "while", "switch", "catch"):
                continue

            module_info.functions.append(
                FunctionInfo(name=func_name, visibility=Visibility.PUBLIC)
            )

        return module_info
