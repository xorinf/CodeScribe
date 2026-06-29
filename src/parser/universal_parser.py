"""
universal_parser.py -- Fallback Parser for Multiple Languages.

Uses regex to extract basic class and function structures from non-Python
languages. This acts as a fallback for languages that do not yet have a
dedicated AST parser.
"""

from __future__ import annotations

import re
from pathlib import Path

from src.parser.base import (
    BaseParser,
    ClassInfo,
    FunctionInfo,
    ModuleInfo,
    Visibility,
)

class UniversalParser(BaseParser):
    """Regex-based fallback parser for generic programming languages."""

    def language(self) -> str:
        return "universal"

    def supported_extensions(self) -> list[str]:
        return [
            ".js", ".ts", ".cpp", ".c", ".h", ".go", ".rs", ".java",
            ".rb", ".php", ".cs", ".swift", ".kt"
        ]

    def parse_file(self, file_path: Path) -> ModuleInfo:
        file_path = Path(file_path).resolve()
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        source = file_path.read_text(encoding="utf-8", errors="replace")
        module_info = ModuleInfo(file_path=file_path)

        # Basic regex to match class definitions
        class_pattern = re.compile(
            r'^\s*(?:export\s+|public\s+|private\s+|protected\s+)*class\s+([A-Za-z_][A-Za-z0-9_]*)',
            re.MULTILINE
        )

        # Regex for keyword-based functions (def, func, fn, function)
        kw_func_pattern = re.compile(
            r'^\s*(?:export\s+|public\s+|private\s+|protected\s+|async\s+)*(?:def|func|fn|function)\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(',
            re.MULTILINE
        )

        # Regex for C-family return-type-based functions
        c_func_pattern = re.compile(
            r'^\s*(?:(?:export|public|private|protected|static|inline|virtual|constexpr)\s+)*([A-Za-z_][A-Za-z0-9_<>:*\s&]*)\s+([A-Za-z_][A-Za-z0-9_]*)\s*\([^)]*\)\s*(?:const\s*)?(?:\{|;|\n|:)',
            re.MULTILINE
        )

        # Extract classes
        for m in class_pattern.finditer(source):
            class_name = m.group(1)
            module_info.classes.append(
                ClassInfo(name=class_name, visibility=Visibility.PUBLIC)
            )

        # Extract keyword-based functions
        for m in kw_func_pattern.finditer(source):
            func_name = m.group(1)
            module_info.functions.append(
                FunctionInfo(name=func_name, visibility=Visibility.PUBLIC)
            )

        # Extract C-style functions
        ignored_names = {'if', 'while', 'for', 'switch', 'catch', 'return', 'else'}
        ignored_returns = {'return', 'class', 'struct', 'enum', 'def', 'func', 'fn', 'function'}
        for m in c_func_pattern.finditer(source):
            ret_type = m.group(1).strip()
            func_name = m.group(2).strip()

            if func_name not in ignored_names and ret_type not in ignored_returns:
                # Basic heuristic to ensure it's actually a return type
                if not any(char in ret_type for char in "()="):
                    module_info.functions.append(
                        FunctionInfo(name=func_name, return_type=ret_type, visibility=Visibility.PUBLIC)
                    )

        return module_info
