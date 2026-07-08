"""
universal_parser.py -- Universal Regex-based Parser.

Provides a fallback parser that uses regular expressions to extract
basic code structures (classes, functions) from languages that do not
have a dedicated AST parser implemented yet.
"""

import re
from pathlib import Path
from typing import Optional

from src.parser.base import (
    BaseParser,
    ClassInfo,
    FunctionInfo,
    MethodInfo,
    ModuleInfo,
    Visibility,
)


class UniversalParser(BaseParser):
    """Regex-based parser for non-Python languages."""

    # Regex for classes: matches `class Name` or `class Name {`
    _CLASS_RE = re.compile(r"^\s*class\s+([A-Za-z0-9_]+)", re.MULTILINE)

    # Regex for keyword-based functions (def, func, fn, function)
    _KW_FUNC_RE = re.compile(
        r"^\s*(?:(?:public|private|protected|static|export|default|async)\s+)*(?:def|func|fn|function)\s+([A-Za-z0-9_]+)\s*\(",
        re.MULTILINE
    )

    # Regex for C-family functions based on return type
    # e.g., `int main(`, `void doSomething (`, `std::string get_name()`
    # Matches a type (one or more words, maybe with ::, <, >, *, &), whitespace, name, and (
    _C_FUNC_RE = re.compile(
        r"^\s*(?:(?:public|private|protected|static|inline|virtual)\s+)*([A-Za-z0-9_:<>\*&]+)\s+([A-Za-z0-9_]+)\s*\(",
        re.MULTILINE
    )

    # We ignore standard keywords that might be mistaken for C-family function return types
    _C_FUNC_IGNORE = {"return", "if", "while", "for", "switch", "catch", "else"}

    def language(self) -> str:
        return "universal"

    def supported_extensions(self) -> list[str]:
        return [
            ".js", ".ts", ".jsx", ".tsx",
            ".java", ".c", ".cpp", ".cc", ".cxx", ".h", ".hpp",
            ".cs", ".go", ".rs", ".php", ".rb", ".swift", ".kt"
        ]

    def parse_file(self, file_path: Path) -> ModuleInfo:
        """Parse a source file using regular expressions.

        Args:
            file_path: Path to the source file.

        Returns:
            A populated ModuleInfo.
        """
        module_info = ModuleInfo(file_path=file_path)

        try:
            content = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            # Try latin-1 if utf-8 fails
            content = file_path.read_text(encoding="latin-1")

        lines = content.splitlines()

        # Find classes
        for match in self._CLASS_RE.finditer(content):
            name = match.group(1)
            line_no = self._get_line_number(content, match.start())
            cls = ClassInfo(name=name, start_line=line_no, end_line=line_no)
            module_info.classes.append(cls)

        # Track found function names to avoid duplicates
        found_funcs = set()

        # Find keyword-based functions
        for match in self._KW_FUNC_RE.finditer(content):
            name = match.group(1)
            if name in found_funcs:
                continue
            found_funcs.add(name)
            line_no = self._get_line_number(content, match.start())
            func = FunctionInfo(name=name, start_line=line_no, end_line=line_no)
            module_info.functions.append(func)

        # Find C-family functions
        for match in self._C_FUNC_RE.finditer(content):
            ret_type = match.group(1)
            name = match.group(2)
            if name in found_funcs or ret_type in self._C_FUNC_IGNORE or ret_type == name:
                continue
            found_funcs.add(name)
            line_no = self._get_line_number(content, match.start())
            func = FunctionInfo(
                name=name,
                return_type=ret_type,
                start_line=line_no,
                end_line=line_no
            )
            module_info.functions.append(func)

        return module_info

    def _get_line_number(self, text: str, index: int) -> int:
        """Calculate line number (1-based) from character index."""
        return text.count("\n", 0, index) + 1
