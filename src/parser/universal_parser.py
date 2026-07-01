import re
from pathlib import Path
from typing import Optional
from src.parser.base import (
    BaseParser,
    ParseResult,
    ModuleInfo,
    ClassInfo,
    FunctionInfo,
    Visibility,
)

class UniversalParser(BaseParser):
    def language(self) -> str:
        return "universal"

    def supported_extensions(self) -> list[str]:
        return [".js", ".ts", ".go", ".rs", ".java", ".cpp", ".c", ".h", ".cs", ".php", ".rb", ".swift", ".kt"]

    def parse_file(self, file_path: Path) -> ModuleInfo:
        try:
            content = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            content = file_path.read_text(encoding="latin-1")

        module = ModuleInfo(file_path=file_path)

        class_pattern = re.compile(r"^\s*(?:public\s+|private\s+|protected\s+|abstract\s+|final\s+|export\s+)*(?:class|struct|interface|trait)\s+([a-zA-Z_]\w*)", re.MULTILINE)
        func_kw_pattern = re.compile(r"^\s*(?:public\s+|private\s+|protected\s+|static\s+|async\s+|export\s+)*(?:def|function|func|fn)\s+([a-zA-Z_]\w*)\s*\(", re.MULTILINE)
        func_c_pattern = re.compile(r"^\s*(?:public\s+|private\s+|protected\s+|static\s+|inline\s+|virtual\s+|override\s+)*[a-zA-Z_][a-zA-Z0-9_<>\[\]]*\s+(?:[*&]\s*)?([a-zA-Z_]\w*)\s*\(", re.MULTILINE)

        for m in class_pattern.finditer(content):
            module.classes.append(ClassInfo(name=m.group(1)))

        funcs = set()
        for m in func_kw_pattern.finditer(content):
            name = m.group(1)
            if name not in funcs:
                module.functions.append(FunctionInfo(name=name))
                funcs.add(name)

        for m in func_c_pattern.finditer(content):
            name = m.group(1)
            if name not in ["if", "for", "while", "switch", "catch", "return"] and name not in funcs:
                module.functions.append(FunctionInfo(name=name))
                funcs.add(name)

        return module
