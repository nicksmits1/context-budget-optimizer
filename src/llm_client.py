import os
import time
import torch
from dotenv import load_dotenv

load_dotenv()

MODEL_ID = "Qwen/Qwen2.5-1.5B-Instruct"

_pipeline = None


def _get_pipeline():
    global _pipeline
    if _pipeline is not None:
        return _pipeline

    from transformers import pipeline

    device = "mps" if torch.backends.mps.is_available() else "cpu"
    _pipeline = pipeline(
        "text-generation",
        model=MODEL_ID,
        dtype=torch.float16 if device == "mps" else torch.float32,
        device=device,
    )
    return _pipeline


class LLMClient:
    """Runs a local Qwen model for inference — no API needed."""

    def __init__(self):
        self._available = True
        self._pipe = None

    @property
    def available(self) -> bool:
        return self._available

    def _pipe_ready(self):
        if self._pipe is None:
            try:
                self._pipe = _get_pipeline()
            except Exception:
                self._available = False
                return False
        return True

    def generate(self, prompt: str, system: str = "", max_tokens: int = 512) -> dict:
        if not self._pipe_ready():
            return self._mock_response()

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        try:
            start = time.time()
            out = self._pipe(
                messages,
                max_new_tokens=max_tokens,
                do_sample=True,
                temperature=0.3,
                top_p=0.9,
            )
            wall_time = time.time() - start
            answer = out[0]["generated_text"][-1]["content"]
            return {
                "answer": answer,
                "model": MODEL_ID,
                "wall_time_ms": round(wall_time * 1000, 1),
                "mock": False,
            }
        except Exception as e:
            return {
                "answer": f"[LLM error: {e}]",
                "model": MODEL_ID,
                "wall_time_ms": 0,
                "mock": True,
            }

    def generate_with_context(self, query: str, context: str, max_tokens: int = 256) -> dict:
        system = (
            "You are a helpful assistant. Answer the user's question using only "
            "the provided context. If the context doesn't contain enough information, "
            "say so. Be concise and specific."
        )
        prompt = f"Context:\n{context}\n\nQuestion: {query}"
        return self.generate(prompt, system=system, max_tokens=max_tokens)

    def judge_answer(self, query: str, answer: str, expected_keywords: list[str]) -> dict:
        prompt = (
            f"Rate the following answer to the question on a scale of 1-5 "
            f"(1=irrelevant, 5=excellent). Consider whether it addresses the question "
            f"and covers these key topics: {', '.join(expected_keywords)}.\n\n"
            f"Question: {query}\n\nAnswer: {answer}\n\n"
            f"Respond with ONLY a single integer from 1 to 5."
        )
        result = self.generate(prompt, max_tokens=8)
        try:
            score = int("".join(c for c in result["answer"] if c.isdigit())[:1])
            return {"score": min(max(score, 1), 5), "mock": result["mock"]}
        except (ValueError, IndexError):
            return {"score": 3, "mock": True}

    @staticmethod
    def _mock_response() -> dict:
        return {
            "answer": "[Mock — failed to load local model]",
            "model": "mock",
            "wall_time_ms": 50.0,
            "mock": True,
        }
