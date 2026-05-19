"""
base.py -- Abstract Interfaces and Data Models for Code Parsing.

This module defines the contracts that every language-specific parser
must fulfill, along with the data structures used to represent parsed
code elements. These models are intentionally language-agnostic so that
the analyzer and generator modules can work with any supported language
through a single, unified interface.

Data Flow:
    Source File  -->  BaseParser.parse()  -->  ParseResult
                                                 |
                                                 +-- ModuleInfo
                                                       +-- FunctionInfo
                                                       +-- ClassInfo
                                                             +-- MethodInfo
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class Visibility(Enum):
    """Visibility level of a code element.

    Used to distinguish between public API surface and internal
    implementation details during documentation generation.
    """

    PUBLIC = "public"
    PRIVATE = "private"
    PROTECTED = "protected"


# ---------------------------------------------------------------------------
# Data Models -- building blocks of a ParseResult
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Parameter:
    """Represents a single function or method parameter.

    Attributes:
        name: The parameter name as it appears in the source code.
        type_hint: The declared type annotation, if present.
        default_value: The default value expression as a string, if present.
    """

    name: str
    type_hint: Optional[str] = None
    default_value: Optional[str] = None


@dataclass(frozen=True)
class FunctionInfo:
    """Represents a standalone function defined at module level.

    Attributes:
        name: The function name.
        docstring: The raw docstring extracted from the source, if present.
        parameters: An ordered list of the function's parameters.
        return_type: The declared return type annotation, if present.
        decorators: A list of decorator names applied to the function.
        visibility: Whether the function is public or private.
        start_line: The line number where the function definition begins.
        end_line: The line number where the function definition ends.
    """

    name: str
    docstring: Optional[str] = None
    parameters: list[Parameter] = field(default_factory=list)
    return_type: Optional[str] = None
    decorators: list[str] = field(default_factory=list)
    visibility: Visibility = Visibility.PUBLIC
    start_line: int = 0
    end_line: int = 0


@dataclass(frozen=True)
class MethodInfo:
    """Represents a method defined inside a class body.

    Identical in structure to FunctionInfo but semantically distinct.
    Methods always belong to a parent ClassInfo.

    Attributes:
        name: The method name.
        docstring: The raw docstring extracted from the source, if present.
        parameters: An ordered list of the method's parameters.
        return_type: The declared return type annotation, if present.
        decorators: A list of decorator names applied to the method.
        visibility: Whether the method is public or private.
        is_static: True if the method is decorated with @staticmethod.
        is_classmethod: True if the method is decorated with @classmethod.
        start_line: The line number where the method definition begins.
        end_line: The line number where the method definition ends.
    """

    name: str
    docstring: Optional[str] = None
    parameters: list[Parameter] = field(default_factory=list)
    return_type: Optional[str] = None
    decorators: list[str] = field(default_factory=list)
    visibility: Visibility = Visibility.PUBLIC
    is_static: bool = False
    is_classmethod: bool = False
    start_line: int = 0
    end_line: int = 0


@dataclass(frozen=True)
class ClassInfo:
    """Represents a class definition within a module.

    Attributes:
        name: The class name.
        docstring: The raw docstring extracted from the source, if present.
        base_classes: A list of parent class names this class inherits from.
        methods: An ordered list of methods defined in this class.
        decorators: A list of decorator names applied to the class.
        visibility: Whether the class is public or private.
        start_line: The line number where the class definition begins.
        end_line: The line number where the class definition ends.
    """

    name: str
    docstring: Optional[str] = None
    base_classes: list[str] = field(default_factory=list)
    methods: list[MethodInfo] = field(default_factory=list)
    decorators: list[str] = field(default_factory=list)
    visibility: Visibility = Visibility.PUBLIC
    start_line: int = 0
    end_line: int = 0


@dataclass(frozen=True)
class ImportInfo:
    """Represents a single import statement.

    Attributes:
        module: The module path being imported (e.g. "os.path").
        names: The specific names imported (e.g. ["join", "dirname"]).
              Empty list means the entire module was imported.
        alias: The alias used in an `import X as Y` statement, if any.
        is_relative: True if this is a relative import (starts with a dot).
    """

    module: str
    names: list[str] = field(default_factory=list)
    alias: Optional[str] = None
    is_relative: bool = False


@dataclass
class ModuleInfo:
    """Represents a single parsed source file (module).

    This is the central data structure produced by a parser for one file.
    It aggregates all top-level elements discovered during parsing.

    Attributes:
        file_path: Absolute path to the source file.
        module_docstring: The module-level docstring, if present.
        imports: All import statements found in the module.
        functions: All top-level function definitions.
        classes: All class definitions.
        global_variables: Names of module-level variable assignments.
    """

    file_path: Path
    module_docstring: Optional[str] = None
    imports: list[ImportInfo] = field(default_factory=list)
    functions: list[FunctionInfo] = field(default_factory=list)
    classes: list[ClassInfo] = field(default_factory=list)
    global_variables: list[str] = field(default_factory=list)


@dataclass
class ParseResult:
    """Aggregated result of parsing an entire codebase.

    Produced by running a parser across all source files in a project.
    This is the top-level structure handed off to the analyzer module.

    Attributes:
        modules: A list of ModuleInfo objects, one per parsed file.
        language: The language identifier (e.g. "python").
        errors: A list of human-readable error messages for files
                that could not be parsed.
    """

    modules: list[ModuleInfo] = field(default_factory=list)
    language: str = "unknown"
    errors: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Abstract Base Parser
# ---------------------------------------------------------------------------


class BaseParser(ABC):
    """Abstract interface that all language-specific parsers must implement.

    A concrete parser (e.g. PythonParser) subclasses BaseParser and
    provides implementations for parsing individual files and collecting
    results across an entire directory tree.

    Example usage (once a concrete parser exists):
        parser = PythonParser()
        if parser.can_parse(Path("main.py")):
            module = parser.parse_file(Path("main.py"))
    """

    @abstractmethod
    def language(self) -> str:
        """Return the language identifier this parser handles.

        Returns:
            A lowercase string such as "python", "javascript", etc.
        """

    @abstractmethod
    def supported_extensions(self) -> list[str]:
        """Return the file extensions this parser can handle.

        Returns:
            A list of extensions including the leading dot,
            e.g. [".py"] or [".js", ".jsx"].
        """

    def can_parse(self, file_path: Path) -> bool:
        """Check whether this parser supports the given file.

        The default implementation checks the file extension against
        supported_extensions(). Subclasses may override this for more
        sophisticated checks (e.g. shebang line inspection).

        Args:
            file_path: Path to the source file.

        Returns:
            True if this parser can handle the file.
        """
        return file_path.suffix in self.supported_extensions()

    @abstractmethod
    def parse_file(self, file_path: Path) -> ModuleInfo:
        """Parse a single source file into a ModuleInfo structure.

        Args:
            file_path: Absolute or relative path to the source file.

        Returns:
            A ModuleInfo dataclass populated with the parsed elements.

        Raises:
            FileNotFoundError: If the file does not exist.
            SyntaxError: If the file contains unparseable syntax.
        """

    def parse_directory(
        self,
        root: Path,
        exclude_dirs: Optional[list[str]] = None,
    ) -> ParseResult:
        """Parse all supported files under a directory tree.

        Walks the directory, filters by supported extensions, and
        aggregates individual ModuleInfo results into a ParseResult.
        Files that fail to parse are recorded in ParseResult.errors
        rather than raising exceptions.

        Args:
            root: The root directory to search.
            exclude_dirs: Directory names to skip during traversal.

        Returns:
            A ParseResult containing all successfully parsed modules
            and any errors encountered.
        """
        import os

        if exclude_dirs is None:
            exclude_dirs = []

        result = ParseResult(language=self.language())

        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in exclude_dirs]

            for fname in filenames:
                fpath = Path(dirpath) / fname
                if not self.can_parse(fpath):
                    continue
                try:
                    module_info = self.parse_file(fpath)
                    result.modules.append(module_info)
                except Exception as exc:
                    result.errors.append(f"{fpath}: {exc}")

        return result
