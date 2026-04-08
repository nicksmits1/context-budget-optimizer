from src.chunker import load_and_chunk_corpus
from src.retriever import Retriever
from src.strategies.base import ContextBudget, SelectedContext, ContextStrategy
from src.llm_client import LLMClient
from src.token_counter import estimate_ttft


class Optimizer:
    """Main entry point: query -> retrieve -> strategy -> optimized context -> answer."""

    def __init__(self, corpus_dir: str, llm_client=None):
        self.chunks = load_and_chunk_corpus(corpus_dir)
        self.retriever = Retriever(self.chunks)
        self.llm = llm_client or LLMClient()

    def run(
        self,
        query: str,
        strategy: ContextStrategy,
        budget: ContextBudget,
        top_n: int = 20,
        generate_answer: bool = True,
    ) -> dict:
        candidates = self.retriever.retrieve(query, top_n=top_n)
        selection = strategy.select(query, candidates, budget)
        estimated_ttft = estimate_ttft(selection.total_tokens)

        result = {
            "query": query,
            "strategy": selection.strategy_name,
            "budget_max": budget.max_tokens,
            "budget_target": budget.target_tokens,
            "total_tokens": selection.total_tokens,
            "num_chunks": len(selection.chunks),
            "estimated_ttft_ms": round(estimated_ttft, 1),
            "chunk_ids": [sc.chunk.chunk_id for sc in selection.chunks],
            "strategy_metadata": selection.metadata,
        }

        if generate_answer:
            llm_result = self.llm.generate_with_context(query, selection.text)
            result["answer"] = llm_result["answer"]
            result["actual_ttft_ms"] = llm_result["wall_time_ms"]
            result["llm_mock"] = llm_result["mock"]
        else:
            result["answer"] = None
            result["actual_ttft_ms"] = None
            result["llm_mock"] = True

        return result
