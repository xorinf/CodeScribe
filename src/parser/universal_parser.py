"""
universal_parser.py -- Regex-based fallback parser for non-Python languages.
"""

import re
from pathlib import Path

from src.parser.base import (
    BaseParser,
    ClassInfo,
    FunctionInfo,
    ModuleInfo,
)

class UniversalParser(BaseParser):
    """Fallback parser that uses regex to extract basic structure."""

    def language(self) -> str:
        return "universal"

    def supported_extensions(self) -> list[str]:
        return [
            ".js", ".jsx", ".ts", ".tsx",
            ".java", ".cpp", ".c", ".h", ".cs",
            ".go", ".rb", ".php", ".swift", ".kt",
            ".rs", ".m", ".mm"
        ]

    def parse_file(self, file_path: Path) -> ModuleInfo:
        content = file_path.read_text(encoding="utf-8", errors="ignore")

        module = ModuleInfo(file_path=file_path)

        # Regex for keyword-based functions (def, func, fn, function)
        keyword_func_re = re.compile(
            r"^\s*(?:public\s+|private\s+|protected\s+|static\s+|export\s+|async\s+)*(?:def|func|fn|function)\s+([a-zA-Z_]\w*)\s*\(",
            re.MULTILINE
        )
        for match in keyword_func_re.finditer(content):
            func_name = match.group(1)
            start_idx = match.start()
            line_no = content.count("\n", 0, start_idx) + 1
            module.functions.append(FunctionInfo(name=func_name, start_line=line_no, end_line=line_no))

        # Regex for C-family return-type-based declarations
        c_func_re = re.compile(
            r"^\s*(?:public\s+|private\s+|protected\s+|static\s+|virtual\s+|inline\s+)*"
            r"(?:[a-zA-Z_]\w*(?:<[^>]+>)?[\*\&\s]+)+"
            r"([a-zA-Z_]\w*)\s*\([^)]*\)\s*(?:const\s*)?\{",
            re.MULTILINE
        )
        for match in c_func_re.finditer(content):
            func_name = match.group(1)
            if func_name in {"if", "while", "for", "catch", "switch", "return"}:
                continue
            start_idx = match.start()
            line_no = content.count("\n", 0, start_idx) + 1

            # Avoid adding duplicates if somehow both regexes matched
            if not any(f.name == func_name and f.start_line == line_no for f in module.functions):
                module.functions.append(FunctionInfo(name=func_name, start_line=line_no, end_line=line_no))

        # Regex for class declarations
        class_re = re.compile(
            r"^\s*(?:public\s+|private\s+|protected\s+|export\s+|abstract\s+|final\s+)*class\s+([a-zA-Z_]\w*)",
            re.MULTILINE
        )
        for match in class_re.finditer(content):
            class_name = match.group(1)
            start_idx = match.start()
            line_no = content.count("\n", 0, start_idx) + 1
            module.classes.append(ClassInfo(name=class_name, start_line=line_no, end_line=line_no))

        return module
