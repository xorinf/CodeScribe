import re
from pathlib import Path
from typing import Optional

from src.parser.base import (
    BaseParser,
    ClassInfo,
    FunctionInfo,
    MethodInfo,
    ModuleInfo,
    ParseResult,
    Visibility,
)

# Regex patterns for various languages
CLASS_PATTERN = re.compile(r"^\s*(?:export\s+)?(?:public\s+|private\s+|protected\s+)?class\s+([a-zA-Z0-9_]+)", re.MULTILINE)
FUNC_PATTERN = re.compile(r"^\s*(?:export\s+)?(?:public\s+|private\s+|protected\s+)?(?:static\s+)?(?:function\s+|func\s+|def\s+)([a-zA-Z0-9_]+)\s*\(", re.MULTILINE)


class UniversalParser(BaseParser):
    def language(self) -> str:
        return "universal"

    def supported_extensions(self) -> list[str]:
        return [".js", ".ts", ".java", ".cpp", ".c", ".go", ".rs", ".php", ".rb"]

    def parse_file(self, file_path: Path) -> ModuleInfo:
        file_path = Path(file_path).resolve()

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            source = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            source = ""

        module_info = ModuleInfo(file_path=file_path)

        # Simple regex-based extraction
        for match in CLASS_PATTERN.finditer(source):
            class_name = match.group(1)
            # Find line number (approximate)
            start_line = source[:match.start()].count('\n') + 1
            module_info.classes.append(
                ClassInfo(
                    name=class_name,
                    start_line=start_line,
                    end_line=start_line, # Simplification
                )
            )

        for match in FUNC_PATTERN.finditer(source):
            func_name = match.group(1)
            start_line = source[:match.start()].count('\n') + 1
            module_info.functions.append(
                FunctionInfo(
                    name=func_name,
                    start_line=start_line,
                    end_line=start_line, # Simplification
                )
            )

        return module_info
