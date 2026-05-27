import re
from pathlib import Path

from src.parser.base import (
    BaseParser,
    ClassInfo,
    FunctionInfo,
    ModuleInfo,
)

class UniversalParser(BaseParser):
    """Fallback parser for extracting basic structures using regex."""

    def language(self) -> str:
        return "universal"

    def supported_extensions(self) -> list[str]:
        return [
            ".js", ".ts", ".jsx", ".tsx",
            ".java", ".kt", ".scala",
            ".cpp", ".cc", ".cxx", ".c", ".h", ".hpp",
            ".go",
            ".rs",
            ".rb",
            ".php",
            ".cs",
            ".swift"
        ]

    def parse_file(self, file_path: Path) -> ModuleInfo:
        file_path = Path(file_path).resolve()
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        source = file_path.read_text(encoding="utf-8", errors="ignore")

        module_info = ModuleInfo(file_path=file_path)

        # Regex for classes, interfaces, and structs
        class_regex = re.compile(r'\b(?:class|interface|struct)\s+([A-Za-z_]\w*)')
        for match in class_regex.finditer(source):
            module_info.classes.append(ClassInfo(name=match.group(1)))

        # Regex for functions with explicit keywords
        func_regex = re.compile(r'\b(?:function|func|def|fn)\s+([A-Za-z_]\w*)\s*\(')
        for match in func_regex.finditer(source):
            module_info.functions.append(FunctionInfo(name=match.group(1)))

        # Regex for C-style / Java-style functions and methods
        c_func_regex = re.compile(r'^[ \t]*(?:(?:public|private|protected|static|virtual|inline|export|async)\s+)*([A-Za-z_]\w*(?:<[^>]+>)?[\*\&]?\s+)+([A-Za-z_]\w*)\s*\([^)]*\)\s*(?:const\s*)?\{', re.MULTILINE)
        for match in c_func_regex.finditer(source):
            func_name = match.group(2)
            if func_name not in {"if", "for", "while", "switch", "catch", "return", "else"}:
                # Avoid duplicates from previous regex
                if not any(f.name == func_name for f in module_info.functions):
                    module_info.functions.append(FunctionInfo(name=func_name))

        return module_info
