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
        self._parsers: dict[str, BaseParser] = {}

    def register(self, parser: BaseParser) -> None:
        """Register a parser for all of its supported extensions.

        If an extension is already registered, the new parser replaces
        the previous one silently.

        Args:
            parser: A concrete BaseParser implementation to register.
        """
        for ext in parser.supported_extensions():
            self._parsers[ext] = parser

    def get_parser_for_file(self, file_path: Path) -> Optional[BaseParser]:
        """Look up the appropriate parser for a given file.

        Args:
            file_path: Path to the source file.

        Returns:
            The registered BaseParser for the file's extension,
            or None if no parser is registered for that extension.
        """
        return self._parsers.get(file_path.suffix)

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
    ) -> list[ParseResult]:
        """Run every registered parser across the given directory.

        Each unique parser instance is invoked once with its own
        parse_directory call. Duplicate parser references (registered
        under multiple extensions) are deduplicated.

        Args:
            root: The root directory to search.
            exclude_dirs: Directory names to skip during traversal.

        Returns:
            A list of ParseResult objects, one per unique parser.
        """
        seen: set[int] = set()
        results: list[ParseResult] = []

        for parser in self._parsers.values():
            pid = id(parser)
            if pid in seen:
                continue
            seen.add(pid)
            result = parser.parse_directory(root, exclude_dirs)
            results.append(result)

        return results

    def __len__(self) -> int:
        """Return the number of registered extensions."""
        return len(self._parsers)

    def __repr__(self) -> str:
        """Return a developer-friendly string representation."""
        exts = ", ".join(self.supported_extensions())
        return f"ParserRegistry(extensions=[{exts}])"
