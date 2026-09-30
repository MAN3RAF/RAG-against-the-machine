
PYTHON=python3
SRC=src



install:
	uv sync

run:
	uv run $(PYTHON) $(SRC)

debug:
	uv debug $(PYTHON) $(SRC)

clean:
	rm -rf __pycache__ .pytest_cache .mypy_cache

lint:
	uv run flake8 $(SRC)
	uv run mypy--warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs $(SRC)

.PHONY: install run debug clean lint