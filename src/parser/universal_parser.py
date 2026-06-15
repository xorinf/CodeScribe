"""
universal_parser.py -- Universal Parser for non-Python languages.

Acts as a fallback to extract basic class and function structures from
non-Python languages using regex, handling both keyword-based
(e.g., def, func, fn) and C-family return-type-based declarations.
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
    """Regex-based fallback parser for unsupported languages."""

    def language(self) -> str:
        """Return the language identifier."""
        return "universal"

    def supported_extensions(self) -> list[str]:
        """Return the file extensions this parser can handle."""
        return [
            ".js", ".jsx", ".ts", ".tsx",
            ".java", ".kt", ".kts", ".scala",
            ".c", ".h", ".cpp", ".hpp", ".cc", ".cxx",
            ".cs",
            ".go",
            ".rs",
            ".rb",
            ".php",
            ".swift"
        ]

    def parse_file(self, file_path: Path) -> ModuleInfo:
        """Parse a single source file into a ModuleInfo structure using regex heuristics.

        Args:
            file_path: Absolute or relative path to the source file.

        Returns:
            A ModuleInfo dataclass populated with the parsed elements.
        """
        try:
            content = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return ModuleInfo(file_path=file_path)

        module = ModuleInfo(file_path=file_path)

        class_regex = re.compile(r'^\s*(?:export\s+|public\s+|private\s+|protected\s+|internal\s+)?(?:abstract\s+)?class\s+([A-Za-z0-9_]+)', re.MULTILINE)
        keyword_func_regex = re.compile(r'^\s*(?:export\s+|public\s+|private\s+|protected\s+|internal\s+)?(?:static\s+)?(?:async\s+)?(?:def|function|func|fn)\s+([A-Za-z0-9_]+)\s*(?:\(|(?=\s|$))', re.MULTILINE)
        c_func_regex = re.compile(r'^\s*(?:(?:public|private|protected|internal|static|inline|virtual|export)\s+)*[A-Za-z0-9_<>\[\]]+\s+([A-Za-z0-9_]+)\s*\([^)]*\)\s*\{', re.MULTILINE)

        for m in class_regex.finditer(content):
            name = m.group(1)
            line_num = content.count('\n', 0, m.start()) + 1
            module.classes.append(ClassInfo(name=name, start_line=line_num, end_line=line_num))

        for m in keyword_func_regex.finditer(content):
            name = m.group(1)
            line_num = content.count('\n', 0, m.start()) + 1
            module.functions.append(FunctionInfo(name=name, start_line=line_num, end_line=line_num))

        for m in c_func_regex.finditer(content):
            name = m.group(1)
            # Exclude control flow structures that look like functions
            if name not in ["if", "for", "while", "switch", "catch"]:
                # Avoid duplicates if we already matched it via keyword_func_regex
                if not any(f.name == name for f in module.functions):
                    line_num = content.count('\n', 0, m.start()) + 1
                    module.functions.append(FunctionInfo(name=name, start_line=line_num, end_line=line_num))

        return module
