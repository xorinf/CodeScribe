"""
src.generator -- Documentation Generation Package.

Transforms analyzed code data into human-readable documentation
in Markdown format. This is the final stage of the CodeScribe pipeline.

Public API:
    - DocGenerator: The main generation engine.
"""

from src.generator.generator import DocGenerator

__all__ = ["DocGenerator"]
