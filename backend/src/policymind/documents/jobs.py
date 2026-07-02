"""Document ingestion job — ARQ entry point."""


async def ingest_document_job(ctx: dict[str, object], version_id: int) -> dict[str, object]:
    """ARQ worker entry point. Builds real adapters from config and calls Pipeline.run()."""
    # In production: adapters are built from shared config/settings.
    # The worker process has access to the same services as the API.
    from policymind.documents.pipeline import ProcessingStatus

    # Placeholder — full wiring in R3-R5 when infrastructure is running
    return {
        "status": ProcessingStatus.QUEUED.value,
        "version_id": version_id,
        "message": "Worker received job; full pipeline wiring in integration phase.",
    }
