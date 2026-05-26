from pathlib import Path
import re

from src.parser.base import BaseParser, ModuleInfo, ClassInfo, FunctionInfo

class UniversalParser(BaseParser):
    def language(self) -> str:
        return "universal"

    def supported_extensions(self) -> list[str]:
        return [
            ".js", ".ts", ".java", ".cpp", ".c", ".cs", ".go", ".rs",
            ".php", ".rb", ".swift", ".kt", ".scala", ".m", ".h", ".hpp"
        ]

    def parse_file(self, file_path: Path) -> ModuleInfo:
        file_path = Path(file_path).resolve()
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        source = file_path.read_text(encoding="utf-8", errors="ignore")

        module_info = ModuleInfo(file_path=file_path)

        class_pattern = re.compile(
            r'(?:public\s+|private\s+|protected\s+)?(?:abstract\s+)?class\s+([A-Za-z0-9_]+)',
            re.MULTILINE
        )
        for match in class_pattern.finditer(source):
            module_info.classes.append(ClassInfo(name=match.group(1)))

        func_pattern = re.compile(
            r'(?:public\s+|private\s+|protected\s+)?(?:static\s+)?(?:async\s+)?(?:function\s+)?(?:[\w\<\>\[\]]+\s+)?([A-Za-z0-9_]+)\s*\([^)]*\)\s*(?:\{|:)',
            re.MULTILINE
        )
        for match in func_pattern.finditer(source):
            name = match.group(1)
            # Skip common control flow keywords
            if name not in ("if", "else", "for", "while", "switch", "catch", "return", "sizeof"):
                module_info.functions.append(FunctionInfo(name=name))

        return module_info
