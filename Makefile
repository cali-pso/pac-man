CONFIG_FILE = config.json
MAIN_SCRIPT = pac-man.py
PYTHON_CMD = uv run python3

.PHONY: install run debug clean lint lint-strict build

install:
	uv sync

run:
	$(PYTHON_CMD) $(MAIN_SCRIPT) $(CONFIG_FILE)

debug:
	$(PYTHON_CMD) -m pdb $(MAIN_SCRIPT) $(CONFIG_FILE)

clean:
	rm -rf __pycache__ .mypy_cache build dist *.spec

fclean: clean
	rm -rf .venv

lint:
	- uv run flake8 ./src/
	- uv run mypy --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs .

build:
	uv run pyinstaller --name pac-man \
		--onedir \
		--paths . \
		--add-binary "mlx/libmlx.so:mlx" \
		--hidden-import pydantic \
		--hidden-import pygame \
		--hidden-import mazegenerator \
		--hidden-import mlx \
		src/__main__.py
	mkdir dist/pac-man/src/
	mkdir dist/pac-man/src/assets
	cp -r src/assets dist/pac-man/src
	cp config.json dist/pac-man/
