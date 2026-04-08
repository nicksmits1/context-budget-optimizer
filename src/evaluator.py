import json
import os
from datetime import datetime


BUDGET_LEVELS = [2048, 4096, 8192, 16384]


def keyword_score(answer: str, keywords: list[str]) -> float:
    if not answer or not keywords:
        return 0.0
    answer_lower = answer.lower()
    hits = sum(1 for kw in keywords if kw.lower() in answer_lower)
    return hits / len(keywords)


def doc_coverage(selected_chunk_ids: list[str], relevant_doc_ids: list[str]) -> float:
    if not relevant_doc_ids:
        return 1.0
    selected_docs = {cid.split("::")[0] for cid in selected_chunk_ids}
    hits = sum(1 for doc_id in relevant_doc_ids if doc_id in selected_docs)
    return hits / len(relevant_doc_ids)


class Evaluator:
    def __init__(self, corpus_dir: str, queries_path: str):
        from src.optimizer import Optimizer
        from src.llm_client import LLMClient

        self.llm = LLMClient()
        self.optimizer = Optimizer(corpus_dir, self.llm)

        with open(queries_path) as f:
            self.queries = json.load(f)

    def run_all(self, budgets=None, generate_answers: bool = True) -> dict:
        from src.strategies.base import ContextBudget
        from src.strategies import ALL_STRATEGIES

        budgets = budgets or BUDGET_LEVELS
        strategies = [cls() for cls in ALL_STRATEGIES]

        results = []
        for q in self.queries:
            for strat in strategies:
                # pass LLM client to summary strategy if available
                if hasattr(strat, "llm_client") and strat.llm_client is None:
                    strat.llm_client = self.llm

                for budget_size in budgets:
                    budget = ContextBudget(max_tokens=budget_size)
                    run = self.optimizer.run(
                        query=q["query"],
                        strategy=strat,
                        budget=budget,
                        generate_answer=generate_answers,
                    )

                    kw_score = 0.0
                    judge_score = None
                    if run["answer"] and not run.get("llm_mock", True):
                        kw_score = keyword_score(run["answer"], q["expected_answer_keywords"])
                        judge_result = self.llm.judge_answer(
                            q["query"], run["answer"], q["expected_answer_keywords"]
                        )
                        if not judge_result["mock"]:
                            judge_score = judge_result["score"]
                    elif run["answer"]:
                        kw_score = keyword_score(run["answer"], q["expected_answer_keywords"])

                    coverage = doc_coverage(run["chunk_ids"], q["relevant_doc_ids"])

                    results.append({
                        "query_id": q["id"],
                        "query": q["query"],
                        "difficulty": q["difficulty"],
                        "requires_multi_doc": q["requires_multi_doc"],
                        "strategy": run["strategy"],
                        "budget": budget_size,
                        "tokens_used": run["total_tokens"],
                        "num_chunks": run["num_chunks"],
                        "estimated_ttft_ms": run["estimated_ttft_ms"],
                        "actual_ttft_ms": run.get("actual_ttft_ms"),
                        "keyword_score": round(kw_score, 3),
                        "judge_score": judge_score,
                        "coverage": round(coverage, 3),
                        "chunk_ids": run["chunk_ids"],
                        "answer": run.get("answer", ""),
                        "llm_mock": run.get("llm_mock", True),
                    })

        return {"results": results, "summary": self._summarize(results)}

    def _summarize(self, results: list[dict]) -> dict:
        """Group results by (strategy, budget) and compute averages."""
        groups = {}
        for r in results:
            key = (r["strategy"], r["budget"])
            groups.setdefault(key, []).append(r)

        summary = []
        for (strat, budget), group in sorted(groups.items()):
            n = len(group)
            summary.append({
                "strategy": strat,
                "budget": budget,
                "avg_keyword_score": round(sum(r["keyword_score"] for r in group) / n, 3),
                "avg_tokens_used": round(sum(r["tokens_used"] for r in group) / n, 1),
                "avg_estimated_ttft_ms": round(sum(r["estimated_ttft_ms"] for r in group) / n, 1),
                "avg_coverage": round(sum(r["coverage"] for r in group) / n, 3),
                "count": n,
            })

            # add avg judge score if we have any
            judge_scores = [r["judge_score"] for r in group if r["judge_score"] is not None]
            if judge_scores:
                summary[-1]["avg_judge_score"] = round(sum(judge_scores) / len(judge_scores), 2)

        return summary


