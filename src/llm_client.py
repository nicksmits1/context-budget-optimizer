import os
import time
from dotenv import load_dotenv

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")
HF_MODEL = "Qwen/Qwen3.5-27B"
HF_API_URL = f"https://router.huggingface.co/novita/v3/openai/chat/completions"


class LLMClient:
    """Thin wrapper around HuggingFace Inference API using a Qwen model."""

    def __init__(self, token=None, model=None):
        self.token = token or HF_TOKEN
        self.model = model or HF_MODEL
        self._available = self.token is not None

    @property
    def available(self) -> bool:
        return self._available

    def generate(
        self, prompt: str, system: str = "", max_tokens: int = 1024
    ) -> dict:
        """Call the HuggingFace Inference API. Returns dict with 'answer' and 'timing' keys."""
        if not self._available:
            return self._mock_response(prompt)

        try:
            from huggingface_hub import InferenceClient

            client = InferenceClient(
                provider="novita",
                api_key=self.token,
            )

            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})

            start = time.time()
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
            )
            wall_time = time.time() - start

            answer = response.choices[0].message.content

            return {
                "answer": answer,
                "model": self.model,
                "wall_time_ms": round(wall_time * 1000, 1),
                "mock": False,
            }
        except Exception as e:
            return {
                "answer": f"[LLM call failed: {e}]",
                "model": self.model,
                "wall_time_ms": 0,
                "mock": True,
            }

    def generate_with_context(
        self, query: str, context: str, max_tokens: int = 1024
    ) -> dict:
        system = (
            "You are a helpful assistant. Answer the user's question using only "
            "the provided context. If the context doesn't contain enough information, "
            "say so. Be concise and specific."
        )
        prompt = f"Context:\n{context}\n\nQuestion: {query}"
        return self.generate(prompt, system=system, max_tokens=max_tokens)

    def judge_answer(
        self, query: str, answer: str, expected_keywords: list[str]
    ) -> dict:
        """LLM-as-judge: score answer relevance on 1-5 scale."""
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
    def _mock_response(prompt: str) -> dict:
        return {
            "answer": (
                "[Mock response — no HF_TOKEN set. "
                "Set HF_TOKEN in .env to get real LLM answers.]"
            ),
            "model": "mock",
            "wall_time_ms": 50.0,
            "mock": True,
        }
