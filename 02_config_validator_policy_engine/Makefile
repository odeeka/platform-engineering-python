.PHONY: install test build clean

install:
	pip install '.[dev]'

test:
	pytest -v

build:
	pyinstaller \
		--onefile \
		--name config-validator \
		--clean \
		--noconfirm \
		config_validator_entry.py
	@echo "Binary built: dist/config-validator"

clean:
	rm -rf build/ dist/ *.spec __pycache__ .pytest_cache
