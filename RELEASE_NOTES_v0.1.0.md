# SafeSight AI v0.1.0

This is the first evidence-bounded release of SafeSight AI's canonical `safesight` package.

## Included

- bounded FastAPI image-upload validation with content-type checks, size limits, and byte-level image verification;
- explicit `/health` liveness and `/ready` model-readiness semantics;
- fail-closed `/predict` behavior when no reviewed safety model artifact is packaged;
- deterministic `RiskPolicy` with validated finite `[0,1]` inputs and explicit LOW/MEDIUM/HIGH thresholds;
- deterministic synthetic legacy-detector fixture with validated and functional threshold filtering;
- Python 3.10/3.11/3.12 fail-closed CI;
- 85% minimum coverage gate, with 96.24% canonical-package coverage in the reference validation run;
- wheel and source distribution build plus fresh-environment wheel installation smoke test;
- deterministic fixed-seed policy benchmark with machine-readable JSON evidence;
- non-root Docker runtime with container liveness/readiness smoke tests;
- CodeQL analysis;
- source archive, SHA-256 checksums, CycloneDX SBOM, GitHub Release assets, and a versioned GHCR image.

## Evidence boundary

SafeSight AI v0.1.0 does **not** ship a reviewed computer-vision model artifact or a versioned evaluation dataset. The release therefore does not claim validated image-classification accuracy, precision, recall, F1, calibration, GPU/CUDA inference, production request capacity, or real-world safety effectiveness.

The benchmark measures only deterministic in-process risk-policy classification of seeded synthetic confidence scores. It excludes image decoding, model inference, HTTP/network overhead, concurrency, accelerators, and production safety behavior.

## Reference validation

- CI run: `33200052693`
- CodeQL run: `33200052683`
- Tests: `50/50` passed on Python `3.10`, `3.11`, and `3.12`
- Canonical `safesight` coverage: `96.24%`
- Coverage gate: `85%` fail-closed
- Reference benchmark: median `37.725465 ms`, p95 `38.247523 ms`, p99 `38.320200 ms` per 10,000 policy classifications; derived `264,728.683` classifications/second; peak traced memory `0.002338 MiB`

The release workflow reruns the correctness, packaging, and benchmark gates before publishing versioned artifacts.
