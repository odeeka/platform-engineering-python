.PHONY: install test build clean

install:
	pip install '.[dev]'

test:
	pytest -v

build:
	pyinstaller \
		--onefile \
		--name preflight \
		--clean \
		--noconfirm \
		preflight_entry.py
	@echo "Binary built: dist/preflight"

clean:
	rm -rf build/ dist/ *.spec __pycache__ .pytest_cache
