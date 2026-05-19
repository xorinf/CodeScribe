"""
generator.py -- Documentation Generator Engine.

Orchestrates the full documentation generation pipeline. Takes an
AnalysisResult (from the analyzer) and the original ParseResult
(from the parser), then uses the template engine to produce
complete, structured Markdown documentation files.

Responsibilities:
    1. Generate a master index document with project overview.
    2. Generate per-module documentation pages.
    3. Write all output files to the target directory.

Usage:
    from src.generator.generator import DocGenerator

    generator = DocGenerator(project_name="CodeScribe")
    generator.generate(parse_result, analysis_result, output_dir=Path("./docs"))
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from src.parser.base import ModuleInfo, ParseResult, FunctionInfo, ClassInfo
from src.analyzer.models import AnalysisResult, ModuleMetrics
from src.generator import templates
from src.generator.nlp import NLPEngine

logger = logging.getLogger("CodeScribe")


class DocGenerator:
    """Transforms analysis results into Markdown documentation files.

    The generator is the final stage of the CodeScribe pipeline.
    It receives structured data from the parser and analyzer, applies
    templates to produce human-readable documentation, and writes
    the output to disk.

    Attributes:
        _project_name: The name used in documentation headers.
        _include_private: Whether to document private/protected elements.
        _nlp_engine: The NLP Engine for enhancing docstrings.
    """

    def __init__(
        self,
        project_name: str = "Project",
        include_private: bool = False,
        use_nlp: bool = False,
        api_key: Optional[str] = None,
    ) -> None:
        """Initialize the generator.

        Args:
            project_name: Name of the project for documentation headers.
            include_private: If True, includes private and protected
                           elements in the generated documentation.
            use_nlp: Whether to enable AI-powered documentation generation.
            api_key: Optional API key for the AI model.
        """
        self._project_name = project_name
        self._include_private = include_private
        self._nlp_engine = NLPEngine(api_key=api_key, enabled=use_nlp)

    def generate(
        self,
        parse_result: ParseResult,
        analysis: AnalysisResult,
        output_dir: Path,
        single_file: bool = True,
    ) -> list[Path]:
        """Run the full documentation generation pipeline.

        Args:
            parse_result: The output from the parser.
            analysis: The output from the semantic analyzer.
            output_dir: Directory where documentation files are written.
            single_file: If True, generates a single index.md file.
                        If False, generates separate files per module.

        Returns:
            A list of Paths to the generated documentation files.
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        generated_files: list[Path] = []

        if single_file:
            path = self._generate_single_file(
                parse_result, analysis, output_dir
            )
            generated_files.append(path)
        else:
            paths = self._generate_multi_file(
                parse_result, analysis, output_dir
            )
            generated_files.extend(paths)

        logger.info(
            "Documentation generated: %d file(s) in %s",
            len(generated_files),
            output_dir,
        )

        return generated_files

    def _generate_single_file(
        self,
        parse_result: ParseResult,
        analysis: AnalysisResult,
        output_dir: Path,
    ) -> Path:
        """Generate all documentation into a single index.md file.

        Args:
            parse_result: Parser output.
            analysis: Analyzer output.
            output_dir: Target directory.

        Returns:
            Path to the generated index.md file.
        """
        sections: list[str] = []

        # 1. Project header with stats
        sections.append(templates.render_project_header(
            self._project_name,
            analysis.codebase_stats,
            analysis.language,
        ))

        # 2. Table of contents
        modules = self._filter_modules(parse_result.modules)
        sections.append(templates.render_table_of_contents(modules))

        # 3. Module sections
        metrics_map = self._build_metrics_map(analysis)
        for mod in modules:
            module_metrics = metrics_map.get(mod.file_path.name)
            filtered_mod = self._filter_module_elements(mod)
            sections.append(templates.render_module_section(
                filtered_mod, module_metrics
            ))

        # 4. Dependency analysis
        sections.append(templates.render_dependency_section(analysis))

        # 5. Class hierarchy
        inheritance_section = templates.render_inheritance_section(analysis)
        if inheritance_section:
            sections.append(inheritance_section)

        # Write to file
        content = "\n".join(sections)
        output_path = output_dir / "index.md"
        output_path.write_text(content, encoding="utf-8")

        logger.info("Generated %s (%d bytes)", output_path, len(content))
        return output_path

    def _generate_multi_file(
        self,
        parse_result: ParseResult,
        analysis: AnalysisResult,
        output_dir: Path,
    ) -> list[Path]:
        """Generate separate documentation files per module.

        Also generates an index.md with the project overview and
        links to individual module docs.

        Args:
            parse_result: Parser output.
            analysis: Analyzer output.
            output_dir: Target directory.

        Returns:
            List of paths to all generated files.
        """
        generated: list[Path] = []
        modules = self._filter_modules(parse_result.modules)
        metrics_map = self._build_metrics_map(analysis)

        # Generate index with overview
        index_sections: list[str] = []
        index_sections.append(templates.render_project_header(
            self._project_name,
            analysis.codebase_stats,
            analysis.language,
        ))
        index_sections.append("## Modules\n")
        for mod in modules:
            name = mod.file_path.stem
            index_sections.append("- [{}]({}.md)".format(name, name))
        index_sections.append("")
        index_sections.append(templates.render_dependency_section(analysis))
        inheritance_section = templates.render_inheritance_section(analysis)
        if inheritance_section:
            index_sections.append(inheritance_section)

        index_path = output_dir / "index.md"
        index_path.write_text("\n".join(index_sections), encoding="utf-8")
        generated.append(index_path)

        # Generate per-module files
        for mod in modules:
            module_metrics = metrics_map.get(mod.file_path.name)
            filtered_mod = self._filter_module_elements(mod)
            content = templates.render_module_section(
                filtered_mod, module_metrics
            )

            file_name = "{}.md".format(mod.file_path.stem)
            file_path = output_dir / file_name
            file_path.write_text(content, encoding="utf-8")
            generated.append(file_path)

            logger.debug("Generated %s", file_path)

        return generated

    # -------------------------------------------------------------------
    # Internal Helpers
    # -------------------------------------------------------------------

    def _build_metrics_map(
        self, analysis: AnalysisResult
    ) -> dict[str, ModuleMetrics]:
        """Build a lookup from module file name to its metrics.

        Args:
            analysis: The analysis result.

        Returns:
            A dict mapping file names to ModuleMetrics.
        """
        result: dict[str, ModuleMetrics] = {}
        for m in analysis.module_metrics:
            if m.file_path:
                result[m.file_path.name] = m
        return result

    def _filter_modules(self, modules: list[ModuleInfo]) -> list[ModuleInfo]:
        """Filter and sort modules for documentation.

        Removes __init__.py files that have no content worth documenting.
        Sorts remaining modules alphabetically.

        Args:
            modules: The full list of parsed modules.

        Returns:
            A filtered and sorted list.
        """
        filtered = []
        for mod in modules:
            # Skip empty __init__.py files
            if mod.file_path.name == "__init__.py":
                has_content = (
                    mod.functions
                    or mod.classes
                    or mod.global_variables
                )
                if not has_content:
                    continue
            filtered.append(mod)

        return sorted(filtered, key=lambda m: m.file_path.name)

    def _filter_module_elements(self, mod: ModuleInfo) -> ModuleInfo:
        """Filter out private elements if include_private is False.

        Creates a shallow copy of the ModuleInfo with filtered lists.

        Args:
            mod: The original module info.

        Returns:
            A new ModuleInfo with filtered elements.
        """
        if self._include_private:
            return mod

        from src.parser.base import Visibility
        import dataclasses

        filtered = ModuleInfo(
            file_path=mod.file_path,
            module_docstring=mod.module_docstring,
            imports=mod.imports,
            global_variables=mod.global_variables,
        )

        # Filter functions and optionally enhance docstrings
        filtered.functions = []
        for f in mod.functions:
            if not self._include_private and f.visibility != Visibility.PUBLIC:
                continue
            if not f.docstring and self._nlp_engine.enabled:
                summary = self._nlp_engine.generate_function_summary(f, mod.file_path.name)
                if summary:
                    # Note: Auto-generated summaries get a clear prefix
                    f = dataclasses.replace(f, docstring=f"**[AI Generated]** {summary}")
            filtered.functions.append(f)

        # Filter classes and optionally enhance docstrings
        filtered.classes = []
        for c in mod.classes:
            if not self._include_private and c.visibility != Visibility.PUBLIC:
                continue
            
            # Enhance class docstring
            if not c.docstring and self._nlp_engine.enabled:
                summary = self._nlp_engine.generate_class_summary(c, mod.file_path.name)
                if summary:
                    c = dataclasses.replace(c, docstring=f"**[AI Generated]** {summary}")
            
            # Enhance method docstrings
            enhanced_methods = []
            for m in c.methods:
                if not self._include_private and m.visibility != Visibility.PUBLIC:
                    continue
                if not m.docstring and self._nlp_engine.enabled:
                    # We can use generate_function_summary for methods as they share structure
                    m_as_func = FunctionInfo(
                        name=m.name, parameters=m.parameters, return_type=m.return_type,
                        decorators=m.decorators, visibility=m.visibility
                    )
                    summary = self._nlp_engine.generate_function_summary(m_as_func, mod.file_path.name)
                    if summary:
                        m = dataclasses.replace(m, docstring=f"**[AI Generated]** {summary}")
                enhanced_methods.append(m)
            
            if enhanced_methods != c.methods:
                c = dataclasses.replace(c, methods=enhanced_methods)
                
            filtered.classes.append(c)

        return filtered
