"""
analyzer.py -- Semantic Analyzer Engine.

Takes ParseResult data from the parser module and performs semantic
analysis to understand code relationships, dependencies, and structure.

Responsibilities:
    1. Build the import dependency graph (internal vs external).
    2. Map the class inheritance hierarchy.
    3. Compute per-module metrics (complexity, documentation coverage).
    4. Aggregate codebase-wide statistics.

Usage:
    from src.parser.registry import ParserRegistry
    from src.analyzer.analyzer import SemanticAnalyzer

    registry = ParserRegistry()
    # Assuming parsers are registered
    parse_results = registry.parse_all(Path("./src"))

    # Combine results if needed or analyze one
    analyzer = SemanticAnalyzer()
    if parse_results:
        analysis = analyzer.analyze(parse_results[0])
        print(analysis.codebase_stats)
"""

from __future__ import annotations

import logging
from collections import Counter
from pathlib import Path
from typing import Optional

from src.parser.base import (
    ClassInfo,
    FunctionInfo,
    ModuleInfo,
    ParseResult,
    Visibility,
)
from src.analyzer.models import (
    AnalysisResult,
    CodebaseStats,
    DependencyEdge,
    DependencyGraph,
    InheritanceNode,
    InheritanceTree,
    ModuleMetrics,
)

logger = logging.getLogger("CodeScribe")


