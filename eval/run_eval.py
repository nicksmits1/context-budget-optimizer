#!/usr/bin/env python3
"""Run the full evaluation suite.

Usage:
    python eval/run_eval.py           # full eval (280 combos, needs generous API quota)
    python eval/run_eval.py --quick   # quick eval (2 budgets, no judge calls — ~70 LLM calls)
"""

import argparse
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
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", action="store_true",
                        help="Run a smaller eval (2 budgets, no judge) for free-tier API limits")
    args = parser.parse_args()

    console.print("\n[bold]Context Budget Optimizer — Evaluation Suite[/bold]\n")

    if args.quick:
        console.print("[dim]Quick mode: 2 budgets, no LLM-as-judge[/dim]\n")

    console.print("Loading corpus and building index...")
    evaluator = Evaluator(CORPUS_DIR, QUERIES_PATH)

    # probe the LLM provider
    if evaluator.llm.available:
        console.print("Testing LLM connection...")
        test = evaluator.llm.generate("Say OK", max_tokens=4)
        if test["mock"]:
            console.print("[yellow]LLM provider failed — falling back to mock mode[/yellow]")
        else:
            console.print(f"[green]LLM active[/green] — using {test['model']}")
    else:
        console.print("[yellow]LLM in mock mode[/yellow] — set HF_TOKEN in .env for real answers")

    n_docs = len(set(c.doc_id for c in evaluator.optimizer.chunks))
    console.print(f"Corpus: {len(evaluator.optimizer.chunks)} chunks from {n_docs} documents")
    console.print(f"Eval queries: {len(evaluator.queries)}\n")

    budgets = [1024, 2048] if args.quick else None
    use_judge = not args.quick

    n_combos = len(budgets or [1024, 2048, 4096]) * 5 * len(evaluator.queries)
    console.print(f"Running {n_combos} evaluations (this may take a few minutes)...\n")

    eval_data = evaluator.run_all(
        budgets=budgets,
        generate_answers=evaluator.llm.available,
        use_judge=use_judge,
    )

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
