import re
from pathlib import Path
from typing import Optional

from src.parser.base import BaseParser, ModuleInfo, ClassInfo, FunctionInfo


class UniversalParser(BaseParser):
    """
    A fallback parser that extracts basic class and function structures
    from non-Python languages using regular expressions.
    """

    def __init__(self, extensions: list[str] = None) -> None:
        self._extensions = extensions or []

        # Regex to match class definitions
        self.class_pattern = re.compile(r'\bclass\s+([A-Za-z0-9_]+)', re.MULTILINE)

        # Regex to match keyword-based function definitions (e.g., def, func, fn, function)
        self.kw_func_pattern = re.compile(r'\b(?:def|func|fn|function)\s+([A-Za-z0-9_]+)\s*\(', re.MULTILINE)

        # Regex to match C-family return-type-based function declarations
        # Matches: [modifiers] ReturnType funcName(
        self.c_func_pattern = re.compile(
            r'^[ \t]*(?:(?:public|private|protected|internal|static|virtual|override|inline|constexpr|async)\s+)*'
            r'[a-zA-Z_][a-zA-Z0-9_<>,:\[\]*&]*\s+'
            r'([a-zA-Z_]\w*)'
            r'\s*\(',
            re.MULTILINE
        )

    def language(self) -> str:
        return "universal"

    def supported_extensions(self) -> list[str]:
        return self._extensions

    def parse_file(self, file_path: Path) -> ModuleInfo:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        classes = []
        functions = []

        # Find classes
        for match in self.class_pattern.finditer(content):
            class_name = match.group(1)
            classes.append(ClassInfo(name=class_name))

        # Find keyword functions
        for match in self.kw_func_pattern.finditer(content):
            func_name = match.group(1)
            functions.append(FunctionInfo(name=func_name))

        # Find C-family functions
        for match in self.c_func_pattern.finditer(content):
            func_name = match.group(1)
            # Basic deduplication
            if not any(f.name == func_name for f in functions):
                # Filter out control flow that looks like function calls
                if func_name not in ["if", "for", "while", "switch", "catch", "return"]:
                    functions.append(FunctionInfo(name=func_name))

        return ModuleInfo(
            file_path=file_path,
            classes=classes,
            functions=functions
        )
