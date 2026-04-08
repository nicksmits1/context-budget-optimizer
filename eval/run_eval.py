#!/usr/bin/env python3
"""Run the full evaluation suite."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from rich.console import Console
from rich.table import Table
from src.evaluator import Evaluator, generate_report

console = Console()

CORPUS_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "corpus")
QUERIES_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "eval_queries.json")
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")


def main():
    console.print("\n[bold]Context Budget Optimizer — Evaluation Suite[/bold]\n")

    console.print("Loading corpus and building index...")
    evaluator = Evaluator(CORPUS_DIR, QUERIES_PATH)

    llm_status = "active (Qwen via HuggingFace)" if evaluator.llm.available else "mock mode (no HF_TOKEN)"
    console.print(f"LLM status: {llm_status}")
    console.print(f"Corpus: {len(evaluator.optimizer.chunks)} chunks from {len(set(c.doc_id for c in evaluator.optimizer.chunks))} documents")
    console.print(f"Eval queries: {len(evaluator.queries)}\n")

    console.print("Running evaluations (this may take a few minutes)...\n")
    eval_data = evaluator.run_all(generate_answers=evaluator.llm.available)

    # print summary table
    table = Table(title="Strategy Comparison")
    table.add_column("Strategy", style="cyan")
    table.add_column("Budget", justify="right")
    table.add_column("Avg Quality", justify="right", style="green")
    table.add_column("Avg Tokens", justify="right")
    table.add_column("Est. TTFT", justify="right")
    table.add_column("Coverage", justify="right", style="yellow")

    for s in eval_data["summary"]:
        table.add_row(
            s["strategy"],
            str(s["budget"]),
            f"{s['avg_keyword_score']:.3f}",
            f"{s['avg_tokens_used']:.0f}",
            f"{s['avg_estimated_ttft_ms']:.0f}ms",
            f"{s['avg_coverage']:.3f}",
        )

    console.print(table)

    # save results
    json_path, md_path = generate_report(eval_data, RESULTS_DIR)
    console.print(f"\n[green]Results saved:[/green]")
    console.print(f"  JSON: {json_path}")
    console.print(f"  Report: {md_path}\n")


if __name__ == "__main__":
    main()
