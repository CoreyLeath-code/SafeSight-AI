.PHONY: install lint test benchmark reproduce build

install:
	python -m pip install --upgrade pip
	python -m pip install -e ".[dev]"

lint:
	python -m compileall -q safesight src api app tests
	ruff check safesight tests/test_release_*.py src/detector.py api/main.py app/app/app/core/risk_engine.py

test:
	python -m pytest tests -v --cov=safesight --cov-report=term-missing --cov-fail-under=85

benchmark:
	python -m safesight.benchmark --seed 20260828 --samples 10000 --iterations 50 --warmups 5 --output benchmark-results.json

build:
	python -m build

reproduce: lint test build benchmark
