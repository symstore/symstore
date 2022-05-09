all: check flake8

flake8:
	flake8 . test

check:
	./test

cov:
	coverage erase
	./test --coverage
	coverage combine
	coverage html

loc:
	@wc $(shell find . -name "*.py")
