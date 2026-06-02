"""
universal_parser.py -- Fallback Parser for Multiple Languages using Regex.

This module provides a UniversalParser that extracts basic class and function
structures from non-Python languages using regular expressions. It acts as a
fallback mechanism for languages not yet supported by dedicated AST parsers.
"""

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
    """Regex-based parser for unsupported languages."""

    def language(self) -> str:
        return "universal"

    def supported_extensions(self) -> list[str]:
        # Support a broad set of common languages as fallback
        return [
            ".js", ".ts", ".java", ".c", ".cpp", ".cs", ".rb", ".go",
            ".rs", ".php", ".swift", ".kt", ".scala", ".m", ".h", ".hpp"
        ]

    def parse_file(self, file_path: Path) -> ModuleInfo:
        file_path = Path(file_path).resolve()
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            source = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            # Fallback or skip if not decodable
            return ModuleInfo(file_path=file_path)

        module_info = ModuleInfo(file_path=file_path)

        # Regex for functions:
        # Handles keyword-based (def, function, func, fn, fun) and return-type-based (C/C++/Java style)
        func_pattern = re.compile(
            r'(?m)^\s*(?:public\s+|private\s+|protected\s+|static\s+|async\s+|export\s+|inline\s+|virtual\s+)*'
            r'(?:'
                r'(?:def|function|func|fn|fun)\s+([a-zA-Z_]\w*)'  # Keyword based
                r'|'
                r'(?:[a-zA-Z_][\w<>\[\]]*\s+)+([a-zA-Z_]\w*)'      # Return type based
            r')\s*\('
        )
        for match in func_pattern.finditer(source):
            # match.group(1) is keyword based, match.group(2) is return type based
            func_name = match.group(1) or match.group(2)
            # Avoid matching control flow statements as functions in C-style languages
            if func_name and func_name not in {"if", "for", "while", "switch", "catch"}:
                module_info.functions.append(FunctionInfo(
                    name=func_name,
                    visibility=Visibility.PUBLIC, # Simplify visibility
                ))

        # Regex for classes and structs: captures class/struct name
        class_pattern = re.compile(
            r'(?m)^\s*(?:public\s+|private\s+|protected\s+|export\s+|abstract\s+|type\s+)*'
            r'(?:class|struct|interface|protocol)\s+([a-zA-Z_]\w*)'
        )
        for match in class_pattern.finditer(source):
            class_name = match.group(1)
            module_info.classes.append(ClassInfo(
                name=class_name,
                visibility=Visibility.PUBLIC,
            ))

        return module_info
