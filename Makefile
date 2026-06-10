all: install lint run

install:
	pip install --upgrade setuptools
	pip install .

lint:
	flake8 --exclude=.venv,build,dist . && mypy --exclude '^\.venv/' --exclude '^build/' --exclude '^dist/' . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 --exclude=.venv,build,dist . && mypy --exclude '^\.venv/' --exclude '^build/' --exclude '^dist/' --exclude '^tests/' . --strict

run:
	python3 a_maze_ing.py config.txt

debug:
	python3 -m pdb a_maze_ing.py config.txt

test:
	python3 -m pytest test_amazing.py -v

clean:
	rm -rf __pycache__ .mypy_cache .pytest_cache mazegen/__pycache__ \
		tests/__pycache__

fclean: clean
	rm -rf *.egg-info dist build mazegen-*.whl

.PHONY: all install lint run debug clean fclean
