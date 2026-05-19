"""
python_parser.py -- Concrete AST Parser for Python Source Files.

Uses Python's built-in `ast` module to parse source files into Abstract
Syntax Trees, then walks the tree to extract structured information
(functions, classes, methods, imports, docstrings, type hints) and
maps them onto the data models defined in base.py.

Supported Python features:
    - Module-level docstrings
    - Import and ImportFrom statements
    - Function definitions with parameters, type hints, decorators
    - Class definitions with base classes, methods, decorators
    - Visibility detection (public vs private via underscore convention)
    - Static methods and class methods
    - Global variable assignments at module level
"""

from __future__ import annotations

import ast
import logging
from pathlib import Path
from typing import Optional

from src.parser.base import (
    BaseParser,
    ClassInfo,
    FunctionInfo,
    ImportInfo,
    MethodInfo,
    ModuleInfo,
    Parameter,
    Visibility,
)

logger = logging.getLogger("CodeScribe")


# ---------------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------------


def _determine_visibility(name: str) -> Visibility:
    """Determine the visibility of a code element by its naming convention.

    Python convention:
        - Names starting with double underscore (but not ending with it)
          are name-mangled and considered private.
        - Names starting with a single underscore are protected/internal.
        - Everything else is public.

    Args:
        name: The identifier name to classify.

    Returns:
        The corresponding Visibility enum value.
    """
    if name.startswith("__") and not name.endswith("__"):
        return Visibility.PRIVATE
    if name.startswith("_"):
        return Visibility.PROTECTED
    return Visibility.PUBLIC


def _get_docstring(node: ast.AST) -> Optional[str]:
    """Extract the docstring from an AST node, if present.

    Works for Module, FunctionDef, AsyncFunctionDef, and ClassDef nodes.

    Args:
        node: The AST node to inspect.

    Returns:
        The docstring text, or None if no docstring is found.
    """
    try:
        return ast.get_docstring(node)
    except TypeError:
        return None


def _unparse_annotation(node: Optional[ast.AST]) -> Optional[str]:
    """Convert a type annotation AST node back to its source string.

    Uses ast.unparse (Python 3.9+) to reconstruct the annotation.

    Args:
        node: The annotation AST node, or None.

    Returns:
        The string representation of the annotation, or None.
    """
    if node is None:
        return None
    try:
        return ast.unparse(node)
    except Exception:
        return None


def _unparse_default(node: Optional[ast.AST]) -> Optional[str]:
    """Convert a default value AST node back to its source string.

    Args:
        node: The default value AST node, or None.

    Returns:
        The string representation of the default value, or None.
    """
    if node is None:
        return None
    try:
        return ast.unparse(node)
    except Exception:
        return None


def _extract_decorator_names(decorator_list: list[ast.expr]) -> list[str]:
    """Extract human-readable names from a list of decorator AST nodes.

    Handles simple decorators (@staticmethod), attribute decorators
    (@app.route), and call decorators (@pytest.mark.parametrize(...)).

    Args:
        decorator_list: List of decorator expression nodes.

    Returns:
        A list of decorator name strings.
    """
    names: list[str] = []
    for dec in decorator_list:
        try:
            names.append(ast.unparse(dec))
        except Exception:
            names.append("<unknown_decorator>")
    return names


