import re
from pathlib import Path

from src.parser.base import (
    BaseParser,
    ClassInfo,
    FunctionInfo,
    ModuleInfo,
    Visibility,
)

class UniversalParser(BaseParser):
    """Fallback parser using regex to extract functions and classes for non-Python files."""

    def language(self) -> str:
        return "universal"

    def supported_extensions(self) -> list[str]:
        return [
            ".js", ".jsx", ".ts", ".tsx", ".java", ".cpp", ".c", ".h",
            ".cs", ".go", ".rs", ".php", ".rb"
        ]

    def parse_file(self, file_path: Path) -> ModuleInfo:
        file_path = Path(file_path).resolve()

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            source = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            # Skip binary files or files with unknown encoding
            return ModuleInfo(file_path=file_path)

        module_info = ModuleInfo(file_path=file_path)

        # Basic regex to extract function names
        # Matches: def func_name(, function func_name(, func func_name(
        func_pattern = re.compile(r'\b(?:def|function|func|fn)\s+([a-zA-Z_]\w*)\s*\(', re.MULTILINE)
        for match in func_pattern.finditer(source):
            func_name = match.group(1)
            visibility = Visibility.PRIVATE if func_name.startswith('_') else Visibility.PUBLIC
            module_info.functions.append(FunctionInfo(
                name=func_name,
                visibility=visibility,
            ))

        # Basic regex to extract class names
        # Matches: class ClassName
        class_pattern = re.compile(r'\bclass\s+([a-zA-Z_]\w*)', re.MULTILINE)
        for match in class_pattern.finditer(source):
            class_name = match.group(1)
            visibility = Visibility.PRIVATE if class_name.startswith('_') else Visibility.PUBLIC
            module_info.classes.append(ClassInfo(
                name=class_name,
                visibility=visibility,
            ))

        return module_info
