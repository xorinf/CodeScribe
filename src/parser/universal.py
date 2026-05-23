"""
universal.py -- Fallback Parser for Unsupported Languages.

Uses a broad, regex-based approach to extract basic class and
function structures from any text-based source file when a dedicated
language parser is not available.
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
    ParseResult,
    Visibility,
)

class UniversalParser(BaseParser):
    """Regex-based fallback parser for unsupported languages."""

    def __init__(self) -> None:
        self._class_pattern = re.compile(
            r"^\s*(?:export\s+|public\s+|private\s+|protected\s+|abstract\s+|sealed\s+)*(?:class|struct|interface|trait|enum)\s+([A-Za-z_][A-Za-z0-9_]*)",
            re.MULTILINE
        )

        self._func_kw_pattern = re.compile(
            r"^\s*(?:export\s+|public\s+|private\s+|protected\s+|static\s+|async\s+|inline\s+)*(?:def|function|fn|func)\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(",
            re.MULTILINE
        )

        self._c_func_pattern = re.compile(
            r"^\s*(?:export\s+|public\s+|private\s+|protected\s+|static\s+|virtual\s+|inline\s+|override\s+|final\s+)*[A-Za-z_][A-Za-z0-9_<>\[\]]*\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(",
            re.MULTILINE
        )

    def language(self) -> str:
        return "universal"

    def supported_extensions(self) -> list[str]:
        return []

    def can_parse(self, file_path: Path) -> bool:
        return True

    def parse_file(self, file_path: Path) -> ModuleInfo:
        file_path = Path(file_path).resolve()
        module_info = ModuleInfo(file_path=file_path)

        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception:
            return module_info

        for match in self._class_pattern.finditer(content):
            class_name = match.group(1)
            module_info.classes.append(ClassInfo(name=class_name))

        found_funcs = set()
        for match in self._func_kw_pattern.finditer(content):
            func_name = match.group(1)
            found_funcs.add(func_name)
            module_info.functions.append(FunctionInfo(name=func_name))

        for match in self._c_func_pattern.finditer(content):
            func_name = match.group(1)
            if func_name not in found_funcs and func_name not in ("if", "for", "while", "catch", "switch"):
                found_funcs.add(func_name)
                module_info.functions.append(FunctionInfo(name=func_name))

        return module_info
