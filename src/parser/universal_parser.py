import re
from pathlib import Path

from src.parser.base import (
    BaseParser,
    ModuleInfo,
    FunctionInfo,
    ClassInfo,
    ParseResult,
)

class UniversalParser(BaseParser):
    """
    A fallback parser that uses regex to extract basic class and function
    structures from non-Python languages.
    """

    def language(self) -> str:
        return "universal"

    def supported_extensions(self) -> list[str]:
        return [
            ".js", ".ts", ".java", ".cpp", ".c", ".cs", ".go",
            ".rs", ".rb", ".php", ".swift", ".kt", ".h", ".hpp", ".m"
        ]

    def parse_file(self, file_path: Path) -> ModuleInfo:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except UnicodeDecodeError:
            with open(file_path, "r", encoding="latin-1") as f:
                content = f.read()

        module_info = ModuleInfo(file_path=file_path)

        # Match classes: "class MyClass"
        class_pattern = re.compile(r'^[ \t]*class\s+([A-Za-z_][A-Za-z0-9_]*)\b', re.MULTILINE)
        classes = class_pattern.findall(content)

        # To avoid duplicates, we use a set for names, but let's keep order
        seen_classes = set()
        for cls_name in classes:
            if cls_name not in seen_classes:
                module_info.classes.append(ClassInfo(name=cls_name))
                seen_classes.add(cls_name)

        # Match keyword-based functions (e.g. def, function, func, fn)
        keyword_func = re.compile(
            r'^[ \t]*(?:public\s+|private\s+|protected\s+|static\s+|async\s+|export\s+)*'
            r'(?:def|function|func|fn)\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(',
            re.MULTILINE
        )
        kw_funcs = keyword_func.findall(content)

        # Match C-style return-type-based functions (e.g. int calculate(int a))
        # Negative lookahead avoids keywords like if, while, for, switch, etc.
        c_func = re.compile(
            r'^[ \t]*(?:public\s+|private\s+|protected\s+|static\s+|async\s+|virtual\s+|inline\s+|override\s+|export\s+)*'
            r'(?!(?:def|function|func|fn|if|while|for|switch|catch|return|new|class)\b)'
            r'[A-Za-z_][A-Za-z0-9_<>,:\[\]]*\s+(?:\*|&)*([A-Za-z_][A-Za-z0-9_]*)\s*\(',
            re.MULTILINE
        )
        c_funcs = c_func.findall(content)

        seen_funcs = set()
        for func_name in kw_funcs + c_funcs:
            if func_name not in seen_funcs and func_name not in seen_classes:
                module_info.functions.append(FunctionInfo(name=func_name))
                seen_funcs.add(func_name)

        return module_info
