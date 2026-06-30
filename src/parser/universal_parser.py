from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

from src.parser.base import (
    BaseParser,
    ClassInfo,
    FunctionInfo,
    ModuleInfo,
)


class UniversalParser(BaseParser):
    """Fallback parser for non-Python languages using regular expressions.

    Extracts basic class and function structures from source code across
    a variety of languages by matching common structural patterns.
    """

    def language(self) -> str:
        """Return the language identifier this parser handles."""
        return "universal"

    def supported_extensions(self) -> list[str]:
        """Return the file extensions this parser can handle."""
        return [
            ".js", ".jsx", ".ts", ".tsx",
            ".java", ".cpp", ".cc", ".c", ".h", ".hpp",
            ".cs", ".go", ".rs", ".php", ".rb", ".kt",
            ".swift", ".scala", ".m", ".mm"
        ]

    def parse_file(self, file_path: Path) -> ModuleInfo:
        """Parse a source file using regex to find classes and functions.

        Args:
            file_path: Absolute or relative path to the source file.

        Returns:
            A ModuleInfo dataclass populated with the parsed elements.
        """
        module = ModuleInfo(file_path=file_path)

        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
        except Exception:
            return module

        # 1. Class declarations
        class_regex = re.compile(
            r'^[ \t]*(?:export\s+|public\s+|private\s+|protected\s+|abstract\s+|final\s+)*class\s+([A-Za-z_][A-Za-z0-9_]*)',
            re.MULTILINE
        )
        for match in class_regex.finditer(content):
            name = match.group(1)
            line_no = content[:match.start()].count('\n') + 1
            module.classes.append(ClassInfo(name=name, start_line=line_no, end_line=line_no))

        # 2. Keyword-based function declarations (def, func, fn, function)
        kw_func_regex = re.compile(
            r'^[ \t]*(?:export\s+|public\s+|private\s+|protected\s+|async\s+|static\s+)*(?:def|func|fn|function)\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(',
            re.MULTILINE
        )
        for match in kw_func_regex.finditer(content):
            name = match.group(1)
            line_no = content[:match.start()].count('\n') + 1
            # Avoid duplicates if multiple regexes match
            if not any(f.name == name for f in module.functions):
                module.functions.append(
                    FunctionInfo(name=name, start_line=line_no, end_line=line_no)
                )

        # 3. C-family return-type-based function declarations
        # Matches patterns like: `int main(...) {` or `public void doSomething() {`
        c_func_regex = re.compile(
            r'^[ \t]*(?:(?:public|private|protected|static|inline|virtual|override|final|async)\s+)*'
            r'([A-Za-z_][A-Za-z0-9_<>,: \t*&\[\]]*?)\s+'
            r'([A-Za-z_][A-Za-z0-9_]*)\s*'
            r'\([^)]*\)\s*'
            r'(?:const\s*)?(?:noexcept\s*)?(?:throws[^{]+)?'
            r'\{',
            re.MULTILINE
        )
        for match in c_func_regex.finditer(content):
            ret_type = match.group(1).strip()
            name = match.group(2)

            # Filter out common control flow keywords that look like function calls
            if name in ('if', 'for', 'while', 'switch', 'catch', 'else', 'return'):
                continue

            # Skip if the return type looks like a keyword (which means it's likely a keyword-based declaration we already caught or should catch)
            if any(ret_type.endswith(kw) for kw in ['def', 'func', 'fn', 'function', 'class']):
                continue

            line_no = content[:match.start()].count('\n') + 1

            # Avoid duplicates
            if not any(f.name == name for f in module.functions):
                module.functions.append(
                    FunctionInfo(name=name, return_type=ret_type, start_line=line_no, end_line=line_no)
                )

        return module
