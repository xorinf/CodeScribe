# CodeScribe

CodeScribe is a documentation generation tool that analyzes Python code and automatically writes Markdown docs. It uses Google Gemini to generate missing docstrings.

## Features
- Parses Python AST to find classes and functions.
- Generates dependency graphs and inheritance trees.
- Outputs clean Markdown documentation.
- Uses LLM APIs to write missing docstrings automatically.

## Usage
```bash
# Set your API key
export GEMINI_API_KEY="your-api-key"

# Generate docs for your project
python -m src.cli generate --use-nlp -i ./src -o ./docs
```

## Roadmap

We are currently shifting focus toward building our own custom LLM tailored for codebase comprehension.

- **Phase 1-3:** Core CLI, AST Parsing, and Markdown Generation (Completed)
- **Phase 4:** Data Engineering & Pipeline
- **Phase 5:** Custom LLM Architecture
- **Phase 6:** Pretraining & RLHF
- **Phase 7:** Local Inference & Quantization
- **Phase 8:** Autonomous Agent Capabilities

*See `roadmap.md` for full details.*
