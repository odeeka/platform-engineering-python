.PHONY: install test build clean run

install:
	pip install '.[dev]'

test:
	pytest -v

run:
	mini-api --port 8080

build:
	pyinstaller \
		--onefile \
		--name mini-api \
		--clean \
		--noconfirm \
		mini_api_entry.py
	@echo "Binary built: dist/mini-api"

clean:
	rm -rf build/ dist/ *.spec __pycache__ .pytest_cache
