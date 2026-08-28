"""Deterministic development benchmark for SafeSight's risk-policy code path."""

from __future__ import annotations

import argparse
import json
import os
import platform
import random
import statistics
import time
import tracemalloc
from collections.abc import Iterable
from pathlib import Path

from . import __version__
from .policy import RiskLevel, RiskPolicy


def _percentile(values: list[float], quantile: float) -> float:
    if not values:
        raise ValueError("values must not be empty")
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, round((len(ordered) - 1) * quantile)))
    return ordered[index]


def _dataset(seed: int, samples: int) -> list[float]:
    if samples <= 0:
        raise ValueError("samples must be greater than zero")
    rng = random.Random(seed)
    return [rng.random() for _ in range(samples)]


def _classify(policy: RiskPolicy, values: Iterable[float]) -> dict[str, int]:
    counts = {level.value: 0 for level in RiskLevel}
    for value in values:
        counts[policy.classify(value).level.value] += 1
    return counts


def run_benchmark(
    *,
    seed: int = 20260828,
    samples: int = 10_000,
    iterations: int = 50,
    warmups: int = 5,
) -> dict[str, object]:
    """Benchmark a fixed set of synthetic confidence scores.

    The benchmark measures only deterministic policy classification. It does
    not measure computer-vision inference, API/network latency, or safety/model
    quality.
    """
    if iterations <= 0 or warmups < 0:
        raise ValueError("iterations must be > 0 and warmups must be >= 0")

    values = _dataset(seed, samples)
    policy = RiskPolicy()
    expected_counts = _classify(policy, values)

    for _ in range(warmups):
        if _classify(policy, values) != expected_counts:
            raise RuntimeError("deterministic benchmark warm-up changed output")

    latencies_ms: list[float] = []
    tracemalloc.start()
    try:
        for _ in range(iterations):
            start = time.perf_counter_ns()
            counts = _classify(policy, values)
            elapsed_ns = time.perf_counter_ns() - start
            if counts != expected_counts:
                raise RuntimeError("deterministic benchmark output changed")
            latencies_ms.append(elapsed_ns / 1_000_000)
        _, peak_bytes = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()

    median_ms = statistics.median(latencies_ms)
    total_decisions = samples * iterations
    total_seconds = sum(latencies_ms) / 1000.0

    return {
        "protocol": {
            "seed": seed,
            "samples_per_iteration": samples,
            "measured_iterations": iterations,
            "warmups": warmups,
            "medium_threshold": policy.medium_threshold,
            "high_threshold": policy.high_threshold,
            "scope": (
                "in-process deterministic risk-policy classification of seeded "
                "synthetic confidence scores"
            ),
        },
        "performance": {
            "median_ms": round(median_ms, 6),
            "p95_ms": round(_percentile(latencies_ms, 0.95), 6),
            "p99_ms": round(_percentile(latencies_ms, 0.99), 6),
            "decisions_per_second": round(total_decisions / total_seconds, 3),
            "peak_traced_memory_mib": round(peak_bytes / (1024 * 1024), 6),
        },
        "deterministic_result_snapshot": expected_counts,
        "environment": {
            "git_sha": os.getenv("GITHUB_SHA", "local-unrecorded"),
            "python": platform.python_version(),
            "platform": platform.platform(),
            "package_version": __version__,
        },
        "interpretation": (
            "Development benchmark only. Excludes model inference, image decoding, "
            "HTTP/network overhead, concurrency, accelerator behavior, and any claim "
            "about real-world safety or model quality."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=20260828)
    parser.add_argument("--samples", type=int, default=10_000)
    parser.add_argument("--iterations", type=int, default=50)
    parser.add_argument("--warmups", type=int, default=5)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    result = run_benchmark(
        seed=args.seed,
        samples=args.samples,
        iterations=args.iterations,
        warmups=args.warmups,
    )
    rendered = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)


if __name__ == "__main__":
    main()
