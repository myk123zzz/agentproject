"""Port type definitions for the retrieval domain."""

from dataclasses import dataclass, field


@dataclass
class SearchHit:
    chunk_id: str
    text: str
    score: float
    channel: str
    rank: int
    page_number: int = 1
    document_name: str = ""
    document_version: str = ""
    bbox: tuple[float, float, float, float] | None = None


@dataclass
class Citation:
    id: str
    document_name: str
    document_version: str
    page_number: int
    quote: str
    bbox: tuple[float, float, float, float] | None = None
    channel: str = ""
    score: float = 0.0


@dataclass
class CitationValidation:
    is_valid: bool
    unknown_ids: list[str] = field(default_factory=list)
    unused_ids: list[str] = field(default_factory=list)
    present_ids: list[str] = field(default_factory=list)


@dataclass
class RetrievalTrace:
    dense_hits: int = 0
    bm25_hits: int = 0
    graph_hits: int = 0
    fused_count: int = 0
    rerank_count: int = 0
    final_count: int = 0
    rerank_used: bool = False
    graph_used: bool = False
    latency_ms: float = 0.0
    error: str | None = None


@dataclass
class RetrievalBundle:
    query: str
    hits: list[SearchHit]
    citations: list[Citation]
    context: str
    trace: RetrievalTrace


@dataclass
class HybridCandidates:
    dense: list[SearchHit]
    sparse: list[SearchHit]
