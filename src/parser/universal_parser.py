"""
Universal Parser for multi-language support using regex.

This parser provides a fallback mechanism to extract basic class and function
structures from languages other than Python.
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
    """Regex-based parser for multiple programming languages.

    Extracts class and function definitions using heuristics and regular expressions.
    """

    def language(self) -> str:
        return "multi"

    def supported_extensions(self) -> list[str]:
        return [
            ".js", ".jsx", ".ts", ".tsx",
            ".java", ".kt", ".scala",
            ".c", ".cpp", ".cc", ".h", ".hpp",
            ".cs", ".go", ".rs", ".rb", ".php",
            ".swift", ".m", ".sh", ".bash"
        ]

    def parse_file(self, file_path: Path) -> ModuleInfo:
        """Parse a source file using regular expressions."""
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            raise RuntimeError(f"Could not read file {file_path}: {e}")

        module_info = ModuleInfo(file_path=file_path)

        # 1. Match classes, structs, interfaces
        # Example: class MyClass, struct MyStruct, interface MyInterface
        class_pattern = re.compile(r'\b(?:class|struct|interface)\s+([a-zA-Z_]\w*)')
        for match in class_pattern.finditer(content):
            name = match.group(1)
            # Rough line number calculation
            start_line = content.count('\n', 0, match.start()) + 1
            module_info.classes.append(
                ClassInfo(
                    name=name,
                    start_line=start_line,
                    end_line=start_line, # Cannot easily determine end line
                )
            )

        # 2. Match functions with keywords
        # Example: def func, function func, fn func, func func
        kw_func_pattern = re.compile(r'\b(?:def|function|func|fn)\s+([a-zA-Z_]\w*)\s*\(')
        for match in kw_func_pattern.finditer(content):
            name = match.group(1)
            start_line = content.count('\n', 0, match.start()) + 1
            module_info.functions.append(
                FunctionInfo(
                    name=name,
                    start_line=start_line,
                    end_line=start_line,
                )
            )

        # 3. Match C-family functions (return type based)
        # Excludes known keywords to avoid double counting or matching control structures
        # Example: int my_func(int a), void method()
        c_func_pattern = re.compile(
            r'^[ \t]*(?:(?:virtual|static|inline|public|private|protected)\s+)*'
            r'([a-zA-Z_][a-zA-Z0-9_<>:]*)\s+([a-zA-Z_]\w*)\s*\(',
            re.MULTILINE
        )

        excluded_keywords = {
            'if', 'else', 'for', 'while', 'switch', 'catch', 'return',
            'class', 'struct', 'interface', 'new', 'delete', 'throw'
        }

        for match in c_func_pattern.finditer(content):
            ret_type = match.group(1)
            name = match.group(2)

            # Skip if it looks like a control structure
            if ret_type in excluded_keywords or name in excluded_keywords:
                continue

            # Skip if we already found a keyword-based function with the same name near here
            # (simple heuristic to avoid duplicates)

            start_line = content.count('\n', 0, match.start()) + 1

            # Check if this name is already in our list
            if any(f.name == name for f in module_info.functions):
                continue

            module_info.functions.append(
                FunctionInfo(
                    name=name,
                    return_type=ret_type,
                    start_line=start_line,
                    end_line=start_line,
                )
            )

        return module_info
