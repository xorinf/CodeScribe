"""
CodeScribe CLI - Command-Line Interface for the Documentation Engine.

This module provides the primary entry point for interacting with CodeScribe.
It exposes subcommands for generating documentation, analyzing codebases,
and initializing project configurations.

Usage:
    python -m src.cli generate --input ./my_project --output ./docs
    python -m src.cli analyze --input ./my_project
    python -m src.cli init
    python -m src.cli version
"""

import argparse
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

APP_NAME: str = "CodeScribe"
APP_VERSION: str = "0.1.0"
DEFAULT_CONFIG_FILENAME: str = "codescribe.json"
DEFAULT_OUTPUT_DIR: str = "./docs"
SUPPORTED_LANGUAGES: list[str] = ["python", "universal"]

# Default configuration values written by `codescribe init`
DEFAULT_CONFIG: dict = {
    "version": APP_VERSION,
    "input": ".",
    "output": DEFAULT_OUTPUT_DIR,
    "languages": SUPPORTED_LANGUAGES,
    "exclude": [
        "__pycache__",
        ".git",
        ".venv",
        "venv",
        "node_modules",
        "dist",
        "build",
    ],
    "verbose": False,
}

# ---------------------------------------------------------------------------
# Logger Setup
# ---------------------------------------------------------------------------


