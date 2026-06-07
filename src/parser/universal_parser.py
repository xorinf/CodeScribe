import re
from pathlib import Path
from typing import Optional

from src.parser.base import (
    BaseParser,
    ClassInfo,
    FunctionInfo,
    ModuleInfo,
    ParseResult,
    Visibility,
)


class UniversalParser(BaseParser):
    """Fallback parser for non-Python languages using regular expressions.

    Extracts basic structural information (classes and functions) from
    languages like JavaScript, TypeScript, Go, Rust, Java, C++, etc.
    """

    def language(self) -> str:
        return "universal"

    def supported_extensions(self) -> list[str]:
        return [
            ".js", ".ts", ".go", ".rs", ".java", ".cpp", ".c", ".h", ".hpp",
            ".cs", ".php", ".rb", ".swift", ".kt", ".m", ".mm"
        ]

    def parse_file(self, file_path: Path) -> ModuleInfo:
        file_path = Path(file_path).resolve()

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            content = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            # Fallback if there are decoding issues
            content = file_path.read_text(encoding="latin-1")

        module = ModuleInfo(file_path=file_path)

        # 1. Class extraction regex
        # Matches typical class definitions (e.g. `public class MyClass`)
        class_regex = re.compile(
            r"^\s*(?:public\s+|private\s+|protected\s+|export\s+|abstract\s+|final\s+)*"
            r"class\s+([A-Za-z_][A-Za-z0-9_]*)",
            re.MULTILINE
        )
        for match in class_regex.finditer(content):
            name = match.group(1)
            # Find line number (approximation)
            start_index = match.start()
            line_num = content.count('\n', 0, start_index) + 1
            module.classes.append(
                ClassInfo(
                    name=name,
                    start_line=line_num,
                    end_line=line_num,  # We can't reliably determine end line with regex easily
                )
            )

        # 2. Keyword-based function extraction regex (def, func, fn, function)
        # Matches functions declared with specific keywords
        kw_regex = re.compile(
            r"^\s*(?:public\s+|private\s+|protected\s+|export\s+|async\s+|static\s+)*"
            r"(?:def|func|fn|function)\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(",
            re.MULTILINE
        )
        for match in kw_regex.finditer(content):
            name = match.group(1)
            start_index = match.start()
            line_num = content.count('\n', 0, start_index) + 1
            module.functions.append(
                FunctionInfo(
                    name=name,
                    start_line=line_num,
                    end_line=line_num,
                )
            )

        # 3. C-family return-type-based function extraction regex
        # Matches `Type name(...) {` or `Type name(...);`
        c_family_regex = re.compile(
            r"^\s*(?:public\s+|private\s+|protected\s+|static\s+|inline\s+|virtual\s+|extern\s+|constexpr\s+)*"
            r"(?!(?:if|while|for|switch|catch|return|new|delete|class|struct|enum|namespace|else|elif)\b)"
            r"([A-Za-z_][A-Za-z0-9_<>:\[\]\*&]*)\s+"
            r"([A-Za-z_][A-Za-z0-9_]*)\s*\([^)]*\)\s*(?:const\s*)?(?:noexcept\s*)?(?:\{|;)",
            re.MULTILINE
        )
        for match in c_family_regex.finditer(content):
            return_type = match.group(1).strip()
            name = match.group(2)

            # Skip false positives that often slip through regex
            if name in ('if', 'while', 'for', 'switch', 'catch', 'return', 'new', 'delete', 'else', 'elif'):
                continue

            start_index = match.start()
            line_num = content.count('\n', 0, start_index) + 1

            # Ensure we don't duplicate functions found by kw_regex
            if not any(f.name == name and f.start_line == line_num for f in module.functions):
                module.functions.append(
                    FunctionInfo(
                        name=name,
                        return_type=return_type,
                        start_line=line_num,
                        end_line=line_num,
                    )
                )

        return module
