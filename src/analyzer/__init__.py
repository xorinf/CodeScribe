"""
src.analyzer -- Semantic Analysis Package.

This package analyzes parsed code structures to understand relationships,
dependencies, and architectural patterns. It produces structured analysis
results consumed by the generator module.

Public API:
    - SemanticAnalyzer: The main analysis engine.
    - AnalysisResult: Top-level output container.
    - DependencyGraph, InheritanceTree: Relationship models.
    - ModuleMetrics, CodebaseStats: Quantitative outputs.
"""

from src.analyzer.analyzer import SemanticAnalyzer
from src.analyzer.models import (
    AnalysisResult,
    CodebaseStats,
    DependencyGraph,
    InheritanceTree,
    ModuleMetrics,
)

__all__ = [
    "SemanticAnalyzer",
    "AnalysisResult",
    "CodebaseStats",
    "DependencyGraph",
    "InheritanceTree",
    "ModuleMetrics",
]
