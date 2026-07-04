import re
from pathlib import Path
from typing import Optional

from src.parser.base import (
    BaseParser, ModuleInfo, ParseResult, Visibility, FunctionInfo, ClassInfo
)

class UniversalParser(BaseParser):
    def language(self) -> str:
        return "multi"

    def supported_extensions(self) -> list[str]:
        # Return common extensions for non-Python languages as fallback
        return [
            ".js", ".jsx", ".ts", ".tsx", ".go", ".rs", ".java",
            ".cpp", ".hpp", ".cc", ".cxx", ".c", ".h", ".cs", ".php", ".rb", ".swift"
        ]

    def parse_file(self, file_path: Path) -> ModuleInfo:
        source = file_path.read_text(encoding="utf-8")
        module_info = ModuleInfo(file_path=file_path)

        # Function/Method matches:
        # keywords: def, func, fn, function
        # C-family: Type name(args) {

        func_pattern = re.compile(
            r'(?:public\s+|private\s+|protected\s+)?(?:static\s+)?(?:async\s+)?'
            r'(?:def|func|fn|function)?\s*'
            r'([A-Za-z0-9_<>\[\]]+)\s+'
            r'([A-Za-z_][A-Za-z0-9_]*)\s*\(([^)]*)\)',
            re.MULTILINE
        )

        for match in func_pattern.finditer(source):
            type_or_keyword = match.group(1).strip()
            name = match.group(2).strip()
            if name in ['if', 'while', 'for', 'switch', 'catch']:
                continue

            module_info.functions.append(FunctionInfo(
                name=name,
                visibility=Visibility.PUBLIC # Default to public
            ))

        class_pattern = re.compile(
            r'(?:public\s+|private\s+|protected\s+)?(?:abstract\s+)?class\s+([A-Za-z_][A-Za-z0-9_]*)',
            re.MULTILINE
        )

        for match in class_pattern.finditer(source):
            name = match.group(1)
            module_info.classes.append(ClassInfo(
                name=name,
                visibility=Visibility.PUBLIC
            ))

        return module_info
