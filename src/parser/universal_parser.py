"""
universal_parser.py -- Fallback Regex-Based Parser for Any Language.

Uses regular expressions to extract basic structural information (classes
and functions) from any programming language. It relies on common keywords
(def, function, func, fn) or C-family return-type syntax.
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
    """Regex-based parser to support basic extraction for non-Python languages."""

    # Keywords that often appear at the start of a C-family function
    # return type position but are not actual return types.
    RESERVED_KEYWORDS = {
        "class", "if", "for", "while", "switch", "catch", "return", "def", "function", "func", "fn"
    }

    # Regex for class extraction (e.g. `class MyClass`)
    CLASS_PATTERN = re.compile(r'\bclass\s+([a-zA-Z_]\w*)')

    # Regex for keyword-based functions (e.g. `def my_func(`)
    KW_FUNC_PATTERN = re.compile(r'\b(?:def|function|func|fn)\s+([a-zA-Z_]\w*)\s*\(')

    # Regex for C-family functions based on return types:
    # Optional modifiers, followed by a return type (can have <T> or []),
    # followed by the function name, arguments in parentheses, and an opening brace, throws, or a colon.
    CFAM_FUNC_PATTERN = re.compile(
        r'^\s*(?:(?:public|private|protected|static|inline|virtual|override|final)\s+)*'
        r'([a-zA-Z_]\w*(?:<[^>]+>)?(?:\[\])?)\s+'
        r'([a-zA-Z_]\w*)\s*\([^)]*\)\s*(?:\{|throws|:\s*[^{]+{)',
        re.MULTILINE
    )

    def language(self) -> str:
        """Return the language identifier this parser handles."""
        return "universal"

    def supported_extensions(self) -> list[str]:
        """Return the file extensions this parser can handle."""
        return [
            ".js", ".jsx", ".ts", ".tsx",
            ".java", ".c", ".cpp", ".h", ".hpp", ".cs",
            ".go", ".rs", ".rb", ".php", ".swift", ".kt", ".m"
        ]

    def parse_file(self, file_path: Path) -> ModuleInfo:
        """Parse a single source file into a ModuleInfo structure."""
        content = file_path.read_text(encoding="utf-8", errors="ignore")

        module_info = ModuleInfo(file_path=file_path)

        # 1. Extract Classes
        for match in self.CLASS_PATTERN.finditer(content):
            class_name = match.group(1)
            # Create a simple ClassInfo, mapping to regex start/end index as 'lines' is not precise here
            # But line numbers aren't strict in regex
            start_idx = match.start()
            start_line = content.count('\n', 0, start_idx) + 1
            module_info.classes.append(ClassInfo(name=class_name, start_line=start_line, end_line=start_line))

        # 2. Extract Keyword-based Functions
        for match in self.KW_FUNC_PATTERN.finditer(content):
            func_name = match.group(1)
            start_idx = match.start()
            start_line = content.count('\n', 0, start_idx) + 1
            module_info.functions.append(FunctionInfo(name=func_name, start_line=start_line, end_line=start_line))

        # 3. Extract C-family Functions
        for match in self.CFAM_FUNC_PATTERN.finditer(content):
            ret_type = match.group(1)
            func_name = match.group(2)

            # Avoid matching keywords like 'if', 'for' as return types or function names
            if ret_type not in self.RESERVED_KEYWORDS and func_name not in self.RESERVED_KEYWORDS:
                start_idx = match.start()
                start_line = content.count('\n', 0, start_idx) + 1
                module_info.functions.append(FunctionInfo(
                    name=func_name,
                    return_type=ret_type,
                    start_line=start_line,
                    end_line=start_line
                ))

        return module_info
