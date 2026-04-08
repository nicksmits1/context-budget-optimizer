import tiktoken

_encoder = tiktoken.get_encoding("cl100k_base")


def count_tokens(text: str) -> int:
    return len(_encoder.encode(text))


def estimate_ttft(token_count: int) -> float:
    """Rough heuristic: base latency + per-token overhead for context processing."""
    base_ms = 150.0
    per_token_ms = 0.08
    return base_ms + token_count * per_token_ms
