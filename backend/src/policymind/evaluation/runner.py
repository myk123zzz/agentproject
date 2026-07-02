"""EvaluationRunner — executes eval runs and compares baselines."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class GoldenCase:
    id: str
    category: str
    question: str
    required_facts: list[str] = field(default_factory=list)
    expected_document_versions: list[str] = field(default_factory=list)
    expected_pages: list[int] = field(default_factory=list)
    expected_route: str = ""
    expected_tools: list[str] = field(default_factory=list)
    expected_graph_edges: list[str] = field(default_factory=list)
    should_refuse: bool = False


@dataclass
class CaseResult:
    case_id: str
    answer: str
    metrics: dict[str, float] = field(default_factory=dict)
    trace: dict[str, Any] = field(default_factory=dict)


@dataclass
class EvaluationReport:
    dataset_version: str
    model_name: str
    prompt_version: str
    variant: str
    results: list[CaseResult] = field(default_factory=list)
    aggregate_metrics: dict[str, float] = field(default_factory=dict)


class EvaluationRunner:
    """Runs golden cases against a configured system variant and computes metrics."""

    def __init__(self, dataset: list[GoldenCase]):
        self._dataset = dataset

    async def run_case(self, case: GoldenCase, variant: str = "full") -> CaseResult:
        """Evaluate a single case (stub — real impl calls agent graph)."""
        return CaseResult(
            case_id=case.id,
            answer=f"Answer for: {case.question}",
            metrics={
                "required_fact_coverage": 1.0,
                "routing_accuracy": 1.0,
            },
        )

    async def run(self, dataset_version: str = "v1") -> EvaluationReport:
        results = []
        for case in self._dataset:
            results.append(await self.run_case(case))
        return EvaluationReport(
            dataset_version=dataset_version,
            model_name="default",
            prompt_version="v1",
            variant="full",
            results=results,
        )


def compare_reports(*reports: EvaluationReport) -> dict[str, Any]:
    """Compare metrics across multiple evaluation runs."""
    comparison: dict[str, Any] = {"variants": [], "metrics": {}}
    for r in reports:
        comparison["variants"].append(r.variant)
        for metric, value in r.aggregate_metrics.items():
            if metric not in comparison["metrics"]:
                comparison["metrics"][metric] = []
            comparison["metrics"][metric].append(value)
    return comparison
