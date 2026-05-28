import re
from pathlib import Path

from src.parser.base import (
    BaseParser,
    ClassInfo,
    FunctionInfo,
    ModuleInfo,
)

class UniversalParser(BaseParser):
    """Fallback parser for multiple languages using regular expressions.

    Extracts basic class and function structures from non-Python languages.
    """

    def language(self) -> str:
        return "universal"

    def supported_extensions(self) -> list[str]:
        return [
            ".js", ".ts", ".java", ".cpp", ".c", ".cs", ".go", ".rs", ".php", ".rb",
            ".swift", ".kt"
        ]

    def parse_file(self, file_path: Path) -> ModuleInfo:
        file_path = Path(file_path).resolve()
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        source = file_path.read_text(encoding="utf-8", errors="ignore")
        module_info = ModuleInfo(file_path=file_path)

        # Naive regex for classes
        class_regex = re.compile(r'\b(?:class|struct|interface)\s+([a-zA-Z_]\w*)')

        # Naive regex for functions/methods
        func_regex = re.compile(
            r'\b(?:def|function|func|fn|public|private|protected|static|virtual|inline|const|abstract|override|[\w<>\[\]]+)\s+([a-zA-Z_]\w*)\s*\([^)]*\)\s*(?:\{|:|->|throws)'
        )

        for line_no, line in enumerate(source.splitlines(), start=1):
            class_match = class_regex.search(line)
            if class_match:
                name = class_match.group(1)
                module_info.classes.append(ClassInfo(name=name, start_line=line_no, end_line=line_no))
                continue

            func_match = func_regex.search(line)
            if func_match:
                name = func_match.group(1)
                # Ignore common keywords
                if name not in ("if", "for", "while", "switch", "catch", "return", "class", "else", "elif"):
                    module_info.functions.append(FunctionInfo(name=name, start_line=line_no, end_line=line_no))

        return module_info