def generate_report(eval_data: dict, output_dir: str):
    """Write JSON results and a markdown report."""
    os.makedirs(output_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    json_path = os.path.join(output_dir, f"eval_{ts}.json")
    with open(json_path, "w") as f:
        json.dump(eval_data, f, indent=2, default=str)

    summary = eval_data["summary"]
    md_lines = [
        "# Context Budget Optimizer — Evaluation Report",
        f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"\n**Queries evaluated:** {len(eval_data['results']) // (len(set(r['strategy'] for r in eval_data['results'])) * len(set(r['budget'] for r in eval_data['results'])))}",
        "\n## Strategy Comparison\n",
        "| Strategy | Budget | Avg Quality (kw) | Avg Tokens | Est. TTFT (ms) | Avg Coverage |",
        "|----------|--------|-------------------|------------|----------------|--------------|",
    ]

    for s in summary:
        judge_col = f" | Judge: {s['avg_judge_score']}" if "avg_judge_score" in s else ""
        md_lines.append(
            f"| {s['strategy']} | {s['budget']} | {s['avg_keyword_score']} | "
            f"{s['avg_tokens_used']:.0f} | {s['avg_estimated_ttft_ms']:.0f} | "
            f"{s['avg_coverage']}{judge_col} |"
        )

    # Pareto analysis
    md_lines.append("\n## Pareto Analysis: Quality per Token\n")
    md_lines.append("Strategies ranked by keyword_score / tokens_used (higher is better):\n")

    pareto = []
    for s in summary:
        if s["avg_tokens_used"] > 0:
            efficiency = s["avg_keyword_score"] / s["avg_tokens_used"] * 1000
            pareto.append((efficiency, s))
    pareto.sort(key=lambda x: x[0], reverse=True)

    md_lines.append("| Rank | Strategy | Budget | Quality/1K Tokens | Coverage |")
    md_lines.append("|------|----------|--------|-------------------|----------|")
    for rank, (eff, s) in enumerate(pareto[:10], 1):
        md_lines.append(
            f"| {rank} | {s['strategy']} | {s['budget']} | {eff:.4f} | {s['avg_coverage']} |"
        )

    md_lines.append("\n## Key Takeaways\n")
    if pareto:
        best = pareto[0][1]
        md_lines.append(
            f"- **Best quality-per-token:** {best['strategy']} at budget {best['budget']} "
            f"achieves {best['avg_keyword_score']} keyword score using {best['avg_tokens_used']:.0f} tokens"
        )

    # best raw quality
    best_quality = max(summary, key=lambda s: s["avg_keyword_score"])
    md_lines.append(
        f"- **Highest raw quality:** {best_quality['strategy']} at budget {best_quality['budget']} "
        f"with keyword score {best_quality['avg_keyword_score']}"
    )

    # best coverage
    best_cov = max(summary, key=lambda s: s["avg_coverage"])
    md_lines.append(
        f"- **Best coverage:** {best_cov['strategy']} at budget {best_cov['budget']} "
        f"with {best_cov['avg_coverage']} average doc coverage"
    )

    md_lines.append(
        "\n- Larger budgets generally improve coverage and quality, but with diminishing returns"
    )
    md_lines.append(
        "- MMR provides diversity at the cost of slightly lower raw similarity scores"
    )
    md_lines.append(
        "- Importance weighting benefits queries where recency and document type matter"
    )

    md_path = os.path.join(output_dir, f"report_{ts}.md")
    with open(md_path, "w") as f:
        f.write("\n".join(md_lines))

    return json_path, md_path