def _extract_parameters(func_node: ast.FunctionDef) -> list[Parameter]:
    """Extract parameter information from a function definition node.

    Handles positional arguments, keyword-only arguments, defaults,
    and type annotations. Skips 'self' and 'cls' parameters for methods.

    Args:
        func_node: An ast.FunctionDef or ast.AsyncFunctionDef node.

    Returns:
        An ordered list of Parameter dataclass instances.
    """
    params: list[Parameter] = []
    args_node = func_node.args

    # Calculate default value alignment.
    # Defaults are right-aligned to positional args:
    #   def f(a, b, c=1, d=2) -> defaults = [1, 2], args = [a, b, c, d]
    #   So c gets defaults[0], d gets defaults[1].
    positional_args = args_node.args
    num_defaults = len(args_node.defaults)
    default_offset = len(positional_args) - num_defaults

    for i, arg in enumerate(positional_args):
        name = arg.arg
        if name in ("self", "cls"):
            continue

        type_hint = _unparse_annotation(arg.annotation)

        default_value = None
        default_index = i - default_offset
        if default_index >= 0 and default_index < len(args_node.defaults):
            default_value = _unparse_default(args_node.defaults[default_index])

        params.append(Parameter(
            name=name,
            type_hint=type_hint,
            default_value=default_value,
        ))

    # Keyword-only arguments (after * in the signature)
    for i, arg in enumerate(args_node.kwonlyargs):
        type_hint = _unparse_annotation(arg.annotation)
        default_value = None
        if i < len(args_node.kw_defaults) and args_node.kw_defaults[i] is not None:
            default_value = _unparse_default(args_node.kw_defaults[i])

        params.append(Parameter(
            name=arg.arg,
            type_hint=type_hint,
            default_value=default_value,
        ))

    # *args
    if args_node.vararg:
        params.append(Parameter(
            name=f"*{args_node.vararg.arg}",
            type_hint=_unparse_annotation(args_node.vararg.annotation),
        ))

    # **kwargs
    if args_node.kwarg:
        params.append(Parameter(
            name=f"**{args_node.kwarg.arg}",
            type_hint=_unparse_annotation(args_node.kwarg.annotation),
        ))

    return params


# ---------------------------------------------------------------------------
# Python AST Parser
# ---------------------------------------------------------------------------


