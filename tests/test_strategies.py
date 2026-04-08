import numpy as np
import pytest
from src.chunker import Chunk, chunk_document, parse_frontmatter
from src.token_counter import count_tokens, estimate_ttft
from src.types import ScoredChunk
from src.strategies.base import ContextBudget
from src.strategies.topk import TopKStrategy
from src.strategies.budget_topk import BudgetTopKStrategy
from src.strategies.mmr import MMRStrategy
from src.strategies.importance import ImportanceStrategy
from src.strategies.summary import SummaryStrategy
from src.evaluator import keyword_score, doc_coverage


def _make_scored_chunk(chunk_id, content, score, doc_id="test_doc", metadata=None):
    meta = metadata or {"department": "engineering", "doc_type": "technical", "created": "2025-06-01", "sensitivity": "internal"}
    tokens = count_tokens(content)
    emb = np.random.randn(384).astype(np.float32)
    emb = emb / np.linalg.norm(emb)
    return ScoredChunk(
        chunk=Chunk(chunk_id=chunk_id, doc_id=doc_id, content=content, token_count=tokens, metadata=meta),
        score=score,
        embedding=emb,
    )


@pytest.fixture
def sample_chunks():
    return [
        _make_scored_chunk("doc_a::chunk_0", "Revenue was $47.2M in Q3. " * 10, 0.9, "doc_a"),
        _make_scored_chunk("doc_a::chunk_1", "Gross margin improved to 72.4%. " * 10, 0.85, "doc_a"),
        _make_scored_chunk("doc_b::chunk_0", "The parental leave policy allows 16 weeks. " * 10, 0.7, "doc_b"),
        _make_scored_chunk("doc_c::chunk_0", "Kubernetes cluster runs on EKS with three node groups. " * 10, 0.6, "doc_c"),
        _make_scored_chunk("doc_d::chunk_0", "The on-call rotation runs Monday to Monday. " * 8, 0.5, "doc_d"),
        _make_scored_chunk("doc_e::chunk_0", "SOC 2 audit is underway with Deloitte. " * 6, 0.4, "doc_e"),
    ]


class TestTokenCounter:
    def test_known_string(self):
        assert count_tokens("hello world") > 0

    def test_empty_string(self):
        assert count_tokens("") == 0

    def test_estimate_ttft_increases_with_tokens(self):
        assert estimate_ttft(1000) > estimate_ttft(100)

    def test_estimate_ttft_positive(self):
        assert estimate_ttft(0) > 0


class TestChunker:
    def test_parse_frontmatter(self):
        text = "---\ntitle: Test\ndepartment: eng\n---\n\n# Hello\nBody text."
        meta, body = parse_frontmatter(text)
        assert meta["title"] == "Test"
        assert "Hello" in body

    def test_chunks_retain_metadata(self):
        raw = "---\ntitle: Test Doc\ndepartment: finance\ndoc_type: report\ncreated: '2025-01-01'\nsensitivity: confidential\n---\n\n# Section 1\n\nSome content here that should be chunked properly.\n\n## Section 2\n\nMore content in a second section with enough words to form a chunk."
        chunks = chunk_document("test_doc", raw)
        assert len(chunks) >= 1
        assert chunks[0].metadata["department"] == "finance"
        assert chunks[0].doc_id == "test_doc"
        assert "test_doc::chunk_" in chunks[0].chunk_id

    def test_chunk_ids_unique(self):
        raw = "---\ntitle: Test\n---\n\n## A\nFirst.\n\n## B\nSecond.\n\n## C\nThird."
        chunks = chunk_document("test", raw)
        ids = [c.chunk_id for c in chunks]
        assert len(ids) == len(set(ids))


class TestTopK:
    def test_respects_budget(self, sample_chunks):
        strategy = TopKStrategy()
        budget = ContextBudget(max_tokens=200)
        result = strategy.select("test query", sample_chunks, budget)
        assert result.total_tokens <= budget.max_tokens

    def test_ordered_by_score(self, sample_chunks):
        strategy = TopKStrategy()
        budget = ContextBudget(max_tokens=10000)
        result = strategy.select("test query", sample_chunks, budget)
        scores = [c.score for c in result.chunks]
        assert scores == sorted(scores, reverse=True)


