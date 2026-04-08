import numpy as np
from src.strategies.base import ContextStrategy, ContextBudget, SelectedContext
from src.types import ScoredChunk


class MMRStrategy(ContextStrategy):
    name = "mmr"

    def __init__(self, lambda_param: float = 0.7):
        self.lambda_param = lambda_param

    def select(
        self, query: str, candidates: list[ScoredChunk], budget: ContextBudget
    ) -> SelectedContext:
        if not candidates:
            return SelectedContext(chunks=[], total_tokens=0, strategy_name=self.name)

        remaining = list(candidates)
        selected: list[ScoredChunk] = []
        total = 0

        while remaining:
            best_score = -float("inf")
            best_idx = 0

            for i, cand in enumerate(remaining):
                if total + cand.chunk.token_count > budget.max_tokens:
                    continue

                relevance = cand.score

                redundancy = 0.0
                if selected:
                    sel_embs = np.stack([s.embedding for s in selected])
                    with np.errstate(all="ignore"):
                        sims = np.nan_to_num(sel_embs @ cand.embedding, nan=0.0)
                    redundancy = float(np.max(sims))

                mmr = self.lambda_param * relevance - (1 - self.lambda_param) * redundancy

                if mmr > best_score:
                    best_score = mmr
                    best_idx = i

            # nothing fits budget anymore
            if best_score == -float("inf"):
                break

            pick = remaining.pop(best_idx)
            selected.append(pick)
            total += pick.chunk.token_count

            if total >= budget.target_tokens:
                break

        return SelectedContext(
            chunks=selected,
            total_tokens=total,
            strategy_name=self.name,
            metadata={"lambda": self.lambda_param},
        )
