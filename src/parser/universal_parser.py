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
    """Regex-based fallback parser for extracting structures from various languages.

    Extracts basic class and function structures from non-Python languages
    using heuristic regular expressions. Handles keyword-based definitions
    (def, func, fn, function) and C-family return-type-based definitions.
    """

    def language(self) -> str:
        return "universal"

    def supported_extensions(self) -> list[str]:
        return [
            ".js", ".jsx", ".ts", ".tsx",
            ".go", ".rs", ".java", ".c",
            ".cpp", ".cc", ".cxx", ".h", ".hpp",
            ".cs", ".php", ".rb", ".swift", ".kt"
        ]

    def parse_file(self, file_path: Path) -> ModuleInfo:
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception:
            return ModuleInfo(file_path=file_path)

        # 1. Class/Struct/Interface matching
        class_pattern = re.compile(r'\b(?:class|struct|interface)\s+([a-zA-Z_]\w*)')
        classes = []
        for match in class_pattern.finditer(content):
            name = match.group(1)
            classes.append(ClassInfo(name=name))

        # 2. Keyword-based function matching (def, func, fn, function)
        kw_func_pattern = re.compile(r'\b(?:def|func|fn|function)\s+([a-zA-Z_]\w*)\s*\(')
        functions = []
        kw_funcs = set()
        for match in kw_func_pattern.finditer(content):
            name = match.group(1)
            functions.append(FunctionInfo(name=name))
            kw_funcs.add(name)

        # 3. C-family return-type-based function matching
        c_func_pattern = re.compile(
            r'^\s*(?:(?:public|private|protected|static|virtual|inline|async|override)\s+)*'
            r'([a-zA-Z_]\w*(?:<[^>]+>)?(?:\[\])?[\*&]?)\s+'
            r'([a-zA-Z_]\w*)\s*\(',
            re.MULTILINE
        )
        ignore_names = {"if", "for", "while", "switch", "catch"}
        ignore_rets = {"return", "else", "new", "throw", "case"}

        for match in c_func_pattern.finditer(content):
            ret_type = match.group(1)
            name = match.group(2)

            if name in ignore_names or ret_type in ignore_rets:
                continue

            if name not in kw_funcs:
                functions.append(FunctionInfo(name=name, return_type=ret_type))

        return ModuleInfo(
            file_path=file_path,
            classes=classes,
            functions=functions
        )