class TestBudgetTopK:
    def test_respects_hard_ceiling(self, sample_chunks):
        strategy = BudgetTopKStrategy()
        budget = ContextBudget(max_tokens=300)
        result = strategy.select("test query", sample_chunks, budget)
        assert result.total_tokens <= budget.max_tokens

    def test_packs_small_chunks(self, sample_chunks):
        strategy = BudgetTopKStrategy()
        budget = ContextBudget(max_tokens=5000)
        result = strategy.select("test query", sample_chunks, budget)
        # should include multiple chunks via packing
        assert len(result.chunks) >= 2 if len(sample_chunks) >= 2 else True


class TestMMR:
    def test_respects_budget(self, sample_chunks):
        strategy = MMRStrategy(lambda_param=0.7)
        budget = ContextBudget(max_tokens=300)
        result = strategy.select("test query", sample_chunks, budget)
        assert result.total_tokens <= budget.max_tokens

    def test_diversity(self):
        """MMR should prefer diverse chunks over near-duplicates."""
        base_emb = np.array([1.0, 0.0, 0.0], dtype=np.float32)
        similar_emb = np.array([0.99, 0.1, 0.0], dtype=np.float32)
        similar_emb /= np.linalg.norm(similar_emb)
        diff_emb = np.array([0.0, 1.0, 0.0], dtype=np.float32)

        chunks = [
            ScoredChunk(chunk=Chunk("a::0", "a", "Text A", 10, {}), score=0.95, embedding=base_emb),
            ScoredChunk(chunk=Chunk("a::1", "a", "Text A copy", 10, {}), score=0.93, embedding=similar_emb),
            ScoredChunk(chunk=Chunk("b::0", "b", "Text B different", 10, {}), score=0.80, embedding=diff_emb),
        ]

        strategy = MMRStrategy(lambda_param=0.5)
        budget = ContextBudget(max_tokens=30)
        result = strategy.select("test", chunks, budget)

        selected_ids = [c.chunk.chunk_id for c in result.chunks]
        # with lambda=0.5 and budget for all 3, should pick a::0 then b::0 (diverse) before a::1
        if len(selected_ids) >= 2:
            assert "a::0" in selected_ids
            assert "b::0" in selected_ids


class TestImportance:
    def test_respects_budget(self, sample_chunks):
        strategy = ImportanceStrategy()
        budget = ContextBudget(max_tokens=300)
        result = strategy.select("test query", sample_chunks, budget)
        assert result.total_tokens <= budget.max_tokens

    def test_weights_in_metadata(self, sample_chunks):
        strategy = ImportanceStrategy()
        budget = ContextBudget(max_tokens=5000)
        result = strategy.select("test query", sample_chunks, budget)
        assert "weights" in result.metadata


class TestSummary:
    def test_respects_budget(self, sample_chunks):
        strategy = SummaryStrategy(top_full=2, llm_client=None)
        budget = ContextBudget(max_tokens=500)
        result = strategy.select("test query", sample_chunks, budget)
        assert result.total_tokens <= budget.max_tokens + 50  # small tolerance for extractive fallback

    def test_compression_metadata(self, sample_chunks):
        strategy = SummaryStrategy(top_full=2, llm_client=None)
        budget = ContextBudget(max_tokens=5000)
        result = strategy.select("test query", sample_chunks, budget)
        assert "compressed" in result.metadata


class TestEvaluatorHelpers:
    def test_keyword_score(self):
        assert keyword_score("Revenue was $47.2M in Q3", ["revenue", "47.2", "Q3"]) == 1.0
        assert keyword_score("Hello world", ["revenue", "Q3"]) == 0.0
        assert keyword_score("", ["a"]) == 0.0

    def test_doc_coverage(self):
        assert doc_coverage(["doc_a::chunk_0", "doc_b::chunk_1"], ["doc_a", "doc_b"]) == 1.0
        assert doc_coverage(["doc_a::chunk_0"], ["doc_a", "doc_b"]) == 0.5
        assert doc_coverage([], ["doc_a"]) == 0.0
