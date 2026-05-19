# CodeScribe Epic Roadmap: The Custom AI Era

## Phase 1: Foundation (Completed)
- [x] Set up zero-dependency project structure
- [x] Implement robust CLI architecture (`src/cli.py`)
- [x] Define parsing interfaces & registry (`src/parser`)

## Phase 2: Core Analysis (Completed)
- [x] Implement deep AST parsing for Python codebase extraction
- [x] Develop semantic analyzer (dependency graphs, inheritance trees)

## Phase 3: Initial Documentation Engine (Completed)
- [x] Create markdown template engine for structured docs
- [x] Auto-generate documentation to `docs/`
- [x] Integrate baseline NLP via external LLM APIs (Google Gemini)

---

## THE PIVOT: Building the CodeScribe Custom LLM

## Phase 4: Extreme Data Engineering & Pipeline
- [ ] **Data Scraping Engine:** Build an asynchronous scraper to ingest millions of high-quality open-source repositories from GitHub/GitLab.
- [ ] **Data Cleansing:** Implement heuristic filters to remove low-quality code, boilerplate, and sensitive secrets (PII).
- [ ] **Custom Tokenizer:** Train a highly optimized Byte-Pair Encoding (BPE) tokenizer specifically designed for programming languages, preserving whitespace and syntax semantics.
- [ ] **Vector Database:** Set up a massive local vector store (e.g., Milvus or Qdrant) to handle billions of code embeddings.

## Phase 5: Custom LLM Architecture Design
- [ ] **Model Architecture:** Design a specialized Decoder-only Transformer model optimized for code understanding (e.g., Rotary Position Embeddings, Flash Attention 2).
- [ ] **Context Window Expansion:** Implement techniques (like Ring Attention or ALiBi) to support massive 100k+ token context windows for full-repository comprehension.
- [ ] **Multi-Modal Syntax:** Embed not just raw text, but AST graph structures directly into the model's understanding.

## Phase 6: Pretraining & RLHF (The Heavy Compute)
- [ ] **Distributed Training:** Set up a PyTorch/DeepSpeed distributed training pipeline for a multi-GPU cluster.
- [ ] **Pretraining:** Train the base model on 1 Trillion+ tokens of code and documentation pairs.
- [ ] **Instruction Tuning:** Fine-tune the model specifically for the "Documentation Generation" and "Code Explanation" tasks.
- [ ] **RLHF (Reinforcement Learning from Human Feedback):** Create a feedback loop where developers rate the quality of the generated documentation to align the model's outputs perfectly with human expectations.

## Phase 7: Local Inference & Quantization
- [ ] **Model Compression:** Apply aggressive quantization (4-bit / 8-bit GGUF/AWQ) to shrink the model so it can run entirely locally on a MacBook M-Series chip.
- [ ] **Custom Inference Engine:** Build a high-performance C++/Rust inference backend (or integrate `llama.cpp`) directly into the CodeScribe CLI.
- [ ] **Zero-Latency Docs:** Replace the external Gemini API in `src/generator/nlp.py` with our local, blazing-fast custom LLM.

## Phase 8: Autonomous Agent Capabilities (God Mode)
- [ ] **Self-Healing Codebase:** Allow the LLM to autonomously detect bugs, write tests, and submit PRs to fix them.
- [ ] **Architectural Refactoring:** The AI suggests and automatically implements massive architectural changes across hundreds of files.
- [ ] **CodeScribe V2:** The AI becomes completely self-aware of its own codebase and writes the next version of itself.
