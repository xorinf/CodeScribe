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
    """A regex-based universal parser for non-Python languages.

    Extracts basic structures like classes and functions.
    """

    def language(self) -> str:
        return "universal"

    def supported_extensions(self) -> list[str]:
        return [
            ".js", ".ts", ".go", ".rs", ".java",
            ".cpp", ".c", ".cs", ".rb", ".php",
            ".swift", ".kt", ".scala"
        ]

    def parse_file(self, file_path: Path) -> ModuleInfo:
        content = file_path.read_text(encoding="utf-8", errors="replace")

        classes = []
        functions = []

        # Class matching: class ClassName
        class_pattern = re.compile(r'\bclass\s+([A-Za-z0-9_]+)', re.MULTILINE)
        for match in class_pattern.finditer(content):
            class_name = match.group(1)
            # Basic approximation of line number
            start_line = content[:match.start()].count('\n') + 1
            classes.append(
                ClassInfo(
                    name=class_name,
                    start_line=start_line,
                    end_line=start_line, # approximate
                )
            )

        # Keyword function matching: def/fn/func/function Name(...)
        func_pattern = re.compile(r'\b(?:def|fn|func|function)\s+([A-Za-z0-9_]+)\s*\(', re.MULTILINE)
        for match in func_pattern.finditer(content):
            func_name = match.group(1)
            start_line = content[:match.start()].count('\n') + 1
            functions.append(
                FunctionInfo(
                    name=func_name,
                    start_line=start_line,
                    end_line=start_line, # approximate
                )
            )

        # C-family function matching: return_type name(...)
        # e.g. int main(int argc)
        c_func_pattern = re.compile(
            r'^\s*(?:(?:inline|static|virtual|public|private|protected)\s+)*'
            r'([A-Za-z0-9_<>:,\s\*&]+)\s+([A-Za-z0-9_]+)\s*\([^;\{]*\)\s*(?:const)?\s*\{',
            re.MULTILINE
        )
        for match in c_func_pattern.finditer(content):
            return_type = match.group(1).strip()
            func_name = match.group(2).strip()

            # Filter out common false positives
            if func_name in ["if", "for", "while", "switch", "catch", "else"] or return_type in ["else"]:
                continue

            start_line = content[:match.start()].count('\n') + 1
            functions.append(
                FunctionInfo(
                    name=func_name,
                    return_type=return_type,
                    start_line=start_line,
                    end_line=start_line, # approximate
                )
            )

        # Deduplicate functions by name and line
        unique_funcs = {}
        for f in functions:
            key = (f.name, f.start_line)
            if key not in unique_funcs:
                unique_funcs[key] = f

        return ModuleInfo(
            file_path=file_path,
            classes=classes,
            functions=list(unique_funcs.values()),
        )
