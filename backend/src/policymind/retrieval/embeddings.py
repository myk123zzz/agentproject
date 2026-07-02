"""Embedding provider — real OpenAI-compatible + no-op test fallback."""

from typing import Protocol

from policymind.core.errors import EmbeddingUnavailable


class EmbeddingProvider(Protocol):
    dimension: int
    model_name: str

    async def embed_documents(self, texts: list[str]) -> list[list[float]]: ...
    async def embed_query(self, text: str) -> list[float]: ...


class OpenAIEmbeddingProvider:
    """OpenAI-compatible embedding API."""

    def __init__(
        self,
        *,
        base_url: str = "https://api.openai.com/v1",
        api_key: str = "",
        model: str = "text-embedding-3-small",
    ) -> None:
        self._base_url = base_url
        self._api_key = api_key
        self.model_name = model
        self.dimension = 1536

    async def _call(self, texts: list[str]) -> list[list[float]]:
        import httpx

        headers = {"Authorization": f"Bearer {self._api_key}"}
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    f"{self._base_url}/embeddings",
                    json={"input": texts, "model": self.model_name},
                    headers=headers,
                )
                resp.raise_for_status()
                data = resp.json()
                return [item["embedding"] for item in data["data"]]
        except Exception as exc:
            raise EmbeddingUnavailable(f"Embedding API error: {exc}") from exc

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        vectors = await self._call(texts)
        if any(len(v) == 0 for v in vectors):
            raise EmbeddingUnavailable("Embedding API returned zero vectors")
        self.dimension = len(vectors[0]) if vectors else self.dimension
        return vectors

    async def embed_query(self, text: str) -> list[float]:
        vectors = await self._call([text])
        if not vectors or len(vectors[0]) == 0:
            raise EmbeddingUnavailable("Embedding API returned zero vector")
        return vectors[0]


class NoOpEmbeddingProvider:
    """Fixed-vector provider for testing."""

    dimension: int = 768
    model_name: str = "noop/test"

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [[0.1] * self.dimension for _ in texts]

    async def embed_query(self, text: str) -> list[float]:
        return [0.1] * self.dimension
