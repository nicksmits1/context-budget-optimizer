from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from src.types import ScoredChunk


@dataclass
class ContextBudget:
    max_tokens: int
    target_tokens: int = 0

    def __post_init__(self):
        if self.target_tokens <= 0:
            self.target_tokens = int(self.max_tokens * 0.70)


@dataclass
class SelectedContext:
    chunks: list[ScoredChunk]
    total_tokens: int
    strategy_name: str
    metadata: dict = field(default_factory=dict)

    @property
    def text(self) -> str:
        parts = []
        for sc in self.chunks:
            header = f"[{sc.chunk.metadata.get('title', sc.chunk.doc_id)}]"
            parts.append(f"{header}\n{sc.chunk.content}")
        return "\n\n---\n\n".join(parts)


class ContextStrategy(ABC):
    name: str = "base"

    @abstractmethod
    def select(
        self, query: str, candidates: list[ScoredChunk], budget: ContextBudget
    ) -> SelectedContext:
        pass
