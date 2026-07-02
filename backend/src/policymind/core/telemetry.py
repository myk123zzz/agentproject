"""OpenTelemetry and Prometheus setup."""

from typing import Any


def setup_telemetry(app: Any, settings: Any) -> None:
    """Initialize OpenTelemetry tracing and Prometheus metrics endpoints."""
    # Placeholder — real implementation uses opentelemetry-instrumentation-fastapi
    pass


class Metrics:
    """Application-level metrics counters."""

    def __init__(self) -> None:
        self.request_count: int = 0
        self.error_count: int = 0
        self.total_latency_ms: float = 0.0

    def record_request(self, latency_ms: float, is_error: bool = False) -> None:
        self.request_count += 1
        self.total_latency_ms += latency_ms
        if is_error:
            self.error_count += 1


_metrics = Metrics()


def get_metrics() -> Metrics:
    return _metrics
