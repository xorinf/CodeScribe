"""
universal_parser.py -- Fallback Parser for Supported Non-Python Languages.

This parser provides basic extraction of class and function structures from
non-Python languages using regular expressions. It acts as a fallback to
ensure the documentation engine can generate basic structure for a wide
range of languages.
"""

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
    """Regex-based parser for non-Python languages."""

    def language(self) -> str:
        return "universal"

    def supported_extensions(self) -> list[str]:
        return [
            ".js", ".ts", ".java", ".c", ".cpp", ".cs", ".go",
            ".rs", ".rb", ".php", ".swift", ".kt",
            ".h", ".hpp", ".cc", ".hh"
        ]

    def parse_file(self, file_path: Path) -> ModuleInfo:
        file_path = Path(file_path).resolve()
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            source = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            # Skip unreadable files gracefully for a universal parser
            return ModuleInfo(file_path=file_path)

        module_info = ModuleInfo(file_path=file_path)

        # Basic regex to match class declarations
        # e.g., class MyClass, class MyClass extends Base
        class_pattern = re.compile(r'\bclass\s+([a-zA-Z_]\w*)\b')
        for match in class_pattern.finditer(source):
            class_name = match.group(1)
            # Estimate line number by counting newlines before the match
            start_line = source.count('\n', 0, match.start()) + 1
            module_info.classes.append(ClassInfo(
                name=class_name,
                visibility=Visibility.PUBLIC,
                start_line=start_line,
                end_line=start_line, # simple estimation
            ))

        # Basic regex to match function declarations
        # keyword-based (def, func, fn, function)
        # e.g. function doSomething(), def do_something():
        keyword_func_pattern = re.compile(
            r'\b(?:def|func|fn|function)\s+([a-zA-Z_]\w*)\s*\('
        )
        for match in keyword_func_pattern.finditer(source):
            func_name = match.group(1)
            start_line = source.count('\n', 0, match.start()) + 1
            module_info.functions.append(FunctionInfo(
                name=func_name,
                visibility=Visibility.PUBLIC,
                start_line=start_line,
                end_line=start_line, # simple estimation
            ))

        # C-family return-type-based function declarations
        # (Very naive, looks for type name, function name, parentheses)
        # e.g., int main(int argc), void doSomething()
        # Note: we avoid keywords like if, while, for, switch, catch, etc.
        c_func_pattern = re.compile(
            r'^(?:\s*(?:public|private|protected|static|inline|virtual)\s+)*'
            r'([a-zA-Z_][\w<>\[\]]*)\s+'
            r'([a-zA-Z_]\w*)\s*\([^)]*\)\s*(?:const\s*)?\{?',
            re.MULTILINE
        )

        # keywords to exclude from matching as a return type or function name
        reserved = {
            "if", "while", "for", "switch", "catch", "return",
            "class", "struct", "new", "delete", "throw"
        }

        for match in c_func_pattern.finditer(source):
            ret_type = match.group(1)
            func_name = match.group(2)

            if ret_type in reserved or func_name in reserved:
                continue

            # avoid double counting functions caught by keyword regex if any language mixes both somehow
            if not any(f.name == func_name for f in module_info.functions):
                start_line = source.count('\n', 0, match.start()) + 1
                module_info.functions.append(FunctionInfo(
                    name=func_name,
                    return_type=ret_type,
                    visibility=Visibility.PUBLIC,
                    start_line=start_line,
                    end_line=start_line,
                ))

        return module_info
