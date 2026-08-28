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
