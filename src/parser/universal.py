"""
Universal Regex-Based Parser.

A fallback parser that uses regular expressions to extract basic
class and function structures from unsupported languages.
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
    """Regex-based parser for general programming languages."""

    # We use a broad set of extensions for the UniversalParser
    _SUPPORTED_EXTS = [
        ".js", ".jsx", ".ts", ".tsx",  # JS/TS
        ".java", ".go", ".rs",          # Java, Go, Rust
        ".cpp", ".cc", ".cxx", ".hpp", ".h", ".c",  # C/C++
        ".cs", ".php", ".rb",           # C#, PHP, Ruby
        ".kt", ".kts", ".swift",        # Kotlin, Swift
    ]

    def __init__(self) -> None:
        """Initialize regex patterns."""
        # A simple pattern to catch class definitions.
        # e.g. public class Foo, struct Bar, interface Baz
        self._class_pattern = re.compile(
            r'^\s*(?:public\s+|private\s+|protected\s+|export\s+|abstract\s+)*(?:class|struct|interface)\s+([A-Za-z0-9_]+)',
            re.MULTILINE
        )

        # A simple pattern to catch function/method definitions.
        # e.g. public static void main(, function foo(, def my_func(
        self._func_pattern = re.compile(
            r'^\s*(?:public\s+|private\s+|protected\s+|export\s+|static\s+|async\s+|abstract\s+|virtual\s+|override\s+)*(?:def|function|func|fn|[A-Za-z0-9_<>\[\]]+)\s+([A-Za-z0-9_]+)\s*\(',
            re.MULTILINE
        )

    def language(self) -> str:
        """Return the language identifier."""
        return "universal"

    def supported_extensions(self) -> list[str]:
        """Return supported file extensions."""
        return self._SUPPORTED_EXTS

    def parse_file(self, file_path: Path) -> ModuleInfo:
        """Parse a file using regex to find classes and functions.

        Args:
            file_path: Path to the source file.

        Returns:
            A populated ModuleInfo dataclass.
        """
        file_path = Path(file_path).resolve()

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            source = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            # Skip binary files or unreadable encodings
            source = ""

        module_info = ModuleInfo(file_path=file_path)

        # Extract classes
        for match in self._class_pattern.finditer(source):
            class_name = match.group(1)
            # Find line number (roughly)
            start_index = match.start()
            line_num = source.count('\n', 0, start_index) + 1

            module_info.classes.append(ClassInfo(
                name=class_name,
                visibility=Visibility.PUBLIC, # Default to public
                start_line=line_num,
                end_line=line_num,
            ))

        # Extract functions
        for match in self._func_pattern.finditer(source):
            func_name = match.group(1)

            # Skip common keywords that might match the regex
            if func_name in ("if", "for", "while", "switch", "catch"):
                continue

            start_index = match.start()
            line_num = source.count('\n', 0, start_index) + 1

            module_info.functions.append(FunctionInfo(
                name=func_name,
                visibility=Visibility.PUBLIC, # Default to public
                start_line=line_num,
                end_line=line_num,
            ))

        return module_info
