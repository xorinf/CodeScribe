"""
universal_parser.py -- Fallback regex-based parser for any language.

Provides a rough extraction of classes and functions for languages
that do not yet have a dedicated AST parser.
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
)


class UniversalParser(BaseParser):
    """Regex-based parser for non-Python languages.

    Acts as a fallback to extract basic class and function structures
    handling both keyword-based and C-family return-type-based declarations.
    """

    def language(self) -> str:
        return "universal"

    def supported_extensions(self) -> list[str]:
        # Broad list of supported extensions
        return [
            ".js", ".jsx", ".ts", ".tsx",
            ".java", ".cpp", ".cc", ".c", ".h", ".hpp",
            ".cs", ".go", ".rs", ".rb", ".php",
            ".swift", ".kt", ".scala", ".m", ".sh"
        ]

    def parse_file(self, file_path: Path) -> ModuleInfo:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        module_info = ModuleInfo(file_path=file_path)

        # 1. Match class definitions
        # Example: class MyClass { or class MyClass extends Base {
        class_pattern = re.compile(r"^\s*(?:public\s+|private\s+|protected\s+)?(?:abstract\s+)?class\s+([A-Za-z0-9_]+)", re.MULTILINE)
        for match in class_pattern.finditer(content):
            class_name = match.group(1)
            # Basic info since we can't easily parse bodies with regex reliably
            module_info.classes.append(ClassInfo(name=class_name))

        # 2. Match function/method definitions (keyword-based)
        # Example: def foo(), func foo(), fn foo(), function foo()
        keyword_func_pattern = re.compile(r"^\s*(?:public\s+|private\s+|protected\s+)?(?:static\s+)?(?:def|func|fn|function)\s+([A-Za-z0-9_]+)\s*\(", re.MULTILINE)
        for match in keyword_func_pattern.finditer(content):
            func_name = match.group(1)
            module_info.functions.append(FunctionInfo(name=func_name))

        # 3. Match function/method definitions (C-family return type based)
        # Example: int main(int argc, char** argv) {
        # Match type (one or more words/symbols), space, name, opening parenthesis
        # We need to be careful to avoid keywords like 'if', 'while', 'for', 'switch', 'catch'
        cfamily_func_pattern = re.compile(r"^\s*(?:public\s+|private\s+|protected\s+)?(?:static\s+|virtual\s+|inline\s+)?(?:[A-Za-z_][A-Za-z0-9_:<>\*&]*\s+)+([A-Za-z_][A-Za-z0-9_]*)\s*\(", re.MULTILINE)

        reserved_words = {"if", "for", "while", "switch", "catch", "return"}

        for match in cfamily_func_pattern.finditer(content):
            func_name = match.group(1)
            if func_name not in reserved_words:
                # Also avoid re-adding if already found by keyword
                if not any(f.name == func_name for f in module_info.functions):
                    module_info.functions.append(FunctionInfo(name=func_name))

        return module_info
