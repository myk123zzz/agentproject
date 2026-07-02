#!/usr/bin/env python3
"""Run offline evaluation across all baseline variants."""

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend" / "src"))


async def main():
    from policymind.evaluation.runner import EvaluationRunner, GoldenCase

    dataset_path = Path(__file__).resolve().parents[1] / "evaluation" / "datasets" / "golden_v1.jsonl"
    cases: list[GoldenCase] = []
    if dataset_path.exists():
        with open(dataset_path, encoding="utf-8") as f:
            for line in f:
                raw = json.loads(line)
                cases.append(GoldenCase(**raw))

    runner = EvaluationRunner(cases)
    report = await runner.run()
    print(f"Dataset: {report.dataset_version}, Variant: {report.variant}")
    print(f"Cases evaluated: {len(report.results)}")


if __name__ == "__main__":
    asyncio.run(main())
