.PHONY: test verify clean lint

PYTHON = python

# Canonical test command — matches CI (test.yml) and README
test:
	@echo "Running Tests (pytest)..."
	$(PYTHON) -m pytest tests/ -x -q

# Full verification: tests + architecture boundary + doc consistency
verify: test
	@echo "Running Architecture Verification..."
	$(PYTHON) scripts/verify_layer_boundaries.py
	$(PYTHON) scripts/verify_docs_consistency.py

# Lint check
lint:
	@echo "Running Lint..."
	$(PYTHON) -m ruff check tonesoul/ tests/

clean:
	@echo "Cleaning artifacts..."
	rm -rf __pycache__
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
