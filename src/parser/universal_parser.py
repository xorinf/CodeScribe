import re
from pathlib import Path

from src.parser.base import BaseParser, ModuleInfo, FunctionInfo, ClassInfo

class UniversalParser(BaseParser):
    def language(self) -> str:
        return "universal"

    def supported_extensions(self) -> list[str]:
        return [
            ".js", ".jsx", ".ts", ".tsx", ".go", ".c", ".cpp", ".cc", ".cxx", ".h", ".hpp", ".hxx",
            ".java", ".rs", ".rb", ".php", ".cs", ".swift", ".kt", ".kts", ".m", ".mm",
            ".scala", ".pl", ".pm", ".sh", ".bash", ".lua", ".sql", ".dart", ".r", ".v", ".sv", ".vhdl"
        ]

    def parse_file(self, file_path: Path) -> ModuleInfo:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        module = ModuleInfo(file_path=file_path)

        seen_functions = set()
        seen_classes = set()

        # Extract classes/structs/interfaces
        class_re = re.compile(r'\b(?:class|struct|interface)\s+([a-zA-Z_]\w*)')
        for m in class_re.finditer(content):
            name = m.group(1)
            if name not in seen_classes:
                module.classes.append(ClassInfo(name=name))
                seen_classes.add(name)

        # Keyword-based functions (def, func, fn, function)
        func_kw_re = re.compile(r'\b(?:def|func|fn|function)\s+([a-zA-Z_]\w*)\s*\(')
        for m in func_kw_re.finditer(content):
            name = m.group(1)
            if name not in seen_functions:
                module.functions.append(FunctionInfo(name=name))
                seen_functions.add(name)

        # C-family return-type-based functions
        func_c_re = re.compile(r'^\s*(?:(?:public|private|protected|static|inline|virtual)\s+)*([a-zA-Z_]\w*(?:<[^>]+>)?(?:\[\])?)\s+([a-zA-Z_]\w*)\s*\([^)]*\)\s*(?:\{|;|:)', re.MULTILINE)
        for m in func_c_re.finditer(content):
            name = m.group(2)
            if name not in {"if", "else", "for", "while", "switch", "catch", "return", "sizeof"} and name not in seen_functions:
                module.functions.append(FunctionInfo(
                    name=name,
                    return_type=m.group(1)
                ))
                seen_functions.add(name)

        return module
