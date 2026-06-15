# Goal
Complete the project to support generating docs for **any** language using the UniversalParser.

The memory states:
- "The codebase's parsing architecture uses a `ParserRegistry` (`src/parser/registry.py`) to map file extensions to language-specific parsers. A `UniversalParser` (`src/parser/universal_parser.py`) acts as a fallback to extract basic class and function structures from non-Python languages using regex, handling both keyword-based (e.g., def, func, fn) and C-family return-type-based declarations."
- "The `SemanticAnalyzer` expects a single `ParseResult`. When using multiple parsers in `src/cli.py`, their individual results must be combined into a single `ParseResult` object before analysis."
- "Adding support for new languages requires updating the `SUPPORTED_LANGUAGES` list and `_LANGUAGE_EXTENSIONS` dictionary in `src/cli.py` to ensure the `ParserRegistry` properly routes files."
- "Although the project roadmap mentions a pivot towards building a custom CodeScribe LLM, the user explicitly directed that the primary, overriding goal of the project is to generate documentation for any programming language."

# Plan

1. **Implement `UniversalParser`:**
   - Create `src/parser/universal_parser.py` subclassing `BaseParser`.
   - Implement `language()` returning "universal".
   - Implement `supported_extensions()` to return a broad list of extensions for common languages (js, ts, java, go, rb, rs, c, cpp, etc.).
   - Implement `parse_file(self, file_path)` using regex to extract classes and functions (keyword-based `(def|function|func|fn)` and C-style return-type-based).

2. **Update `src/cli.py`:**
   - Add new supported languages to `SUPPORTED_LANGUAGES`.
   - Add extensions to `_LANGUAGE_EXTENSIONS`.
   - Update `_handle_generate` to use `ParserRegistry` to parse multiple languages.
   - Aggregate all `ParseResult` from `ParserRegistry.parse_all` into a single `ParseResult` before calling `SemanticAnalyzer.analyze`.
   - Add `UniversalParser` to `ParserRegistry`.

3. **Verify:**
   - Test against multiple languages (js, c, ts, rb, rs) to ensure functions and classes are extracted.
   - Test end-to-end `python -m src.cli generate` command.

4. **Pre commit:**
   - Complete pre commit steps.

5. **Submit.**
