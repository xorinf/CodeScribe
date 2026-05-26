"""
src.parser -- Code Parsing and AST Generation Package.

This package is responsible for ingesting source code files and
producing structured, language-agnostic representations (parse results)
that downstream modules (analyzer, generator) can consume.

Architecture:
    - base.py      : Abstract interfaces and data models that every
                     language-specific parser must implement.
    - registry.py  : A central registry that maps file extensions to
                     their corresponding parser implementations.
    - python_parser.py : Concrete parser for Python source files.
    - universal_parser.py : Fallback parser using regex for other languages.
"""
