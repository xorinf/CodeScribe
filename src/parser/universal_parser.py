import re
from pathlib import Path
from typing import Optional

from src.parser.base import BaseParser, ParseResult, ModuleInfo, ClassInfo, FunctionInfo, Visibility

class UniversalParser(BaseParser):
    """Regex-based fallback parser for non-Python languages."""

    def language(self) -> str:
        return "universal"

    def supported_extensions(self) -> list[str]:
        return [
            ".js", ".ts", ".jsx", ".tsx",
            ".java", ".c", ".cpp", ".cc", ".h", ".hpp",
            ".cs", ".go", ".rs", ".rb", ".php", ".swift", ".kt"
        ]

    def parse_file(self, file_path: Path) -> ModuleInfo:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except UnicodeDecodeError:
            # Fallback for binary or weirdly encoded files
            return ModuleInfo(file_path=file_path)

        module_info = ModuleInfo(file_path=file_path)

        # 1. Match Classes: e.g. class Foo { or class Foo(Bar)
        class_pattern = re.compile(r'^\s*(?:public\s+|private\s+|protected\s+)?(?:abstract\s+|sealed\s+)?class\s+([A-Za-z0-9_]+)', re.MULTILINE)
        for match in class_pattern.finditer(content):
            class_name = match.group(1)
            module_info.classes.append(ClassInfo(name=class_name))

        # 2. Match Keyword-based functions: e.g. def foo(), function bar(), fn baz(), func qux()
        keyword_func_pattern = re.compile(r'^\s*(?:public\s+|private\s+|protected\s+)?(?:export\s+)?(?:async\s+)?(?:def|function|fn|func)\s+([A-Za-z0-9_]+)\s*\(', re.MULTILINE)
        for match in keyword_func_pattern.finditer(content):
            func_name = match.group(1)
            module_info.functions.append(FunctionInfo(name=func_name))

        # 3. Match C-family return-type functions: e.g. int foo(), void *bar(int x)
        # We need a heuristic here. Let's look for:
        # Optional visibility -> Optional modifiers -> Return Type (Identifier or Pointer) -> Function Name -> (
        # We avoid matching 'if', 'for', 'while', 'switch', 'catch'
        c_func_pattern = re.compile(
            r'^\s*(?:public\s+|private\s+|protected\s+)?'
            r'(?:static\s+|virtual\s+|inline\s+)?'
            r'(?:[A-Za-z0-9_<>:,\s]+[\*\&]?\s+)'
            r'([A-Za-z0-9_]+)\s*\([^)]*\)\s*(?:const)?\s*\{',
            re.MULTILINE
        )

        exclude_keywords = {"if", "for", "while", "switch", "catch", "return", "new", "delete", "throw"}

        for match in c_func_pattern.finditer(content):
            func_name = match.group(1)
            if func_name not in exclude_keywords:
                module_info.functions.append(FunctionInfo(name=func_name))

        return module_info
