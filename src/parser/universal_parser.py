from __future__ import annotations

import re
from pathlib import Path

from src.parser.base import (
    BaseParser,
    ClassInfo,
    FunctionInfo,
    ModuleInfo,
    ParseResult,
    Visibility,
)


class UniversalParser(BaseParser):
    """Fallback parser for non-Python languages using regular expressions.

    Extracts basic class and function structures from languages like
    C/C++, Java, JavaScript, Rust, Go, etc., handling both keyword-based
    and C-family return-type-based declarations.
    """

    def __init__(self, extensions: list[str]) -> None:
        """Initialize the UniversalParser with a list of extensions.

        Args:
            extensions: A list of extensions including the leading dot.
        """
        self._extensions = extensions

    def language(self) -> str:
        """Return a generic language identifier.

        Returns:
            The string "universal".
        """
        return "universal"

    def supported_extensions(self) -> list[str]:
        """Return the file extensions this parser is configured to handle.

        Returns:
            A list of extension strings.
        """
        return self._extensions

    def parse_file(self, file_path: Path) -> ModuleInfo:
        """Parse a single source file using regex heuristics.

        Args:
            file_path: Absolute or relative path to the source file.

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
            # Fallback if it's not strictly utf-8
            source = file_path.read_text(encoding="latin-1")

        module_info = ModuleInfo(file_path=file_path)

        # Basic regex to find classes (e.g. class MyClass {)
        class_pattern = re.compile(
            r'\b(?:class|struct|interface)\s+([a-zA-Z_]\w*)',
            re.MULTILINE
        )
        for match in class_pattern.finditer(source):
            class_name = match.group(1)
            # Estimate line number by counting newlines before the match
            start_line = source.count('\n', 0, match.start()) + 1

            module_info.classes.append(ClassInfo(
                name=class_name,
                start_line=start_line,
                end_line=start_line, # End line is a rough estimate
                visibility=Visibility.PUBLIC
            ))

        # Regex for keyword-based functions (def, func, fn, function)
        kw_func_pattern = re.compile(
            r'\b(?:def|func|fn|function)\s+([a-zA-Z_]\w*)\s*\(',
            re.MULTILINE
        )

        # Regex for C-family functions (return_type name(args))
        # This is quite permissive and might catch false positives
        c_func_pattern = re.compile(
            r'^\s*(?:(?:public|private|protected|static|inline|virtual)\s+)*[a-zA-Z_][a-zA-Z0-9_:<>\*&]*\s+([a-zA-Z_]\w*)\s*\(',
            re.MULTILINE
        )

        found_functions: set[str] = set()

        def add_function(match: re.Match) -> None:
            func_name = match.group(1)
            # Ignore some common keywords that might match the C-pattern
            if func_name in {"if", "for", "while", "switch", "catch"}:
                return
            if func_name in found_functions:
                return

            found_functions.add(func_name)
            start_line = source.count('\n', 0, match.start()) + 1

            module_info.functions.append(FunctionInfo(
                name=func_name,
                start_line=start_line,
                end_line=start_line,
                visibility=Visibility.PUBLIC
            ))

        for match in kw_func_pattern.finditer(source):
            add_function(match)

        for match in c_func_pattern.finditer(source):
            add_function(match)

        return module_info
