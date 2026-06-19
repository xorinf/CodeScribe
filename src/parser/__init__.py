"""
src.parser -- Code Parsing and AST Generation Package.
"""
from src.parser.base import BaseParser, ModuleInfo, ClassInfo, FunctionInfo, ParseResult
from src.parser.registry import ParserRegistry
from src.parser.python_parser import PythonParser
from src.parser.universal_parser import UniversalParser