class SemanticAnalyzer:
    """Analyzes parsed code to discover relationships and compute metrics.

    The analyzer is stateless. Each call to analyze() produces an
    independent AnalysisResult from the provided ParseResult.

    Attributes:
        _project_root: Optional root path used to resolve internal
                      module names. If not set, all imports are
                      treated based on heuristics.
    """

    def __init__(self, project_root: Optional[Path] = None) -> None:
        """Initialize the analyzer.

        Args:
            project_root: The root directory of the project being
                         analyzed. Used to distinguish internal imports
                         from external/stdlib imports.
        """
        self._project_root = project_root.resolve() if project_root else None

    def analyze(self, parse_result: ParseResult) -> AnalysisResult:
        """Run the full analysis pipeline on a ParseResult.

        Args:
            parse_result: The output of a parser's parse_directory call.

        Returns:
            A fully populated AnalysisResult.
        """
        result = AnalysisResult(language=parse_result.language)

        # Collect known module names from the parsed files.
        known_modules = self._collect_known_modules(parse_result)

        # Step 1: Build dependency graph.
        result.dependency_graph = self._build_dependency_graph(
            parse_result, known_modules
        )

        # Step 2: Build inheritance tree.
        result.inheritance_tree = self._build_inheritance_tree(parse_result)

        # Step 3: Compute per-module metrics.
        result.module_metrics = self._compute_module_metrics(parse_result)

        # Step 4: Aggregate codebase statistics.
        result.codebase_stats = self._compute_codebase_stats(
            result.module_metrics, result.dependency_graph
        )

        # Propagate parse errors as warnings.
        for err in parse_result.errors:
            result.warnings.append("Parse error: {}".format(err))

        logger.info(
            "Analysis complete: %d modules, %d dependencies, %d classes in hierarchy",
            result.codebase_stats.total_modules,
            len(result.dependency_graph.edges),
            len(result.inheritance_tree.nodes),
        )

        return result

    # -------------------------------------------------------------------
    # Step 1: Dependency Graph
    # -------------------------------------------------------------------

    def _collect_known_modules(self, parse_result: ParseResult) -> set[str]:
        """Build a set of module names from parsed files.

        This is used to determine whether an import targets an internal
        module (part of this project) or an external dependency.

        Args:
            parse_result: The parser output.

        Returns:
            A set of module name strings derived from file paths.
        """
        known: set[str] = set()
        for mod in parse_result.modules:
            # Derive module name from file path.
            name = self._path_to_module_name(mod.file_path)
            if name:
                known.add(name)
                # Also add parent package names.
                parts = name.split(".")
                for i in range(1, len(parts)):
                    known.add(".".join(parts[:i]))
        return known

    def _path_to_module_name(self, file_path: Path) -> Optional[str]:
        """Convert a file path to a Python-style dotted module name.

        If a project root is set, the module name is relative to it.
        Otherwise, we use the file's own path components.

        Args:
            file_path: Absolute or relative path to the source file.

        Returns:
            A dotted module name string, or None if conversion fails.
        """
        try:
            path = Path(file_path)
            if self._project_root:
                path = path.relative_to(self._project_root)
            # Remove .py extension and convert separators to dots.
            parts = list(path.parts)
            if parts and parts[-1].endswith(".py"):
                parts[-1] = parts[-1][:-3]
            # Remove __init__ from the end (it represents the package).
            if parts and parts[-1] == "__init__":
                parts = parts[:-1]
            if not parts:
                return None
            return ".".join(parts)
        except (ValueError, TypeError):
            return None

    def _build_dependency_graph(
        self,
        parse_result: ParseResult,
        known_modules: set[str],
    ) -> DependencyGraph:
        """Construct the import dependency graph.

        Args:
            parse_result: The parser output.
            known_modules: Set of internal module names.

        Returns:
            A populated DependencyGraph.
        """
        graph = DependencyGraph()
        graph.modules = set(known_modules)

        for mod in parse_result.modules:
            source_name = self._path_to_module_name(mod.file_path) or str(mod.file_path)
            graph.modules.add(source_name)

            for imp in mod.imports:
                target = imp.module
                if not target:
                    continue

                # Determine if the import target is internal.
                top_level = target.split(".")[0]
                is_internal = (
                    target in known_modules
                    or top_level in known_modules
                    or imp.is_relative
                )

                edge = DependencyEdge(
                    source=source_name,
                    target=target,
                    imported_names=list(imp.names),
                    is_internal=is_internal,
                    is_relative=imp.is_relative,
                )
                graph.edges.append(edge)

                if is_internal:
                    graph.internal_deps.add(target)
                else:
                    graph.external_deps.add(target)

        return graph

    # -------------------------------------------------------------------
    # Step 2: Inheritance Tree
    # -------------------------------------------------------------------

    def _build_inheritance_tree(
        self, parse_result: ParseResult
    ) -> InheritanceTree:
        """Construct the class inheritance hierarchy.

        Maps every class to its parent classes and discovers which
        classes in the codebase are subclassed by others.

        Args:
            parse_result: The parser output.

        Returns:
            A populated InheritanceTree.
        """
        tree = InheritanceTree()

        # First pass: register all classes.
        for mod in parse_result.modules:
            module_name = self._path_to_module_name(mod.file_path) or str(mod.file_path)
            for cls in mod.classes:
                fq_name = "{}.{}".format(module_name, cls.name)
                node = InheritanceNode(
                    class_name=fq_name,
                    module_path=str(mod.file_path),
                    base_classes=list(cls.base_classes),
                )
                tree.nodes[fq_name] = node

        # Second pass: resolve subclass relationships.
        # Build a lookup from short class name to fully qualified names.
        short_to_fq: dict[str, list[str]] = {}
        for fq_name in tree.nodes:
            short = fq_name.rsplit(".", 1)[-1]
            short_to_fq.setdefault(short, []).append(fq_name)

        for fq_name, node in tree.nodes.items():
            for base in node.base_classes:
                # Try to find the base class in known nodes.
                candidates = short_to_fq.get(base, [])
                for candidate in candidates:
                    if candidate != fq_name and candidate in tree.nodes:
                        tree.nodes[candidate].subclasses.append(fq_name)
                        node.depth = max(node.depth, tree.nodes[candidate].depth + 1)

        # Identify root classes (no known parent in the codebase).
        for fq_name, node in tree.nodes.items():
            has_internal_parent = False
            for base in node.base_classes:
                candidates = short_to_fq.get(base, [])
                if any(c in tree.nodes and c != fq_name for c in candidates):
                    has_internal_parent = True
                    break
            if not has_internal_parent:
                tree.roots.append(fq_name)

        return tree

    # -------------------------------------------------------------------
    # Step 3: Per-Module Metrics
    # -------------------------------------------------------------------

    def _compute_module_metrics(
        self, parse_result: ParseResult
    ) -> list[ModuleMetrics]:
        """Compute quantitative metrics for each parsed module.

        Args:
            parse_result: The parser output.

        Returns:
            A list of ModuleMetrics, one per module.
        """
        metrics_list: list[ModuleMetrics] = []

        for mod in parse_result.modules:
            module_name = self._path_to_module_name(mod.file_path) or mod.file_path.name

            # Count methods across all classes.
            total_methods = sum(len(cls.methods) for cls in mod.classes)

            # Documentation coverage.
            documented_funcs = sum(1 for f in mod.functions if f.docstring)
            documented_classes = sum(1 for c in mod.classes if c.docstring)
            total_documentable = len(mod.functions) + len(mod.classes)
            doc_coverage = (
                (documented_funcs + documented_classes) / total_documentable
                if total_documentable > 0
                else 0.0
            )

            # Average parameters per function.
            all_funcs = list(mod.functions)
            for cls in mod.classes:
                all_funcs_and_methods = list(mod.functions)  # standalone funcs
            total_params = sum(len(f.parameters) for f in mod.functions)
            avg_params = (
                total_params / len(mod.functions) if mod.functions else 0.0
            )

            # Public vs private API surface.
            public_count = sum(
                1
                for f in mod.functions
                if f.visibility == Visibility.PUBLIC
            ) + sum(
                1
                for c in mod.classes
                if c.visibility == Visibility.PUBLIC
            )
            private_count = (
                len(mod.functions) + len(mod.classes) - public_count
            )

            # Estimate total lines from the last element's end_line.
            total_lines = self._estimate_line_count(mod)

            metrics = ModuleMetrics(
                module_name=module_name,
                file_path=mod.file_path,
                total_lines=total_lines,
                num_functions=len(mod.functions),
                num_classes=len(mod.classes),
                num_methods=total_methods,
                num_imports=len(mod.imports),
                num_global_vars=len(mod.global_variables),
                has_docstring=mod.module_docstring is not None,
                documented_functions=documented_funcs,
                documented_classes=documented_classes,
                documentation_coverage=round(doc_coverage, 2),
                avg_params_per_function=round(avg_params, 2),
                public_api_count=public_count,
                private_api_count=private_count,
            )
            metrics_list.append(metrics)

        return metrics_list

    def _estimate_line_count(self, mod: ModuleInfo) -> int:
        """Estimate the total line count of a module.

        Uses the end_line of the last function or class definition.
        Falls back to reading the file if possible.

        Args:
            mod: The module info to estimate lines for.

        Returns:
            An approximate line count.
        """
        max_line = 0
        for f in mod.functions:
            if f.end_line > max_line:
                max_line = f.end_line
        for c in mod.classes:
            if c.end_line > max_line:
                max_line = c.end_line

        if max_line > 0:
            return max_line

        # Fall back to counting lines in the file.
        try:
            return len(mod.file_path.read_text(encoding="utf-8").splitlines())
        except (OSError, UnicodeDecodeError):
            return 0

    # -------------------------------------------------------------------
    # Step 4: Codebase-Wide Statistics
    # -------------------------------------------------------------------

    def _compute_codebase_stats(
        self,
        module_metrics: list[ModuleMetrics],
        dep_graph: DependencyGraph,
    ) -> CodebaseStats:
        """Aggregate individual module metrics into codebase-wide stats.

        Args:
            module_metrics: List of per-module metrics.
            dep_graph: The dependency graph for determining most-imported.

        Returns:
            A populated CodebaseStats.
        """
        total_modules = len(module_metrics)
        if total_modules == 0:
            return CodebaseStats()

        total_functions = sum(m.num_functions for m in module_metrics)
        total_classes = sum(m.num_classes for m in module_metrics)
        total_methods = sum(m.num_methods for m in module_metrics)
        total_imports = sum(m.num_imports for m in module_metrics)
        total_lines = sum(m.total_lines for m in module_metrics)

        # Overall documentation coverage.
        total_documented = sum(m.documented_functions + m.documented_classes for m in module_metrics)
        total_documentable = total_functions + total_classes
        overall_doc_coverage = (
            total_documented / total_documentable
            if total_documentable > 0
            else 0.0
        )

        # Averages.
        avg_functions = total_functions / total_modules
        avg_classes = total_classes / total_modules

        # Most complex module (highest function + class + method count).
        most_complex = max(
            module_metrics,
            key=lambda m: m.num_functions + m.num_classes + m.num_methods,
        )

        # Most depended-on module.
        target_counter: Counter[str] = Counter()
        for edge in dep_graph.edges:
            if edge.is_internal:
                target_counter[edge.target] += 1

        most_depended = (
            target_counter.most_common(1)[0][0]
            if target_counter
            else None
        )

        return CodebaseStats(
            total_modules=total_modules,
            total_functions=total_functions,
            total_classes=total_classes,
            total_methods=total_methods,
            total_imports=total_imports,
            total_lines=total_lines,
            overall_doc_coverage=round(overall_doc_coverage, 2),
            avg_functions_per_module=round(avg_functions, 2),
            avg_classes_per_module=round(avg_classes, 2),
            most_complex_module=most_complex.module_name,
            most_depended_on=most_depended,
        )