class PythonParser(BaseParser):
    """Concrete parser for Python source files using the ast module.

    Parses .py files into the unified data model defined in base.py.
    Leverages Python's built-in ast module for reliable, standard-library
    parsing without external dependencies.

    Example:
        parser = PythonParser()
        module_info = parser.parse_file(Path("src/cli.py"))
        print(module_info.functions)
    """

    def language(self) -> str:
        """Return the language identifier.

        Returns:
            The string "python".
        """
        return "python"

    def supported_extensions(self) -> list[str]:
        """Return supported file extensions for Python.

        Returns:
            A list containing ".py".
        """
        return [".py"]

    def parse_file(self, file_path: Path) -> ModuleInfo:
        """Parse a single Python source file into a ModuleInfo structure.

        Reads the file, parses it into an AST, then walks the top-level
        nodes to extract functions, classes, imports, and module-level
        variable assignments.

        Args:
            file_path: Path to the .py file.

        Returns:
            A populated ModuleInfo dataclass.

        Raises:
            FileNotFoundError: If the file does not exist.
            SyntaxError: If the file cannot be parsed as valid Python.
        """
        file_path = Path(file_path).resolve()

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(file_path))

        module_info = ModuleInfo(file_path=file_path)
        module_info.module_docstring = _get_docstring(tree)

        for node in ast.iter_child_nodes(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                module_info.functions.append(self._parse_function(node))

            elif isinstance(node, ast.ClassDef):
                module_info.classes.append(self._parse_class(node))

            elif isinstance(node, ast.Import):
                module_info.imports.extend(self._parse_import(node))

            elif isinstance(node, ast.ImportFrom):
                module_info.imports.append(self._parse_import_from(node))

            elif isinstance(node, ast.Assign):
                module_info.global_variables.extend(
                    self._parse_assignment(node)
                )

            elif isinstance(node, ast.AnnAssign):
                var_name = self._parse_ann_assignment(node)
                if var_name:
                    module_info.global_variables.append(var_name)

        logger.debug(
            "Parsed %s: %d functions, %d classes, %d imports",
            file_path.name,
            len(module_info.functions),
            len(module_info.classes),
            len(module_info.imports),
        )

        return module_info

    # -------------------------------------------------------------------
    # Private parsing methods
    # -------------------------------------------------------------------

    def _parse_function(self, node: ast.FunctionDef) -> FunctionInfo:
        """Parse a top-level function definition node.

        Args:
            node: An ast.FunctionDef or ast.AsyncFunctionDef node.

        Returns:
            A populated FunctionInfo dataclass.
        """
        return FunctionInfo(
            name=node.name,
            docstring=_get_docstring(node),
            parameters=_extract_parameters(node),
            return_type=_unparse_annotation(node.returns),
            decorators=_extract_decorator_names(node.decorator_list),
            visibility=_determine_visibility(node.name),
            start_line=node.lineno,
            end_line=node.end_lineno or node.lineno,
        )

    def _parse_class(self, node: ast.ClassDef) -> ClassInfo:
        """Parse a class definition node including its methods.

        Args:
            node: An ast.ClassDef node.

        Returns:
            A populated ClassInfo dataclass.
        """
        methods: list[MethodInfo] = []
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                methods.append(self._parse_method(item))

        base_classes: list[str] = []
        for base in node.bases:
            try:
                base_classes.append(ast.unparse(base))
            except Exception:
                base_classes.append("<unknown>")

        return ClassInfo(
            name=node.name,
            docstring=_get_docstring(node),
            base_classes=base_classes,
            methods=methods,
            decorators=_extract_decorator_names(node.decorator_list),
            visibility=_determine_visibility(node.name),
            start_line=node.lineno,
            end_line=node.end_lineno or node.lineno,
        )

    def _parse_method(self, node: ast.FunctionDef) -> MethodInfo:
        """Parse a method definition inside a class body.

        Detects @staticmethod and @classmethod decorators to set the
        corresponding flags on the MethodInfo.

        Args:
            node: An ast.FunctionDef or ast.AsyncFunctionDef node
                 found inside a ClassDef body.

        Returns:
            A populated MethodInfo dataclass.
        """
        decorator_names = _extract_decorator_names(node.decorator_list)

        return MethodInfo(
            name=node.name,
            docstring=_get_docstring(node),
            parameters=_extract_parameters(node),
            return_type=_unparse_annotation(node.returns),
            decorators=decorator_names,
            visibility=_determine_visibility(node.name),
            is_static="staticmethod" in decorator_names,
            is_classmethod="classmethod" in decorator_names,
            start_line=node.lineno,
            end_line=node.end_lineno or node.lineno,
        )

    def _parse_import(self, node: ast.Import) -> list[ImportInfo]:
        """Parse an `import X` statement.

        A single import statement can import multiple modules
        (e.g. `import os, sys`), so this returns a list.

        Args:
            node: An ast.Import node.

        Returns:
            A list of ImportInfo dataclasses.
        """
        results: list[ImportInfo] = []
        for alias in node.names:
            results.append(ImportInfo(
                module=alias.name,
                names=[],
                alias=alias.asname,
                is_relative=False,
            ))
        return results

    def _parse_import_from(self, node: ast.ImportFrom) -> ImportInfo:
        """Parse a `from X import Y` statement.

        Args:
            node: An ast.ImportFrom node.

        Returns:
            A populated ImportInfo dataclass.
        """
        module = node.module or ""
        names = [alias.name for alias in node.names]

        return ImportInfo(
            module=module,
            names=names,
            alias=None,
            is_relative=node.level > 0,
        )

    def _parse_assignment(self, node: ast.Assign) -> list[str]:
        """Extract variable names from a module-level assignment.

        Only extracts simple name targets (e.g. `X = 10`).
        Ignores tuple unpacking, subscript, and attribute assignments.

        Args:
            node: An ast.Assign node.

        Returns:
            A list of variable name strings.
        """
        names: list[str] = []
        for target in node.targets:
            if isinstance(target, ast.Name):
                names.append(target.id)
        return names

    def _parse_ann_assignment(self, node: ast.AnnAssign) -> Optional[str]:
        """Extract the variable name from an annotated assignment.

        Handles statements like `x: int = 10`.

        Args:
            node: An ast.AnnAssign node.

        Returns:
            The variable name string, or None if the target
            is not a simple Name node.
        """
        if isinstance(node.target, ast.Name):
            return node.target.id
        return None
