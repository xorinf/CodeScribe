"""
Universal Parser for multi-language documentation generation.

Provides a fallback parser for non-Python languages using regular expressions.
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
    """Regex-based fallback parser for generic programming languages."""

    def language(self) -> str:
        """Return the language identifier.

        Returns:
            The string "universal".
        """
        return "universal"

    def supported_extensions(self) -> list[str]:
        """Return supported file extensions.

        Returns:
            A list of common programming language extensions.
        """
        return [
            ".js", ".ts", ".java", ".cpp", ".c", ".go", ".rs",
            ".rb", ".php", ".cs", ".swift", ".kt", ".scala", ".m", ".h"
        ]

    def parse_file(self, file_path: Path) -> ModuleInfo:
        """Parse a generic source file using simple regex rules.

        Args:
            file_path: Path to the source file.

        Returns:
            A populated ModuleInfo dataclass.
        """
        file_path = Path(file_path).resolve()

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        source = file_path.read_text(encoding="utf-8")
        lines = source.splitlines()

        module_info = ModuleInfo(file_path=file_path)

        # Simple regex patterns for common constructs across many languages
        function_pattern = re.compile(r"^\s*(?:public\s+|private\s+|protected\s+|static\s+|export\s+|async\s+)*(?:function\s+|func\s+|def\s+|fn\s+|[\w<>\[\]]+\s+)([a-zA-Z_]\w*)\s*\(", re.MULTILINE)
        class_pattern = re.compile(r"^\s*(?:public\s+|private\s+|protected\s+|export\s+)*(?:class|struct|interface)\s+([a-zA-Z_]\w*)", re.MULTILINE)

        # Extract functions
        for match in function_pattern.finditer(source):
            func_name = match.group(1)
            # Skip obvious false positives like control structures
            if func_name in ("if", "for", "while", "switch", "catch"):
                continue

            # Estimate line number
            line_idx = source[:match.start()].count("\n") + 1

            module_info.functions.append(FunctionInfo(
                name=func_name,
                visibility=Visibility.PUBLIC, # Default assumption
                start_line=line_idx,
                end_line=line_idx
            ))

        # Extract classes
        for match in class_pattern.finditer(source):
            class_name = match.group(1)
            line_idx = source[:match.start()].count("\n") + 1

            module_info.classes.append(ClassInfo(
                name=class_name,
                visibility=Visibility.PUBLIC,
                start_line=line_idx,
                end_line=line_idx
            ))

        return module_info
