# SafeSight AI — Evidence & Metrics

SafeSight v0.1.0 deliberately separates **software correctness/performance evidence** from **computer-vision model quality**. No reviewed model artifact or versioned evaluation dataset is shipped in this release, so accuracy, precision, recall, F1, model size, GPU utilization, inference latency, and real-world safety effectiveness are **not reported as validated metrics**.

## Verified software evidence

Source CI run: [`33200052693`](https://github.com/CoreyLeath-code/SafeSight-AI/actions/runs/33200052693), validated on the PR merge ref `3b97d3cee729a1284807fab8822b0898df562cef`.

| Evidence | Verified result |
|---|---:|
| Tests | 50/50 passed |
| Python matrix | 3.10 / 3.11 / 3.12 passed |
| Canonical `safesight` coverage | 96.24% (186 statements, 7 missed) |
| Coverage gate | 85% fail-closed |
| Ruff + compile checks | passed |
| Wheel + sdist build | passed |
| Built-wheel install smoke test | passed |
| Container build | passed |
| `/health` container smoke test | HTTP 200 |
| `/ready` without verified model | HTTP 503, as designed |
| CodeQL | passed on the validated head |

## Research-style development benchmark

**Question measured:** How long does the deterministic in-process `RiskPolicy` take to classify the same seeded set of synthetic confidence scores on a documented GitHub Actions runner?

This benchmark does **not** execute computer-vision inference and must not be interpreted as image inference latency, HTTP capacity, GPU performance, safety effectiveness, or model accuracy.

### Protocol

- seed: `20260828`
- synthetic confidence scores per iteration: `10,000`
- warm-up iterations: `5`
- measured iterations: `50`
- total measured classifications: `500,000`
- medium threshold: `0.60`
- high threshold: `0.85`
- timing: `time.perf_counter_ns()` around deterministic policy classification
- memory: Python `tracemalloc` peak during measured iterations
- Python: `3.11.16`
- runner platform: `Linux-6.17.0-1022-azure-x86_64-with-glibc2.39`
- source artifact: [`benchmarks/latest.json`](benchmarks/latest.json)
- originating CI run: `33200052693`

### Results

| Measurement | Verified value |
|---|---:|
| Median latency / 10,000 classifications | 37.725465 ms |
| p95 latency / 10,000 classifications | 38.247523 ms |
| p99 latency / 10,000 classifications | 38.320200 ms |
| Derived classifications / second | 264,728.683 |
| Peak traced Python memory | 0.002338 MiB |
| LOW results in seeded fixture | 6,025 |
| MEDIUM results in seeded fixture | 2,441 |
| HIGH results in seeded fixture | 1,534 |

Timing values characterize this specific runner and workload. They are not hard SLAs and may vary across machines or dependency/runtime versions. The LOW/MEDIUM/HIGH counts are deterministic regression evidence for the fixed seed and thresholds, not evidence that the thresholds are clinically, legally, or operationally optimal.

## Model-quality evidence status

| Model-quality evidence | v0.1.0 status |
|---|---|
| Reviewed model artifact with immutable hash | Not shipped |
| Versioned evaluation dataset | Not shipped |
| Dataset provenance/licensing record | Not shipped |
| Train/validation/test split protocol | Not shipped |
| Precision / recall / F1 | Not validated |
| Calibration / threshold study | Not validated |
| Subgroup / scenario error analysis | Not validated |
| Image inference latency / throughput | Not measurable from the release because inference is intentionally unavailable |

The API therefore fails closed: a valid image can be decoded and validated, but `/predict` returns HTTP 503 with `verified_model_unavailable` rather than fabricating a safety classification.

## Reproducing the evidence

```bash
python -m venv .venv
source .venv/bin/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
make reproduce
```

Equivalent benchmark-only command:

```bash
python -m safesight.benchmark \
  --seed 20260828 \
  --samples 10000 \
  --iterations 50 \
  --warmups 5 \
  --output benchmark-results.json
```

For a release, the release workflow reruns the gates and publishes a fresh `benchmark-results.json`, source/checksum artifacts, an SBOM, Python distributions, and the versioned GHCR image.
