"""
registry.py -- Central Parser Registry.

Provides a singleton registry that maps file extensions to their
corresponding parser implementations. The CLI and other entry points
use this registry to look up the correct parser for a given file
without needing to know about specific parser classes.

Usage:
    from src.parser.registry import ParserRegistry

    registry = ParserRegistry()
    registry.register(PythonParser())

    parser = registry.get_parser_for_file(Path("main.py"))
    if parser:
        result = parser.parse_file(Path("main.py"))
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from src.parser.base import BaseParser, ParseResult


class ParserRegistry:
    """Maps file extensions to parser instances.

    Acts as a lookup table so the rest of the application can resolve
    the correct parser for any given file without tight coupling to
    specific language implementations.

    Attributes:
        _parsers: Internal mapping of file extension to BaseParser.
    """

    def __init__(self) -> None:
        """Initialize an empty registry."""
        from src.parser.universal import UniversalParser
        self._parsers: dict[str, BaseParser] = {}
        self._fallback_parser = UniversalParser()

    def register(self, parser: BaseParser) -> None:
        """Register a parser for all of its supported extensions.

        If an extension is already registered, the new parser replaces
        the previous one silently.

        Args:
            parser: A concrete BaseParser implementation to register.
        """
        for ext in parser.supported_extensions():
            self._parsers[ext] = parser

    def get_parser_for_file(self, file_path: Path) -> BaseParser:
        """Look up the appropriate parser for a given file.

        Args:
            file_path: Path to the source file.

        Returns:
            The registered BaseParser for the file's extension,
            or the Universal fallback parser if no parser is registered.
        """
        return self._parsers.get(file_path.suffix, self._fallback_parser)

    def get_parser_for_extension(self, extension: str) -> Optional[BaseParser]:
        """Look up the appropriate parser for a given extension string.

        Args:
            extension: A file extension including the leading dot
                      (e.g. ".py").

        Returns:
            The registered BaseParser, or None if not found.
        """
        return self._parsers.get(extension)

    def supported_extensions(self) -> list[str]:
        """Return all file extensions that have a registered parser.

        Returns:
            A sorted list of extension strings.
        """
        return sorted(self._parsers.keys())

    def parse_all(
        self,
        root: Path,
        exclude_dirs: Optional[list[str]] = None,
    ) -> ParseResult:
        """Parse all files in the given directory using appropriate parsers.

        Walks the directory tree, skipping excluded directories, and uses
        the specific parser registered for each file's extension, or falls
        back to the UniversalParser.

        Args:
            root: The root directory to search.
            exclude_dirs: Directory names to skip during traversal.

        Returns:
            A single combined ParseResult containing all parsed modules.
        """
        import os

        if exclude_dirs is None:
            exclude_dirs = []

        combined_result = ParseResult(language="mixed")

        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in exclude_dirs]

            for fname in filenames:
                if fname.startswith(".") or not Path(fname).suffix:
                    continue

                fpath = Path(dirpath) / fname
                parser = self.get_parser_for_file(fpath)

                try:
                    module_info = parser.parse_file(fpath)
                    # Exclude empty modules parsed by universal parser
                    if parser.language() == "universal" and not module_info.classes and not module_info.functions:
                        continue
                    combined_result.modules.append(module_info)
                except Exception as exc:
                    combined_result.errors.append(f"{fpath}: {exc}")

        return combined_result

    def __len__(self) -> int:
        """Return the number of registered extensions."""
        return len(self._parsers)

    def __repr__(self) -> str:
        """Return a developer-friendly string representation."""
        exts = ", ".join(self.supported_extensions())
        return f"ParserRegistry(extensions=[{exts}])"
