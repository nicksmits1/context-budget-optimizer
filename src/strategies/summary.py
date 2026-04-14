from src.strategies.base import ContextStrategy, ContextBudget, SelectedContext
from src.types import ScoredChunk
from src.token_counter import count_tokens


class SummaryStrategy(ContextStrategy):
    name = "summary"

    def __init__(self, top_full: int = 5, llm_client=None):
        self.top_full = top_full
        self.llm_client = llm_client

    def select(
        self, query: str, candidates: list[ScoredChunk], budget: ContextBudget
    ) -> SelectedContext:
        sorted_cands = sorted(candidates, key=lambda c: c.score, reverse=True)

        # keep top chunks in full
        full_chunks = sorted_cands[: self.top_full]
        rest = sorted_cands[self.top_full :]

        full_tokens = sum(c.chunk.token_count for c in full_chunks)
        remaining_budget = budget.max_tokens - full_tokens

        if remaining_budget <= 0 or not rest:
            # budget already consumed by full chunks
            selected = []
            total = 0
            for sc in full_chunks:
                if total + sc.chunk.token_count > budget.max_tokens:
                    break
                selected.append(sc)
                total += sc.chunk.token_count
            return SelectedContext(
                chunks=selected,
                total_tokens=total,
                strategy_name=self.name,
                metadata={"compressed": False},
            )

        # gather text from lower-ranked chunks to summarize
        rest_text = "\n\n".join(c.chunk.content for c in rest)
        original_rest_tokens = sum(c.chunk.token_count for c in rest)

        summary_text = self._compress(query, rest_text, remaining_budget)
        summary_tokens = count_tokens(summary_text)

        # build a synthetic ScoredChunk for the summary
        from src.chunker import Chunk
        import numpy as np

        summary_chunk = ScoredChunk(
            chunk=Chunk(
                chunk_id="__summary__",
                doc_id="__summary__",
                content=summary_text,
                token_count=summary_tokens,
                metadata={"doc_type": "summary", "title": "Compressed Context"},
            ),
            score=0.0,
            embedding=np.zeros(1),
        )

        selected = list(full_chunks) + [summary_chunk]
        total = sum(c.chunk.token_count for c in selected)

        return SelectedContext(
            chunks=selected,
            total_tokens=total,
            strategy_name=self.name,
            metadata={
                "compressed": True,
                "original_rest_tokens": original_rest_tokens,
                "summary_tokens": summary_tokens,
                "compression_ratio": round(
                    original_rest_tokens / max(summary_tokens, 1), 2
                ),
            },
        )

    def _compress(self, query: str, text: str, target_tokens: int) -> str:
        """Compress text using LLM if available, else do extractive truncation."""
        if self.llm_client and getattr(self.llm_client, "available", False):
            try:
                prompt = (
                    f"Summarize the following information as it relates to this query: '{query}'. "
                    f"Be concise. Keep the summary under {target_tokens} tokens.\n\n{text}"
                )
                gen_limit = min(target_tokens, 512)
                result = self.llm_client.generate(prompt, max_tokens=gen_limit)
                if not result.get("mock", True):
                    return result["answer"]
            except Exception:
                pass

        # fallback: extractive — take first N tokens worth of sentences
        sentences = text.replace("\n", " ").split(". ")
        out = []
        tokens_so_far = 0
        for s in sentences:
            t = count_tokens(s)
            if tokens_so_far + t > target_tokens:
                break
            out.append(s)
            tokens_so_far += t
        return ". ".join(out)
