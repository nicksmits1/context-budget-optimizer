import numpy as np
from dataclasses import dataclass, field
from src.chunker import Chunk


@dataclass
class ScoredChunk:
    chunk: Chunk
    score: float
    embedding: np.ndarray