def _setup_logger(verbose: bool = False) -> logging.Logger:
    """Configure and return the application logger.

    Args:
        verbose: If True, sets the log level to DEBUG. Otherwise INFO.

    Returns:
        A configured logging.Logger instance.
    """
    logger = logging.getLogger(APP_NAME)
    if logger.handlers:
        return logger

    level = logging.DEBUG if verbose else logging.INFO
    logger.setLevel(level)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    formatter = logging.Formatter(
        fmt="[%(levelname)s] %(message)s",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


# ---------------------------------------------------------------------------
# Configuration Loader
# ---------------------------------------------------------------------------


def _load_config(config_path: Optional[Path] = None) -> dict:
    """Load project configuration from a codescribe.json file.

    Searches the current working directory for a config file unless
    an explicit path is provided. Returns default values if no config
    file is found.

    Args:
        config_path: Optional explicit path to the configuration file.

    Returns:
        A dictionary containing the merged configuration.
    """
    if config_path is None:
        config_path = Path.cwd() / DEFAULT_CONFIG_FILENAME

    if config_path.is_file():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                user_config = json.load(f)
            merged = {**DEFAULT_CONFIG, **user_config}
            return merged
        except (json.JSONDecodeError, OSError) as exc:
            print(f"[WARNING] Failed to read config at {config_path}: {exc}")

    return dict(DEFAULT_CONFIG)


# ---------------------------------------------------------------------------
# Path Validation
# ---------------------------------------------------------------------------


def _validate_input_path(input_path: str) -> Path:
    """Validate that the provided input path exists and is a directory.

    Args:
        input_path: The raw string path from user input.

    Returns:
        A resolved Path object pointing to the input directory.

    Raises:
        SystemExit: If the path does not exist or is not a directory.
    """
    path = Path(input_path).resolve()
    if not path.exists():
        print(f"[ERROR] Input path does not exist: {path}")
        sys.exit(1)
    if not path.is_dir():
        print(f"[ERROR] Input path is not a directory: {path}")
        sys.exit(1)
    return path


def _ensure_output_dir(output_path: str) -> Path:
    """Ensure the output directory exists, creating it if necessary.

    Args:
        output_path: The raw string path for the output directory.

    Returns:
        A resolved Path object pointing to the output directory.
    """
    path = Path(output_path).resolve()
    path.mkdir(parents=True, exist_ok=True)
    return path


# ---------------------------------------------------------------------------
# Subcommand Handlers
# ---------------------------------------------------------------------------


def _handle_generate(args: argparse.Namespace) -> None:
    """Handler for the 'generate' subcommand.

    Orchestrates the full documentation generation pipeline:
    parse -> analyze -> generate output.

    Args:
        args: Parsed command-line arguments.
    """
    config = _load_config()
    verbose = args.verbose or config.get("verbose", False)
    logger = _setup_logger(verbose)

    input_dir = _validate_input_path(args.input or config.get("input", "."))
    output_dir = _ensure_output_dir(args.output or config.get("output", DEFAULT_OUTPUT_DIR))
    file_format = args.format

    logger.info("Starting %s v%s", APP_NAME, APP_VERSION)
    logger.info("Input directory  : %s", input_dir)
    logger.info("Output directory : %s", output_dir)
    logger.info("Output format    : %s", file_format)
    logger.debug("Full configuration: %s", json.dumps(config, indent=2))

    # ------------------------------------------------------------------
    # Step 1: Parse source files
    # ------------------------------------------------------------------
    logger.info("Step 1/3 -- Parsing source files...")
    start = time.time()
    
    from src.parser.registry import ParserRegistry
    from src.parser.python_parser import PythonParser
    from src.parser.universal_parser import UniversalParser
    from src.parser.base import ParseResult

    registry = ParserRegistry()
    registry.register(PythonParser())
    registry.register(UniversalParser())

    parse_results = registry.parse_all(input_dir, exclude_dirs=config.get("exclude", []))

    # Combine results into a single ParseResult
    parse_result = ParseResult(language="multi")
    for pr in parse_results:
        parse_result.modules.extend(pr.modules)
        parse_result.errors.extend(pr.errors)

    elapsed = time.time() - start

    if not parse_result.modules:
        logger.warning("No supported source files found in %s", input_dir)
        logger.warning("Supported languages: %s", ", ".join(SUPPORTED_LANGUAGES))
        sys.exit(0)

    logger.info(
        "  Parsed %d module(s) in %.2fs",
        len(parse_result.modules),
        elapsed,
    )

    # ------------------------------------------------------------------
    # Step 2: Analyze code structure
    # ------------------------------------------------------------------
    logger.info("Step 2/3 -- Analyzing code structure...")
    start = time.time()
    
    from src.analyzer.analyzer import SemanticAnalyzer
    analyzer = SemanticAnalyzer(project_root=input_dir)
    analysis = analyzer.analyze(parse_result)
    
    logger.info(
        "  Analyzed %d classes and %d dependencies in %.2fs",
        len(analysis.inheritance_tree.nodes),
        len(analysis.dependency_graph.edges),
        time.time() - start,
    )

    # ------------------------------------------------------------------
    # Step 3: Generate documentation
    # ------------------------------------------------------------------
    logger.info("Step 3/3 -- Generating documentation...")
    start = time.time()
    
    from src.generator.generator import DocGenerator
    
    use_nlp = getattr(args, "use_nlp", False)
    api_key = getattr(args, "api_key", None)
    
    generator = DocGenerator(
        project_name=APP_NAME,
        include_private=config.get("include_private", False),
        use_nlp=use_nlp,
        api_key=api_key
    )
    
    files = generator.generate(
        parse_result, analysis, output_dir, single_file=False
    )
    
    logger.info(
        "  Generated %d file(s) in %.2fs",
        len(files),
        time.time() - start,
    )

    logger.info("Pipeline complete. Output target: %s", output_dir)


def _handle_analyze(args: argparse.Namespace) -> None:
    """Handler for the 'analyze' subcommand.

    Runs only the parsing and analysis steps without generating output.
    Useful for inspecting what CodeScribe detects in a codebase.

    Args:
        args: Parsed command-line arguments.
    """
    config = _load_config()
    verbose = args.verbose or config.get("verbose", False)
    logger = _setup_logger(verbose)

    input_dir = _validate_input_path(args.input or config.get("input", "."))

    logger.info("Analyzing codebase at: %s", input_dir)

    source_files = _collect_source_files(input_dir, config.get("exclude", []))

    if not source_files:
        logger.warning("No supported source files found in %s", input_dir)
        sys.exit(0)

    logger.info("Detected %d source file(s):", len(source_files))
    for f in source_files:
        rel = f.relative_to(input_dir)
        size = f.stat().st_size
        logger.info("  %-40s  %d bytes", str(rel), size)

    # TODO: Wire into src.parser and src.analyzer once implemented.
    logger.info("Deep analysis pending implementation (Phase 2).")


def _handle_scrape(args: argparse.Namespace) -> None:
    """Handler for the 'scrape' subcommand."""
    config = _load_config()
    verbose = args.verbose or config.get("verbose", False)
    logger = _setup_logger(verbose)

    # Resolve output directory
    output_dir = Path(args.output_dir).resolve()
    
    tokens = []
    if args.tokens:
        tokens = [t.strip() for t in args.tokens.split(",")]

    logger.info("Starting Data Scraping Engine...")
    logger.info("Platform: %s", args.platform)
    logger.info("Language: %s", args.language)
    logger.info("Output Directory: %s", output_dir)

    # Build the query
    query_parts = []
    if args.language:
        query_parts.append(f"language:{args.language}")
    query_parts.append(f"stars:>={args.min_stars}")
    query = " ".join(query_parts)

    from src.scraper.engine import AsyncScraperEngine
    import asyncio
    
    engine = AsyncScraperEngine(tokens=tokens)
    
    try:
        asyncio.run(
            engine.ingest_repositories(
                platform=args.platform,
                query=query,
                output_dir=output_dir,
                limit=args.limit,
                download_source=not args.no_download
            )
        )
    except KeyboardInterrupt:
        logger.warning("Scraping interrupted by user.")
    except Exception as e:
        logger.error("Scraping failed: %s", e)


def _handle_cleanse(args: argparse.Namespace) -> None:
    """Handler for the 'cleanse' subcommand."""
    config = _load_config()
    verbose = args.verbose or config.get("verbose", False)
    logger = _setup_logger(verbose)

    input_dir = Path(args.input_dir).resolve()
    output_file = Path(args.output_file).resolve()
    
    languages = [lang.strip() for lang in args.languages.split(",")]

    logger.info("Starting Data Cleansing Engine...")
    logger.info("Input Directory: %s", input_dir)
    logger.info("Output File: %s", output_file)
    logger.info("Allowed Languages: %s", languages)

    from src.cleanser.pipeline import CleanserPipeline
    
    pipeline = CleanserPipeline(languages=languages)
    try:
        pipeline.process_directory(input_dir, output_file)
    except KeyboardInterrupt:
        logger.warning("Cleansing interrupted by user.")
    except Exception as e:
        logger.error("Cleansing failed: %s", e)


def _handle_tokenize(args: argparse.Namespace) -> None:
    """Handler for the 'tokenize' subcommand."""
    config = _load_config()
    verbose = args.verbose or config.get("verbose", False)
    logger = _setup_logger(verbose)

    dataset_path = Path(args.dataset).resolve()
    output_path = Path(args.output).resolve()
    
    logger.info("Starting Custom Tokenizer Training...")
    logger.info("Dataset: %s", dataset_path)
    logger.info("Vocab Size: %d", args.vocab_size)
    logger.info("Output Tokenizer: %s", output_path)

    from src.tokenizer.trainer import CodeTokenizerTrainer
    
    trainer = CodeTokenizerTrainer(vocab_size=args.vocab_size)
    try:
        trainer.train(dataset_path=dataset_path, output_path=output_path)
    except KeyboardInterrupt:
        logger.warning("Training interrupted by user.")
    except Exception as e:
        logger.error("Training failed: %s", e)


def _handle_init(args: argparse.Namespace) -> None:
    """Handler for the 'init' subcommand.

    Creates a default codescribe.json configuration file in the
    current working directory.

    Args:
        args: Parsed command-line arguments.
    """
    logger = _setup_logger(args.verbose)
    config_path = Path.cwd() / DEFAULT_CONFIG_FILENAME

    if config_path.exists() and not args.force:
        logger.warning(
            "Configuration file already exists: %s", config_path
        )
        logger.warning("Use --force to overwrite.")
        sys.exit(1)

    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(DEFAULT_CONFIG, f, indent=2)
        f.write("\n")

    logger.info("Created configuration file: %s", config_path)
    logger.info("Edit this file to customize CodeScribe for your project.")


def _handle_version(args: argparse.Namespace) -> None:
    """Handler for the 'version' subcommand.

    Prints the application name and version, then exits.

    Args:
        args: Parsed command-line arguments.
    """
    print(f"{APP_NAME} v{APP_VERSION}")


# ---------------------------------------------------------------------------
# File Collection Utility
# ---------------------------------------------------------------------------

# Map of supported language names to their file extensions.
_LANGUAGE_EXTENSIONS: dict[str, list[str]] = {
    "python": [".py"],
    "universal": [
        ".js", ".ts", ".go", ".rs", ".java",
        ".cpp", ".c", ".cs", ".rb", ".php",
        ".swift", ".kt", ".scala"
    ],
}


def _collect_source_files(
    root: Path,
    exclude_dirs: list[str],
) -> list[Path]:
    """Walk the directory tree and collect supported source files.

    Args:
        root: The root directory to search.
        exclude_dirs: Directory names to skip during traversal.

    Returns:
        A sorted list of Path objects pointing to source files.
    """
    valid_extensions: set[str] = set()
    for lang in SUPPORTED_LANGUAGES:
        valid_extensions.update(_LANGUAGE_EXTENSIONS.get(lang, []))

    collected: list[Path] = []

    for dirpath, dirnames, filenames in os.walk(root):
        # Prune excluded directories in-place so os.walk skips them.
        dirnames[:] = [
            d for d in dirnames if d not in exclude_dirs
        ]
        for fname in filenames:
            if Path(fname).suffix in valid_extensions:
                collected.append(Path(dirpath) / fname)

    return sorted(collected)


# ---------------------------------------------------------------------------
# Argument Parser Construction
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    """Construct and return the top-level argument parser with subcommands.

    Returns:
        A fully configured argparse.ArgumentParser.
    """
    parser = argparse.ArgumentParser(
        prog="codescribe",
        description=(
            f"{APP_NAME} v{APP_VERSION} -- "
            "AI-Enhanced Documentation Generator. "
            "Analyzes source code and generates comprehensive, "
            "human-readable documentation automatically."
        ),
    )
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"{APP_NAME} v{APP_VERSION}",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        title="commands",
        description="Available subcommands",
    )

    # -- generate --------------------------------------------------------
    gen_parser = subparsers.add_parser(
        "generate",
        aliases=["gen"],
        help="Generate documentation from a codebase.",
    )
    gen_parser.add_argument(
        "--input", "-i",
        type=str,
        default=None,
        help="Path to the source code directory (default: current directory).",
    )
    gen_parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help=f"Path to the output documentation directory (default: {DEFAULT_OUTPUT_DIR}).",
    )
    gen_parser.add_argument(
        "--format", "-f",
        type=str,
        choices=["markdown", "html"],
        default="markdown",
        help="Output format for generated documentation (default: markdown).",
    )
    gen_parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose (debug) output.",
    )
    gen_parser.add_argument(
        "--use-nlp",
        action="store_true",
        help="Enable AI-powered documentation generation for missing docstrings.",
    )
    gen_parser.add_argument(
        "--api-key",
        type=str,
        default=None,
        help="Optional API key for the AI model (or set CODESCRIBE_API_KEY env var).",
    )
    gen_parser.set_defaults(func=_handle_generate)

    # -- analyze ---------------------------------------------------------
    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Analyze a codebase without generating documentation.",
    )
    analyze_parser.add_argument(
        "--input", "-i",
        type=str,
        default=None,
        help="Path to the source code directory (default: current directory).",
    )
    analyze_parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose (debug) output.",
    )
    analyze_parser.set_defaults(func=_handle_analyze)

    # -- scrape ----------------------------------------------------------
    scrape_parser = subparsers.add_parser(
        "scrape",
        help="Asynchronously scrape open-source repositories.",
    )
    scrape_parser.add_argument(
        "--platform",
        type=str,
        choices=["github", "gitlab"],
        default="github",
        help="Platform to scrape from (default: github)."
    )
    scrape_parser.add_argument(
        "--language",
        type=str,
        default="python",
        help="Filter by language (default: python)."
    )
    scrape_parser.add_argument(
        "--min-stars",
        type=int,
        default=100,
        help="Minimum stars for repositories (default: 100)."
    )
    scrape_parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Maximum number of repositories to ingest (default: 10)."
    )
    scrape_parser.add_argument(
        "--output-dir",
        type=str,
        default="./scraped_data",
        help="Directory to save scraped data and zipballs (default: ./scraped_data)."
    )
    scrape_parser.add_argument(
        "--tokens",
        type=str,
        default=None,
        help="Comma-separated API tokens for rate limit rotation."
    )
    scrape_parser.add_argument(
        "--no-download",
        action="store_true",
        help="Only fetch metadata, do not download source code zipballs."
    )
    scrape_parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose (debug) output."
    )
    scrape_parser.set_defaults(func=_handle_scrape)

    # -- cleanse ---------------------------------------------------------
    cleanse_parser = subparsers.add_parser(
        "cleanse",
        help="Cleanse scraped data from zipballs.",
    )
    cleanse_parser.add_argument(
        "--input-dir",
        type=str,
        default="./scraped_data",
        help="Directory containing scraped zip files (default: ./scraped_data)."
    )
    cleanse_parser.add_argument(
        "--output-file",
        type=str,
        default="./dataset.jsonl",
        help="Output JSONL file path (default: ./dataset.jsonl)."
    )
    cleanse_parser.add_argument(
        "--languages",
        type=str,
        default=".py",
        help="Comma-separated file extensions to process (default: .py)."
    )
    cleanse_parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose (debug) output."
    )
    cleanse_parser.set_defaults(func=_handle_cleanse)

    # -- tokenize --------------------------------------------------------
    tokenize_parser = subparsers.add_parser(
        "tokenize",
        help="Train a Byte-Level BPE tokenizer on a JSONL dataset.",
    )
    tokenize_parser.add_argument(
        "--dataset",
        type=str,
        required=True,
        help="Path to the cleansed JSONL dataset."
    )
    tokenize_parser.add_argument(
        "--vocab-size",
        type=int,
        default=50000,
        help="Target vocabulary size (default: 50000)."
    )
    tokenize_parser.add_argument(
        "--output",
        type=str,
        default="./tokenizer.json",
        help="Path to save the trained tokenizer (default: ./tokenizer.json)."
    )
    tokenize_parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose (debug) output."
    )
    tokenize_parser.set_defaults(func=_handle_tokenize)

    # -- init ------------------------------------------------------------
    init_parser = subparsers.add_parser(
        "init",
        help="Initialize a codescribe.json configuration file.",
    )
    init_parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite an existing configuration file.",
    )
    init_parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose (debug) output.",
    )
    init_parser.set_defaults(func=_handle_init)

    # -- version ---------------------------------------------------------
    version_parser = subparsers.add_parser(
        "version",
        help="Display the current CodeScribe version.",
    )
    version_parser.set_defaults(func=_handle_version)

    return parser


# ---------------------------------------------------------------------------
# Main Entry Point
# ---------------------------------------------------------------------------


def main() -> None:
    """Parse arguments and dispatch to the appropriate subcommand handler."""
    parser = _build_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    args.func(args)


if __name__ == "__main__":
    main()
