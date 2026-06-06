"""
universal_parser.py -- Fallback Parser for Unsupported Languages.

Uses regular expressions to extract basic class and function structures
from a variety of programming languages. While less accurate than
AST-based parsing, it provides baseline documentation generation
for languages that lack dedicated parser implementations.
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
    Visibility,
)


class UniversalParser(BaseParser):
    """Regex-based parser for extracting basic code structures.

    Supports a wide variety of C-family and keyword-based languages
    by matching common function and class declaration patterns.
    """

    def language(self) -> str:
        return "universal"

    def supported_extensions(self) -> list[str]:
        return [
            ".js", ".ts", ".go", ".rs", ".c", ".cpp", ".cc", ".h", ".hpp",
            ".java", ".cs", ".rb", ".php", ".swift", ".kt", ".scala",
            ".dart", ".m", ".mm",
        ]

    def parse_file(self, file_path: Path) -> ModuleInfo:
        """Parse a source file using regex heuristics.

        Extracts class names, keyword-based functions (def, func, etc.),
        and C-family return-type-based functions.
        """
        file_path = Path(file_path).resolve()

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        source = file_path.read_text(encoding="utf-8", errors="replace")

        module_info = ModuleInfo(file_path=file_path)

        # Extract classes: `class X {`
        class_pattern = re.compile(r'\bclass\s+([a-zA-Z_]\w*)')
        for match in class_pattern.finditer(source):
            class_name = match.group(1)
            # Check visibility from previous tokens maybe, default to PUBLIC
            module_info.classes.append(ClassInfo(
                name=class_name,
                visibility=Visibility.PUBLIC,
            ))

        # Extract keyword-based functions: `def|func|fn|function X(...)`
        kw_pattern = re.compile(r'\b(?:def|func|fn|function)\s+([a-zA-Z_]\w*)')
        for match in kw_pattern.finditer(source):
            func_name = match.group(1)
            module_info.functions.append(FunctionInfo(
                name=func_name,
                visibility=Visibility.PUBLIC,
            ))

        # Extract C-family return-type functions: `ReturnType FuncName(...)`
        c_pattern = re.compile(
            r'^[ \t]*'
            r'(?:(?:public|private|protected|static|virtual|inline|const|volatile)[ \t]+)*'
            r'(?!(?:def|func|fn|function|class|return|if|for|while|switch|catch|new|delete)\b)'
            r'([a-zA-Z_][a-zA-Z0-9_<>:]*(?:[ \t]*[*&]+)*)[ \t]+'
            r'([*&]*[ \t]*[a-zA-Z_]\w*)[ \t]*\(',
            re.MULTILINE
        )
        for match in c_pattern.finditer(source):
            return_type = match.group(1).strip()
            func_name_raw = match.group(2).strip()

            # Clean up function name if it starts with * or &
            func_name = re.sub(r'^[*&\s]+', '', func_name_raw)

            module_info.functions.append(FunctionInfo(
                name=func_name,
                return_type=return_type,
                visibility=Visibility.PUBLIC,
            ))

        return module_info
