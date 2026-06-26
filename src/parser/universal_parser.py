import re
from pathlib import Path
from typing import Optional

from src.parser.base import BaseParser, ModuleInfo, ClassInfo, FunctionInfo, Parameter

# Regex patterns
CLASS_PATTERN = re.compile(r'\b(?:class|struct|interface)\s+([a-zA-Z_]\w*)')
KW_FUNC_PATTERN = re.compile(r'\b(?:def|func|fn|function)\s+([a-zA-Z_]\w*)\s*\((.*?)\)')
C_FUNC_PATTERN = re.compile(r'\b([a-zA-Z_]\w*(?:<[^>]+>)?(?:\[\])?)\s+([a-zA-Z_]\w*)\s*\((.*?)\)\s*(?:\{|;|throws)')

IGNORE_C_FUNCS = {'if', 'for', 'while', 'switch', 'catch', 'return'}

class UniversalParser(BaseParser):
    def language(self) -> str:
        return "universal"

    def supported_extensions(self) -> list[str]:
        return [
            ".js", ".ts", ".java", ".c", ".cpp", ".cs", ".go",
            ".rs", ".rb", ".php", ".swift", ".kt"
        ]

    def parse_file(self, file_path: Path) -> ModuleInfo:
        file_path = Path(file_path).resolve()
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            source = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            # Fallback or just return empty if it's binary or not utf-8
            return ModuleInfo(file_path=file_path)

        module_info = ModuleInfo(file_path=file_path)

        # Find classes
        for match in CLASS_PATTERN.finditer(source):
            class_name = match.group(1)
            module_info.classes.append(ClassInfo(name=class_name))

        # Find keyword functions
        for match in KW_FUNC_PATTERN.finditer(source):
            func_name = match.group(1)
            args_str = match.group(2)
            # Simple parse for args (comma separated)
            params = []
            if args_str.strip():
                for arg in args_str.split(','):
                    arg = arg.strip()
                    if arg:
                        # Extract the first word or the whole arg as name for simplicity
                        params.append(Parameter(name=arg))

            module_info.functions.append(FunctionInfo(name=func_name, parameters=params))

        # Find C-family functions
        for match in C_FUNC_PATTERN.finditer(source):
            ret_type, func_name, args_str = match.groups()
            if func_name not in IGNORE_C_FUNCS:
                params = []
                if args_str.strip():
                    for arg in args_str.split(','):
                        arg = arg.strip()
                        if arg:
                            params.append(Parameter(name=arg))
                module_info.functions.append(FunctionInfo(
                    name=func_name,
                    return_type=ret_type,
                    parameters=params
                ))

        return module_info
