import os
import re
import yaml
from dataclasses import dataclass, field
from src.token_counter import count_tokens

TARGET_MIN_TOKENS = 200
TARGET_MAX_TOKENS = 400


@dataclass
class Chunk:
    chunk_id: str
    doc_id: str
    content: str
    token_count: int
    metadata: dict = field(default_factory=dict)


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Split YAML frontmatter from body. Returns (metadata, body)."""
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not match:
        return {}, text
    meta = yaml.safe_load(match.group(1)) or {}
    body = text[match.end():]
    return meta, body


def _split_by_headers(body: str) -> list[str]:
    """Split markdown text on ## or ### headers, keeping the header with its section."""
    sections = re.split(r"(?=^#{2,3}\s)", body, flags=re.MULTILINE)
    return [s.strip() for s in sections if s.strip()]


def _split_by_paragraphs(text: str) -> list[str]:
    """Fallback: split on double newlines."""
    parts = re.split(r"\n\s*\n", text)
    return [p.strip() for p in parts if p.strip()]


def _merge_small_sections(sections: list[str]) -> list[str]:
    """Merge consecutive small sections to hit the target chunk size."""
    merged = []
    buf = ""
    for section in sections:
        candidate = (buf + "\n\n" + section).strip() if buf else section
        if count_tokens(candidate) > TARGET_MAX_TOKENS and buf:
            merged.append(buf)
            buf = section
        else:
            buf = candidate
    if buf:
        merged.append(buf)
    return merged


def _split_large_section(text: str) -> list[str]:
    """Break a section that exceeds TARGET_MAX_TOKENS into paragraph-level pieces."""
    paragraphs = _split_by_paragraphs(text)
    return _merge_small_sections(paragraphs)


def chunk_document(doc_id: str, raw_text: str) -> list[Chunk]:
    metadata, body = parse_frontmatter(raw_text)
    sections = _split_by_headers(body)
    if len(sections) <= 1:
        sections = _split_by_paragraphs(body)

    sections = _merge_small_sections(sections)

    # further split anything still too large
    final_sections = []
    for sec in sections:
        if count_tokens(sec) > TARGET_MAX_TOKENS:
            final_sections.extend(_split_large_section(sec))
        else:
            final_sections.append(sec)

    chunks = []
    for i, text in enumerate(final_sections):
        chunks.append(Chunk(
            chunk_id=f"{doc_id}::chunk_{i}",
            doc_id=doc_id,
            content=text,
            token_count=count_tokens(text),
            metadata=dict(metadata),
        ))
    return chunks


def load_and_chunk_corpus(corpus_dir: str) -> list[Chunk]:
    all_chunks = []
    for fname in sorted(os.listdir(corpus_dir)):
        if not fname.endswith(".md"):
            continue
        doc_id = fname.replace(".md", "")
        with open(os.path.join(corpus_dir, fname), "r") as f:
            raw = f.read()
        all_chunks.extend(chunk_document(doc_id, raw))
    return all_chunks
