import json

import pytest

from safesight import benchmark
from safesight.benchmark import run_benchmark


def test_benchmark_is_deterministic_for_fixed_seed():
    first = run_benchmark(seed=7, samples=100, iterations=2, warmups=1)
    second = run_benchmark(seed=7, samples=100, iterations=2, warmups=1)
    assert first["deterministic_result_snapshot"] == second["deterministic_result_snapshot"]
    assert sum(first["deterministic_result_snapshot"].values()) == 100


def test_benchmark_protocol_records_scope_and_sample_count():
    result = run_benchmark(seed=11, samples=25, iterations=1, warmups=0)
    protocol = result["protocol"]
    assert protocol["samples_per_iteration"] == 25
    assert protocol["measured_iterations"] == 1
    assert "risk-policy classification" in protocol["scope"]
    assert "model inference" in result["interpretation"]


@pytest.mark.parametrize(
    "kwargs",
    [
        {"samples": 0},
        {"iterations": 0},
        {"warmups": -1},
    ],
)
def test_invalid_benchmark_protocol_is_rejected(kwargs):
    with pytest.raises(ValueError):
        run_benchmark(**kwargs)


def test_benchmark_cli_writes_machine_readable_output(monkeypatch, tmp_path, capsys):
    output = tmp_path / "benchmark.json"
    monkeypatch.setattr(
        "sys.argv",
        [
            "safesight-benchmark",
            "--seed",
            "9",
            "--samples",
            "20",
            "--iterations",
            "1",
            "--warmups",
            "0",
            "--output",
            str(output),
        ],
    )
    benchmark.main()
    written = json.loads(output.read_text(encoding="utf-8"))
    printed = json.loads(capsys.readouterr().out)
    assert written["protocol"]["seed"] == 9
    assert written == printed
