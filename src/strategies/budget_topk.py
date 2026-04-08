from src.strategies.base import ContextStrategy, ContextBudget, SelectedContext
from src.types import ScoredChunk


class BudgetTopKStrategy(ContextStrategy):
    name = "budget_topk"

    def select(
        self, query: str, candidates: list[ScoredChunk], budget: ContextBudget
    ) -> SelectedContext:
        sorted_cands = sorted(candidates, key=lambda c: c.score, reverse=True)
        selected = []
        total = 0

        # first pass: greedily pick high-scoring chunks that fit
        skipped = []
        for sc in sorted_cands:
            if total + sc.chunk.token_count <= budget.target_tokens:
                selected.append(sc)
                total += sc.chunk.token_count
            else:
                skipped.append(sc)

        # second pass: try to pack remaining budget with smaller skipped chunks
        remaining = budget.max_tokens - total
        for sc in sorted(skipped, key=lambda c: c.chunk.token_count):
            if sc.chunk.token_count <= remaining:
                selected.append(sc)
                total += sc.chunk.token_count
                remaining -= sc.chunk.token_count

        # re-sort by score for consistent output ordering
        selected.sort(key=lambda c: c.score, reverse=True)

        return SelectedContext(
            chunks=selected,
            total_tokens=total,
            strategy_name=self.name,
            metadata={"packing_used": len(skipped) > 0},
        )
