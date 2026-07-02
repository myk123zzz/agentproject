"""OpenTelemetry and Prometheus setup."""

from typing import Any


def setup_telemetry(app: Any, settings: Any) -> None:
    """Initialize OpenTelemetry tracing and Prometheus metrics endpoints.

    In production, configures:
    - OTLP exporter for traces
    - Prometheus metrics endpoint at /metrics
    - Request/error/latency histograms for API, retrieval, and agent spans
    """
    # Placeholder — production setup uses:
    #   from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    #   FastAPIInstrumentor.instrument_app(app)
    #   from prometheus_fastapi_instrumentator import Instrumentator
    #   Instrumentator().instrument(app).expose(app)


class Metrics:
    """Application-level metrics collector."""

    def __init__(self) -> None:
        self.request_count: int = 0
        self.error_count: int = 0
        self.total_latency_ms: float = 0.0

    def record_request(self, latency_ms: float, is_error: bool = False) -> None:
        self.request_count += 1
        self.total_latency_ms += latency_ms
        if is_error:
            self.error_count += 1

    def avg_latency_ms(self) -> float:
        if self.request_count == 0:
            return 0.0
        return self.total_latency_ms / self.request_count

    def error_rate(self) -> float:
        if self.request_count == 0:
            return 0.0
        return self.error_count / self.request_count


_metrics = Metrics()


def get_metrics() -> Metrics:
    return _metrics
