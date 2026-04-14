#!/usr/bin/env python3
"""Interactive CLI demo for the Context Budget Optimizer."""

import os
import sys

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt

from src.optimizer import Optimizer
from src.strategies.base import ContextBudget
from src.strategies import ALL_STRATEGIES
from src.llm_client import LLMClient
from src.token_counter import estimate_ttft

console = Console()

CORPUS_DIR = os.path.join(os.path.dirname(__file__), "data", "corpus")


def show_strategy_results(optimizer: Optimizer, query: str, budget_size: int):
    strategies = [cls() for cls in ALL_STRATEGIES]
    budget = ContextBudget(max_tokens=budget_size)

    # pass llm client to summary strategy
    for s in strategies:
        if hasattr(s, "llm_client") and s.llm_client is None:
            s.llm_client = optimizer.llm

    results = []
    for strat in strategies:
        console.print(f"  Running [cyan]{strat.name}[/cyan]...", end="")
        r = optimizer.run(query, strat, budget, generate_answer=optimizer.llm.available)
        results.append(r)
        console.print(f" {r['num_chunks']} chunks, {r['total_tokens']} tokens")

    # chunk selection table
    table = Table(title=f"Chunk Selection (budget: {budget_size} tokens)")
    table.add_column("Strategy", style="cyan")
    table.add_column("Chunks", justify="right")
    table.add_column("Tokens Used", justify="right")
    table.add_column("Est. TTFT", justify="right")
    table.add_column("Top Chunk IDs")

    for r in results:
        chunk_preview = ", ".join(r["chunk_ids"][:3])
        if len(r["chunk_ids"]) > 3:
            chunk_preview += f" (+{len(r['chunk_ids']) - 3} more)"
        table.add_row(
            r["strategy"],
            str(r["num_chunks"]),
            str(r["total_tokens"]),
            f"{r['estimated_ttft_ms']:.0f}ms",
            chunk_preview,
        )

    console.print()
    console.print(table)

    # answers if available
    if any(r.get("answer") and not r.get("llm_mock") for r in results):
        console.print()
        for r in results:
            if r.get("answer") and not r.get("llm_mock"):
                console.print(Panel(
                    r["answer"],
                    title=f"[cyan]{r['strategy']}[/cyan] — {r['actual_ttft_ms']:.0f}ms",
                    border_style="dim",
                ))
    elif results:
        console.print(
            "\n[dim]Set HF_TOKEN in .env to see generated answers from Qwen.[/dim]"
        )


def main():
    console.print(Panel(
        "[bold]Context Budget Optimizer[/bold]\n"
        "Interactive demo — compare context selection strategies side by side.\n"
        "Type a query, pick a budget, and see how each strategy performs.",
        border_style="blue",
    ))

    console.print("Loading corpus and building embeddings (first run may take a moment)...")
    llm = LLMClient()
    optimizer = Optimizer(CORPUS_DIR, llm)

    n_docs = len(set(c.doc_id for c in optimizer.chunks))
    console.print(f"Loaded {len(optimizer.chunks)} chunks from {n_docs} documents.")

    if llm.available:
        console.print("Testing LLM connection...")
        test = llm.generate("Say OK", max_tokens=4)
        if test["mock"]:
            console.print("[yellow]LLM provider failed — running in mock mode[/yellow]\n")
        else:
            console.print(f"[green]LLM active[/green] — using {test['model']}\n")
    else:
        console.print("[yellow]LLM in mock mode[/yellow] — set HF_TOKEN in .env for real answers\n")

    while True:
        query = Prompt.ask("\n[bold]Enter a query[/bold] (or 'quit')")
        if query.lower() in ("quit", "exit", "q"):
            break

        budget_size = IntPrompt.ask(
            "Token budget", default=2048,
            choices=["1024", "2048", "4096"],
        )

        show_strategy_results(optimizer, query, budget_size)

    console.print("\nDone.")


if __name__ == "__main__":
    main()
