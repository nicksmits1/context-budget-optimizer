from datetime import datetime, timezone
from src.strategies.base import ContextStrategy, ContextBudget, SelectedContext
from src.types import ScoredChunk

DOC_TYPE_SCORES = {
    "report": 1.0,
    "technical": 0.9,
    "requirements": 0.85,
    "roadmap": 0.8,
    "case_study": 0.75,
    "playbook": 0.7,
    "guide": 0.65,
    "runbook": 0.65,
    "policy": 0.6,
    "postmortem": 0.6,
    "legal": 0.55,
    "plan": 0.5,
    "meeting_notes": 0.4,
}

SENSITIVITY_PENALTY = {
    "public": 0.0,
    "internal": 0.1,
    "confidential": 0.3,
    "restricted": 0.5,
}


def _recency_score(created) -> float:
    if not created:
        return 0.0
    try:
        doc_date = datetime.strptime(created, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        days_old = (now - doc_date).days
        # simple decay: score 1.0 for today, ~0.5 at 180 days, ~0.25 at 360 days
        return max(0.0, 1.0 / (1.0 + days_old / 180.0))
    except (ValueError, TypeError):
        return 0.0


class ImportanceStrategy(ContextStrategy):
    name = "importance"

    def __init__(
        self,
        w_relevance: float = 0.50,
        w_recency: float = 0.20,
        w_source: float = 0.15,
        w_sensitivity: float = 0.15,
    ):
        self.w_relevance = w_relevance
        self.w_recency = w_recency
        self.w_source = w_source
        self.w_sensitivity = w_sensitivity

    def _importance_score(self, sc: ScoredChunk) -> float:
        meta = sc.chunk.metadata
        relevance = sc.score
        recency = _recency_score(meta.get("created"))
        source = DOC_TYPE_SCORES.get(meta.get("doc_type", ""), 0.5)
        penalty = SENSITIVITY_PENALTY.get(meta.get("sensitivity", "internal"), 0.1)

        return (
            self.w_relevance * relevance
            + self.w_recency * recency
            + self.w_source * source
            - self.w_sensitivity * penalty
        )

    def select(
        self, query: str, candidates: list[ScoredChunk], budget: ContextBudget
    ) -> SelectedContext:
        scored = [(self._importance_score(c), c) for c in candidates]
        scored.sort(key=lambda x: x[0], reverse=True)

        selected = []
        total = 0
        for imp_score, sc in scored:
            if total + sc.chunk.token_count > budget.max_tokens:
                continue
            selected.append(sc)
            total += sc.chunk.token_count
            if total >= budget.target_tokens:
                break

        return SelectedContext(
            chunks=selected,
            total_tokens=total,
            strategy_name=self.name,
            metadata={
                "weights": {
                    "relevance": self.w_relevance,
                    "recency": self.w_recency,
                    "source_type": self.w_source,
                    "sensitivity": self.w_sensitivity,
                }
            },
        )
