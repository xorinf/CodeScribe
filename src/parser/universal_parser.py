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
    def language(self) -> str:
        return "universal"

    def supported_extensions(self) -> list[str]:
        return [
            ".js", ".ts", ".java", ".cpp", ".c", ".cs", ".go", ".rs", ".rb", ".php", ".swift", ".kt"
        ]

    def parse_file(self, file_path: Path) -> ModuleInfo:
        content = file_path.read_text(encoding="utf-8")

        module = ModuleInfo(file_path=file_path)

        # Regex for keyword-based functions (def, func, fn, function)
        kw_func_regex = re.compile(r'\b(?:def|func|fn|function)\s+([a-zA-Z_]\w*)\s*\(')
        # Regex for C-family functions (return_type name(args))
        # This is quite tricky to do perfectly with regex, but we do a best effort.
        c_func_regex = re.compile(r'^\s*(?:(?:public|private|protected|static|inline|virtual)\s+)*[a-zA-Z_]\w*(?:<[^>]+>)?[\*\&\s]+\s*([a-zA-Z_]\w*)\s*\(', re.MULTILINE)

        # Regex for class (class name)
        class_regex = re.compile(r'\b(?:class|struct|interface)\s+([a-zA-Z_]\w*)')

        for match in kw_func_regex.finditer(content):
            module.functions.append(FunctionInfo(name=match.group(1)))

        for match in c_func_regex.finditer(content):
            name = match.group(1)
            # prevent double-counting if keyword regex caught it
            if not any(f.name == name for f in module.functions):
                # Also ignore common control structures
                if name not in {"if", "for", "while", "switch", "catch"}:
                    module.functions.append(FunctionInfo(name=name))

        for match in class_regex.finditer(content):
            module.classes.append(ClassInfo(name=match.group(1)))

        return module
