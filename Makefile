all: check flake8

flake8:
	flake8 . test symstore/bin/symstore

check:
	./test

cov:
	coverage combine
	coverage erase
	./test --coverage
	coverage combine
	coverage html

loc:
	@wc $(shell find . -name "*.py") symstore/bin/symstore
