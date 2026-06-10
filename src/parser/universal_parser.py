import re
from pathlib import Path
from typing import Optional

from src.parser.base import BaseParser, ModuleInfo, ClassInfo, FunctionInfo, ParseResult


class UniversalParser(BaseParser):
    """A fallback parser that uses regex to extract basic code structures
    for non-Python languages.
    """

    def language(self) -> str:
        """Return the language identifier."""
        return "multi"

    def supported_extensions(self) -> list[str]:
        """Return the file extensions this parser can handle."""
        return [
            ".js", ".ts", ".jsx", ".tsx",
            ".java", ".cpp", ".c", ".h", ".hpp",
            ".go", ".rs"
        ]

    def parse_file(self, file_path: Path) -> ModuleInfo:
        """Parse a single source file into a ModuleInfo structure."""

        try:
            content = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            # Fallback if there are encoding issues
            content = file_path.read_text(encoding="latin-1", errors="ignore")

        classes = []
        functions = []

        for line_num, line in enumerate(content.splitlines(), start=1):
            # Try to match class declarations
            class_match = re.search(r'\bclass\s+([a-zA-Z_]\w*)', line)
            if class_match:
                classes.append(ClassInfo(name=class_match.group(1), start_line=line_num, end_line=line_num))
                continue

            # Try to match keyword-based function declarations (def, func, fn, function)
            kw_func_match = re.search(r'\b(?:def|func|fn|function)\s+([a-zA-Z_]\w*)', line)
            if kw_func_match:
                functions.append(FunctionInfo(name=kw_func_match.group(1), start_line=line_num, end_line=line_num))
                continue

            # Try to match C-family return-type-based function declarations
            # Examples: int c_func(int a, char b) {, std::string cppFunc() const {, public static void javaFunc(String[] args) {
            c_func_match = re.search(
                r'^\s*(?:(?:public|private|protected|static|virtual|inline|explicit)\s+)*[a-zA-Z_][a-zA-Z0-9_:]*(?:<[^>]+>)?[\s\*\&]+([a-zA-Z_]\w*)\s*\(',
                line
            )
            if c_func_match:
                name = c_func_match.group(1)
                # Filter out control flow keywords that might look like functions
                if name not in ['if', 'for', 'while', 'catch', 'switch', 'return', 'else', 'sizeof']:
                    functions.append(FunctionInfo(name=name, start_line=line_num, end_line=line_num))

        return ModuleInfo(
            file_path=file_path,
            classes=classes,
            functions=functions
        )
