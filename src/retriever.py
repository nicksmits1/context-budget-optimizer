import numpy as np
from src.chunker import Chunk
from src.embedder import embed_texts, embed_query
from src.types import ScoredChunk


class Retriever:
    def __init__(self, chunks: list[Chunk]):
        self.chunks = chunks
        texts = [c.content for c in chunks]
        self.embeddings = embed_texts(texts)
        # normalize for cosine similarity
        norms = np.linalg.norm(self.embeddings, axis=1, keepdims=True)
        norms = np.where(norms == 0, 1, norms)
        self.embeddings = self.embeddings / norms

    def retrieve(self, query: str, top_n: int = 20) -> list[ScoredChunk]:
        q_emb = embed_query(query)
        q_emb = q_emb / (np.linalg.norm(q_emb) or 1.0)
        with np.errstate(all="ignore"):
            scores = self.embeddings @ q_emb
        scores = np.nan_to_num(scores, nan=0.0)
        top_idx = np.argsort(scores)[::-1][:top_n]
        return [
            ScoredChunk(
                chunk=self.chunks[i],
                score=float(scores[i]),
                embedding=self.embeddings[i],
            )
            for i in top_idx
        ]
