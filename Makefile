all: check flake8

flake8:
	flake8 .

check:
	pytest

cov:
	coverage erase
	pytest --cov=. tests
	coverage html

loc:
	@wc $(shell find . -name "*.py")
