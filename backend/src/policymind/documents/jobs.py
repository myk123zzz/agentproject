"""Document ingestion job definitions for ARQ worker."""


async def ingest_document_job(ctx: dict[str, object], version_id: int) -> dict[str, object]:
    """ARQ worker entry point — resolves dependencies and calls Pipeline.run().

    ctx contains Redis connection info injected by ARQ.
    """
    from policymind.documents.pipeline import IngestionPipeline

    # In production, build pipeline from real adapters.
    # For now, stub — real wiring comes in Task 8 (FastAPI).
    pipeline = IngestionPipeline(
        storage=None,  # type: ignore[arg-type]
        parser=None,  # type: ignore[arg-type]
        embedder=None,  # type: ignore[arg-type]
        vector_store=None,  # type: ignore[arg-type]
        graph_repo=None,  # type: ignore[arg-type]
    )
    result = await pipeline.run(version_id)
    return {"status": result.status.value, "version_id": version_id}
