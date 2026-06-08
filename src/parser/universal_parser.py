"""
universal_parser.py -- Regex-based Universal Parser for Non-Python Languages.

Acts as a fallback to extract basic class and function structures from
non-Python languages using regular expressions. Handles both keyword-based
and C-family return-type-based declarations.
"""

from __future__ import annotations

import re
from pathlib import Path

from src.parser.base import (
    BaseParser,
    ClassInfo,
    FunctionInfo,
    MethodInfo,
    ModuleInfo,
    Visibility,
)


class UniversalParser(BaseParser):
    """Regex-based parser for non-Python languages."""

    def language(self) -> str:
        """Return the language identifier."""
        return "universal"

    def supported_extensions(self) -> list[str]:
        """Return supported file extensions for the universal parser."""
        return [
            ".js", ".ts", ".jsx", ".tsx",  # JavaScript / TypeScript
            ".java",                        # Java
            ".c", ".h",                     # C
            ".cpp", ".hpp", ".cc", ".hh",   # C++
            ".cs",                          # C#
            ".go",                          # Go
            ".rs",                          # Rust
            ".rb",                          # Ruby
            ".php",                         # PHP
            ".swift",                       # Swift
            ".kt", ".kts",                  # Kotlin
            ".m", ".mm",                    # Objective-C / Objective-C++
            ".scala",                       # Scala
            ".groovy",                      # Groovy
        ]

    def parse_file(self, file_path: Path) -> ModuleInfo:
        """Parse a source file using regular expressions.

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

        source = file_path.read_text(encoding="utf-8", errors="replace")
        lines = source.splitlines()

        module_info = ModuleInfo(file_path=file_path)

        # Basic regex for classes, structs, interfaces
        # e.g., class Foo { ... }
        #       struct Bar { ... }
        #       interface Baz { ... }
        class_pattern = re.compile(
            r'^\s*(?:public\s+|private\s+|protected\s+|internal\s+)?(?:abstract\s+|sealed\s+|final\s+)?(class|struct|interface|trait)\s+([a-zA-Z_]\w*)(?:\s*(?:extends|implements|:)\s*([a-zA-Z0-9_<>, \t]+))?\s*\{?',
            re.MULTILINE
        )

        # Regex for keyword-based functions (def, func, fn, function)
        # e.g., function doSomething(arg) { ... }
        #       def do_something(arg)
        #       func doSomething(arg string) error { ... }
        #       fn do_something(arg: &str) -> Result<(), Error> { ... }
        kw_func_pattern = re.compile(
            r'^\s*(?:public\s+|private\s+|protected\s+|internal\s+|static\s+|async\s+|export\s+)*\b(def|func|fn|function)\b\s+([a-zA-Z_]\w*)\s*\(([^)]*)\)',
            re.MULTILINE
        )

        # Regex for C-family functions (return type followed by name)
        # e.g., int main(int argc, char** argv)
        #       void doSomething() { ... }
        #       std::string get_name() const;
        # Excludes known keywords to avoid false positives
        c_func_pattern = re.compile(
            r'^\s*(?:public\s+|private\s+|protected\s+|internal\s+|static\s+|virtual\s+|inline\s+|constexpr\s+)*([a-zA-Z_][\w:<>]*[\s\*&]+)([a-zA-Z_]\w*)\s*\(([^)]*)\)',
            re.MULTILINE
        )

        # Extract classes
        for match in class_pattern.finditer(source):
            kind = match.group(1)
            name = match.group(2)
            # Find line number (inefficient but works for a basic parser)
            start_index = match.start()
            line_no = source[:start_index].count("\n") + 1

            # Simple visibility heuristic based on name
            visibility = Visibility.PRIVATE if name.startswith("_") else Visibility.PUBLIC

            class_info = ClassInfo(
                name=name,
                visibility=visibility,
                start_line=line_no,
                end_line=line_no,  # Hard to accurately determine without a real parser
            )
            module_info.classes.append(class_info)

        # Extract keyword-based functions
        for match in kw_func_pattern.finditer(source):
            kw = match.group(1)
            name = match.group(2)

            start_index = match.start()
            line_no = source[:start_index].count("\n") + 1

            visibility = Visibility.PRIVATE if name.startswith("_") else Visibility.PUBLIC

            func_info = FunctionInfo(
                name=name,
                visibility=visibility,
                start_line=line_no,
                end_line=line_no,
            )
            module_info.functions.append(func_info)

        # Extract C-family functions
        for match in c_func_pattern.finditer(source):
            return_type = match.group(1).strip()
            name = match.group(2)

            # Skip if it looks like a control flow keyword
            if name in {"if", "for", "while", "switch", "catch", "return"}:
                continue
            if return_type in {"return", "new", "delete", "throw", "else"}:
                continue

            start_index = match.start()
            line_no = source[:start_index].count("\n") + 1

            visibility = Visibility.PRIVATE if name.startswith("_") else Visibility.PUBLIC

            func_info = FunctionInfo(
                name=name,
                return_type=return_type,
                visibility=visibility,
                start_line=line_no,
                end_line=line_no,
            )
            module_info.functions.append(func_info)

        return module_info
