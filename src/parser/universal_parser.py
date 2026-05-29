from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

from src.parser.base import (
    BaseParser,
    ClassInfo,
    FunctionInfo,
    MethodInfo,
    ModuleInfo,
    Parameter,
    ParseResult,
    Visibility,
)


class UniversalParser(BaseParser):
    """Regex-based fallback parser for extracting basic structures from non-Python languages."""

    def language(self) -> str:
        return "universal"

    def supported_extensions(self) -> list[str]:
        return [
            ".js", ".ts", ".java", ".cpp", ".c", ".go", ".rb", ".php", ".cs",
            ".rs", ".swift", ".kt", ".m", ".h", ".hpp", ".scala"
        ]

    def parse_file(self, file_path: Path) -> ModuleInfo:
        """Parse a single source file into a ModuleInfo structure."""
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            content = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            # Fallback for potentially weird encodings
            content = file_path.read_text(encoding="latin-1")

        lines = content.splitlines()

        module_info = ModuleInfo(file_path=file_path)

        # Regex patterns
        # Very basic class matching: `class Foo`, `class Foo extends Bar`, `class Foo {`
        class_pattern = re.compile(r'^\s*(?:public\s+|private\s+|protected\s+)?(?:abstract\s+)?class\s+([a-zA-Z_]\w*)', re.MULTILINE)

        # Very basic function/method matching: `function foo(...)`, `def foo(...)`, `func foo(...)`, `void foo(...)`, `int foo(...)`
        # We try to capture things that look like function definitions.
        func_pattern = re.compile(r'^\s*(?:public\s+|private\s+|protected\s+|static\s+|async\s+)*(?:function|def|func|void|int|string|bool|float|double|char|long|short)\s+([a-zA-Z_]\w*)\s*\([^)]*\)', re.MULTILINE)

        # Find classes
        for match in class_pattern.finditer(content):
            class_name = match.group(1)
            # We don't have perfect line numbers with this simple regex, but we can approximate or leave as 0
            # A more robust approach would iterate over lines, but for a fallback this is acceptable
            module_info.classes.append(
                ClassInfo(name=class_name)
            )

        # Find functions
        for match in func_pattern.finditer(content):
            func_name = match.group(1)
            # If it's a known language construct we could try to differentiate methods vs functions,
            # but UniversalParser is a fallback and doesn't know context. We'll just add as function.
            module_info.functions.append(
                FunctionInfo(name=func_name)
            )

        return module_info
