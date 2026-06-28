from pathlib import Path
from typing import Optional
import re

from src.parser.base import (
    BaseParser,
    ParseResult,
    ModuleInfo,
    FunctionInfo,
    ClassInfo,
    Visibility,
)

class UniversalParser(BaseParser):
    def language(self) -> str:
        return "multi"

    def supported_extensions(self) -> list[str]:
        return [
            ".js", ".ts", ".jsx", ".tsx",
            ".java", ".c", ".cpp", ".cc", ".h", ".hpp",
            ".go", ".rs", ".rb", ".php"
        ]

    def parse_file(self, file_path: Path) -> ModuleInfo:
        text = file_path.read_text(encoding="utf-8", errors="ignore")

        module_info = ModuleInfo(file_path=file_path)

        # 1. Regex for keywords (def, func, function, fn)
        keyword_pattern = re.compile(r'\b(?:def|func|function|fn)\s+([a-zA-Z_]\w*)\s*\(')

        # 2. Regex for C-family return-type functions
        c_pattern = re.compile(
            r'^\s*'
            r'(?:(?:public|private|protected|static|final|virtual|inline|abstract)\s+)*'
            r'([a-zA-Z_]\w*(?:<[^>]+>)?(?:\[\])?(?:\s*[*&]+)?)\s+'
            r'([a-zA-Z_]\w*)\s*\([^)]*\)\s*(?:const)?\s*\{',
            re.MULTILINE
        )

        # 3. Classes/Structs/Interfaces
        class_pattern = re.compile(r'\b(?:class|struct|interface)\s+([a-zA-Z_]\w*)')

        seen_funcs = set()

        for match in keyword_pattern.finditer(text):
            func_name = match.group(1)
            if func_name not in seen_funcs:
                module_info.functions.append(FunctionInfo(name=func_name))
                seen_funcs.add(func_name)

        for match in c_pattern.finditer(text):
            return_type = match.group(1)
            func_name = match.group(2)
            # Filter out things that are actually keyword matches just in case
            if return_type in ("def", "func", "function", "fn", "return", "if", "else", "while", "for"):
                continue
            if func_name not in seen_funcs:
                module_info.functions.append(FunctionInfo(name=func_name, return_type=return_type))
                seen_funcs.add(func_name)

        for match in class_pattern.finditer(text):
            cls_name = match.group(1)
            module_info.classes.append(ClassInfo(name=cls_name))

        return module_info
