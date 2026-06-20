from pathlib import Path
import re
from typing import Optional

from src.parser.base import (
    BaseParser,
    ParseResult,
    ModuleInfo,
    FunctionInfo,
    ClassInfo,
    Visibility,
)


class UniversalParser(BaseParser):
    """Fallback parser for unsupported languages.

    Uses regex heuristics to extract basic function and class definitions
    from a variety of programming languages.
    """

    def __init__(self, extensions: list[str]) -> None:
        """Initialize the UniversalParser.

        Args:
            extensions: A list of file extensions this instance should handle.
        """
        self._extensions = extensions

    def language(self) -> str:
        return "universal"

    def supported_extensions(self) -> list[str]:
        return self._extensions

    def parse_file(self, file_path: Path) -> ModuleInfo:
        file_path = Path(file_path).resolve()

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        source = file_path.read_text(encoding="utf-8", errors="replace")

        module_info = ModuleInfo(file_path=file_path)

        # 1. Parse Classes
        # Matches class, struct, interface followed by name
        class_pattern = re.compile(r'\b(?:class|struct|interface)\s+([a-zA-Z_]\w*)', re.MULTILINE)
        for match in class_pattern.finditer(source):
            class_name = match.group(1)
            module_info.classes.append(ClassInfo(name=class_name))

        # 2. Parse Keyword Functions (def, func, fn, function)
        kw_pattern = re.compile(r'\b(?:def|func|fn|function)\s+([a-zA-Z_]\w*)', re.MULTILINE)
        found_func_names = set()
        for match in kw_pattern.finditer(source):
            func_name = match.group(1)
            found_func_names.add(func_name)
            module_info.functions.append(FunctionInfo(name=func_name))

        # 3. Parse C-Family Functions (return type based)
        c_pattern = re.compile(
            r'^\s*(?:(?:public|private|protected|static|virtual|inline|async|export)\s+)*'
            r'([a-zA-Z_]\w*(?:<[^>]+>)?(?:\[\])?(?:\s*[\*&]+)?)\s+'
            r'([a-zA-Z_]\w*)\s*\(',
            re.MULTILINE
        )
        ignore_keywords = {
            "def", "func", "fn", "function", "return", "if", "else", "while",
            "for", "switch", "catch", "new", "throw", "class", "struct", "interface"
        }

        for match in c_pattern.finditer(source):
            return_type, func_name = match.groups()
            return_type_base = return_type.strip().split()[0].strip('*&')

            if return_type_base not in ignore_keywords and func_name not in ignore_keywords:
                if func_name not in found_func_names:
                    found_func_names.add(func_name)
                    module_info.functions.append(
                        FunctionInfo(name=func_name, return_type=return_type.strip())
                    )

        return module_info
