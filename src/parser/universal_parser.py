"""
universal_parser.py -- Fallback regex-based parser for multiple languages.

Uses regular expressions to extract basic class and function structures
from non-Python languages. It handles both keyword-based (e.g., def, func, fn)
and C-family return-type-based declarations.
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
    """Fallback parser for languages without dedicated AST support.

    Extracts top-level classes and functions using heuristics (regex).
    """

    def __init__(self, language_name: str, extensions: list[str]) -> None:
        """Initialize the universal parser for a specific language.

        Args:
            language_name: The name of the language (e.g., "javascript").
            extensions: A list of supported file extensions (e.g., [".js"]).
        """
        self._language = language_name
        self._extensions = extensions

        # Regex patterns
        self._class_pattern = re.compile(
            r'\b(?:(?:public|private|protected|abstract|static|final|export)\s+)*class\s+([a-zA-Z_][a-zA-Z0-9_]*)'
        )

        # e.g., function myJsFunc(), fn rust_func(), func goFunc()
        self._func_keyword_pattern = re.compile(
            r'\b(?:(?:public|private|protected|static|async|export)\s+)*(?:def|func|function|fn)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\('
        )

        # e.g., int myMethod(), std::string get_string()
        self._func_ctype_pattern = re.compile(
            r'\b(?:(?:public|private|protected|static|virtual|inline|async|constexpr|export)\s+)*(?!def|func|function|fn|if|for|while|switch|catch|return)([a-zA-Z_][a-zA-Z0-9_<>:\[\]\*&]*)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\('
        )

    def language(self) -> str:
        return self._language

    def supported_extensions(self) -> list[str]:
        return self._extensions

    def parse_file(self, file_path: Path) -> ModuleInfo:
        """Parse a single source file using regex heuristics.

        Args:
            file_path: Absolute or relative path to the source file.

        Returns:
            A ModuleInfo dataclass populated with the parsed elements.
        """
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            raise RuntimeError(f"Failed to read file: {e}")

        module = ModuleInfo(file_path=file_path)

        # Find classes
        for match in self._class_pattern.finditer(content):
            class_name = match.group(1)
            # Simplistic visibility and line number (regex doesn't give us lines easily without more work,
            # but we can count newlines up to the match start)
            start_line = content.count('\n', 0, match.start()) + 1

            # Simple visibility check
            match_str = match.group(0).lower()
            visibility = Visibility.PUBLIC
            if "private" in match_str:
                visibility = Visibility.PRIVATE
            elif "protected" in match_str:
                visibility = Visibility.PROTECTED

            module.classes.append(
                ClassInfo(
                    name=class_name,
                    visibility=visibility,
                    start_line=start_line,
                    end_line=start_line, # Regex can't easily find end_line for blocks
                )
            )

        # Find keyword functions
        for match in self._func_keyword_pattern.finditer(content):
            func_name = match.group(1)
            start_line = content.count('\n', 0, match.start()) + 1

            match_str = match.group(0).lower()
            visibility = Visibility.PUBLIC
            if "private" in match_str:
                visibility = Visibility.PRIVATE
            elif "protected" in match_str:
                visibility = Visibility.PROTECTED

            module.functions.append(
                FunctionInfo(
                    name=func_name,
                    visibility=visibility,
                    start_line=start_line,
                    end_line=start_line,
                )
            )

        # Find C-type functions
        for match in self._func_ctype_pattern.finditer(content):
            return_type = match.group(1)
            func_name = match.group(2)

            # Skip common keywords that might look like return types
            if return_type in ("else", "new", "class"):
                continue

            start_line = content.count('\n', 0, match.start()) + 1

            match_str = match.group(0).lower()
            visibility = Visibility.PUBLIC
            if "private" in match_str:
                visibility = Visibility.PRIVATE
            elif "protected" in match_str:
                visibility = Visibility.PROTECTED

            module.functions.append(
                FunctionInfo(
                    name=func_name,
                    return_type=return_type,
                    visibility=visibility,
                    start_line=start_line,
                    end_line=start_line,
                )
            )

        return module
