import re
from pathlib import Path
from typing import Optional

from src.parser.base import (
    BaseParser,
    ClassInfo,
    FunctionInfo,
    ModuleInfo,
    ParseResult,
    Visibility,
)


class UniversalParser(BaseParser):
    """A regex-based fallback parser for non-Python languages.

    Extracts basic class and function structures from various
    programming languages using regular expressions.
    """

    def language(self) -> str:
        return "universal"

    def supported_extensions(self) -> list[str]:
        return [
            ".js", ".jsx", ".ts", ".tsx", ".java", ".cpp", ".c", ".h", ".cs",
            ".go", ".rs", ".php", ".rb", ".swift", ".kt", ".m"
        ]

    def parse_file(self, file_path: Path) -> ModuleInfo:
        """Parse a source file using regular expressions."""
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            raise ValueError(f"Could not read file {file_path}: {e}")

        # Regex patterns
        class_pattern = re.compile(
            r'^\s*(?:(?:public|private|protected|abstract|final|export|default)\s+)*'
            r'(?:class|struct|interface|trait)\s+([A-Za-z0-9_]+)',
            re.MULTILINE
        )

        function_pattern = re.compile(
            r'^\s*(?:(?:public|private|protected|static|async|export|inline|virtual|override|mut)\s+)*'
            r'(?:(?:def|fn|func|function)\s+|(?!(?:return|else|new|delete|throw|typedef|import|using)\b)[A-Za-z_][A-Za-z0-9_<>\[\]]*\s+(?:\*\s*|&\s*)?)'
            r'([A-Za-z0-9_]+)\s*\(',
            re.MULTILINE
        )

        classes = []
        for m in class_pattern.finditer(content):
            class_name = m.group(1)
            # Create a simple ClassInfo object for the extracted class
            cls_info = ClassInfo(
                name=class_name,
                docstring=None,
                start_line=content[:m.start()].count('\n') + 1,
                end_line=content[:m.start()].count('\n') + 1,
            )
            classes.append(cls_info)

        functions = []
        for m in function_pattern.finditer(content):
            func_name = m.group(1)
            # Ignore common false positives
            if func_name in ("if", "for", "while", "switch", "catch"):
                continue

            func_info = FunctionInfo(
                name=func_name,
                docstring=None,
                start_line=content[:m.start()].count('\n') + 1,
                end_line=content[:m.start()].count('\n') + 1,
            )
            functions.append(func_info)

        module_info = ModuleInfo(
            file_path=file_path,
            classes=classes,
            functions=functions,
        )

        return module_info
