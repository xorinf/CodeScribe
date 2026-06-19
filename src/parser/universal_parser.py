import re
from pathlib import Path
from src.parser.base import BaseParser, ModuleInfo, ClassInfo, FunctionInfo, ParseResult

class UniversalParser(BaseParser):
    def language(self) -> str:
        return "universal"

    def supported_extensions(self) -> list[str]:
        # Return common extensions for non-python languages
        return [
            ".js", ".jsx", ".ts", ".tsx",
            ".java", ".c", ".cpp", ".h", ".hpp",
            ".go", ".rs", ".rb", ".php", ".cs",
            ".swift", ".kt", ".kts"
        ]

    def parse_file(self, file_path: Path) -> ModuleInfo:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception:
            return ModuleInfo(file_path=file_path)

        module_info = ModuleInfo(file_path=file_path)

        class_pattern = re.compile(r'\bclass\s+([a-zA-Z_][a-zA-Z0-9_]*)')
        classes = class_pattern.findall(content)
        for cls_name in classes:
            module_info.classes.append(ClassInfo(name=cls_name))

        func_kw_pattern = re.compile(r'\b(?:def|func|fn|function)\s+([a-zA-Z_][a-zA-Z0-9_]*)')
        kw_funcs = func_kw_pattern.findall(content)
        for func_name in kw_funcs:
            module_info.functions.append(FunctionInfo(name=func_name))

        c_func_pattern = re.compile(
            r'^[ \t]*(?:(?:public|private|protected|static|final|volatile|virtual|inline|constexpr)[ \t]+)*'
            r'(?!if|for|while|switch|return|def|func|fn|function|class)'
            r'[a-zA-Z_][a-zA-Z0-9_<>:\[\]]*[ \t\*&]+'
            r'([a-zA-Z_][a-zA-Z0-9_]*)[ \t]*\(',
            re.MULTILINE
        )
        c_funcs = c_func_pattern.findall(content)
        for func_name in c_funcs:
            if func_name not in [f.name for f in module_info.functions]:
                module_info.functions.append(FunctionInfo(name=func_name))

        return module_info
