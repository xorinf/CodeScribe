import re
from pathlib import Path
from src.parser.base import (
    BaseParser,
    ParseResult,
    ModuleInfo,
    ClassInfo,
    FunctionInfo,
    Visibility
)

class UniversalParser(BaseParser):
    """Regex-based fallback parser for extracting basic code structures
    from non-Python languages. Handles both keyword-based and
    C-family return-type-based declarations.
    """

    def language(self) -> str:
        return "universal"

    def supported_extensions(self) -> list[str]:
        return [".js", ".ts", ".java", ".cpp", ".c", ".cs", ".go", ".rs", ".rb", ".php"]

    def parse_file(self, file_path: Path) -> ModuleInfo:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        module_info = ModuleInfo(file_path=file_path)

        keyword_func_pattern = re.compile(
            r'^\s*(?:public\s+|private\s+|protected\s+|static\s+|async\s+|export\s+)*(?:def|func|fn|function)\s+([A-Za-z0-9_]+)\s*\(',
            re.MULTILINE
        )
        c_func_pattern = re.compile(
            r'^\s*(?:(?:public|private|protected|static|virtual|inline|explicit|async)\s+)*([A-Za-z0-9_<>:]+)\s+([A-Za-z0-9_]+)\s*\(',
            re.MULTILINE
        )
        class_pattern = re.compile(
            r'^\s*(?:(?:public|private|protected|static|abstract|final|export)\s+)*class\s+([A-Za-z0-9_]+)',
            re.MULTILINE
        )

        for match in class_pattern.finditer(content):
            name = match.group(1)
            module_info.classes.append(ClassInfo(name=name))

        found_functions = set()
        for match in keyword_func_pattern.finditer(content):
            name = match.group(1)
            if name not in found_functions:
                found_functions.add(name)
                module_info.functions.append(FunctionInfo(name=name))

        for match in c_func_pattern.finditer(content):
            ret_type = match.group(1)
            name = match.group(2)
            if name not in ('if', 'for', 'while', 'switch', 'catch', 'return', 'else', 'elif') and ret_type not in ('def', 'func', 'fn', 'function', 'class', 'public', 'private', 'protected', 'static', 'async', 'export'):
                if name not in found_functions:
                    found_functions.add(name)
                    module_info.functions.append(FunctionInfo(name=name, return_type=ret_type))

        return module_info
