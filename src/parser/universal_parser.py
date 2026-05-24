from __future__ import annotations

import re
from pathlib import Path

from src.parser.base import (
    BaseParser,
    ModuleInfo,
    ClassInfo,
    FunctionInfo,
    Visibility,
)


class UniversalParser(BaseParser):
    """Fallback parser for non-Python languages using regular expressions.

    Extracts basic class and function structures from non-Python languages.
    This parser doesn't construct full ASTs but relies on common patterns
    found across C-like languages (Java, C++, TS/JS, etc.).
    """

    def language(self) -> str:
        """Return the language identifier.

        Returns:
            The string "universal".
        """
        return "universal"

    def supported_extensions(self) -> list[str]:
        """Return supported file extensions for Universal parser.

        Returns:
            A list containing common non-Python extensions.
        """
        return [".js", ".ts", ".java", ".cpp", ".c", ".cs", ".go", ".rs"]

    def parse_file(self, file_path: Path) -> ModuleInfo:
        """Parse a single source file into a ModuleInfo structure using regex.

        Args:
            file_path: Path to the source file.

        Returns:
            A populated ModuleInfo dataclass.

        Raises:
            FileNotFoundError: If the file does not exist.
        """
        file_path = Path(file_path).resolve()

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            source = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            # Fallback to ignore for non-UTF8 files
            source = file_path.read_text(encoding="utf-8", errors="ignore")

        module_info = ModuleInfo(file_path=file_path)

        # Basic regex to find classes (e.g. `class MyClass {`)
        # This is very basic and won't catch everything perfectly.
        class_pattern = re.compile(r"class\s+([a-zA-Z_]\w*)\s*(?:extends\s+[a-zA-Z_]\w*\s*)?\{")
        for match in class_pattern.finditer(source):
            class_name = match.group(1)
            # Estimate line number simply by counting newlines before the match
            start_line = source.count("\n", 0, match.start()) + 1
            module_info.classes.append(
                ClassInfo(
                    name=class_name,
                    visibility=Visibility.PUBLIC,
                    start_line=start_line,
                    end_line=start_line, # Hard to determine end line without full parsing
                )
            )

        # Basic regex to find functions (e.g. `function myFunc(...)` or `type myFunc(...) {`)
        # This covers JS/TS 'function' keyword and C-like return-type functions
        func_pattern = re.compile(
            r"(?:(?:public|private|protected|static|export|async)\s+)*"
            r"(?:function\s+)?([a-zA-Z_]\w*)\s*\([^)]*\)\s*(?::\s*[a-zA-Z_]\w*\s*)?\{"
        )

        for match in func_pattern.finditer(source):
            func_name = match.group(1)

            # Filter out common control structures that look like functions
            if func_name in ("if", "for", "while", "switch", "catch"):
                continue

            start_line = source.count("\n", 0, match.start()) + 1
            module_info.functions.append(
                FunctionInfo(
                    name=func_name,
                    visibility=Visibility.PUBLIC,
                    start_line=start_line,
                    end_line=start_line,
                )
            )

        return module_info
