from src.strategies.base import ContextStrategy, ContextBudget, SelectedContext
from src.types import ScoredChunk


class TopKStrategy(ContextStrategy):
    name = "topk"

    def select(
        self, query: str, candidates: list[ScoredChunk], budget: ContextBudget
    ) -> SelectedContext:
        sorted_cands = sorted(candidates, key=lambda c: c.score, reverse=True)
        selected = []
        total = 0
        for sc in sorted_cands:
            total += sc.chunk.token_count
            if total > budget.max_tokens:
                break
            selected.append(sc)
        return SelectedContext(
            chunks=selected,
            total_tokens=sum(c.chunk.token_count for c in selected),
            strategy_name=self.name,
        )
