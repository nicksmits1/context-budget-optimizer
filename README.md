# Context Budget Optimizer

A Python tool that intelligently selects, compresses, and prioritizes document chunks for LLM context windows. Given a user query and a corpus of enterprise documents, it applies multiple context selection strategies to minimize Time to First Token (TTFT) while maximizing answer quality. Then, the tool benchmarks them against each other with a built-in eval harness. Enterprise context management systems face tradeoffs examined in this project. Namely, efficiently serving the right context to agentic AI tools, with enterprise-grade awareness of metadata, permissions, and source diversity is difficult and can be tackled with different context strategies.

## Architecture

```
context-budget-optimizer/
├── data/
│   ├── corpus/                  # 28 synthetic enterprise documents (markdown + YAML frontmatter)
│   └── eval_queries.json        # 14 eval queries with ground truth
├── src/
│   ├── chunker.py               # Header/paragraph-aware document chunking
│   ├── embedder.py              # sentence-transformers wrapper (all-MiniLM-L6-v2)
│   ├── retriever.py             # Cosine similarity retrieval over numpy vectors
│   ├── token_counter.py         # tiktoken counting + TTFT estimation heuristic
│   ├── llm_client.py            # Qwen 2.5 via HuggingFace Inference API (graceful mock fallback)
│   ├── optimizer.py             # Main pipeline: query, retrieve, strategy, answer
│   ├── evaluator.py             # Eval harness: benchmarks all strategies × budgets
│   ├── types.py                 # Shared data types (ScoredChunk)
│   └── strategies/
│       ├── base.py              # Abstract ContextStrategy interface
│       ├── topk.py              # Naive top-k by similarity (baseline)
│       ├── budget_topk.py       # Budget-aware top-k with bin-packing
│       ├── mmr.py               # Maximal Marginal Relevance (diversity)
│       ├── importance.py        # Metadata-weighted scoring (recency, type, sensitivity)
│       └── summary.py           # Compress low-priority chunks via LLM summarization
├── eval/
│   ├── run_eval.py              # Full evaluation suite runner
│   └── results/                 # Auto-generated JSON + markdown reports
├── tests/
│   └── test_strategies.py       # Unit tests for all components
├── demo.py                      # Interactive CLI demo
├── requirements.txt
└── pyproject.toml
```

## Setup

```bash
# Clone and install
cd context-budget-optimizer
pip install -r requirements.txt

# Add your HuggingFace token to a .env file for LLM-powered answers
.env
HF_TOKEN=your_token_here
```

Everything works without an API key. The HF token enables Qwen-powered answer generation and LLM-as-judge scoring.

## Usage

### Interactive Demo

```bash
python demo.py
```

Type a query, pick a token budget (2048 / 4096 / 8192 / 16384), and see how each strategy selects chunks. With an HF token set, you'll also see generated answers and wall-clock timing.

### Run Evaluations

```bash
python eval/run_eval.py
```

Runs all 5 strategies × 4 budget levels × 14 queries = 280 evaluations. Outputs:
- A summary table to stdout
- JSON results in `eval/results/`
- A markdown report with strategy comparison and Pareto analysis


## Strategies

Each strategy implements a simple interface — `select(query, candidates, budget) → SelectedContext` — making it trivial to add new ones.

### Top-K (baseline)
Sort chunks by cosine similarity, take from the top until the budget is full. Simple, fast, no awareness of redundancy or metadata. This is what most naive RAG implementations do.

### Budget-Aware Top-K
Same ranking as top-k, but with a two-pass approach: first greedily fill to a soft target (70% of budget), then bin-pack smaller chunks into remaining space. Ensures the hard token ceiling is never exceeded while maximizing budget utilization.

### Maximal Marginal Relevance (MMR)
Iteratively selects chunks that balance relevance to the query with diversity from already-selected chunks:

```
MMR(chunk) = λ · sim(chunk, query) − (1−λ) · max(sim(chunk, selected))
```

Prevents the context window from being filled with near-duplicate information — critical when multiple documents cover similar topics.

### Importance-Weighted
Scores chunks using a weighted combination of:
- **Similarity** (0.50) — how relevant to the query
- **Recency** (0.20) — newer documents score higher (exponential decay)
- **Source type** (0.15) — reports > technical docs > meeting notes
- **Sensitivity penalty** (0.15) — deprioritize confidential docs when budget is tight

This is the most "enterprise-aware" strategy. It demonstrates that context management isn't just about vector similarity — metadata signals matter.

### Summary (Compression)
Keeps the top-5 chunks in full, then compresses remaining chunks into a summary using an LLM call. Falls back to extractive truncation if no API key is available. Tracks compression ratio in metadata. Highest quality-per-token potential, but adds latency from the summarization call.

