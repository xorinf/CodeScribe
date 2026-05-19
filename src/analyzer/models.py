"""
models.py -- Data Models for Semantic Analysis Results.

Defines the output structures produced by the semantic analyzer.
These models capture the relationships, dependencies, and metrics
that the analyzer discovers by examining parsed code data.

Data Flow:
    ParseResult (from parser)  -->  SemanticAnalyzer.analyze()  -->  AnalysisResult
                                                                        |
                                                                        +-- DependencyGraph
                                                                        +-- InheritanceTree
                                                                        +-- ModuleMetrics
                                                                        +-- CodebaseStats
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Dependency Graph
# ---------------------------------------------------------------------------


@dataclass
class DependencyEdge:
    """Represents a single dependency from one module to another.

    Attributes:
        source: The module that contains the import statement.
        target: The module being imported.
        imported_names: Specific names imported (empty means whole module).
        is_internal: True if the target is part of this codebase.
        is_relative: True if this is a relative import.
    """

    source: str
    target: str
    imported_names: list[str] = field(default_factory=list)
    is_internal: bool = False
    is_relative: bool = False


@dataclass
class DependencyGraph:
    """Represents the full import dependency graph of the codebase.

    Attributes:
        edges: All dependency edges discovered across all modules.
        modules: Set of all module names that appear in the graph.
        external_deps: Set of third-party/stdlib module names.
        internal_deps: Set of project-internal module names.
    """

    edges: list[DependencyEdge] = field(default_factory=list)
    modules: set[str] = field(default_factory=set)
    external_deps: set[str] = field(default_factory=set)
    internal_deps: set[str] = field(default_factory=set)

    def get_dependencies_of(self, module_name: str) -> list[DependencyEdge]:
        """Return all edges where the given module is the source.

        Args:
            module_name: The module to look up.

        Returns:
            List of DependencyEdge objects originating from this module.
        """
        return [e for e in self.edges if e.source == module_name]

    def get_dependents_of(self, module_name: str) -> list[DependencyEdge]:
        """Return all edges where the given module is the target.

        Shows which modules depend on the given module.

        Args:
            module_name: The module to look up.

        Returns:
            List of DependencyEdge objects pointing to this module.
        """
        return [e for e in self.edges if e.target == module_name]


# ---------------------------------------------------------------------------
# Inheritance Tree
# ---------------------------------------------------------------------------


@dataclass
class InheritanceNode:
    """Represents a class and its position in the inheritance hierarchy.

    Attributes:
        class_name: The fully qualified class name (module.ClassName).
        module_path: The file path where this class is defined.
        base_classes: Direct parent class names.
        subclasses: Direct child class names discovered in the codebase.
        depth: The depth in the inheritance tree (0 = no known parent).
    """

    class_name: str
    module_path: Optional[str] = None
    base_classes: list[str] = field(default_factory=list)
    subclasses: list[str] = field(default_factory=list)
    depth: int = 0


@dataclass
class InheritanceTree:
    """The full class inheritance hierarchy of the codebase.

    Attributes:
        nodes: Mapping of fully qualified class name to its node.
        roots: Class names that have no known parent in the codebase.
    """

    nodes: dict[str, InheritanceNode] = field(default_factory=dict)
    roots: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Module-Level Metrics
# ---------------------------------------------------------------------------


@dataclass
class ModuleMetrics:
    """Quantitative metrics computed for a single module.

    Attributes:
        module_name: The module's file name or qualified path.
        file_path: Absolute path to the source file.
        total_lines: Approximate line count of the module.
        num_functions: Number of top-level functions.
        num_classes: Number of class definitions.
        num_methods: Total number of methods across all classes.
        num_imports: Number of import statements.
        num_global_vars: Number of module-level variable assignments.
        has_docstring: Whether the module has a top-level docstring.
        documented_functions: Number of functions that have docstrings.
        documented_classes: Number of classes that have docstrings.
        documentation_coverage: Percentage of documented elements (0.0 - 1.0).
        avg_params_per_function: Average parameter count per function.
        public_api_count: Number of public functions and classes.
        private_api_count: Number of protected/private functions and classes.
    """

    module_name: str
    file_path: Optional[Path] = None
    total_lines: int = 0
    num_functions: int = 0
    num_classes: int = 0
    num_methods: int = 0
    num_imports: int = 0
    num_global_vars: int = 0
    has_docstring: bool = False
    documented_functions: int = 0
    documented_classes: int = 0
    documentation_coverage: float = 0.0
    avg_params_per_function: float = 0.0
    public_api_count: int = 0
    private_api_count: int = 0


# ---------------------------------------------------------------------------
# Codebase-Level Statistics
# ---------------------------------------------------------------------------


@dataclass
class CodebaseStats:
    """Aggregated statistics across the entire analyzed codebase.

    Attributes:
        total_modules: Number of source files analyzed.
        total_functions: Total function definitions across all modules.
        total_classes: Total class definitions across all modules.
        total_methods: Total method definitions across all classes.
        total_imports: Total import statements across all modules.
        total_lines: Approximate total line count.
        overall_doc_coverage: Percentage of documented elements (0.0 - 1.0).
        avg_functions_per_module: Average functions per module.
        avg_classes_per_module: Average classes per module.
        most_complex_module: Module with the highest element count.
        most_depended_on: Module that is imported by the most others.
    """

    total_modules: int = 0
    total_functions: int = 0
    total_classes: int = 0
    total_methods: int = 0
    total_imports: int = 0
    total_lines: int = 0
    overall_doc_coverage: float = 0.0
    avg_functions_per_module: float = 0.0
    avg_classes_per_module: float = 0.0
    most_complex_module: Optional[str] = None
    most_depended_on: Optional[str] = None


# ---------------------------------------------------------------------------
# Top-Level Analysis Result
# ---------------------------------------------------------------------------


@dataclass
class AnalysisResult:
    """Complete output of the semantic analyzer.

    Aggregates all analysis products into a single structure for
    downstream consumption by the generator module.

    Attributes:
        dependency_graph: The import dependency graph.
        inheritance_tree: The class inheritance hierarchy.
        module_metrics: Per-module quantitative metrics.
        codebase_stats: Aggregated statistics for the whole codebase.
        language: The language of the analyzed codebase.
        warnings: Non-fatal issues discovered during analysis.
    """

    dependency_graph: DependencyGraph = field(default_factory=DependencyGraph)
    inheritance_tree: InheritanceTree = field(default_factory=InheritanceTree)
    module_metrics: list[ModuleMetrics] = field(default_factory=list)
    codebase_stats: CodebaseStats = field(default_factory=CodebaseStats)
    language: str = "unknown"
    warnings: list[str] = field(default_factory=list)
