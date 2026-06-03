import re
from pathlib import Path
from typing import Optional

from src.parser.base import BaseParser, ModuleInfo, ClassInfo, FunctionInfo, ParseResult


class UniversalParser(BaseParser):
    """Fallback parser that uses regex to extract structures from various languages."""

    def language(self) -> str:
        return "universal"

    def supported_extensions(self) -> list[str]:
        return [
            ".js", ".jsx", ".ts", ".tsx", ".java", ".cpp", ".c", ".cc", ".cxx",
            ".h", ".hpp", ".cs", ".go", ".rs", ".php", ".rb", ".swift", ".kt",
            ".kts", ".scala", ".m", ".mm"
        ]

    def parse_file(self, file_path: Path) -> ModuleInfo:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        classes = []
        functions = []

        # Regex for classes
        class_pattern = re.compile(r'\bclass\s+([A-Za-z_]\w*)')
        for match in class_pattern.finditer(content):
            class_name = match.group(1)
            classes.append(ClassInfo(name=class_name))

        # Regex for keyword-based functions
        keyword_func_pattern = re.compile(r'\b(?:def|function|func|fn)\s+([A-Za-z_]\w*)\s*\(')
        for match in keyword_func_pattern.finditer(content):
            func_name = match.group(1)
            functions.append(FunctionInfo(name=func_name))

        # Regex for C-family return-type-based functions (very simplified heuristic)
        # Matches e.g. "int main(", "void* my_func(", "MyClass::my_method("
        # Avoid matching control structures like "if (", "for (", "while ("
        # Must have at least one type word, followed by function name, then (
        c_func_pattern = re.compile(r'^[ \t]*(?:(?:public|private|protected|static|virtual|inline|constexpr)\s+)*([A-Za-z_]\w*(?:<[^>]+>)?[\s\*\&]+)+([A-Za-z_]\w*)\s*\(', re.MULTILINE)

        for match in c_func_pattern.finditer(content):
            func_name = match.group(2)
            # Filter out control flow that might accidentally match
            if func_name not in {"if", "for", "while", "switch", "catch"}:
                functions.append(FunctionInfo(name=func_name))

        # Deduplicate functions by name to avoid double counting if regex overlap (though unlikely here)
        unique_funcs = []
        seen = set()
        for f in functions:
            if f.name not in seen:
                seen.add(f.name)
                unique_funcs.append(f)

        unique_classes = []
        seen_c = set()
        for c in classes:
            if c.name not in seen_c:
                seen_c.add(c.name)
                unique_classes.append(c)

        return ModuleInfo(
            file_path=file_path,
            classes=unique_classes,
            functions=unique_funcs
        )
