"""
universal_parser.py -- Regex-Based Fallback Parser for Multi-Language Support.

Extracts basic classes and functions using heuristic regex patterns.
"""

from __future__ import annotations

import re
from pathlib import Path

from src.parser.base import (
    BaseParser,
    ClassInfo,
    FunctionInfo,
    ModuleInfo,
)


class UniversalParser(BaseParser):
    """Regex-based fallback parser for extracting basic structure."""

    def __init__(self, language: str, extensions: list[str]) -> None:
        self._language = language
        self._extensions = extensions

    def language(self) -> str:
        return self._language

    def supported_extensions(self) -> list[str]:
        return self._extensions

    def parse_file(self, file_path: Path) -> ModuleInfo:
        file_path = Path(file_path).resolve()
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            content = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            content = file_path.read_text(encoding="latin-1", errors="ignore")

        module_info = ModuleInfo(file_path=file_path)

        # Regex to find class definitions
        class_re = re.compile(r'\bclass\s+([A-Za-z_][A-Za-z0-9_]*)\b')
        seen_classes = set()
        for match in class_re.finditer(content):
            name = match.group(1)
            if name not in seen_classes:
                module_info.classes.append(ClassInfo(name=name))
                seen_classes.add(name)

        seen_functions = set()
        # Regex to find keyword-based functions
        kw_func_re = re.compile(r'\b(?:def|func|fn|function)\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(')
        for match in kw_func_re.finditer(content):
            name = match.group(1)
            if name not in seen_functions:
                module_info.functions.append(FunctionInfo(name=name))
                seen_functions.add(name)

        # Regex to find C-family return-type-based functions
        c_func_re = re.compile(
            r'^[ \t]*(?:(?:public|private|protected|static|virtual|inline|constexpr)\s+)*'
            r'(?!(?:return|else|elif|if|while|for|switch|catch)\b)'
            r'(?:[A-Za-z_][A-Za-z0-9_<>:\[\]]*\s*[*&]*\s+)+'
            r'([A-Za-z_][A-Za-z0-9_]*)\s*\(',
            re.MULTILINE
        )
        for match in c_func_re.finditer(content):
            name = match.group(1)
            if name not in seen_functions:
                module_info.functions.append(FunctionInfo(name=name))
                seen_functions.add(name)

        return module_info
